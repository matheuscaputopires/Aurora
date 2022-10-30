from datetime import datetime

def get_date_from_route_name(name):
    name_array = name.split('#')
    year = int(name_array[1][:4])
    month = int(name_array[1][4:-2])
    day = int(name_array[1][6:])
    return datetime(year, month, day)