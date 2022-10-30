# -*- coding: utf-8 -*-
import os
import time
import logging
import helper.utils as utils
from datetime import datetime
from config import Config

class Log:
    def __init__(self):
        self.logger = None
        self.path_log = None
        self.config = Config()
        self._arcpy = __import__("arcpy") if self.config.get_env() != "test" else None
        self.process_name = self.config.process_name
        self.process_full_name = None    

    def setup_log(self):
        self.path_log = os.path.join(self.config.get_job_process_folder(), "log")
        now = datetime.now()
        self.process_full_name = '%s-%s-%s-%s-%s-%s-%s' % (self.process_name, now.year, now.month, now.day, now.hour, now.minute, now.second)
        FILE_NAME = '%s.log' % (self.process_full_name)
        FORMAT_LOG = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        utils.create_folder(self.path_log)
        logging.basicConfig(filename=os.path.join(self.path_log, FILE_NAME), format=FORMAT_LOG, level=logging.INFO)

        # set up logging to console 
        console = logging.StreamHandler() 
        console.setLevel(logging.DEBUG) 
        # set a format which is simpler for console use 
        formatter = logging.Formatter(FORMAT_LOG)
        console.setFormatter(formatter) 
        # add the handler to the root logger 
        logging.getLogger('').addHandler(console) 
        logger = logging.getLogger(self.process_name)
        self.logger = logger

    def error(self, message):
        self._arcpy.AddError(message)
        self.logger.error(message)

    def info(self, message):
        self._arcpy.AddMessage(message)
        self.logger.info(message)

    def finish(self, message):
        self.info(message)
        self._clear_log_files_older_7_days()

    def _clear_log_files_older_7_days(self):
        age = 7
        age = int(age)*86400
    
        for file in os.listdir(self.path_log):
            now = time.time()
            filepath = os.path.join(self.path_log, file)
            modified = os.stat(filepath).st_mtime
            if modified < now - age and os.path.isfile(filepath):
                os.remove(filepath)
                self.info("deleted file: %s (%s)" % (file, modified))