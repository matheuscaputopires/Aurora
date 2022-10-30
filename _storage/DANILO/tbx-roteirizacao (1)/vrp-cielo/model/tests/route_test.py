from unittest import TestCase
from datetime import datetime

from model.route import Route

class TestRoute(TestCase):

    def test_get_values(self):

        name = 'DEYVID1° - Bairro CENTRO (Foco Conquista)#20211115'

        companies = [
            {'CD_LOGN': 'Mary', 'LIST_ID': 'Central', 'GEO_ID': 1, 'COST': 1.1, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5}, 
            {'CD_LOGN': 'Mary', 'LIST_ID': 'Central', 'GEO_ID': 2, 'COST': 1.2, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5},
            {'CD_LOGN': 'Mary', 'LIST_ID': 'Florida', 'GEO_ID': 2, 'COST': 0.4, 'LATITUDE_Y': -15, 'LONGITUDE_X': -9},
            {'CD_LOGN': 'Mary', 'LIST_ID': 'Miami', 'GEO_ID': 2, 'COST': 1.8, 'LATITUDE_Y': -10, 'LONGITUDE_X': -5}
        ]

        route = Route(name, name, 3, 50)

        result = route.get_values()

        expected = {
            'Name': name,
            'StartDepotName': name,
            'EarliestStartTime': datetime.strptime("15/11/2021 09:00:00", '%d/%m/%Y %H:%M:%S'),
            'LatestStartTime': datetime.strptime("15/11/2021 18:00:00", '%d/%m/%Y %H:%M:%S'),
            'CostPerUnitTime': float(1.0),
            'MaxOrderCount': 3,
            'AssignmentRule': 2,
            'MaxTotalTime': 580,
            'MaxTotalDistance': 50
        }

        self.assertEqual(result, expected)
