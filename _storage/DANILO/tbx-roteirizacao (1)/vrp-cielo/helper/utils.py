import os
import time
import shutil
from datetime import datetime
import config
import pandas as pd

def delete_if_exists(path):
    if os.path.exists(path) == True:
        shutil.rmtree(path)

def delete_file_if_exists(path_file):
    print(path_file)
    if os.path.exists(path_file) == True:
        os.remove(path_file)

def create_folder_temp(folder_temp):
    delete_if_exists(folder_temp)
    os.makedirs(folder_temp)

def datetime_to_timestamp(date):
    return date.timestamp() * 1000

def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp / 1000) if timestamp != None and timestamp > 0 else datetime(1976, 1, 1, 0, 0, 0)

def datetime_to_yyyymmddhhmmss(date):
    def _format_number(num):
        return num if num > 9 else "0"+str(num)
    return "%s-%s-%s %s:%s:%s" % (_format_number(date.year), _format_number(date.month), _format_number(date.day), _format_number(date.hour), _format_number(date.minute), _format_number(date.second))

def get_colum_file_xls(path):
    xl_file = pd.ExcelFile(path)
    folder = xl_file.sheet_names[0]
    xls = xl_file.parse(folder)
    columns = []
    for column in xls.columns:
        columns.append(column)
    return columns

def read_file_xlsx(path):
    xl_file = pd.ExcelFile(path)
    folder = xl_file.sheet_names[0]
    data_frame = pd.read_excel(path, sheet_name=folder)
    data_frame = data_frame.fillna('')
    rows = data_frame.to_dict(orient='record')
    lines = []
    for data in rows:
        lines.append(data)
    return lines
 