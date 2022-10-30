import os
from config import Config
import helper.utils as utils
from esri import feature_server
from service.base_route import BaseRoute
from esri.geodatabase import Geodatabase
from service.schedule import Schedule

class Company():
    def __init__(self, logger):
        self.logger = logger
        self.params = Config().get_params()
        self.geodatabase = Geodatabase(logger)
        self.base_route = BaseRoute(logger)
        self.schedule = Schedule(logger)

    def synchronize(self):

        self.logger.info("Sincronizando empresas...")

        ft_companies = os.path.join(self.geodatabase.get_path(), self.params['company_name'])

        self.geodatabase.copy_template_feature_to_temp_gdb(self.params['company_name'])

        schedules = feature_server.get_feature_data(self.params['schedules_feature_url'], self.schedule.condition_schedule(), distinct_values="empresaid", geometries=False)

        where = "roteirizar = 1"
        if len(schedules) > 0:
            companies_id = ""
            for index, schedule in enumerate(schedules):
                separator = "" if index == 0 else ","
                companies_id += "%s%s" % (separator, schedule['attributes']["empresaid"])

            where += " OR id IN (%s)" % (companies_id)

        companies = feature_server.get_feature_data(self.params['leads_feature_url'], where)
        executives = feature_server.get_feature_data(self.params['executive_feature_url'])

        self.logger.info("Empresas encontradas (%s) para condição (%s)" % (len(companies), where))
        for company in companies:
            del company['attributes']['objectid']
            del company['attributes']['globalid']
            company['attributes']['latitude'] = company['geometry']['y']
            company['attributes']['longitude'] = company['geometry']['x']

            executive_filtered = [item['attributes']['id'] for item in executives if item['attributes']['carteiraid'] == company['attributes']['carteiraid']]
            if len(executive_filtered) > 0:
                company['attributes']['executivoid'] = executive_filtered[0]

            company['attributes']['datamaiorreceita'] = utils.timestamp_to_datetime(company['attributes']['datamaiorreceita'])
            company['attributes']['attr_time'] = self.params['service_time_minutes']
            company['attributes']['DeliveryQuantity_1'] = 1 if company['attributes']['tipoalerta'] == None else None
            company['attributes']['DeliveryQuantity_2'] = 1 if company['attributes']['tipoalerta'] != None else None

        self.geodatabase.insert_data(companies, ft_companies, self.params['local_feature_fields'])
