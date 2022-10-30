# -*- coding: utf-8 -*-
from patterns.singleton import Singleton
from esri import feature_server

WHERE_WORK_AREA_IS_NOT_NULL = "polo IS NOT NULL AND carteira IS NOT NULL AND inativo = 0" # AND id= 1159101

class WorkAreas(metaclass=Singleton):
    def __init__(self, logger, params):
        self.logger = logger
        self.params = params
        self.work_areas = []
        
    def get(self):
        if len(self.work_areas) == 0:
            self.work_areas = feature_server.get_feature_data(self.params['work_areas_feature_url'], WHERE_WORK_AREA_IS_NOT_NULL)
        return self.work_areas    