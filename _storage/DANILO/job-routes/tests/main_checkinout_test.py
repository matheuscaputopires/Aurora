from unittest import TestCase
from mock import patch, MagicMock
from freezegun import freeze_time

from main_checkinout import MainCheckInOut

class TestMainCheckInOut(TestCase):

    @patch('main_checkinout.open')
    @patch('main_checkinout.json')
    @patch('main_checkinout.Config')
    @patch('main_checkinout.Checkinout')
    @patch('main_checkinout.Log')
    @patch('main_checkinout.Notification')
    def test_execute_no_control_file(self, mock_Notification, mock_Log, mock_Checkinout, mock_Config, mock_json, mock_open):
        mock_Config.return_value.get_env = MagicMock(return_value="test")    
        mock_json.dump = MagicMock(return_value=None)
        
        main = MainCheckInOut()    
        main.execute()

        mock_Checkinout.return_value.execute.assert_called_with()        
        self.assertEqual(mock_json.dump.call_count, 2)

    @patch('main_checkinout.open')
    @patch('main_checkinout.json')
    @patch('main_checkinout.Config')
    @patch('main_checkinout.Checkinout')
    @patch('main_checkinout.Log')
    @patch('main_checkinout.Notification')
    def test_execute_with_control_file_already_created(self, mock_Notification, mock_Log, mock_Checkinout, mock_Config, mock_json, mock_open):
        mock_Config.return_value.get_env = MagicMock(return_value="test")    
        mock_json.dump = MagicMock(return_value=None)
        
        json_fake = {
            'execute': False,
            'time_execute': '2022-01-16 13:00:00'
        }
        mock_json.load = MagicMock(return_value=json_fake)

        main = MainCheckInOut()    
        main.execute()

        mock_Checkinout.return_value.execute.assert_called_with()        
        self.assertEqual(mock_json.dump.call_count, 2)        

    @freeze_time("2022-01-16 18:00:00")
    @patch('main_checkinout.open')
    @patch('main_checkinout.json')
    @patch('main_checkinout.Config')
    @patch('main_checkinout.Checkinout')
    @patch('main_checkinout.Log')
    @patch('main_checkinout.Notification')
    def test_execute_running_process_more_limit(self, mock_Notification, mock_Log, mock_Checkinout, mock_Config, mock_json, mock_open):

        mock_Config.return_value.get_env = MagicMock(return_value="test")    
        mock_json.dump = MagicMock(return_value=None)
        
        json_fake = {
            'execute': True,
            'time_execute': '2022-01-16 13:00:00'
        }
        mock_json.load = MagicMock(return_value=json_fake)
        
        main = MainCheckInOut() 
        main.limit_execution = 4
        main.execute()

        mock_Checkinout.return_value.execute.assert_not_called()
        mock_json.dump.assert_not_called()
        mock_Notification.return_value.time_check_in_out_long.assert_called_once()

    @freeze_time("2022-01-16 13:30:00")
    @patch('main_checkinout.open')
    @patch('main_checkinout.json')
    @patch('main_checkinout.Config')
    @patch('main_checkinout.Checkinout')
    @patch('main_checkinout.Log')
    @patch('main_checkinout.Notification')
    def test_execute_running_process_within_limit(self, mock_Notification, mock_Log, mock_Checkinout, mock_Config, mock_json, mock_open):

        mock_Config.return_value.get_env = MagicMock(return_value="test")    
        mock_json.dump = MagicMock(return_value=None)
        
        json_fake = {
            'execute': True,
            'time_execute': '2022-01-16 13:00:00'
        }
        mock_json.load = MagicMock(return_value=json_fake)
        
        main = MainCheckInOut()
        main.limit_execution = 1    
        main.execute()

        mock_Checkinout.return_value.execute.assert_not_called()
        mock_json.dump.assert_not_called()
        mock_Notification.return_value.time_check_in_out_long.assert_not_called()        

    @patch('main_checkinout.open')
    @patch('main_checkinout.json')
    @patch('main_checkinout.Config')
    @patch('main_checkinout.Checkinout')
    @patch('main_checkinout.Log')
    @patch('main_checkinout.Notification')
    def test_execute_exception(self, mock_Notification, mock_Log, mock_Checkinout, mock_Config, mock_json, mock_open):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Checkinout.return_value.execute = Exception('Boom!')

        main = MainCheckInOut()
        main.execute()

        mock_Notification.return_value.error_process.assert_called()

