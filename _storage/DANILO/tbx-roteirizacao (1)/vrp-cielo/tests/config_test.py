from unittest import TestCase
from mock import patch, MagicMock
from mock.mock import mock_open
import os

from config import Config

class TestConfig(TestCase):    

    @classmethod
    def setUpClass(self):
        self._config_file = {
            'url_base': 'url_base',
            'feature_url': 'feature_url',
            'work_areas_url': 'work_areas_url',
            'executive_url': 'executive_url',
            'ags_url': 'ags_url',
            'generate_token_url': 'generate_token_url',
            'user_hierarchies': 'user_hierarchies'
        }

    @patch('config.os')
    @patch('config.json')
    @patch('config.open')
    def test_get_params(self, mock_open, mock_json, mock_os):        
        FOLDER = 'path/folder_example'
        mock_os.path.dirname = MagicMock(return_value=FOLDER)
        mock_os.path.abspath = MagicMock(return_value=None)
    
        CONF = {'staging': {'path_network': 'path/folder/file'}}
        mock_json.load = MagicMock(return_value=CONF)

        config_filename_fake = os.path.join(FOLDER, 'config.json')
        mock_os.path.join = MagicMock(return_value=config_filename_fake)
        
        mock_open.open = MagicMock(return_value="json_file")
        
        config = Config()
        env = "Homologação"
        username = "mary"
        password = "abc123"
        result = config.get_params(env, username, password)

        self.assertEqual(CONF['staging'], result)

        mock_os.path.dirname.assert_called_with(None)
        mock_os.path.join.assert_called_with(FOLDER, 'config.json')

    def test_get_url_workarea(self):
        config = Config()
        config.config_file = self._config_file

        result = config.get_url_workarea()

        expected = self._config_file['url_base'] + self._config_file['feature_url'] + self._config_file['work_areas_url']
        self.assertEqual(result, expected)

    def test_get_url_executive(self):
        config = Config()
        config.config_file = self._config_file

        result = config.get_url_executive()

        expected = self._config_file['url_base'] + self._config_file['feature_url'] + self._config_file['executive_url']
        self.assertEqual(result, expected)

    def test_get_url_ags(self):
        config = Config()
        config.config_file = self._config_file

        result = config.get_url_ags()

        expected = self._config_file['url_base'] + self._config_file['ags_url']
        self.assertEqual(result, expected)              

    def test_get_url_generate_token(self):
        config = Config()
        config.config_file = self._config_file

        result = config.get_url_generate_token()

        expected = self._config_file['url_base'] + self._config_file['generate_token_url']
        self.assertEqual(result, expected)

    def test_get_url_user_hierarchies(self):
        config = Config()
        config.config_file = self._config_file

        result = config.get_url_user_hierarchies()

        expected = self._config_file['url_base'] + self._config_file['user_hierarchies']
        self.assertEqual(result, expected)                 