# -*- coding: utf-8 -*-
import re
import os
import json
from datetime import datetime, timedelta
from datetime import datetime as date
import helper.utils as utils
import random

from model.order import Order
from model.depot import Depot
from model.route import Route
from model.breaks import Breaks
from model.geometry_point import GeometryPoint

from esri.geodatabase import Geodatabase

from sklearn.cluster import kmeans_plusplus
import numpy as np

TRAVEL_MODE = "Driving Time" #"Walking Distance"
FT_COMPANIES_WITHOUT_ROUTE = "EmpresasNaoRoteirizadas"
FT_COMPANIES_WITH_ROUTE = "EmpresasRoteirizadas"
FT_ROUTE = "Roteiros"

class VehicleRoutingProblem():
    def __init__(self, logger, config, process_name, layer_name_process, companies, 
    path_gdb_finale, param_excel, num_total_routes, num_visits_per_route, limit_km, 
    cursorCompaniesWithRoute, cursorCompaniesWithoutRoute, cursorRoutesWithoutShape, cursorRoutes):
        self.logger = logger
        self.config = config
        self.layer_name_process = layer_name_process
        self.path_gdb_finale = path_gdb_finale
        self._arcpy = __import__("arcpy") if self.config.get_env_run() != "test" else None
        self.companies = companies
        self.geodatabase = Geodatabase(self.logger, self.config)
        self.process_name = process_name
        self.path_temp = self.config.get_folder_temp()
        self.path_gdb = os.path.join(self.path_temp, process_name+".gdb")
        self.feature_path = {}
        self.param_excel = param_excel
        self.num_total_routes = num_total_routes
        self.num_visits_per_route = num_visits_per_route
        self.limit_km = limit_km
        self.verify_depots = {}
        self.cursorCompaniesWithRoute = cursorCompaniesWithRoute
        self.cursorCompaniesWithoutRoute = cursorCompaniesWithoutRoute
        self.cursorRoutesWithoutShape = cursorRoutesWithoutShape
        self.cursorRoutes = cursorRoutes        
    
    def _get_route_name(self, route_date):
        return '%s%s#%s' % (self.companies[0]['GEO_ID'], self.companies[0]['IBGE'], route_date.strftime("%Y%m%d") if route_date != None else "")
    
    def _setup_workspace_arcpy(self):
        #self.logger.info("Configurando variáveis do ambiente arcpy...")
        if self._arcpy.env.workspace != self.path_gdb:
            self._arcpy.env.workspace = self.path_gdb

    def _get_route_day(self, index):
        route_day = (datetime.now() + timedelta(days=index)).strftime("%Y-%m-%d")
        route_day = datetime.strptime(route_day, "%Y-%m-%d").replace(hour=9, minute=0, second=0, microsecond=0)

        return route_day

    def _create_gdb_tmp(self):
        name_file = self.process_name +".gdb"
        self.geodatabase.create(self.path_temp, name_file)

    def _get_feature_path(self, layer):
        if layer not in self.feature_path:
            self.feature_path[layer] = self.geodatabase.get_path_feature(layer)
        return self.feature_path[layer]

    def exists_generated_routes(self):
        self._setup_workspace_arcpy()
        path_vrp_temp = os.path.join(self.path_temp, self.process_name+'.gdb')
        if not os.path.exists(path_vrp_temp): return False

        ft_orders = self.geodatabase.get_path_feature('Orders')
        ft_routes = self.geodatabase.get_path_feature('Routes')

        is_corrupted = (ft_routes == None or ft_orders == None)
        
        if not is_corrupted:
            if self.geodatabase.count(ft_orders) == 0 or self.geodatabase.count(ft_routes) == 0: is_corrupted = True

        if is_corrupted:
            self._arcpy.Delete_management(path_vrp_temp)
            return False

        return True

    def _create_layer_route(self):
        #self.logger.info("Criando objeto do VRP...")
        route_day = datetime.now().strftime("%Y-%m-%d")
        route_layer = self._arcpy.na.MakeVehicleRoutingProblemAnalysisLayer(
            self.config.path_network, 
            self.layer_name_process, 
            TRAVEL_MODE, 
            "Minutes", "Meters", route_day, "LOCAL_TIME_AT_LOCATIONS", "ALONG_NETWORK", "Medium", "Medium", "DIRECTIONS", "CLUSTER")
        self.vrp_layer = route_layer.getOutput(0)

    def _define_orders(self):
        #self.logger.info("Definindo e populando orders "+ str(self.companies[0]['GEO_ID']) +"...")
        orders = []

        for c in self.companies:
            orders.append(Order(str(c['NU_EC']), self._get_route_name(None), c['PRIORIDADE_AGENDADO'], c['LATITUDE_Y'], c['LONGITUDE_X']).get_values())

        fields = ['Name', 'Description', 'ServiceTime', 'Revenue', 'AssignmentRule', 'SHAPE@JSON']
        self.geodatabase.insert_data(self.path_gdb, self._get_feature_path('Orders'), fields, orders)
    
    def _verify_orders(self):
        #self.logger.info("Verificando orders com erro e removendo...")
        insert_fields = self.param_excel.copy()
        fields = ['OBJECTID', 'Status', 'Name', 'SHAPE@JSON']
        orders = self.geodatabase.search_data(self.path_gdb, self._get_feature_path('Orders'), fields)

        for column in ["ID_ROTA", "OPCOES", "SEQUENCIA", 'SHAPE@JSON']:
                if column in insert_fields:
                    insert_fields.remove(column)
        
        for column in ["DATA_GERACAO", "Motivo1", "Motivo2", "Motivo3", "Motivo4", 'SHAPE@JSON']:
            if not column in insert_fields:
                insert_fields.append(column)

        order_errors = []
        order_error_update = []
        order_where = []
        for order in orders:
            if order['Status'] != 0:
                order['AssignmentRule'] = 0
                order_error_update.append(order)
                order_where.append(str(order['OBJECTID']))
                order_errors.append(order)
                
        if len(order_errors) > 0:
            fields_error = ['Name', 'AssignmentRule']
            order_where="OBJECTID in (%s)" % ','.join(order_where)
            self.geodatabase.update_data(self.path_gdb, self._get_feature_path('Orders'), fields_error, order_where, order_error_update, "Name")
        
        if len(order_errors) > 0:
            #self.logger.info("Foram encontrados "+ str(len(order_errors)) +" erros...")
            fields.remove('OBJECTID')

            errors = []
            for order_error in order_errors:
                company = [c for c in self.companies if str(c["NU_EC"]) == order_error["Name"]][0]

                company['Motivo1'] = 'Empresa fora do network'
                company['Motivo2'] = ""
                company['Motivo3'] = ''
                company['Motivo4'] = ''
                company['DATA_GERACAO'] = utils.datetime_to_timestamp(date.now())

                for fields in insert_fields:
                    if fields != 'SHAPE@JSON':
                        company[fields] = str(company[fields])
                    if fields == 'STR_MIS_CAD':
                        company['STR_MIS_CAD'] = company['STR_MIS_CAD'][:1023]

                company['geometry'] = GeometryPoint(company['LATITUDE_Y'], company['LONGITUDE_X']).get_shape_xy()
                errors.append(company)
            
            # self.geodatabase.insert_data(self.path_gdb, FT_COMPANIES_WITHOUT_ROUTE, insert_fields, errors)

            for row in errors:
                feature_row = self.geodatabase.prepare_row(row, insert_fields)
                self.cursorCompaniesWithoutRoute.insertRow(feature_row)
    
            #self.logger.info("Verificando se alguma order com erro é um Depot..." + str(len(order_errors)))

            depots = self.geodatabase.search_data(self.path_gdb, self._get_feature_path('Depots'), ['OBJECTID', 'Name', 'SHAPE@X', 'SHAPE@Y'])

            for order_error in order_errors:
                shape = json.loads(order_error['SHAPE@JSON'])
                depot_update = [d for d in depots if d['SHAPE@X'] == shape['x'] and d['SHAPE@Y'] == shape['y']]
            
            if len(depot_update) > 0:
                #self.logger.info("Foram encontrados "+ str(len(depot_update)) +" depósito com erro...")
                order_no_error =  self.geodatabase.search_data(self.path_gdb, self._get_feature_path('Orders'), ['OBJECTID', 'Name', 'SHAPE@X', 'SHAPE@Y'], 'Status = 0')

                for index, depot_erro in enumerate(depot_update):
                    self.geodatabase.delete_rows(self.path_gdb, self._get_feature_path('Depots'), [depot_erro])
                    if len(order_no_error) > 0:
                        new_depots = [Depot(depot_erro['Name'], order_no_error[index]['SHAPE@Y'], order_no_error[index]['SHAPE@X']).get_values()]
                        self.geodatabase.insert_data(self.path_gdb, self._get_feature_path('Depots'), ['Name', 'SHAPE@JSON'], new_depots)

    def _create_cluster(self):
        lat_lng = [[c['LONGITUDE_X'], c['LATITUDE_Y']] for c in self.companies]

        X = np.array(lat_lng)
        centers_init, indices = kmeans_plusplus(X, n_clusters=self.num_total_routes, random_state=0)

        return centers_init

    def _define_depots(self):
        #self.logger.info("Definindo e populando depots...")
        fields = ['Name', 'SHAPE@JSON']
        cluster = self._create_cluster()
        depots = []
        for index, init_point in enumerate(cluster):
            lng_x = init_point[0]; lat_y = init_point[1]
            route_day = self._get_route_day((index + 1))
            route_name = str(random.random()) + "_" + self._get_route_name(route_day) + "#" + str(index + 1)

            depots.append(Depot(route_name, lat_y, lng_x).get_values())

        self.geodatabase.insert_data(self.path_gdb, self._get_feature_path('Depots'), fields, depots)

        return depots

    def _define_pre_routes(self, depots):
        #self.logger.info("Definindo os routes...")
        fields = ['Name', 'StartDepotName', 'EarliestStartTime', 'LatestStartTime', 'CostPerUnitTime', 'MaxOrderCount', 'AssignmentRule', 'MaxTotalTime', 'MaxTotalDistance']
        pre_routes = []
        for depot in depots:
            pre_routes.append(Route(depot['Name'], depot['Name'], self.num_visits_per_route, self.limit_km).get_values())
        
        self.geodatabase.insert_data(self.path_gdb, self._get_feature_path('Routes'), fields, pre_routes)

    def _generate_routes(self):
        #self.logger.info("Gerando as rotas com o VRP...")
        try:
            #output_layer_file = os.path.join(self.path_temp, self.layer_name_process + ".lyrx")
            #self._arcpy.management.SaveToLayerFile(self.layer_name_process, output_layer_file, "RELATIVE")            
            self._arcpy.na.Solve(self.layer_name_process, "HALT", "TERMINATE", None, '')
        except:
            self._verify_orders()
            self._arcpy.na.Solve(self.layer_name_process, "HALT", "TERMINATE", None, '')

    def _save_companies_with_violations(self):
        #self.logger.info("Salvando empresas com violações...")
        fields_violations = ['Name', 'ViolatedConstraint_1', 'ViolatedConstraint_2', 'ViolatedConstraint_3', 'ViolatedConstraint_4']
        orders_with_violations = self.geodatabase.search_data(self.path_gdb, self._get_feature_path('Orders'), fields_violations, "ArriveTime IS NULL")

        insert_in_fields = self.param_excel.copy()
        name_file = self.process_name +".gdb"

        for column in ["ID_ROTA", "OPCOES", "SEQUENCIA", 'SHAPE@JSON']:
            if column in insert_in_fields:
                insert_in_fields.remove(column)

        insert_in_fields.append('SHAPE@JSON')

        if len(orders_with_violations) > 0:
            companies_with_violations = []
            for order in orders_with_violations:
                company = [c for c in self.companies if str(c["NU_EC"]) == order["Name"]][0]

                for fields in insert_in_fields:
                    if fields != 'SHAPE@JSON' and fields != 'Motivo1' and fields != 'Motivo2' and fields != 'Motivo3' and fields != 'Motivo4' and fields != 'DATA_GERACAO':
                        company[fields] = str(company[fields])
                    if fields == 'STR_MIS_CAD':
                        company['STR_MIS_CAD'] = company['STR_MIS_CAD'][:1023]
            
                for num in [1,2,3,4]:
                    if order["ViolatedConstraint_" + str(num)] != None:
                        violation = self.geodatabase.get_violated_domain(order["ViolatedConstraint_" + str(num)], self.path_temp, name_file)
                        company["Motivo" + str(num)] = str(violation)
                    else:
                        company["Motivo" + str(num)] = ''
                
                company["DATA_GERACAO"] = utils.datetime_to_timestamp(date.now())
                company['geometry'] = GeometryPoint(company['LATITUDE_Y'], company['LONGITUDE_X']).get_shape_xy()

                companies_with_violations.append(company)

            #self.geodatabase.insert_data(self.path_gdb, FT_COMPANIES_WITHOUT_ROUTE, insert_in_fields, companies_with_violations) 

            for row in companies_with_violations:
                feature_row = self.geodatabase.prepare_row(row, insert_in_fields)
                self.cursorCompaniesWithoutRoute.insertRow(feature_row)
    
    def delete_companies_outside_city_limits(self):
        self._setup_workspace_arcpy()
        companies_without_route_to_delete = self.geodatabase.search_data(self.path_gdb, FT_COMPANIES_WITHOUT_ROUTE, ["OBJECTID", "Motivo1"], "Motivo1 = 'Limite de rotas por município atingido'")
        self.geodatabase.delete_rows(self.path_gdb, FT_COMPANIES_WITHOUT_ROUTE, companies_without_route_to_delete)        
    
    def save_companies_outside_city_limits(self, not_routerize):
        self._setup_workspace_arcpy()
        companies_not_roterize = []

        insert_in_fields = self.param_excel.copy()

        for column in ["ID_ROTA", "OPCOES", "SEQUENCIA", 'SHAPE@JSON']:
            if column in insert_in_fields:
                insert_in_fields.remove(column)

        insert_in_fields.append('SHAPE@JSON')        

        for company in not_routerize:
            for fields in insert_in_fields:
                if fields != 'SHAPE@JSON' and fields != 'Motivo1' and fields != 'Motivo2' and fields != 'Motivo3' and fields != 'Motivo4' and fields != 'DATA_GERACAO':
                    company[fields] = str(company[fields])
                if fields == 'STR_MIS_CAD':
                    company['STR_MIS_CAD'] = company['STR_MIS_CAD'][:1023]

            for num in [1,2,3,4]:
                if num == 1:
                    company["Motivo" + str(num)] = 'Limite de rotas por município atingido'
                else:
                    company["Motivo" + str(num)] = ''
        
            company["DATA_GERACAO"] = utils.datetime_to_timestamp(date.now())
            company['geometry'] = GeometryPoint(company['LATITUDE_Y'], company['LONGITUDE_X']).get_shape_xy()

            companies_not_roterize.append(company)

        #self.geodatabase.insert_data(self.path_gdb, FT_COMPANIES_WITHOUT_ROUTE, insert_in_fields, companies_not_roterize)
        for row in companies_not_roterize:
            feature_row = self.geodatabase.prepare_row(row, insert_in_fields)
            self.cursorCompaniesWithoutRoute.insertRow(feature_row)


    def _save_route_orders(self):
        #self.logger.info("_save_route_orders*****************************")
        fields_orders = ["OBJECTID", "Name", "Sequence", "RouteName", "ArriveTime"]
        list_orders = self.geodatabase.search_data(self.path_gdb, self._get_feature_path('Orders'), fields_orders, "Sequence IS NOT NULL", "ORDER BY Sequence ASC")
        
        insert_in_fields = self.param_excel.copy()

        for column in ["DATA_GERACAO", "Motivo1", "Motivo2", "Motivo3", "Motivo4", 'SHAPE@JSON']:
            if column in insert_in_fields:
                insert_in_fields.remove(column)
        
        for column in ["ID_ROTA", "OPCOES", "SEQUENCIA", 'SHAPE@JSON']:
            if not column in insert_in_fields:
                insert_in_fields.append(column)

        route_companies = []
        for order in list_orders:
            company = [c for c in self.companies if str(c["NU_EC"]) == order["Name"]][0]
            
            company['ID_ROTA'] = order['RouteName']
            company['OPCOES'] = order['RouteName'].split('#')[2]
            company['SEQUENCIA'] = (int(order['Sequence']) - 1)
            
            for fields in insert_in_fields:
                if fields != 'SHAPE@JSON':
                    company[fields] = str(company[fields])
                if fields == 'STR_MIS_CAD':
                    company['STR_MIS_CAD'] = company['STR_MIS_CAD'][:1023] 

            company['geometry'] = GeometryPoint(company['LATITUDE_Y'], company['LONGITUDE_X']).get_shape_xy()
            route_companies.append(company)

        #self.geodatabase.insert_data(self.path_gdb, FT_COMPANIES_WITH_ROUTE, insert_in_fields, route_companies)
        for row in route_companies:
            feature_row = self.geodatabase.prepare_row(row, insert_in_fields)
            self.cursorCompaniesWithRoute.insertRow(feature_row)

    def _save_routes(self):
        #self.logger.info("_save_routes*****************************")  
        fields_routes = ['Name', 'MaxOrderCount', 'TotalCost', 'TotalTime', 'TotalOrderServiceTime', 'TotalTravelTime', 'TotalDistance', 'OrderCount', 'MaxTotalDistance', 'SHAPE@JSON']
        
        fields_routes_without_shape = fields_routes.copy()
        fields_routes_without_shape.remove('SHAPE@JSON')

        routes = self.geodatabase.search_data(self.path_gdb, self._get_feature_path('Routes'), fields_routes)
        for route in routes:
            if route['SHAPE@JSON'] == None:
                del route['SHAPE@JSON']
                feature_row = self.geodatabase.prepare_row(route, fields_routes_without_shape)
                self.cursorRoutesWithoutShape.insertRow(tuple(feature_row))
            else:
                feature_row = self.geodatabase.prepare_row(route, fields_routes)
                self.cursorRoutes.insertRow(tuple(feature_row))            

    def _verify_route(self):
        #self.logger.info("_verify_route*****************************")          
        first_orders = self.geodatabase.search_data(self.path_gdb, self._get_feature_path('Orders'), ['OBJECTID', 'Name', 'Sequence', 'AssignmentRule', 'SHAPE@X', 'SHAPE@Y'], "Sequence=2")
        depots = self.geodatabase.search_data(self.path_gdb, self._get_feature_path('Depots'), ['OBJECTID', 'Name', 'SHAPE@X', 'SHAPE@Y'])
        new_depots = []
        routes_names = [d['Name'] for d in depots]
        is_any_order_not_depot = False
        
        order_update = []
        order_where = []

        for order in first_orders:
            depot_filtered = [d for d in depots if d['SHAPE@Y'] == order['SHAPE@Y'] and d['SHAPE@X'] == order['SHAPE@X']]
            if len(depot_filtered) == 0:
                is_any_order_not_depot = True
                new_depots.append(Depot(routes_names.pop(), order['SHAPE@Y'], order['SHAPE@X']).get_values())
            else:
                new_depots.append(Depot(routes_names.pop(), depot_filtered[0]['SHAPE@Y'], depot_filtered[0]['SHAPE@X']).get_values())
            
            order_where.append(str(order['OBJECTID']))
            ANCHOR_FIRST = 4
            order['AssignmentRule'] = ANCHOR_FIRST
            order_update.append(order)
            
        if len(order_update) > 0:
            fields_order_update = ['OBJECTID', 'Name', 'AssignmentRule']
            order_where="OBJECTID in (%s)" % ','.join(order_where)
            self.geodatabase.update_data(self.path_gdb, self._get_feature_path('Orders'), fields_order_update, order_where, order_update, "OBJECTID")

        if is_any_order_not_depot:
            self.geodatabase.delete_rows(self.path_gdb, self._get_feature_path('Depots'), depots)
            self.geodatabase.insert_data(self.path_gdb, self._get_feature_path('Depots'), ['Name', 'SHAPE@JSON'], new_depots)
            self._generate_routes()    

    def _create_feature_output(self):
        self.geodatabase.copy_feature(os.path.join(self.path_gdb_finale, FT_COMPANIES_WITH_ROUTE), self.path_gdb, FT_COMPANIES_WITH_ROUTE)
        self.geodatabase.copy_feature(os.path.join(self.path_gdb_finale, FT_COMPANIES_WITHOUT_ROUTE), self.path_gdb, FT_COMPANIES_WITHOUT_ROUTE)
        self.geodatabase.copy_feature(os.path.join(self.path_gdb_finale, FT_ROUTE), self.path_gdb, FT_ROUTE, "POLYLINE")
    
    def save_output(self):
        self._setup_workspace_arcpy()
        self._save_companies_with_violations()
        self._save_route_orders()
        self._save_routes()        
    
    def execute(self):
        try:
            self._setup_workspace_arcpy()

            self._create_gdb_tmp()

            #self._create_feature_output()
            
            self._create_layer_route()

            self._define_orders()

            depots = self._define_depots()

            self._define_pre_routes(depots)
        
            self._generate_routes()

            self._verify_route()

            self.save_output()

        except Exception as e:
            import traceback, sys
            traceback_text = "".join([x for x in traceback.format_exception(*sys.exc_info()) if x])
            self.logger.error(traceback_text)
            raise e            