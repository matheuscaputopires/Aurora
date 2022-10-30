from unittest import TestCase
from mock import patch, MagicMock
import esri.feature_server as feature_server
import json

class LogFake:
    pass

def create_bad_good_function_generator():
    def error_fn():
        raise
    def valid_fn():
        return 'result of a valid call'

    list_of_functions = [error_fn, valid_fn]
    for fn in list_of_functions:
        yield fn

def retry_while_wrapper_fn():
    function_generator = create_bad_good_function_generator()

    def internal_fn():
        for fn in function_generator:
            return fn()

    return internal_fn

class TesteFeatureServer(TestCase):

    @patch('esri.feature_server.ags')
    def test_retry_while_fail_limit_exceeded_no_exit_app(self, mock_ags):
        def error_function():
            raise

        result_expected = None
        result = feature_server.retry_while(
            fn=error_function, tries=1, exit_app_if_fail=False)

        self.assertEqual(result, result_expected)

    @patch('esri.feature_server.ags')
    def test_retry_while_fail_limit_exceeded_with_exit_app(self, mock_ags):
        def error_function():
            raise

        with self.assertRaises(SystemExit):
            feature_server.retry_while(
                fn=error_function,
                tries=2, sleep_time=0.001, exit_app_if_fail=True)

    @patch('esri.feature_server.ags')
    def test_retry_while_with_log(self, mock_ags):
        log_fake = MagicMock(return_value=LogFake())

        result_expected = 'result of a valid call'
        result = feature_server.retry_while(
            fn=retry_while_wrapper_fn(),
            tries=2, sleep_time=0.001, logger=log_fake, exit_app_if_fail=False)

        self.assertEqual(result, result_expected)

    @patch('esri.feature_server.ags')
    def test_retry_while_without_log(self, mock_ags):
        result_expected = 'result of a valid call'
        result = feature_server.retry_while(
            fn=retry_while_wrapper_fn(),
            tries=3, sleep_time=0.001, exit_app_if_fail=False)

        self.assertEqual(result, result_expected)

    @patch('esri.feature_server.ags')
    def test_get_feature_data(self, mock_ags):

        token_fake = 123456789
        mock_ags.generate_token = MagicMock(return_value=token_fake)

        response_fake = {'features': [{'attributes': {'id': 1}}]}
        response_fake_empty = {'features': []}
        mock_ags.get_data = MagicMock(side_effect=[response_fake, response_fake_empty])

        feature_url = 'https://arcgis-server/feature/0'
        result = feature_server.get_feature_data(feature_url)
        result_expected = response_fake['features']
        self.assertEqual(result, result_expected)

        feature_url_fake = feature_url + '/query'
        feature_params_fake = { 'token': token_fake, 'where': '1=1', 'f': 'json', 'outFields': '*' }
        feature_params_fake['orderByFields'] = None
        feature_params_fake['returnGeometry'] = 'true'
        feature_params_fake['resultOffset'] = 0
        feature_params_fake['resultRecordCount'] = 2000
        #mock_ags.get_data.assert_any_call(feature_url=feature_url_fake, feature_params=feature_params_fake)
        
        feature_params_fake['resultOffset'] = 1
        mock_ags.get_data.assert_any_call(feature_url=feature_url_fake, feature_params=feature_params_fake)

        self.assertEqual(mock_ags.get_data.call_count, 2)

    @patch('esri.feature_server.ags')
    def test_get_feature_data_with_distinct_values(self, mock_ags):

        token_fake = 123456789
        mock_ags.generate_token = MagicMock(return_value=token_fake)

        response_fake = {'features': [{'attributes': {'id': 1}}]}
        response_fake_empty = {'features': []}
        mock_ags.get_data = MagicMock(side_effect=[response_fake, response_fake_empty])

        feature_url = 'https://arcgis-server/feature/0'
        result = feature_server.get_feature_data(feature_url, "id=1", "id", False)
        result_expected = response_fake['features']
        self.assertEqual(result, result_expected)

        feature_url_fake = feature_url + '/query'
        feature_params_fake = { 'token': token_fake, 'where': 'id=1', 'f': 'json', 'outFields': 'id' }
        feature_params_fake['orderByFields'] = 'id'
        feature_params_fake['groupByFieldsForStatistics'] = 'id'
        feature_params_fake['returnDistinctValues'] = 'true'
        feature_params_fake['returnGeometry'] = 'false'
        feature_params_fake['resultOffset'] = 0
        feature_params_fake['resultRecordCount'] = 2000        
        #mock_ags.get_data.assert_any_call(feature_url=feature_url_fake, feature_params=feature_params_fake)
        feature_params_fake['resultOffset'] = 1
        mock_ags.get_data.assert_any_call(feature_url=feature_url_fake, feature_params=feature_params_fake)
        self.assertEqual(mock_ags.get_data.call_count, 2)

    @patch('esri.feature_server.ags')
    def test_post_feature_data(self, mock_ags):

        TOKEN_FAKE = "123456789"
        mock_ags.generate_token = MagicMock(return_value=TOKEN_FAKE)
        RESPONSE_FAKE = {'addResults': [{'objectId': 1, 'globalId': '{444-4545}', 'success': True}]}
        mock_ags.post_data = MagicMock(return_value=RESPONSE_FAKE)
        payload = { 'objectid': '1'}
        feature_url = 'https://link-server/feature/0'
        result = feature_server.post_feature_data(feature_url, payload)

        result_expected = RESPONSE_FAKE['addResults']
        self.assertEqual(result, result_expected)

        mock_ags.generate_token.assert_called_with()
        feature_url_expected = feature_url + '/addFeatures'
        payload_expected = { 'features': json.dumps(payload), 'f': 'pjson', 'rollbackOnFailure': 'true', 'token': TOKEN_FAKE }
        mock_ags.post_data.assert_called_with(feature_url_expected, payload_expected)

    @patch('esri.feature_server.ags')
    def test_delete_feature_data(self, mock_ags):

        TOKEN_FAKE = "123456789"
        mock_ags.generate_token = MagicMock(return_value=TOKEN_FAKE)
        RESPONSE_FAKE = {'deleteResults': [{'objectId': 1, 'globalId': '{444-4545}', 'success': True}]}
        mock_ags.delete_data = MagicMock(return_value=RESPONSE_FAKE)

        feature_url = 'https://link-server/feature/0'
        where_filter = '1=1'
        result = feature_server.delete_feature_data(feature_url, where_filter)

        result_expected = RESPONSE_FAKE
        self.assertEqual(result, result_expected)

        mock_ags.generate_token.assert_called_with()
        feature_url_expected = feature_url + '/deleteFeatures'
        payload = { 'token': TOKEN_FAKE, 'where': where_filter, 'f': 'json' }
        mock_ags.delete_data.assert_called_with(feature_url_expected, payload)

    @patch('esri.feature_server.ags')
    def test_update_feature_data(self, mock_ags):

        TOKEN_FAKE = "123456789"
        mock_ags.generate_token = MagicMock(return_value=TOKEN_FAKE)
        RESPONSE_FAKE = {'updateResults': [{'objectId': 1, 'globalId': '{444-4545}', 'success': True}]}
        mock_ags.post_data = MagicMock(return_value=RESPONSE_FAKE)
        payload = { 'objectid': '1'}
        feature_url = 'https://link-server/feature/0'
        result = feature_server.update_feature_data(feature_url, payload)

        result_expected = RESPONSE_FAKE['updateResults']
        self.assertEqual(result, result_expected)

        mock_ags.generate_token.assert_called_with()
        feature_url_expected = feature_url + '/updateFeatures'
        payload_expected = { 'features': json.dumps(payload), 'f': 'pjson', 'rollbackOnFailure': 'true', 'token': TOKEN_FAKE }
        mock_ags.post_data.assert_called_with(feature_url_expected, payload_expected)

    @patch('esri.feature_server.ags')
    def test_calculate_feature_data(self, mock_ags):

        TOKEN_FAKE = "123456789"
        mock_ags.generate_token = MagicMock(return_value=TOKEN_FAKE)
        RESPONSE_FAKE = {'updatedFeatureCount': 2}
        mock_ags.post_data = MagicMock(return_value=RESPONSE_FAKE)

        feature_url = 'https://link-server/feature/0'
        where = "id=123"
        calc_expression = [{'field': 'inativo', 'value': 1}]
        result = feature_server.calculate_feature_data(feature_url, where, calc_expression)

        result_expected = RESPONSE_FAKE['updatedFeatureCount']
        self.assertEqual(result, result_expected)

        mock_ags.generate_token.assert_called_with()
        feature_url_expected = feature_url + '/calculate'
        payload_expected = { 'where': where, 'calcExpression': json.dumps(calc_expression), 'f': 'pjson', 'token': TOKEN_FAKE }
        mock_ags.post_data.assert_called_with(feature_url_expected, payload_expected)

    @patch('esri.feature_server.ags')
    def test_count_feature_data(self, mock_ags):

        TOKEN_FAKE = "123456789"
        mock_ags.generate_token = MagicMock(return_value=TOKEN_FAKE)
        RESPONSE_FAKE = {'count': 200}
        mock_ags.get_data = MagicMock(return_value=RESPONSE_FAKE)

        feature_url = 'https://link-server/feature/0'
        where = "id=123"
        result = feature_server.count_feature_data(feature_url, where)

        result_expected = RESPONSE_FAKE['count']
        self.assertEqual(result, result_expected)

        mock_ags.generate_token.assert_called_with()
        feature_url_expected = feature_url + '/query'
        feature_params_expected = { 'token': TOKEN_FAKE, 'where': where, 'f': 'json', 'outFields': '*', 'returnCountOnly': 'true' }
        mock_ags.get_data.assert_called_with(feature_url=feature_url_expected, feature_params=feature_params_expected)        
