from unittest import TestCase
from mock import patch, MagicMock

import os
from helper.log import Log
import helper.utils as utils

class TestLog(TestCase):

    @classmethod
    def setUpClass(self):
        self._path = os.path.dirname(os.path.abspath(__file__))
        self._path_log = os.path.join(self._path, 'logs')
        self._path_log_top = os.path.join(os.path.abspath(os.path.join("tests", os.pardir)), "helper/logs")

    @patch('helper.log.Config')
    def test_setup_log(self, mock_Config):        

        config_fake = MagicMock()
        config_fake.get_env_run = MagicMock(return_value="test")
        mock_Config.return_value = config_fake

        logger = Log()
        logger.config.get_folder_main = MagicMock(return_value=self._path)

        logger.setup_log()
        file_log_is_created = False
        self.assertEqual(logger.logger.name, 'tbx-roterizacao')

        path_log = self._path_log
        if os.path.exists(path_log) or os.path.exists(self._path_log_top):
           file_log_is_created = True
        
        self.assertTrue(file_log_is_created)
        logger.logger.root.handlers[0].close()

    @patch('helper.log.Config')
    def test_error(self, mock_Config):

        config_fake = MagicMock()
        config_fake.get_env_run = MagicMock(return_value="test")
        mock_Config.return_value = config_fake        
        
        logger = Log()
        MESSAGE = 'Message example of error'
        logger.config.get_folder_main = MagicMock(return_value=self._path)

        arcpyFake = ArcpyFake()
        logger._arcpy = MagicMock(return_value=arcpyFake)

        logger.setup_log()
        logger.error(MESSAGE)

        logger._arcpy.AddError.assert_called_with(MESSAGE)

    @patch('helper.log.Config')
    def test_info(self, mock_Config):

        config_fake = MagicMock()
        config_fake.get_env_run = MagicMock(return_value="test")
        mock_Config.return_value = config_fake

        logger = Log()
        MESSAGE = 'Message example of information'
        logger.config.get_folder_main = MagicMock(return_value=self._path)

        arcpyFake = ArcpyFake()
        logger._arcpy = MagicMock(return_value=arcpyFake)

        logger.setup_log()
        logger.info(MESSAGE)

        logger._arcpy.AddMessage.assert_called_with(MESSAGE)        

    @patch('helper.log.Config')
    def test_finish(self, mock_Config):

        config_fake = MagicMock()
        config_fake.get_env_run = MagicMock(return_value="test")
        mock_Config.return_value = config_fake        
        
        logger = Log()
        MESSAGE = 'Message example of finish log'
        logger.config.get_folder_main = MagicMock(return_value=self._path)

        logger.info = MagicMock(return_value=None)
        logger._clear_log_files_older_7_days = MagicMock(return_value=None)
        logger.setup_log()
        logger.finish(MESSAGE)

        logger.info.assert_called_with(MESSAGE)
        logger._clear_log_files_older_7_days.assert_called_with()        

    @patch('helper.log.os')
    @patch('helper.log.time')
    @patch('helper.log.Config')
    def test_clear_log_files_older_7_days_when_exists(self, mock_Config, mock_time, mock_os):

        config_fake = MagicMock()
        config_fake.get_env_run = MagicMock(return_value="test")
        mock_Config.return_value = config_fake        
        
        FOLDER = "path/folder_example"
        
        FILES = ['file1', 'file2']
        STATS = FileFake(-1)

        mock_os.listdir = MagicMock(return_value=FILES)
        mock_time.time = MagicMock(return_value=604800)
        mock_os.path.join = MagicMock(return_value=FOLDER)
        mock_os.stat = MagicMock(return_value=STATS)
        mock_os.path.isfile = MagicMock(return_value=True)
        mock_os.remove = MagicMock(return_value=None)

        logger = Log()
        
        logger.info = MagicMock(return_value=None)

        logger._clear_log_files_older_7_days()

        mock_os.listdir.assert_called()
        mock_time.time.assert_called()
        mock_os.path.join.assert_called()
        mock_os.stat.assert_called()
        mock_os.path.isfile.assert_called()
        mock_os.remove.assert_called()
        logger.info.assert_called()


    @classmethod
    def tearDownClass(self):
        utils.delete_if_exists(self._path_log)
        utils.delete_if_exists(self._path_log_top)

class ArcpyFake:
    pass    

class FileFake:
    def __init__(self, time):
        self.st_mtime = time
