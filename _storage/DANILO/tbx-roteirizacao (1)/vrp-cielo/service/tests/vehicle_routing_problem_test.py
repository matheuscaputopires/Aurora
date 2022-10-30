from unittest import TestCase, mock
from mock import patch, MagicMock
import datetime
from freezegun import freeze_time
from config import Config
from model.route import Route
import os

from service.vehicle_routing_problem import VehicleRoutingProblem

LAYER_NAME_ROUTE = "WorkVehicleRoutingProblem"
TRAVEL_MODE = "Driving Time"

class TestVehicleRoutingProblem(TestCase):

    @classmethod
    def setUpClass(self):
        self.config_fake = MagicMock(return_value=Config())
        self.config_fake.get_env_run = MagicMock(return_value="test")
        self.config_fake.path_network = "path/network"
        self.log_fake = MagicMock(return_value=LogFake())
        self.cursorCompaniesWithRouteFake = MagicMock(return_value=None)
        self.cursorCompaniesWithoutRouteFake = MagicMock(return_value=None)
        self.cursorRoutesWithoutShapeFake = MagicMock(return_value=None)
        self.cursorRoutesFake = MagicMock(return_value=None)
        self.layer_name_process_fake = "WorkVehicleRoutingProblem"

    def _get_mock_arcpy(self):
        arcpyFake = ArcpyFake()
        return MagicMock(return_value=arcpyFake)                

    @freeze_time("2021-11-15")
    @patch('service.vehicle_routing_problem.Geodatabase')
    def test_create_layer_route(self, mock_Geodatabase):
        process_name = ""
        companies = []
        num_total_route_fake = 5
        num_total_visit_per_route_fake = 3
        limit_km_fake = 30
        
        vrp = VehicleRoutingProblem(self.log_fake, self.config_fake, process_name, self.layer_name_process_fake, companies, 
        None, None, num_total_route_fake, num_total_visit_per_route_fake, limit_km_fake,
        self.cursorCompaniesWithRouteFake, self.cursorCompaniesWithoutRouteFake, self.cursorRoutesWithoutShapeFake, self.cursorRoutesFake)
        
        vrp._arcpy = self._get_mock_arcpy()
        MakeVehicleRoutingProblemAnalysisLayer_fake = MagicMock()
        MakeVehicleRoutingProblemAnalysisLayer_fake.getOutput = MagicMock(return_value=None)
        vrp._arcpy.na.MakeVehicleRoutingProblemAnalysisLayer = MagicMock(return_value=MakeVehicleRoutingProblemAnalysisLayer_fake)

        vrp._create_layer_route()

        start_route_day_fake = datetime.datetime(2021, 11, 15)
        vrp._arcpy.na.MakeVehicleRoutingProblemAnalysisLayer.assert_called_once_with(
            self.config_fake.path_network, 
            LAYER_NAME_ROUTE, 
            TRAVEL_MODE, 
            "Minutes", "Meters", start_route_day_fake.strftime("%Y-%m-%d"), "LOCAL_TIME_AT_LOCATIONS", "ALONG_NETWORK", "Medium", "Medium", "DIRECTIONS", "CLUSTER"
        )
        MakeVehicleRoutingProblemAnalysisLayer_fake.getOutput.assert_called_with(0)

    def test_define_orders(self):

        window_start = datetime.datetime(2020, 1, 1, 10, 0, 0)
        window_end = datetime.datetime(2020, 1, 1, 11, 0, 0)
        companies = [
            {
                'GEO_ID': 123456,
                'CD_LOGN': 'Mary', 
                'IBGE': 'Central',
                'NU_EC': 123,
                'PRIORIDADE_AGENDADO': 1,
                'JANELA_INICIO': window_start, 
                'JANELA_FIM': window_end, 
                'JANELA_INICIO2': None,
                'JANELA_FIM2': None,
                'HORA_INICIO_AGENDAMENTO': None,
                'HORA_FIM_AGENDAMENTO': None,
                'LATITUDE_Y': -10, 
                'LONGITUDE_X': -5
            }
        ]        
        process_name = ""
        num_total_route_fake = 5
        num_total_visit_per_route_fake = 3
        limit_km_fake = 30
        vrp = VehicleRoutingProblem(self.log_fake, self.config_fake, process_name, self.layer_name_process_fake,
        companies, None, None, num_total_route_fake, num_total_visit_per_route_fake, limit_km_fake, 
        self.cursorCompaniesWithRouteFake, self.cursorCompaniesWithoutRouteFake, self.cursorRoutesWithoutShapeFake, self.cursorRoutesFake)

        route_day_fake = datetime.datetime(2021, 11, 15, 9, 0, 0)
        vrp._get_route_day = MagicMock(return_value=route_day_fake)

        path_gdb_fake = "path_gdb"
        vrp.path_gdb = path_gdb_fake

        feature_path_fake = {'Orders': 'OrdersXPTO'}
        vrp.feature_path = feature_path_fake

        vrp.geodatabase.insert_data = MagicMock(return_value=None)

        vrp._define_orders()

        fields = ['Name', 'Description', 'ServiceTime', 'Revenue', 'AssignmentRule', 'SHAPE@JSON']
        orders = [
            {
                'Name': '123', 
                'Description': '123456Central#',
                'ServiceTime': 20,
                'Revenue': 1,
                'AssignmentRule': 3,
                'geometry': { 
                    "x": -5, 
                    "y": -10
                }
            },
        ]
        vrp.geodatabase.insert_data.assert_called_once_with(path_gdb_fake, feature_path_fake['Orders'], fields, orders)

    @mock.patch('random.random')
    def test_define_depots(self, random_mock):
        random_mock.return_value = 1234
        companies = [
            {'CD_LOGN': 'Mary', 'IBGE': 'Central', 'GEO_ID': 1, 'COST': 1.1, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5}, 
            {'CD_LOGN': 'Mary', 'IBGE': 'Central', 'GEO_ID': 2, 'COST': 1.2, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5},
            {'CD_LOGN': 'Mary', 'IBGE': 'Florida', 'GEO_ID': 2, 'COST': 0.4, 'LATITUDE_Y': -15, 'LONGITUDE_X': -9},
            {'CD_LOGN': 'Mary', 'IBGE': 'Miami', 'GEO_ID': 2, 'COST': 1.8, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5}
        ]

        num_total_route_fake = 5
        num_total_visit_per_route_fake = 3
        limit_km_fake = 30
        process_name = ""
        vrp = VehicleRoutingProblem(self.log_fake, self.config_fake, process_name, self.layer_name_process_fake,
        companies, None, None, num_total_route_fake, num_total_visit_per_route_fake, limit_km_fake, 
        self.cursorCompaniesWithRouteFake, self.cursorCompaniesWithoutRouteFake, self.cursorRoutesWithoutShapeFake, self.cursorRoutesFake)
        
        vrp._create_cluster = MagicMock(return_value=[[0, 1]])

        route_day_fake = datetime.datetime(2021, 11, 15, 9, 0, 0)
        vrp._get_route_day = MagicMock(return_value=route_day_fake)

        path_gdb_fake = "path_gdb"
        vrp.path_gdb = path_gdb_fake

        feature_path_fake = {'Depots': 'DepotsXPTO'}
        vrp.feature_path = feature_path_fake

        vrp.geodatabase.insert_data = MagicMock(return_value=None)

        result = vrp._define_depots()

        fields = ['Name', 'SHAPE@JSON']
        depots = [{
            'Name': '1234_1Central#20211115#1', 
            'geometry': { 
                "x": 0, 
                "y": 1
            }
        }]
        vrp.geodatabase.insert_data.assert_called_once_with(path_gdb_fake, feature_path_fake['Depots'], fields, depots)

        expected = depots
        self.assertEqual(result, expected)

    def test_define_pre_routes(self):
        companies = [
            {'CD_LOGN': 'Mary', 'LIST_ID': 'Central', 'GEO_ID': 1, 'COST': 1.1, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5}, 
            {'CD_LOGN': 'Mary', 'LIST_ID': 'Central', 'GEO_ID': 2, 'COST': 1.2, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5},
            {'CD_LOGN': 'Mary', 'LIST_ID': 'Florida', 'GEO_ID': 2, 'COST': 0.4, 'LATITUDE_Y': -15, 'LONGITUDE_X': -9},
            {'CD_LOGN': 'Mary', 'LIST_ID': 'Miami', 'GEO_ID': 2, 'COST': 1.8, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5}
        ]

        process_name = ""
        num_total_route_fake = 5
        num_total_visit_per_route_fake = 3
        limit_km_fake = 30
        vrp = VehicleRoutingProblem(self.log_fake, self.config_fake, process_name, self.layer_name_process_fake,
        companies, None, None, num_total_route_fake, num_total_visit_per_route_fake, limit_km_fake, 
        self.cursorCompaniesWithRouteFake, self.cursorCompaniesWithoutRouteFake, self.cursorRoutesWithoutShapeFake, self.cursorRoutesFake)

        fields = ['Name', 'StartDepotName', 'EarliestStartTime', 'LatestStartTime', 'CostPerUnitTime', 'MaxOrderCount', 'AssignmentRule', 'MaxTotalTime', 'MaxTotalDistance']

        depots = [{"Name": 'test_1#20211123'}]

        path_gdb_fake = "path_gdb"
        vrp.path_gdb = path_gdb_fake

        feature_path_fake = {'Routes': 'DepotsXPTO'}
        vrp.feature_path = feature_path_fake

        vrp.geodatabase.insert_data = MagicMock(return_value=None)

        vrp._define_pre_routes(depots)

        pre_routes = [Route(depots[0]['Name'], depots[0]['Name'], num_total_visit_per_route_fake, limit_km_fake).get_values()]

        vrp.geodatabase.insert_data.assert_called_once_with(path_gdb_fake, feature_path_fake['Routes'], fields, pre_routes)

    def test_generate_routes(self):
        process_name = ""
        companies = []
        num_total_route_fake = 5
        num_total_visit_per_route_fake = 3
        limit_km_fake = 30
        vrp = VehicleRoutingProblem(self.log_fake, self.config_fake, process_name, self.layer_name_process_fake,
        companies, None, None, num_total_route_fake, num_total_visit_per_route_fake, limit_km_fake, 
        self.cursorCompaniesWithRouteFake, self.cursorCompaniesWithoutRouteFake, self.cursorRoutesWithoutShapeFake, self.cursorRoutesFake)

        vrp._arcpy = self._get_mock_arcpy()
        vrp._arcpy.na.Solve = MagicMock(return_value=None)

        path_temp_fake = "temp"
        vrp.path_temp = path_temp_fake

        vrp._generate_routes()

        output_layer_file = os.path.join(path_temp_fake, LAYER_NAME_ROUTE + ".lyrx")
        vrp._arcpy.na.Solve.assert_called_once_with(LAYER_NAME_ROUTE, "HALT", "TERMINATE", None, '')

    @freeze_time("2021-11-13")
    def test_save_companies_with_violations(self):
        companies = [
            {'NU_EC': '123', 'CD_LOGN': 'Mary', 'LIST_ID': 'Central', 'GEO_ID': 1, 'COST': 1.1, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5}, 
            {'NU_EC': '1234', 'CD_LOGN': 'Mary', 'LIST_ID': 'Central', 'GEO_ID': 2, 'COST': 1.2, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5},
            {'NU_EC': '12345', 'CD_LOGN': 'Mary', 'LIST_ID': 'Florida', 'GEO_ID': 2, 'COST': 0.4, 'LATITUDE_Y': -15, 'LONGITUDE_X': -9},
            {'NU_EC': '123456', 'CD_LOGN': 'Mary', 'LIST_ID': 'Miami', 'GEO_ID': 2, 'COST': 1.8, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5}
        ]

        process_name = ""
        fields = ["NU_EC", "CD_LOGN", "LIST_ID", "GEO_ID", "COST", "LATITUDE_Y", "LONGITUDE_X"]
        num_total_route_fake = 5
        num_total_visit_per_route_fake = 3
        limit_km_fake = 30
        vrp = VehicleRoutingProblem(self.log_fake, self.config_fake, process_name, self.layer_name_process_fake,
        companies, None, fields, num_total_route_fake, num_total_visit_per_route_fake, limit_km_fake, 
        self.cursorCompaniesWithRouteFake, self.cursorCompaniesWithoutRouteFake, self.cursorRoutesWithoutShapeFake, self.cursorRoutesFake)

        violation = [
            {  
                'Name': '123',
                'ViolatedConstraint_1': 'MaxTotalTime', 
                'ViolatedConstraint_2': None, 
                'ViolatedConstraint_3': None, 
                'ViolatedConstraint_4': None 
            }
        ]

        vrp.geodatabase.search_data = MagicMock(return_value=violation)

        path_gdb_finale_fake = "path_gdb"
        vrp.path_gdb_finale = path_gdb_finale_fake

        feature_path_fake = {'Orders': 'OrdersXPTO'}
        vrp.feature_path = feature_path_fake

        vrp.geodatabase.insert_data = MagicMock(return_value=None)

        vrp.geodatabase.get_violated_domain = MagicMock(return_value="Item Max Total Time")

        vrp._save_companies_with_violations()

        feature_row_expected = ('123', 'Mary', 'Central', '1', '1.1', '-10', '-5', '{"x": "-5", "y": "-10", "spatialReference": {"wkid": 4326}}')
        self.cursorCompaniesWithoutRouteFake.insertRow.assert_called_once_with(feature_row_expected)

    def test_save_route_orders(self):
        companies = [
            {'NU_EC': '123', 'CD_LOGN': 'Mary', 'IBGE': 'Central', 'GEO_ID': 1, 'RANK': 1.1, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5}, 
            {'NU_EC': '1234', 'CD_LOGN': 'Mary', 'IBGE': 'Central', 'GEO_ID': 2, 'RANK': 1.2, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5},
            {'NU_EC': '12345', 'CD_LOGN': 'Mary', 'IBGE': 'Florida', 'GEO_ID': 2, 'RANK': 0.4, 'LATITUDE_Y': -15, 'LONGITUDE_X': -9},
            {'NU_EC': '123456', 'CD_LOGN': 'Mary', 'IBGE': 'Miami', 'GEO_ID': 2, 'RANK': 1.8, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5}
        ]

        process_name = ""
        params = ["NU_EC", "ID_ROTA", "OPCOES", "SEQUENCIA", 'SHAPE@JSON']
        num_total_route_fake = 5
        num_total_visit_per_route_fake = 3
        limit_km_fake = 30
        vrp = VehicleRoutingProblem(self.log_fake, self.config_fake, process_name, self.layer_name_process_fake,
        companies, None, params, num_total_route_fake, num_total_visit_per_route_fake, limit_km_fake, 
        self.cursorCompaniesWithRouteFake, self.cursorCompaniesWithoutRouteFake, self.cursorRoutesWithoutShapeFake, self.cursorRoutesFake)

        orders = [
            {'Sequence': 2, 'Name': '123', 'RouteName': 'teste1#20211120#1', 'ArriveTime': '2021-11-24 10:40', 'IBGE': 'Central', 'GEO_ID': 1, 'RANK': 1.1, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5}, 
        ]

        vrp.geodatabase.search_data = MagicMock(return_value=orders)

        path_gdb_finale_fake = "path_gdb"
        vrp.path_gdb_finale = path_gdb_finale_fake

        vrp.path_gdb = path_gdb_finale_fake

        feature_path_fake = {'Orders': 'OrdersXPTO'}
        vrp.feature_path = feature_path_fake

        vrp.geodatabase.insert_data = MagicMock(return_value=None)

        vrp._save_route_orders()

        fields_orders = ["OBJECTID", "Name", "Sequence", "RouteName", "ArriveTime"]
        vrp.geodatabase.search_data.assert_called_once_with(path_gdb_finale_fake, feature_path_fake['Orders'], fields_orders, 'Sequence IS NOT NULL', 'ORDER BY Sequence ASC')
        
        feature_row_expected = ('123', 'Mary', 'Central', '1', '1.1', '-10', '-5', '{"x": "-5", "y": "-10", "spatialReference": {"wkid": 4326}}')
        self.cursorCompaniesWithoutRouteFake.insertRow.assert_called_once_with(feature_row_expected)        

    def test_save_routes_without_shape(self):
        companies = [
            {'NU_EC': '123', 'CD_LOGN': 'Mary', 'IBGE': 'Central', 'GEO_ID': 1, 'RANK': 1.1, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5}, 
            {'NU_EC': '1234', 'CD_LOGN': 'Mary', 'IBGE': 'Central', 'GEO_ID': 2, 'RANK': 1.2, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5},
            {'NU_EC': '12345', 'CD_LOGN': 'Mary', 'IBGE': 'Florida', 'GEO_ID': 2, 'RANK': 0.4, 'LATITUDE_Y': -15, 'LONGITUDE_X': -9},
            {'NU_EC': '123456', 'CD_LOGN': 'Mary', 'IBGE': 'Miami', 'GEO_ID': 2, 'RANK': 1.8, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5}
        ]

        process_name = ""
        params = ["NU_EC", "ID_ROTA", "OPCOES", "SEQUENCIA", 'SHAPE@JSON']
        num_total_route_fake = 5
        num_total_visit_per_route_fake = 3
        limit_km_fake = 30
        vrp = VehicleRoutingProblem(self.log_fake, self.config_fake, process_name, self.layer_name_process_fake,
        companies, None, params, num_total_route_fake, num_total_visit_per_route_fake, limit_km_fake, 
        self.cursorCompaniesWithRouteFake, self.cursorCompaniesWithoutRouteFake, self.cursorRoutesWithoutShapeFake, self.cursorRoutesFake)

        vrp._get_feature_path = MagicMock(return_value={'Routes': 'RoutesXPTO'})

        routes_fake = [{
            'Name': '91144CAMACARI#20220513#1',
            'MaxOrderCount': 3,
            'TotalCost': 64.11563041619956,
            'TotalTime': 124.11563041619956,
            'TotalOrderServiceTime': 60.0,
            'TotalTravelTime': 4.115630416199565,
            'TotalDistance': 2170.9965726585433,
            'OrderCount': 3,
            'MaxTotalDistance': 50000.0,
            'SHAPE@JSON': None
        }]
        vrp.geodatabase.search_data = MagicMock(return_value=routes_fake)
        vrp.geodatabase.insert_data = MagicMock(return_value=None)

        vrp._save_routes()

        feature_row_expected = ('91144CAMACARI#20220513#1', 3, 64.11563041619956, 124.11563041619956, 60.0, 4.115630416199565, 2170.9965726585433, 3, 50000.0)
        self.cursorRoutesWithoutShapeFake.insertRow.assert_called_once_with(feature_row_expected)
        self.cursorRoutesFake.assert_not_called()

    def test_save_routes(self):
        companies = [
            {'NU_EC': '123', 'CD_LOGN': 'Mary', 'IBGE': 'Central', 'GEO_ID': 1, 'RANK': 1.1, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5}, 
            {'NU_EC': '1234', 'CD_LOGN': 'Mary', 'IBGE': 'Central', 'GEO_ID': 2, 'RANK': 1.2, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5},
            {'NU_EC': '12345', 'CD_LOGN': 'Mary', 'IBGE': 'Florida', 'GEO_ID': 2, 'RANK': 0.4, 'LATITUDE_Y': -15, 'LONGITUDE_X': -9},
            {'NU_EC': '123456', 'CD_LOGN': 'Mary', 'IBGE': 'Miami', 'GEO_ID': 2, 'RANK': 1.8, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5}
        ]

        process_name = ""
        params = ["NU_EC", "ID_ROTA", "OPCOES", "SEQUENCIA", 'SHAPE@JSON']
        num_total_route_fake = 5
        num_total_visit_per_route_fake = 3
        limit_km_fake = 30
        vrp = VehicleRoutingProblem(self.log_fake, self.config_fake, process_name, self.layer_name_process_fake,
        companies, None, params, num_total_route_fake, num_total_visit_per_route_fake, limit_km_fake, 
        self.cursorCompaniesWithRouteFake, self.cursorCompaniesWithoutRouteFake, self.cursorRoutesWithoutShapeFake, self.cursorRoutesFake)

        vrp._get_feature_path = MagicMock(return_value={'Routes': 'RoutesXPTO'})

        routes_fake = [{
            'Name': '91144CAMACARI#20220513#1',
            'MaxOrderCount': 3,
            'TotalCost': 64.11563041619956,
            'TotalTime': 124.11563041619956,
            'TotalOrderServiceTime': 60.0,
            'TotalTravelTime': 4.115630416199565,
            'TotalDistance': 2170.9965726585433,
            'OrderCount': 3,
            'MaxTotalDistance': 50000.0,
            'SHAPE@JSON': {'x': 1, 'y': 1}
        }]
        vrp.geodatabase.search_data = MagicMock(return_value=routes_fake)
        vrp.geodatabase.insert_data = MagicMock(return_value=None)

        vrp._save_routes()

        feature_row_expected = ('91144CAMACARI#20220513#1', 3, 64.11563041619956, 124.11563041619956, 60.0, 4.115630416199565, 2170.9965726585433, 3, 50000.0, {'x': 1, 'y': 1})
        self.cursorRoutesFake.insertRow.assert_called_once_with(feature_row_expected)
        self.cursorRoutesWithoutShapeFake.assert_not_called()

class ArcpyFake:
    def __init__(self):
        self.env = {}
class LogFake:
    pass