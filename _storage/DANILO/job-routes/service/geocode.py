import os
from config import Config
import helper.utils as utils
from esri import feature_server
from service.base_route import BaseRoute
from esri.geodatabase import Geodatabase
from esri.tool import Tool

GEOCODED_FEATURE_NAME = "Geocoded_Companies"
WORK_AREAS_FEATURE_NAME = "Carteiras"
INTERSECT_FEATURE_NAME = "Compan_WorkAre_Int"

class Geocode():
    def __init__(self, logger):
        self.logger = logger
        self.params = Config().get_params()
        self.route_generation_date = Config().route_generation_date
        self._arcpy = __import__("arcpy") if Config().get_env() != "test" else None
        self.geodatabase = Geodatabase(logger)
        self.tool = Tool(logger)
        self.base_route = BaseRoute(logger)
        self.work_areas = []
        self.work_areas_dict = {}

    def _get_work_areas(self):
        if len(self.work_areas) == 0:
            self.work_areas = self.base_route.get_work_areas()
            for area in self.work_areas:
                self.work_areas_dict[area['attributes']['id']] = area

        return self.work_areas

    def _path_company_to_geocod(self):
        return os.path.join(self.geodatabase.get_path(), self.params['company_geocode'])

    def _path_company_geocoded(self):
        return os.path.join(self.geodatabase.get_path(), GEOCODED_FEATURE_NAME)

    def _path_company_intersect(self):
        return os.path.join(self.geodatabase.get_path(), INTERSECT_FEATURE_NAME)

    def _identify_companies_same_and_new_address(self, companies, companies_id):
        def _is_same_location(item, item2):
            fields = ['endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep', 'carteiraid']
            return len([1 for f in fields if item[f] == item2[f]]) == len(fields)

        companies_server = []
        if len(companies_id) > 0:
            where = "id in (%s)" % (','.join((str(id) for id in companies_id)))
            companies_server = feature_server.get_feature_data(self.params['leads_feature_url'], where)

        companies_dict = {}
        for c in companies_server: 
            companies_dict[c['attributes']['id']] = c['attributes']

        companies_same_address = []
        companies_new_address = []

        for company in companies:
            attr = company['attributes']
            if attr['id'] in companies_dict and _is_same_location(attr, companies_dict[attr['id']]) == True:
                company['attributes']['objectid'] = companies_dict[attr['id']]['objectid']
                companies_same_address.append(company['attributes'])
            else:
                companies_new_address.append(company)

        self.logger.info("Identificação de empresas sem alteração de endereço (%s) e novos endereços ou empresas (%s)..." % (len(companies_same_address), len(companies_new_address)))
        
        return {
            'new_address': companies_new_address,
            'same_address': companies_same_address
        }
    
    def _update_company_same_address(self, companies):
        if len(companies) == 0:
            return
        payload = []
        for company in companies:
            payload.append({
                'attributes': {
                    'objectid': company['objectid'],
                    'empresa': company['empresa'],
                    'clientepagseguro': company['clientepagseguro'],
                    'origem': company['origem'],
                    'roteirizar': company['roteirizar'],
                    'tipoalerta': company['tipoalerta']
                }
            })
        self.logger.info("Atualizando empresas que não tiveram atualização de endereço (%s)..." % (len(companies)))
        feature_server.update_feature_data(self.params['leads_feature_url'], payload)
    
    def _synchronize_leads_for_geocode(self):

        self.geodatabase.copy_template_table_to_temp_gdb(self.params['company_geocode'])
        geocodcompanies = feature_server.get_feature_data(self.params['geocode_companies'], logger=self.logger)

        companies_dict = {}
        companies = []
        companies_id = []
        for geocodcompany in geocodcompanies:
            company_id = geocodcompany['attributes']['id']
            if company_id in companies_dict and companies_dict[company_id] < geocodcompany['attributes']['objectid']:
                companies = [c for c in companies if c['attributes']['id'] != company_id]

            companies_dict[company_id] = geocodcompany['attributes']['objectid']
            
            del geocodcompany['attributes']['objectid']
            del geocodcompany['attributes']['globalid']
            geocodcompany['attributes']['enderecocompleto'] = '{0}, {1}, {2}, {3}, {4}, {5}'.format(geocodcompany['attributes']['endereco'], geocodcompany['attributes']['numero'], geocodcompany['attributes']['bairro'], geocodcompany['attributes']['cidade'], geocodcompany['attributes']['estado'], geocodcompany['attributes']['cep'])
            geocodcompany['attributes']['roteirizar'] = 1 if geocodcompany['attributes']['roteirizar'] != 0 else geocodcompany['attributes']['roteirizar']

            companies.append(geocodcompany)
            companies_id.append(company_id)

        self.logger.info("Leads sincronizados para geocodificação (%s)..." % (len(companies)))
        if len(companies) != len(geocodcompanies):
            leads_removed = len(geocodcompanies) - len(companies)
            self.logger.info("Leads duplicados removidos da geocodificação (%s)..." % (leads_removed))

        group_of_companies = self._identify_companies_same_and_new_address(companies, companies_id)

        self._update_company_same_address(group_of_companies['same_address'])
        self.geodatabase.insert_data(group_of_companies['new_address'], self._path_company_to_geocod(), self.params['local_table_fields'])

    def _list_fields(self, feature):
        return [f.name for f in self._arcpy.ListFields(feature)]

    def _get_fields(self, feature):
        remove_fields = ['objectid', 'shape', 'globalid', 'shape_length', 'shape_area']
        fields = [field_name for field_name in self._list_fields(feature) if field_name.lower() not in remove_fields]
        fields.append('SHAPE@JSON')
        return fields

    def _synchronize_work_areas(self):
        feature_work_areas = os.path.join(self.geodatabase.get_path(), WORK_AREAS_FEATURE_NAME)
        self.geodatabase.copy_template_feature_to_temp_gdb(WORK_AREAS_FEATURE_NAME, geom_type="POLYGON")

        work_areas = self._get_work_areas()

        self.logger.info("Carteiras sincronizados (%s)..." % (len(work_areas)))
        field_names = self._get_fields(feature_work_areas)
        self.geodatabase.insert_data(work_areas, feature_work_areas, field_names)

    def _geocode_leads(self):
        self.logger.info("Geocodificando endereços de leads...")
        self._arcpy.geocoding.GeocodeAddresses(
            self._path_company_to_geocod(),
            self.params['path_locator'],
            "'Single Line Input' enderecocompleto VISIBLE NONE",
            self._path_company_geocoded(),
            "STATIC", None, "ROUTING_LOCATION", "Subaddress;'Point Address';'Street Address';'Distance Marker';'Street Name'", "ALL")

    def _identify_work_areas(self):
        self.logger.info("Identificando as carteiras dos leads geocodificados...")
        self.tool.intersect(GEOCODED_FEATURE_NAME, WORK_AREAS_FEATURE_NAME, INTERSECT_FEATURE_NAME)

    def _company_contains_workarea(self, company):
        return company['USER_carteiraid'] != None and company['USER_polo'] != None
    
    def _validate_publish(self):
        self.logger.info("Validação do resultado da geocodificação...")

        feature_companies_intersect = self._path_company_intersect()
        companies_intersect = self.geodatabase.search_data(feature_companies_intersect, self._list_fields(feature_companies_intersect))

        feature_companies_geocode = self._path_company_geocoded()
        companies_geocode = self.geodatabase.search_data(feature_companies_geocode, self._list_fields(feature_companies_geocode))

        geocoded = []
        not_geocoded = []

        companies_intersect_dict = {}
        for i in companies_intersect:
            companies_intersect_dict[i['USER_id']] = i

        for company in companies_geocode:
            if company['Score'] >= 80 and company['USER_id'] in companies_intersect_dict:
                if self._company_contains_workarea(company):
                    if companies_intersect_dict[i['USER_id']]['polo'] == company['USER_polo']:
                        geocoded.append(companies_intersect_dict[company['USER_id']])
                    else:
                        not_geocoded.append(company)
                else:
                    geocoded.append(companies_intersect_dict[company['USER_id']])
            else:
                not_geocoded.append(company)

        self.logger.info("Leads geocodificados (%s) e não geocodificados (%s)..." % (len(geocoded), len(not_geocoded)))



        return {
            'geocoded': geocoded,
            'not_geocoded': not_geocoded
        }

    def _deletion_features(self, update_ids):
        response = feature_server.get_feature_data(feature_url=self.params['leads_feature_url'], geometries=False, distinct_values='id')
        feature_ids = [item['attributes']['id'] for item in response]
        result_ids = list(set(feature_ids) & set(update_ids))
        ids = [str(id) for id in result_ids]
        ids.append('0')
        return ids

    def _publish_new_leads(self, companies):
        self.logger.info("Publicação de leads geocodificados com sucesso...")
        payload = []
        ids = []
        count = 0

        for company in companies:
            count = count + 1
            ids.append(company['USER_id'])

            if self._company_contains_workarea(company):
                carteiraid = company['USER_carteiraid']
                carteira = company['USER_carteira'] if company['USER_carteira'] != None else self.work_areas_dict[carteiraid]['attributes']['carteira']
                polo = company['USER_polo']
            else:
                carteiraid = company['id']
                carteira = company['carteira']
                polo = company['polo']                    

            item = {
                "attributes": {
                    "carteiraid": carteiraid,
                    "mcc": None,
                    "nomeresponsavel": None,
                    "tipoalerta": company['USER_tipoalerta'],
                    "id": company['USER_id'],
                    "empresa": company['USER_empresa'],
                    "nomecontato": " ",
                    "cnpjcpf": None,
                    "segmento": None,
                    "faixatpv": None,
                    "endereco": company['USER_endereco'],
                    "numero": company['USER_numero'],
                    "bairro": company['USER_bairro'],
                    "cidade": company['USER_cidade'],
                    "estado": company['USER_estado'],
                    "complemento": " ",
                    "latitude": company['Shape'][1],
                    "longitude": company['Shape'][0],
                    "telefone": None,
                    "clientepagseguro": 0,
                    "cnae": " ",
                    "roteirizar": company['USER_roteirizar'],
                    "tipopessoa": " ",
                    "situacaocliente": " ",
                    "receitapresumida": 0,
                    "origemempresa": " ",
                    "maiorreceita": 0,
                    "datamaiorreceita": None,
                    "nomeexecutivo": company['nome'],
                    "polo": polo,
                    "carteira": carteira,
                    "origem": 0,
                    "cep": company['USER_cep'],
                    "datageocodificacao": utils.datetime_to_timestamp(self.route_generation_date),
                    "dataidentificacaocarteira": utils.datetime_to_timestamp(self.route_generation_date)
                },
                "geometry": {
                    "x": company['Shape'][0],
                    "y": company['Shape'][1],
                    "spatialReference": {
                        "wkid": 4326
                    }
                }
            }

            payload.append(item)

            if count % 1600 == 0 or len(companies) == count:
                featureids = self._deletion_features(ids)
                query_filter = "id in ({0})".format(', '.join(featureids))
                deleted_companies = feature_server.delete_feature_data(self.params['leads_feature_url'], query_filter)

                if 'success' in deleted_companies:
                    self.logger.info("Foram deletadas ({0}) empresas para atualização...".format(len(featureids)-1))

                    response = feature_server.post_feature_data(self.params['leads_feature_url'], payload)
                    if response[0]['success'] == False:
                        self.logger.info("Erro na publicação (%s/%s) empresas..." % (count, len(companies)))
                        self.logger.info(str(response[0]))
                    else:
                        self.logger.info("Foram publicadas (%s/%s) empresas..." % (count, len(companies)))

                else:
                    self.logger.info("Erro ao deletar empresas para atualização na geocodificação...")
                    self.logger.info(str(deleted_companies['error']))

                payload = []
                ids = []

    def _delete_old_companies_not_geocode_table(self, companies):        
        all_companies = companies['geocoded'] + companies['not_geocoded']
        count = 0
        ids = []
        for company in all_companies:
            count += 1
            ids.append(str(company['USER_id']))

            if count % 1000 == 0 or count == len(all_companies):
                query_filter = "id in (%s)" % (",".join(ids))
                feature_server.delete_feature_data(self.params['non_geocode_companies'], query_filter)
                ids = []
    
    def _sync_company_not_geocode_table(self, companies):
        self.logger.info("Atualização da tabela de leads que não foram geocodificados...")

        if len(companies) > 0:
            payload = []
            count = 0
            for company in companies:
                count = count + 1
                item = {
                    "attributes": {
                        "empresa": company['USER_empresa'],
                        "id": company['USER_id'],
                        "clientepagseguro": company['USER_clientepagseguro'],
                        "origem": company['USER_origem'],
                        "endereco": company['USER_endereco'],
                        "numero": company['USER_numero'],
                        "complemento": company['USER_complemento'],
                        "bairro": company['USER_bairro'],
                        "cidade": company['USER_cidade'],
                        "estado": company['USER_estado'],
                        "cep": company['USER_cep'],
                        "enderecocompleto": company['USER_enderecocompleto'],
                        "geocode_tipoendereco": company['StPreType'],
                        "geocode_endereco": company['StName'],
                        "geocode_numero": company['AddNum'],
                        "geocode_bairro": company['District'],
                        "geocode_cidade": company['City'],
                        "geocode_estado": company['RegionAbbr'],
                        "geocode_cep": company['Postal'],
                        "geocode_enderecocompleto": company['Match_addr'],
                        "geocode_longitude": company['Shape'][0],
                        "geocode_latitude": company['Shape'][1],
                        "geocode_status": company['Status'],
                        "geocode_score": company['Score'],
                        "datageocodificacao": utils.datetime_to_timestamp(self.route_generation_date),
                        "geocode_complemento": company['USER_complemento'],
                        "roteirizar": company['USER_roteirizar'],
                        "carteiraid": company['USER_carteiraid'],
                        "tipoalerta": company['USER_tipoalerta'],
                        "polo": company['USER_polo'],
                        "carteira": company['USER_carteira']
                    }
                }

                payload.append(item)

                if count % 1600 == 0 or len(companies) == count:
                    response = feature_server.post_feature_data(self.params['non_geocode_companies'], payload)
                    self.logger.info("Foram inseridas (%s/%s) empresas na tabela..." % (count, len(response)))
                    payload = []

    def _delete_rows_geocode_table(self):
        query_filter = "1 = 1"
        feature_server.delete_feature_data(self.params['geocode_companies'], query_filter)        

    def run(self):
        self.logger.info("Preparando para geocodificação de leads...")
        self._synchronize_leads_for_geocode()
        self._synchronize_work_areas()
        self._geocode_leads()
        self._identify_work_areas()

        companies = self._validate_publish()

        self._publish_new_leads(companies['geocoded'])
        self._delete_old_companies_not_geocode_table(companies)
        self._sync_company_not_geocode_table(companies['not_geocoded'])
        self._delete_rows_geocode_table()
