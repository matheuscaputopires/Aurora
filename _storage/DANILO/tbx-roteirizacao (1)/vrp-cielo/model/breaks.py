import model.helper as helper

class Breaks:
    def __init__(self, route_name, service_time):
        self.route_name = route_name
        self.service_time = service_time
        self.time_window_start =  helper.get_date_from_route_name(self.route_name).replace(hour=12, minute=0, second=0, microsecond=0)
        self.time_window_end = helper.get_date_from_route_name(self.route_name).replace(hour=13, minute=0, second=0, microsecond=0)
    
    def get_values(self):
        return {
            "RouteName": self.route_name,
            "ServiceTime": self.service_time,
            "TimeWindowStart": self.time_window_start,
            "TimeWindowEnd": self.time_window_end,
            "Precedence": 1
        }