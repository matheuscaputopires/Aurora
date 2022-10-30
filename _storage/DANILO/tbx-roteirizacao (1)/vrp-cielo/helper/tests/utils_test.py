from unittest import TestCase
from mock import patch, MagicMock
from datetime import datetime

import helper.utils as utils

class TestUtils(TestCase):

    @patch('helper.utils.os')
    @patch('helper.utils.shutil')
    def test_delete_folder_if_exists(self, mock_shutil, mock_os):
            
        FOLDER = "path/folder_example"

        mock_os.path.exists = MagicMock(return_value=True)

        utils.delete_if_exists(FOLDER)

        mock_os.path.exists.assert_called_with(FOLDER)
        mock_shutil.rmtree.assert_called_with(FOLDER)

    @patch('helper.utils.os')
    @patch('helper.utils.shutil')
    def test_delete_folder_if_not_exists(self, mock_shutil, mock_os):
            
        FOLDER = "path/folder_example"

        mock_os.path.exists = MagicMock(return_value=False)

        utils.delete_if_exists(FOLDER)

        mock_os.path.exists.assert_called_with(FOLDER)
        mock_shutil.rmtree.assert_not_called()

    @patch('helper.utils.os')
    @patch('helper.utils.config')
    @patch('helper.utils.shutil')
    def test_create_folder_temp_when_exists(self, mock_shutil, mock_config, mock_os):

        FOLDER = "path/folder_example"

        mock_config.get_folder_temp = MagicMock(return_value=FOLDER) 
        mock_os.path.exists = MagicMock(return_value=True)

        utils.create_folder_temp(FOLDER)

        mock_shutil.rmtree.assert_called_with(FOLDER)
        mock_os.makedirs.assert_called_with(FOLDER)

    @patch('helper.utils.os')
    @patch('helper.utils.config')
    def test_create_folder_temp_not_exists(self, mock_config, mock_os):

        FOLDER = "path/folder_example"

        mock_config.get_folder_temp = MagicMock(return_value=FOLDER) 
        mock_os.path.exists = MagicMock(return_value=False)

        utils.create_folder_temp(FOLDER)

        mock_os.remove.assert_not_called()
        mock_os.makedirs.assert_called_with(FOLDER)

    def test_datetime_to_timestamp(self):

        date_20210315 = datetime(2021, 3, 15, 0, 0, 0)
        result = utils.datetime_to_timestamp(date_20210315)

        result_expected = date_20210315.timestamp() * 1000
        self.assertEqual(result, result_expected)

    def test_timestamp_to_datetime(self):
        
        date_mock = datetime(2021, 3, 15, 0, 0, 0)
        timestamp = date_mock.timestamp() * 1000
        result = utils.timestamp_to_datetime(timestamp)

        result_expected = date_mock
        self.assertEqual(result, result_expected)

    def test_timestamp_to_datetime_is_negative(self):
        timestamp = -1615777200000.0
        result = utils.timestamp_to_datetime(timestamp)

        result_expected = datetime(1976, 1, 1, 0, 0, 0)
        self.assertEqual(result, result_expected)

    def test_timestamp_to_datetime_is_none(self):
        timestamp = None
        result = utils.timestamp_to_datetime(timestamp)

        result_expected = datetime(1976, 1, 1, 0, 0, 0)
        self.assertEqual(result, result_expected)

    def test_datetime_to_yyyymmddhhmmss(self):

        date = datetime(2021, 3, 15, 0, 0, 0)
        result = utils.datetime_to_yyyymmddhhmmss(date)

        expected = "2021-03-15 00:00:00"
        self.assertEqual(result, expected)
