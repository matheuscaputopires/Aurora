import arcgis, requests, json
from arcgis.gis import GIS
from unittest import TestCase

featureUrl = 'https://pagsegurohml.img.com.br/server/rest/services/Hosted/Roteirizacao/FeatureServer/0/query'

gis = GIS("https://pagsegurohml.img.com.br/portal", "integracao", "dX34DFrsw7")
token = gis._con.token
#print(token)


payload = { 'token': token, 'where': '1=1', 'f': 'json', 'returnGeometry': 'true', 'outFields': '*' }
statusUrl =  { 'token': token }

r = requests.get(featureUrl, params=payload )
#print (r.text)

data = json.loads(r.text)
#print(type(data['features'])) 

for feature in data['features']:
    atributes_list = (feature['attributes'])
    geometry_list = (feature['geometry'])
    print(atributes_list.get('carteiraid'), atributes_list.get('nomecontato'))
    print(geometry_list.get('x'), geometry_list.get('y'))
    
class TestContract (TestCase):
    def test_verificar_status_endpoint_roteiros(self):
        request = requests.get(featureUrl, params=statusUrl)
        assert request.status_code == 200
        assert r.json() != []

    def test_verificar_lista_atributos_nao_vazia(self):
        assert atributes_list != []
