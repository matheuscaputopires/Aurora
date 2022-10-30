# -*- coding: utf-8 -*-
from patterns.singleton import Singleton
from helper.log import Log
from helper.mail import Mail
from config import Config
from esri import feature_server

class Notification(metaclass=Singleton):
    process_name: str = None
    params: str = None
    total_work_areas: int = 0
    total_geocode_with_route: int = 0
    total_companies: int = 0
    total_companies_router: int = 0
    total_routes_generated: int = 0
    total_companies_non_routes: int = 0
    total_companies_non_geocoded: int = 0
    looger: Log = None

    def __init__(self, process_name: str, params: str, logger: Log) -> None:
        self.process_name = process_name
        self.params = params
        self.logger = logger

    def _get_name_process(self, action):
        return 'Processo: %s - %s' % (self.process_name, action)

    def _get_values_str(self):
        return {
            "work_area": "Carteiras: " + str(self.total_work_areas),
            "geocode_with_route": "Empresas à geocodificar para roteirizar: " + str(self.total_geocode_with_route),
            "total_companies": "Empresas à roteirizar: " + str(self.total_companies),
            "total_companies_router": "Total de empresas à roteirizar: " + str(self.total_companies_router),
            "total_routes_generated": "Total de empresas roteirizadas: " + str(self.total_routes_generated),
            "total_companies_non_routes": "Total de empresas não roteirizadas: " + str(self.total_companies_non_routes),
            "total_companies_non_geocoded": "Total de empresas não geocodificadas: " + str(self.total_companies_non_geocoded)
        }

    def _body_str(self):
        values_str = self._get_values_str()
        html = """\
            <p>Olá,<br><br>
            Abaixo detalhes da execução.<br><br>
            <strong>Resumo dos dados:</strong> <br>
            """+values_str['work_area']+""" <br>
            """+values_str['geocode_with_route']+""" <br>
            """+values_str['total_companies']+""" <br>
            _____________________________+ <br>
            = """+values_str['total_companies_router']+""" <br>
            </p>            
        """
        return html               

    def _start_html_str(self):        
        html = """\
        <html>
        <body>
            """ + self._body_str() + """
        </body>
        </html>
        """
        return html   

    def _finish_html_str(self):
        values_str = self._get_values_str()
        finish_body = """\
            <br>
            <strong>Resultado:</strong> <br>
            """+values_str['total_routes_generated']+""" <br>
            """+values_str['total_companies_non_routes']+""" <br>
            """+values_str['total_companies_non_geocoded']+""" <br>
        """

        html = """\
        <html>
        <body>
            """ + self._body_str() + """
            """ + finish_body + """
        </body>
        </html>
        """
        return html           

    def _start_text_str(self):
        values_str = self._get_values_str()
        text = """\
            Olá,
            Abaixo detalhes da execução.
            Resumo dos dados:
            """+values_str['work_area']+"""
            """+values_str['geocode_with_route']+"""
            """+values_str['total_companies']+"""
            _____________________________+
            ="""+values_str['total_companies_router']+"""
        """
        return text                
    
    def _finish_text_str(self):
        start_text = self._start_text_str()
        
        values_str = self._get_values_str()
        finish_str = """\
            --------------------
            Resultado:
            """+values_str['total_routes_generated']+"""
            """+values_str['total_companies_non_routes']+"""
            """+values_str['total_companies_non_geocoded']+"""
        """
        return start_text + finish_str
        

    def _set_start_values(self):
        self.total_work_areas = feature_server.count_feature_data(self.params['work_areas_feature_url'], "polo IS NOT NULL AND carteira IS NOT NULL AND inativo = 0")
        self.total_geocode_with_route = feature_server.count_feature_data(self.params['geocode_companies'], "roteirizar <> 0")
        self.total_companies = feature_server.count_feature_data(self.params['leads_feature_url'], "roteirizar <> 0")

        self.total_companies_router = self.total_geocode_with_route + self.total_companies

    def _env_is_not_prod(self):
        return self.params['environment'] != 'production'
    
    def start_process(self):

        if self._env_is_not_prod():
            return

        self._set_start_values()

        # Create the plain-text and HTML version of your message
        text = self._start_text_str()
        html = self._start_html_str()

        mail = Mail()
        subject = self._get_name_process("Início da Execução")
        mail.send(text, html, subject)

    def _set_finish_values(self):
        date = Config().route_generation_date
        date_created = '%s-%s-%s' % (date.year, date.month, date.day)
        self.total_routes_generated = feature_server.count_feature_data(self.params['routes_feature_url'], "datacriacao BETWEEN Date '%s 00:00:00' AND Date '%s 23:59:59'" % (date_created, date_created))
        self.total_companies_non_routes = feature_server.count_feature_data(self.params['non_route_companies_feature_url'], "datageracaorota BETWEEN Date '%s 00:00:00' AND Date '%s 23:59:59'" % (date_created, date_created))
        self.total_companies_non_geocoded = feature_server.count_feature_data(self.params['non_geocode_companies'], "datageocodificacao BETWEEN Date '%s 00:00:00' AND Date '%s 23:59:59'" % (date_created, date_created))

        self.logger.info("query total_routes_generated:  datacriacao BETWEEN Date '%s 00:00:00' AND Date '%s 23:59:59'" % (date_created, date_created))
        self.logger.info("query total_companies_non_routes: datageracaorota BETWEEN Date '%s 00:00:00' AND Date '%s 23:59:59'" % (date_created, date_created))
        self.logger.info("query total_companies_non_geocoded: datageocodificacao BETWEEN Date '%s 00:00:00' AND Date '%s 23:59:59'" % (date_created, date_created))
    
    def finish_process(self):

        if self._env_is_not_prod():
            return

        self._set_finish_values()
        
        text = self._finish_text_str()
        html = self._finish_html_str()

        mail = Mail()
        subject = self._get_name_process("Fim da Execução")
        mail.send(text, html, subject)

    def error_process(self, message):

        if self._env_is_not_prod():
            return

        text = """\
            Olá,
            Houve um erro no processo de geração de roteiros.
            Erro para análise:
            """+message+"""
        """
        html = """\
        <html>
        <body>
            <p>
                Olá, <br><br>
                Houve um erro no processo de geração de roteiros.<br>
                Erro para análise: <br>
                """ + message + """
            </p>
        </body>
        </html>
        """

        mail = Mail()
        subject = self._get_name_process("Erro na Execução")
        mail.send(text, html, subject)
    
    def time_check_in_out_long(self, message):
    
        if self._env_is_not_prod():
            return

        text = """\
            Olá,
            O tempo de execução do Check-In/Out está levando mais tempo do que o esperado.
            Tempo:
            """+message+"""
        """
        html = """\
        <html>
        <body>
            <p>
                Olá, <br><br>
                O tempo de execução do Check-In/Out está levando mais tempo do que o esperado.<br>
                Tempo: <br>
                """ + message + """
            </p>
        </body>
        </html>
        """

        mail = Mail()
        subject = self._get_name_process("Tempo de Execução")
        mail.send(text, html, subject)  

