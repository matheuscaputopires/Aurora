import os
import json
from datetime import timedelta
from datetime import datetime as date
from config import Config
import helper.utils as utils
from esri import feature_server
from esri.geodatabase import Geodatabase
from esri.tool import Tool

FT_WORK_AREAS = "Carteiras"
FT_WORK_AREAS_INTERSECT = "WorkArea_to_Inter"
FT_COMPANIES_TO_INTERSECT = "Companies_to_Inter"
FT_COMPANIES_INTERSECTED = "Compan_WorkAre_Upt"
WHERE_WORK_AREA_IS_NOT_NULL = "polo IS NOT NULL AND carteira IS NOT NULL AND inativo = 0" # AND id= 1159101

class BaseRoute():
    def __init__(self, logger):    
        self.logger = logger
        self.params = Config().get_params()
        self.route_generation_date = Config().route_generation_date
        self._arcpy = __import__("arcpy") if Config().get_env() != "test" else None
        self.geodatabase = Geodatabase(logger)
        self.tool = Tool(logger)
        self.user_hierarchies = None
        self.holidays = self._get_holidays()
    
    def _get_holidays(self):
        dirpath = Config().get_folder_main()
        config_filename = os.path.join(dirpath, 'holidays.json')
        with open(config_filename) as json_file:
            holidays = json.load(json_file)['holidays']
        return holidays

    def _get_user_hierarchies(self):
        if self.user_hierarchies == None:
            self.user_hierarchies = feature_server.get_feature_data(self.params['user_hierarchies'])
        return self.user_hierarchies

    def start_route_day(self):
        return (date.now() + timedelta(days=self.params['route']['next_days'])).replace(hour=self.params['route']['start_time']['hour'], minute=self.params['route']['start_time']['minute'], second=0, microsecond=0)

    def get_route_day(self, date=date.now()):
        route_day = date + timedelta(days=1)
        if route_day.weekday() == 5 or route_day.weekday() == 6:
            return self.get_route_day(route_day)
        
        for holiday in self.holidays:
            if int(holiday['day']) == route_day.day and int(holiday['month']) == route_day.month:
                return self.get_route_day(route_day)

        return route_day

    def normalize_companies_server(self):
        self.logger.info('Normalizando dados de empresas...')
        work_areas = feature_server.get_feature_data(self.params['work_areas_feature_url'], WHERE_WORK_AREA_IS_NOT_NULL)

        last_date_created_work_area = utils.timestamp_to_datetime(work_areas[0]['attributes']['created_date'])
        
        where_companies = "((nomeexecutivo IS NULL OR nomeexecutivo = ' ' OR polo IS NULL or carteira IS NULL or carteira = ' ') AND carteiraid IS NOT NULL AND roteirizar = 1)"
        where_companies += " OR roteirizar = 1 AND dataidentificacaocarteira < Date '%s 23:59:59'" % (last_date_created_work_area.strftime('%Y-%m-%d'))
        where_companies += " OR roteirizar = 1 AND dataidentificacaocarteira IS NULL"
        companies = feature_server.get_feature_data(self.params['leads_feature_url'], where_companies)

        self.logger.info("Empresas encontradas para normalização (%s)..." % (len(companies)))
        if len(companies) == 0:
            return

        self.geodatabase.copy_template_feature_to_temp_gdb(self.params['company_name'], FT_COMPANIES_TO_INTERSECT)

        companies_to_insert = []
        for company in companies:
            companies_to_insert.append({
                'attributes': {
                    'id': company['attributes']['id']
                },
                'geometry': company['geometry']
            })        
        self.geodatabase.insert_data(companies_to_insert, FT_COMPANIES_TO_INTERSECT, ["id", "SHAPE@XY"])

        self.geodatabase.copy_template_feature_to_temp_gdb(FT_WORK_AREAS, FT_WORK_AREAS_INTERSECT, "POLYGON")
        self.geodatabase.insert_data(work_areas, FT_WORK_AREAS_INTERSECT, ["id", "carteira", "polo", "nome", "SHAPE@JSON"])                

        self.tool.intersect(FT_COMPANIES_TO_INTERSECT, FT_WORK_AREAS_INTERSECT, FT_COMPANIES_INTERSECTED)

        companies_intersected = self.geodatabase.search_data(FT_COMPANIES_INTERSECTED, ["id", "id_1", "carteira", "polo", "nome"], dict_key="id")

        companies_to_update = []
        count = 0
        date_identify_work_area = utils.datetime_to_timestamp(self.route_generation_date)
        for company in companies:
            count +=1
            company_id = company['attributes']['id']
            company['attributes']['dataidentificacaocarteira'] = date_identify_work_area
            if company_id in companies_intersected:
                work_area_filtered = companies_intersected[company_id]
                company['attributes']['nomeexecutivo'] = work_area_filtered['nome']
                company['attributes']['polo'] = work_area_filtered['polo']
                company['attributes']['carteira'] = work_area_filtered['carteira']
                company['attributes']['carteiraid'] = work_area_filtered['id_1']
            else:
                company['attributes']['roteirizar'] = 0

            companies_to_update.append(company)

            if count % 1000 == 0 or count == len(companies):
                self.logger.info('Normalizando empresas (%s/%s)...' % (count, len(companies)))
                feature_server.update_feature_data(self.params['leads_feature_url'], companies_to_update)
                companies_to_update = []

    def get_polo_and_travelmode_of_work_areas(self):
        return [item['attributes'] for item in feature_server.get_feature_data(self.params['work_areas_feature_url'], WHERE_WORK_AREA_IS_NOT_NULL, "polo, modoviagem", False)]

    def get_carteira_and_travelmode_of_work_areas(self):
        return [item['attributes'] for item in feature_server.get_feature_data(self.params['work_areas_feature_url'], WHERE_WORK_AREA_IS_NOT_NULL, "id, modoviagem, distanciatotalroteiro", False)]

    def get_work_areas(self):
        return feature_server.get_feature_data(self.params['work_areas_feature_url'], WHERE_WORK_AREA_IS_NOT_NULL) # AND id in (1,2)

    def _get_name_superiors(self, work_area_id):
        order_hierarchy = ['Supervisor', 'Coordenador', 'Gerente', 'Gerente Geral']
        user_filtered = [i['attributes'] for i in self._get_user_hierarchies() if i['attributes']['carteiraid'] == work_area_id]
        hierarchy = {}
        if len(user_filtered) == 0:
            for p in order_hierarchy:
                hierarchy[p] = None
        else:
            user = user_filtered[0]
            user_filtered = user['usuariosuperior']
            for p in order_hierarchy:
                superior = [i['attributes'] for i in self._get_user_hierarchies() if i['attributes']['usuario'] == user_filtered and i['attributes']['perfil'] == p]
                hierarchy[p] = None
                if len(superior) > 0:
                    user_filtered = superior[0]['usuariosuperior']
                    hierarchy[p] = superior[0]['nome']
            
        return hierarchy
    
    def construct_payload(self, company, executive, sequence, visit_date, creation_date, date_scheduled, id_scheduled, work_area, position_x, position_y):
        hierarchy = self._get_name_superiors(work_area['id'])
        return {
                "attributes": {
                    "empresaid": company['id'],
                    "executivoid": executive['id'],
                    "nome": executive['nome'],
                    "realizado": 0,
                    "sequencia": sequence,
                    "dataprogramada": utils.datetime_to_timestamp(visit_date),
                    "datacriacao": utils.datetime_to_timestamp(creation_date),
                    "dataagendada": None if date_scheduled == None else utils.datetime_to_timestamp(date_scheduled),
                    "agendamentoid": id_scheduled,
                    "polo": work_area['polo'],
                    "carteira": work_area['carteira'],
                    "empresa": company['empresa'],
                    "endereco": company['endereco'],
                    "numero": company['numero'],
                    "cidade": company['cidade'],
                    "estado": company['estado'],
                    "bairro": company['bairro'],
                    "cep": company['cep'],
                    "origem": 0,
                    "foracarteira": 0,
                    "inativo": 0,
                    "gerenciageral": hierarchy['Gerente Geral'],
                    "gerencia": hierarchy['Gerente'],
                    "coordenacao": hierarchy['Coordenador'],
                    "supervisao": hierarchy['Supervisor'],
                    "carteiraid": work_area['id'],
                    "cnpjcpf": company['cnpjcpf'],
                    "idpagseguro": company['idpagseguro'],
                    "nomeusuarioexecutivo": executive['nomeusuarioexecutivo'],
                    "tipoalerta": company['tipoalerta']
                },
                "geometry": {
                    "x": position_x,
                    "y": position_y,
                    "spatialReference": {
                        "wkid": 4326
                    }
                }}

    def get_name_feature_filtered(self, name):
        return os.path.join("in_memory", name + "_filtered")
    
    def filter_data_in_feature(self, feature_name, where):
        feature = os.path.join(self.geodatabase.get_path(), feature_name)
        feature_filtered = self._arcpy.SelectLayerByAttribute_management(feature, "NEW_SELECTION", where)
        self._arcpy.CopyFeatures_management(feature_filtered , self.get_name_feature_filtered(feature_name))

    def filter_area_by_polo_travelmode(self, area, polo_travelmode):
        return area['attributes']['polo'] == polo_travelmode['polo'] and area['attributes']['modoviagem'] == polo_travelmode['modoviagem']

    def filter_company(self, polo_travelmode, work_areas):
        work_areas_ids = [str(area['attributes']['id']) for area in work_areas if self.filter_area_by_polo_travelmode(area, polo_travelmode)]
        where = "carteiraId IN (%s)" % (",".join(work_areas_ids))
        self.filter_data_in_feature("Empresas", where)                      

    def filter_company_by_id(self, polo_travelmode):
        work_areas_ids = [str(polo_travelmode['id'])]
        where = "carteiraId IN (%s)" % (",".join(work_areas_ids))
        self.filter_data_in_feature("Empresas", where)                              

    def get_executives_ids(self, companies):
        return [str(item) for item in utils.get_unique_values_from_items('executivoId', companies)]

    def _delete_unrealized_routes(self, executives_ids):
        self.logger.info('Deletando roteiros não executados...')
        now = date.now()
        tomorrow = self.get_route_day(now)
        query_filter = "inativo = 1 AND dataprogramada >= DATE '{0}-{1}-{2}' AND realizado = 0 AND executivoid IN ({3})".format(tomorrow.year, tomorrow.month, tomorrow.day, (",".join(executives_ids)))
        response = feature_server.delete_feature_data(self.params['routes_feature_url'], query_filter)
        #deleted_count = len(response['deleteResults'])
        #self.logger.info('Foram deletados {0} roteiros'.format(deleted_count))        
        self.logger.info('Foram deletados roteiros com a query: {0}'.format(query_filter))
    
    def _inactive_unrealized_routes(self, executives_ids, reverse=False):
        tomorrow = self.get_route_day()
        where = "dataprogramada >= DATE '{0}-{1}-{2}' AND realizado = 0 AND executivoid IN ({3})".format(tomorrow.year, tomorrow.month, tomorrow.day, (",".join(executives_ids)))
        calc_expression = [{'field': 'inativo', 'value': 1 if reverse == False else 0}]
        response_count = feature_server.calculate_feature_data(self.params['routes_feature_url'], where, calc_expression)
        self.logger.info('Foram inativados {0} roteiros'.format(response_count))            

    def _publish_routes(self, executives_ids, routes):        
        self.logger.info("Publicando roteiros no ArcGIS Server...")
        try:
            routes_feature_url = self.params['routes_feature_url']
            routes_by_executive_id = utils.get_unique_values_from_items('executivoid', [item['attributes'] for item in routes])
            for executive_id in routes_by_executive_id:
                payload = [item for item in routes if item['attributes']['executivoid'] == executive_id]

                results = feature_server.post_feature_data(routes_feature_url, payload)

                transactions_fail = [item for item in results if item['success'] == False]
                if len(transactions_fail) > 0:
                    self.logger.error('Falha ao inserir os roteios da executive_id %s' % (executive_id))
                    if len(transactions_fail) == len(payload):
                        self._inactive_unrealized_routes(executives_ids, True)                        
        except Exception as e:
            self._inactive_unrealized_routes(executives_ids, True)
            raise e

    def publish_new_routes(self, executives_ids, routes):
        self._inactive_unrealized_routes(executives_ids)
        self._publish_routes(executives_ids, routes)
        self._delete_unrealized_routes(executives_ids)