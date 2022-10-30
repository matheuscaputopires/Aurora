# -*- coding: utf-8 -*-
import time

from config import Config
from helper.log import Log
from service.notification import Notification

from service.orchestrator import Orchestrator

class GeneralError(Exception):
    pass

class Main():
    def __init__(self):
        self.params = Config("routes").get_params()

    def execute(self):     

        logger = Log()
        logger.setup_log()

        try:
            logger.info('Iniciando processamento...') 

            start_time = time.time()

            orchestrator = Orchestrator(logger)
            orchestrator.execute()

            logger.info("Job concluído com sucesso")
            logger.info("--- %s segundos ---" % (time.time() - start_time))

        except Exception as e:
            import traceback, sys
            traceback_text = "".join([x for x in traceback.format_exception(*sys.exc_info()) if x])
            logger.error(traceback_text)
            Notification(logger.process_full_name, self.params, logger).error_process(traceback_text)
        
        finally:
            logger.finish('Fim de processamento')            

if __name__ == "__main__":
        Main().execute()