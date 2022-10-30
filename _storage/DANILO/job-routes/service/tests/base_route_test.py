from unittest import TestCase
from mock import patch, MagicMock
import datetime
from freezegun import freeze_time
import os

from service.base_route import BaseRoute

FT_WORK_AREAS = "Carteiras"
FT_WORK_AREAS_INTERSECT = "WorkArea_to_Inter"
FT_COMPANIES_TO_INTERSECT = "Companies_to_Inter"
FT_COMPANIES_INTERSECTED = "Compan_WorkAre_Upt"
WHERE_WORK_AREA_IS_NOT_NULL = "polo IS NOT NULL AND carteira IS NOT NULL AND inativo = 0"
HOLIDAYS = {
    "holidays": [{'day': '01', 'month': '01'}, {'day': '02', 'month': '04'}, {'day': '21', 'month': '04'}, {'day': '01', 'month': '05'}, {'day': '07', 'month': '09'}, {'day': '12', 'month': '10'}, {'day': '02', 'month': '11'}, {'day': '15', 'month': '11'}, {'day': '25', 'month': '12'}]
}

class TestBaseRoute(TestCase):

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.feature_server')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    def test_get_holidays(self, mock_Tool, mock_Geodatabase, mock_Config, mock_feature_server, mock_open, mock_json):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)
        
        PARAMS_FAKE = {
            "user_hierarchies": "https://link-service-arcgis-server/feature/10"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)

        result = base_route._get_holidays()

        holidays_expected = HOLIDAYS["holidays"]

        self.assertEqual(result, holidays_expected)
    
    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    def test_get_route_day(self, mock_Tool, mock_Geodatabase, mock_Config, mock_open, mock_json):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Config.return_value.get_params = MagicMock(return_value=None)
        mock_Geodatabase = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)

        date = datetime.datetime(2021, 12, 13, 9, 0, 0)
        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)        
        result = base_route.get_route_day(date)

        result_expected = datetime.datetime(2021, 12, 14, 9, 0, 0)
        self.assertEqual(result, result_expected)

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.feature_server')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    def test_get_user_hierarchies(self, mock_Tool, mock_Geodatabase, mock_Config, mock_feature_server, mock_open, mock_json):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)
        
        PARAMS_FAKE = {
            "user_hierarchies": "https://link-service-arcgis-server/feature/10"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        user_hierarchies_fake = [{'attributes': {'nome': 'John'}}]
        mock_feature_server.get_feature_data = MagicMock(return_value=user_hierarchies_fake)

        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)

        result = base_route._get_user_hierarchies()

        self.assertEqual(result, user_hierarchies_fake)

    @freeze_time("2021-03-15")
    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    def test_start_route_day(self, mock_Tool, mock_Geodatabase, mock_Config, mock_open, mock_json):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        

        PARAMS_FAKE = {
                        "route": {
                            "next_days": 1,
                            "start_time": {
                            "hour": 9,
                            "minute": 0
                         }
                        }
                }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        date_expected = datetime.datetime(2021, 3, 16, 9, 0, 0)
        
        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)
        start_route_day = base_route.start_route_day()

        self.assertEqual(start_route_day, date_expected)

    @patch('service.base_route.json')
    @patch('service.base_route.open')    
    @patch('service.base_route.feature_server')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    @patch('service.base_route.utils')
    def test_normalize_companies_server(self, mock_utils, mock_Tool, mock_Geodatabase, mock_Config, mock_feature_server, mock_open, mock_json):

        date20211213 = datetime.datetime(2021, 12, 13, 9, 0, 0)
        mock_utils.timestamp_to_datetime = MagicMock(return_value=date20211213)
        mock_utils.datetime_to_timestamp = MagicMock(return_value=123456)

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        companies_intersected_fake = {
            10: {'id_1': 1, 'polo': 'San Francisco', 'carteira': 'Central', 'nome': 'Juan'},
            20: {'id_1': 1, 'polo': 'San Francisco', 'carteira': 'Central', 'nome': 'Juan'}
        }
        mock_Geodatabase.return_value.search_data = MagicMock(return_value=companies_intersected_fake)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        

        PARAMS_FAKE = {
            "work_areas_feature_url": "https://link-service-arcgis-server/feature/1",
            "leads_feature_url": "https://link-service-arcgis-server/feature/2",
            "company_name": "Empresas"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        work_areas_fake = [{'attributes': {'id': 1, 'polo': 'San Francisco', 'carteira': 'Central', 'nome': 'Juan', 'created_date': 123456789}}]
        companies_fake = [
            {'attributes': { 'id': 10, 'carteiraid': 1}, 'geometry': {'x': 123, 'y': 321}}, 
            {'attributes': { 'id': 20, 'carteiraid': 1}, 'geometry': {'x': 123, 'y': 321}},
            {'attributes': { 'id': 30, 'carteiraid': 2}, 'geometry': {'x': 123, 'y': 321}}
            ]
        mock_feature_server.get_feature_data = MagicMock(side_effect=[work_areas_fake, companies_fake])

        mock_feature_server.update_feature_data = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)
        base_route.normalize_companies_server()
        
        mock_Geodatabase.return_value.copy_template_feature_to_temp_gdb.assert_any_call(PARAMS_FAKE['company_name'], FT_COMPANIES_TO_INTERSECT)
        
        companies_to_insert_fake = [
            {
                'attributes': {'id': 10},
                'geometry': {'x': 123, 'y': 321}
            },
            {
                'attributes': {'id': 20},
                'geometry': {'x': 123, 'y': 321}
            },
            {
                'attributes': {'id': 30},
                'geometry': {'x': 123, 'y': 321}
            }]
        mock_Geodatabase.return_value.insert_data.assert_any_call(companies_to_insert_fake, FT_COMPANIES_TO_INTERSECT, ["id", "SHAPE@XY"])
        
        mock_Geodatabase.return_value.copy_template_feature_to_temp_gdb.assert_any_call(FT_WORK_AREAS, FT_WORK_AREAS_INTERSECT, "POLYGON")
        
        mock_Geodatabase.return_value.insert_data.assert_any_call(work_areas_fake, FT_WORK_AREAS_INTERSECT, ["id", "carteira", "polo", "nome", "SHAPE@JSON"])
        
        mock_Tool.return_value.intersect.assert_called_with(FT_COMPANIES_TO_INTERSECT, FT_WORK_AREAS_INTERSECT, FT_COMPANIES_INTERSECTED)
        
        mock_Geodatabase.return_value.search_data.assert_called_with(FT_COMPANIES_INTERSECTED, ["id", "id_1", "carteira", "polo", "nome"], dict_key="id")

        mock_feature_server.get_feature_data.assert_any_call(PARAMS_FAKE['work_areas_feature_url'], WHERE_WORK_AREA_IS_NOT_NULL)
        where_fake = "((nomeexecutivo IS NULL OR nomeexecutivo = ' ' OR polo IS NULL or carteira IS NULL or carteira = ' ') AND carteiraid IS NOT NULL AND roteirizar = 1) OR roteirizar = 1 AND dataidentificacaocarteira < Date '2021-12-13 23:59:59' OR roteirizar = 1 AND dataidentificacaocarteira IS NULL"
        mock_feature_server.get_feature_data.assert_any_call(PARAMS_FAKE['leads_feature_url'], where_fake)

        companies_to_update = [
            {'attributes': { 'id': 10, 'carteiraid': 1, 'dataidentificacaocarteira': 123456, 'polo': 'San Francisco', 'carteira': 'Central', 'nomeexecutivo': 'Juan'}, 'geometry': {'x': 123, 'y': 321}}, 
            {'attributes': { 'id': 20, 'carteiraid': 1, 'dataidentificacaocarteira': 123456, 'polo': 'San Francisco', 'carteira': 'Central', 'nomeexecutivo': 'Juan'}, 'geometry': {'x': 123, 'y': 321}},
            {'attributes': { 'id': 30, 'carteiraid': 2, 'dataidentificacaocarteira': 123456, 'roteirizar': 0 }, 'geometry': {'x': 123, 'y': 321}}
            ]
        mock_feature_server.update_feature_data.assert_called_with(PARAMS_FAKE['leads_feature_url'], companies_to_update)

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.feature_server')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    @patch('service.base_route.utils')
    def test_normalize_companies_server_without_companies(self, mock_utils, mock_Tool, mock_Geodatabase, mock_Config, mock_feature_server, mock_open, mock_json):

        date20211213 = datetime.datetime(2021, 12, 13, 9, 0, 0)
        mock_utils.timestamp_to_datetime = MagicMock(return_value=date20211213)
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        

        PARAMS_FAKE = {
            "work_areas_feature_url": "https://link-service-arcgis-server/feature/1",
            "leads_feature_url": "https://link-service-arcgis-server/feature/2"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        work_areas_fake = [{'attributes': {'id': 1, 'polo': 'San Francisco', 'carteira': 'Central', 'nome': 'Juan', 'created_date': 123456789}}]
        companies_fake = []
        mock_feature_server.get_feature_data = MagicMock(side_effect=[work_areas_fake, companies_fake])

        mock_feature_server.update_feature_data = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)        
        base_route.normalize_companies_server()

        mock_feature_server.get_feature_data.assert_any_call(PARAMS_FAKE['work_areas_feature_url'], WHERE_WORK_AREA_IS_NOT_NULL)
        where_fake = "((nomeexecutivo IS NULL OR nomeexecutivo = ' ' OR polo IS NULL or carteira IS NULL or carteira = ' ') AND carteiraid IS NOT NULL AND roteirizar = 1) OR roteirizar = 1 AND dataidentificacaocarteira < Date '2021-12-13 23:59:59' OR roteirizar = 1 AND dataidentificacaocarteira IS NULL"
        mock_feature_server.get_feature_data.assert_any_call(PARAMS_FAKE['leads_feature_url'], where_fake)

        mock_feature_server.update_feature_data.assert_not_called()

    @patch('service.base_route.json')
    @patch('service.base_route.open')    
    @patch('service.base_route.feature_server')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    def test_get_work_areas(self, mock_Tool, mock_Geodatabase, mock_Config, mock_feature_server, mock_open, mock_json):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        
        
        PARAMS_FAKE = {
            "work_areas_feature_url": "https://link-service-arcgis-server/feature/1"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        work_areas_fake = [1, 2]
        mock_feature_server.get_feature_data = MagicMock(return_value=work_areas_fake)
        
        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)        
        result = base_route.get_work_areas()

        self.assertEqual(result, work_areas_fake)
        mock_feature_server.get_feature_data.assert_called_with(PARAMS_FAKE["work_areas_feature_url"], WHERE_WORK_AREA_IS_NOT_NULL)

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.feature_server')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    def test_get_polo_and_travelmode_of_work_areas(self, mock_Tool, mock_Geodatabase, mock_Config, mock_feature_server, mock_open, mock_json):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)

        PARAMS_FAKE = {
            "work_areas_feature_url": "https://link-service-arcgis-server/feature/1"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        work_areas_fake = [{ 'attributes': {'id': 1}}, { 'attributes': {'id': 2}}]
        mock_feature_server.get_feature_data = MagicMock(return_value=work_areas_fake)

        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)        
        result = base_route.get_polo_and_travelmode_of_work_areas()

        result_expected = [{'id': 1}, {'id': 2}]
        self.assertEqual(result, result_expected)
        mock_feature_server.get_feature_data.assert_called_with(PARAMS_FAKE["work_areas_feature_url"], WHERE_WORK_AREA_IS_NOT_NULL, "polo, modoviagem", False)

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.feature_server')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    def test_get_carteira_and_travelmode_of_work_areas(self, mock_Tool, mock_Geodatabase, mock_Config, mock_feature_server, mock_open, mock_json):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        

        PARAMS_FAKE = {
            "work_areas_feature_url": "https://link-service-arcgis-server/feature/1"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        work_areas_fake = [{ 'attributes': {'id': 1}}, { 'attributes': {'id': 2}}]
        mock_feature_server.get_feature_data = MagicMock(return_value=work_areas_fake)

        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)        
        result = base_route.get_carteira_and_travelmode_of_work_areas()

        result_expected = [{'id': 1}, {'id': 2}]
        self.assertEqual(result, result_expected)
        mock_feature_server.get_feature_data.assert_called_with(PARAMS_FAKE["work_areas_feature_url"], WHERE_WORK_AREA_IS_NOT_NULL, "id, modoviagem, distanciatotalroteiro", False)        

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.utils')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    def test_construct_payload(self, mock_Tool, mock_Geodatabase, mock_Config, mock_utils, mock_open, mock_json):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        
        
        mock_utils.datetime_to_timestamp = MagicMock(side_effect=[12456, 124567, 12456789])

        hierarchy_fake = {
            'Supervisor': 'Karla Biaca Correa',
            'Coordenador': 'Anderson de Oliveira Bonilha',
            'Gerente': 'Guilherme Ribeiro Gomes',
            'Gerente Geral': 'Eduardo Macedo Esteves'
        }

        result_expected = {
            "attributes": {
                "empresaid": 10,
                "executivoid": 20,
                "nome": "John Silva",
                "realizado": 0,
                "sequencia": 1,
                "dataprogramada": 12456,
                "datacriacao": 124567,
                "dataagendada": 12456789,
                "agendamentoid": 123,
                "polo": "Region A",
                "carteira": "Central",
                "empresa": "Company Foods",
                "endereco": "Av 9 Julho",
                "numero": "100",
                "cidade": "Sao Paulo",
                "estado": "SP",
                "bairro": "Centro",
                "cep": "11236-963",
                "origem": 0,
                "foracarteira": 0,
                "inativo": 0,
                "gerenciageral": hierarchy_fake['Gerente Geral'],
                "gerencia": hierarchy_fake['Gerente'],
                "coordenacao": hierarchy_fake['Coordenador'],
                "supervisao": hierarchy_fake['Supervisor'],
                "carteiraid": 30,
                "cnpjcpf": "123456789",
                "idpagseguro": 123,
                "nomeusuarioexecutivo": "jsilva",
                "tipoalerta": "ALERT_VISIT",
            },
            "geometry": {
                "x": 1234.56,
                "y": -6543.21,
                "spatialReference": {
                    "wkid": 4326
                }
            }}

        params_att = result_expected['attributes']
        params_geom = result_expected['geometry']

        date_20210316 = datetime.datetime(2021, 3, 16, 0, 0, 0)
        visit_date = date_20210316
        creation_date = date_20210316
        date_scheduled = date_20210316
        id_scheduled = 123

        company = {
            "id": params_att['empresaid'],
            "empresa": params_att['empresa'],
            "endereco": params_att["endereco"],
            "numero": params_att["numero"],
            "cidade": params_att["cidade"],
            "estado": params_att["estado"],
            "bairro": params_att["bairro"],
            "cep": params_att["cep"],
            "cnpjcpf": params_att["cnpjcpf"],
            "idpagseguro": params_att["idpagseguro"],
            "tipoalerta": params_att["tipoalerta"]
        }
        executive = {
            "id": params_att['executivoid'],
            "nome": params_att['nome'],
            "nomeusuarioexecutivo": params_att["nomeusuarioexecutivo"]
        }
        
        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)

        base_route._get_name_superiors = MagicMock(return_value=hierarchy_fake)

        work_area = {
            'id': 30,
            'polo': params_att['polo'],
            'carteira': params_att['carteira']
        }

        result = base_route.construct_payload(
            company, executive, 
            params_att['sequencia'], visit_date, creation_date, date_scheduled, id_scheduled,
            work_area,
            params_geom['x'], params_geom['y'])

        self.assertEqual(result, result_expected)

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.utils')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    def test_construct_payload_without_sheduling(self, mock_Tool, mock_Geodatabase, mock_Config, mock_utils, mock_open, mock_json):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        
        
        mock_utils.datetime_to_timestamp = MagicMock(side_effect=[12456, 124567])

        hierarchy_fake = {
            'Supervisor': 'Karla Biaca Correa',
            'Coordenador': 'Anderson de Oliveira Bonilha',
            'Gerente': 'Guilherme Ribeiro Gomes',
            'Gerente Geral': 'Eduardo Macedo Esteves'
        }

        result_expected = {
            "attributes": {
                "empresaid": 10,
                "executivoid": 20,
                "nome": "John Silva",
                "realizado": 0,
                "sequencia": 1,
                "dataprogramada": 12456,
                "datacriacao": 124567,
                "dataagendada": None,
                "agendamentoid": None,
                "polo": "Region A",
                "carteira": "Central",
                "empresa": "Company Foods",
                "endereco": "Av 9 Julho",
                "numero": "100",
                "cidade": "Sao Paulo",
                "estado": "SP",
                "bairro": "Centro",
                "cep": "11236-963",
                "origem": 0,
                "foracarteira": 0,
                "inativo": 0,
                "gerenciageral": hierarchy_fake['Gerente Geral'],
                "gerencia": hierarchy_fake['Gerente'],
                "coordenacao": hierarchy_fake['Coordenador'],
                "supervisao": hierarchy_fake['Supervisor'],
                "carteiraid": 30,
                "cnpjcpf": "123456789",
                "idpagseguro": 123,
                "nomeusuarioexecutivo": "jsilva",
                "tipoalerta": "ALERT_VISIT"
            },
            "geometry": {
                "x": 1234.56,
                "y": -6543.21,
                "spatialReference": {
                    "wkid": 4326
                }
            }}

        params_att = result_expected['attributes']
        params_geom = result_expected['geometry']

        date_20210316 = datetime.datetime(2021, 3, 16, 0, 0, 0)
        visit_date = date_20210316
        creation_date = date_20210316
        date_scheduled = None
        id_scheduled = None

        company = {
            "id": params_att['empresaid'],
            "empresa": params_att['empresa'],
            "endereco": params_att["endereco"],
            "numero": params_att["numero"],
            "cidade": params_att["cidade"],
            "estado": params_att["estado"],
            "bairro": params_att["bairro"],
            "cep": params_att["cep"],
            "cnpjcpf": params_att["cnpjcpf"],
            "idpagseguro": params_att["idpagseguro"],
            "tipoalerta": params_att["tipoalerta"]
        }
        executive = {
            "id": params_att['executivoid'],
            "nome": params_att['nome'],
            "nomeusuarioexecutivo": params_att["nomeusuarioexecutivo"]
        }

        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)

        base_route._get_name_superiors = MagicMock(return_value=hierarchy_fake)

        work_area = {
            'id': 30,
            'polo': params_att['polo'],
            'carteira': params_att['carteira']
        }

        result = base_route.construct_payload(
            company, executive,
            params_att['sequencia'], visit_date, creation_date, date_scheduled, id_scheduled,
            work_area,
            params_geom['x'], params_geom['y'])

        self.assertEqual(result, result_expected)

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    def test_get_name_feature_filtered(self, mock_Tool, mock_Geodatabase, mock_Config, mock_open, mock_json):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        

        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)

        name = "feature"
        result = base_route.get_name_feature_filtered(name)

        result_expected = os.path.join("in_memory", name + "_filtered")
        self.assertEqual(result, result_expected)

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.BaseRoute')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    def test_filter_data_in_feature(self, mock_Tool, mock_Geodatabase, mock_Config, mock_BaseRoute, mock_open, mock_json):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)
        
        log_fake = MagicMock(return_value=LogFake())
        
        base_route = BaseRoute(log_fake)
        
        base_route._arcpy = MagicMock(return_value=ArcpyFake())

        base_route.geodatabase.get_path = MagicMock(return_value="folder")
        name_feature_filtered = "name_feature_filtered"
        base_route.get_name_feature_filtered = MagicMock(return_value=name_feature_filtered)

        feature_filtered_fake = "feature filtered"
        base_route._arcpy.SelectLayerByAttribute_management = MagicMock(return_value=feature_filtered_fake)
        base_route._arcpy.CopyFeatures_management = MagicMock(return_value=None)

        feature_name = "name_feature"
        where = "1=1"
        base_route.filter_data_in_feature(feature_name, where)

        feature = os.path.join("folder", feature_name)
        base_route._arcpy.SelectLayerByAttribute_management.assert_called_with(feature, "NEW_SELECTION", where)
        base_route.get_name_feature_filtered.assert_called_with(feature_name)
        base_route._arcpy.CopyFeatures_management.assert_called_with(feature_filtered_fake, name_feature_filtered)

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    def test_filter_area_by_polo_travelmode(self, mock_Tool, mock_Geodatabase, mock_Config, mock_open, mock_json):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        

        log_fake = MagicMock(return_value=LogFake())
        
        base_route = BaseRoute(log_fake)

        area = { 'attributes': { 'id': 1 ,'polo': 'Region A', 'modoviagem': 'Walking' } }
        polo_travelmode = { 'polo': 'Region A', 'modoviagem': 'Walking' }
        result = base_route.filter_area_by_polo_travelmode(area, polo_travelmode)

        self.assertEqual(result, True)        

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    def test_filter_company(self, mock_Tool, mock_Geodatabase, mock_Config, mock_open, mock_json):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)    
        log_fake = MagicMock(return_value=LogFake())

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        
        
        base_route = BaseRoute(log_fake)

        base_route.filter_data_in_feature = MagicMock(return_value=None)

        base_route.filter_area_by_polo_travelmode = MagicMock(side_effect=[True, True])
        
        polo_travelmode = { 'polo': 'Region A', 'modoviagem': 'Walking' }
        work_areas_fake = [{'attributes': {'id': 1, 'polo': 'Region A', 'modoviagem': 'Walking'}}, {'attributes': {'id': 2, 'polo': 'Region A', 'modoviagem': 'Walking'}}]
        base_route.filter_company(polo_travelmode, work_areas_fake)

        base_route.filter_area_by_polo_travelmode.assert_any_call(work_areas_fake[0], polo_travelmode)
        base_route.filter_area_by_polo_travelmode.assert_any_call(work_areas_fake[1], polo_travelmode)
        base_route.filter_data_in_feature.assert_called_with("Empresas", "carteiraId IN (1,2)")

    @freeze_time("2021-03-28")
    @patch('service.base_route.json')
    @patch('service.base_route.open')    
    @patch('service.base_route.BaseRoute')
    @patch('service.base_route.feature_server')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')  
    @patch('service.base_route.Tool')  
    def test_delete_unrealized_routes(self, mock_Tool, mock_Geodatabase, mock_Config, mock_feature_server, mock_BaseRoute, mock_open, mock_json):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        

        PARAMS_FAKE = {
            "routes_feature_url": "https://link-service-arcgis-server/feature/1"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)


        RESPONSE_FAKE = { 'deleteResults': [ { 'success': True } ]}
        mock_feature_server.delete_feature_data = MagicMock(return_value=RESPONSE_FAKE)
        
        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)

        datetime_fake = datetime.datetime(2021, 3, 29, 9, 0, 0)
        base_route.get_route_day = MagicMock(return_value=datetime_fake)

        base_route.geodatabase = MagicMock(return_value=None)

        executives_ids = ['1', '2']
        base_route._delete_unrealized_routes(executives_ids)
        now_expected = datetime.datetime(2021, 3, 28, 0, 0, 0)
        base_route.get_route_day.assert_called_with(now_expected)

        query_filter = "inativo = 1 AND dataprogramada >= DATE '2021-3-29' AND realizado = 0 AND executivoid IN (1,2)"
        mock_feature_server.delete_feature_data.assert_called_with(PARAMS_FAKE['routes_feature_url'], query_filter)

    @freeze_time("2021-03-28")
    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.BaseRoute')
    @patch('service.base_route.feature_server')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')  
    @patch('service.base_route.Tool')  
    def test_inactive_unrealized_routes(self, mock_Tool, mock_Geodatabase, mock_Config, mock_feature_server, mock_BaseRoute, mock_open, mock_json):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        

        PARAMS_FAKE = {
            "routes_feature_url": "https://link-service-arcgis-server/feature/1"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        RESPONSE_FAKE = 1
        mock_feature_server.calculate_feature_data = MagicMock(return_value=RESPONSE_FAKE)
        
        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)

        datetime_fake = datetime.datetime(2021, 3, 29, 9, 0, 0)
        base_route.get_route_day = MagicMock(return_value=datetime_fake)

        base_route.geodatabase = MagicMock(return_value=None)

        executives_ids = ['1', '2']
        base_route._inactive_unrealized_routes(executives_ids)
        base_route.get_route_day.assert_called_with()

        calc_expression = [{'field': 'inativo', 'value': 1}]
        where = "dataprogramada >= DATE '2021-3-29' AND realizado = 0 AND executivoid IN (1,2)"
        mock_feature_server.calculate_feature_data.assert_called_with(PARAMS_FAKE['routes_feature_url'], where, calc_expression)

    @freeze_time("2021-03-28")
    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.BaseRoute')
    @patch('service.base_route.feature_server')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase') 
    @patch('service.base_route.Tool')   
    def test_inactive_unrealized_routes_reverse(self, mock_Tool, mock_Geodatabase, mock_Config, mock_feature_server, mock_BaseRoute, mock_open, mock_json):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)

        PARAMS_FAKE = {
            "routes_feature_url": "https://link-service-arcgis-server/feature/1"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        RESPONSE_FAKE = 1
        mock_feature_server.calculate_feature_data = MagicMock(return_value=RESPONSE_FAKE)
        
        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)

        datetime_fake = datetime.datetime(2021, 3, 29, 9, 0, 0)
        base_route.get_route_day = MagicMock(return_value=datetime_fake)

        base_route.geodatabase = MagicMock(return_value=None)

        executives_ids = ['1', '2']
        base_route._inactive_unrealized_routes(executives_ids, True)
        base_route.get_route_day.assert_called_with()

        calc_expression = [{'field': 'inativo', 'value': 0}]
        where = "dataprogramada >= DATE '2021-3-29' AND realizado = 0 AND executivoid IN (1,2)"
        mock_feature_server.calculate_feature_data.assert_called_with(PARAMS_FAKE['routes_feature_url'], where, calc_expression)                

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.utils')
    @patch('service.base_route.feature_server')
    @patch('service.base_route.Config')
    @patch('service.base_route.BaseRoute')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.Tool')
    def test_publish_routes(self, mock_Tool, mock_Geodatabase, mock_BaseRoute, mock_Config, mock_feature_server, mock_utils, mock_open, mock_json):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        

        PARAMS_FAKE = {
            "routes_feature_url": "https://link-service-arcgis-server/feature/1"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)            
        
        mock_utils.get_unique_values_from_items = MagicMock(return_value=[10])

        results_fake = [{'success': True}]
        mock_feature_server.post_feature_data = MagicMock(return_value=results_fake)
        
        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)

        base_route._inactive_unrealized_routes = MagicMock(return_value=None)

        executives_ids = ['10']
        routes = [{'attributes': {'executivoid': 10}}]
        base_route._publish_routes(executives_ids, routes)

        mock_utils.get_unique_values_from_items.assert_called_with('executivoid', [routes[0]['attributes']])
        mock_feature_server.post_feature_data.assert_called_with(PARAMS_FAKE['routes_feature_url'], routes)
        base_route.logger.error.assert_not_called()
        base_route._inactive_unrealized_routes.assert_not_called()

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.utils')
    @patch('service.base_route.feature_server')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.BaseRoute')
    @patch('service.base_route.Tool')
    def test_publish_routes_error_post(self, mock_Tool, mock_BaseRoute, mock_Geodatabase, mock_Config, mock_feature_server, mock_utils, mock_open, mock_json):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        

        PARAMS_FAKE = {
            "routes_feature_url": "https://link-service-arcgis-server/feature/1"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)            
        
        mock_utils.get_unique_values_from_items = MagicMock(return_value=[10])

        results_fake = [{'success': False}]
        mock_feature_server.post_feature_data = MagicMock(return_value=results_fake)
        
        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)

        base_route._inactive_unrealized_routes = MagicMock(return_value=None)

        executives_ids = ['10']
        routes = [{'attributes': {'executivoid': 10}}]
        base_route._publish_routes(executives_ids, routes)

        mock_utils.get_unique_values_from_items.assert_called_with('executivoid', [routes[0]['attributes']])
        mock_feature_server.post_feature_data.assert_called_with(PARAMS_FAKE['routes_feature_url'], routes)
        base_route.logger.error.assert_called_with('Falha ao inserir os roteios da executive_id 10')
        base_route._inactive_unrealized_routes.assert_called_with(executives_ids, True)

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.utils')
    @patch('service.base_route.feature_server')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.BaseRoute')
    @patch('service.base_route.Tool')
    def test_publish_routes_exception_post(self, mock_Tool, mock_BaseRoute, mock_Geodatabase, mock_Config, mock_feature_server, mock_utils, mock_open, mock_json):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        

        PARAMS_FAKE = {
            "routes_feature_url": "https://link-service-arcgis-server/feature/1"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)            
        
        mock_utils.get_unique_values_from_items = MagicMock(return_value=[10])

        mock_feature_server.post_feature_data = MagicMock(return_value=Exception('Boom!'))
        
        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)

        base_route._inactive_unrealized_routes = MagicMock(return_value=None)

        with self.assertRaises(Exception):
            executives_ids = ['10']
            routes = [{'attributes': {'executivoid': 10}}]
            base_route._publish_routes(executives_ids, routes)

        mock_utils.get_unique_values_from_items.assert_called_with('executivoid', [routes[0]['attributes']])
        mock_feature_server.post_feature_data.assert_called_with(PARAMS_FAKE['routes_feature_url'], routes)
        base_route.logger.error.assert_not_called()
        base_route._inactive_unrealized_routes.assert_called_with(executives_ids, True)

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.BaseRoute')
    @patch('service.base_route.Tool')
    def test_publish_new_routes(self, mock_Tool, mock_BaseRoute, mock_Geodatabase, mock_Config, mock_open, mock_json):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        

        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)

        base_route._inactive_unrealized_routes = MagicMock(return_value=None)
        base_route._publish_routes = MagicMock(return_value=None)
        base_route._delete_unrealized_routes = MagicMock(return_value=None)     

        executives_ids = ['10']
        routes = [{'attributes': {'executivoid': 10}}]
        base_route.publish_new_routes(executives_ids, routes)

        base_route._inactive_unrealized_routes.assert_called_with(executives_ids)
        base_route._publish_routes.assert_called_with(executives_ids, routes)
        base_route._delete_unrealized_routes.assert_called_with(executives_ids)

    @patch('service.base_route.json')
    @patch('service.base_route.open')
    @patch('service.base_route.Config')
    @patch('service.base_route.Geodatabase')
    @patch('service.base_route.BaseRoute')
    @patch('service.base_route.Tool')
    def test_get_name_superiors(self, mock_Tool, mock_BaseRoute, mock_Geodatabase, mock_Config, mock_open, mock_json):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        mock_Config.return_value.get_folder_main = MagicMock(return_value="folder_main")
        mock_json.load = MagicMock(return_value=HOLIDAYS)        

        log_fake = MagicMock(return_value=LogFake())
        base_route = BaseRoute(log_fake)

        work_area_id = 1158501
        user_hierarchies_fake = [
            {
                "attributes": {
                    "usuario": "eesteves",
                    "nome": "Eduardo Macedo Esteves",
                    "email": "eesteves@uolinc.com",
                    "perfil": "Gerente Geral",
                    "usuariosuperior": None,
                    "id": 5,
                    "carteiraid": None
                }
            },
            {
                "attributes": {
                    "usuario": "gugomes",
                    "nome": "Guilherme Ribeiro Gomes",
                    "email": "gugomes@uolinc.com",
                    "perfil": "Gerente",
                    "usuariosuperior": "eesteves",
                    "id": 4,
                    "carteiraid": None
                }
            },
            {
                "attributes": {
                    "usuario": "abonilha",
                    "nome": "Anderson de Oliveira Bonilha",
                    "email": "abonilha@uolinc.com",
                    "perfil": "Coordenador",
                    "usuariosuperior": "gugomes",
                    "id": 3,
                    "carteiraid": None
                }
            },
            {
                "attributes": {
                    "usuario": "kcorrea",
                    "nome": "Karla Biaca Correa",
                    "email": "kcorrea@uolinc.com",
                    "perfil": "Supervisor",
                    "polo": "SP Jundiaí",
                    "usuariosuperior": "abonilha",
                    "id": 2,
                    "carteiraid": None
                }
            },
            {
                "attributes": {
                    "usuario": "tgabriel",
                    "nome": "Toniel Batista Gabriel",
                    "email": "tgabriel@uolinc.com",
                    "perfil": "Executivo",
                    "polo": "SP Jundiaí",
                    "carteira": "01 Jardim Santa Gertrudes",
                    "carteiraid": 1158501,
                    "usuariosuperior": "kcorrea",
                    "id": 1
                }
            }
        ]

        base_route._get_user_hierarchies = MagicMock(return_value=user_hierarchies_fake)

        result = base_route._get_name_superiors(work_area_id)

        result_expected = {
            'Supervisor': 'Karla Biaca Correa',
            'Coordenador': 'Anderson de Oliveira Bonilha',
            'Gerente': 'Guilherme Ribeiro Gomes',
            'Gerente Geral': 'Eduardo Macedo Esteves'
        }
        
        self.assertEqual(result, result_expected)




class ArcpyFake:
    pass
class LogFake:
    pass