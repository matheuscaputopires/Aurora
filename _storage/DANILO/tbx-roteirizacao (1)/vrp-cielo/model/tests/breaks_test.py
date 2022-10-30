from unittest import TestCase
import datetime

from model.breaks import Breaks
import model.helper as helper

class TestBreaks(TestCase):

    def test_get_values(self):

        route_name = 'DEYVID1° - Bairro CENTRO (Foco Conquista)#20211115'
        service_time = datetime.datetime(2020, 1, 1, 10, 0, 0)

        breaks = Breaks(route_name, service_time)

        result = breaks.get_values()

        expected = {
            "RouteName": route_name,
            "ServiceTime": service_time,
            "TimeWindowStart": helper.get_date_from_route_name(route_name).replace(hour=12, minute=0, second=0, microsecond=0),
            "TimeWindowEnd": helper.get_date_from_route_name(route_name).replace(hour=13, minute=0, second=0, microsecond=0),
            "Precedence": 1
        }

        self.assertEqual(result, expected)
