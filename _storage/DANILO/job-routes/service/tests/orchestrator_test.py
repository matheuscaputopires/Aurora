from unittest import TestCase
from mock import patch, MagicMock
from freezegun import freeze_time
import os
import datetime
import json

from service.orchestrator import Orchestrator

class TestOrchestrator(TestCase):

    @patch('service.orchestrator.Company')
    @patch('service.orchestrator.BaseRoute')
    @patch('service.orchestrator.VehicleRoutingProblem')
    @patch('service.orchestrator.Config')
    @patch('service.orchestrator.Geodatabase')
    @patch('service.orchestrator.Notification')
    def test_generate_route_vrp(self, mock_Notification, mock_Geodatabase, mock_Config, mock_VehicleRoutingProblem, mock_BaseRoute, mock_Company):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {
            "type_tool": "VRP"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        mock_vrp = MagicMock()
        mock_VehicleRoutingProblem.return_value = mock_vrp

        log_fake = MagicMock(return_value=LogFake())
        orchestrator = Orchestrator(log_fake)

        orchestrator.base_route.normalize_companies_server = MagicMock(return_value=None)
        mock_Company.synchronize = MagicMock(return_value=None)

        orchestrator.generate_route()

        mock_vrp.run.assert_called_with()

    @patch('service.orchestrator.Company')
    @patch('service.orchestrator.BaseRoute')
    @patch('service.orchestrator.Route')
    @patch('service.orchestrator.Config')
    @patch('service.orchestrator.Geodatabase')
    @patch('service.orchestrator.Notification')
    def test_generate_tool_route(self, mock_Notification, mock_Geodatabase, mock_Config, mock_Tool_Route, mock_BaseRoute, mock_Company):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        PARAMS_FAKE = {
            "type_tool": "Route"
        }
        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)

        mock_route = MagicMock()
        mock_Tool_Route.return_value = mock_route

        log_fake = MagicMock(return_value=LogFake())
        orchestrator = Orchestrator(log_fake)

        orchestrator.base_route.normalize_companies_server = MagicMock(return_value=None)
        mock_Company.synchronize = MagicMock(return_value=None)
        orchestrator._synchronize_schedules = MagicMock(return_value=None)

        orchestrator.generate_route()

        orchestrator._synchronize_schedules.assert_not_called()

        mock_route.run.assert_called_with()

    @patch('service.orchestrator.Company')
    @patch('service.orchestrator.BaseRoute')
    @patch('service.orchestrator.Config')
    @patch('service.orchestrator.Geodatabase')
    @patch('service.orchestrator.Notification')
    def test_execute(self, mock_Notification, mock_Geodatabase, mock_Config, mock_BaseRoute, mock_Company):

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Geodatabase = MagicMock(return_value=None)
        mock_BaseRoute = MagicMock(return_value=None)

        log_fake = MagicMock(return_value=LogFake())
        orchestrator = Orchestrator(log_fake)

        orchestrator.geodatabase.create = MagicMock(return_value=None)
        orchestrator.generate_geocode = MagicMock(return_value=None)
        orchestrator.generate_route = MagicMock(return_value=None)

        orchestrator.execute()

        orchestrator.geodatabase.create.assert_called_with()
        orchestrator.generate_geocode.assert_called_with()
        orchestrator.generate_route.assert_called_with()

        mock_Notification.return_value.start_process.assert_called_once_with()
        mock_Notification.return_value.finish_process.assert_called_once_with()


class ArcpyFake:
    pass

class LogFake:
    pass
