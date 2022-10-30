from unittest import TestCase
from mock import patch, MagicMock
from freezegun import freeze_time
import random
import datetime
import os

from service.vehicle_routing_problem import VehicleRoutingProblem

LAYER_NAME_ROUTE = "WorkVehicleRoutingProblem"
TRAVEL_MODE = "Walking Time"

class TestVehicleRoutingProblem(TestCase):

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_make_layer_route(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)
        
        PARAMS_FAKE = {
            "path_network_layer": "path/dir/network_routing"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        
        vrp = VehicleRoutingProblem(log_fake)

        vrp._arcpy = MagicMock(return_value=ArcpyFake())

        route_day_fake = datetime.datetime(2021, 4, 24, 0, 0, 0)
        vrp.base_route.start_route_day = MagicMock(return_value=route_day_fake)

        MakeVehicleRoutingProblemAnalysisLayer_fake = MagicMock()
        MakeVehicleRoutingProblemAnalysisLayer_fake.getOutput = MagicMock(return_value=None)
        vrp._arcpy.na.MakeVehicleRoutingProblemAnalysisLayer = MagicMock(return_value=MakeVehicleRoutingProblemAnalysisLayer_fake)

        #describe_fake = MagicMock()
        #describe_fake.network.catalogPath = MagicMock(return_value=None)
        #vrp._arcpy.Describe = MagicMock(return_value=describe_fake)
        vrp._arcpy.na.GetTravelModes = MagicMock(return_value=None)

        vrp._arcpy.na.GetSolverProperties = MagicMock(return_value=None)

        vrp._make_layer_route()

        vrp.base_route.start_route_day.assert_called_with()
        
        vrp._arcpy.na.MakeVehicleRoutingProblemAnalysisLayer.assert_called_with(
            PARAMS_FAKE['path_network_layer'], 
            LAYER_NAME_ROUTE, 
            TRAVEL_MODE, 
            "Minutes", "Meters", route_day_fake, "LOCAL_TIME_AT_LOCATIONS", "ALONG_NETWORK", "Medium", "Medium", "DIRECTIONS", "CLUSTER")

        MakeVehicleRoutingProblemAnalysisLayer_fake.getOutput.assert_called_with(0)
        #vrp._arcpy.Describe.assert_called_with(None)
        #vrp._arcpy.na.GetTravelModes.assert_called_with(describe_fake.network.catalogPath)
        vrp._arcpy.na.GetTravelModes.assert_called_with(PARAMS_FAKE['path_network_layer'])
        vrp._arcpy.na.GetSolverProperties.assert_called_with(None)

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_get_work_areas(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())
        
        vrp = VehicleRoutingProblem(log_fake)

        work_areas_fake = [1, 2]
        vrp.base_route.get_work_areas = MagicMock(return_value=work_areas_fake)        

        result = vrp._get_work_areas()

        self.assertEqual(result, work_areas_fake)
        vrp.base_route.get_work_areas.assert_called_with()

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_get_work_areas_with_values(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())
        
        vrp = VehicleRoutingProblem(log_fake)

        vrp.base_route.get_work_areas = MagicMock(return_value=None)
        
        work_areas_fake = [1, 2]
        vrp.work_areas = work_areas_fake

        result = vrp._get_work_areas()

        self.assertEqual(result, work_areas_fake)
        vrp.base_route.get_work_areas.assert_not_called()

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_create_feature_in_memory(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())
        
        vrp = VehicleRoutingProblem(log_fake)

        vrp._arcpy = MagicMock(return_value=ArcpyFake())

        describe_fake = DescribeFake()
        vrp._arcpy.Describe = MagicMock(return_value=describe_fake)
        
        feature_template_fake = "OrdersX" 
        vrp.geodatabase.get_path_feature = MagicMock(return_value=feature_template_fake)

        vrp._arcpy.CreateFeatureclass_management = MagicMock(return_value=None)

        feature_name = 'Orders_All'
        feature_template_name = 'Orders'
        vrp._create_feature_in_memory(feature_name, feature_template_name)

        vrp.geodatabase.get_path_feature.assert_called_with(feature_template_name)
        vrp._arcpy.CreateFeatureclass_management.assert_called_with("in_memory", feature_name, "POINT", feature_template_fake, "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", "SIRGAS2000")

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_append_orders_all(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())

        vrp = VehicleRoutingProblem(log_fake)

        vrp._arcpy = MagicMock(return_value=ArcpyFake())
        feature_orders_fake = 'OrdersX'
        vrp.geodatabase.get_path_feature = MagicMock(return_value=feature_orders_fake)

        vrp._arcpy.Append_management = MagicMock(return_value=None)

        vrp._append_orders_all()

        vrp.geodatabase.get_path_feature.assert_called_with("Orders")
        feature_orders_all = os.path.join("in_memory", 'Orders_All')
        vrp._arcpy.Append_management.assert_called_with(feature_orders_fake, feature_orders_all, "NO_TEST")

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_clear_objects_vrp(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())

        vrp = VehicleRoutingProblem(log_fake)

        vrp.geodatabase.clear_objects = MagicMock(return_value=None)

        vrp._clear_objects_vrp()

        features = ['Routes', 'RouteZones', 'Depots', 'Orders']
        vrp.geodatabase.clear_objects.assert_called_with(features)

    @patch('service.vehicle_routing_problem.utils')
    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.feature_server')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_register_companies_with_violations(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_feature_server, mock_BaseRoute, mock_utils):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {
            "leads_feature_url": "https://link-service-arcgis-server/feature/1",
            "non_route_companies_feature_url": "https://link-service-arcgis-server/feature/1"
        }        
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        vrp = VehicleRoutingProblem(log_fake)

        orders_with_violations_fake = [{
            'Name': '12345', 
            'ViolatedConstraint_1': 1, 
            'ViolatedConstraint_2': None, 
            'ViolatedConstraint_3': None, 
            'ViolatedConstraint_4': None, 
            'ViolatedConstraint_5': None
        }]
        vrp.geodatabase.search_data = MagicMock(return_value=orders_with_violations_fake)
        
        companies_fake = [{
            'attributes': {
                'objectid': 1,
                'globalid': 'ABC123456',
                'id': 12345,
                'empresa': 'ABC'
            },
            'geometry': {}
        }]
        mock_feature_server.get_feature_data = MagicMock(return_value=companies_fake)
        vrp.geodatabase.get_violated_domain = MagicMock(return_value="Max 5 KM")
        mock_utils.datetime_to_timestamp = MagicMock(return_value=123456789)
        mock_feature_server.delete_feature_data = MagicMock(return_value=None)
        
        results_fake = [{
            'success': True
        }]
        mock_feature_server.post_feature_data = MagicMock(return_value=results_fake)

        polo_travelmode = { 'id': '1', 'polo': 'Region A', 'modoviagem': 'Walking', 'distanciatotalroteiro': 10 }
        vrp._register_companies_with_violations(polo_travelmode)

        feature_orders_all = os.path.join("in_memory", 'Orders_All')
        vrp.geodatabase.search_data.assert_called_with(feature_orders_all, ['Name', 'ViolatedConstraint_1', 'ViolatedConstraint_2', 'ViolatedConstraint_3', 'ViolatedConstraint_4'], "ArriveTime IS NULL")

        mock_feature_server.get_feature_data.assert_called_with(PARAMS_FAKE['leads_feature_url'], "id in (12345)")
        vrp.geodatabase.get_violated_domain.assert_called_with(orders_with_violations_fake[0]['ViolatedConstraint_1'])
        mock_feature_server.delete_feature_data.assert_called_with(PARAMS_FAKE['non_route_companies_feature_url'], "carteiraid = 1")
        payload_companies_with_violations_fake = [{
            'attributes': {
                'id': 12345,
                'empresa': 'ABC',
                'violacaoregra1': 'Max 5 KM',
                'datageracaorota': 123456789
            },
            'geometry': {
                'z': 0,
                'spatialReference': {'wkid':102100, 'latestWkid': 3857}
            }
        }]
        mock_feature_server.post_feature_data.assert_called_with(PARAMS_FAKE['non_route_companies_feature_url'], payload_companies_with_violations_fake)

        vrp.logger.info.assert_called_with("O total de 1 empresas não foram roteirizadas...")

    @patch('service.vehicle_routing_problem.utils')
    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.feature_server')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_register_companies_with_violations_with_fail_post(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_feature_server, mock_BaseRoute, mock_utils):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {
            "leads_feature_url": "https://link-service-arcgis-server/feature/1",
            "non_route_companies_feature_url": "https://link-service-arcgis-server/feature/1"
        }        
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        vrp = VehicleRoutingProblem(log_fake)

        orders_with_violations_fake = [{
            'Name': '12345', 
            'ViolatedConstraint_1': 'Max 5 KM', 
            'ViolatedConstraint_2': None, 
            'ViolatedConstraint_3': None, 
            'ViolatedConstraint_4': None, 
            'ViolatedConstraint_5': None
        }]
        vrp.geodatabase.search_data = MagicMock(return_value=orders_with_violations_fake)
        
        companies_fake = [{
            'attributes': {
                'objectid': 1,
                'globalid': 'ABC123456',
                'id': 12345,
                'empresa': 'ABC'
            },
            'geometry': {}
        }]
        mock_feature_server.get_feature_data = MagicMock(return_value=companies_fake)
        vrp.geodatabase.get_violated_domain = MagicMock(return_value="Max 5 KM")                        
        mock_utils.datetime_to_timestamp = MagicMock(return_value=123456789)
        mock_feature_server.delete_feature_data = MagicMock(return_value=None)
        
        results_fake = [{
            'success': False
        }]
        mock_feature_server.post_feature_data = MagicMock(return_value=results_fake)

        polo_travelmode = { 'id': '1', 'polo': 'Region A', 'modoviagem': 'Walking', 'distanciatotalroteiro': 10 }
        vrp._register_companies_with_violations(polo_travelmode)

        feature_orders_all = os.path.join("in_memory", 'Orders_All')
        vrp.geodatabase.search_data.assert_called_with(feature_orders_all, ['Name', 'ViolatedConstraint_1', 'ViolatedConstraint_2', 'ViolatedConstraint_3', 'ViolatedConstraint_4'], "ArriveTime IS NULL")

        mock_feature_server.get_feature_data.assert_called_with(PARAMS_FAKE['leads_feature_url'], "id in (12345)")
        vrp.geodatabase.get_violated_domain.assert_called_with(orders_with_violations_fake[0]['ViolatedConstraint_1'])
        mock_feature_server.delete_feature_data.assert_called_with(PARAMS_FAKE['non_route_companies_feature_url'], "carteiraid = 1")
        payload_companies_with_violations_fake = [{
            'attributes': {
                'id': 12345,
                'empresa': 'ABC',
                'violacaoregra1': 'Max 5 KM',
                'datageracaorota': 123456789
            },
            'geometry': {
                'z': 0,
                'spatialReference': {'wkid':102100, 'latestWkid': 3857}
            }
        }]
        mock_feature_server.post_feature_data.assert_called_with(PARAMS_FAKE['non_route_companies_feature_url'], payload_companies_with_violations_fake)

        vrp.logger.error.assert_called_with("Falha ao inserir empresas que não foram roteirizadas para a carteira_id 1")
        vrp.logger.info.assert_called_with("O total de 1 empresas não foram roteirizadas...")

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.feature_server')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_register_companies_with_violations_nothing_items(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_feature_server, mock_BaseRoute):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {
            "leads_feature_url": "https://link-service-arcgis-server/feature/1",
            "non_route_companies_feature_url": "https://link-service-arcgis-server/feature/1"
        }        
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        log_fake = MagicMock(return_value=LogFake())
        vrp = VehicleRoutingProblem(log_fake)

        vrp.geodatabase.search_data = MagicMock(return_value=[])
        
        mock_feature_server.get_feature_data = MagicMock(return_value=None)
        vrp.geodatabase.get_violated_domain = MagicMock(return_value=None)
        mock_feature_server.delete_feature_data = MagicMock(return_value=None)    
        mock_feature_server.post_feature_data = MagicMock(return_value=None)

        polo_travelmode = { 'id': '1', 'polo': 'Region A', 'modoviagem': 'Walking', 'distanciatotalroteiro': 10 }
        vrp._register_companies_with_violations(polo_travelmode)

        feature_orders_all = os.path.join("in_memory", 'Orders_All')
        vrp.geodatabase.search_data.assert_called_with(feature_orders_all, ['Name', 'ViolatedConstraint_1', 'ViolatedConstraint_2', 'ViolatedConstraint_3', 'ViolatedConstraint_4'], "ArriveTime IS NULL")

        mock_feature_server.get_feature_data.assert_not_called()
        vrp.geodatabase.get_violated_domain.assert_not_called()
        mock_feature_server.delete_feature_data.assert_not_called()
        mock_feature_server.post_feature_data.assert_not_called()

        vrp.logger.error.assert_not_called()
        vrp.logger.info.assert_not_called()

    @freeze_time("2021-04-24")
    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.feature_server')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_get_payload_routes(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_feature_server, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        date20210424 = datetime.datetime(2021, 4, 24, 0, 0, 0)
        mock_Config.return_value.route_generation_date = date20210424
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {
            "executive_feature_url": "https://link-service-arcgis-server/feature/1"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)
        
        executives_fake = [{'attributes': {'id': 10, 'nome': 'João'}}]
        mock_feature_server.get_feature_data = MagicMock(return_value=executives_fake)
        
        log_fake = MagicMock(return_value=LogFake())

        vrp = VehicleRoutingProblem(log_fake)

        vrp._arcpy = MagicMock(return_value=ArcpyFake())

        vrp.geodatabase.get_path = MagicMock(return_value="path")
        
        companies_fake = [{'id': 20, 'empresa': 'Padaria', 'carteiraId': 30, 'executivoId': 10}]
        date20210424_0900 = datetime.datetime(2021, 4, 24, 9, 0, 0)
        orders_all_fake = [{'Name': 20, 'RouteName': '30#20210424', 'Description': 10, 'TimeWindowStart': date20210424_0900, 'ArriveTime': date20210424_0900, 'Sequence': 2, 'SHAPE@X': 123.45, 'SHAPE@Y': 543.21}]
        vrp.geodatabase.search_data = MagicMock(side_effect=[companies_fake, orders_all_fake])

        order_routes_fake = { '30#20210424': date20210424_0900}
        vrp._reordering_routes = MagicMock(return_value=order_routes_fake)

        work_areas_fake = [{'attributes': {'id': 30, 'polo': 'São José', 'carteira': 'Centro'}}]
        vrp._get_work_areas = MagicMock(return_value=work_areas_fake)

        scheduled_fake = {'id': 123}
        vrp.schedule.get_schedule_dict = MagicMock(return_value=scheduled_fake)        
        
        item_route_fake = {
                    "attributes": {
                    "empresaid": "Company Test"
                }}
        vrp.base_route.construct_payload = MagicMock(return_value=item_route_fake)

        result = vrp._get_payload_routes()

        result_expected = [item_route_fake]
        self.assertEqual(result, result_expected)

        ft_companies = os.path.join("path", "Empresas")
        vrp.geodatabase.search_data.assert_any_call(ft_companies, ['id', 'empresa', 'carteiraId', 'executivoId', 'endereco', 'numero', 'cidade', 'estado', 'bairro', 'cep', 'cnpjcpf', 'idpagseguro', 'tipoalerta'])

        mock_feature_server.get_feature_data.assert_called_with(PARAMS_FAKE['executive_feature_url'])

        feature_orders_all = os.path.join("in_memory", 'Orders_All')
        vrp.geodatabase.search_data.assert_any_call(feature_orders_all, ['Name', 'Description', 'Sequence','RouteName', 'TimeWindowStart' ,'ArriveTime', 'SHAPE@X', 'SHAPE@Y', 'ViolatedConstraint_2'])

        vrp._reordering_routes.assert_called_once()
        vrp._get_work_areas.assert_called_with()
        
        vrp.base_route.construct_payload.assert_called_with(
            companies_fake[0], executives_fake[0]['attributes'],
            1, date20210424_0900, date20210424, date20210424_0900, scheduled_fake['id'],
            work_areas_fake[0]['attributes'],
            orders_all_fake[0]['SHAPE@X'], orders_all_fake[0]['SHAPE@Y'])

    @freeze_time("2021-04-24")
    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.feature_server')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_get_payload_routes_no_items(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_feature_server, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {
            "executive_feature_url": "https://link-service-arcgis-server/feature/1"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)
        
        executives_fake = [{'attributes': {'id': 10, 'nome': 'João'}}]
        mock_feature_server.get_feature_data = MagicMock(return_value=executives_fake)
        
        log_fake = MagicMock(return_value=LogFake())

        vrp = VehicleRoutingProblem(log_fake)

        vrp._arcpy = MagicMock(return_value=ArcpyFake())

        vrp.geodatabase.get_path = MagicMock(return_value="path")
        
        companies_fake = [{'id': 20, 'empresa': 'Padaria', 'carteiraId': 30, 'executivoId': 10}]
        orders_all_fake = [{'Name': 20, 'Description': 10, 'TimeWindowStart': None, 'ArriveTime': None, 'Sequence': 2, 'SHAPE@X': 123.45, 'SHAPE@Y': 543.21, 'ViolatedConstraint_2': 'Erro na geração'}]
        vrp.geodatabase.search_data = MagicMock(side_effect=[companies_fake, orders_all_fake])

        order_routes_fake = {}
        vrp._reordering_routes = MagicMock(return_value=order_routes_fake)

        vrp._get_work_areas = MagicMock(return_value=None)

        result = vrp._get_payload_routes()

        result_expected = []
        self.assertEqual(result, result_expected)

        ft_companies = os.path.join("path", "Empresas")
        vrp.geodatabase.search_data.assert_any_call(ft_companies, ['id', 'empresa', 'carteiraId', 'executivoId', 'endereco', 'numero', 'cidade', 'estado', 'bairro', 'cep', 'cnpjcpf', 'idpagseguro', 'tipoalerta'])

        mock_feature_server.get_feature_data.assert_called_with(PARAMS_FAKE['executive_feature_url'])

        feature_orders_all = os.path.join("in_memory", 'Orders_All')
        vrp.geodatabase.search_data.assert_any_call(feature_orders_all, ['Name', 'Description', 'Sequence','RouteName', 'TimeWindowStart' ,'ArriveTime', 'SHAPE@X', 'SHAPE@Y', 'ViolatedConstraint_2'])

        vrp._reordering_routes.assert_called_once()
        vrp._get_work_areas.assert_not_called()
        vrp.base_route.construct_payload.assert_not_called()

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.utils')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_generate_routes(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_utils, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)
        
        log_fake = MagicMock(return_value=LogFake())

        vrp = VehicleRoutingProblem(log_fake)
        vrp._arcpy = MagicMock(return_value=ArcpyFake())

        feature_orders = 'feature/orders'
        feature_routes = 'feature/routes'
        vrp.geodatabase.get_path_feature = MagicMock(side_effect=[feature_orders, feature_routes, ['bla']])

        vrp._create_pre_routes = MagicMock(return_value=None)

        vrp._separate_orders_without_schedule = MagicMock(return_value=None)
        vrp._exist_visits_scheduled_out_of_hours = MagicMock(side_effect=[True, False])
        vrp._change_rule_preserve_route_to_schedules = MagicMock(return_value=None)
        vrp._arcpy.Append_management = MagicMock(return_value=None)

        vrp.geodatabase.delete_data = MagicMock(return_value=None)
        vrp._solve_route = MagicMock(side_effect=[None, None, None, None, Exception('Boom!')])
        vrp._append_orders_all = MagicMock(return_value=None)
        
        orders_with_schedule = [{'Name': 'XXX1234'}]
        routes_last_date = [{'EarliestStartTime': datetime.datetime(2021, 12, 31, 0, 0, 0, 0)}]
        vrp.geodatabase.search_data = MagicMock(side_effect=[orders_with_schedule, routes_last_date, orders_with_schedule])
        route_day_start_fake = datetime.datetime(2022, 1, 3, 0, 0, 0, 0)
        vrp.base_route.get_route_day = MagicMock(return_value=route_day_start_fake)

        polo_travelmode = { 'id': 1, 'polo': 'Region A', 'modoviagem': 'Walking' }
        years = ['2021', '2022']
        vrp._generate_routes(polo_travelmode, years)

        vrp._create_pre_routes.assert_any_call(polo_travelmode, years[0])
        vrp.geodatabase.delete_data.assert_any_call(feature_orders, "Sequence IS NOT NULL")
        feature_orders_all = os.path.join("in_memory", 'Orders_All')
        vrp.geodatabase.delete_data.assert_any_call(feature_orders_all, "Sequence IS NULL")
        vrp._solve_route.assert_any_call()

        vrp._separate_orders_without_schedule.assert_any_call()
        vrp._exist_visits_scheduled_out_of_hours.assert_any_call()
        vrp._change_rule_preserve_route_to_schedules.assert_any_call()
        feature_orders_temp_fake = os.path.join("in_memory", 'Orders_Temp')
        vrp._arcpy.Append_management.assert_any_call(feature_orders_temp_fake, "Orders", "NO_TEST", None, None)

        vrp._append_orders_all.assert_any_call()

        vrp.geodatabase.search_data.assert_any_call("Orders", ["Name"], where="TimeWindowStart IS NOT NULL")
        vrp.geodatabase.search_data.assert_any_call(feature_routes, ["EarliestStartTime"], order_by="ORDER BY EarliestStartTime DESC")
        vrp.base_route.get_route_day.assert_called_once_with(routes_last_date[0]["EarliestStartTime"])
        mock_Depots.return_value.create.assert_called_once_with(polo_travelmode, route_day_start=route_day_start_fake)

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.utils')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_generate_routes_once_year(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_utils, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        
        log_fake = MagicMock(return_value=LogFake())

        vrp = VehicleRoutingProblem(log_fake)
        vrp._arcpy = MagicMock(return_value=ArcpyFake())

        feature_orders = 'feature/orders'
        feature_routes = 'feature/routes'
        vrp.geodatabase.get_path_feature = MagicMock(side_effect=[feature_orders, feature_routes])
        
        vrp.geodatabase.search_data = MagicMock(return_value=[])

        vrp._separate_orders_without_schedule = MagicMock(return_value=None)
        vrp._exist_visits_scheduled_out_of_hours = MagicMock(return_value=None)
        vrp._change_rule_preserve_route_to_schedules = MagicMock(return_value=None)
        vrp._arcpy.Append_management = MagicMock(return_value=None)

        vrp._create_pre_routes = MagicMock(return_value=None)
        vrp.geodatabase.delete_data = MagicMock(return_value=None)
        vrp._solve_route = MagicMock(return_value=None)
        vrp._append_orders_all = MagicMock(return_value=None)
        
        vrp.base_route.get_route_day = MagicMock(return_value=None)
        mock_Depots.create = MagicMock(return_value=None)

        polo_travelmode = [{ 'id': 1, 'polo': 'Region A', 'modoviagem': 'Walking' }]
        years = ['2021']
        vrp._generate_routes(polo_travelmode, years)

        vrp._create_pre_routes.assert_called_once_with(polo_travelmode, years[0])
        vrp.geodatabase.delete_data.assert_not_called()
        vrp._solve_route.assert_called_once_with()
        vrp._append_orders_all.assert_called_once_with()

        vrp.geodatabase.search_data.assert_called_once_with("Orders", ["Name"], where="TimeWindowStart IS NOT NULL")
        vrp._separate_orders_without_schedule.assert_not_called()
        vrp._exist_visits_scheduled_out_of_hours.assert_not_called()
        vrp._change_rule_preserve_route_to_schedules.assert_not_called()
        vrp._arcpy.Append_management.assert_not_called()

        vrp.base_route.get_route_day.assert_not_called()
        mock_Depots.create.assert_not_called()      

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.utils')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_run(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_utils, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)
        
        log_fake = MagicMock(return_value=LogFake())

        vrp = VehicleRoutingProblem(log_fake)

        vrp._arcpy = MagicMock(return_value=ArcpyFake())

        polo_travelmode = [{ 'id': 1, 'polo': 'Region A', 'modoviagem': 'Walking' }]
        vrp.base_route.get_carteira_and_travelmode_of_work_areas = MagicMock(return_value=polo_travelmode)
        vrp._make_layer_route = MagicMock(return_value=None)
        
        travel_modes_fake = {'Driving Time': 'Driving', 'Walking Time': 'Walking'}
        vrp.travel_modes = travel_modes_fake
        
        vrp._create_feature_in_memory = MagicMock(return_value=None)

        solver_properties_fake = MagicMock()
        solver_properties_fake.applyTravelMode = MagicMock(return_value=None)
        vrp.solver_properties = MagicMock(return_value=solver_properties_fake)

        work_areas_fake = [{'attributes': {'id': '1', 'polo': 'Region A'}}]
        vrp._get_work_areas = MagicMock(return_value=work_areas_fake)
        vrp.base_route.filter_company_by_id = MagicMock(return_value=None)

        feature_filtered_fake = 'feature_name_filtered'
        vrp.base_route.get_name_feature_filtered = MagicMock(return_value=feature_filtered_fake)

        companies_fake = [{"executivoId": 1}]
        vrp.geodatabase.search_data = MagicMock(return_value=companies_fake)

        vrp._load_companies_to_orders = MagicMock(return_value=None)
        years_fake = ['2021']
        mock_Depots.return_value.create = MagicMock(return_value=years_fake)
        ##vrp._create_route_zones = MagicMock(return_value=None)
        vrp._generate_routes = MagicMock(return_value=None)
        vrp._register_companies_with_violations = MagicMock(return_value=None)
        vrp._clear_objects_vrp = MagicMock(return_value=None)
        payload_fake = [{
                    "attributes": {
                    "empresa": "Company Test"
                }}]
        vrp._get_payload_routes = MagicMock(return_value=payload_fake)
        executives_ids_fake = ['10']
        vrp.base_route.get_executives_ids = MagicMock(return_value=executives_ids_fake)
        vrp.base_route.publish_new_routes = MagicMock(return_value=None)

        vrp.run()

        vrp.base_route.get_carteira_and_travelmode_of_work_areas.assert_called_with()
        vrp._make_layer_route.assert_called_with()
        vrp._create_feature_in_memory.assert_called_with('Orders_All', 'Orders')
        vrp.solver_properties.applyTravelMode.assert_called_with(travel_modes_fake['Walking Time'])
        vrp.base_route.filter_company_by_id.assert_called_with(polo_travelmode[0])
        vrp.base_route.get_name_feature_filtered.assert_called_with("Empresas")
        vrp.geodatabase.search_data.assert_called_with(feature_filtered_fake, ['executivoId'])
        vrp._load_companies_to_orders.assert_called_with()
        mock_Depots.return_value.create.assert_called_with(polo_travelmode[0])
        ##vrp._create_route_zones.assert_called_with()
        vrp._generate_routes.assert_called_once_with(polo_travelmode[0], years_fake)
        vrp._register_companies_with_violations.assert_called_with(polo_travelmode[0])
        vrp._get_payload_routes.assert_called_with()
        vrp.base_route.get_executives_ids.assert_called_with(companies_fake)
        vrp.base_route.publish_new_routes.assert_called_with(executives_ids_fake, payload_fake)        
        vrp._clear_objects_vrp.assert_called_with()
        vrp.logger.info.assert_called_with('Gerando roteiros para o idcarteira(modoviagem) (1(Walking)) (1/1)')

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.utils')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_run_without_companies(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_utils, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)
        
        log_fake = MagicMock(return_value=LogFake())

        vrp = VehicleRoutingProblem(log_fake)

        vrp._arcpy = MagicMock(return_value=ArcpyFake())

        polo_travelmode = [{ 'id': 1, 'polo': 'Region A', 'modoviagem': 'Walking' }]
        vrp.base_route.get_carteira_and_travelmode_of_work_areas = MagicMock(return_value=polo_travelmode)
        vrp._make_layer_route = MagicMock(return_value=None)
        
        travel_modes_fake = {'Driving Time': 'Driving', 'Walking Time': 'Walking'}
        vrp.travel_modes = travel_modes_fake
        
        vrp._create_feature_in_memory = MagicMock(return_value=None)

        solver_properties_fake = MagicMock()
        solver_properties_fake.applyTravelMode = MagicMock(return_value=None)
        vrp.solver_properties = MagicMock(return_value=solver_properties_fake)
        
        vrp.base_route.filter_company = MagicMock(return_value=None)

        feature_filtered_fake = 'feature_name_filtered'
        vrp.base_route.get_name_feature_filtered = MagicMock(return_value=feature_filtered_fake)

        companies_fake = []
        vrp.geodatabase.search_data = MagicMock(return_value=companies_fake)

        vrp._load_companies_to_orders = MagicMock(return_value=None)
        mock_Depots.create = MagicMock(return_value=None)
        vrp._create_route_zones = MagicMock(return_value=None)
        vrp._create_pre_routes = MagicMock(return_value=None)
        vrp._solve_route = MagicMock(return_value=None)
        vrp._append_orders_all = MagicMock(return_value=None)
        vrp._clear_objects_vrp = MagicMock(return_value=None)
        vrp._get_payload_routes = MagicMock(return_value=None)
        vrp.base_route.get_executives_ids = MagicMock(return_value=None)
        vrp.base_route.publish_new_routes = MagicMock(return_value=None)        

        vrp.run()

        vrp.base_route.get_carteira_and_travelmode_of_work_areas.assert_called_with()
        vrp._make_layer_route.assert_called_with()
        vrp._create_feature_in_memory.assert_called_with('Orders_All', 'Orders')
        vrp.base_route.get_name_feature_filtered.assert_called_with("Empresas")
        vrp.geodatabase.search_data.assert_called_with(feature_filtered_fake, ['executivoId'])
        
        solver_properties_fake.applyTravelMode.assert_not_called()
        vrp._load_companies_to_orders.assert_not_called()
        mock_Depots.create.assert_not_called()
        vrp._create_route_zones.assert_not_called()
        vrp._create_pre_routes.assert_not_called()
        vrp._solve_route.assert_not_called()
        vrp._append_orders_all.assert_not_called()
        vrp._get_payload_routes.assert_not_called()
        vrp.base_route.get_executives_ids.assert_not_called()
        vrp.base_route.publish_new_routes.assert_not_called()                
        vrp._clear_objects_vrp.assert_not_called()

        vrp.logger.info.assert_called_with('Nenhuma empresa encontrada para o idcarteira(modoviagem) (1(Walking))')

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_create_route_zones(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())

        vrp = VehicleRoutingProblem(log_fake)

        feature_depots_path = '/path/depots'
        feature_route_zones_path = '/path/route_zones'
        vrp.geodatabase.get_path_feature = MagicMock(side_effect=[feature_depots_path, feature_route_zones_path])
        
        start_points = [{'Name': '1#20210629'}]
        vrp.geodatabase.search_data = MagicMock(return_value=start_points)
        
        work_areas = [{'attributes': {'id': '1', 'polo': 'Region A', 'modoviagem': 'Walking'}, 'geometry': None}]
        vrp._get_work_areas = MagicMock(return_value=work_areas)

        vrp.geodatabase.insert_data = MagicMock(return_value=None)

        vrp._create_route_zones()

        vrp.geodatabase.get_path_feature.assert_any_call('Depots')
        vrp.geodatabase.search_data.assert_called_with(feature_depots_path, ['Name'])
        vrp._get_work_areas.assert_called_with()
        vrp.geodatabase.get_path_feature.assert_any_call('RouteZones')
        
        route_zones = []
        route_zones.append({
                'attributes': {
                    'RouteName': '1#20210629'
                },
                'geometry': None
            })
        vrp.geodatabase.insert_data.assert_called_with(route_zones, feature_route_zones_path, ['RouteName', 'SHAPE@JSON'])

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_get_date_from_route_name(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())

        vrp = VehicleRoutingProblem(log_fake)

        result = vrp._get_date_from_route_name('1#20210629')
        expected = datetime.datetime(2021, 6, 29)
        self.assertEqual(result, expected)

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_create_pre_routes(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())

        vrp = VehicleRoutingProblem(log_fake)

        feature_depots_path = '/path/depots'
        feature_companies_path = '/path/companies'
        vrp.geodatabase.get_path_feature = MagicMock(side_effect=[feature_depots_path, feature_companies_path, feature_companies_path])
        
        vrp.base_route.get_name_feature_filtered = MagicMock(return_value=feature_companies_path)

        start_points = [{'Name': '1#20210629'}, {'Name': '1#20220629'}]        
        vrp.geodatabase.search_data = MagicMock(side_effect=[start_points, [], []])

        vrp.geodatabase.delete_data = MagicMock(return_value=None)

        vrp._get_date_from_route_name = MagicMock(return_value=datetime.datetime(2021, 6, 29))
        vrp.geodatabase.insert_data = MagicMock(return_value=None)

        polo_travelmode = { 'id': '1', 'polo': 'Region A', 'modoviagem': 'Walking', 'distanciatotalroteiro': 10 }
        year = '2021'
        vrp._create_pre_routes(polo_travelmode, year)

        vrp.geodatabase.get_path_feature.assert_any_call('Depots')
        vrp.geodatabase.search_data.assert_any_call(feature_depots_path, ['Name'])
        vrp.geodatabase.search_data.assert_any_call(feature_companies_path, ['Id'], where="DeliveryQuantity_2 IS NOT NULL")
        vrp.geodatabase.search_data.assert_any_call(feature_companies_path, ['Id'], where="TimeWindowStart IS NOT NULL")
        vrp.geodatabase.delete_data.assert_called_with(feature_companies_path, "1=1")
        vrp._get_date_from_route_name.assert_any_call(start_points[0]['Name'])
        vrp._get_date_from_route_name.assert_any_call(start_points[1]['Name'])
        vrp.base_route.get_name_feature_filtered.assert_any_call('Empresas')
        vrp.geodatabase.get_path_feature.assert_any_call('Routes')

        pre_routes = []
        pre_routes.append({
                'attributes': {
                    'Name': '1#20210629',
                    'StartDepotName': '1#20210629',
                    'EarliestStartTime': datetime.datetime(2021, 6, 29, 9, 0, 0),
                    'LatestStartTime': datetime.datetime(2021, 6, 29, 18, 0, 0),
                    'CostPerUnitTime': 1,
                    'MaxOrderCount': 30,
                    'AssignmentRule': 2,
                    'Capacity_1': 30,
                    'MaxTotalDistance': 10000
                }
            })
        vrp.geodatabase.insert_data.assert_called_with(pre_routes, feature_companies_path, ['Name', 'StartDepotName', 'EarliestStartTime', 'LatestStartTime', 'CostPerUnitTime', 'MaxOrderCount', 'AssignmentRule', 'Capacity_1', 'MaxTotalDistance'])

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_create_pre_routes_with_distance_default_and_schedule(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())

        vrp = VehicleRoutingProblem(log_fake)

        feature_depots_path = '/path/depots'
        feature_companies_path = '/path/companies'
        vrp.geodatabase.get_path_feature = MagicMock(side_effect=[feature_depots_path, feature_companies_path, feature_companies_path])

        vrp.base_route.get_name_feature_filtered = MagicMock(return_value=feature_companies_path)
        
        start_points = [{'Name': '1#20210629'}]
        companies_with_alerts_fake = [{'id': 1}]
        companies_with_schedule_fake = [{'id': 1}]
        vrp.geodatabase.search_data = MagicMock(side_effect=[start_points, companies_with_alerts_fake, companies_with_schedule_fake])

        vrp.geodatabase.delete_data = MagicMock(return_value=None)
        
        vrp._get_date_from_route_name = MagicMock(return_value=datetime.datetime(2021, 6, 29))
        vrp.geodatabase.insert_data = MagicMock(return_value=None)

        polo_travelmode = { 'id': '1', 'polo': 'Region A', 'modoviagem': 'Walking', 'distanciatotalroteiro': None }

        year = "2021"
        vrp._create_pre_routes(polo_travelmode, year)

        vrp.geodatabase.get_path_feature.assert_any_call('Depots')
        vrp.geodatabase.search_data.assert_any_call(feature_depots_path, ['Name'])
        vrp.geodatabase.search_data.assert_any_call(feature_companies_path, ['Id'], where="DeliveryQuantity_2 IS NOT NULL")
        vrp.geodatabase.search_data.assert_any_call(feature_companies_path, ['Id'], where="TimeWindowStart IS NOT NULL")        
        vrp.geodatabase.delete_data.assert_called_with(feature_companies_path, "1=1")
        vrp._get_date_from_route_name.assert_called_with(start_points[0]['Name'])
        vrp.base_route.get_name_feature_filtered.assert_any_call('Empresas')
        vrp.geodatabase.get_path_feature.assert_any_call('Routes')

        pre_routes = []
        pre_routes.append({
                'attributes': {
                    'Name': '1#20210629',
                    'StartDepotName': '1#20210629',
                    'EarliestStartTime': datetime.datetime(2021, 6, 29, 9, 0, 0),
                    'LatestStartTime': datetime.datetime(2021, 6, 29, 18, 0, 0),
                    'CostPerUnitTime': 1,
                    'MaxOrderCount': 30,
                    'AssignmentRule': 2,
                    'Capacity_1': 29,
                    'Capacity_2': 1
                }
            })
        fields_expected = ['Name', 'StartDepotName', 'EarliestStartTime', 'LatestStartTime', 'CostPerUnitTime', 'MaxOrderCount', 'AssignmentRule', 'Capacity_1', 'Capacity_2']
        vrp.geodatabase.insert_data.assert_called_with(pre_routes, feature_companies_path, fields_expected)

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_reordering_routes(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())

        vrp = VehicleRoutingProblem(log_fake)

        feature_orders_all = os.path.join("in_memory", 'Orders_All')
        feature_routes_path = '/path/routes'
        vrp.geodatabase.get_path_feature = MagicMock(side_effect=[feature_routes_path])

        orders_with_schedule = [{'RouteName': '1#20210601'}]
        routes_orderby_date_desc = [{'Name': '1#20210603', 'StartTime': datetime.datetime(2021, 6, 3, 0, 0, 0)}, {'Name': '1#20210602', 'StartTime': datetime.datetime(2021, 6, 2, 0, 0, 0)}]
        routes_orderby_count_asc = [{'Name': '1#20210602', 'StartTime': datetime.datetime(2021, 6, 3, 0, 0, 0)}, {'Name': '1#20210603', 'StartTime': datetime.datetime(2021, 6, 2, 0, 0, 0)}]
        vrp.geodatabase.search_data = MagicMock(side_effect=[orders_with_schedule, routes_orderby_date_desc, routes_orderby_count_asc])

        result = vrp._reordering_routes()

        expected = {
            '1#20210602': datetime.datetime(2021, 6, 3, 0, 0),
            '1#20210603': datetime.datetime(2021, 6, 2, 0, 0)
            }
        self.assertEqual(result, expected)

        vrp.geodatabase.search_data.assert_any_call(feature_orders_all, ['RouteName'], "RouteName IS NOT NULL AND TimeWindowStart IS NOT NULL", distinct="RouteName")

        fields = ['Name', 'StartTime']
        where_routes = "StartTime IS NOT NULL AND Name <> '1#20210601'"
        vrp.geodatabase.get_path_feature.assert_any_call("Routes")
        vrp.geodatabase.search_data.assert_any_call(feature_routes_path, fields, where_routes, order_by="ORDER BY StartTime DESC")        
        vrp.geodatabase.search_data.assert_any_call(feature_routes_path, fields, where_routes, order_by="ORDER BY OrderCount ASC")        

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_reordering_routes_without_schedule(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())

        vrp = VehicleRoutingProblem(log_fake)

        feature_orders_all = os.path.join("in_memory", 'Orders_All')
        feature_routes_path = '/path/routes'
        vrp.geodatabase.get_path_feature = MagicMock(side_effect=[feature_routes_path])

        orders_with_schedule = []
        routes_orderby_date_desc = [{'Name': '1#20210603', 'StartTime': datetime.datetime(2021, 6, 3, 0, 0, 0)}, {'Name': '1#20210602', 'StartTime': datetime.datetime(2021, 6, 2, 0, 0, 0)}]
        routes_orderby_count_asc = [{'Name': '1#20210602', 'StartTime': datetime.datetime(2021, 6, 3, 0, 0, 0)}, {'Name': '1#20210603', 'StartTime': datetime.datetime(2021, 6, 2, 0, 0, 0)}]
        vrp.geodatabase.search_data = MagicMock(side_effect=[orders_with_schedule, routes_orderby_date_desc, routes_orderby_count_asc])

        result = vrp._reordering_routes()

        expected = {
            '1#20210602': datetime.datetime(2021, 6, 3, 0, 0),
            '1#20210603': datetime.datetime(2021, 6, 2, 0, 0)
            }
        self.assertEqual(result, expected)

        vrp.geodatabase.search_data.assert_any_call(feature_orders_all, ['RouteName'], "RouteName IS NOT NULL AND TimeWindowStart IS NOT NULL", distinct="RouteName")

        fields = ['Name', 'StartTime']
        where_routes = "StartTime IS NOT NULL"
        vrp.geodatabase.get_path_feature.assert_any_call("Routes")
        vrp.geodatabase.search_data.assert_any_call(feature_routes_path, fields, where_routes, order_by="ORDER BY StartTime DESC")        
        vrp.geodatabase.search_data.assert_any_call(feature_routes_path, fields, where_routes, order_by="ORDER BY OrderCount ASC")        

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_load_companies_to_orders(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())

        vrp = VehicleRoutingProblem(log_fake)

        ft_companies_fake = 'feature_companies'
        vrp.base_route.get_name_feature_filtered = MagicMock(return_value=ft_companies_fake)

        vrp._arcpy = MagicMock(return_value=ArcpyFake())
        vrp._arcpy.na.AddLocations = MagicMock(return_value=None)

        vrp._load_companies_to_orders()

        vrp.base_route.get_name_feature_filtered.assert_called_once_with("Empresas")
        vrp._arcpy.na.AddLocations.assert_called_once_with(
            LAYER_NAME_ROUTE, 
            "Orders", 
            ft_companies_fake, 
            "Name id #;Description carteiraId #;ServiceTime Attr_Time #;TimeWindowStart TimeWindowStart #;TimeWindowEnd TimeWindowEnd #;MaxViolationTime MaxViolationTime #;TimeWindowStart2 # #;TimeWindowEnd2 # #;MaxViolationTime2 # #;InboundArriveTime # #;OutboundDepartTime # #;DeliveryQuantity_1 DeliveryQuantity_1 #;DeliveryQuantity_2 DeliveryQuantity_2 #;DeliveryQuantity_3 # #;DeliveryQuantity_4 # #;DeliveryQuantity_5 # #;DeliveryQuantity_6 # #;DeliveryQuantity_7 # #;DeliveryQuantity_8 # #;DeliveryQuantity_9 # #;PickupQuantity_1 # #;PickupQuantity_2 # #;PickupQuantity_3 # #;PickupQuantity_4 # #;PickupQuantity_5 # #;PickupQuantity_6 # #;PickupQuantity_7 # #;PickupQuantity_8 # #;PickupQuantity_9 # #;Revenue # #;AssignmentRule # 3;RouteName # #;Sequence # #;CurbApproach # 0", 
            "5000 Meters", None, "Routing_Streets SHAPE;Routing_Streets_Override NONE;Routing_ND_Junctions NONE", "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "EXCLUDE", None
            )

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_solve_route(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Config.return_value.get_folder_temp = MagicMock(return_value="temp")

        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())
        vrp = VehicleRoutingProblem(log_fake)

        vrp._arcpy = MagicMock(return_value=ArcpyFake())
        vrp._arcpy.management.SaveToLayerFile = MagicMock(return_value=None)
        vrp._arcpy.na.Solve = MagicMock(return_value=None)

        vrp._solve_route()

        output_layer_file = os.path.join("temp", LAYER_NAME_ROUTE + ".lyrx")
        vrp._arcpy.management.SaveToLayerFile.assert_called_once_with(LAYER_NAME_ROUTE, output_layer_file, "RELATIVE")
        vrp._arcpy.na.Solve.assert_called_once_with(LAYER_NAME_ROUTE, "HALT", "TERMINATE", None, '')

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_separate_orders_without_schedule(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Config.return_value.get_folder_temp = MagicMock(return_value="temp")

        log_fake = MagicMock(return_value=LogFake())
        vrp = VehicleRoutingProblem(log_fake)
        vrp._arcpy = MagicMock(return_value=ArcpyFake())

        companies_fake = [
            {'Name': '22692', 'ArriveTime': None, 'TimeWindowStart': datetime.datetime(2022, 3, 11, 11, 0), 'RouteName': None, 'AssignmentRule': 3, 'SHAPE@JSON': {'x':-46.704459999999983,'y':-23.679719999999975,'spatialReference':{'wkid':4326,'latestWkid':4326}}},
            {'Name': '22693', 'ArriveTime': None, 'TimeWindowStart': datetime.datetime(2022, 3, 12, 11, 0), 'RouteName': None, 'AssignmentRule': 3, 'SHAPE@JSON': {'x':-46.704459999999983,'y':-23.679719999999975,'spatialReference':{'wkid':4326,'latestWkid':4326}}}
        ]

        vrp.geodatabase.search_data = MagicMock(return_value=companies_fake)
        vrp._create_feature_in_memory = MagicMock(return_value=None)
        vrp._arcpy.Append_management = MagicMock(return_value=None)
        vrp.geodatabase.delete_data = MagicMock(return_value=None)

        vrp._separate_orders_without_schedule()

        vrp._create_feature_in_memory.assert_called_with('Orders_Temp', 'Orders')
        feature_orders_temp_fake = os.path.join("in_memory", 'Orders_Temp')
        vrp._arcpy.Append_management.assert_called_once_with("Orders", feature_orders_temp_fake, "NO_TEST", None, None, "TimeWindowStart IS NULL AND TimeWindowEnd IS NULL")
        vrp.geodatabase.delete_data.assert_called_once_with('Orders', 'TimeWindowStart IS NULL AND TimeWindowEnd IS NULL')

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_exist_visits_scheduled_out_of_hours(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Config.return_value.get_folder_temp = MagicMock(return_value="temp")

        log_fake = MagicMock(return_value=LogFake())
        vrp = VehicleRoutingProblem(log_fake)

        companies_fake = [
            {'Name': '22692', 'ArriveTime': datetime.datetime(2022, 3, 11, 10, 45, 20, 967082), 'TimeWindowStart': datetime.datetime(2022, 3, 11, 11, 0), 'RouteName': '1159101#20220311', 'AssignmentRule': 3, 'SHAPE@JSON': '{"x":-46.704459999999983,"y":-23.679719999999975,"spatialReference":{"wkid":4326,"latestWkid":4326}}'},
            {'Name': '22693', 'ArriveTime': datetime.datetime(2022, 3, 11, 11, 45, 20, 967082), 'TimeWindowStart': datetime.datetime(2022, 3, 11, 11, 0), 'RouteName': '1159101#20220311', 'AssignmentRule': 3, 'SHAPE@JSON': '{"x":-46.704459999999983,"y":-23.679719999999975,"spatialReference":{"wkid":4326,"latestWkid":4326}}'}
        ]

        vrp.geodatabase.search_data = MagicMock(return_value=companies_fake)
        vrp.depots.change_position = MagicMock(return_value=None)

        vrp._exist_visits_scheduled_out_of_hours()

        fields = ["Name", "ArriveTime", "TimeWindowStart", "RouteName", "AssignmentRule", "SHAPE@JSON"]

        companies_result = [
            {
                'Name': '22692', 
                'ArriveTime': datetime.datetime(2022, 3, 11, 10, 45, 20, 967082), 
                'TimeWindowStart': datetime.datetime(2022, 3, 11, 11, 0), 
                'RouteName': '1159101#20220311', 'AssignmentRule': 2, 
                'SHAPE@JSON': '{"x":-46.704459999999983,"y":-23.679719999999975,"spatialReference":{"wkid":4326,"latestWkid":4326}}'}
        ]
        shape_x_fake = -46.704459999999983
        shape_y_fake = -23.679719999999975
        vrp.depots.change_position.assert_called_once_with(companies_fake[1]['RouteName'], shape_x_fake, shape_y_fake)

    @patch('service.vehicle_routing_problem.BaseRoute')
    @patch('service.vehicle_routing_problem.Config')
    @patch('service.vehicle_routing_problem.Geodatabase')
    @patch('service.vehicle_routing_problem.Schedule')
    @patch('service.vehicle_routing_problem.VRPDepots')
    def test_change_rule_preserve_route_to_schedules(self, mock_Depots, mock_Schedule, mock_Geodatabase, mock_Config, mock_BaseRoute):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Config.return_value.get_folder_temp = MagicMock(return_value="temp")

        log_fake = MagicMock(return_value=LogFake())
        vrp = VehicleRoutingProblem(log_fake)

        companies_fake = [
            {'Name': '22692', 'AssignmentRule': 1}
        ]

        vrp.geodatabase.search_data = MagicMock(return_value=companies_fake)

        vrp._change_rule_preserve_route_to_schedules()

        fields = ["Name", "AssignmentRule"]

        companies_result = [
            {'Name': '22692', 'AssignmentRule': 2}
        ]

        vrp.geodatabase.update_data.assert_called_once_with("Orders", fields, "TimeWindowStart IS NOT NULL", companies_result, "Name")


class ArcpyFake:
    pass

class LogFake:
    pass

class DescribeFake():
    def __init__(self):
        self.spatialReference = "SIRGAS2000"