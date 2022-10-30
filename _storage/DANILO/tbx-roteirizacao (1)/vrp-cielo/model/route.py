import model.helper as helper
class Route:
    def __init__(self, name, start_depot_name, max_order_count, limit_km):
        self.name = name
        self.start_depot_name = start_depot_name
        self.earliest_start_time = helper.get_date_from_route_name(self.name).replace(hour=9, minute=0, second=0, microsecond=0)
        self.latest_start_time = helper.get_date_from_route_name(self.name).replace(hour=18, minute=0, second=0, microsecond=0)
        self.cost_per_unit_time = float(1.0)
        self.max_order_count = max_order_count
        self.assignment_rule = 2
        self.max_total_time = 580 # 8h de trabalho
        self.limit_km = limit_km
    
    def get_values(self):
        return {
            'Name': self.name,
            'StartDepotName': self.start_depot_name,
            'EarliestStartTime': self.earliest_start_time,
            'LatestStartTime': self.latest_start_time,
            'CostPerUnitTime': self.cost_per_unit_time,
            'MaxOrderCount': self.max_order_count,
            'AssignmentRule': self.assignment_rule,
            'MaxTotalTime': self.max_total_time,
            "MaxTotalDistance": self.limit_km
        }