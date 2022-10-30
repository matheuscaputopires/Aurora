import esri.arcgis_server as ags
import json
import time

def retry_while(fn, tries=3, sleep_time=60, logger=None, exit_app_if_fail=True):
    '''
        It executes a given function n times, and sleeps between each try.

        It accepts a logger to track the situation and a flag to exit the
        application if all the tries had failed.

        fn: a function without parameters that shall be processed
        tries: number of times the fn function will be tried
        sleep_time: number of seconds to sleep between each try
        logger: application logger
        exit_app_if_fail: flag to order a system exit if all tries had failed
    '''
    def log(message):
        if logger:
            logger.error(message)
        else:
            print(message)

    while tries:
        try:
            return fn()
        except Exception as err:
            log('Erro durante chamada do AGS')
            log(err)

        tries -= 1

        if tries:
            log('Dormindo.... [ resta(m) %s tentativa(s) ]' % tries)
            time.sleep(sleep_time)

    if exit_app_if_fail:
        log('Erro irrecuperável, saindo da aplicação....')
        exit(1)

def count_feature_data(feature_url, where="1=1", logger=None):
    feature_url += '/query'
    token = ags.generate_token()
    feature_params = { 'token': token, 'where': where, 'f': 'json', 'outFields': '*', 'returnCountOnly': 'true' }

    fn = lambda: ags.get_data(feature_url=feature_url, feature_params=feature_params)
    response = retry_while(fn=fn, tries=3, sleep_time=60, logger=logger, exit_app_if_fail=True)

    return response['count']    

def get_feature_data(feature_url, where="1=1", distinct_values=None, geometries=True, feature_limit=None, logger=None, order_by_field=None):
    """``where`` opcional, exemplo: "field1 = 1 AND field2 = 'XPTO'..."
    ``distinct_values`` opcional, exemplo: "field1, field2..."
    ``geometries`` por padrão é True
    ``feature_limit`` opcional, exemplo: 100 ou 200
    """
    feature_url += '/query'
    all_features = []
    result_off_set = 0
    result_record_count = 2000
    token = ags.generate_token()

    feature_params = { 'token': token, 'where': where, 'f': 'json', 'outFields': '*' }
    feature_params['orderByFields'] = order_by_field
    if distinct_values != None:
        feature_params['outFields'] = distinct_values
        feature_params['orderByFields'] = distinct_values
        feature_params['groupByFieldsForStatistics'] = distinct_values
        feature_params['returnDistinctValues'] = "true"


    feature_params['returnGeometry'] = 'true' if geometries == True else 'false'

    more_records = True
    while (more_records):
        
        feature_params['resultOffset'] = result_off_set
        feature_params['resultRecordCount'] = result_record_count

        fn = lambda: ags.get_data(feature_url=feature_url, feature_params=feature_params)
        response = retry_while(fn=fn, tries=3, sleep_time=60, logger=logger, exit_app_if_fail=True)

        acquired_features = response['features']
        records_found = len(acquired_features)
        more_records = True if records_found > 0 else False
        all_features += acquired_features
        result_off_set += records_found        

    return all_features

def post_feature_data(feature_url, payload, logger=None):
    token = ags.generate_token()
    feature_url += '/addFeatures'
    data = json.dumps(payload)
    payload = { 'features': data, 'f': 'pjson', 'rollbackOnFailure': 'true', 'token': token }

    fn = lambda: ags.post_data(feature_url, payload)
    response = retry_while(fn=fn, tries=3, sleep_time=60, logger=logger, exit_app_if_fail=True)

    return [{'success': response['error']['message']}] if 'error' in response else response['addResults']

def delete_feature_data(feature_url, filter, logger=None):
    token = ags.generate_token()
    feature_url += '/deleteFeatures'
    payload = { 'token': token, 'where': filter, 'f': 'json' }

    fn = lambda: ags.delete_data(feature_url, payload)
    response = retry_while(fn=fn, tries=3, sleep_time=60, logger=logger, exit_app_if_fail=True)

    return response

def update_feature_data(feature_url, payload, logger=None):
    token = ags.generate_token()
    feature_url += '/updateFeatures'
    data = json.dumps(payload)
    payload = { 'features': data, 'f': 'pjson', 'rollbackOnFailure': 'true', 'token': token }

    fn = lambda: ags.post_data(feature_url, payload)
    response = retry_while(fn=fn, tries=3, sleep_time=60, logger=logger, exit_app_if_fail=True)

    return [{'success': response['error']['message']}] if 'error' in response else response['updateResults']

def calculate_feature_data(feature_url, where, calc_expression, logger=None):
    """``where``, exemplo: "field1 = 1 AND field2 = 'XPTO'..."
    ``calc_expression`` opcional, exemplo: [{"field" : "Quality", "value" : 3}]"
    """
    token = ags.generate_token()
    feature_url += '/calculate'
    payload = { 'where': where, 'calcExpression': json.dumps(calc_expression), 'f': 'pjson', 'token': token }

    fn = lambda: ags.post_data(feature_url, payload)
    response = retry_while(fn=fn, tries=3, sleep_time=60, logger=logger, exit_app_if_fail=True)

    return [{'success': response['error']['message']}] if 'error' in response else response['updatedFeatureCount']
