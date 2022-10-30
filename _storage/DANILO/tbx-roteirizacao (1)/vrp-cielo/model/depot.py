from model.geometry_point import GeometryPoint

class Depot(GeometryPoint):
    def __init__(self, name, latitude_y, longitude_x):
        super().__init__(latitude_y, longitude_x)
        self.name = name

    def get_values(self):
        return {
            'Name': self.name, 
            'geometry': self.get_shape_xy()
        }