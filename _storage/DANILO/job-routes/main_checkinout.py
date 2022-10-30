# -*- coding: utf-8 -*-
import os
import time
import json
import datetime

from config import Config
from helper.log import Log
from service.notification import Notification

from service.checkinout import Checkinout

class GeneralError(Exception):
    pass

class MainCheckInOut():
    def __init__(self):
        self.config = Config('checkinout')
        self.params = self.config.get_params()
        self.logger = Log()
        self.logger.setup_log()
        self.limit_execution = 4
        self.path_execution_control_file = os.path.join(self.config.get_job_process_folder(), "check-in-out-execute.json")
    
    def _verify_execute(self):
        try:            
            with open(self.path_execution_control_file) as json_file:
                data = json.load(json_file)
                is_running = data['execute']
                if is_running:
                    time_start = datetime.datetime.strptime(data['time_execute'], "%Y-%m-%d %H:%M:%S").replace(microsecond=0)
                    finish_execute = time_start + datetime.timedelta(hours=self.limit_execution)
                    if datetime.datetime.now().time() > finish_execute.time():
                        notification = Notification(self.logger.process_full_name, self.params, self.logger)
                        message = "Iniciado: %s e não finalizou em um prazo de %sh ainda!" % (str(time_start), str(self.limit_execution))
                        notification.time_check_in_out_long(message)
                else:
                    self._write_file_execute(True)

                return is_running 
        except:
            self._write_file_execute(True)
            return False

    def _write_file_execute(self, value):
        with open(self.path_execution_control_file, 'w+', encoding='utf-8') as file:
            values = {
                "execute": value,
                "time_execute": str(datetime.datetime.now().replace(microsecond=0))
            }
            json.dump(values, file, ensure_ascii=False, indent=4)

    def execute(self):
        try:
            if self._verify_execute():
                self.logger.info("Já existe um processo em execução.")
                return False

            self.logger.info('Iniciando processamento...')

            start_time = time.time()

            checkinout = Checkinout(self.logger)
            checkinout.execute()

            self._write_file_execute(False)

            self.logger.info("Job concluído com sucesso")
            self.logger.info("--- %s segundos ---" % (time.time() - start_time))
                
        except Exception as e:
            import traceback, sys
            traceback_text = "".join([x for x in traceback.format_exception(*sys.exc_info()) if x])
            self.logger.error(traceback_text)
            Notification(self.logger.process_full_name, self.params, self.logger).error_process(traceback_text)
            self._write_file_execute(False)
        
        finally:
            self.logger.finish('Fim de processamento')            

if __name__ == "__main__":
        MainCheckInOut().execute()        