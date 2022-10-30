class GeometryPoint:
    def __init__(self, latitude_y, longitude_x):
        self.latitude_y = latitude_y
        self.longitude_x = longitude_x

    def get_shape_xy(self):
        return { 
            "x": self.longitude_x, 
            "y": self.latitude_y
        }