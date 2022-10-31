# -*- encoding: utf-8 -*-
#!/usr/bin/python
import datetime
import json
import os
import time
from datetime import date, datetime

from arcpy.management import XYTableToPoint
from core._logs import *
from core.libs.BaseDBPath import BaseDBPath

from .Database import Database, wrap_on_database_editing
from .Editor import CursorManager
from .Feature import Feature


class Table(BaseDBPath, CursorManager):
    x_field: str = 'Longitude'
    y_field: str = 'Latitude'

    def __init__(self, path: str = None, name: str = None, *args, **kwargs):
        super().__init__(path=path, name=name, *args, **kwargs)
    
    @wrap_on_database_editing
    def geocode_addresses(self) -> Feature:
        points = XYTableToPoint(
            in_table=self.full_path,
            out_feature_class=os.path.join(self.temp_db, f'{self.name.split(".")[0]}_XY'),
            x_field=self.x_field,
            y_field=self.y_field,
            coordinate_system=self.default_sr
        )
        return Feature(points)
