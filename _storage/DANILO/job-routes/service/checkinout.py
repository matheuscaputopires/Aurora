
# -*- coding: utf-8 -*-
import os
import copy
from config import Config
from esri import feature_server
from service.notification import Notification
from esri.geodatabase import Geodatabase
from helper.errors import Error

FT_CHECKINOUT = 'checkinout'
FT_COMPANIES = 'companies'
TB_CHECKINOUT_NEAR_COMPANIES = 'checkinout_near_companies'

FIELDS_CHECKINOUT = [
    {'name': 'id', 'type': 'LONG'},
    {'name': 'objectid_server', 'type': 'LONG'},
    {'name': 'empresaid', 'type': 'LONG'},
    {'name': 'executivoid', 'type': 'LONG'},
    {'name': 'proximoempresa', 'type': 'SHORT'},
    {'name': 'polo', 'type': 'TEXT'},
    {'name': 'carteira', 'type': 'TEXT'},
    {'name': 'empresa', 'type': 'TEXT'},
    {'name': 'executivo', 'type': 'TEXT'}
]
FIELDS_COMPANY = [
    {'name': 'id', 'type': 'LONG'},
    {'name': 'empresa', 'type': 'TEXT'},
    {'name': 'polo', 'type': 'TEXT'},
    {'name': 'carteira', 'type': 'TEXT'},
    {'name': 'nomeexecutivo', 'type': 'TEXT'}    
]
class Checkinout:
    def __init__(self, logger):
        self.logger = logger
        self.config = Config()
        self._arcpy = __import__("arcpy") if self.config.get_env() != "test" else None
        self.params = self.config.get_params()
        self.geodatabase = Geodatabase(logger)
        self.notification = Notification(self.logger.process_full_name, self.params, logger)
        self.checkinouts = None
        self.fields_ft_company = None
        self.fields_ft_checkinout = None

    def _create_environment_analysis(self):
        self.geodatabase.create()
        self.geodatabase.create_feature(FT_CHECKINOUT, FIELDS_CHECKINOUT)
        self.geodatabase.create_feature(FT_COMPANIES, FIELDS_COMPANY)

    def _add_objectid_server(self, items):
        for item in items:
            item['attributes']['objectid_server'] = item['attributes']['objectid']        
        
        return items
    
    def _get_checkinouts(self):
        checkinouts = feature_server.get_feature_data(self.params['checkinout_feature_url'], "proximoempresa IS NULL AND empresaid IS NOT NULL")
        checkinouts = self._add_objectid_server(checkinouts)
        self.checkinouts = checkinouts
        
        return checkinouts
    
    def _get_companies(self, checkinouts):
        if len(checkinouts) == 0:
            return []

        companies_ids = []
        for checkinout in checkinouts:
            companies_ids.append(str(checkinout['attributes']['empresaid']))
        
        companies = feature_server.get_feature_data(self.params['leads_feature_url'], "id IN (%s)" % ",".join(companies_ids))
        #companies = self._add_objectid_server(companies) #TODO: TESTE E APAGAR
        return companies       
    
    def _populate_features(self, checkinouts, companies):

        def _get_fields_to_gdb(fields_base):
            fields = [field['name'] for field in fields_base]
            fields.append('SHAPE@JSON')
            return fields 

        self.logger.info('Populando dados nas features de Check-in/out e Empresas...')
        self.fields_ft_checkinout = _get_fields_to_gdb(FIELDS_CHECKINOUT)
        self.fields_ft_company = _get_fields_to_gdb(FIELDS_COMPANY)
        self.geodatabase.insert_data(checkinouts, FT_CHECKINOUT, self.fields_ft_checkinout)
        self.geodatabase.insert_data(companies, FT_COMPANIES, self.fields_ft_company)
        
    def _get_key(self, item):
        return '%s#%s' % (item['IN_FID'],item['NEAR_FID'])
    
    def _get_dict_checkinout_near_companies(self):
        checkinout_near_companies = self.geodatabase.search_data(TB_CHECKINOUT_NEAR_COMPANIES, ["IN_FID", "NEAR_FID", "NEAR_DIST"])
        dict_checkinout_near = {}
        for item in checkinout_near_companies:
            dict_checkinout_near[self._get_key(item)] = item

        return dict_checkinout_near

    def _get_dict_search_data(self, entity_name, fields, key):
        items = self.geodatabase.search_data(entity_name, fields)
        dict_items = {}
        for item in items:
            dict_items[item[key]] = item

        return dict_items                
    
    def _get_fields_search_data(self, entity_fields):
        fields = copy.copy(entity_fields)
        fields.append('objectid')
        return fields

    def _get_dict_checkinout(self):
        fields = self._get_fields_search_data(self.fields_ft_checkinout)
        return self._get_dict_search_data(FT_CHECKINOUT, fields, 'objectid_server')

    def _get_dict_companies(self):
        fields = self._get_fields_search_data(self.fields_ft_company)
        return self._get_dict_search_data(FT_COMPANIES, fields, 'id')        
    
    def _analyze_nearby_companies(self):
        self.logger.info('Analisando os registros de check-in/out que estão até 20m da empresa...')

        def _prepare_payload(checkinout, near_company, company):        
            return {
                'attributes': {
                    'objectid': checkinout['objectid'],
                    'proximoempresa': near_company,
                    'polo': company['polo'],
                    'carteira': company['carteira'],
                    'empresa': company['empresa'],
                    'executivo': company['nomeexecutivo']
                }
            }

        path_out_table = os.path.join(self.geodatabase.get_path(), TB_CHECKINOUT_NEAR_COMPANIES)
        self._arcpy.analysis.GenerateNearTable(FT_CHECKINOUT, FT_COMPANIES, path_out_table, "20 Meters", "NO_LOCATION", "NO_ANGLE", "ALL", 10000, "GEODESIC")

        dict_checkinout_near = self._get_dict_checkinout_near_companies()
        dict_checkinout = self._get_dict_checkinout()
        dict_companies = self._get_dict_companies()

        payload = []
        for checkinout_attr in self.checkinouts:
            checkinout = checkinout_attr['attributes']
            near_company = 0

            objectid_server_check = checkinout['objectid']
            objectid_local_checkin = dict_checkinout[objectid_server_check]['objectid']
            
            company_id = checkinout['empresaid']
            objectid_local_company = dict_companies[company_id]['objectid']
            
            checkinout_search_id = {'IN_FID': objectid_local_checkin, 'NEAR_FID': objectid_local_company}
            if self._get_key(checkinout_search_id) in dict_checkinout_near:
                near_company = 1 if dict_checkinout_near[self._get_key(checkinout_search_id)]['NEAR_DIST'] <= 20 else 0
            
            payload.append(_prepare_payload(checkinout, near_company, dict_companies[company_id]))

        return payload

    def _publish_checkinout_updated(self, payload):
        self.logger.info('Publicando atualização de %s check-in/out(s)' % (len(payload)))
        feature_server.update_feature_data(self.params['checkinout_feature_url'], payload)

    def execute(self):
        try:
            self._create_environment_analysis()

            checkinouts = self._get_checkinouts()
            companies = self._get_companies(checkinouts)

            if len(checkinouts) == 0 or len(companies) == 0:
                 raise Error('Did not find checkinout items or companies items!')

            self._populate_features(checkinouts, companies)

            payload = self._analyze_nearby_companies()
            self._publish_checkinout_updated(payload)

        except Error as e:
            self.logger.info(e)