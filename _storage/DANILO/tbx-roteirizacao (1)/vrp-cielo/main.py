# -*- coding: utf-8 -*-
import sys
import time
from config import Config
from helper.log import Log
from service.orchestrator import Orchestrator

class Main():
    def __init__(self, logger):
        self.logger = logger
        self.config = Config()
        self._arcpy = __import__("arcpy") if self.config.get_env_run() != "test" else None
        self.debug = False

    def _verify_license_network(self):
        #Verifique a licença do Network Analyst, se disponível. Falha se a licença do Network Analyst não estiver disponível.
        if self._arcpy.CheckExtension("network") == "Available":
            self._arcpy.CheckOutExtension("network")
        else:
            raise self._arcpy.ExecuteError("Network Analyst Extension license is not available.")
    
    def execute(self):

        self.logger.info('Toolbox version 2.3') 
        self.logger.info('Iniciando...')

        param_xlsx = None
        param_path_network = None
        param_saida = None
        param_number_day_route = None
        param_number_visit_per_day = None
        param_continue_process = False

        start_time = time.time()
        
        self._verify_license_network()

        if self.debug:
            param_xlsx = r"D:\Temp\BASE_11072022_IZAK.xlsx"
            param_path_network = r"D:\StreetMapPremium\LA_2021\FGDB\StreetMap_Data\LatinAmerica.gdb\Routing\Routing_ND"
            param_saida = r"D:\Profile\OneDrive - Imagem Geosistemas e Comercio LTDA\Documentos\ArcGIS\Projects\CIELO-TBXGeocode"
            param_number_day_route = 5
            param_number_visit_per_day = 4
            param_continue_process = False
        else:
            # param_xlsx = self._arcpy.GetParameterAsText(0)
            # param_path_network = self._arcpy.GetParameterAsText(1)
            # param_saida = self._arcpy.GetParameterAsText(2)
            # param_number_day_route = self._arcpy.GetParameterAsText(3)
            # param_number_visit_per_day = self._arcpy.GetParameterAsText(4)
            
            param_xlsx = sys.argv[1]
            param_path_network = sys.argv[2] if sys.argv[2] != '0' else None
            param_saida = sys.argv[3]
            param_number_day_route = sys.argv[4]
            param_number_visit_per_day = sys.argv[5]

            if sys.argv[6] == '1':
                param_continue_process = True
            else:
                param_continue_process = False

        if param_path_network != None:
            self.config.path_network = param_path_network

        if param_xlsx == None or param_saida == None or param_number_day_route == None or param_number_visit_per_day == None:
            self.logger.error("Preencha os campos corretamente!")
            return

        Orchestrator(self.logger, self.config, param_continue_process).execute(param_xlsx, param_saida, param_number_day_route, param_number_visit_per_day)

        self.logger.info("Processamento concluído com sucesso")
        self.logger.info("--- %s segundos ---" % (time.time() - start_time))
        

if __name__ == "__main__":
    try:
        logger = Log()
        logger.setup_log()
        params = Main(logger).execute()

    except Exception as e:
        import traceback, sys
        traceback_text = "".join([x for x in traceback.format_exception(*sys.exc_info()) if x])
        logger.error(traceback_text)
    
    finally:
        logger.finish('Fim de processamento')