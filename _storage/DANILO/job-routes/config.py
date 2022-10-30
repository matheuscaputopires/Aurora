# -*- coding: utf-8 -*-
from patterns.singleton import Singleton
import os
import json
from datetime import datetime
import helper.utils as utils

class Config(metaclass=Singleton):
    name_temp: str = None
    route_generation_date: datetime = None
    root_process_folder: str = None

    def __init__(self, process_name: str) -> None:
        self.temp_name = "temp_" + process_name
        self.process_name = "job-" + process_name
        self.route_generation_date = datetime.now()
        self.root_process_folder = os.path.join("c:\\", "JobPagSeguro_Process")

    def get_folder_main(self):
        return os.path.dirname(os.path.abspath(__file__))

    def get_folder_temp(self):
        return os.path.join(self.get_job_process_folder(), self.temp_name)

    def get_folder_template(self):
        return os.path.join(self.get_folder_main(), 'template')

    def get_env(self):
        return os.getenv('JOBRoute', 'develop')

    def get_params(self):
        dirpath = self.get_folder_main()
        environment = self.get_env()
        config_filename = os.path.join(dirpath, 'config.json')
        CONF = None
        with open(config_filename) as json_file:
            CONF = json.load(json_file)        

        CONF[environment]['environment'] = environment

        return CONF[environment]

    def create_folder_temp(self):
        folder_temp = self.get_folder_temp()
        utils.delete_if_exists(folder_temp)
        utils.create_folder(folder_temp)

    def get_job_process_folder(self):
        folder_process = os.path.join(self.root_process_folder, self.process_name)
        folder_process_env = os.path.join(folder_process, self.get_env())
        utils.create_folder(folder_process_env)
        return folder_process_env