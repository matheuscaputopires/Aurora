from unittest import TestCase
from mock import patch, MagicMock
import datetime
import os
import json

from service.schedule import Schedule

FT_GEOCODE_SCHEDULES_RESULT = "Geocode_Agendamentos_Result"

class TestSchedule(TestCase):

    @patch('service.schedule.Tool')
    @patch('service.schedule.utils')
    @patch('service.schedule.Config')
    @patch('service.schedule.Geodatabase')
    @patch('service.schedule.BaseRoute')
    def test_prepare_item_schedule(self, mock_BaseRoute, mock_Geodatabase, mock_Config, mock_utils, mock_Tool):

        mock_Config.return_value.get_env = MagicMock(return_value="test")

        PARAMS_FAKE = {
            "service_time_minutes": 15
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        date_timestamp_fake = 123456789
        mock_utils.datetime_to_timestamp = MagicMock(return_value=date_timestamp_fake)

        date_20210424_09h00 = datetime.datetime(2021, 4, 24, 9, 0, 0)
        ITEM = { 'attributes': {'datahora': date_20210424_09h00, 'empresaid': 1, 'endereco': None, 'cidade': None, 'bairro': None, 'estado': None}}
        ITEM_FAKE = {'TimeWindowStart': '2021-01-01', 'id': 1}
        COLUMNS_TO_FROM = [
            {'from': 'datahora', 'to': 'TimeWindowStart', 'format': 'date'},
            {'from': 'empresaid', 'to': 'id', 'format': None},
            {'from': 'TimeWindowEnd', 'to': 'TimeWindowEnd', 'format': 'date'},
            {'from': 'MaxViolationTime', 'to': 'MaxViolationTime', 'format': None}]

        log_fake = MagicMock(return_value=LogFake())
        schedule = Schedule(log_fake)

        schedule.geodatabase.prepare_item = MagicMock(return_value=ITEM_FAKE)

        result = schedule._prepare_item_schedule(ITEM)

        schedule.geodatabase.prepare_item.assert_called_with(COLUMNS_TO_FROM, ITEM['attributes'])
        self.assertEqual(result, ITEM_FAKE)

    @patch('service.schedule.Tool')
    @patch('service.schedule.utils')
    @patch('service.schedule.Config')
    @patch('service.schedule.Geodatabase')
    @patch('service.schedule.BaseRoute')
    def test_prepare_item_schedule_with_address(self, mock_BaseRoute, mock_Geodatabase, mock_Config, mock_utils, mock_Tool):

        mock_Config.return_value.get_env = MagicMock(return_value="test")

        PARAMS_FAKE = {
            "service_time_minutes": 15
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        date_timestamp_fake = 123456789
        mock_utils.datetime_to_timestamp = MagicMock(return_value=date_timestamp_fake)

        date_20210424_09h00 = datetime.datetime(2021, 4, 24, 9, 0, 0)
        ITEM = {
            'attributes': {'datahora': date_20210424_09h00, 'empresaid': 1, 'endereco': 'Av. 9 Julho', 'cidade': 'Sao Jose Campos', 'bairro': 'Centro', 'estado': 'SP', 'geometry': {'x': 1234.56, 'y': 5643.21}},
            'geometry': {'x': 1234.56, 'y': 5643.21}
            }
        ITEM_FAKE = {'TimeWindowStart': '2021-01-01', 'id': 1}
        COLUMNS_TO_FROM = [
            {'from': 'datahora', 'to': 'TimeWindowStart', 'format': 'date'},
            {'from': 'empresaid', 'to': 'id', 'format': None},
            {'from': 'TimeWindowEnd', 'to': 'TimeWindowEnd', 'format': 'date'},
            {'from': 'MaxViolationTime', 'to': 'MaxViolationTime', 'format': None},
            {'from': 'endereco', 'to': 'endereco', 'format': None},
            {'from': 'numero', 'to': 'numero', 'format': None},
            {'from': 'cidade', 'to': 'cidade', 'format': None},
            {'from': 'bairro', 'to': 'bairro', 'format': None},
            {'from': 'estado', 'to': 'estado', 'format': None},
            {'from': 'cep', 'to': 'cep', 'format': None},
            {'from': 'SHAPE@JSON', 'to': 'SHAPE@JSON', 'format': None}]

        log_fake = MagicMock(return_value=LogFake())
        schedule = Schedule(log_fake)

        schedule.geodatabase.prepare_item = MagicMock(return_value=ITEM_FAKE)

        result = schedule._prepare_item_schedule(ITEM)

        schedule.geodatabase.prepare_item.assert_called_with(COLUMNS_TO_FROM, ITEM['attributes'])
        self.assertEqual(result, ITEM_FAKE)
    
    @patch('service.schedule.Tool')
    @patch('service.schedule.BaseRoute')
    @patch('service.schedule.feature_server')
    @patch('service.schedule.Config')
    @patch('service.schedule.Geodatabase')
    @patch('service.schedule.utils')
    def test_synchronize_schedules_ags_to_gdb_geocode(self, mock_utils, mock_Geodatabase, mock_Config, mock_feature_server, mock_BaseRoute, mock_Tool):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")

        PARAMS_FAKE = {
            "schedules_feature_url": "https://link-service-arcgis-server",
            "company_name": "feature_company",
            "company_geocode": "TableFake"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)
        mock_utils.datetime_to_timestamp = MagicMock(return_value=12345)
        mock_Geodatabase.return_value.get_path = MagicMock(return_value="path")

        shape_json_fake = {
            "x": 100.00,
            "y": -10000.0,
            "z": 1
        }

        shape_json_str_fake = json.dumps(shape_json_fake)

        schedules_geocoded_fake = [{
            "USER_id": 1,
            "Match_addr": "Avenida Minas",
            "Score": 85,
            'SHAPE@JSON': shape_json_str_fake
        },
        {
            "USER_id": 2,
            "Match_addr": "Avenida",
            "Score": 40,
            'SHAPE@JSON': shape_json_str_fake
        },
        {
            "USER_id": 3,
            "Match_addr": "Avenida",
            "Score": 45,
            'SHAPE@JSON': shape_json_str_fake
        }]

        mock_Geodatabase.return_value.search_data = MagicMock(return_value=schedules_geocoded_fake)

        where_fake = "id in (1,2)"
        mock_Geodatabase.return_value.construct_where = MagicMock(return_value=where_fake)

        schedules_without_address =[
        {'attributes': {'datahora': 123456, "id": 1, 'empresaid': 1, 'endereco': 'Avenida Minas Gerais', 'numero': 43, 'cidade': "Caraguatatuba", 'bairro': "Jardim Primavera", 'estado': "SP", 'cep': '11600-700'}},
        {'attributes': {'datahora': 123456, "id": 2, 'empresaid': 2, 'endereco': 'Avenida', 'numero': 43, 'cidade': "Caraguatatuba", 'bairro': "Jardim Primavera", 'estado': "SP", 'cep': '11600-700'}, 'geometry': {"x": 100, "y": 100}},
        {'attributes': {'datahora': 123456, "id": 3, 'empresaid': 3, 'endereco': 'Avenida', 'numero': 43, 'cidade': "Caraguatatuba", 'bairro': "Jardim Primavera", 'estado': "SP", 'cep': '11600-700'}}
        ]
        
        log_fake = MagicMock(return_value=LogFake())
        schedule = Schedule(log_fake)

        features_fake= [{"id":1}, {"id": 2}, {"id": 3}]
        schedule._prepare_item_schedule = MagicMock(side_effect=[features_fake[0], features_fake[1], features_fake[2]])

        feature_ags_field_id = "id"
        feature_gdb = os.path.join("/path/gdb", PARAMS_FAKE['company_name'])
        feature_columns_to_update =  ['id','TimeWindowStart', 'TimeWindowEnd', 'MaxViolationTime', 'endereco', 'numero', 'bairro', 'cidade', 'estado', 'SHAPE@JSON']
        feature_gdb_field_id = "id"

        schedule._synchronize_schedules_ags_to_gdb(schedules_without_address,feature_ags_field_id,feature_gdb, feature_columns_to_update, feature_gdb_field_id, True)        
        
        companies_expected = schedules_without_address
        companies_expected[0]['attributes']['enderecocompleto'] = "Avenida Minas Gerais, 43, Jardim Primavera, Caraguatatuba, SP, 11600-700"
        companies_expected[1]['attributes']['enderecocompleto'] = "Avenida, 43, Jardim Primavera, Caraguatatuba, SP, 11600-700"
        companies_expected[2]['attributes']['enderecocompleto'] = "Avenida, 43, Jardim Primavera, Caraguatatuba, SP, 11600-700"

        feature_schedule_expected = os.path.join("path", "Geocode_Agendamentos")
        feature_geocoded_expected = os.path.join("path", FT_GEOCODE_SCHEDULES_RESULT)
        columns_expected = ['id', "enderecocompleto"]
        mock_Geodatabase.return_value.insert_data.assert_called_with(companies_expected, feature_schedule_expected, columns_expected)

        mock_Tool.return_value.geocode.assert_called_with(feature_schedule_expected, FT_GEOCODE_SCHEDULES_RESULT)

        mock_Geodatabase.return_value.search_data.assert_called_with(feature_geocoded_expected, ["Score", "USER_id", "Match_addr", 'SHAPE@JSON'])

        new_items_ags_expected = companies_expected
        new_items_ags_expected[0]['attributes']['data_geocode'] = 123456
        new_items_ags_expected[1]['attributes']['data_geocode'] = 123456
        new_items_ags_expected[2]['attributes']['data_geocode']  = 123456
        new_items_ags_expected[0]['attributes']['endereco_geocode'] = "Avenida Minas"
        new_items_ags_expected[1]['attributes']['endereco_geocode'] = "Avenida"
        new_items_ags_expected[2]['attributes']['endereco_geocode'] = "Avenida"
        new_items_ags_expected[0]['attributes']['geometry'] = shape_json_fake
        new_items_ags_expected[1]['attributes']['geometry'] = shape_json_fake
        new_items_ags_expected[2]['attributes']['geometry'] = shape_json_fake
        new_items_ags_expected[0]['geometry'] = shape_json_fake
        new_items_ags_expected[1]['geometry'] = shape_json_fake
        new_items_ags_expected[2]['geometry'] = shape_json_fake
        mock_feature_server.update_feature_data.assert_called_with(PARAMS_FAKE['schedules_feature_url'], new_items_ags_expected)

        mock_Geodatabase.return_value.update_data.assert_called_with(feature_gdb, feature_columns_to_update, where_fake, features_fake, feature_gdb_field_id)

    @patch('service.schedule.Tool')
    @patch('service.schedule.BaseRoute')
    @patch('service.schedule.feature_server')
    @patch('service.schedule.Config')
    @patch('service.schedule.Geodatabase')
    def test_synchronize_schedules(self, mock_Geodatabase, mock_Config, mock_feature_server, mock_BaseRoute, mock_Tool):

        mock_Config.return_value.get_env = MagicMock(return_value="test")

        PARAMS_FAKE = {
            "schedules_feature_url": "https://link-service-arcgis-server",
            "company_name": "feature_company"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        SCHEDULES_FAKE = [
            {'attributes': {'id': 11, 'name': 'John', 'endereco': None, 'cidade': None, 'bairro': None, 'estado': None, 'empresaid': 11, 'executivoid': 1159101}},
            {'attributes': {'id': 12, 'name': 'Mary', 'endereco': 'Avenue 9', 'cidade': 'Los Angeles', 'bairro': 'Sta Monica', 'estado': 'CA', 'empresaid': 12, 'executivoid': 1159101}},
            {'attributes': {'id': 12, 'name': 'Mary', 'endereco': None, 'cidade': None, 'bairro': None, 'estado': None, 'empresaid': 12, 'executivoid': 1159102}}
            ]
        mock_feature_server.get_feature_data = MagicMock(return_value=SCHEDULES_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        schedule = Schedule(log_fake)

        START_ROUTE_DAY_FAKE = datetime.datetime(2021, 3, 16, 9, 0, 0)
        schedule.base_route.start_route_day = MagicMock(return_value=START_ROUTE_DAY_FAKE)

        schedule.geodatabase.get_path = MagicMock(return_value="/path/gdb")

        schedule._synchronize_schedules_ags_to_gdb = MagicMock(side_effect=[None, None])

        schedule._separate_field_to_string = MagicMock(return_value="11,12,12")

        companies_fake = [
            {'id': 11, 'carteiraId': 1159101, 'executivoId': 1159101},
            {'id': 12, 'carteiraId': 1159101, 'executivoId': 1159101}
        ]

        schedule.geodatabase.search_data = MagicMock(return_value=companies_fake)

        schedule.synchronize_schedules()        

        ft_companies = os.path.join("/path/gdb", PARAMS_FAKE['company_name'])

        where_schedules_expected = "datahora >= DATE '2021-03-16'"
        mock_feature_server.get_feature_data.assert_called_with(PARAMS_FAKE['schedules_feature_url'], where_schedules_expected, order_by_field='id ASC')

        ft_columns_to_update_expected = ['id','TimeWindowStart', 'TimeWindowEnd', 'MaxViolationTime']
        schedule._synchronize_schedules_ags_to_gdb.assert_any_call([SCHEDULES_FAKE[0]], "id", ft_companies, ft_columns_to_update_expected, "id")

        ft_columns_to_update_expected_with_addr = ft_columns_to_update_expected + ['endereco', 'numero', 'bairro', 'cidade', 'estado', 'SHAPE@JSON']
        schedule._synchronize_schedules_ags_to_gdb.assert_any_call([SCHEDULES_FAKE[1]], "id", ft_companies, ft_columns_to_update_expected_with_addr, "id", True)
    
    @patch('service.schedule.Tool')
    @patch('service.schedule.BaseRoute')
    @patch('service.schedule.feature_server')
    @patch('service.schedule.Config')
    @patch('service.schedule.Geodatabase')
    def test_synchronize_schedules_empty(self, mock_Geodatabase, mock_Config, mock_feature_server, mock_BaseRoute, mock_Tool):

        mock_Config.return_value.get_env = MagicMock(return_value="test")

        PARAMS_FAKE = {
            "schedules_feature_url": "https://link-service-arcgis-server",
            "company_name": "feature_company"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        SCHEDULES_FAKE = [
            {'attributes': {'id': 1, 'name': 'John', 'endereco': None, 'cidade': None, 'bairro': None, 'estado': None, 'empresaid': 11, 'executivoid': 1159101}},
            {'attributes': {'id': 2, 'name': 'Mary', 'endereco': 'Avenue 9', 'cidade': 'Los Angeles', 'bairro': 'Sta Monica', 'estado': 'CA', 'empresaid': 12, 'executivoid': 1159101}}
            ]
        mock_feature_server.get_feature_data = MagicMock(return_value=SCHEDULES_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        schedule = Schedule(log_fake)

        START_ROUTE_DAY_FAKE = datetime.datetime(2021, 3, 16, 9, 0, 0)
        schedule.base_route.start_route_day = MagicMock(return_value=START_ROUTE_DAY_FAKE)

        schedule.geodatabase.get_path = MagicMock(return_value="/path/gdb")

        schedule._synchronize_schedules_ags_to_gdb = MagicMock(side_effect=[None, None])

        schedule._separate_field_to_string = MagicMock(return_value="")

        companies_fake = []

        schedule.geodatabase.search_data = MagicMock(return_value=companies_fake)

        schedule.synchronize_schedules()        

        where_schedules_expected = "datahora >= DATE '2021-03-16'"
        mock_feature_server.get_feature_data.assert_called_with(PARAMS_FAKE['schedules_feature_url'], where_schedules_expected, order_by_field='id ASC')

    @patch('service.schedule.Tool')
    @patch('service.schedule.BaseRoute')
    @patch('service.schedule.feature_server')
    @patch('service.schedule.Config')
    @patch('service.schedule.Geodatabase')
    def test_get_schedule_dict(self, mock_Geodatabase, mock_Config, mock_feature_server, mock_BaseRoute, mock_Tool):

        mock_Config.return_value.get_env = MagicMock(return_value="test")

        log_fake = MagicMock(return_value=LogFake())
        schedule = Schedule(log_fake)

        dict_schedules_fake = {'1#10112020090000': {'id': 1}}
        schedule.dict_schedules = dict_schedules_fake

        company_id = 1
        date_scheduled = datetime.datetime(2020, 11, 10, 9, 0, 0)
        result = schedule.get_schedule_dict(company_id, date_scheduled)

        expected = dict_schedules_fake['1#10112020090000']
        self.assertEqual(result, expected)

    @patch('service.schedule.Tool')
    @patch('service.schedule.BaseRoute')
    @patch('service.schedule.feature_server')
    @patch('service.schedule.Config')
    @patch('service.schedule.Geodatabase')
    def test_get_schedule_dict_date_schedule_is_none(self, mock_Geodatabase, mock_Config, mock_feature_server, mock_BaseRoute, mock_Tool):

        mock_Config.return_value.get_env = MagicMock(return_value="test")

        log_fake = MagicMock(return_value=LogFake())
        schedule = Schedule(log_fake)

        company_id = 1
        date_scheduled = None
        result = schedule.get_schedule_dict(company_id, date_scheduled)

        expected = None
        self.assertEqual(result, expected)        

    @patch('service.schedule.Tool')
    @patch('service.schedule.BaseRoute')
    @patch('service.schedule.feature_server')
    @patch('service.schedule.Config')
    @patch('service.schedule.Geodatabase')
    def test_get_schedule_dict_not_found_schedule(self, mock_Geodatabase, mock_Config, mock_feature_server, mock_BaseRoute, mock_Tool):

        mock_Config.return_value.get_env = MagicMock(return_value="test")

        log_fake = MagicMock(return_value=LogFake())
        schedule = Schedule(log_fake)

        dict_schedules_fake = {'1#10112020090000': {'id': 1}}
        schedule.dict_schedules = dict_schedules_fake

        company_id = 1
        date_scheduled = datetime.datetime(2020, 11, 11, 9, 0, 0)
        result = schedule.get_schedule_dict(company_id, date_scheduled)

        expected = None
        self.assertEqual(result, expected)
    
    @patch('service.schedule.Tool')
    @patch('service.schedule.BaseRoute')
    @patch('service.schedule.feature_server')
    @patch('service.schedule.Config')
    @patch('service.schedule.Geodatabase')
    def test_separate_field_to_string(self, mock_Geodatabase, mock_Config, mock_feature_server, mock_BaseRoute, mock_Tool):

        mock_Config.return_value.get_env = MagicMock(return_value="test")

        log_fake = MagicMock(return_value=LogFake())
        schedule = Schedule(log_fake)

        array_fake = [{"attributes":{"field1": 'teste1', "field2": "teste2"}}, {"attributes":{"field1": 'teste3', "field2": "teste4"}}, {"attributes":{"field1": 'teste5', "field2": "teste6"}}]

        result_string = schedule._separate_field_to_string("field1", array_fake)

        result_expected = "teste1,teste3,teste5"

        self.assertEqual(result_string, result_expected)

class LogFake:
    pass