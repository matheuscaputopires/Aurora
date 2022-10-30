from model.geometry_point import GeometryPoint
import model.helper as helper
from datetime import datetime

class Order(GeometryPoint):
    def __init__(self, name, description, revenue, latitude_y, longitude_x):
        super().__init__(latitude_y, longitude_x)
        self.name = name
        self.description = description
        self.revenue = revenue
        self.service_time = 20

    def _validate_time_window(self, date, date2):
        def is_empty(v):
            return v == '' or v == None
        return None if is_empty(date) or is_empty(date2) else date

    def _format_time_window(self, time_window):
        route_day = helper.get_date_from_route_name(self.description)
        if type(time_window) == str:
            time_window = datetime.strptime(time_window, '%H:%M:%S')
        return route_day.replace(hour=time_window.hour, minute=time_window.minute, second=0, microsecond=0) if time_window != None else None

    def get_values(self):
        return {
            'Name': self.name, 
            'Description': self.description,
            'ServiceTime': self.service_time,
            'Revenue': self.revenue,
            'AssignmentRule': 3,
            'geometry': self.get_shape_xy()
        }