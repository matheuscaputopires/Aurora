from esri.arcgis_server import ArcGISServer
import json
import time

class FeatureServer:
    def __init__(self, logger, config):
        self.ags = ArcGISServer(config)
        self.logger = logger

    def retry_while(self, fn, tries=3, sleep_time=60, logger=None, exit_app_if_fail=True):
        '''
            It executes a given function n times, and sleeps between each try.

            It accepts a logger to track the situation and a flag to exit the
            application if all the tries had failed.

            fn: a function without parameters that shall be processed
            tries: number of times the fn function will be tried
            sleep_time: number of seconds to sleep between each try
            logger: application logger
            exit_app_if_fail: flag to order a system exit if all tries had failed
        '''
        while tries:
            try:
                return fn()
            except Exception as err:
                self.logger.error('Erro durante chamada do AGS')
                self.logger.error(err)

            tries -= 1

            if tries:
                self.logger.error('Dormindo.... [ resta(m) %s tentativa(s) ]' % tries)
                time.sleep(sleep_time)

        if exit_app_if_fail:
            self.logger.error('Erro irrecuperável, saindo da aplicação....')
            exit(1)

    def _format_response(self, response, field_data):
        success = True
        data = None
        if not 'error' in response:
            data = response[field_data]
        else: 
            data = response['error']['message']
            success = False
            self.logger.error(data)

        return {'success': success, 'data': data}        

    def get_feature_data(self, feature_url, where="1=1", distinct_values=None, geometries=True, feature_limit=None):
        """``where`` opcional, exemplo: "field1 = 1 AND field2 = 'XPTO'..."
        ``distinct_values`` opcional, exemplo: "field1, field2..."
        ``geometries`` por padrão é True
        ``feature_limit`` opcional, exemplo: 100 ou 200
        """
        feature_url += '/query'
        all_features = []
        result_off_set = 0
        result_record_count = 2000
        token = self.ags.generate_token()

        feature_params = { 'token': token, 'where': where, 'f': 'json', 'outFields': '*' }
        if distinct_values != None:
            feature_params['outFields'] = distinct_values
            feature_params['orderByFields'] = distinct_values
            feature_params['groupByFieldsForStatistics'] = distinct_values
            feature_params['returnDistinctValues'] = "true"


        feature_params['returnGeometry'] = 'true' if geometries == True else 'false'

        more_records = True
        while (more_records):
            
            feature_params['resultOffset'] = result_off_set
            feature_params['resultRecordCount'] = result_record_count

            fn = lambda: self.ags.get_data(feature_url=feature_url, feature_params=feature_params)
            response = self.retry_while(fn=fn, tries=3, sleep_time=60, exit_app_if_fail=True)

            acquired_features = response['features']
            records_found = len(acquired_features)
            more_records = True if records_found > 0 else False
            all_features += acquired_features
            result_off_set += records_found        

        return all_features

    def post_feature_data(self, feature_url, payload):
        token = self.ags.generate_token()
        feature_url += '/addFeatures'
        data = json.dumps(payload)
        payload = { 'features': data, 'f': 'pjson', 'rollbackOnFailure': 'true', 'token': token }

        fn = lambda: self.ags.post_data(feature_url, payload)
        response = self.retry_while(fn=fn, tries=3, sleep_time=60, exit_app_if_fail=True)

        return self._format_response(response, 'addResults')

    def delete_feature_data(self, feature_url, filter):
        token = self.ags.generate_token()
        feature_url += '/deleteFeatures'
        payload = { 'token': token, 'where': filter, 'f': 'json' }

        fn = lambda: self.ags.delete_data(feature_url, payload)
        response = self.retry_while(fn=fn, tries=3, sleep_time=60, exit_app_if_fail=True)

        return response

    def calculate_feature_data(self, feature_url, where, calc_expression):
        """``where``, exemplo: "field1 = 1 AND field2 = 'XPTO'..."
        ``calc_expression`` opcional, exemplo: [{"field" : "Quality", "value" : 3}]"
        """
        token = self.ags.generate_token()
        feature_url += '/calculate'
        payload = { 'where': where, 'calcExpression': json.dumps(calc_expression), 'f': 'pjson', 'token': token }

        fn = lambda: self.ags.post_data(feature_url, payload)
        response = self.retry_while(fn=fn, tries=3, sleep_time=60, exit_app_if_fail=True)

        return self._format_response(response, 'updatedFeatureCount')
        
