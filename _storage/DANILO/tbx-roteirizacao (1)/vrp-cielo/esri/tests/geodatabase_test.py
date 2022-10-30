from unittest import TestCase
from mock import patch, MagicMock
from config import Config
from esri.geodatabase import Geodatabase
import os
import json

class TestGeodatabase(TestCase):

    @classmethod
    def setUpClass(self):
        self.config_fake = MagicMock(return_value=Config())
        self.config_fake.get_env_run = MagicMock(return_value="test")
        self.log_fake = MagicMock(return_value=LogFake())

    def _get_mock_arcpy(self):
        arcpyFake = ArcpyFake()
        return MagicMock(return_value=arcpyFake)

    def test_search_data(self):        
        geodatabase = Geodatabase(self.log_fake, self.config_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        ITEMS_FAKE = [(1, 'Jhon'), (2, 'Mary')]
        geodatabase._arcpy.da.SearchCursor.return_value.__enter__.return_value = ITEMS_FAKE

        path_fake = "/path/"
        feature = 'gdb/feature_name'
        fields = ['id', 'name']
        where = None
        result = geodatabase.search_data(path_fake, feature, fields, where)

        result_expected = [{'id': 1, 'name': 'Jhon'}, {'id': 2, 'name': 'Mary'}]
        self.assertEqual(result, result_expected)

    def test_create(self):
        geodatabase = Geodatabase(self.log_fake, self.config_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        geodatabase._arcpy.CreateFileGDB_management = MagicMock(return_value=None)

        folder_out = "../../temp"
        name = "Routers"

        geodatabase.create(folder_out, name)
        geodatabase._arcpy.CreateFileGDB_management.assert_called_once_with(folder_out, name)

    def test_create_feature(self):
        geodatabase = Geodatabase(self.log_fake, self.config_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        sr_fake = "Spatial3857"
        geodatabase._arcpy.SpatialReference = MagicMock(return_value=sr_fake)
        geodatabase._arcpy.CreateFeatureclass_management = MagicMock(return_value=None)
        geodatabase._arcpy.AddField_management = MagicMock(return_value=None)

        fgdb_path = "path_name"
        name = "feature_router"
        type = "POINT"
        fields = ["ID", "Name"]
        geodatabase.create_feature(fgdb_path, name, type, fields)

        geodatabase._arcpy.SpatialReference.assert_called_once_with(3857)
        feature_name_fake = "featurerouter"
        geodatabase._arcpy.CreateFeatureclass_management.assert_called_once_with(fgdb_path, feature_name_fake, type, "", "DISABLED", "DISABLED", sr_fake)

        geodatabase._arcpy.AddField_management.assert_any_call(feature_name_fake, fields[0], "TEXT",  field_length=1024, field_alias=fields[0], field_is_nullable="NULLABLE")
        geodatabase._arcpy.AddField_management.assert_any_call(feature_name_fake, fields[1], "TEXT",  field_length=1024, field_alias=fields[1], field_is_nullable="NULLABLE")

    def test_insert_data(self):
        geodatabase = Geodatabase(self.log_fake, self.config_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        insert_cursor_fake = InsertCursorFake(None, None)
        insert_cursor_fake.insertRow = MagicMock(return_value=None)
        geodatabase._arcpy.da.InsertCursor.return_value.__enter__.return_value = insert_cursor_fake

        fgdb_path = "router_vrp.gdb"
        feature = "feature_routers"
        fields = ['CD_LOGN', 'CD_MCC', 'SHAPE@JSON']
        rows = [{
                "CD_LOGN": "Mary",
                "CD_MCC": "1234",
                "geometry":{
                    "x": -60.03583,
                    "y": -3.1191
                }
         }]
        geodatabase.insert_data(fgdb_path, feature, fields, rows)
        
        feature_path = os.path.join(fgdb_path, feature)
        geodatabase._arcpy.da.InsertCursor.assert_called_with(feature_path, fields)
        row = rows[0]
        feature_geometry = json.dumps({'x': -60.03583, 'y': -3.1191, 'spatialReference': {'wkid': 4326}})
        feature_row_fake = (row['CD_LOGN'], row['CD_MCC'], feature_geometry)
        insert_cursor_fake.insertRow.assert_called_with(feature_row_fake)

    def test_export_to_json(self):
        geodatabase = Geodatabase(self.log_fake, self.config_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        geodatabase._arcpy.conversion.FeaturesToJSON = MagicMock(return_value=None)

        fgdb_path = "router_vrp"
        feature = "feature_routers"
        path_out = "path/file.json"
        geodatabase.export_to_json(fgdb_path, feature, path_out)

        feature_path = os.path.join(fgdb_path, feature)
        geodatabase._arcpy.conversion.FeaturesToJSON.assert_called_once_with(feature_path, path_out, "FORMATTED", "NO_Z_VALUES", "NO_M_VALUES", "GEOJSON", "WGS84", "USE_FIELD_NAME")

    def test_export_to_csv(self):
        geodatabase = Geodatabase(self.log_fake, self.config_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        geodatabase._arcpy.conversion.TableToTable = MagicMock(return_value=None)

        feature = "feature_routers"
        path_out = "path/file.json"
        name_out = "feature_routers"
        geodatabase.export_to_csv(feature, path_out, name_out)

        geodatabase._arcpy.conversion.TableToTable.assert_called_once_with(feature, path_out, feature+".csv")

    def test_get_datasets(self):

        geodatabase = Geodatabase(self.log_fake, self.config_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        DATASETS_FAKE = ['Routexpto']
        geodatabase._arcpy.ListDatasets = MagicMock(return_value=DATASETS_FAKE)

        names = ["Route*"]
        result = geodatabase._get_datasets(names)

        result_expected = ['', 'Routexpto']
        self.assertEqual(result, result_expected)

    def test_get_datasets_not_found(self):

        geodatabase = Geodatabase(self.log_fake, self.config_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        DATASETS_FAKE = []
        geodatabase._arcpy.ListDatasets = MagicMock(return_value=DATASETS_FAKE)

        names = ["Route*"]
        result = geodatabase._get_datasets(names)

        result_expected = ['']
        self.assertEqual(result, result_expected)        

    def test_get_path_feature(self):

        geodatabase = Geodatabase(self.log_fake, self.config_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        DATASETS_FAKE = ['Routexpto']
        geodatabase._get_datasets = MagicMock(return_value=DATASETS_FAKE)
        FEATURE_FAKE = ['Stopsxxyy', 'Routesyyggg']
        geodatabase._arcpy.ListFeatureClasses = MagicMock(return_value=FEATURE_FAKE)

        result = geodatabase.get_path_feature('Stops')

        result_expected = os.path.join(DATASETS_FAKE[0], 'Stopsxxyy')
        self.assertEqual(result, result_expected)
        geodatabase._get_datasets.assert_called_with(["Route*", "VehicleRoutingProblem*"])
        geodatabase._arcpy.ListFeatureClasses.assert_called_with(feature_dataset=DATASETS_FAKE[0])

    def test_update_data(self):
        
        fgdb_path = "router_vrp.gdb"
        feature = 'feature_name'
        fields = ['id', 'name']
        where = 'id in (1)' 
        rows_to_update = [{'id': 1, 'name': 'John'}]
        field_key = 'id'
        
        geodatabase = Geodatabase(self.log_fake, self.config_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        update_cursor_fake = UpdateCursorFake(None, None, None)
        update_cursor_fake.updateRow = MagicMock(return_value=None)
        geodatabase._arcpy.da.UpdateCursor.return_value.__enter__.return_value = update_cursor_fake

        geodatabase.update_data(fgdb_path, feature, fields, where, rows_to_update, field_key)

        row_expected = [1, 'John']
        update_cursor_fake.updateRow.assert_called_with(row_expected)


class ArcpyFake:
    pass
class LogFake:
    pass
class InsertCursorFake():
    def __init__(self, feature, fields):
        pass
    def insertRow(self, params):
        pass

class UpdateCursorFake():
    def __init__(self, feature, fields, where):
        pass
    def __iter__(self):
        self.count = 1
        return self

    def __next__(self):
        if self.count <= 2:
            self.count += 1
            return [1, 'Mary']
        else:
            raise StopIteration
    def updateRow(self, params):
        pass
    def deleteRow(self):
        pass 

class DescribeFake():
    def __init__(self):
        self.spatialReference = "SIRGAS2000"