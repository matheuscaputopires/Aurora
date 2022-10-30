from unittest import TestCase
from mock import patch, MagicMock

from main import Main

class TestMain(TestCase):

    @patch('main.Config')
    @patch('main.Orchestrator')
    @patch('main.Log')
    def test_execute(self, mock_Log, mock_Orchestrator, mock_Config):

        mock_Config.return_value.get_env = MagicMock(return_value="test")

        route = Main()    
        route.execute()

        mock_Orchestrator.return_value.execute.assert_called_with()

    @patch('main.Config')
    @patch('main.Orchestrator')
    @patch('main.Log')
    @patch('main.Notification')
    def test_execute_exception(self, mock_Notification, mock_Log, mock_Orchestrator, mock_Config):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Orchestrator.return_value.execute = Exception('Boom!')

        route = Main()
        route.execute()

        mock_Notification.return_value.error_process.assert_called()




