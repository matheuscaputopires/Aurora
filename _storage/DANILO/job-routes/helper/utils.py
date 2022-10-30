import os
import shutil
import math
from datetime import datetime

def delete_if_exists(path):
    if os.path.exists(path) == True:
        shutil.rmtree(path)

def get_unique_values_from_items(key, items):
    used = set()
    return [x[key] for x in items if x[key] not in used and (used.add(x[key]) or True)]

def datetime_to_timestamp(date):
    return date.timestamp() * 1000

def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp / 1000) if timestamp != None and timestamp > 0 else datetime(1976, 1, 1, 0, 0, 0)

def format_date_dmY(date):
    return date.strftime('%d%m%Y')    

def exist_path(path_folder):
    return os.path.isdir(path_folder)

def create_folder(path_folder):
    if exist_path(path_folder) == False:
        os.makedirs(path_folder)

def calc_distance_2_points(p1, p2):
    return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )