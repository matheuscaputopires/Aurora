from unittest import TestCase
from mock import patch, MagicMock

from service.work_areas import WorkAreas

class TestWorkAreas(TestCase):

    @classmethod
    def setUpClass(self):
        self.log_fake = MagicMock(return_value=LogFake()) 
        self.params = {
            'work_areas_feature_url': '/feature/work-area',
        }

    def get_instance(self):
        return WorkAreas(self.log_fake, self.params)
    
    @patch('service.work_areas.feature_server')
    def test_get(self, mock_feature_server):
        
        work_areas_fake = [{'id': 123, 'polo': 'Region A', 'carteira': 'Central Park'}]
        mock_feature_server.get_feature_data = MagicMock(return_value=work_areas_fake)

        work_area = self.get_instance()

        result = work_area.get()
    
        mock_feature_server.get_feature_data.assert_any_call(self.params['work_areas_feature_url'], "polo IS NOT NULL AND carteira IS NOT NULL AND inativo = 0")

        self.assertEqual(result, work_areas_fake)

class LogFake:
    pass