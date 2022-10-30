import requests
import json
from config import Config

def generate_token():
    params = Config().get_params()
    payload = { 'username': params['portal_username'], 'password': params['portal_password'], 'referer': params['ags_url'], 'f': 'json' }
    r = requests.post(params['generate_token_url'], data=payload)
    response = json.loads(r.text)
    token = response['token']
    return token

def get_data(feature_url, feature_params):
    r = requests.get(url=feature_url, params=feature_params)
    return json.loads(r.text)

def post_data(feature_url, payload):
    r = requests.post(url=feature_url, data=payload)
    response = json.loads(r.text)
    return response

def delete_data(feature_url, payload):
    return post_data(feature_url, payload)