import os
from config import Config
import helper.utils as utils
from esri import feature_server
from service.base_route import BaseRoute
from service.notification import Notification
from esri.geodatabase import Geodatabase
from service.vehicle_routing_problem import VehicleRoutingProblem
from service.route import Route
from service.geocode import Geocode
from helper.errors import Error
from service.company import Company

class Orchestrator():
    def __init__(self, logger):
        self.logger = logger
        self._arcpy = __import__("arcpy") if Config().get_env() != "test" else None
        self.params = Config().get_params()
        self.geodatabase = Geodatabase(logger)
        self.base_route = BaseRoute(logger)
        self.notification = Notification(self.logger.process_full_name, self.params, logger)
        self.company = Company(logger)

    def generate_geocode(self):
        geocode = Geocode(self.logger)
        geocode.run()

    def generate_route(self):
        self.base_route.normalize_companies_server()
        self.company.synchronize()

        self.logger.info("Tool de rota: %s" % (self.params['type_tool']))
        if self.params['type_tool'] == 'VRP':
            vrp = VehicleRoutingProblem(self.logger)
            vrp.run()
        elif self.params['type_tool'] == 'Route':
            tool_route = Route(self.logger)
            tool_route.run()
        else:
            raise Error('Param route not define in config.json!')

    def execute(self):
        self.geodatabase.create()
        self.notification.start_process()
        self.generate_geocode()
        self.generate_route()
        self.notification.finish_process()