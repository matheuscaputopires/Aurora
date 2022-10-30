from unittest import TestCase
from datetime import datetime

from model.depot import Depot

class TestDepot(TestCase):

    def test_get_values(self):

        name = 'DEYVID1° - Bairro CENTRO (Foco Conquista)#20211115'
        latitude_y = -2.123
        longitude_x = -10.123

        depot = Depot(name, latitude_y, longitude_x)

        result = depot.get_values()

        expected = {
            'Name': name,
            'geometry': { 
                "x": longitude_x, 
                "y": latitude_y
            }
        }

        self.assertEqual(result, expected)
