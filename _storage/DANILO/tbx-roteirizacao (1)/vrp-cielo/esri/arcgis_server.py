import requests
import json

class ArcGISServer():
    def __init__(self, config):
        self.config = config    

    def generate_token(self):
        params = self.config.get_params()
        payload = { 'username': params['portal_username'], 'password': params['portal_password'], 'referer': self.config.get_url_ags(), 'f': 'json' }
        r = requests.post(self.config.get_url_generate_token(), data=payload)
        response = json.loads(r.text)
        token = response['token']
        return token

    def get_data(self, feature_url, feature_params):
        r = requests.get(url=feature_url, params=feature_params)
        return json.loads(r.text)

    def post_data(self, feature_url, payload):
        r = requests.post(url=feature_url, data=payload)
        response = json.loads(r.text)
        return response

    def delete_data(self, feature_url, payload):
        return self.post_data(feature_url, payload)