from unittest import TestCase, mock
from mock import patch, MagicMock
import sys

from main import Main

class TestMain(TestCase):

    @patch('main.Config')
    @patch('main.Log')
    @patch('main.Orchestrator')
    def test_execute(self, mock_Orchestrator, mock_Log, mock_Config):

        config_fake = MagicMock()
        config_fake.get_env_run = MagicMock(return_value="test")
        mock_Config.return_value = config_fake

        # sys_argv = MagicMock()
        # sys_argv.argv = MagicMock(side_effect=[1, 2, 3, 4, 5, 6])
        # mock_argv.return_value = sys_argv

        Orchestrator_fake = MagicMock()
        mock_Orchestrator.return_value = Orchestrator_fake

        logger_fake = MagicMock(return_value=LogFake())
        main = Main(logger_fake)

        main.debug = False

        main._arcpy = MagicMock(return_value = ArcpyFake())

        main._arcpy.CheckExtension = MagicMock(return_value="Available")
        main._arcpy.CheckOutExtension = MagicMock(return_value=[True])        
        
        xlsx_fake = './files/base_imagem.xlsx'
        path_network = '/path/network'
        saida_fake = '../resultado/'
        number_day_route_fake = 5
        number_visit_route_fake = 15
        continue_process_fake = '1'
        #main._arcpy.GetParameterAsText = MagicMock(side_effect=[xlsx_fake, path_network, saida_fake, 
        #number_day_route_fake, number_visit_route_fake, continue_process_fake])

        testargs = [None, xlsx_fake, path_network, saida_fake, number_day_route_fake, 15, '1']
        with patch.object(sys, 'argv', testargs):
            main.execute()

        main._arcpy.CheckExtension.assert_called_with("network")
        main._arcpy.CheckOutExtension.assert_called_with("network")
        self.assertEqual(config_fake.path_network, path_network)
        Orchestrator_fake.execute.assert_called_with(xlsx_fake, saida_fake, number_day_route_fake, number_visit_route_fake)

class LogFake:
    pass

class ArcpyFake:
    pass