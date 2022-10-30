# -*- coding: utf-8 -*-
import helper.utils as utils
from config import Config
from service.work_areas import WorkAreas
from esri.geodatabase import Geodatabase
from service.base_route import BaseRoute
from sklearn.cluster import kmeans_plusplus
import numpy as np
import math
import json

LIMIT_ROUTES_PER_DAY = 30

class VRPDepots():
    def __init__(self, logger):    
        self.logger = logger
        self._arcpy = __import__("arcpy") if Config().get_env() != "test" else None
        self.geodatabase = Geodatabase(logger)
        self.base_route = BaseRoute(logger)
        self.params = Config().get_params()
        self.work_areas = WorkAreas(logger, self.params)
        self.days = []
        self.years = []
    
    def change_position(self, id_depots, x, y):
        fields = ["Name", "SHAPE@JSON"]
        feature = self.geodatabase.get_path_feature('Depots')
        depots  = self.geodatabase.search_data(feature, fields, "Name='%s'" % (id_depots))
        
        list_depot = []
        for depot in depots:
            shape = json.loads(depot["SHAPE@JSON"])
            shape["x"] = x; shape["y"] = y
            depot["SHAPE@JSON"] = json.dumps(shape)
            list_depot.append(depot)
        
        self.geodatabase.update_data(feature, fields, "1=1", list_depot, "Name")

    def _get_work_areas_ids(self, polo_travelmode):
        return [str(area['attributes']['id']) for area in self.work_areas.get() if area['attributes']['id'] == polo_travelmode['id'] and area['attributes']['modoviagem'] == polo_travelmode['modoviagem']]

    def _remove_schedule_outside_route_period(self, schedules_per_day):
        schedules_per_day_verified = {}
        for key in schedules_per_day:
            schedule_date = utils.format_date_dmY(schedules_per_day[key]['TimeWindowStart'])
            schedule_exist_in_route_days = len([day for day in self.days if utils.format_date_dmY(day) == schedule_date]) > 0
            if schedule_exist_in_route_days:
                schedules_per_day_verified[key] = schedules_per_day[key]

        return schedules_per_day_verified
    
    def _group_by_schedules_per_day(self, companies, clusters):
        schedules_per_day = {}        
        for company in companies:
            if company['TimeWindowStart'] != None:
                date_formated = utils.format_date_dmY(company['TimeWindowStart'])
                if date_formated not in schedules_per_day or (date_formated in schedules_per_day and utils.datetime_to_timestamp(schedules_per_day[date_formated]['TimeWindowStart']) > utils.datetime_to_timestamp(company['TimeWindowStart'])):
                        schedules_per_day[date_formated] = company    

        if len(schedules_per_day) > 0:
            for schedule in schedules_per_day:
                company = schedules_per_day[schedule]
                for center in clusters:
                    company_point = [company['SHAPE@X'], company['SHAPE@Y']]
                    center_point = [center[0], center[1]]
                    distance = utils.calc_distance_2_points(company_point, center_point)
                    if ('cluster_closer' in company and company['cluster_closer_distance'] > distance) or 'cluster_closer' not in company:
                        company['cluster_closer'] = center_point
                        company['cluster_closer_distance'] = distance
                        schedules_per_day[schedule] = company
                        
                company = schedules_per_day[schedule]                        

        schedules_per_day = self._remove_schedule_outside_route_period(schedules_per_day)

        return schedules_per_day

    def _create_cluster(self, companies):
        lat_lng = [[c['SHAPE@X'], c['SHAPE@Y']] for c in companies]
        number_cluster = math.ceil(len(lat_lng)/LIMIT_ROUTES_PER_DAY)
        number_cluster = number_cluster if number_cluster > 0 else 1

        X = np.array(lat_lng)
        centers_init, indices = kmeans_plusplus(X, n_clusters=number_cluster, random_state=0) # Calculate seeds from kmeans++

        return centers_init

    def identify_days_and_years_route_period(self, clusters, route_day_start):
        route_day = route_day_start if route_day_start != None else self.base_route.get_route_day()
        self.days = []
        for center in clusters:
            route_day = route_day if len(self.days) == 0 else self.base_route.get_route_day(route_day)
            self.days.append(route_day)
            year = route_day.strftime("%Y")                
            if year not in self.years:
                self.years.append(year)        

    def _remove_item_cluster(self, clusters, center):
        return [c for c in clusters if c[0] != center[0] and c[1] != center[1]]

    def create(self, polo_travelmode, route_day_start=None):
        self.logger.info("Criando os pontos de partidas dos executivos no objeto Depots do VRP...")

        feature_companies = self.geodatabase.get_path_feature('Orders')
        feature_depots = self.geodatabase.get_path_feature('Depots')
    
        work_areas_ids = self._get_work_areas_ids(polo_travelmode)
        for name in work_areas_ids:
            companies = self.geodatabase.search_data(feature_companies, ['Name', 'TimeWindowStart', 'Description', 'SHAPE@X', 'SHAPE@Y'], "Description='%s'" % (name))
            if len(companies) == 0:                
                self.logger.info('Nenhuma empresa encontrada nessa carteira (%s) e carteiraid(travelmode) (%s(%s))' % (name, polo_travelmode['id'], polo_travelmode['modoviagem']))
                continue
            
            clusters = self._create_cluster(companies)
            self.identify_days_and_years_route_period(clusters, route_day_start)

            schedules_per_day = self._group_by_schedules_per_day(companies, clusters)
            
            depots = []
            for route_day in self.days:
                center = clusters[0]
                route_day_key = utils.format_date_dmY(route_day)
                if route_day_key in schedules_per_day:
                    center = schedules_per_day[route_day_key]['cluster_closer']

                depots.append({
                    'attributes': {
                        'Name': '%s#%s' % (name, route_day.strftime("%Y%m%d"))
                    },
                    'geometry': {
                        'x': center[0],
                        'y': center[1]
                    }
                })

                clusters = self._remove_item_cluster(clusters, center)

            self.geodatabase.delete_data(feature_depots, "1=1")
            self.geodatabase.insert_data(depots, feature_depots, ['Name', 'SHAPE@XY'])
    
        self.years.sort()
        return self.years        