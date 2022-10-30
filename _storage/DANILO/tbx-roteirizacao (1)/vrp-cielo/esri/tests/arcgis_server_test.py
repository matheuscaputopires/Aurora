from unittest import TestCase
from mock import patch, MagicMock
from esri.arcgis_server import ArcGISServer
from config import Config
import json
class TestArcGISServer(TestCase):

    @patch('esri.arcgis_server.requests')
    def test_generate_token(self, mock_requests):

        TOKEN_FAKE = {'token': '12345'}
        response_fake = ResponseFake(json.dumps(TOKEN_FAKE))
        mock_requests.post = MagicMock(return_value=response_fake)

        config_fake = MagicMock(return_value=Config())
        arcgisserver = ArcGISServer(config_fake)

        PARAMS_FAKE = {
                        "portal_username": "username",
                        "portal_password": "password",
                        "ags_url": "https://link-server",
                        "generate_token_url": "/generate-token"
                }
        arcgisserver.config.get_params = MagicMock(return_value=PARAMS_FAKE)

        token = arcgisserver.generate_token()
        self.assertEqual(token, TOKEN_FAKE['token'])

    @patch('esri.arcgis_server.requests')
    def test_get_data(self, mock_requests):        
        
        text_fake = {'features': [{'id': 1}]}
        response_fake = ResponseFake(json.dumps(text_fake))
        mock_requests.get = MagicMock(return_value=response_fake)
        feature_url = 'https://arcgis-server/feature/0'
        params = '1=1'
        
        config_fake = MagicMock(return_value=Config())
        arcgisserver = ArcGISServer(config_fake)        
        
        result = arcgisserver.get_data(feature_url, params)

        result_expected = text_fake
        self.assertEqual(result, result_expected)
    
    def _setup_mock_post_data(self, mock_requests):        
        json_str_fake = {'features': [{'id': 1}]}
        response_fake = ResponseFake(json.dumps(json_str_fake))
        mock_requests.post = MagicMock(return_value=response_fake)
    
    @patch('esri.arcgis_server.requests')
    def test_post_data(self, mock_requests):
        self._setup_mock_post_data(mock_requests)             
        TOKEN_FAKE = "123456789"
        feature_url = 'https://arcgis-server/feature/0'
        payload = { 'token': TOKEN_FAKE, 'where': '1=1', 'f': 'json' }

        config_fake = MagicMock(return_value=Config())
        arcgisserver = ArcGISServer(config_fake)

        result = arcgisserver.post_data(feature_url, payload)
        result_expected = {'features': [{'id': 1}]}
        self.assertEqual(result, result_expected)

    @patch('esri.arcgis_server.requests')
    def test_delete_data(self, mock_requests):        
        self._setup_mock_post_data(mock_requests)        
        feature_url = 'https://arcgis-server/feature/0'
        payload = { 'token': '123456', 'where': '1=1', 'f': 'json' }

        config_fake = MagicMock(return_value=Config())
        arcgisserver = ArcGISServer(config_fake)        

        result = arcgisserver.delete_data(feature_url, payload)
        self.assertEqual(result, {'features': [{'id': 1}]})

class HttpFake:
    def request(self, feature, method, headers, body):
        return None    
class ContentFake():
    def decode(self):
        return None

class ResponseFake:
    def __init__(self, text):
        self.text = text
    def text(self):
        return self.text
class ConnFake:
    def __init__(self, token):        
        self._con = TokenFake(token)

class TokenFake:
    def __init__(self, token):
        self.token = token