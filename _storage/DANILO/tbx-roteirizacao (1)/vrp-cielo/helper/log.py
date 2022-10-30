# -*- coding: utf-8 -*-
import os
import time
import logging
from datetime import datetime
from config import Config

class Log:
    def __init__(self):
        self.logger = None
        self.path_log = None
        self.config = Config()
        self._arcpy = __import__("arcpy") if self.config.get_env_run() != "test" else None
        
    def setup_log(self):
        path_main = self.config.get_folder_main()
        self.path_log = os.path.join(path_main, 'logs')
        PROCESS_NAME = 'tbx-roterizacao'
        now = datetime.now()
        FILE_NAME = '%s-%s-%s-%s-%s-%s-%s.log' % (PROCESS_NAME, now.year, now.month, now.day, now.hour, now.minute, now.second)
        FORMAT_LOG = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        isdir = os.path.isdir(self.path_log)
        if isdir == False:
            os.mkdir(self.path_log)
        logging.basicConfig(filename=os.path.join(self.path_log, FILE_NAME), format=FORMAT_LOG, level=logging.INFO)

        # set up logging to console 
        console = logging.StreamHandler() 
        console.setLevel(logging.DEBUG) 
        # set a format which is simpler for console use 
        formatter = logging.Formatter(FORMAT_LOG)
        console.setFormatter(formatter) 
        # add the handler to the root logger 
        logging.getLogger('').addHandler(console) 
        logger = logging.getLogger(PROCESS_NAME)
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