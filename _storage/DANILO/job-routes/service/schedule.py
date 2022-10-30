# -*- coding: utf-8 -*-
import os
from config import Config
from datetime import datetime, timedelta
from datetime import datetime as date
import json
import helper.utils as utils
from esri import feature_server
from esri.tool import Tool
from esri.geodatabase import Geodatabase
from service.base_route import BaseRoute

FT_GEOCODE_SCHEDULES = "Geocode_Agendamentos"
FT_GEOCODE_SCHEDULES_RESULT = "Geocode_Agendamentos_Result"

class Schedule():
    def __init__(self, logger):    
        self.logger = logger
        self.params = Config().get_params()
        self._arcpy = __import__("arcpy") if Config().get_env() != "test" else None
        self.geodatabase = Geodatabase(logger)
        self.base_route = BaseRoute(logger)
        self.tool = Tool(logger)
        self.dict_schedules = {}

    def _get_id_dict(self, company_id, date_scheduled):
        date_schedule_format = utils.timestamp_to_datetime(date_scheduled) if isinstance(date_scheduled, int) else date_scheduled
        return '%s#%s' % (company_id, date_schedule_format.strftime('%d%m%Y%H%M%S'))

    def _add_dict_schedule(self, item):
        self.dict_schedules[self._get_id_dict(item['empresaid'], item['datahora'])] = item
    
    def _prepare_item_schedule(self, item):
        item_prepared = item['attributes']
        self._add_dict_schedule(item_prepared)
        columns_to_from = [
            {'from': 'datahora', 'to': 'TimeWindowStart', 'format': 'date'},
            {'from': 'empresaid', 'to': 'id', 'format': None},
            {'from': 'TimeWindowEnd', 'to': 'TimeWindowEnd', 'format': 'date'},
            {'from': 'MaxViolationTime', 'to': 'MaxViolationTime', 'format': None}]
        
        if self._address_informed(item_prepared) and 'geometry' in item and item['geometry'] != None:
            columns_to_from.append({'from': 'endereco', 'to': 'endereco', 'format': None})
            columns_to_from.append({'from': 'numero', 'to': 'numero', 'format': None})
            columns_to_from.append({'from': 'cidade', 'to': 'cidade', 'format': None})
            columns_to_from.append({'from': 'bairro', 'to': 'bairro', 'format': None})
            columns_to_from.append({'from': 'estado', 'to': 'estado', 'format': None})
            columns_to_from.append({'from': 'cep', 'to': 'cep', 'format': None})
            
            columns_to_from.append({'from': 'SHAPE@JSON', 'to': 'SHAPE@JSON', 'format': None})
            item_prepared['SHAPE@JSON'] = json.dumps(item_prepared['geometry'])

        time_window_start = utils.timestamp_to_datetime(item_prepared['datahora'])
        time_window_end = time_window_start + timedelta(minutes=self.params['service_time_minutes'])
        item_prepared['TimeWindowEnd'] = utils.datetime_to_timestamp(time_window_end)
        item_prepared['MaxViolationTime'] = 0
        return self.geodatabase.prepare_item(columns_to_from, item_prepared)
    
    def _synchronize_schedules_ags_to_gdb(self, schedule_to_visit, feature_ags_field_id, feature_gdb, feature_columns_to_update, feature_gdb_field_id, geocode = False):
        if len(schedule_to_visit) > 0:
            if geocode:
                self.geodatabase.copy_template_table_to_temp_gdb(self.params['company_geocode'], FT_GEOCODE_SCHEDULES)

                companies = []
                for item in schedule_to_visit:
                    item['attributes']['enderecocompleto'] = '{0}, {1}, {2}, {3}, {4}, {5}'.format(item['attributes']['endereco'], item['attributes']['numero'], item['attributes']['bairro'], item['attributes']['cidade'], item['attributes']['estado'], item['attributes']['cep'])
                    companies.append(item)
                
                fields_geocode_schedules = ["id", "enderecocompleto"]

                self.geodatabase.insert_data(companies, os.path.join(self.geodatabase.get_path(), FT_GEOCODE_SCHEDULES), fields_geocode_schedules)

                self.tool.geocode(
                    os.path.join(self.geodatabase.get_path(), FT_GEOCODE_SCHEDULES),
                    FT_GEOCODE_SCHEDULES_RESULT)
                
                schedules_geocoded = self.geodatabase.search_data(os.path.join(self.geodatabase.get_path(), FT_GEOCODE_SCHEDULES_RESULT), ["Score", "USER_id", "Match_addr", 'SHAPE@JSON'])

                new_schedule_to_visit = []
                for tb_schedule in schedules_geocoded:
                    schedule = [c for c in schedule_to_visit if c['attributes']["id"] == tb_schedule["USER_id"]][0]
                    schedule['attributes']["data_geocode"] = utils.datetime_to_timestamp(datetime.now())
                    schedule['attributes']["endereco_geocode"] = tb_schedule['Match_addr']
                    if float(tb_schedule['Score']) >= 80:
                        schedule['attributes']["geometry"] = json.loads(tb_schedule['SHAPE@JSON'])
                        schedule["geometry"] = json.loads(tb_schedule['SHAPE@JSON'])
                        schedule["geometry"]['z'] = float(0.0)
                    else:
                        schedule['attributes']["erro_geocode"] = "Score: " + str(tb_schedule['Score'])
                        if 'geometry' in schedule:
                            schedule.pop('geometry', None)
                    new_schedule_to_visit.append(schedule)

                feature_server.update_feature_data(self.params["schedules_feature_url"], new_schedule_to_visit)
                self.logger.info("Agendamentos geocodificados atualizados: " + str(len(new_schedule_to_visit)))
                
                schedule_to_visit = new_schedule_to_visit
            
            features = [self._prepare_item_schedule(item) for item in schedule_to_visit]
            where = self.geodatabase.construct_where(feature_ags_field_id, features)
            self.geodatabase.update_data(feature_gdb, feature_columns_to_update, where, features, feature_gdb_field_id)

    def _address_informed(self, item):
        return item['endereco'] != None and item['cidade'] != None and item['bairro'] != None and item['estado'] != None
    
    def condition_schedule(self):
        return "datahora >= DATE '%s'" % (self.base_route.start_route_day().strftime("%Y-%m-%d"))

    def _separate_field_to_string(self, field, array):
        return ",".join([value['attributes'][field] for value in array])        

    def synchronize_schedules(self):
        self.logger.info("Sincronizando agendamentos...")

        schedules_feature_url = self.params['schedules_feature_url']
        where_schedules = self.condition_schedule()
        schedule_to_visit = feature_server.get_feature_data(schedules_feature_url, where_schedules, order_by_field="id ASC")
        ft_schedule_companies = os.path.join(self.geodatabase.get_path(), self.params['company_name'])
        self.logger.info("Agendamentos encontrados (%s) para condição (%s)" % (len(schedule_to_visit), where_schedules))

        get_ids_schedules = self._separate_field_to_string("empresaid", schedule_to_visit)
        if get_ids_schedules != '':
            companies = self.geodatabase.search_data("Empresas", ["id", "carteiraId", "executivoId"], "id IN (%s)" % get_ids_schedules)

            schedules_without_address = []
            schedules_with_address = []
            for item in schedule_to_visit:
                item_attr = item['attributes']
                if len([c for c in companies if c['id'] == item_attr['empresaid'] and c['executivoId'] == item_attr['executivoid']]) == 0: #agendamento pertence ao executivo responsável pela empresa?
                    continue
                if self._address_informed(item_attr):
                    schedules_with_address.append(item)
                else:
                    schedules_without_address.append(item)
                
            def _schedules_without_address(ft_companies):
                feature_columns_to_update = ['id','TimeWindowStart', 'TimeWindowEnd', 'MaxViolationTime']
                self._synchronize_schedules_ags_to_gdb(ft_companies, "id", ft_schedule_companies, feature_columns_to_update, "id")

            def _schedules_with_address(ft_companies):
                feature_columns_to_update = ['id','TimeWindowStart', 'TimeWindowEnd', 'MaxViolationTime', 'endereco', 'numero', 'bairro', 'cidade', 'estado', 'SHAPE@JSON']
                self._synchronize_schedules_ags_to_gdb(ft_companies, "id", ft_schedule_companies, feature_columns_to_update, "id", True)            

            _schedules_without_address(schedules_without_address)
            _schedules_with_address(schedules_with_address)

    def get_schedule_dict(self, company_id, date_scheduled):
        if company_id == None or date_scheduled == None:
            return None
        id_dict = self._get_id_dict(company_id, date_scheduled)
        return self.dict_schedules[id_dict] if id_dict in self.dict_schedules else None
    