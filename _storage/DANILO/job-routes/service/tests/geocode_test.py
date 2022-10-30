from unittest import TestCase
from mock import patch, MagicMock
from freezegun import freeze_time
import os
import datetime
import copy

from service.geocode import Geocode

GEOCODE_TABLE_NAME = "GeocodificacaoEmpresas"
GEOCODED_FEATURE_NAME = "Geocoded_Companies"
WORK_AREAS_FEATURE_NAME = "Carteiras"
INTERSECT_FEATURE_NAME = "Compan_WorkAre_Int"

class TestGeocode(TestCase):

    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.feature_server')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_update_company_same_address(self, mock_Tool, mock_Geodatabase, mock_feature_server, mock_Config, mock_BaseRoute):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {
            "leads_feature_url": "https://link-service-arcgis-server/feature/0",
        }        
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        companies_fake = [{
            'objectid': 1,
            'empresa': 'Coke',
            'clientepagseguro': 0,
            'origem': 0,
            'roteirizar': 1,
            'tipoalerta': 'CRM'
        }]
        geocode._update_company_same_address(companies_fake)

        payload_fake = [{
            'attributes': companies_fake[0]
        }]
        mock_feature_server.update_feature_data.assert_called_with(PARAMS_FAKE['leads_feature_url'], payload_fake)

    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.feature_server')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_update_company_same_address_empty_companies(self, mock_Tool, mock_Geodatabase, mock_feature_server, mock_Config, mock_BaseRoute):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {
            "leads_feature_url": "https://link-service-arcgis-server/feature/0",
        }        
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        companies_fake = []
        geocode._update_company_same_address(companies_fake)

        mock_feature_server.update_feature_data.assert_not_called()

    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.feature_server')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_identify_companies_same_and_new_address(self, mock_Tool, mock_Geodatabase, mock_feature_server, mock_Config, mock_BaseRoute):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {
            "leads_feature_url": "https://link-service-arcgis-server/feature/0",
        }        
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        companies_server_fake = [
            {
                'attributes': {
                    'objectid': 1,
                    'id': 100,
                    'empresa': 'Coke',
                    'endereco': 'Avenida Brasil', 
                    'numero': '100', 
                    'complemento': None, 
                    'bairro': 'Centro', 
                    'cidade': 'Sao Paulo', 
                    'estado': 'SP', 
                    'cep': '12300000', 
                    'carteiraid': 101
                }
            },
            {
                'attributes': {
                    'objectid': 2,
                    'id': 200,
                    'empresa': 'Pepsi',
                    'endereco': 'Avenida 9 Julho', 
                    'numero': '50', 
                    'complemento': None, 
                    'bairro': 'Centro', 
                    'cidade': 'Sao Paulo', 
                    'estado': 'SP', 
                    'cep': '12300000', 
                    'carteiraid': 201
                }
            },            
        ]
        mock_feature_server.get_feature_data = MagicMock(return_value=companies_server_fake)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        companies_fake = copy.deepcopy(companies_server_fake)
        companies_fake[0]['attributes']['objectid'] = 30
        companies_fake[1]['attributes']['objectid'] = 31
        companies_fake[1]['attributes']['endereco'] = 'Rua Alfredo'
        companies_fake[1]['attributes']['numero'] = '70'
        companies_fake[1]['attributes']['bairro'] = 'Jardim Flores'
        companies_id_fake = [100,200]
        result = geocode._identify_companies_same_and_new_address(companies_fake, companies_id_fake)

        expected = {
            'new_address': [companies_fake[1]],
            'same_address': [companies_fake[0]['attributes']]
        }
        self.assertEqual(result, expected)

        mock_feature_server.get_feature_data.assert_called_with(PARAMS_FAKE['leads_feature_url'], 'id in (100,200)')        

    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.feature_server')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_identify_companies_same_and_new_address_empty_companies(self, mock_Tool, mock_Geodatabase, mock_feature_server, mock_Config, mock_BaseRoute):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_BaseRoute = MagicMock(return_value=None)

        mock_feature_server.get_feature_data = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        companies_fake = []
        companies_id_fake = []
        result = geocode._identify_companies_same_and_new_address(companies_fake, companies_id_fake)

        expected = {
            'new_address': [],
            'same_address': []
        }
        self.assertEqual(result, expected)

        mock_feature_server.get_feature_data.assert_not_called()

    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.feature_server')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_synchronize_leads_for_geocode(self, mock_Tool, mock_Geodatabase, mock_feature_server, mock_Config, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {
            "geocode_companies": "https://link-service-arcgis-server/feature/10",
            "local_table_fields": ["endereco", "numero", "bairro", "cidade", "estado", "cep", "roteirizar"],
            "company_geocode": "TableFakeGeocode"
        }

        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        geocode_companies_fake = [
            {'attributes': {'objectid': 1, 'globalid': 1, 'id': 101, 'endereco': 'Rua Cinco', 'numero': 129, 'bairro': 'Centro', 'cidade': 'São Paulo', 'estado': 'SP', 'cep': '00000-000', 'roteirizar': 1}},
            {'attributes': {'objectid': 2, 'globalid': 2, 'id': 102, 'endereco': 'Rua Dez', 'numero': 10, 'bairro': 'Centro', 'cidade': 'São Paulo', 'estado': 'SP', 'cep': '00000-000', 'roteirizar': 1}},
            {'attributes': {'objectid': 3, 'globalid': 3, 'id': 102, 'endereco': 'Rua Onze', 'numero': 11, 'bairro': 'Centro', 'cidade': 'São Paulo', 'estado': 'SP', 'cep': '00000-000', 'roteirizar': 1}}
            ]
        mock_feature_server.get_feature_data = MagicMock(return_value=geocode_companies_fake)

        geocode.geodatabase.get_path = MagicMock(return_value="/path/gdb")

        geocode.geodatabase.copy_template_table_to_temp_gdb = MagicMock(return_value=None)

        geocode.geodatabase.insert_data = MagicMock(return_value=None)

        table_fake = [
            {'attributes': {'id': 101, 'endereco': 'Rua Cinco', 'numero': 129, 'bairro': 'Centro', 'cidade': 'São Paulo', 'estado': 'SP', 'cep': '00000-000', 'roteirizar': 1, 'enderecocompleto': 'Rua Cinco, 129, Centro, São Paulo, SP, 00000-000'}},
            {'attributes': {'id': 102, 'endereco': 'Rua Onze', 'numero': 11, 'bairro': 'Centro', 'cidade': 'São Paulo', 'estado': 'SP', 'cep': '00000-000', 'roteirizar': 1, 'enderecocompleto': 'Rua Onze, 11, Centro, São Paulo, SP, 00000-000'}}
            ]
        group_of_companies_fake = {
            'new_address': table_fake,
            'same_address': []
        }
        geocode._identify_companies_same_and_new_address = MagicMock(return_value=group_of_companies_fake)
        geocode._update_company_same_address = MagicMock(return_value=None)

        geocode._synchronize_leads_for_geocode()

        geocode.geodatabase.get_path.assert_called_with()
        geocode.geodatabase.copy_template_table_to_temp_gdb.assert_called_with(PARAMS_FAKE['company_geocode'])

        mock_feature_server.get_feature_data.assert_called_with(PARAMS_FAKE['geocode_companies'], logger=log_fake)

        geocode._identify_companies_same_and_new_address.assert_called()
        geocode._update_company_same_address.assert_called()
        
        table_companies = os.path.join("/path/gdb", PARAMS_FAKE['company_geocode'])
        geocode.geodatabase.insert_data.assert_called_with(table_fake, table_companies, PARAMS_FAKE['local_table_fields'])


    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_get_fields(self, mock_Tool, mock_Geodatabase, mock_Config, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        geocode._arcpy = MagicMock(return_value=ArcpyFake())

        list_fields_fake = [
            ObjectView({'name':'name'}),
            ObjectView({'name':'objectid'}),
            ObjectView({'name':'shape'}),
            ObjectView({'name':'globalid'}),
            ObjectView({'name':'shape_length'}),
            ObjectView({'name':'shape_area'})]
        geocode._arcpy.ListFields = MagicMock(return_value=list_fields_fake)

        feature_fake = '/path/feature_name'
        result = geocode._get_fields(feature_fake)

        result_expected = ['name', 'SHAPE@JSON']
        self.assertEqual(result, result_expected)

        geocode._arcpy.ListFields.assert_called_with(feature_fake)

    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_synchronize_work_areas(self, mock_Tool, mock_Geodatabase, mock_Config, mock_BaseRoute):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        path_fake = 'path_gdb'
        geocode.geodatabase.get_path = MagicMock(return_value=path_fake)
        geocode.geodatabase.copy_template_feature_to_temp_gdb = MagicMock(return_value=None)
        work_areas_fake = [{"attributes": {"id": 1}}, {"attributes": {"id": 2}}]
        geocode.base_route.get_work_areas = MagicMock(return_value=work_areas_fake)
        fields_fake = ['name']
        geocode._get_fields = MagicMock(return_value=fields_fake)
        geocode.geodatabase.insert_data = MagicMock(return_value=None)

        geocode._synchronize_work_areas()

        geocode.geodatabase.get_path.assert_called_with()
        geocode.geodatabase.copy_template_feature_to_temp_gdb.assert_called_with(WORK_AREAS_FEATURE_NAME, geom_type="POLYGON")
        geocode.base_route.get_work_areas.assert_called_with()
        feature_work_areas_fake = os.path.join(path_fake, WORK_AREAS_FEATURE_NAME)
        geocode._get_fields.assert_called_with(feature_work_areas_fake)
        geocode.geodatabase.insert_data.assert_called_with(work_areas_fake, feature_work_areas_fake, fields_fake)

    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_geocode_leads(self, mock_Tool, mock_Geodatabase, mock_Config, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {
            "path_locator": "path/folder/locator",
            "company_geocode": "GeocodificacaoEmpresas"
        }

        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        geocode._arcpy = MagicMock(return_value=ArcpyFake())

        path_fake = 'path_gdb'
        geocode.geodatabase.get_path = MagicMock(return_value=path_fake)
        geocode._arcpy.geocoding.GeocodeAddresses = MagicMock(return_value=None)

        geocode._geocode_leads()

        geocode.geodatabase.get_path.assert_called_with()
        path_company_to_geocod = os.path.join(path_fake, PARAMS_FAKE['company_geocode'])
        path_company_geocoded = os.path.join(path_fake, GEOCODED_FEATURE_NAME)
        geocode._arcpy.geocoding.GeocodeAddresses.assert_called_with(
            path_company_to_geocod,
            PARAMS_FAKE['path_locator'],
            "'Single Line Input' enderecocompleto VISIBLE NONE",
            path_company_geocoded,
            "STATIC", None, "ROUTING_LOCATION", "Subaddress;'Point Address';'Street Address';'Distance Marker';'Street Name'", "ALL")

    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_identify_work_areas(self, mock_Tool, mock_Geodatabase, mock_Config, mock_BaseRoute):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        geocode._arcpy = MagicMock(return_value=ArcpyFake())

        geocode._arcpy.analysis.Intersect = MagicMock(return_value=None)

        geocode._identify_work_areas()

        mock_Tool.return_value.intersect.assert_called_with(GEOCODED_FEATURE_NAME, WORK_AREAS_FEATURE_NAME, INTERSECT_FEATURE_NAME)

    @patch('service.geocode.utils')
    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_validate_publish(self, mock_Tool, mock_Geodatabase, mock_Config, mock_BaseRoute, mock_utils):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        path_fake = 'path_gdb'
        geocode.geodatabase.get_path = MagicMock(return_value=path_fake)

        fields_fake = ['name']
        geocode._list_fields = MagicMock(side_effect=[fields_fake, fields_fake])

        companies_intersect_fake = [{'Score': 80, 'USER_id': 1, 'polo': 'SP'}, {'Score': 81, 'USER_id': 5, 'polo': 'SP'}, {'Score': 81, 'USER_id': 4, 'polo': 'SP'}]
        companies_geocode_fake = [
            {'Score': 80, 'USER_id': 1, 'USER_carteiraid': 100, 'USER_carteira': 'Carteira XPTO', 'USER_polo': 'SP'}, 
            {'Score': 81, 'USER_id': 3, 'USER_carteiraid': 100, 'USER_carteira': 'Carteira XPTO', 'USER_polo': 'SP'}, 
            {'Score': 81, 'USER_id': 4, 'USER_carteiraid': 200, 'USER_carteira': 'Carteira XPTO', 'USER_polo': 'RJ'}, 
            {'Score': 81, 'USER_id': 5, 'USER_carteiraid': None, 'USER_carteira': None, 'USER_polo': None}, 
            {'Score': 79, 'USER_id': 2}
            ]
        geocode.geodatabase.search_data = MagicMock(side_effect=[companies_intersect_fake, companies_geocode_fake])

        result = geocode._validate_publish()

        geocoded_fake = [companies_intersect_fake[0], companies_intersect_fake[1]]
        not_geocoded_fake = [companies_geocode_fake[1], companies_geocode_fake[2], companies_geocode_fake[4]]

        result_expected = {
            'geocoded': geocoded_fake,
            'not_geocoded': not_geocoded_fake
        }

        self.assertEqual(result, result_expected)

        geocode.geodatabase.get_path.assert_called_with()
        feature_companies_intersect_fake = os.path.join(path_fake, INTERSECT_FEATURE_NAME)
        geocode._list_fields.assert_any_call(feature_companies_intersect_fake)
        feature_companies_geocode_fake = os.path.join(path_fake, GEOCODED_FEATURE_NAME)
        geocode._list_fields.assert_any_call(feature_companies_geocode_fake)
        geocode.geodatabase.search_data.assert_any_call(feature_companies_intersect_fake, fields_fake)
        geocode.geodatabase.search_data.assert_any_call(feature_companies_geocode_fake, fields_fake)


    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.feature_server')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_deletion_features(self, mock_Tool, mock_Geodatabase, mock_feature_server, mock_Config, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {
            "leads_feature_url": "https://link-service-arcgis-server/feature/0"
        }

        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        companies_id_fake = [{ 'attributes': { 'id': 1}}]
        mock_feature_server.get_feature_data = MagicMock(return_value=companies_id_fake)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        result_ids = geocode._deletion_features([1, 2])
        self.assertEqual(result_ids, ['1', '0'])

        mock_feature_server.get_feature_data.assert_called_with(feature_url=PARAMS_FAKE['leads_feature_url'], geometries=False, distinct_values='id')

    @patch('service.geocode.utils')
    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.feature_server')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_publish_new_leads(self, mock_Tool, mock_Geodatabase, mock_feature_server, mock_Config, mock_BaseRoute, mock_utils):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        date_timestamp_fake = 123456789
        mock_utils.datetime_to_timestamp = MagicMock(return_value=date_timestamp_fake)

        results_fake = [{'success': True}]
        mock_feature_server.post_feature_data = MagicMock(return_value=results_fake)
        mock_feature_server.delete_feature_data = MagicMock(return_value=results_fake[0])

        PARAMS_FAKE = {
            "leads_feature_url": "https://link-service-arcgis-server/feature/0"
        }

        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        geocode._deletion_features = MagicMock(return_value=['1'])

        companies_fake = [{ "FID_Carteiras": 1, "USER_id": 1, "USER_empresa": "Nome Empresa", "USER_endereco": "Rua Um", "USER_numero": "129", "USER_bairro": "centro", "USER_cidade": "São Paulo", "USER_estado": "SP", "id": 1,"nome": "Nome", "polo": 1, "USER_polo": None, "USER_carteiraid": None, "USER_carteira": None, "carteira": "Carteira", "USER_cep": "00000-000", "USER_roteirizar": 1, "USER_tipoalerta": "ALERT_VISIT", "Shape": (0, 0) }]
        geocode._publish_new_leads(companies_fake)

        ids = []
        ids.append(companies_fake[0]['USER_id'])

        payload_fake = [{'attributes': {'carteiraid': 1, 'mcc': None, 'nomeresponsavel': None, 'tipoalerta': 'ALERT_VISIT', 'id': 1, 'empresa': 'Nome Empresa', 'nomecontato': ' ', 'cnpjcpf': None, 'segmento': None, 'faixatpv': None, 'endereco': 'Rua Um', 'numero': '129', 'bairro': 'centro', 'cidade': 'São Paulo', 'estado': 'SP', 'complemento': ' ', 'latitude': 0, 'longitude': 0, 'telefone': None, 'clientepagseguro': 0, 'cnae': ' ', 'roteirizar': 1, 'tipopessoa': ' ', 'situacaocliente': ' ', 'receitapresumida': 0, 'origemempresa': ' ', 'maiorreceita': 0, 'datamaiorreceita': None, 'nomeexecutivo': 'Nome', 'polo': 1, 'carteira': 'Carteira', 'origem': 0, 'cep': '00000-000', 'datageocodificacao': 123456789, 'dataidentificacaocarteira': 123456789}, 'geometry': {'x': 0, 'y': 0, 'spatialReference': {'wkid': 4326}}}]

        query_filter = 'id in (1)'
        mock_feature_server.delete_feature_data.assert_called_with(PARAMS_FAKE['leads_feature_url'], query_filter)
        mock_feature_server.post_feature_data.assert_called_with(PARAMS_FAKE['leads_feature_url'], payload_fake)

    @patch('service.geocode.utils')
    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.feature_server')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_publish_new_leads_with_data_workarea(self, mock_Tool, mock_Geodatabase, mock_feature_server, mock_Config, mock_BaseRoute, mock_utils):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        date_timestamp_fake = 123456789
        mock_utils.datetime_to_timestamp = MagicMock(return_value=date_timestamp_fake)

        results_fake = [{'success': True}]
        mock_feature_server.post_feature_data = MagicMock(return_value=results_fake)
        mock_feature_server.delete_feature_data = MagicMock(return_value=results_fake[0])

        PARAMS_FAKE = {
            "leads_feature_url": "https://link-service-arcgis-server/feature/0"
        }

        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        geocode._deletion_features = MagicMock(return_value=['1'])

        companies_fake = [{ "FID_Carteiras": 1, "USER_id": 1, "USER_empresa": "Nome Empresa", "USER_endereco": "Rua Um", "USER_numero": "129", "USER_bairro": "centro", "USER_cidade": "São Paulo", "USER_estado": "SP", "id": 1,"nome": "Nome", "polo": 1, "USER_polo": 100, "USER_carteiraid": 1001, "USER_carteira": "Carteira 1001", "carteira": "Carteira", "USER_cep": "00000-000", "USER_roteirizar": 1, "USER_tipoalerta": "ALERT_VISIT", "Shape": (0, 0) }]
        geocode._publish_new_leads(companies_fake)

        ids = []
        ids.append(companies_fake[0]['USER_id'])

        payload_fake = [{'attributes': {'carteiraid': 1001, 'mcc': None, 'nomeresponsavel': None, 'tipoalerta': 'ALERT_VISIT', 'id': 1, 'empresa': 'Nome Empresa', 'nomecontato': ' ', 'cnpjcpf': None, 'segmento': None, 'faixatpv': None, 'endereco': 'Rua Um', 'numero': '129', 'bairro': 'centro', 'cidade': 'São Paulo', 'estado': 'SP', 'complemento': ' ', 'latitude': 0, 'longitude': 0, 'telefone': None, 'clientepagseguro': 0, 'cnae': ' ', 'roteirizar': 1, 'tipopessoa': ' ', 'situacaocliente': ' ', 'receitapresumida': 0, 'origemempresa': ' ', 'maiorreceita': 0, 'datamaiorreceita': None, 'nomeexecutivo': 'Nome', 'polo': 100, 'carteira': 'Carteira 1001', 'origem': 0, 'cep': '00000-000', 'datageocodificacao': 123456789, 'dataidentificacaocarteira': 123456789}, 'geometry': {'x': 0, 'y': 0, 'spatialReference': {'wkid': 4326}}}]

        query_filter = 'id in (1)'
        mock_feature_server.delete_feature_data.assert_called_with(PARAMS_FAKE['leads_feature_url'], query_filter)
        mock_feature_server.post_feature_data.assert_called_with(PARAMS_FAKE['leads_feature_url'], payload_fake)

    @patch('service.geocode.utils')
    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.feature_server')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_publish_new_leads_error_delete_companies(self, mock_Tool, mock_Geodatabase, mock_feature_server, mock_Config, mock_BaseRoute, mock_utils):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        date_timestamp_fake = 123456789
        mock_utils.datetime_to_timestamp = MagicMock(return_value=date_timestamp_fake)

        mock_feature_server.post_feature_data = MagicMock(return_value=None)
        results_fake = [{'error': 'Boom!'}]
        mock_feature_server.delete_feature_data = MagicMock(return_value=results_fake[0])

        PARAMS_FAKE = {
            "leads_feature_url": "https://link-service-arcgis-server/feature/0"
        }

        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        geocode._deletion_features = MagicMock(return_value=['1'])

        companies_fake = [{ "FID_Carteiras": 1, "USER_id": 1, "USER_empresa": "Nome Empresa", "USER_endereco": "Rua Um", "USER_numero": "129", "USER_bairro": "centro", "USER_cidade": "São Paulo", "USER_estado": "SP", "id": 1,"nome": "Nome", "polo": 1, "USER_polo": None, "USER_carteiraid": None, "USER_carteira": None, "carteira": "Carteira", "USER_cep": "00000-000", "USER_roteirizar": 1, "USER_tipoalerta": "ALERT_VISIT", "Shape": (0, 0) }]
        geocode._publish_new_leads(companies_fake)

        ids = []
        ids.append(companies_fake[0]['USER_id'])

        payload_fake = [{'attributes': {'carteiraid': 1, 'mcc': None, 'nomeresponsavel': None, 'tipoalerta': 'ALERT_VISIT', 'id': 1, 'empresa': 'Nome Empresa', 'nomecontato': ' ', 'cnpjcpf': None, 'segmento': None, 'faixatpv': None, 'endereco': 'Rua Um', 'numero': '129', 'bairro': 'centro', 'cidade': 'São Paulo', 'estado': 'SP', 'complemento': ' ', 'latitude': 0, 'longitude': 0, 'telefone': None, 'clientepagseguro': 0, 'cnae': ' ', 'roteirizar': 1, 'tipopessoa': ' ', 'situacaocliente': ' ', 'receitapresumida': 0, 'origemempresa': ' ', 'maiorreceita': 0, 'datamaiorreceita': None, 'nomeexecutivo': 'Nome', 'polo': 1, 'carteira': 'Carteira', 'origem': 0, 'cep': '00000-000', 'datageocodificacao': 123456789, 'dataidentificacaocarteira': 123456789}, 'geometry': {'x': 0, 'y': 0, 'spatialReference': {'wkid': 4326}}}]

        query_filter = 'id in (1)'
        mock_feature_server.delete_feature_data.assert_called_with(PARAMS_FAKE['leads_feature_url'], query_filter)
        mock_feature_server.post_feature_data.assert_not_called()

    @patch('service.geocode.utils')
    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.feature_server')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_publish_new_leads(self, mock_Tool, mock_Geodatabase, mock_feature_server, mock_Config, mock_BaseRoute, mock_utils):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        date_timestamp_fake = 123456789
        mock_utils.datetime_to_timestamp = MagicMock(return_value=date_timestamp_fake)

        results_error_fake = [{'success': False}]
        mock_feature_server.post_feature_data = MagicMock(return_value=results_error_fake)
        results_fake = [{'success': True}]
        mock_feature_server.delete_feature_data = MagicMock(return_value=results_fake[0])

        PARAMS_FAKE = {
            "leads_feature_url": "https://link-service-arcgis-server/feature/0"
        }

        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        geocode._deletion_features = MagicMock(return_value=['1'])

        companies_fake = [{ "FID_Carteiras": 1, "USER_id": 1, "USER_empresa": "Nome Empresa", "USER_endereco": "Rua Um", "USER_numero": "129", "USER_bairro": "centro", "USER_cidade": "São Paulo", "USER_estado": "SP", "id": 1,"nome": "Nome", "polo": 1, "USER_polo": None, "USER_carteiraid": None, "USER_carteira": None, "carteira": "Carteira", "USER_cep": "00000-000", "USER_roteirizar": 1, "USER_tipoalerta": "ALERT_VISIT", "Shape": (0, 0) }]
        geocode._publish_new_leads(companies_fake)

        ids = []
        ids.append(companies_fake[0]['USER_id'])

        payload_fake = [{'attributes': {'carteiraid': 1, 'mcc': None, 'nomeresponsavel': None, 'tipoalerta': 'ALERT_VISIT', 'id': 1, 'empresa': 'Nome Empresa', 'nomecontato': ' ', 'cnpjcpf': None, 'segmento': None, 'faixatpv': None, 'endereco': 'Rua Um', 'numero': '129', 'bairro': 'centro', 'cidade': 'São Paulo', 'estado': 'SP', 'complemento': ' ', 'latitude': 0, 'longitude': 0, 'telefone': None, 'clientepagseguro': 0, 'cnae': ' ', 'roteirizar': 1, 'tipopessoa': ' ', 'situacaocliente': ' ', 'receitapresumida': 0, 'origemempresa': ' ', 'maiorreceita': 0, 'datamaiorreceita': None, 'nomeexecutivo': 'Nome', 'polo': 1, 'carteira': 'Carteira', 'origem': 0, 'cep': '00000-000', 'datageocodificacao': 123456789, 'dataidentificacaocarteira': 123456789}, 'geometry': {'x': 0, 'y': 0, 'spatialReference': {'wkid': 4326}}}]

        query_filter = 'id in (1)'
        mock_feature_server.delete_feature_data.assert_called_with(PARAMS_FAKE['leads_feature_url'], query_filter)
        mock_feature_server.post_feature_data.assert_called_with(PARAMS_FAKE['leads_feature_url'], payload_fake)

    @patch('service.geocode.utils')
    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.feature_server')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_delete_old_companies_not_geocode_table(self, mock_Tool, mock_Geodatabase, mock_feature_server, mock_Config, mock_BaseRoute, mock_utils):    
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {
            "non_geocode_companies": "https://link-service-arcgis-server/feature/10"
        }

        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)        
        
        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        companies_fake = {
            'geocoded': [],
            'not_geocoded': [{'USER_id': 1}]
        }
        geocode._delete_old_companies_not_geocode_table(companies_fake)        

        query_filter = "id in (1)"
        mock_feature_server.delete_feature_data.assert_called_with(PARAMS_FAKE['non_geocode_companies'], query_filter)
    
    @patch('service.geocode.utils')
    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.feature_server')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_sync_company_not_geocode_table(self, mock_Tool, mock_Geodatabase, mock_feature_server, mock_Config, mock_BaseRoute, mock_utils):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        date_timestamp_fake = 123456789
        mock_utils.datetime_to_timestamp = MagicMock(return_value=date_timestamp_fake)

        results_fake = [{'success': True}]
        mock_feature_server.post_feature_data = MagicMock(return_value=results_fake)

        date_20210424_09h00 = datetime.datetime(2021, 4, 24, 9, 0, 0)

        PARAMS_FAKE = {
            "non_geocode_companies": "https://link-service-arcgis-server/feature/10"
        }

        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        companies_fake = [{ 'USER_empresa': 'Nome Empresa',  'USER_id': 1, 'USER_clientepagseguro': 0, 'USER_origem': 0, "USER_endereco": "Rua Um", "USER_numero": "129", "USER_complemento": "Casa", "USER_bairro": "Centro", "USER_cidade": "São Paulo", "USER_estado": "SP", "USER_cep": "00000-000", "USER_enderecocompleto": "Rua Um, 129", "USER_roteirizar": 1, "USER_carteiraid": 100, "USER_tipoalerta": "XPTO", "USER_carteira": "Carteira", "USER_polo": "SP", "StPreType": "Rua", "StName": "Um", "AddNum": "129", "District": "Centro", "City": "São Paulo", "RegionAbbr": "SP", "Postal": "00000-000", "Match_addr": "Rua Um, 129", "Status": "M", "Score": 90, "Shape": (0, 0)}]
        geocode._sync_company_not_geocode_table(companies_fake)

        payload_fake = [{ 'empresa': 'Nome Empresa',  'id': 1, 'clientepagseguro': 0, 'origem': 0, "endereco": "Rua Um", "numero": "129", "bairro": "centro", "cidade": "São Paulo", "estado": "SP", "cep": "00000-000", "enderecocompleto": "Rua Um, 129", "geocode_tipoendereco": "Rua", "geocode_endereco": "Um", "geocode_numero": "129", "complemento": "Casa", "geocode_bairro": "Centro", "geocode_cidade": "São Paulo", "geocode_estado": "SP", "geocode_cep": "00000-000", "geocode_enderecocompleto": "Rua Um, 129", "geocode_longitude": 0, "geocode_latitude": 0, "geocode_status": "M", "geocode_score": 90, "datageocodificacao": date_20210424_09h00, 'dataidentificacaocarteira': date_20210424_09h00, "geocode_complemento": "Centro", "roteirizar": 1, "carteiraid": 100, "tipoalerta": "XPTO", "polo": "SP", "carteira": "Carteira" }]
        mock_feature_server.post_feature_data(PARAMS_FAKE['non_geocode_companies'], payload_fake)

    @patch('service.geocode.utils')
    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.feature_server')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_delete_rows_geocode_table(self, mock_Tool, mock_Geodatabase, mock_feature_server, mock_Config, mock_BaseRoute, mock_utils):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {
            "geocode_companies": "https://link-service-arcgis-server/feature/10"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)        

        mock_feature_server.delete_feature_data = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)
        geocode._delete_rows_geocode_table()

        query_filter = "1 = 1"
        mock_feature_server.delete_feature_data.assert_called_with(PARAMS_FAKE['geocode_companies'], query_filter)

    @patch('service.geocode.BaseRoute')
    @patch('service.geocode.Config')
    @patch('service.geocode.Geodatabase')
    @patch('service.geocode.Tool')
    def test_run(self, mock_Tool, mock_Geodatabase, mock_Config, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())
        geocode = Geocode(log_fake)

        geocode._synchronize_leads_for_geocode = MagicMock(return_value=None)
        geocode._synchronize_work_areas = MagicMock(return_value=None)
        geocode._geocode_leads = MagicMock(return_value=None)
        geocode._identify_work_areas = MagicMock(return_value=None)

        companies_fake = {
            'geocoded': [],
            'not_geocoded': []
        }
        geocode._validate_publish = MagicMock(return_value=companies_fake)

        geocode._publish_new_leads = MagicMock(return_value=None)
        geocode._delete_old_companies_not_geocode_table = MagicMock(return_value=None)
        geocode._sync_company_not_geocode_table = MagicMock(return_value=None)
        geocode._delete_rows_geocode_table = MagicMock(return_value=None)

        geocode.run()

        geocode._synchronize_leads_for_geocode.assert_called_with()
        geocode._synchronize_work_areas.assert_called_with()
        geocode._geocode_leads.assert_called_with()
        geocode._identify_work_areas.assert_called_with()
        geocode._validate_publish.assert_called_with()
        geocode._publish_new_leads.assert_called_with(companies_fake['geocoded'])
        geocode._delete_old_companies_not_geocode_table.assert_called_with(companies_fake)
        geocode._sync_company_not_geocode_table.assert_called_with(companies_fake['not_geocoded'])
        geocode._delete_rows_geocode_table.assert_called_with()

class LogFake:
    pass

class ArcpyFake:
    pass

class ObjectView(object):
    def __init__(self, d):
        self.__dict__ = d
