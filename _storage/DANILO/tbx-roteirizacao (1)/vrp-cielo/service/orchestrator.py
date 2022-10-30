# -*- coding: utf-8 -*-
from datetime import datetime as date
import re
import numpy
from service.vehicle_routing_problem import VehicleRoutingProblem
from esri.geodatabase import Geodatabase
import helper.utils as utils
import os
from collections import OrderedDict
import concurrent.futures

LAYER_NAME_ROUTE = "WorkVehicleRoutingProblem"
FT_COMPANIES_WITHOUT_ROUTE = "EmpresasNaoRoteirizadas"
FT_COMPANIES_WITH_ROUTE = "EmpresasRoteirizadas"
FT_ROUTE = "Roteiros"

class Orchestrator():
    def __init__(self, logger, config, continue_process):
        self.logger = logger
        self.config = config
        self.continue_process = continue_process
        self.geodatabase = Geodatabase(self.logger, self.config)
        self.file_gdb_name = 'Roteiros_VRP'
        self.path_gdb = self.file_gdb_name+'.gdb'
        self.gdb_finale = None
        self.fields_excel = None
        self.path_temp = self.config.get_folder_temp()
        self._arcpy = __import__("arcpy") if self.config.get_env_run() != "test" else None

    def _get_key(self, item):
        return '%s#%s' % (item['GEO_ID'], item['IBGE'])
    
    def _filter_keys(self, dict):
        return list(set([self._get_key(row) for row in dict]))
    
    def _get_key_geoid(self, item):
        return '%s' % (item['GEO_ID'])

    def _get_geoid(self, dict):
        return list(set([self._get_key_geoid(row) for row in dict]))

    def _construct_dictionary(self, excel_companies):
        #self.logger.info('_construct_dictionary*************************')
        keys = self._filter_keys(excel_companies)
        geoid = self._get_geoid(excel_companies)
        dictionary = {}
        
        for geo in geoid:
            dictionary[geo] = {}
            for key in keys:
                if geo == key.split('#')[0]:
                    dictionary[geo][key] = [company for company in excel_companies if self._get_key(company) == key and self._get_key_geoid(company) == geo]

        return dictionary
    
    def _create_fgdb_routes(self, folder, name):
        self.geodatabase.create(folder, name)
    
    def _create_feature_routes(self, path, name, type, fields):
        self.geodatabase.create_feature(path, name, type, fields)
    
    def _populate_feature(self, path, feature, fields, data):
        self.geodatabase.insert_data(path, feature, fields, data)
    
    def _generate_gdb_finale(self, fields_excel, param_out):
        self._create_fgdb_routes(param_out, self.file_gdb_name)
        
        self._generate_feature_roteiros(fields_excel, param_out)
        self._generate_feature_violation(fields_excel, param_out)
        self._generate_feature_routes_line(param_out)
    
    def _generate_geojson(self, output_json):
        self.geodatabase.export_to_json(os.path.join(output_json, self.path_gdb), "EmpresasRoteirizadas",  os.path.join(output_json, "roteiros"))
    
    def _generate_csv(self, output):
        self.geodatabase.export_to_csv(os.path.join(self.gdb_finale, "EmpresasRoteirizadas"), output, "EmpresasRoteirizadas")
        self.geodatabase.export_to_csv(os.path.join(self.gdb_finale, "EmpresasNaoRoteirizadas"), output, "EmpresasNaoRoteirizadas")

    def _generate_feature_routes_line(self, param_out):
        feature_name = 'Roteiros'
        fields = ['Name', 'MaxOrderCount', 'TotalCost', 'TotalTime', 'TotalOrderServiceTime', 'TotalTravelTime', 'TotalDistance', 'OrderCount', 'MaxTotalDistance']
        self._create_feature_routes(os.path.join(param_out, self.path_gdb), feature_name, "POLYLINE", fields)
    
    def _generate_feature_roteiros(self, fields_excel, param_out):
        feature_name = 'EmpresasRoteirizadas'
        self._create_feature_routes(os.path.join(param_out, self.path_gdb), feature_name, "POINT", fields_excel)
    
    def _generate_feature_violation(self, fields_excel, param_out):
        #self.logger.info('_generate_feature_violation*************************')
        fields_excel_violation = fields_excel

        for column in ["ID_ROTA", "OPCOES", "SEQUENCIA"]:
            fields_excel_violation.remove(column)
        
        for column in ["DATA_GERACAO", "Motivo1", "Motivo2", "Motivo3", "Motivo4"]:
            fields_excel_violation.append(column)

        feature_name = 'EmpresasNaoRoteirizadas'
        self._create_feature_routes(os.path.join(param_out, self.path_gdb), feature_name, "POINT", fields_excel_violation)

    def _get_fields_file(self, path_file):
        fields = utils.get_colum_file_xls(path_file)
        for column in ["ID_ROTA", "OPCOES", "SEQUENCIA"]:
            fields.append(column)
        return fields
    
    def _delete_gdb_temp(self, path_gdb):
        try:
            utils.delete_if_exists(path_gdb)
        except:
            print("não foi possivel apagar o gdb temp")

    def _delete_gdb_finale_if_exists(self, param_out):
        try:
            gdb_finale = os.path.join(param_out, self.file_gdb_name + '.gdb')
            utils.delete_if_exists(gdb_finale)
        except:
            print("não foi possivel apagar o gdb")
    
    def _order_group_by_vrp(self, entrada, reverse=False):
        #self.logger.info('_order_group_by_vrp*************************')
        chave_numroutes = []

        for key in entrada.keys():
            chave_numroutes.append(
                [
                    key,
                    entrada[key]['num_routes']
                ]
            )

        sorted_chave_numroutes = sorted(chave_numroutes, key=lambda x: x[1], reverse=reverse)

        sorted_entrada = []

        for item in sorted_chave_numroutes:
            sorted_entrada.append(entrada[item[0]])

        return sorted_entrada
    
    def _check_priority(self, group):
        #self.logger.info('_check_priority*************************')
        order_with_priority = {}
        for item in group:
            for company in group[item]:
                if company['PRIORIDADE_AGENDADO'] == 1:
                    order_with_priority[item] = []
                    order_with_priority[item] = group[item]

        for item in group:
            if not item in order_with_priority:
                order_with_priority[item] = []
                order_with_priority[item] = group[item]

        return order_with_priority
    
    def _get_limit_value_from_key(self, company, key, value_default = None):
        limit = value_default
        for item in company:
            if item[key] != None:
                if str(item[key]).strip() != '' and str(item[key]) != '0':
                    limit = int(item[key])
                 
        return limit
    
    def _check_limit_route(self, companies, total_routes_gerate, total_routes):
        #self.logger.info('_check_limit_route*************************')
        total_remove_route = 0
        for company in companies:
            if companies[company]['num_routes'] > 1 and (total_routes_gerate - total_remove_route) > total_routes:
                companies[company]['num_routes'] -= 1
                total_remove_route += 1
        
        return { "company": companies, "total-remove": (total_routes_gerate - total_remove_route) }
    
    def _calculate_total_routes(self, companies, limit_visit):
        return int(numpy.round(len(companies) / int(limit_visit)))

    def _group_by_vrp(self, group, total_routes, total_visit_per_route):
        #self.logger.info('_group_by_vrp*************************')
        total_group = len(group)
        total_routes_gerate = 0
        not_roteirized = []
        
        group = self._check_priority(group)

        if total_group > total_routes:
            refactor_group = {}
            for gp in group:
                if len(refactor_group) < total_routes:
                    refactor_group[gp] = []
                    for lead in group[gp]:
                        refactor_group[gp].append(lead)
                else:
                    for lead in group[gp]:
                        not_roteirized.append(lead)
                        
            group = refactor_group

        companies = {}
        for group_geoid in group:
            limit_visit = self._get_limit_value_from_key(group[group_geoid], "LIMITE_VISITAS", total_visit_per_route)
            companies[group_geoid] = {}
            companies[group_geoid]['limit_km'] = self._get_limit_value_from_key(group[group_geoid], "LIMITE_METROS")
            companies[group_geoid]['limit_visit'] = limit_visit
            companies[group_geoid]['num_routes'] = None
            companies[group_geoid]["orders"] = []
            for company in group[group_geoid]:
                companies[group_geoid]["orders"].append(company)
            
            routes_total = self._calculate_total_routes(companies[group_geoid]['orders'], limit_visit)
            companies[group_geoid]['num_routes'] =  routes_total if routes_total != 0 else 1
            total_routes_gerate += companies[group_geoid]['num_routes']
        
        if total_routes_gerate > total_routes:
            new_order = OrderedDict(reversed(list(companies.items())))
            while total_routes_gerate != total_routes:
                verify = self._check_limit_route(new_order, total_routes_gerate, total_routes)
                companies = verify['company']
                total_routes_gerate = verify['total-remove']

        return {"companies": companies, "route_not_roteirized": not_roteirized}

    def _validade_excel_file(self, xlsx):
        self.logger.info("Validando arquivo excel")
        fields_excel_requeired = ["GEO_ID", "IBGE", "LONGITUDE_X", "LATITUDE_Y", "NU_EC", "PRIORIDADE_AGENDADO", "LIMITE_VISITAS", "LIMITE_METROS"]
        error = False

        for field in fields_excel_requeired:
            if not field in self.fields_excel:
                self.logger.info("Campo não encontrado: " + field)
                error = True
        
        if error:
            return error

        for file in xlsx:
            for field in fields_excel_requeired:
                if file[field] == "" or file[field] == None:
                    self.logger.info(field + " campo obrigatório vazio: \n" + str(file))
                    error = True
        
        return error
        
    def _append_results(self, gdb_routes_vrp_temp):
        self.logger.info("Realizando o append dos dados...")
        for layer in [FT_COMPANIES_WITH_ROUTE, FT_COMPANIES_WITHOUT_ROUTE, FT_ROUTE]:
            path_vrp_temp = []
            for vrp_temp in gdb_routes_vrp_temp:
                path_vrp_temp.append(os.path.join(self.path_temp, vrp_temp+'.gdb', layer))
            self.geodatabase.append_data(path_vrp_temp, os.path.join(self.gdb_finale, layer))        
    
    def for_execution_group(self, groups_companies, group, num_total_routes, num_visits_per_route, cursorCompaniesWithRoute, cursorCompaniesWithoutRoute, cursorRoutesWithoutShape, cursorRoutes):
        companies = self._group_by_vrp(groups_companies[group], num_total_routes, num_visits_per_route)                        
        process_names = []
        for index, company in enumerate(companies['companies']):
            name_company = re.sub('[^A-Za-z0-9]+', '', company)
            process_name = "routes_vrp_temp_%s" % (name_company)                            
            # self.logger.info("\n\n -----------" + process_name + "----------- \n\n")

            company_route = companies['companies'][company]
            num_visits_per_route = num_visits_per_route if company_route['limit_visit'] == None or company_route['limit_visit'] == '' else company_route['limit_visit']
            layer_name_process = LAYER_NAME_ROUTE + "_" + name_company 
            
            vrp = VehicleRoutingProblem(self.logger, self.config, process_name, layer_name_process, company_route['orders'], self.gdb_finale, self.fields_excel, company_route['num_routes'], num_visits_per_route, company_route['limit_km'], cursorCompaniesWithRoute, cursorCompaniesWithoutRoute, cursorRoutesWithoutShape, cursorRoutes)
            if self.continue_process and vrp.exists_generated_routes():
                vrp.save_output()
            else:
                vrp.execute()

            #vrp.delete_companies_outside_city_limits()

            if index == 0:
                vrp.save_companies_outside_city_limits(companies['route_not_roteirized'])
            
            process_names.append(process_name)
        
        return process_names

    def _create_folder_output(self, param_out):
        def format_number(num):
            return num if num > 9 else '0'+str(num)
            
        date_execution = date.now()
        label_date_execution = "%s%s%s%s%s" % (date_execution.year, format_number(date_execution.month), format_number(date_execution.day), format_number(date_execution.hour), format_number(date_execution.minute))
        new_folder_out = "Output_" + label_date_execution
        param_out = os.path.join(param_out, new_folder_out)
        utils.create_folder_temp(param_out)
        return param_out     

    def normalize_visit_options(self, groups_companies):
        geo_id_to_normalize = []
        for geo_id in groups_companies:
            count = 0
            for city in groups_companies[geo_id]:
                count += 1
            if count > 1:
                geo_id_to_normalize.append(geo_id)
        
        where_geo_id = "GEO_ID in ('%s')" % ','.join(geo_id_to_normalize)
        companies_with_routes = self.geodatabase.search_data(self.gdb_finale, FT_COMPANIES_WITH_ROUTE, ["OBJECTID", "ID_ROTA", "OPCOES"], where_geo_id, "ORDER BY ID_ROTA ASC")
        previous_route = None
        visit_option = 0
        for route_visit in companies_with_routes:
            if route_visit['ID_ROTA'] != previous_route:
                previous_route = route_visit['ID_ROTA']
                visit_option += 1
            route_visit['OPCOES'] = visit_option

        self.geodatabase.update_data(self.gdb_finale, FT_COMPANIES_WITH_ROUTE, ["OBJECTID", "OPCOES"], where_geo_id, companies_with_routes, "OBJECTID")

    def execute(self, param_excel, param_out, num_total_routes, num_visits_per_route):
        num_total_routes = int(num_total_routes)
        num_visits_per_route = int(num_visits_per_route)

        if self.continue_process == False:
            self._delete_gdb_temp(self.path_temp)
            utils.create_folder_temp(self.path_temp)

        self.fields_excel = self._get_fields_file(param_excel)

        xlsx = utils.read_file_xlsx(param_excel)

        if self._validade_excel_file(xlsx):
            self.logger.error("Arquivo excel não validado")
            return

        self.logger.info("Lendo arquivo excel: total de linhas: " + str(len(xlsx)) + "\n")

        groups_companies = self._construct_dictionary(xlsx)

        total_groups = len(groups_companies)
        self.logger.info("Total de grupos para roteirizar: " + str(total_groups) + "\n")

        param_out = self._create_folder_output(param_out)

        self._generate_gdb_finale(self.fields_excel, param_out)

        self.gdb_finale = os.path.join(param_out, self.path_gdb)
        
        self.logger.info('Iniciando processamento...')
        # self.logger.info("for do VRP")

        edit = self._arcpy.da.Editor(self.gdb_finale)
        edit.startEditing(False, True)
        edit.startOperation()

        #criando cursores finais        
        fields = self.fields_excel.copy()
        for column in ["DATA_GERACAO", "Motivo1", "Motivo2", "Motivo3", "Motivo4", 'SHAPE@JSON']:
            if column in fields:
                fields.remove(column)

        for column in ["ID_ROTA", "OPCOES", "SEQUENCIA", 'SHAPE@JSON']:
            if not column in fields:
                fields.append(column)                

        cursorCompaniesWithRoute = self._arcpy.da.InsertCursor(os.path.join(self.gdb_finale, FT_COMPANIES_WITH_ROUTE), fields)

        fields2 = self.fields_excel.copy()
        for column in ["ID_ROTA", "OPCOES", "SEQUENCIA", 'SHAPE@JSON']:
            if column in fields2:
                fields2.remove(column)

        fields2.append('SHAPE@JSON') 

        cursorCompaniesWithoutRoute = self._arcpy.da.InsertCursor(os.path.join(self.gdb_finale, FT_COMPANIES_WITHOUT_ROUTE), fields2)

        fields_routes = ['Name', 'MaxOrderCount', 'TotalCost', 'TotalTime', 'TotalOrderServiceTime', 'TotalTravelTime', 'TotalDistance', 'OrderCount', 'MaxTotalDistance']
        cursorRoutesWithoutShape = self._arcpy.da.InsertCursor(os.path.join(self.gdb_finale, FT_ROUTE), fields_routes)

        fields_routes2 = ['Name', 'MaxOrderCount', 'TotalCost', 'TotalTime', 'TotalOrderServiceTime', 'TotalTravelTime', 'TotalDistance', 'OrderCount', 'MaxTotalDistance', 'SHAPE@JSON']
        cursorRoutes = self._arcpy.da.InsertCursor(os.path.join(self.gdb_finale, FT_ROUTE), fields_routes2)

        # cursorCompaniesWithRoute = None
        # cursorCompaniesWithoutRoute = None
        # cursorRoutesWithoutShape = None
        # cursorRoutes = None

        # for index, group in enumerate(groups_companies):
        #     self.for_execution_group(groups_companies, group, num_total_routes, num_visits_per_route, cursorCompaniesWithRoute, cursorCompaniesWithoutRoute, cursorRoutesWithoutShape, cursorRoutes)

        gdb_routes_vrp_temp = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()-1) as executor:
            execution_group = {executor.submit(self.for_execution_group, groups_companies, group, num_total_routes, num_visits_per_route, cursorCompaniesWithRoute, cursorCompaniesWithoutRoute, cursorRoutesWithoutShape, cursorRoutes): group for index, group in enumerate(groups_companies)}
            for execution in concurrent.futures.as_completed(execution_group):
                response = execution_group[execution]                
                try:
                    process_names = execution.result()
                except Exception as exc:
                    self.logger.info('%r generated an exception GEO_ID: %s' % (response, exc))
                else:
                    self.logger.info('GEO_ID: %s' % (response)) 
                    gdb_routes_vrp_temp = gdb_routes_vrp_temp + process_names

        del cursorCompaniesWithRoute
        del cursorCompaniesWithoutRoute
        del cursorRoutesWithoutShape
        del cursorRoutes

        self.normalize_visit_options(groups_companies)

        edit.stopOperation()
        edit.stopEditing(True)

        #self._append_results(gdb_routes_vrp_temp)
        
        # self.logger.info("fim...for do VRP")

        try:
            self._generate_geojson(param_out)
            self._generate_csv(param_out)
        except:
            self.logger.info("Erro ao gerar arquivos de saída")