from unittest import TestCase
from mock import patch, MagicMock
from mock.mock import ANY
import datetime
from helper.log import Log

from service.notification import Notification

class TestNotification(TestCase):

    @classmethod
    def setUpClass(self):
        self.log_fake = MagicMock(return_value=Log) 
        self.process_name = 'job-1234'
        self.params = {
            'work_areas_feature_url': '/feature/work-area',
            'geocode_companies': '/feature/geocode',
            'leads_feature_url': '/feature/leads',
            'routes_feature_url': '/feature/routes',
            'non_route_companies_feature_url': '/feature/non_route',
            'non_geocode_companies': '/feature/non_geocoded'
        }

    def get_instance(self):
        return Notification(self.process_name, self.params, self.log_fake)

    def notification_instance(self):
        instance = self.get_instance()
        instance.params['environment'] = 'production'
        return instance

    def notification_instance_not_prod(self):
        instance = self.get_instance()
        instance.params['environment'] = 'staging'
        return instance
    
    @patch('service.notification.Mail')
    @patch('service.notification.feature_server')
    def test_start_process(self, mock_feature_server, mock_Mail):
        
        total_work_areas = 1
        total_geocode_with_route = 10
        total_companies = 100
        mock_feature_server.count_feature_data = MagicMock(side_effect=[total_work_areas, total_geocode_with_route, total_companies])

        notification = self.notification_instance()

        notification.start_process()
        
        subject = 'Processo: job-1234 - Início da Execução'
        mock_Mail.return_value.send.assert_called_once_with(ANY, ANY, subject)

        mock_feature_server.count_feature_data.assert_any_call(self.params['work_areas_feature_url'], "polo IS NOT NULL AND carteira IS NOT NULL AND inativo = 0")
        mock_feature_server.count_feature_data.assert_any_call(self.params['geocode_companies'], "roteirizar <> 0")
        mock_feature_server.count_feature_data.assert_any_call(self.params['leads_feature_url'], "roteirizar <> 0")

        self.assertEqual(total_work_areas, notification.total_work_areas)
        self.assertEqual(total_geocode_with_route, notification.total_geocode_with_route)
        self.assertEqual(total_companies, notification.total_companies)

    @patch('service.notification.Mail')
    @patch('service.notification.feature_server')
    def test_start_process_not_prod(self, mock_feature_server, mock_Mail):
        
        mock_feature_server.count_feature_data = MagicMock(return_value=None)

        notification = self.notification_instance_not_prod()
        notification.start_process()
        
        mock_Mail.return_value.send.assert_not_called()
        mock_feature_server.count_feature_data.assert_not_called()


    @patch('service.notification.Config')
    @patch('service.notification.Mail')
    @patch('service.notification.feature_server')
    def test_finish_process(self, mock_feature_server, mock_Mail, mock_Config):
        
        date20210424 = datetime.datetime(2021, 4, 24, 0, 0, 0)
        mock_Config.return_value.route_generation_date = date20210424

        total_routes_generated = 108
        total_companies_non_routes = 1
        total_companies_non_geocoded = 1
        mock_feature_server.count_feature_data = MagicMock(side_effect=[total_routes_generated, total_companies_non_routes, total_companies_non_geocoded])

        notification = self.notification_instance()

        notification.total_work_areas = 1
        notification.total_geocode_with_route = 10
        notification.total_companies = 100

        notification.finish_process()
        
        subject = 'Processo: job-1234 - Fim da Execução'
        mock_Mail.return_value.send.assert_called_once_with(ANY, ANY, subject)

        mock_feature_server.count_feature_data.assert_any_call(self.params['routes_feature_url'], "datacriacao BETWEEN Date '2021-4-24 00:00:00' AND Date '2021-4-24 23:59:59'")
        mock_feature_server.count_feature_data.assert_any_call(self.params['non_route_companies_feature_url'], "datageracaorota BETWEEN Date '2021-4-24 00:00:00' AND Date '2021-4-24 23:59:59'")
        mock_feature_server.count_feature_data.assert_any_call(self.params['non_geocode_companies'], "datageocodificacao BETWEEN Date '2021-4-24 00:00:00' AND Date '2021-4-24 23:59:59'")

        self.assertEqual(total_routes_generated, notification.total_routes_generated)
        self.assertEqual(total_companies_non_routes, notification.total_companies_non_routes)

    @patch('service.notification.Config')
    @patch('service.notification.Mail')
    @patch('service.notification.feature_server')
    def test_finish_process_not_prod(self, mock_feature_server, mock_Mail, mock_Config):    

        mock_feature_server.count_feature_data = MagicMock(return_value=None)

        notification = self.notification_instance_not_prod()
        notification.finish_process()
        
        mock_Mail.return_value.send.assert_not_called()
        mock_feature_server.count_feature_data.assert_not_called()

    @patch('service.notification.Mail')
    @patch('service.notification.feature_server')
    def test_error_process(self, mock_feature_server, mock_Mail):
        
        notification = self.notification_instance()

        message = 'ERRO001'
        notification.error_process(message)
        
        subject = 'Processo: job-1234 - Erro na Execução'
        mock_Mail.return_value.send.assert_called_once_with(ANY, ANY, subject)

    @patch('service.notification.Mail')
    @patch('service.notification.feature_server')
    def test_error_process_not_prod(self, mock_feature_server, mock_Mail):
        
        notification = self.notification_instance_not_prod()

        message = 'ERRO001'
        notification.error_process(message)
        
        mock_Mail.return_value.send.assert_not_called()

    @patch('service.notification.Mail')
    @patch('service.notification.feature_server')
    def test_time_check_in_out_long(self, mock_feature_server, mock_Mail):
        
        notification = self.notification_instance()

        message = 'CHECKINOUT'
        notification.time_check_in_out_long(message)
        
        subject = 'Processo: job-1234 - Tempo de Execução'
        mock_Mail.return_value.send.assert_called_once_with(ANY, ANY, subject)        

    @patch('service.notification.Mail')
    @patch('service.notification.feature_server')
    def test_time_check_in_out_long_not_prod(self, mock_feature_server, mock_Mail):
        
        notification = self.notification_instance_not_prod()

        message = 'CHECKINOUT'
        notification.time_check_in_out_long(message)
        
        mock_Mail.return_value.send.assert_not_called()