from esri import feature_server
import json
import csv
from datetime import datetime
import helper.utils as utils
from sklearn.cluster import kmeans_plusplus
from config import Config

config = Config("routes")

import arcpy
#arcpy.env.workspace = r"C:\Users\dramalho\Imagem Geosistemas e Comercio LTDA\Team site - PagSeguro\Documentos Recebidos\OneDrive_2021-11-04\POLOS_PILOTO_ROTAS_08112021 (1).gdb"

def load_carteiras():
    
    #validação de código único para carteiras
    count_distinct = 0
    with arcpy.da.SearchCursor('polos', ["CODIGO_CARTEIRA"], sql_clause=("DISTINCT CODIGO_CARTEIRA", None)) as cursor:
        for row in cursor:
            count_distinct = count_distinct + 1

    count_feature = arcpy.GetCount_management('polos')
    if int(count_feature[0]) != count_distinct:
        raise 'Existe código duplicado na feature carteiras'


    hierarquias = feature_server.get_feature_data('https://pagsegurohml.img.com.br/server/rest/services/Roteirizacao/Hierarquia_Usuario/MapServer/2')
    
    payload = []
    with arcpy.da.SearchCursor("polos", ["POLO", "CARTEIRA", "CENTRO_DE_CUSTO", "CODIGO_CARTEIRA", "SHAPE@JSON"], spatial_reference=arcpy.SpatialReference(3857)) as cursor:
        for row in cursor:
            polo = row[0]
            carteira = row[1]
            centro_custo = row[2]
            codigo_carteira = row[3]
            geometry = row[4]

            geometry = json.loads(geometry)
            if 'hasZ' in geometry:
                del geometry['hasZ']
            if 'hasM' in geometry:
                del geometry['hasM']

            hierarquia_filtered = [i['attributes'] for i in hierarquias if str(i['attributes']['carteiraid']) == str(codigo_carteira)]
            nome_executivo = None
            if len(hierarquia_filtered) > 0:
                nome_executivo = hierarquia_filtered[0]['nome']

            item = {
                    "attributes": {
                    "carteira": carteira,
                    "polo": polo,
                    "centro_de_custo": centro_custo,
                    "id": int(codigo_carteira),
                    "nome": nome_executivo if nome_executivo != None else polo + ' - ' + carteira,
                    "modoviagem": 'Walking',
                    "distanciatotalroteiro": 5
                },
                    "geometry": geometry
            }
            payload.append(item)

    feature_url_carteiras = 'https://pagsegurohml.img.com.br/server/rest/services/Roteirizacao/RoteirizacaoPagSeguroDB/FeatureServer/3'
    result = feature_server.post_feature_data(feature_url_carteiras, payload)
    print(result)

def load_executivos():
        
    arcpy.management.FeatureToPoint("polos", "executive", "INSIDE")

    hierarquias = feature_server.get_feature_data('https://pagsegurohml.img.com.br/server/rest/services/Roteirizacao/Hierarquia_Usuario/MapServer/2')
    
    payload = []
    with arcpy.da.SearchCursor("executive", ["POLO", "CARTEIRA", "CODIGO_CARTEIRA", "SHAPE@JSON"], spatial_reference=arcpy.SpatialReference(3857)) as cursor:
        for row in cursor:
            polo = row[0]
            carteira = row[1]
            codigo_carteira = int(row[2])
            geometry = row[3]
            
            geometry = json.loads(geometry)
            #if 'z' in geometry:
                #del geometry['z']
            if 'm' in geometry:
                del geometry['m']

            hierarquia_filtered = [i['attributes'] for i in hierarquias if str(i['attributes']['carteiraid']) == str(codigo_carteira)]
            nome_usuario = None
            nome_executivo = None
            if len(hierarquia_filtered) > 0:
                nome_usuario = hierarquia_filtered[0]['usuario']
                nome_executivo = hierarquia_filtered[0]['nome']

            item = {
                    "attributes": {
                        "id": codigo_carteira,
                        "nome": nome_executivo if nome_executivo != None else polo + ' - ' + carteira,
                        "telefone": None,
                        "carteiraid": codigo_carteira,
                        "nomecarteira": carteira,
                        "nomeusuarioexecutivo": nome_usuario
                },
                    "geometry": geometry
            }
            payload.append(item)

    #feature_url_carteiras = 'https://pagsegurohml.img.com.br/server/rest/services/Roteirizacao/RoteirizacaoPagSeguroDB/FeatureServer/5'
    feature_url_carteiras = 'https://pagsegurohml.img.com.br/server/rest/services/Roteirizacao/RoteirizacaoPagSeguroDB/FeatureServer/5'
    result = feature_server.post_feature_data(feature_url_carteiras, payload)
    print(result)

def load_empresas():
    
    payload = []
    feature_url = 'https://pagsegurohml.img.com.br/server/rest/services/Roteirizacao/RoteirizacaoPagSeguroDB/FeatureServer/0'
    count = 0
    total = int(arcpy.management.GetCount("leads")[0])

    columns =  ["ID", "ADDRESSNAME", "ADDRESSNUMBER", "ADDRESSCOMPLEMENT", "CEP", "CITY", "DISTRICT", "LATITUDE", "LONGITUDE", "POLO", "CODIGO_CARTEIRA", "SHAPE@JSON", "STATE", "ALERTTYPE"]
    #columns =  ["id", "endereco", "numero", "complemento", "cep", "cidade", "bairro", "latitude", "longitude", "polo", "carteiraid", "SHAPE@JSON"]

    # companies = feature_server.get_feature_data(feature_url, geometries=False)
    # companies_dict = {}
    # for company in companies:
    #     companies_dict[str(company['attributes']['id'])] = company['attributes']    

    with arcpy.da.SearchCursor(
        "leads", 
        columns, 
        #where_clause="id > 51000",
        sql_clause=(None, "ORDER BY id ASC"),
        spatial_reference=arcpy.SpatialReference(3857)) as cursor:
        for row in cursor:
            count = count + 1
            id = int(row[0])
            endereco = row[1]
            numero = row[2]
            complemento = row[3]
            cep = row[4]
            cidade = row[5]
            bairro = row[6]
            latitude = row[7]
            longitude = row[8]
            polo = row[9]
            carteira_id = int(row[10])
            geometry = row[11]
            estado = row[12] 
            alerta = row[13] 
            
            geometry = json.loads(geometry)
            #del geometry['z']
            #del geometry['m']

            if 'm' in geometry:
                del geometry['m']

            if 'z' in geometry:
                del geometry['z']                

            try:
                numero_param = str(int(numero)) if numero != None else " "
            except:
                numero_param = numero

            item = {
                    "attributes": {
                        "carteiraid": carteira_id,
                        "mcc": None,
                        "nomeresponsavel": None,
                        "tipoalerta": alerta,
                        "id": id,
                        "empresa": "Empresa " + str(id),
                        "nomecontato": " ",
                        "cnpjcpf": None,
                        "segmento": None,
                        "faixatpv": None,
                        "endereco": str(endereco)[:255],
                        "numero": numero_param,
                        "bairro": bairro,
                        "cidade": cidade,
                        "estado": estado,
                        "complemento": str(complemento)[:20] if complemento != None and complemento != '<Null>' else " ",
                        "latitude": latitude,
                        "longitude": longitude,
                        "telefone": None,
                        "clientepagseguro": 0,
                        "cnae": " ",
                        "roteirizar": 1,
                        "tipopessoa": "PJ",
                        "situacaocliente":  " ",
                        "receitapresumida": 0,
                        "origemempresa": " ",
                        "maiorreceita": 0,
                        "datamaiorreceita": None,
                        "nomeexecutivo": " ",
                        "polo": polo,
                        "carteira": " ",
                        "origem": 0,
                        "cep": cep,
                        "datageocodificacao": None
                        },
                    "geometry": geometry
            }
            payload.append(item)

            if count % 1000 == 0 or total == count:
                print('Salvando (%s/%s)' % (count, total))

            #if str(id) in companies_dict == False:
                result = feature_server.post_feature_data(feature_url, payload)
                print(result)
                if result[0]['success'] == False:
                    print(result)

                payload = []

def load_gecodificacao_empresas():
    import arcpy
    arcpy.env.workspace = r"D:\Profile\Imagem Geosistemas e Comércio LTDA\SQUAD - TELECOM NEGOCIOS - PagSeguro\Documentos Recebidos\Teste_Motor_Roteirizacao_Imagem\Teste_Motor_Roteirizacao_Imagem\Teste_Motor_Roteirizacao_Imagem.gdb"
    payload = []
    feature_url = 'https://pagsegurohml.img.com.br/server/rest/services/Hosted/BKORoteirizacaoDev/FeatureServer/10'
    count = 0
    total = int(arcpy.management.GetCount("BASE_POLOS_ROTAS08062021_ExcelToTable")[0])
    with arcpy.da.SearchCursor(
        "BASE_POLOS_ROTAS08062021_ExcelToTable", 
        ["ID_UNICO", "ADDRESSNAME", "ADDRESSNUMBER", "ADDRESSCOMPLEMENT", "CEP", "CITY", "DISTRICT",  "UF"]) as cursor:
        for row in cursor:
            count = count + 1
            id = int(row[0])
            endereco = row[1]
            numero = row[2]
            complemento = row[3]
            cep = row[4]
            cidade = row[5]
            bairro = row[6]
            estado = row[7]

            item = {
                    "attributes": {
                        "id": id,
                        "empresa": "Empresa " + str(id),
                        "endereco": endereco,
                        "numero": str(numero) if numero != None else " ",
                        "bairro": bairro,
                        "cidade": cidade,
                        "estado": estado,
                        "complemento": complemento[:20] if complemento != None else " ",
                        "clientepagseguro": 0,
                        "origem": 0,
                        "cep": cep,
                        "datageocodificacao": None
                        }
            }
            payload.append(item)

            if count % 800 == 0 or total == count:
                print('Salvando (%s/%s)' % (count, total))
                result = feature_server.post_feature_data(feature_url, payload)
                if result[0]['success'] == False:
                    print(result)
                payload = []

def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp / 1000) if timestamp != None and timestamp > 0 else datetime(1976, 1, 1, 0, 0, 0)

def complete_data():

    path_gdb = r"C:\Users\dramalho\Imagem Geosistemas e Comercio LTDA\Team site - PagSeguro\Documentos Recebidos\OneDrive_2021-11-04\RoteirosVRP05112021.gdb"
    arcpy.env.workspace = path_gdb
    
    arcpy.management.Project("Roteiros_Temp", path_gdb+ "\\Roteiros", 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]', None, 'PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],UNIT["Meter",1.0]]', "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
    
    arcpy.AddField_management("Roteiros", "sequencia15", "LONG", field_alias="Sequência 15", field_is_nullable="NULLABLE")
    arcpy.AddField_management("Roteiros", "sequenciacarteira", "LONG", field_alias="Sequência Carteira", field_is_nullable="NULLABLE")
    arcpy.AddField_management("Roteiros", "latitude", "DOUBLE", field_alias="Latitude", field_is_nullable="NULLABLE")
    arcpy.AddField_management("Roteiros", "longitude", "DOUBLE", field_alias="Longitude", field_is_nullable="NULLABLE")

    arcpy.AddField_management("Roteiros", "latitudeText", "TEXT", field_alias="latitudeText", field_is_nullable="NULLABLE")
    arcpy.AddField_management("Roteiros", "longitudeText", "TEXT", field_alias="longitudeText", field_is_nullable="NULLABLE")


    arcpy.management.CalculateGeometryAttributes("Roteiros", "latitudeText POINT_Y;longitudeText POINT_X", '', '', None, "DD")

    arcpy.management.CalculateField("Roteiros", "latitudeText", "!latitudeText!.replace('.',',')", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("Roteiros", "longitudeText", "!longitudeText!.replace('.',',')", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

    arcpy.management.CalculateField("Roteiros", "latitude", "!latitudeText!", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("Roteiros", "longitude", "!longitudeText!", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

    arcpy.DeleteField_management("Roteiros", ["latitudeText", "longitudeText"])

    arcpy.management.DeleteFeatures("Roteiros_Temp")

    #arcpy.management.CalculateGeometryAttributes("Roteiros", "latitude POINT_Y;longitude POINT_X", '', '', None, "DD")
    #arcpy.management.CalculateGeometryAttributes("Roteiros", "latitude POINT_Y;longitude POINT_X", '', '', 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]', "DD")
    
    update_rows = []
    count15 = 0
    count_carteira = 0
    carteira_id_loop = None
    last_dataprogramada = None
    with arcpy.da.SearchCursor("Roteiros", ["OBJECTID", "executivoid", "sequencia", "dataprogramada"], sql_clause=(None, "ORDER BY executivoid ASC, dataprogramada ASC, sequencia ASC")) as cursor:
        for row in cursor:
            objectid = row[0]
            executivoid = row[1]
            sequencia = row[2]
            dataprogramada = row[3]

            count15 = count15 + 1
            #quebra de 15 para ROUTE
            # if count15 > 15:
            #    count15 = 1
            
            #quebra de 15 VRP
            if last_dataprogramada == None:
                last_dataprogramada = dataprogramada

            dt_programada_format = '%s/%s/%s' % (dataprogramada.day, dataprogramada.month, dataprogramada.year)
            last_dt_programada_format = '%s/%s/%s' % (last_dataprogramada.day, last_dataprogramada.month, last_dataprogramada.year)
            if dt_programada_format != last_dt_programada_format or count15 > 15:
                count15 = 1
                last_dataprogramada = dataprogramada

            count_carteira = count_carteira + 1
            if carteira_id_loop != executivoid:
                count_carteira = 1

            carteira_id_loop = executivoid

            item = {
                'objectid': objectid,
                'sequencia15': count15,
                'sequenciacarteira': count_carteira
            }
            update_rows.append(item)

            #print(objectid, executivoid, sequencia, dataprogramada)

    count = 0
    with arcpy.da.UpdateCursor("Roteiros", ['objectid','sequencia15', 'sequenciacarteira']) as cursor:
        for row in cursor:
            objectid = row[0]

            row_filtered = [item for item in update_rows if item['objectid'] == objectid][0]

            row[1] = row_filtered['sequencia15']
            row[2] = row_filtered['sequenciacarteira']

            cursor.updateRow(row)
            count = count + 1
            print('Atualizando (%s/%s)' % (count, len(update_rows)))


def _is_empty(x):
    return x == None or x == '-' or x == '' or x == ' '

def load_hierarquia():

    def _getPerfil(cargo):
        for p in ['Gerente Geral', 'Gerente', 'Coordenador', 'Supervisor', 'Executivo']:
            if p in cargo:
                return p

    def _clear_str(s):
        return s.replace(' ', '').lower()
    
    def _get_superior(cargo, user, users_active):
        column_superior = {
            'Executivo': 'SUPERVISOR',
            'Supervisor': 'COORDENADOR',
            'Coordenador': 'GERENTE',
            'Gerente': 'GG'
        }

        if cargo not in column_superior:
            return None

        if not _is_empty(user[column_superior[cargo]]):
            superior_name = user[column_superior[cargo]]
        
        if _is_empty(user[column_superior[cargo]]) or 'TBA - ' in superior_name:                
            for s in column_superior:
                superior_name = user[column_superior[s]]
                if not _is_empty(superior_name) and 'TBA - ' not in superior_name:
                    break

        if superior_name == None:
            return None
        
        superior_user = [user['USUARIO'] for user in users_active if _clear_str(user['NOME']) == _clear_str(superior_name)]

        return superior_user[0] if len(superior_user) > 0 else None

    def _model_user(user, now):
        cargo = _getPerfil(user['CARGO'])
        superior_user = _get_superior(cargo, user, users_active)
        return { 'attributes': {
            'usuario': user['USUARIO'],
            'nome': user['NOME'],
            'email': user['EMAIL'],
            'perfil': cargo,
            'polo': user['POLO'] if not _is_empty(user['POLO']) else None,
            'carteira': user['CARTEIRA'] if not _is_empty(user['CARTEIRA']) else None,
            'carteiraid': int(user['CODIGO_CARTEIRA']) if not _is_empty(user['CODIGO_CARTEIRA']) else None,
            'usuariosuperior': superior_user,
            'id': int(user['ID']) if not _is_empty(user['ID']) else None,
            'datacriacao': now,
        }}

    users_active = []

    with open(r'D:\Profile\Imagem Geosistemas e Comercio LTDA\PS SQUAD - TELECOM NEGOCIOS - PagSeguro\Documentos Recebidos\HIERARQUIA 03.02 Imagem v2-1.csv', encoding="utf8") as csvfile:
        #spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        reader = csv.DictReader(csvfile, delimiter = ';')
        #for row in spamreader:
        for row in reader:
            if not _is_empty(row['EMAIL']) and not _is_empty(row['USUARIO']):
                users_active.append(row)

        feature_url = 'https://pagsegurohml.img.com.br/server/rest/services/Roteirizacao/Hierarquia_Usuario/FeatureServer/2' #staging
        #feature_url = 'https://pagseguro.img.com.br/server/rest/services/Roteirizacao/Hierarquia_Usuario/FeatureServer/2' #production

        if len(users_active) > 0:
            feature_server.delete_feature_data(feature_url, "1=1")

        payload = []
        now = utils.datetime_to_timestamp(datetime.datetime.now())
        count = 0
        for user in users_active:
            count = count + 1
            payload.append(_model_user(user, now))

            if count % 800 == 0 or len(users_active) == count:
                print('Salvando (%s/%s)' % (count, len(users_active)))
                result = feature_server.post_feature_data(feature_url, payload)
                if result[0]['success'] == False:
                    print(result)
                payload = []

def load_ags_to_gdb():
    from arcgis.gis import GIS
    from arcgis.features import FeatureLayer

    url_gis = 'https://pagsegurohml.img.com.br/portal/'
    user = 'portaladmin'
    pwd = '9hQGFKq79Uhu'
    classgis = GIS(url_gis, user, pwd)

    url_fl = 'https://pagsegurohml.img.com.br/server/rest/services/Hosted/RoteirizacaoPagSeguro/FeatureServer/6'
    fl = FeatureLayer(url_fl)
    fs = fl.query()

    #import arcpy
    workspace = r'D:\Profile\OneDrive - Imagem Geosistemas e Comércio LTDA\Documentos\ArcGIS\Projects\MyProject8\MyProject8.gdb'
    #arcpy.TableToTable_conversion(fs, workspace, "executivos")
    fc = "executivos"
    fs.save(workspace, fc)

def update_empresas_by_csv():
    feature_url = 'https://pagsegurohml.img.com.br/server/rest/services/Hosted/BKORoteirizacaoDev/FeatureServer/0'

    companies = feature_server.get_feature_data(feature_url, geometries=False)    

    companies_dict = {}
    for company in companies:
        companies_dict[str(company['attributes']['id'])] = company['attributes']

    payload = []
    count = 0
    with open(r'D:\Profile\Imagem Geosistemas e Comércio LTDA\SQUAD - TELECOM NEGOCIOS - PagSeguro\Documentos Recebidos\BASE_ROTAS_IMAGEM_02082021.csv', encoding="utf8") as csvfile:
        #spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        reader = csv.DictReader(csvfile, delimiter = ';')
        #for row in spamreader:
        rows = list(reader)
        totalrows = len(rows)
        for i, row in enumerate(rows):
            count = count + 1
            if not _is_empty(row['ID_UNICO']):

                company_filtered = [companies_dict[row['ID_UNICO']]] if row['ID_UNICO'] in companies_dict else []

                if len(company_filtered) > 0:
                    payload.append({
                        'attributes': {
                            'objectid': company_filtered[0]['objectid'],
                            'roteirizar': 1
                        }
                    })
                else:
                    print("Empresa não encontrada:", row['ID_UNICO'])

            if count % 800 == 0 or totalrows == count:
                print('Salvando (%s/%s)' % (count, len(payload)))
                result = feature_server.update_feature_data(feature_url, payload)
                if result[0]['success'] == False:
                    print(result)
                payload = []
        print('aui')

def verify_is_router():
    import arcpy
    arcpy.env.workspace = r"D:\Profile\OneDrive - Imagem Geosistemas e Comércio LTDA\Documentos\ArcGIS\Projects\MyProject9\RoteirosVRP060721.gdb"

    feature_url = 'https://pagsegurohml.img.com.br/server/rest/services/Hosted/BKORoteirizacaoDev/FeatureServer/2'
    routes = feature_server.get_feature_data(feature_url, geometries=False)
    count = 0
    with arcpy.da.UpdateCursor("Geocoded_Companies", ['USER_id','Roteirizado', 'Motivo_Nao_Roteirizado']) as cursor:
        for row in cursor:
            id = row[0]
            row_filtered = [item for item in routes if item['attributes']['empresaid'] == id]
            row[1] = 'Sim' if len(row_filtered) > 0 else 'Não'

            cursor.updateRow(row)
            count = count + 1
            print('Atualizando (%s)' % (count))

def verify_is_company():
    import arcpy
    arcpy.env.workspace = r"D:\Profile\OneDrive - Imagem Geosistemas e Comércio LTDA\Documentos\ArcGIS\Projects\MyProject9\RoteirosVRP060721.gdb"

    feature_url = 'https://pagsegurohml.img.com.br/server/rest/services/Hosted/BKORoteirizacaoDev/FeatureServer/0'
    companies = feature_server.get_feature_data(feature_url, geometries=False)
    count = 0
    with arcpy.da.UpdateCursor("Geocoded_Companies", ['USER_id','Roteirizado', 'Motivo_Nao_Roteirizado'], "Roteirizado = 'Não' AND Motivo_Nao_Roteirizado IS NULL") as cursor:
        for row in cursor:
            id = row[0]
            row_filtered = [item for item in companies if item['attributes']['id'] == id]
            row[2] = 'Violação VRP (8h ou Máx 30)' if len(row_filtered) > 0 else 'Fora Carteira'

            cursor.updateRow(row)
            count = count + 1
            print('Atualizando (%s)' % (count))

def verify_is_company_polo_carteira():
    import arcpy
    arcpy.env.workspace = r"D:\Profile\OneDrive - Imagem Geosistemas e Comércio LTDA\Documentos\ArcGIS\Projects\MyProject9\RoteirosVRP060721.gdb"

    feature_url = 'https://pagsegurohml.img.com.br/server/rest/services/Hosted/BKORoteirizacaoDev/FeatureServer/0'
    companies = feature_server.get_feature_data(feature_url, geometries=False)
    count = 0
    with arcpy.da.UpdateCursor("Geocoded_Companies", ['USER_id','Carteira', 'Polo'], "Motivo_Nao_Roteirizado = 'Violação VRP (8h ou Máx 30)'") as cursor:
        for row in cursor:
            id = row[0]
            row_filtered = [item for item in companies if item['attributes']['id'] == id]
            row[1] = row_filtered[0]['attributes']['carteira']
            row[2] = row_filtered[0]['attributes']['polo']

            cursor.updateRow(row)
            count = count + 1
            print('Atualizando (%s)' % (count))            

def identify_companies_diff_by_file():
    path = r"D:\Profile\Imagem Geosistemas e Comercio LTDA\SQUAD TELECOM_NEGOCIOS - Pags-03-19 [EA 02C-0469] PagSeguro EA-Rotas\3-EXECUCAO\3 Banco de Horas"
    company_ids = {}
    with open(path + r"\ids_business_nao_apagar.txt", encoding="utf8") as f:
        for line in f:
            _id = int(line.strip())
            company_ids[_id] = _id

    feature_url = 'https://pagseguro.img.com.br/server/rest/services/Roteirizacao/RoteirizacaoPagSeguro/FeatureServer/0'
    companies = feature_server.get_feature_data(feature_url, geometries=False, distinct_values="id")

    delete_companies_ids = []
    for company in companies:
        _id = company['attributes']['id']
        if not _id in company_ids:
            delete_companies_ids.append(_id)

    delete_companies_ids = list(dict.fromkeys(delete_companies_ids))
    with open(path + r"\ids_business_apagar_diff.txt", "w") as f:
        for _id in delete_companies_ids:
            f.write(str(_id)+'\n')

def identify_companies_duplicate(): #same name and lat/lng and id different    
    feature_url = 'https://pagseguro.img.com.br/server/rest/services/Roteirizacao/RoteirizacaoPagSeguro/FeatureServer/0'
    companies = feature_server.get_feature_data(feature_url, "roteirizar=1",geometries=False)

    companies_namelatlng = []
    companies_dict = {}
    for company in companies:
        att = company['attributes']
        _key = att['empresa']+'#'+str(att['latitude'])+'#'+str(att['longitude'])
        companies_namelatlng.append(_key)
        if not _key in companies_dict:
            companies_dict[_key] = [company['attributes']['id']]            
        else:
            companies_dict[_key].append(company['attributes']['id'])

    path = r"D:\Profile\Imagem Geosistemas e Comercio LTDA\SQUAD TELECOM_NEGOCIOS - Pags-03-19 [EA 02C-0469] PagSeguro EA-Rotas\3-EXECUCAO\3 Banco de Horas"
    with open(path + r"\ids_business_duplicados_a_roteirizar.txt", "w") as f:
        for _key in companies_dict:
            if len(companies_dict[_key]) > 1:
                for _id in companies_dict[_key]:
                    f.write(str(_id)+'\n')

def delete_companies_by_file():
    path = r"D:\Profile\Imagem Geosistemas e Comercio LTDA\SQUAD TELECOM_NEGOCIOS - Pags-03-19 [EA 02C-0469] PagSeguro EA-Rotas\3-EXECUCAO\3 Banco de Horas"
    company_ids = []
    with open(path + r"\ids_business_apagar_diff.txt", encoding="utf8") as f:
        for line in f:
            _id = int(line.strip())
            company_ids.append(_id)

    count = 0
    ids = []
    for _id in company_ids:
        count+=1
        ids.append(str(_id))
        if count % 500 == 0 or count == len(company_ids):
            where = "id in (%s)" % (','.join(ids))
            feature_url = 'https://pagseguro.img.com.br/server/rest/services/Roteirizacao/RoteirizacaoPagSeguro/FeatureServer/0'
            #feature_server.delete_feature_data(feature_url, where)
            ids = []

def disabled_router_one_duplicates_companies():
    path = r"D:\Profile\Imagem Geosistemas e Comercio LTDA\SQUAD TELECOM_NEGOCIOS - Pags-03-19 [EA 02C-0469] PagSeguro EA-Rotas\3-EXECUCAO\3 Banco de Horas"
    company_ids = []
    with open(path + r"\ids_business_duplicados_2.txt", encoding="utf8") as f:
        for line in f:
            _id = int(line.strip())
            company_ids.append(str(_id))

    where = "id in (%s)" % (','.join(company_ids))
    feature_url = 'https://pagseguro.img.com.br/server/rest/services/Roteirizacao/RoteirizacaoPagSeguro/FeatureServer/0'
    companies = feature_server.get_feature_data(feature_url, where, geometries=False)

    companies_namelatlng = []
    companies_dict = {}
    for company in companies:
        att = company['attributes']
        _key = att['empresa']+'#'+str(att['latitude'])+'#'+str(att['longitude'])
        companies_namelatlng.append(_key)
        if not _key in companies_dict:
            companies_dict[_key] = [company['attributes']['id']]            
        else:
            companies_dict[_key].append(company['attributes']['id'])

    update_flag_route = []
    for _key in companies_dict:
        if len(companies_dict[_key]) > 1:
            count = 0
            for _id in companies_dict[_key]:
                if len(companies_dict[_key]) - count == 1:
                    break
                update_flag_route.append(str(_id))
                count += 1

    with open(path + r"\ids_business_flag_nao_roteirizar_duplicados.txt", "w") as f:
        for _id in update_flag_route:
            f.write(str(_id)+'\n')

    where = "id in (%s)" % (",".join(update_flag_route))
    calc_expression = [{"field" : "roteirizar", "value" : 0}]
    feature_server.calculate_feature_data(feature_url, where, calc_expression)
    #antes: 395

#load_carteiras()
#load_executivos()
#load_empresas()
#complete_data()
#load_gecodificacao_empresas()
#load_hierarquia()
#update_empresas_by_csv()
#verify_is_router()
#verify_is_company()
#verify_is_company_polo_carteira()

#delete_companies_by_file()
#identify_companies_duplicate()
#disabled_router_one_duplicates_companies()


import math
	
p1 = [-23.22922303828328, -45.92757535979337]
#p2 = [-23.23545829602693, -45.917434027892725] # 0.011904833129820054
p2 = [-23.23688152070147, -45.916364578865256]  # 0.013576964387077008
distance = math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )

print(distance)

print('acabou')

