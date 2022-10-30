from unittest import TestCase
from mock import patch, MagicMock
from datetime import datetime
from config import Config
import helper.utils as utils

from service.orchestrator import Orchestrator
from service.vehicle_routing_problem import VehicleRoutingProblem

FT_COMPANIES_WITH_ROUTE = "EmpresasRoteirizadas"

class TestOrchestrator(TestCase):

    @classmethod
    def setUpClass(self):
        self.config_fake = MagicMock(return_value=Config())
        self.config_fake.get_env_run = MagicMock(return_value="test")
        self.config_fake.path_network = "path/network"
        self.log_fake = MagicMock(return_value=LogFake())
        self.continue_process_fake = False
        self.gdb_finale_fake = 'path/folder'
    
    def test_normalize_visit_options(self):

        orchestrator = Orchestrator(self.log_fake, self.config_fake, self.continue_process_fake)
        
        orchestrator.gdb_finale = self.gdb_finale_fake
        companies_with_routes_fake = [
            {
                'OBJECTID': 101,
                'ID_ROTA': 1,
                'OPCOES': 1,
            },
            {
                'OBJECTID': 201,
                'ID_ROTA': 2,
                'OPCOES': 1,
            }            
        ]
        orchestrator.geodatabase.search_data = MagicMock(return_value=companies_with_routes_fake)
        orchestrator.geodatabase.update_data = MagicMock(return_value=None)

        groups_companies_fake = {
            'GEO_1122': {
                'IBGE_3366': {},
                'IBGE_4477': {}
            }
        }
        
        orchestrator.normalize_visit_options(groups_companies_fake)

        companies_with_routes_expected = companies_with_routes_fake
        companies_with_routes_expected[1]['OPCOES'] = 2
        where_geo_id_expected = "GEO_ID in ('GEO_1122')"
        orchestrator.geodatabase.update_data.assert_called_with(self.gdb_finale_fake, FT_COMPANIES_WITH_ROUTE, ["OBJECTID", "OPCOES"], where_geo_id_expected, companies_with_routes_expected, "OBJECTID")

    def test_group_by_vrp_limit_visit(self):
        group_by_geo = {
        '91348#SJC': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": 3
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": 3
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": 3
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": 3
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": 3
            },
        ],
        '91348#CARAGUA': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ],
        '91348#TAUBATE': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'TAUBATE',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'TAUBATE',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'TAUBATE',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'TAUBATE',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'TAUBATE',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ],
        '91348#SANTOS': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SANTOS',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SANTOS',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SANTOS',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SANTOS',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SANTOS',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ],
        '91348#UBATUBA': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'UBATUBA',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 1,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'UBATUBA',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 1,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'UBATUBA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 1,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'UBATUBA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 1,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'UBATUBA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 1,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ],
        }

        num_total_routes = 5 # total de rotas que vão ser geradas
        num_visits_per_route = 4 # total de vistas por rota

        orchestrator = Orchestrator(self.log_fake, self.config_fake, self.continue_process_fake)

        group_by_vrp = orchestrator._group_by_vrp(group_by_geo, num_total_routes, num_visits_per_route)

        expected = {
            '91348#UBATUBA': {
                "num_routes": 1,
                "limit_visit": 4,
                "limit_km": None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#SJC': {
                "num_routes": 1,
                "limit_visit": 3,
                "limit_km": None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': 3}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': 3}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': 3}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': 3}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': 3}]
            },
            '91348#CARAGUA': {
                "num_routes": 1,
                "limit_visit": 4,
                "limit_km": None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#TAUBATE': {
                "num_routes": 1,
                "limit_visit": 4,
                "limit_km": None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#SANTOS': {
                "num_routes": 1,
                "limit_visit": 4,
                "limit_km": None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            }
        }

        self.assertEqual(group_by_vrp['companies'], expected)

    def test_group_by_vrp_5_county_5_routes_1_priority(self):
        group_by_geo = {
            '91348#SJC': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
            ],
            '91348#CARAGUA': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
            ],
            '91348#TAUBATE': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
            ],
            '91348#SANTOS': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SANTOS',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SANTOS',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SANTOS',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SANTOS',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SANTOS',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
            ],
            '91348#UBATUBA': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'UBATUBA',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 1,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'UBATUBA',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 1,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'UBATUBA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 1,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'UBATUBA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 1,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'UBATUBA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 1,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ],
        }

        num_total_routes = 5 # total de rotas que vão ser geradas
        num_visits_per_route = 4 # total de vistas por rota

        orchestrator = Orchestrator(self.log_fake, self.config_fake, self.continue_process_fake)

        group_by_vrp = orchestrator._group_by_vrp(group_by_geo, num_total_routes, num_visits_per_route)

        expected = {
            '91348#UBATUBA': {
                "num_routes": 1,
                "limit_visit": 4,
                "limit_km":  None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#SJC': {
                "num_routes": 1,
                "limit_visit": 4,
                "limit_km":  None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#CARAGUA': {
                "num_routes": 1,
                "limit_visit": 4,
                "limit_km":  None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#TAUBATE': {
                "num_routes": 1,
                "limit_visit": 4,
                "limit_km":  None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#SANTOS': {
                "num_routes": 1,
                "limit_visit":  4,
                "limit_km":  None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            }
        }

        self.assertEqual(group_by_vrp['companies'], expected)

    def test_group_by_7_county_to_5_routes(self):
        group_by_geo = {
            '91348#SJC': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ],
            '91348#CARAGUA': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ],
            '91348#TAUBATE': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'TAUBATE',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'TAUBATE',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'TAUBATE',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'TAUBATE',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'TAUBATE',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ],
            '91348#SANTOS': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SANTOS',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SANTOS',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SANTOS',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SANTOS',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SANTOS',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ],
            '91348#UBATUBA': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'UBATUBA',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'UBATUBA',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'UBATUBA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'UBATUBA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'UBATUBA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ],
            '91348#CAMPOS': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CAMPOS',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CAMPOS',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CAMPOS',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CAMPOS',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CAMPOS',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ],
            '91348#CAMPINAS': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CAMPINAS',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CAMPINAS',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CAMPINAS',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CAMPINAS',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CAMPINAS',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ],
        }

        num_total_routes = 5 # total de rotas que vão ser geradas
        num_visits_per_route = 4 # total de vistas por rota

        orchestrator = Orchestrator(self.log_fake, self.config_fake, self.continue_process_fake)

        group_by_vrp = orchestrator._group_by_vrp(group_by_geo, num_total_routes, num_visits_per_route)

        expected = {
            '91348#SJC': {
                "num_routes": 1,
                "limit_visit":  4,
                'limit_km':  None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#CARAGUA': {
                "num_routes": 1,
                "limit_visit":  4,
                'limit_km':  None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#TAUBATE': {
                "num_routes": 1,
                "limit_visit":  4,
                'limit_km':  None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#SANTOS': {
                "num_routes": 1,
                "limit_visit":  4,
                'limit_km':  None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#UBATUBA': {
                "num_routes": 1,
                "limit_visit":  4,
                'limit_km':  None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            }
        }

        self.assertEqual(group_by_vrp['companies'], expected)

    def test_group_by_1_county_to_2_routes(self):
        group_by_geo = {
            '91348#SJC': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ]
        }

        num_total_routes = 2 # total de rotas que vão ser geradas
        num_visits_per_route = 3 # total de vistas por rota

        orchestrator = Orchestrator(self.log_fake, self.config_fake, self.continue_process_fake)

        group_by_vrp = orchestrator._group_by_vrp(group_by_geo, num_total_routes, num_visits_per_route)

        expected = {
            '91348#SJC': {
                "num_routes": 2,
                "limit_visit":  3,
                "limit_km":  None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            }
        }

        self.assertEqual(group_by_vrp['companies'], expected)

    def test_construct_dictionary(self):

        orchestrator = Orchestrator(self.log_fake, self.config_fake, self.continue_process_fake)

        excel_companies = [
            {'IBGE': 'Central', 'CD_LOGN': "Mary", 'GEO_ID': 1}, 
            {'IBGE': 'Central', 'CD_LOGN': "Mary", 'GEO_ID': 1},
            {'IBGE': 'Florida', 'CD_LOGN': "Adan", 'GEO_ID': 2},
            {'IBGE': 'Miami', 'CD_LOGN': "Adan", 'GEO_ID': 2}
        ]

        result = orchestrator._construct_dictionary(excel_companies)

        expected = {
            '1': {
                '1#Central': [{
                    'IBGE': 'Central',
                    'CD_LOGN': 'Mary',
                    'GEO_ID': 1
                }, {
                    'IBGE': 'Central',
                    'CD_LOGN': 'Mary',
                    'GEO_ID': 1
                }]
            },
            '2': {
                '2#Miami': [{
                    'IBGE': 'Miami',
                    'CD_LOGN': 'Adan',
                    'GEO_ID': 2
                }],
                '2#Florida': [{
                    'IBGE': 'Florida',
                    'CD_LOGN': 'Adan',
                    'GEO_ID': 2
                }]
            }
        }

        self.assertEqual(result, expected)

    def test_group_by_3_county_to_2_routes(self):
            group_by_geo = {
            '91348#SJC': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
            ],
            '91348#CARAGUA': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
            ],
            '91348#TAUBATE': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
            ],
        }

            num_total_routes = 2 # total de rotas que vão ser geradas
            num_visits_per_route = 3 # total de vistas por rota

            orchestrator = Orchestrator(self.log_fake, self.config_fake, self.continue_process_fake)

            group_by_vrp = orchestrator._group_by_vrp(group_by_geo, num_total_routes, num_visits_per_route)

            expected = {
                '91348#SJC': {
                    "num_routes": 1,
                    "limit_visit": 3,
                    "limit_km": None,
                    "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
                },
                '91348#CARAGUA': {
                    "num_routes": 1,
                    "limit_visit": 3,
                    "limit_km": None,
                    "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
                }
            }

            self.assertEqual(group_by_vrp['companies'], expected)

    def test_group_by_vrp_limit_km(self):
        group_by_geo = {
            '91348#SJC': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": 3
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": 3
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": 3
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": 3
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": 3
                },
            ],
            '91348#CARAGUA': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
            ],
            '91348#TAUBATE': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
            ],
            '91348#SANTOS': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SANTOS',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": 50,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SANTOS',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": 50,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SANTOS',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": 50,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SANTOS',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": 50,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SANTOS',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 0,
                    "LIMITE_METROS": 50,
                    "LIMITE_VISITAS": None
                },
            ],
            '91348#UBATUBA': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'UBATUBA',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'UBATUBA',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'UBATUBA',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'UBATUBA',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'UBATUBA',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
            ],
        }

        num_total_routes = 5 # total de rotas que vão ser geradas
        num_visits_per_route = 4 # total de vistas por rota

        orchestrator = Orchestrator(self.log_fake, self.config_fake, self.continue_process_fake)

        group_by_vrp = orchestrator._group_by_vrp(group_by_geo, num_total_routes, num_visits_per_route)

        expected = {
            '91348#UBATUBA': {
                "num_routes": 1,
                "limit_visit": 4,
                "limit_km": None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#SJC': {
                "num_routes": 1,
                "limit_visit": 3,
                "limit_km": None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': 3}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': 3}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': 3}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': 3}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': 3}]
            },
            '91348#CARAGUA': {
                "num_routes": 1,
                "limit_visit": 4,
                "limit_km": None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#TAUBATE': {
                "num_routes": 1,
                "limit_visit": 4,
                "limit_km": None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#SANTOS': {
                "num_routes": 1,
                "limit_visit": 4,
                "limit_km": 50,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': 50, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': 50, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': 50, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': 50, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': 50, 'LIMITE_VISITAS': None}]
            }
        }

        self.assertEqual(group_by_vrp['companies'], expected)

    def test_group_by_vrp_all_priority_5_county_5_routes(self):
        group_by_geo = {
            '91348#SJC': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SJC',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                }
            ],
            '91348#CARAGUA': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'CARAGUA',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                }
            ],
            '91348#TAUBATE': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'TAUBATE',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                }
            ],
            '91348#SANTOS': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SANTOS',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SANTOS',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'SANTOS',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
            ],
            '91348#UBATUBA': [
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'UBATUBA',
                    "EMPRESA": 'EMPRESA 1',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'UBATUBA',
                    "EMPRESA": 'EMPRESA 2',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
                {
                    "GEO_ID": 1,
                    "MUNICIPIO": 'UBATUBA',
                    "EMPRESA": 'EMPRESA 3',
                    "PRIORIDADE_AGENDADO": 1,
                    "LIMITE_METROS": None,
                    "LIMITE_VISITAS": None
                },
            ],
        }

        num_total_routes = 5 # total de rotas que vão ser geradas
        num_visits_per_route = 5 # total de vistas por rota

        orchestrator = Orchestrator(self.log_fake, self.config_fake, self.continue_process_fake)

        group_by_vrp = orchestrator._group_by_vrp(group_by_geo, num_total_routes, num_visits_per_route)

        expected = {
            '91348#SJC': {
                "num_routes": 1,
                "limit_visit": 5,
                "limit_km": None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#CARAGUA': {
                "num_routes": 1,
                "limit_visit": 5,
                "limit_km": None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'CARAGUA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#TAUBATE': {
                "num_routes": 1,
                "limit_visit": 5,
                "limit_km": None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'TAUBATE', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#SANTOS': {
                "num_routes": 1,
                "limit_visit": 5,
                "limit_km": None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SANTOS', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            },
            '91348#UBATUBA': {
                "num_routes": 1,
                "limit_visit": 5,
                "limit_km": None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'UBATUBA', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 1, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            }
        }

        self.assertEqual(group_by_vrp['companies'], expected)

    def test_group_by_3_county_to_1_routes(self):
        group_by_geo = {
            '91348#SJC': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'SJC',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ],
            '91348#CARAGUA': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'CARAGUA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ],
            '91348#PARAIBUNA': [
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 1',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 2',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
            {
                "GEO_ID": 1,
                "MUNICIPIO": 'PARAIBUNA',
                "EMPRESA": 'EMPRESA 3',
                "PRIORIDADE_AGENDADO": 0,
                "LIMITE_METROS": None,
                "LIMITE_VISITAS": None
            },
        ]
        }

        num_total_routes = 1 # total de rotas que vão ser geradas
        num_visits_per_route = 3 # total de vistas por rota

        orchestrator = Orchestrator(self.log_fake, self.config_fake, self.continue_process_fake)

        group_by_vrp = orchestrator._group_by_vrp(group_by_geo, num_total_routes, num_visits_per_route)

        expected = {
            '91348#SJC': {
                "num_routes": 1,
                "limit_visit":  3,
                "limit_km":  None,
                "orders": [{'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 1', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 2', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}, {'GEO_ID': 1, 'MUNICIPIO': 'SJC', 'EMPRESA': 'EMPRESA 3', 'PRIORIDADE_AGENDADO': 0, 'LIMITE_METROS': None, 'LIMITE_VISITAS': None}]
            }
        }

        self.assertEqual(group_by_vrp['companies'], expected)

    @patch('service.vehicle_routing_problem.VehicleRoutingProblem')
    def test_execute(self, mock_VehicleRoutingProblem):
        
        orchestrator = Orchestrator(self.log_fake, self.config_fake, self.continue_process_fake)

        orchestrator._generate_geojson = MagicMock(return_value=None)
        orchestrator._generate_csv = MagicMock(return_value=None)

        orchestrator._delete_gdb_temp = MagicMock(return_value=None)

        fields_excel_fake = ['field1', 'field2']
        orchestrator._get_fields_file = MagicMock(return_value=fields_excel_fake)
        
        dic_fake = {'GEOID1#SJC': [{'field1': 'value1'}], 'GEOID2#TAUBATE':[{'field1': 'value1'}]}
        utils.read_file_xlsx = MagicMock(return_value=None)
        orchestrator._construct_dictionary = MagicMock(return_value=dic_fake)

        companies_fake = {
            "companies" : {
                '91347#9855': {
                    'limit_km': 50000,
                    'limit_visit': 3,
                    'num_routes': 1,
                    'orders': [{
                        'DT_INICIO': '2022-04-24 00:00:00',
                        'DT_FIM': '2022-05-01 00:00:00',
                        'FLG_SMNA': 'SEMANA 24/04/22 - 01/05/22',
                        'NOME_GEO': 'CN - ITABUNA - 1',
                        'GEO_ID': 91347,
                        'CD_EXEC_ATUAL': 46336,
                        'RANK': 12,
                        'NU_EC': 1028617876,
                        'STR_MIS_CAD': 'MISSÕES: NEGOCIAR PRODUTO - RR [EC 1028617876]',
                        'DT_ATLZZ': '2022-05-01 00:00:00',
                        'LIMITE_VISITAS': 3,
                        'PRIORIDADE_AGENDADO': 0,
                        'LATITUDE_Y': -14.67464095,
                        'LONGITUDE_X': -39.37521509,
                        'LIMITE_METROS': 50000,
                        'SG_SO_UF': 'BA',
                        'IBGE': 9855,
                        'NM_MUNICIPIO': 'ITAJUIPE',
                        'DC_END_FISICO_EC': 'R SANTOS DUMONT 13',
                        'NU_SO_CEP': 45630000,
                        'DC_COMPLEMENTO_END': 'CENTRO  '
                    }]
                },    
                '91347#9951740': {
                    'limit_km': 50000,
                    'limit_visit': 3,
                    'num_routes': 1,
                    'orders': [{
                        'DT_INICIO': '2022-04-24 00:00:00',
                        'DT_FIM': '2022-05-01 00:00:00',
                        'FLG_SMNA': 'SEMANA 24/04/22 - 01/05/22',
                        'NOME_GEO': 'CN - ITABUNA - 1',
                        'GEO_ID': 91347,
                        'CD_EXEC_ATUAL': 46336,
                        'RANK': 6,
                        'NU_EC': 1105157978,
                        'STR_MIS_CAD': 'MISSÕES: RR HABILITADO, SEM RECEITA [EC 1105157978], (INATIVO NO MÊS)  INATIVO DE 7 A 30 DIAS [EC 1105157978]',
                        'DT_ATLZZ': '2022-04-24 09:27:00',
                        'LIMITE_VISITAS': 3,
                        'PRIORIDADE_AGENDADO': 0,
                        'LATITUDE_Y': -14.62916356,
                        'LONGITUDE_X': -39.55667058,
                        'LIMITE_METROS': 50000,
                        'SG_SO_UF': 'BA',
                        'IBGE': 9951740,
                        'NM_MUNICIPIO': 'COARACI',
                        'DC_END_FISICO_EC': 'AV ITAPITANGA ',
                        'NU_SO_CEP': 45638000,
                        'DC_COMPLEMENTO_END': '66 TERREO CENTRO  '
                    }]
                }
            },
            "route_not_roteirized": []
        }

        orchestrator._delete_gdb_finale_if_exists = MagicMock(return_value=None)
        orchestrator._generate_gdb_finale = MagicMock(return_value=None)
        utils.create_folder_temp = MagicMock(return_value=None)

        orchestrator._group_by_vrp = MagicMock(return_value=companies_fake)

        path_finale_fake = "path/finale"
        num_route_fake = 5
        num_total_visit_per_day_fake = 4
        #vrp = VehicleRoutingProblem(self.log_fake, self.config_fake, "test", companies_fake, path_finale_fake, fields_excel_fake, num_route_fake, num_total_visit_per_day_fake, None, [])
        #vrp.execute = MagicMock(return_value=None)

        orchestrator.execute = MagicMock(return_value=None)

        param_excel_fake = "path/excel"
        orchestrator.execute(param_excel_fake, path_finale_fake, num_route_fake, num_total_visit_per_day_fake)


class LogFake:
    pass