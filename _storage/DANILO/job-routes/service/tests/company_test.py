from unittest import TestCase
from mock import patch, MagicMock
from freezegun import freeze_time
import os
import datetime
import json

from service.company import Company

class TestCompany(TestCase):

    @patch('service.company.feature_server')
    @patch('service.company.utils')
    @patch('service.company.Config')
    @patch('service.company.Geodatabase')
    @patch('service.company.BaseRoute')
    @patch('service.company.Schedule')
    def test_synchronize(self, mock_Schedule, mock_BaseRoute, mock_Geodatabase, mock_Config, mock_utils, mock_feature_server):
        
        schedule_fake_id = [{'attributes': {'empresaid': 10}}, {'attributes': {'empresaid': 20}}]

        PARAMS_FAKE = {
            "schedules_feature_url": "https://link-service-arcgis-server/feature/4",
            "leads_feature_url": "https://link-service-arcgis-server/feature/1",
            "executive_feature_url": "https://link-service-arcgis-server/feature/2",
            "local_feature_fields": ["id", "carteiraid", "datamaiorreceita", "executivoid","SHAPE@XY"],
            "company_name": "feature_name",
            "service_time_minutes": 15
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        companies_fake = []
        companies_fake.append({'attributes' : {'objectid': 1, 'globalid': 1, 'id': 1, 'carteiraid': 1, 'datamaiorreceita': 12345679, 'tipoalerta': 'ALERT_VISIT'}, 'geometry': {'y': 123, 'x': 321}})
        companies_fake.append({'attributes' : {'objectid': 2, 'globalid': 1, 'id': 2, 'carteiraid': 1, 'datamaiorreceita': 12345679, 'tipoalerta': None}, 'geometry': {'y': 123, 'x': 321}})
        executives_fake = [{'attributes': {'carteiraid': 1, 'id': 1}}]
        mock_feature_server.get_feature_data = MagicMock(side_effect=[schedule_fake_id, companies_fake, executives_fake])

        datetime_fake = datetime.datetime(2021, 3, 29, 9, 0, 0)
        mock_utils.timestamp_to_datetime = MagicMock(return_value=datetime_fake)

        log_fake = MagicMock(return_value=LogFake())
        company = Company(log_fake)

        company.geodatabase.get_path = MagicMock(return_value="/path/gdb")

        company.geodatabase.insert_data = MagicMock(return_value=None)

        company.synchronize()

        company.geodatabase.get_path.assert_called_with()
        company.geodatabase.copy_template_feature_to_temp_gdb.assert_called_with(PARAMS_FAKE['company_name'])

        mock_feature_server.get_feature_data.assert_any_call(PARAMS_FAKE['leads_feature_url'], "roteirizar = 1 OR id IN (10,20)")
        mock_feature_server.get_feature_data.assert_any_call(PARAMS_FAKE['executive_feature_url'])

        data_maior_receita_fake = 12345679
        mock_utils.timestamp_to_datetime.assert_called_with(data_maior_receita_fake)

        features_fake = []
        features_fake.append({'attributes': {'id': 1, 'carteiraid': 1, 'datamaiorreceita': datetime_fake, 'tipoalerta': 'ALERT_VISIT', 'latitude': 123, 'longitude': 321, 'executivoid': 1, 'attr_time': PARAMS_FAKE['service_time_minutes'], 'DeliveryQuantity_1': None, 'DeliveryQuantity_2': 1}, 'geometry': {'y': 123, 'x': 321}})
        features_fake.append({'attributes': {'id': 2, 'carteiraid': 1, 'datamaiorreceita': datetime_fake, 'tipoalerta': None, 'latitude': 123, 'longitude': 321, 'executivoid': 1, 'attr_time': PARAMS_FAKE['service_time_minutes'], 'DeliveryQuantity_1': 1, 'DeliveryQuantity_2': None}, 'geometry': {'y': 123, 'x': 321}})
        ft_companies = os.path.join("/path/gdb", PARAMS_FAKE['company_name'])
        company.geodatabase.insert_data.assert_called_with(features_fake, ft_companies, PARAMS_FAKE['local_feature_fields'])


class ArcpyFake:
    pass

class LogFake:
    pass
