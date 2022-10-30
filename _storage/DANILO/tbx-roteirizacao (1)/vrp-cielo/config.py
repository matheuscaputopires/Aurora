# -*- coding: utf-8 -*-
import os
import json

ENV_DICT = {
    'Homologação': 'staging',
    'Produção': 'production'    
}

class Config():
    def __init__(self):
        self.config_file = None
        self.path_network = None

    def get_folder_main(self):
        return os.path.dirname(os.path.abspath(__file__))

    def get_folder_temp(self):
        return os.path.join(self.get_folder_main(), "temp")

    def get_env(self, env):
        return 'develop' if env == None else ENV_DICT[env]

    def get_env_run(self):
        return os.getenv('TbxLoadWorkArea', 'execute')
        
    def get_params(self, env=None, portal_username=None, portal_password=None):
        if self.config_file == None:
            dirpath = self.get_folder_main()
            environment = self.get_env(env)
            config_filename = os.path.join(dirpath, 'config.json')
            CONF = None
            with open(config_filename) as json_file:
                CONF = json.load(json_file)        
            
            self.config_file = CONF[environment]
            self.config_file['portal_username'] = portal_username
            self.config_file['portal_password'] = portal_password

        return self.config_file
    
    def get_url_workarea(self):
        return self.config_file['url_base'] + self.config_file['feature_url'] + self.config_file['work_areas_url']

    def get_url_executive(self):
        return self.config_file['url_base'] + self.config_file['feature_url'] + self.config_file['executive_url']        

    def get_url_ags(self):
        return self.config_file['url_base'] + self.config_file['ags_url']

    def get_url_generate_token(self):
        return self.config_file['url_base'] + self.config_file['generate_token_url']

    def get_url_user_hierarchies(self):
        return self.config_file['url_base'] + self.config_file['user_hierarchies']        