# -*- coding: utf-8 -*-
import os
from config import Config
import helper.utils as utils
from esri import feature_server
from service.base_route import BaseRoute
from esri.geodatabase import Geodatabase
from datetime import datetime as date

LIMIT_ROUTE_DAY = 30
class Route():
    def __init__(self, logger):    
        self.logger = logger
        self.params = Config().get_params()
        self._arcpy = __import__("arcpy") if Config().get_env() != "test" else None
        self.geodatabase = Geodatabase(logger)
        self.base_route = BaseRoute(logger)
        self.work_areas = []
        self.travel_modes = None
        self.solver_properties = None
        self.route_layer = None

    def _get_work_areas(self):
        if len(self.work_areas) == 0:
            self.work_areas = self.base_route.get_work_areas()
        return self.work_areas

    def _clear_objects_route(self):
        self.geodatabase.clear_objects(['Stops'])

    def _make_layer_route(self):
        layer_name = "WorkRoute"
        travel_mode = "Walking Distance"

        self.logger.info("Criando objeto de análise de rota...")
        layer_object = self._arcpy.na.MakeRouteAnalysisLayer(self.params['path_network_layer'], layer_name, travel_mode, "FIND_BEST_ORDER", time_of_day=self.base_route.start_route_day())
        
        self.route_layer = layer_object.getOutput(0)

        desc = self._arcpy.Describe(self.route_layer)
        self.travel_modes = self._arcpy.na.GetTravelModes(desc.network.catalogPath)
        self.solver_properties = self._arcpy.na.GetSolverProperties(self.route_layer)

    def _get_work_areas_ids(self, polo_travelmode):
        return [str(area['attributes']['id']) for area in self._get_work_areas() if self.base_route.filter_area_by_polo_travelmode(area, polo_travelmode)]
    
    def _get_companies(self, polo_travelmode):
        work_areas_ids = [str(polo_travelmode['id'])]
        self.logger.info("Recuperando dados de empresas...")
        ft_companies = os.path.join(self.geodatabase.get_path(), "Empresas")
        where_companies = "carteiraId IN (%s)" % (",".join(work_areas_ids))
        companies = self.geodatabase.search_data(ft_companies, ['id', 'empresa', 'carteiraId', 'executivoId', 'endereco', 'numero', 'cidade', 'estado', 'bairro', 'cep', 'cnpjcpf', 'idpagseguro'], where_companies)        
        return companies
    
    def _get_executives(self, companies):
        self.logger.info("Recuperando dados de executivos...")
        where_executive = "id IN (%s)" % (",".join(self.base_route.get_executives_ids(companies)))
        executives = feature_server.get_feature_data(self.params['executive_feature_url'], where_executive)        
        return executives

    def _load_companies_to_stops(self):
        self.logger.info("Adicionando empresas na feature Stops...")
        ft_companies_filtered = self.base_route.get_name_feature_filtered("Empresas")
        self._arcpy.na.AddLocations(self.route_layer, "Stops", ft_companies_filtered, "Name id #;RouteName executivoId #;Attr_WalkTime Attr_Time #;TimeWindowStart TimeWindowStart #", "", exclude_restricted_elements="EXCLUDE")

    def _solve_route(self, polo_travelmode):
        self.logger.info("Gerando roteiros...")
        mode = self.travel_modes['Driving Distance'] if polo_travelmode['modoviagem'] == 'Driving' else self.travel_modes['Walking Distance']
        self.solver_properties.applyTravelMode(mode)
        self._arcpy.na.Solve(self.route_layer, "SKIP", "TERMINATE", None, '')

    def _get_stops(self):
        self.logger.info("Recuperando os stops gerados pela rota...")
        feature_path_stops = self.geodatabase.get_path_feature('Stops')        
        stops = self.geodatabase.search_data(feature_path_stops, ['Name', 'RouteName', 'Sequence', 'TimeWindowStart', 'SHAPE@X', 'SHAPE@Y'])
        return stops

    def _construct_payload(self, companies):
        payload = []
        executives = self._get_executives(companies)
        stops = self._get_stops()

        executivo_ids = utils.get_unique_values_from_items('RouteName', stops)

        now = date.now()
        for executivo_id in executivo_ids: #agrupamento das rotas por executivo e separação de 30 em 30
            routes_by_executivo = [item for item in stops if item['RouteName'] == executivo_id]
            routes_by_executivo.sort(key=lambda x: x.get('Sequence'))
            
            sequence = 0
            route_day = self.base_route.get_route_day(now)
            for route in routes_by_executivo:
                sequence += 1

                company = [item for item in companies if str(item['id']) == str(route['Name'])][0]
                work_area = [item['attributes'] for item in self._get_work_areas() if str(item['attributes']['id']) == str(company['carteiraId'])][0]
                executive = [item['attributes'] for item in executives if str(item['attributes']['id']) == str(company['executivoId'])][0]            
                
                creation_date = now
                date_scheduled = None

                route_prepared = self.base_route.construct_payload(
                    company, executive, 
                    sequence, route_day, creation_date, date_scheduled, 
                    work_area,
                    route['SHAPE@X'], route['SHAPE@Y'])

                payload.append(route_prepared)

                if sequence == LIMIT_ROUTE_DAY:
                    sequence = 0
                    route_day = self.base_route.get_route_day(route_day)

        return payload  

    def run(self):

        self._make_layer_route()

        polo_travelmode_of_work_areas = self.base_route.get_carteira_and_travelmode_of_work_areas()
        
        count = 0
        for polo_travelmode in polo_travelmode_of_work_areas:
            count += 1
            self.logger.info('Gerando roteiros para o idcarteira(modoviagem) (%s(%s)) (%s/%s)' % (polo_travelmode['id'], polo_travelmode['modoviagem'], count, len(polo_travelmode_of_work_areas)))
                
            companies = self._get_companies(polo_travelmode)

            if len(companies) == 0:
                self.logger.info('Nenhuma empresa encontrada para o idcarteira(modoviagem) (%s(%s))' % (polo_travelmode['id'], polo_travelmode['modoviagem']))
                continue

            self.base_route.filter_company_by_id(polo_travelmode)

            self._load_companies_to_stops()

            self._solve_route(polo_travelmode)

            routes = self._construct_payload(companies)

            executives_ids = self.base_route.get_executives_ids(companies)
            self.base_route.publish_new_routes(executives_ids, routes)

            self._clear_objects_route()

        
        self.logger.info("Módulo de Route finalizado...")