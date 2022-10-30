from unittest import TestCase
from mock import patch, MagicMock
import os

from config import Config

class TestConfig(TestCase):

    def set_mock_os(self, mock_os, folder_temp):
        self.folder = 'folder_example'
        self.folder_temp = os.path.join(self.folder, folder_temp)
        mock_os.path.dirname = MagicMock(return_value=self.folder)
        mock_os.path.abspath = MagicMock(return_value=None)
        mock_os.path.join = MagicMock(side_effect=os.path.join)
        mock_os.getenv = MagicMock(return_value="test")
        self.mock_os = mock_os
            
    @patch('config.os')
    def test_get_folder_temp(self, mock_os):
        self.set_mock_os(mock_os, 'temp_routes')

        config = Config("routes")
        config.root_process_folder = self.folder
        folder = config.get_folder_temp()

        expected = os.path.join(self.folder, 'job-routes', 'test', 'temp_routes')
        self.assertEqual(expected, folder)

    @patch('config.os')
    def test_get_folder_template(self, mock_os):
        self.set_mock_os(mock_os, 'template')

        config = Config()
        folder = config.get_folder_template()

        self.assertEqual(self.folder_temp, folder)

        mock_os.path.dirname.assert_called_with(None)        

    @patch('config.os')
    @patch('config.json')
    @patch('config.open')
    def test_get_params(self, mock_open, mock_json, mock_os):        
        self.set_mock_os(mock_os, 'temp_routes')
        
        ENV = 'staging'
        mock_os.getenv = MagicMock(return_value=ENV)

        CONF = {'staging': 
            {
                'path_network': 'path/folder/file',
                'environment': 'staging'
            }
        }
        mock_json.load = MagicMock(return_value=CONF)

        config_filename_fake = os.path.join(self.folder, 'config.json')
        mock_os.path.join = MagicMock(return_value=config_filename_fake)
        
        mock_open.open = MagicMock(return_value="json_file")
        
        config = Config()
        result = config.get_params()
        self.assertEqual(CONF['staging'], result)

        mock_os.path.dirname.assert_called_with(None)
        mock_os.path.join.assert_called_with(self.folder, 'config.json')

    @patch('config.utils')
    @patch('config.os')
    def test_create_folder_temp_when_exists(self, mock_os, mock_utils):
        self.set_mock_os(mock_os, "temp_routes")

        config = Config("routes")
        config.create_folder_temp()

        mock_utils.delete_if_exists.assert_called()
        mock_utils.create_folder.assert_called()

    @patch('config.utils')
    @patch('config.os')
    def test_get_job_process_folder(self, mock_os, mock_utils):
        self.set_mock_os(mock_os, "temp_routes")

        config = Config()
        result = config.get_job_process_folder()

        expected = os.path.join(config.root_process_folder, config.process_name, "test")
        self.assertEqual(result, expected)