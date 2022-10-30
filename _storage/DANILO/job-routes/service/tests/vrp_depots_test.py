from unittest import TestCase
from mock import patch, MagicMock
import random
import datetime
import helper.utils as utils

from service.vrp_depots import VRPDepots

class TestVRPDepots(TestCase):

    def _get_input_data(self, name, x, y):
        return {
                    'attributes': {
                        'Name': name
                    },
                    'geometry': {
                        'x': x,
                        'y': y
                    }
                }
    @patch('service.vrp_depots.utils')
    @patch('service.vrp_depots.BaseRoute')
    @patch('service.vrp_depots.kmeans_plusplus')
    @patch('service.vrp_depots.np')
    @patch('service.vrp_depots.Config')
    @patch('service.vrp_depots.Geodatabase')
    @patch('service.vrp_depots.WorkAreas')
    def test_create_depots_with_60_companies(self, mock_WorkAreas, mock_Geodatabase, mock_Config, mock_numpy, mock_kmeans, mock_BaseRoute, mock_utils):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        mock_numpy.array = MagicMock(return_value=None)
        kmeans_fake = [[111.22, 222.11], [333.22, 444.11], [555.22, 666.11]], 3
        mock_kmeans.return_value = kmeans_fake

        mock_utils.format_date_dmY = utils.format_date_dmY
        mock_utils.datetime_to_timestamp = utils.datetime_to_timestamp
        mock_utils.calc_distance_2_points = MagicMock(side_effect=[0.7, 0.5, 0.6, 0.7, 0.5, 0.6])

        log_fake = MagicMock(return_value=LogFake())
        
        depots = VRPDepots(log_fake)

        depots._arcpy = MagicMock(return_value=ArcpyFake())

        date_20210425 = datetime.datetime(2021, 4, 25, 0, 0, 0)
        date_20210426 = datetime.datetime(2021, 4, 26, 0, 0, 0)
        date_20210427 = datetime.datetime(2021, 4, 27, 0, 0, 0)
        depots.base_route.get_route_day = MagicMock(side_effect=[date_20210425, date_20210426, date_20210427, date_20210425, date_20210426, date_20210427])

        feature_companies = 'ordersxpto'
        feature_depots = 'Depotsxpto'
        depots.geodatabase.get_path_feature = MagicMock(side_effect=[feature_companies, feature_depots, feature_companies, feature_depots])

        polo_travelmode = { 'id': '1', 'polo': 'Region A', 'modoviagem': 'Walking' }
        work_areas = [{'attributes': polo_travelmode}]
        mock_WorkAreas.return_value.get = MagicMock(return_value=work_areas)

        depots._filter_area_by_polo_travelmode = MagicMock(return_value=True)

        companies = []
        lat_lng_expected = []
        date_20210426_09h00 = datetime.datetime(2021, 4, 26, 9, 0, 0)
        date_20210426_13h00 = datetime.datetime(2021, 4, 26, 13, 0, 0)
        date_20211201_09h00 = datetime.datetime(2021, 12, 1, 9, 0, 0)
        for num in range(59):
            x = random.random()
            y = random.random()
            if num == 57:
                companies.append({'TimeWindowStart': date_20210426_09h00, 'SHAPE@X': x, 'SHAPE@Y': y})
            elif num == 58:
                companies.append({'TimeWindowStart': date_20210426_13h00, 'SHAPE@X': x, 'SHAPE@Y': y})
            elif num == 59:
                companies.append({'TimeWindowStart': date_20211201_09h00, 'SHAPE@X': x, 'SHAPE@Y': y})
            else:
                companies.append({'TimeWindowStart': None, 'SHAPE@X': x, 'SHAPE@Y': y})
            lat_lng_expected.append([x, y])
        depots.geodatabase.search_data = MagicMock(return_value=companies)

        depots.geodatabase.delete_data = MagicMock(return_value=None)
        depots.geodatabase.insert_data = MagicMock(return_value=None)

        result = depots.create(polo_travelmode)

        expected = ['2021']
        self.assertEqual(result, expected)

        depots.geodatabase.get_path_feature.assert_any_call('Orders')
        depots.geodatabase.get_path_feature.assert_any_call('Depots')
        depots.geodatabase.search_data.assert_called_with(feature_companies, ['Name', 'TimeWindowStart', 'Description', 'SHAPE@X', 'SHAPE@Y'], "Description='1'")                
        mock_numpy.array.assert_called_with(lat_lng_expected)        
        mock_kmeans.assert_called_with(None, n_clusters=2, random_state=0)

        depots.base_route.get_route_day.assert_any_call()
        depots.base_route.get_route_day.assert_any_call(date_20210425)
        depots.base_route.get_route_day.assert_any_call(date_20210426)
        
        depots.geodatabase.delete_data.assert_called_with(feature_depots, "1=1")

        input_data_expected = []
        input_data_expected.append(self._get_input_data(work_areas[0]['attributes']['id']+"#20210425", kmeans_fake[0][0][0], kmeans_fake[0][0][1]))
        input_data_expected.append(self._get_input_data(work_areas[0]['attributes']['id']+"#20210426", kmeans_fake[0][1][0], kmeans_fake[0][1][1]))
        input_data_expected.append(self._get_input_data(work_areas[0]['attributes']['id']+"#20210427", kmeans_fake[0][2][0], kmeans_fake[0][2][1]))
        depots.geodatabase.insert_data.assert_called_with(input_data_expected, feature_depots, ['Name', 'SHAPE@XY'])

        result_second_call = depots.create(polo_travelmode)
        self.assertEqual(result_second_call, expected)


    @patch('service.vrp_depots.kmeans_plusplus')
    @patch('service.vrp_depots.np')
    @patch('service.vrp_depots.Config')
    @patch('service.vrp_depots.Geodatabase')
    @patch('service.vrp_depots.BaseRoute')
    @patch('service.vrp_depots.WorkAreas')
    def test_change_position(self, mock_WorkAreas, mock_BaseRoute, mock_Geodatabase, mock_Config, mock_numpy, mock_kmeans):
        
        mock_Config.return_value.get_env = MagicMock(return_value="test")

        log_fake = MagicMock(return_value=LogFake())
        
        depots = VRPDepots(log_fake)

        fake_depot = [{'Name': '1159101#20220315', 'SHAPE@JSON': '{"x":-46.707649999999944,"y":-23.680889999999977,"spatialReference":{"wkid":4326,"latestWkid":4326}}'}]
        depots.geodatabase.get_path_feature = MagicMock(return_value="Depots")

        depots.geodatabase.search_data = MagicMock(return_value=fake_depot)

        depots.change_position("1159101#20220315", -46.707649999999944, -23.680889999999977)

        result = [{'Name': '1159101#20220315', 'SHAPE@JSON': '{"x": -46.707649999999944, "y": -23.680889999999977, "spatialReference": {"wkid": 4326, "latestWkid": 4326}}'}]

        depots.geodatabase.update_data.assert_called_with("Depots", ['Name', 'SHAPE@JSON'], '1=1', result ,"Name")

class ArcpyFake:
    pass

class LogFake:
    pass

class DescribeFake():
    def __init__(self):
        self.spatialReference = "SIRGAS2000"