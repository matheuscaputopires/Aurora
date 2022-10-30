from unittest import TestCase
from datetime import datetime

from model.order import Order

class TestOrder(TestCase):

    def test_get_values(self):

        name = 'Mary'
        description = 'Mary#20211115'
        service_time = 20
        revenue = 0.5
        latitude_y = -2.123
        longitude_x = -10.123

        order = Order(name, description, revenue, latitude_y, longitude_x)

        result = order.get_values()

        expected = {
            'Name': name, 
            'Description': description,
            'ServiceTime': service_time,
            'Revenue': 0.5,
            'AssignmentRule': 3,
            'geometry': { 
                "x": longitude_x, 
                "y": latitude_y
            }
        }

        self.assertEqual(result, expected)
