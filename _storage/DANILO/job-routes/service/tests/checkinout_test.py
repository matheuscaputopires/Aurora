from unittest import TestCase
from mock import patch, MagicMock
from mock.mock import ANY
from freezegun import freeze_time
import os
import datetime
import json

from service.checkinout import Checkinout

class TestCheckinout(TestCase):

    @classmethod
    def setUpClass(self):
        self.log_fake = MagicMock(return_value=LogFake())
        self.params_fake = {
            "checkinout_feature_url": "https://link-service-arcgis-server/feature/1",
            "leads_feature_url": "https://link-service-arcgis-server/feature/2",
        }

    def _get_mock_arcpy(self):
        arcpyFake = ArcpyFake()
        return MagicMock(return_value=arcpyFake)            

    @patch('service.checkinout.feature_server')
    @patch('service.checkinout.Config')
    @patch('service.checkinout.Geodatabase')
    @patch('service.checkinout.Notification')
    def test_execute(self, mock_Notification, mock_Geodatabase, mock_Config, mock_feature_server):

        mock_Config.return_value.get_env = MagicMock(return_value="test")        
        mock_Config.return_value.get_params = MagicMock(return_value=self.params_fake)

        checkinouts_fake = [{'attributes':{'objectid': 200, 'empresaid': 100}}]
        companies_fake = [{'attributes':{'id': 100}}]
        mock_feature_server.get_feature_data = MagicMock(side_effect=[checkinouts_fake, companies_fake])

        checkinout_near_companies_fake = [{'IN_FID': 1, 'NEAR_FID': 1, 'NEAR_DIST': 20}]
        dict_checkinout_fake = [{'objectid': 1, 'empresaid': 100, 'objectid_server': 200}]
        dict_companies = [{'objectid': 1, 'id': 100, 'polo': 'Region A', 'carteira': 'Central Park', 'empresa': 'Store Tennis', 'nomeexecutivo': 'Mary Wick'}]
        mock_Geodatabase.return_value.search_data = MagicMock(side_effect=[checkinout_near_companies_fake, dict_checkinout_fake, dict_companies])

        checkinout = Checkinout(self.log_fake)
        checkinout._arcpy = self._get_mock_arcpy()

        checkinout.execute()

        mock_Geodatabase.return_value.create.assert_called_once()
        mock_Geodatabase.return_value.create_feature.assert_called()

        mock_feature_server.get_feature_data.assert_any_call(self.params_fake['checkinout_feature_url'], "proximoempresa IS NULL AND empresaid IS NOT NULL")
        mock_feature_server.get_feature_data.assert_any_call(self.params_fake['leads_feature_url'], "id IN (100)")

        fields_ft_checkinout_fake = ['id', 'objectid_server', 'empresaid', 'executivoid', 'proximoempresa', 'polo', 'carteira', 'empresa', 'executivo', 'SHAPE@JSON']
        mock_Geodatabase.return_value.insert_data.assert_any_call(checkinouts_fake, ANY, fields_ft_checkinout_fake)

        fields_ft_company_fake = ['id', 'empresa', 'polo', 'carteira', 'nomeexecutivo', 'SHAPE@JSON']
        mock_Geodatabase.return_value.insert_data.assert_any_call(companies_fake, ANY, fields_ft_company_fake)

        checkinout._arcpy.analysis.GenerateNearTable.assert_called_once_with(ANY, ANY, ANY, "20 Meters", "NO_LOCATION", "NO_ANGLE", "ALL", 10000, "GEODESIC")

        payload_fake = [{
                'attributes': {
                    'objectid': 200,
                    'proximoempresa': 1,
                    'polo': 'Region A',
                    'carteira': 'Central Park',
                    'empresa': 'Store Tennis',
                    'executivo': 'Mary Wick'
                }                
        }]
        mock_feature_server.update_feature_data.assert_called_once_with(self.params_fake['checkinout_feature_url'], payload_fake)

    @patch('service.checkinout.feature_server')
    @patch('service.checkinout.Config')
    @patch('service.checkinout.Geodatabase')
    @patch('service.checkinout.Notification')
    def test_execute_error_nothing_items(self, mock_Notification, mock_Geodatabase, mock_Config, mock_feature_server):

        mock_Config.return_value.get_env = MagicMock(return_value="test")        
        mock_Config.return_value.get_params = MagicMock(return_value=self.params_fake)

        checkinouts_fake = []
        mock_feature_server.get_feature_data = MagicMock(return_value=checkinouts_fake)

        checkinout = Checkinout(self.log_fake)
        checkinout._arcpy = self._get_mock_arcpy()

        checkinout.execute()

        mock_Geodatabase.return_value.create.assert_called_once()
        mock_Geodatabase.return_value.create_feature.assert_called()

        mock_feature_server.get_feature_data.assert_called_with(self.params_fake['checkinout_feature_url'], "proximoempresa IS NULL AND empresaid IS NOT NULL")



class ArcpyFake:
    pass

class LogFake:
    pass
