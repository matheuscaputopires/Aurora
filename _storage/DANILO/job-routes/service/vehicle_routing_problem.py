# -*- coding: utf-8 -*-
import json
import os
from config import Config
import helper.utils as utils
from esri import feature_server
from service.base_route import BaseRoute
from esri.geodatabase import Geodatabase
from service.schedule import Schedule
from service.vrp_depots import VRPDepots
from datetime import datetime as date
import datetime

LAYER_NAME_ROUTE = "WorkVehicleRoutingProblem"
TRAVEL_MODE = "Walking Time" #"Walking Distance"

class VehicleRoutingProblem():
    def __init__(self, logger):    
        self.logger = logger
        self.params = Config().get_params()
        self.route_generation_date = Config().route_generation_date
        self._arcpy = __import__("arcpy") if Config().get_env() != "test" else None
        self.geodatabase = Geodatabase(logger)
        self.base_route = BaseRoute(logger)
        self.schedule = Schedule(logger)
        self.depots = VRPDepots(logger)
        self.work_areas = []
        self.solver_properties = None
        self.travel_modes = None
        self.vrp_layer = None
        self.user_hierarchies = None
        self.feature_path = {}        
    
    def _get_feature_path(self, layer):
        if layer not in self.feature_path:
            self.feature_path[layer] = self.geodatabase.get_path_feature(layer)
        return self.feature_path[layer]
    
    def _get_work_areas(self):
        if len(self.work_areas) == 0:
            self.work_areas = self.base_route.get_work_areas()
        return self.work_areas

    def _create_route_zones(self):
        self.logger.info("Criando polígonos de carteira no objeto RouteZones do VRP...")
        route_zones = []

        feature_depots = self.geodatabase.get_path_feature('Depots')
        start_points = self.geodatabase.search_data(feature_depots, ['Name'])
        for point in start_points:
            id_work_area = str(point['Name'].split('#')[0])
            work_area_filtered = [area for area in self._get_work_areas() if str(area['attributes']['id']) == id_work_area][0]

            zone = {
                'attributes': {
                    'RouteName': point['Name']
                },
                'geometry': work_area_filtered['geometry']
            }
            route_zones.append(zone)

        feature_route_zones = self.geodatabase.get_path_feature('RouteZones')
        self.geodatabase.insert_data(route_zones, feature_route_zones, ['RouteName', 'SHAPE@JSON'])

    def _get_year_route_name(self, name):
        name_array = name.split('#')
        return name_array[1][:4]
    
    def _get_date_from_route_name(self, name):
        name_array = name.split('#')
        year = int(name_array[1][:4])
        month = int(name_array[1][4:-2])
        day = int(name_array[1][6:])
        return date(year, month, day)

    def _create_pre_routes(self, work_area, year):
        self.logger.info("Criando a registros de rotas a serem geradas no objeto Routes do VRP...")
        # feature_route_zones = self.geodatabase.get_path_feature('RouteZones')
        # route_zones = self.geodatabase.search_data(feature_route_zones, ['RouteName'])

        feature_route_zones = self.geodatabase.get_path_feature('Depots')
        route_zones = self.geodatabase.search_data(feature_route_zones, ['Name'])

        ft_companies = self.base_route.get_name_feature_filtered("Empresas")
        companies_with_alerts = self.geodatabase.search_data(ft_companies, ["Id"], where="DeliveryQuantity_2 IS NOT NULL")
        
        diff_alerts = (5 - len(companies_with_alerts)) if len(companies_with_alerts) < 5 else 0

        companies_with_schedule = self.geodatabase.search_data(ft_companies, ["Id"], where="TimeWindowStart IS NOT NULL")
        work_area_without_schedule = len(companies_with_schedule) == 0

        self.geodatabase.delete_data(self._get_feature_path('Routes'), "1=1")

        pre_routes = []
        for zone in route_zones:
            date_route = self._get_date_from_route_name(zone['Name'])
            if year != self._get_year_route_name(zone['Name']):
                continue
            fields = ['Name', 'StartDepotName', 'EarliestStartTime', 'LatestStartTime', 'CostPerUnitTime', 'MaxOrderCount', 'AssignmentRule']
            attributes = {
                    'Name': zone['Name'],
                    'StartDepotName': zone['Name'],
                    'EarliestStartTime': date_route.replace(hour=9, minute=0, second=0),
                    'LatestStartTime': date_route.replace(hour=18, minute=0, second=0),
                    'CostPerUnitTime': 1,
                    'MaxOrderCount': 30,
                    'AssignmentRule': 2
                }                

            if len(companies_with_alerts) > 0:
                attributes['Capacity_1'] = 25 + diff_alerts
                attributes['Capacity_2'] = 5 - diff_alerts
                fields.append('Capacity_1')
                fields.append('Capacity_2')
            else:
                attributes['Capacity_1'] = 30
                fields.append('Capacity_1')
            
            if work_area['distanciatotalroteiro'] != None and work_area_without_schedule:
                attributes['MaxTotalDistance'] = work_area['distanciatotalroteiro']*1000
                fields.append('MaxTotalDistance')

            pre_routes.append({
                'attributes': attributes
            })

                #'MaxTotalDistance': 5000,
                #'CostPerUnitDistance': 2
            
        self.geodatabase.insert_data(pre_routes, self._get_feature_path('Routes'), fields)

    def _make_layer_route(self):
        self.logger.info("Criando objeto de VRP...")
        route_layer = self._arcpy.na.MakeVehicleRoutingProblemAnalysisLayer(
            self.params['path_network_layer'], 
            LAYER_NAME_ROUTE, 
            TRAVEL_MODE, 
            "Minutes", "Meters", self.base_route.start_route_day(), "LOCAL_TIME_AT_LOCATIONS", "ALONG_NETWORK", "Medium", "Medium", "DIRECTIONS", "CLUSTER")
        self.vrp_layer = route_layer.getOutput(0)
        #desc = self._arcpy.Describe(self.vrp_layer)
        #self.travel_modes = self._arcpy.na.GetTravelModes(desc.network.catalogPath)
        self.travel_modes = self._arcpy.na.GetTravelModes(self.params['path_network_layer'])
        self.solver_properties = self._arcpy.na.GetSolverProperties(self.vrp_layer)

    def _load_companies_to_orders(self):
        self.logger.info("Carregando as empresas para o objeto de Ordes do VRP...")
        ft_companies = self.base_route.get_name_feature_filtered("Empresas")
        self._arcpy.na.AddLocations(
            LAYER_NAME_ROUTE, 
            "Orders", 
            ft_companies, 
            "Name id #;Description carteiraId #;ServiceTime Attr_Time #;TimeWindowStart TimeWindowStart #;TimeWindowEnd TimeWindowEnd #;MaxViolationTime MaxViolationTime #;TimeWindowStart2 # #;TimeWindowEnd2 # #;MaxViolationTime2 # #;InboundArriveTime # #;OutboundDepartTime # #;DeliveryQuantity_1 DeliveryQuantity_1 #;DeliveryQuantity_2 DeliveryQuantity_2 #;DeliveryQuantity_3 # #;DeliveryQuantity_4 # #;DeliveryQuantity_5 # #;DeliveryQuantity_6 # #;DeliveryQuantity_7 # #;DeliveryQuantity_8 # #;DeliveryQuantity_9 # #;PickupQuantity_1 # #;PickupQuantity_2 # #;PickupQuantity_3 # #;PickupQuantity_4 # #;PickupQuantity_5 # #;PickupQuantity_6 # #;PickupQuantity_7 # #;PickupQuantity_8 # #;PickupQuantity_9 # #;Revenue # #;AssignmentRule # 3;RouteName # #;Sequence # #;CurbApproach # 0", 
            "5000 Meters", None, "Routing_Streets SHAPE;Routing_Streets_Override NONE;Routing_ND_Junctions NONE", "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "EXCLUDE", None)

    def _solve_route(self):
        self.logger.info("Gerando as rotas com o VRP...")
        output_layer_file = os.path.join(Config().get_folder_temp(), LAYER_NAME_ROUTE + ".lyrx")
        self._arcpy.management.SaveToLayerFile(LAYER_NAME_ROUTE, output_layer_file, "RELATIVE")
        self._arcpy.na.Solve(LAYER_NAME_ROUTE, "HALT", "TERMINATE", None, '')

    def _create_feature_in_memory(self, feature_name, feature_template_name, feature_type="POINT"):
        self.logger.info("Criando feature em memória(%s)..." % (feature_name))
        feature_template = self.geodatabase.get_path_feature(feature_template_name)
        spatial_ref = self._arcpy.Describe(feature_template).spatialReference
        self._arcpy.CreateFeatureclass_management("in_memory", feature_name, feature_type, feature_template, "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", spatial_ref)
    
    def _append_orders_all(self):
        self.logger.info("Adicionando roteiros parciais no objeto Orders_All...")
        feature_orders_all = os.path.join("in_memory", 'Orders_All')
        feature_orders = self.geodatabase.get_path_feature("Orders")
        self._arcpy.Append_management(feature_orders, feature_orders_all, "NO_TEST")

    def _clear_objects_vrp(self):
        features = ['Routes', 'RouteZones', 'Depots', 'Orders']
        self.geodatabase.clear_objects(features)

    def _register_companies_with_violations(self, work_area):
        feature_orders_all = os.path.join("in_memory", 'Orders_All')
        orders_with_violations = self.geodatabase.search_data(feature_orders_all, ['Name', 'ViolatedConstraint_1', 'ViolatedConstraint_2', 'ViolatedConstraint_3', 'ViolatedConstraint_4'], "ArriveTime IS NULL")

        if len(orders_with_violations) > 0:

            orders_ids = [order['Name'] for order in orders_with_violations]
            where="id in (%s)" % ','.join(orders_ids)
            companies = feature_server.get_feature_data(self.params['leads_feature_url'], where)

            payload_companies_with_violations = []
            for order in orders_with_violations:
                company = [c for c in companies if str(c["attributes"]["id"]) == order["Name"]][0]

                for prop in ["objectid", "globalid"]:
                    del company["attributes"][prop]

                for num in [1,2,3,4]:
                    if order["ViolatedConstraint_" + str(num)] != None:
                        company["attributes"]["violacaoregra" + str(num)] = self.geodatabase.get_violated_domain(order["ViolatedConstraint_" + str(num)])

                company["attributes"]["datageracaorota"] = utils.datetime_to_timestamp(self.route_generation_date)
                company['geometry']['z'] = 0
                company['geometry']['spatialReference'] = {'wkid':102100, 'latestWkid': 3857}

                payload_companies_with_violations.append(company)

            query_filter = "carteiraid = %s" % work_area["id"]
            feature_server.delete_feature_data(self.params['non_route_companies_feature_url'], query_filter)

            results = feature_server.post_feature_data(self.params['non_route_companies_feature_url'], payload_companies_with_violations)
            transactions_fail = [item for item in results if item['success'] != True]
            if len(transactions_fail) > 0:
                self.logger.error('Falha ao inserir empresas que não foram roteirizadas para a carteira_id %s' % (work_area["id"]))

            self.logger.info("O total de %s empresas não foram roteirizadas..." % (len(payload_companies_with_violations)))

    def _get_payload_routes(self):
        ft_companies = os.path.join(self.geodatabase.get_path(), "Empresas")
        companies = self.geodatabase.search_data(ft_companies, ['id', 'empresa', 'carteiraId', 'executivoId', 'endereco', 'numero', 'cidade', 'estado', 'bairro', 'cep', 'cnpjcpf', 'idpagseguro', 'tipoalerta'])

        executives = feature_server.get_feature_data(self.params['executive_feature_url'])

        feature_orders_all = os.path.join("in_memory", 'Orders_All')
        orders_all = self.geodatabase.search_data(feature_orders_all, ['Name', 'Description', 'Sequence','RouteName', 'TimeWindowStart' ,'ArriveTime', 'SHAPE@X', 'SHAPE@Y', 'ViolatedConstraint_2'])

        order_routes = self._reordering_routes()

        payload = []
        for route in orders_all:
            company = [item for item in companies if str(item['id']) == str(route['Name'])][0]
            if route['ArriveTime'] == None:                
                continue
            work_area = [item['attributes'] for item in self._get_work_areas() if str(item['attributes']['id']) == str(company['carteiraId'])][0]
            executive = [item['attributes'] for item in executives if str(item['attributes']['id']) == str(company['executivoId'])][0]            
            
            sequence = route['Sequence']-1
            
            if route['RouteName'] in order_routes:
                visit_date = date.strptime(order_routes[route['RouteName']].strftime('%d/%m/%Y') + " " + route['ArriveTime'].strftime('%H:%M:%S'), '%d/%m/%Y %H:%M:%S')
            else:
                visit_date = route['ArriveTime']

            date_scheduled = route['TimeWindowStart']
            scheduled = self.schedule.get_schedule_dict(company['id'], date_scheduled)
            id_scheduled = scheduled['id'] if scheduled != None else None

            item_route = self.base_route.construct_payload(
                company, executive, 
                sequence, visit_date, self.route_generation_date, date_scheduled, id_scheduled,
                work_area,
                route['SHAPE@X'], route['SHAPE@Y'])

            payload.append(item_route)

        return payload

    def _reordering_routes(self):

        self.logger.info('Reordenação das rotas conforme quantidade de visitas...')

        feature_orders_all = os.path.join("in_memory", 'Orders_All')
        orders_with_schedule = self.geodatabase.search_data(feature_orders_all, ['RouteName'], "RouteName IS NOT NULL AND TimeWindowStart IS NOT NULL", distinct="RouteName")
        where_routes = "StartTime IS NOT NULL"
        if len(orders_with_schedule) > 0:
            for order in orders_with_schedule:
                where_routes += " AND Name <> '%s'" % (order['RouteName'])

        feature_routes = self.geodatabase.get_path_feature("Routes")
        fields_routes = ['Name', 'StartTime']
        routes_orderby_date_desc = self.geodatabase.search_data(feature_routes, fields_routes, where_routes, order_by="ORDER BY StartTime DESC")
        routes_orderby_count_asc = self.geodatabase.search_data(feature_routes, fields_routes, where_routes, order_by="ORDER BY OrderCount ASC")

        order_routes = {}
        for route, route_count in zip(routes_orderby_date_desc, routes_orderby_count_asc):
            order_routes[route_count['Name']] = route['StartTime']

        return order_routes
            
    def _clear_orders_already_routed(self):
        self.geodatabase.delete_data(self._get_feature_path('Orders'), "Sequence IS NOT NULL")
        self.geodatabase.delete_data(os.path.join("in_memory", 'Orders_All'), "Sequence IS NULL")
    
    def _regeneration_depots(self, polo_travelmode):
        routes_last_date = self.geodatabase.search_data(self._get_feature_path('Routes'), ["EarliestStartTime"], order_by="ORDER BY EarliestStartTime DESC")
        for route in routes_last_date:
            last_date = route['EarliestStartTime']
            break
        route_day_start = self.base_route.get_route_day(last_date)
        self.depots.create(polo_travelmode, route_day_start=route_day_start)
    
    def _separate_orders_without_schedule(self):
        self._create_feature_in_memory("Orders_Temp", "Orders")
        feature_orders_temp = os.path.join("in_memory", 'Orders_Temp')
        self._arcpy.Append_management("Orders", feature_orders_temp, "NO_TEST", None, None, "TimeWindowStart IS NULL AND TimeWindowEnd IS NULL")
        self.geodatabase.delete_data("Orders", "TimeWindowStart IS NULL AND TimeWindowEnd IS NULL")
    
    def _change_rule_preserve_route_to_schedules(self):
        fields = ["Name", "AssignmentRule"]
        where_orders = "TimeWindowStart IS NOT NULL"
        orders = self.geodatabase.search_data("Orders", fields, where_orders)
        list_update_order = []
        for order in orders:
            order["AssignmentRule"] = 2 # Preserve route
            list_update_order.append(order)            
        self.geodatabase.update_data("Orders", fields, where_orders, list_update_order, "Name")            
    
    def _exist_visits_scheduled_out_of_hours(self):
        fields = ["Name", "ArriveTime", "TimeWindowStart", "RouteName", "SHAPE@JSON"]
        orders = self.geodatabase.search_data("Orders", fields, "1=1", order_by="ORDER BY TimeWindowStart DESC")
        exists = False
        for order in orders:
            time_start = order['TimeWindowStart'].replace(microsecond=0)
            time_arrive = order['ArriveTime'].replace(microsecond=0) 
            max_arrive_time = time_start + datetime.timedelta(minutes=10)
            if time_arrive >= max_arrive_time:
                self.logger.info("Alterando a rota: (%s) para o ponto de partida (depot)" % (order['RouteName']))
                shape = json.loads(order["SHAPE@JSON"])
                self.depots.change_position(order["RouteName"], shape["x"], shape["y"])
                exists = True
            
        return exists
    
    def _generate_routes(self, polo_travelmode, years):        
        for year in years:
            self._create_pre_routes(polo_travelmode, year)            
            try:
                #Gerar rotas somente para os agendamentos
                    # Orders >> criar um Orders_Temp na memoria com as empresas sem agendamento
                    # - gerar a rota só com empresas que tem agendamento (solve_route())
                orders_with_schedule = self.geodatabase.search_data("Orders", ["Name"], where="TimeWindowStart IS NOT NULL")
                if len(orders_with_schedule) > 0:
                    self._separate_orders_without_schedule()
                    self._solve_route()
                    #Se algum agendamento não foi roteirizado (tempo máximo 10 min de tolerância), alterar a posição do ponto de partida para o agendamento mais cedo no dia?
                        # - Precisa alterar a posição do Depots (VRPDepots > change_position(id_depots, x, y))
                        # - gerar rota solve_route()
                    #Senao:
                        # - Alteração de flag na feature Orders para "Preservar a rota e sequência" para os agendamentos
                    if self._exist_visits_scheduled_out_of_hours():
                        self._solve_route()
                    
                    self._change_rule_preserve_route_to_schedules()
                    
                        # - Voltar as empresas sem rota que estão no Orders_Temp para Orders
                    feature_orders_temp = os.path.join("in_memory", 'Orders_Temp')
                    self._arcpy.Append_management(feature_orders_temp, "Orders", "NO_TEST", None, None)
                
                self._solve_route()
                #TODO: Avaliar se o resultado melhora ao mudar a posição do depot para a order número 2 da rota que pertence (func_change_position, self.solve_route())

            except Exception as e:
                self.logger.error('Nenhuma empresa foi roteirizada para o idcarteira(modoviagem) (%s(%s))' % (polo_travelmode['id'], polo_travelmode['modoviagem']))
                self.logger.error(e.args[0])
            
            self._append_orders_all()
            if year != max(years):
                self._clear_orders_already_routed()
                self._regeneration_depots(polo_travelmode)        
    
    def run(self):

        self.schedule.synchronize_schedules()
        #polo_travelmode_of_work_areas = self.base_route.get_polo_and_travelmode_of_work_areas()
        polo_travelmode_of_work_areas = self.base_route.get_carteira_and_travelmode_of_work_areas()
        self._make_layer_route()
        count = 0
        for polo_travelmode in polo_travelmode_of_work_areas:
            count += 1
            self._create_feature_in_memory('Orders_All', 'Orders')
            #self.logger.info('Gerando roteiros para o polo(modoviagem) (%s(%s)) (%s/%s)' % (polo_travelmode['polo'], polo_travelmode['modoviagem'], count, len(polo_travelmode_of_work_areas)))
            self.logger.info('Gerando roteiros para o idcarteira(modoviagem) (%s(%s)) (%s/%s)' % (polo_travelmode['id'], polo_travelmode['modoviagem'], count, len(polo_travelmode_of_work_areas)))
            #self.base_route.filter_company(polo_travelmode, self._get_work_areas())
            self.base_route.filter_company_by_id(polo_travelmode)
            companies = self.geodatabase.search_data(self.base_route.get_name_feature_filtered("Empresas"), ['executivoId'])
            if len(companies) == 0:
                #self.logger.info('Nenhuma empresa encontrada para o polo(modoviagem) (%s(%s))' % (polo_travelmode['polo'], polo_travelmode['modoviagem']))
                self.logger.info('Nenhuma empresa encontrada para o idcarteira(modoviagem) (%s(%s))' % (polo_travelmode['id'], polo_travelmode['modoviagem']))
                continue

            mode = self.travel_modes['Driving Time'] if polo_travelmode['modoviagem'] == 'Driving' else self.travel_modes['Walking Time']
            self.solver_properties.applyTravelMode(mode)

            self._load_companies_to_orders() 
            years = self.depots.create(polo_travelmode)        
            #self._create_route_zones()
            
            self._generate_routes(polo_travelmode, years)
            
            self._register_companies_with_violations(polo_travelmode)

            routes = self._get_payload_routes()    

            executives_ids = self.base_route.get_executives_ids(companies)
            self.base_route.publish_new_routes(executives_ids, routes)            

            self._clear_objects_vrp()
        

