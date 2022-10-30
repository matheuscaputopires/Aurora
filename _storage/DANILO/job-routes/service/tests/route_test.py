from unittest import TestCase
from mock import patch, MagicMock
import os
import datetime
from freezegun import freeze_time

from service.route import Route

class TestRoute(TestCase):

    @patch('service.route.BaseRoute')
    @patch('service.route.Config')
    @patch('service.route.Geodatabase')
    def test_get_work_areas(self, mock_Geodatabase, mock_Config, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())
        
        route = Route(log_fake)

        work_areas_fake = [1, 2]
        route.base_route.get_work_areas = MagicMock(return_value=work_areas_fake)        

        result = route._get_work_areas()

        self.assertEqual(result, work_areas_fake)
        route.base_route.get_work_areas.assert_called_with()

    @patch('service.route.BaseRoute')
    @patch('service.route.Config')
    @patch('service.route.Geodatabase')
    def test_get_work_areas_with_values(self, mock_Geodatabase, mock_Config, mock_BaseRoute):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)    
        mock_BaseRoute = MagicMock(return_value=None)            

        log_fake = MagicMock(return_value=LogFake())
        
        route = Route(log_fake)

        route.base_route.get_work_areas = MagicMock(return_value=None)        
        
        work_areas_fake = [1, 2]
        route.work_areas = work_areas_fake

        result = route._get_work_areas()

        self.assertEqual(result, work_areas_fake)
        route.base_route.get_work_areas.assert_not_called()

    @patch('service.route.BaseRoute')
    @patch('service.route.Config')
    @patch('service.route.Geodatabase')
    def test_make_layer_route(self, mock_Geodatabase, mock_Config, mock_BaseRoute):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {                
            "path_network_layer": "path/folder_example",
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        logger_fake = MagicMock(return_value=LogFake())
        route = Route(logger_fake) 

        arcpyFake = ArcpyFake()
        route._arcpy = MagicMock(return_value=arcpyFake)

        route.base_route.start_route_day = MagicMock(return_value=None)

        route_layer_fake = RouteLayerFake()
        route_output_fake = RouteOutputFake()

        route_layer_fake.getOutput = MagicMock(return_value=route_output_fake)
        route._arcpy.na.MakeRouteAnalysisLayer = MagicMock(return_value=route_layer_fake)        

        describe_fake = MagicMock()
        describe_fake.network.catalogPath = MagicMock(return_value=None)
        route._arcpy.Describe = MagicMock(return_value=describe_fake)
        route._arcpy.na.GetTravelModes = MagicMock(return_value=None)
        route._arcpy.na.GetSolverProperties = MagicMock(return_value=None)

        route._make_layer_route()

        route.base_route.start_route_day.assert_called_with()
        route._arcpy.na.MakeRouteAnalysisLayer.assert_called_with(PARAMS_FAKE['path_network_layer'], "WorkRoute", "Walking Distance", "FIND_BEST_ORDER", time_of_day=None)
        route_layer_fake.getOutput.assert_called_with(0)
        route._arcpy.Describe.assert_called_with(route_output_fake)
        route._arcpy.na.GetTravelModes.assert_called_with(describe_fake.network.catalogPath)
        route._arcpy.na.GetSolverProperties.assert_called_with(route_output_fake)
    
    @patch('service.route.BaseRoute')
    @patch('service.route.Config')
    @patch('service.route.Geodatabase')
    def test_get_companies(self, mock_Geodatabase, mock_Config, mock_BaseRoute):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        logger_fake = MagicMock(return_value=LogFake())
        route = Route(logger_fake) 

        path_fake = 'path_gdb'
        route.geodatabase.get_path = MagicMock(return_value=path_fake)

        companies_fake = [{'id': 20, 'empresa': 'Padaria', 'carteiraId': 1, 'executivoId': 10}]
        route.geodatabase.search_data = MagicMock(return_value=companies_fake)

        polo_travelmode = { 'id': 1 }
        result = route._get_companies(polo_travelmode)

        self.assertEqual(result, companies_fake)

        route.geodatabase.get_path.assert_called_with()

        ft_companies = os.path.join(path_fake, "Empresas")
        route.geodatabase.search_data.assert_called_with(ft_companies, ['id', 'empresa', 'carteiraId', 'executivoId', 'endereco', 'numero', 'cidade', 'estado', 'bairro', 'cep', 'cnpjcpf', 'idpagseguro'], "carteiraId IN (1)")

    @patch('service.route.feature_server')
    @patch('service.route.utils')
    @patch('service.route.BaseRoute')
    @patch('service.route.Config')
    @patch('service.route.Geodatabase')
    def test_get_executives(self, mock_Geodatabase, mock_Config, mock_BaseRoute, mock_utils, mock_feature_server):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {                
            "executive_feature_url": "https://link-service-arcgis-server/feature/1"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        executives_fake = [{'attributes': {'id': 10, 'nome': 'João'}}]
        mock_feature_server.get_feature_data = MagicMock(return_value=executives_fake)

        logger_fake = MagicMock(return_value=LogFake())
        route = Route(logger_fake)

        executives_ids_fake = ['10']
        route.base_route.get_executives_ids = MagicMock(return_value=executives_ids_fake)

        companies = [{'id': 20, 'empresa': 'Padaria', 'carteiraId': 1, 'executivoId': 10}]
        result = route._get_executives(companies)

        self.assertEqual(result, executives_fake)

        route.base_route.get_executives_ids.assert_called_with(companies)
        mock_feature_server.get_feature_data.assert_called_with(PARAMS_FAKE['executive_feature_url'], 'id IN (10)')

    @patch('service.route.BaseRoute')
    @patch('service.route.Config')
    @patch('service.route.Geodatabase')
    def test_load_companies_to_stops(self, mock_Geodatabase, mock_Config, mock_BaseRoute):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        logger_fake = MagicMock(return_value=LogFake())
        route = Route(logger_fake) 

        arcpyFake = ArcpyFake()
        route._arcpy = MagicMock(return_value=arcpyFake)

        ft_companies_filtered_fake = "feature_name"
        route.base_route.get_name_feature_filtered = MagicMock(return_value=ft_companies_filtered_fake)

        route._arcpy.na.AddLocations = MagicMock(return_value=None)

        route_layer_fake = "layer"
        route.route_layer = route_layer_fake

        route._load_companies_to_stops()
        
        route.base_route.get_name_feature_filtered.assert_called_with("Empresas")
        route._arcpy.na.AddLocations(route_layer_fake, "Stops", ft_companies_filtered_fake, "Name id #;RouteName executivoId #;Attr_WalkTime Attr_Time #;TimeWindowStart TimeWindowStart #", "", exclude_restricted_elements="EXCLUDE")

    @patch('service.route.BaseRoute')
    @patch('service.route.Config')
    @patch('service.route.Geodatabase')
    def test_solve_route(self, mock_Geodatabase, mock_Config, mock_BaseRoute):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        logger_fake = MagicMock(return_value=LogFake())
        route = Route(logger_fake) 

        arcpyFake = ArcpyFake()
        route._arcpy = MagicMock(return_value=arcpyFake)

        travel_modes_fake = {'Driving Distance': 'Driving', 'Walking Distance': 'Walking'}
        route.travel_modes = travel_modes_fake

        solver_properties_fake = MagicMock()
        solver_properties_fake.applyTravelMode = MagicMock(return_value=None)
        route.solver_properties = MagicMock(return_value=solver_properties_fake)
        
        route._arcpy.na.Solve = MagicMock(return_value=None)

        route_layer_fake = "layer"
        route.route_layer = route_layer_fake

        polo_travelmode = { 'polo': 'Region A', 'modoviagem': 'Walking' }
        route._solve_route(polo_travelmode)

        route.solver_properties.applyTravelMode.assert_called_with(travel_modes_fake['Walking Distance'])
        route._arcpy.na.Solve.assert_called_with(route_layer_fake, "SKIP", "TERMINATE", None, '')

    @patch('service.route.BaseRoute')
    @patch('service.route.Config')
    @patch('service.route.Geodatabase')
    def test_get_stops(self, mock_Geodatabase, mock_Config, mock_BaseRoute):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        logger_fake = MagicMock(return_value=LogFake())
        route = Route(logger_fake)

        feature_path_stops_fake = 'StopsXPTO'
        route.geodatabase.get_path_feature = MagicMock(return_value=feature_path_stops_fake)        

        stops_all_fake = [{'Name': 20, 'RouteName': 10, 'Description': 10, 'TimeWindowStart': None, 'ArriveTime': None, 'Sequence': 2, 'SHAPE@X': 123.45, 'SHAPE@Y': 543.21, 'ViolatedConstraint_2': 'Erro na geração'}]
        route.geodatabase.search_data = MagicMock(return_value=stops_all_fake)

        result = route._get_stops()

        self.assertEqual(result, stops_all_fake)

        route.geodatabase.get_path_feature.assert_called_with("Stops")
        route.geodatabase.search_data.assert_called_with(feature_path_stops_fake, ['Name', 'RouteName', 'Sequence', 'TimeWindowStart', 'SHAPE@X', 'SHAPE@Y'])

    @freeze_time("2021-03-16")
    @patch('service.route.utils')
    @patch('service.route.BaseRoute')
    @patch('service.route.Config')
    @patch('service.route.Geodatabase')
    def test_construct_payload(self, mock_Geodatabase, mock_Config, mock_BaseRoute, mock_utils):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        mock_utils.get_unique_values_from_items = MagicMock(return_value=[10])

        logger_fake = MagicMock(return_value=LogFake())
        route = Route(logger_fake)

        executives_fake = [{'attributes': {'id': 10, 'nome': 'João'}}]
        route._get_executives = MagicMock(return_value=executives_fake)
        stops_all_fake = [{'Name': 20, 'RouteName': 10, 'Description': 10, 'TimeWindowStart': None, 'ArriveTime': None, 'Sequence': 2, 'SHAPE@X': 123.45, 'SHAPE@Y': 543.21, 'ViolatedConstraint_2': 'Erro na geração'}]
        route._get_stops = MagicMock(return_value=stops_all_fake)

        date20210317_fake = datetime.datetime(2021, 3, 17, 0, 0, 0)
        date20210318_fake = datetime.datetime(2021, 3, 18, 0, 0, 0)
        route.base_route.get_route_day = MagicMock(side_effect=[date20210317_fake, date20210318_fake])

        work_areas = [{'attributes': {'id': 1, 'polo': 'Region A', 'carteira': 'Central'}}]
        route._get_work_areas = MagicMock(return_value=work_areas)

        item_route_fake = {
                    "attributes": {
                    "empresa": "Company Test"
                }}
        route.base_route.construct_payload = MagicMock(return_value=item_route_fake)

        companies = [{'id': 20, 'empresa': 'Padaria', 'carteiraId': 1, 'executivoId': 10}]
        result = route._construct_payload(companies)

        self.assertEqual(result, [item_route_fake])

        route._get_executives.assert_called_with(companies)
        route._get_stops.assert_called_with()
        mock_utils.get_unique_values_from_items.assert_called_with('RouteName', stops_all_fake)

        date20210316_fake = datetime.datetime(2021, 3, 16, 0, 0, 0)
        route.base_route.get_route_day.assert_any_call(date20210316_fake)

        route._get_work_areas.assert_called_with()
        route.base_route.construct_payload.assert_called_with(
                    companies[0], executives_fake[0]['attributes'], 
                    1, date20210317_fake, date20210316_fake, None, 
                    work_areas[0]['attributes'], 
                    stops_all_fake[0]['SHAPE@X'], stops_all_fake[0]['SHAPE@Y'])

    @patch('service.route.BaseRoute')
    @patch('service.route.Config')
    @patch('service.route.Geodatabase')
    def test_run(self, mock_Geodatabase, mock_Config, mock_BaseRoute):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        logger_fake = MagicMock(return_value=LogFake())
        route = Route(logger_fake)

        route._make_layer_route = MagicMock(return_value=None)
        
        #polo_travelmode = [{ 'polo': 'Region A', 'modoviagem': 'Walking' }]
        polo_travelmode = [{ 'id': 30, 'modoviagem': 'Walking' }]
        route.base_route.get_carteira_and_travelmode_of_work_areas = MagicMock(return_value=polo_travelmode)

        companies_fake = [{'id': 20, 'empresa': 'Padaria', 'carteiraId': 30, 'executivoId': 10}]
        route._get_companies = MagicMock(return_value=companies_fake)
        route._get_work_areas = MagicMock(return_value=None)
        route.base_route.filter_company_by_id = MagicMock(return_value=None)
        route._load_companies_to_stops = MagicMock(return_value=None)
        route._solve_route = MagicMock(return_value=None)
        
        payload_fake = [{
                    "attributes": {
                    "empresa": "Company Test"
                }}]
        route._construct_payload = MagicMock(return_value=payload_fake)

        executives_ids_fake = ['10']
        route.base_route.get_executives_ids = MagicMock(return_value=executives_ids_fake)

        route.base_route.publish_new_routes = MagicMock(return_value=None)

        route._clear_objects_route = MagicMock(return_value=None)

        route.run()

        route._make_layer_route.assert_called_with()
        route.base_route.get_carteira_and_travelmode_of_work_areas.assert_called_with()
        route._get_companies.assert_called_with(polo_travelmode[0])
        route.base_route.filter_company_by_id.assert_called_with(polo_travelmode[0])
        route._load_companies_to_stops.assert_called_with()
        route._solve_route.assert_called_with(polo_travelmode[0])
        route._construct_payload.assert_called_with(companies_fake)
        route.base_route.get_executives_ids.assert_called_with(companies_fake)
        route.base_route.publish_new_routes.assert_called_with(executives_ids_fake, payload_fake)
        route._clear_objects_route.assert_called_with()

class ArcpyFake:
    pass

class LogFake:
    pass

class DescribeFake():
    def __init__(self):
        self.spatialReference = "SIRGAS2000"
class RouteLayerFake():
    def getOutput(self, param):
        return None

class RouteOutputFake():
    def saveACopy(self, param):
        return None