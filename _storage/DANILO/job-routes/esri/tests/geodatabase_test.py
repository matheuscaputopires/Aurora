from unittest import TestCase
from mock import patch, MagicMock
from esri.geodatabase import Geodatabase
import os
import json

class TestGeodatabase(TestCase):

    @classmethod
    def setUpClass(self):
        self.log_fake = MagicMock(return_value=LogFake())    

    def _get_mock_arcpy(self):
        arcpyFake = ArcpyFake()
        return MagicMock(return_value=arcpyFake)

    @patch('esri.geodatabase.Config')
    def test_create(self, mock_Config):

        FOLDER = "path/folder_example"
        FILE_GDB = 'fGDB.gdb'

        mock_Config.return_value.create_folder_temp = MagicMock(return_value=None)

        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Config.return_value.get_folder_temp = MagicMock(return_value=FOLDER)

        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()
        
        path_fake = 'path/gdb'
        geodatabase.get_path = MagicMock(return_value=path_fake)

        geodatabase.create()
        
        mock_Config.return_value.create_folder_temp.assert_called_with()
        geodatabase._arcpy.CreateFileGDB_management.assert_called_with(FOLDER, FILE_GDB)

        self.assertTrue(geodatabase._arcpy.env.overwriteOutput)
        self.assertEqual(geodatabase._arcpy.env.workspace, path_fake)        

    @patch('esri.geodatabase.Config')
    def test_get_path(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")

        FOLDER = "path/folder_example"
        FILE_GDB = 'fGDB.gdb'

        path_expected = os.path.join(FOLDER, FILE_GDB)
        mock_Config.return_value.get_folder_temp = MagicMock(return_value=FOLDER)
        
        geodatabase = Geodatabase(self.log_fake)

        path = geodatabase.get_path()

        self.assertEqual(path_expected, path)

    @patch('esri.geodatabase.Config')
    def test_create_feature(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Config.return_value.get_folder_temp = MagicMock(return_value="temp")

        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        sr_fake = "Spatial3857"
        geodatabase._arcpy.SpatialReference = MagicMock(return_value=sr_fake)
        geodatabase._arcpy.CreateFeatureclass_management = MagicMock(return_value=None)
        geodatabase._arcpy.AddField_management = MagicMock(return_value=None)

        name = "feature_router"
        fields = [{'name': 'id', 'type': 'LONG'}, {'name': 'description', 'type': 'TEXT'}]
        geodatabase.create_feature(name, fields)

        geodatabase._arcpy.SpatialReference.assert_called_once_with(3857)
        feature_name_fake = "feature_router"
        path_fake = os.path.join("temp", "fGDB.gdb")
        geodatabase._arcpy.CreateFeatureclass_management.assert_called_once_with(path_fake, feature_name_fake, "POINT", "", "DISABLED", "DISABLED", sr_fake)

        geodatabase._arcpy.AddField_management.assert_any_call(feature_name_fake, fields[0]['name'], fields[0]['type'], "", "", "", fields[0]['name'], "NULLABLE", "NON_REQUIRED")
        geodatabase._arcpy.AddField_management.assert_any_call(feature_name_fake, fields[1]['name'], fields[1]['type'], "", "", "", fields[1]['name'], "NULLABLE", "NON_REQUIRED")

    @patch('esri.geodatabase.Config')
    def test_prepare_item(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")

        columns = [{'from': 'id_xxx', 'to': 'id', 'format': None}]
        item = {'id_xxx': 1, 'name': 'John'}

        geodatabase = Geodatabase(self.log_fake)
        
        result = geodatabase.prepare_item(columns, item)

        result_expected = {'id': 1}      
        self.assertEqual(result, result_expected)

    @patch('esri.geodatabase.Config')
    def test_construct_where(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")

        key = 'id'
        items = [{'id': 1, 'name': 'John'}, {'id': 2, 'name': 'Mary'}]
        geodatabase = Geodatabase(self.log_fake)

        result = geodatabase.construct_where(key, items)

        result_expected = "id in (1,2)"

        self.assertEqual(result, result_expected)

    @patch('esri.geodatabase.Config')
    def test_validate_geometry_key(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)

        feature = {
                "geometry":{
                    "x":123,
                    "y":-987
                }        
        }
        feature_fields = ['id', 'SHAPE@JSON']
        result = geodatabase._validate_geometry_key(feature, feature_fields)

        result_expected = json.dumps({'x': 123, 'y': -987, 'spatialReference': {'wkid': 3857}})
        self.assertEqual(result, result_expected)

    @patch('esri.geodatabase.Config')
    def test_validate_geometry_key_without_shapejson(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)

        feature = {
                "geometry":{
                    "x":123,
                    "y":-987
                }        
        }
        feature_fields = ['id']
        result = geodatabase._validate_geometry_key(feature, feature_fields)

        self.assertEqual(result, (123, -987))

    #examples:
    #https://stackoverflow.com/questions/28850070/python-mocking-a-context-manager
    #https://andrewkowalik.com/posts/mocking-python-context-manager/
    @patch('esri.geodatabase.Config')
    def test_insert_data(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        FEATURE_LOCAL_GDB = 'path/fGDB.gdb/feature'
        FEATURE_FIELDS = ['id', 'carteiraid', 'mcc', 'nomeresponsavel']
        FAKE_DATA = [{
            "attributes":{
            "carteiraid":"None",
            "mcc":"None",
            "nomeresponsavel":"None",
            "tipoalerta":"None",
            "id":2,
            "empresa":"None",
            "nomecontato":" ",
            "cnpjcpf":"None",
            "segmento":"None",
            "faixatpv":"None",
            "endereco":"None",
            "numero":" ",
            "bairro":"None",
            "cidade":"None",
            "estado":"None",
            "complemento":" ",
            "latitude":-3515464.443599999,
            "longitude":-5705172.160700001,
            "telefone":"None",
            "clientepagseguro":0,
            "cnae":"1",
            "roteirizar":0,
            "tipopessoa":" ",
            "situacaocliente":" ",
            "receitapresumida":0.0,
            "origemempresa":" ",
            "maiorreceita":0.0,
            "datamaiorreceita": None
         },
         "geometry":{
            "x":-5705172.160700001,
            "y":-3515464.443599999
         }}]      
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        geodatabase.format_date = MagicMock(return_value=None)

        insert_cursor_fake = InsertCursorFake(None, None)
        insert_cursor_fake.insertRow = MagicMock(return_value=None)
        geodatabase._arcpy.da.InsertCursor.return_value.__enter__.return_value = insert_cursor_fake

        geodatabase.insert_data(FAKE_DATA, FEATURE_LOCAL_GDB, FEATURE_FIELDS)
        
        geodatabase._arcpy.da.InsertCursor.assert_called_with(FEATURE_LOCAL_GDB, FEATURE_FIELDS)
        feature = FAKE_DATA[0]
        feature['attributes']['datamaiorreceita'] = None
        feature_row_fake = (feature['attributes']['id'], feature['attributes']['carteiraid'], feature['attributes']['mcc'], feature['attributes']['nomeresponsavel'])
        insert_cursor_fake.insertRow.assert_called_with(feature_row_fake)

    @patch('esri.geodatabase.Config')
    def test_update_data(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        feature = '/path/gdb/feature_name'
        fields = ['id', 'name']
        where = 'id in (1)' 
        rows_to_update = [{'id': 1, 'name': 'John'}]
        field_key = 'id'
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        update_cursor_fake = UpdateCursorFake(None, None, None)
        update_cursor_fake.updateRow = MagicMock(return_value=None)
        geodatabase._arcpy.da.UpdateCursor.return_value.__enter__.return_value = update_cursor_fake

        geodatabase.update_data(feature, fields, where, rows_to_update, field_key)

        row_expected = [1, 'John']
        update_cursor_fake.updateRow.assert_called_with(row_expected)

    @patch('esri.geodatabase.Config')
    def test_get_datasets(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        DATASETS_FAKE = ['Routexpto']
        geodatabase._arcpy.ListDatasets = MagicMock(return_value=DATASETS_FAKE)

        names = ["Route*"]
        result = geodatabase._get_datasets(names)

        result_expected = ['', 'Routexpto']
        self.assertEqual(result, result_expected)

    @patch('esri.geodatabase.Config')
    def test_get_datasets_not_found(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        DATASETS_FAKE = []
        geodatabase._arcpy.ListDatasets = MagicMock(return_value=DATASETS_FAKE)

        names = ["Route*"]
        result = geodatabase._get_datasets(names)

        result_expected = ['']
        self.assertEqual(result, result_expected)        

    @patch('esri.geodatabase.Config')
    def test_get_path_feature(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")

        geodatabase = Geodatabase(self.log_fake)
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

    @patch('esri.geodatabase.Config')
    def test_search_data(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        ITEMS_FAKE = [(1, 'Jhon'), (2, 'Mary')]
        geodatabase._arcpy.da.SearchCursor.return_value.__enter__.return_value = ITEMS_FAKE

        feature = '/path/gdb/feature_name'
        fields = ['id', 'name']
        where = None
        result = geodatabase.search_data(feature, fields, where)

        result_expected = [{'id': 1, 'name': 'Jhon'}, {'id': 2, 'name': 'Mary'}]
        self.assertEqual(result, result_expected)

    @patch('esri.geodatabase.Config')
    def test_search_data_return_dict(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        ITEMS_FAKE = [(1, 'Jhon'), (2, 'Mary')]
        geodatabase._arcpy.da.SearchCursor.return_value.__enter__.return_value = ITEMS_FAKE

        feature = '/path/gdb/feature_name'
        fields = ['id', 'name']
        where = None
        result = geodatabase.search_data(feature, fields, where, dict_key="id")

        result_expected = {1: {'id': 1, 'name': 'Jhon'}, 2: {'id': 2, 'name': 'Mary'}}
        self.assertEqual(result, result_expected)        

    @patch('esri.geodatabase.Config')
    def test_search_data_distinct(self, mock_Config):    
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        ITEMS_FAKE = [(1, 'Jhon'), (2, 'Mary')]
        geodatabase._arcpy.da.SearchCursor.return_value.__enter__.return_value = ITEMS_FAKE

        feature = '/path/gdb/feature_name'
        fields = ['id']
        where = None
        result = geodatabase.search_data(feature, fields, where, distinct="name")

        result_expected = [{'id': 1}, {'id': 2}]
        self.assertEqual(result, result_expected)        

    @patch('esri.geodatabase.Config')
    def test_copy_template_feature_to_temp_gdb(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        mock_Config.return_value.get_folder_template = MagicMock(return_value="path/template")

        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        describe_fake = DescribeFake()
        geodatabase._arcpy.Describe = MagicMock(return_value=describe_fake)
        geodatabase._arcpy.management.CreateFeatureclass = MagicMock(return_value=None)

        geodatabase.get_path = MagicMock(return_value="path/gdb")

        feature_name = "feature_xpto"
        geodatabase.copy_template_feature_to_temp_gdb(feature_name)

        feature_template = os.path.join("path/template", "template.gdb", feature_name)
        geodatabase._arcpy.Describe.assert_called_with(feature_template)

        geodatabase.get_path.assert_called_with()

        geodatabase._arcpy.management.CreateFeatureclass.assert_called_with(out_path="path/gdb", out_name=feature_name, geometry_type="Point", template=feature_template, has_m="DISABLED", has_z="DISABLED", spatial_reference="SIRGAS2000")

    @patch('esri.geodatabase.Config')
    def test_copy_template_table_to_temp_gdb(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        mock_Config.return_value.get_folder_template = MagicMock(return_value="path/template")

        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        geodatabase._arcpy.management.CreateTable = MagicMock(return_value=None)

        geodatabase.get_path = MagicMock(return_value="path/gdb")

        feature_name = "feature_xpto"
        geodatabase.copy_template_table_to_temp_gdb(feature_name)

        feature_template = os.path.join("path/template", "template.gdb", feature_name)

        geodatabase.get_path.assert_called_with()

        geodatabase._arcpy.management.CreateTable.assert_called_with(out_path="path/gdb", out_name=feature_name,template=feature_template)

    @patch('esri.geodatabase.Config')
    def test_clear_objects(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()
        
        paths_fake = ['path/feature1', 'path/feature2']
        geodatabase.get_path_feature = MagicMock(side_effect=paths_fake)

        geodatabase._arcpy.management.TruncateTable = MagicMock(side_effect=[None, None])
        
        names = ['feature1', 'feature2']
        geodatabase.clear_objects(names)

        geodatabase.get_path_feature.assert_any_call(names[0])
        geodatabase.get_path_feature.assert_any_call(names[1])

        geodatabase._arcpy.management.TruncateTable.assert_any_call(paths_fake[0])
        geodatabase._arcpy.management.TruncateTable.assert_any_call(paths_fake[1])        

    @patch('esri.geodatabase.Config')
    def copy_template_table_to_temp_gdb(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")        
        mock_Config.return_value.get_folder_template = MagicMock(return_value="path/template")

        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        table_name = "table_xpto"
        geodatabase.copy_template_table_to_temp_gdb(table_name)

        geodatabase.get_path.assert_called_with()

        table_template = None
        geodatabase._arcpy.management.CreateTable(out_path="path/gdb", out_name=table_name, template=table_template)

    @patch('esri.geodatabase.Config')
    def test_delete_data(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")

        feature = '/path/gdb/feature_name'
        where = 'id in (1)' 
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        update_cursor_fake = UpdateCursorFake(None, None, None)
        update_cursor_fake.deleteRow = MagicMock(return_value=None)
        geodatabase._arcpy.da.UpdateCursor.return_value.__enter__.return_value = update_cursor_fake

        geodatabase.delete_data(feature, where)

        update_cursor_fake.deleteRow.assert_called_with()

    @patch('esri.geodatabase.Config')
    def test_get_description_of_domain(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        geodatabase.get_path = MagicMock(return_value=None)

        class ItemFake(object):
            pass

        item_fake = ItemFake()
        item_fake.name = 'violations'
        item_fake.domainType = 'CodedValue'
        item_fake.codedValues = {
                1: 'Max order'
            }
        domains_fake = [item_fake]
        geodatabase._arcpy.da.ListDomains = MagicMock(return_value=domains_fake)

        value = 1
        domain_name = "violations"
        result = geodatabase._get_description_of_domain(value, domain_name)

        expected = "Max order"
        self.assertEqual(result, expected)

    @patch('esri.geodatabase.Config')
    def test_get_description_of_domain_nothing_value(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        geodatabase.get_path = MagicMock(return_value=None)

        class ItemFake(object):
            pass

        item_fake = ItemFake()
        item_fake.name = 'violations'
        item_fake.domainType = 'CodedValue'
        item_fake.codedValues = {
                2: 'Max order'
            }
        domains_fake = [item_fake]
        geodatabase._arcpy.da.ListDomains = MagicMock(return_value=domains_fake)

        value = 1
        domain_name = "violations"
        result = geodatabase._get_description_of_domain(value, domain_name)

        expected = 1
        self.assertEqual(result, expected)             

    @patch('esri.geodatabase.Config')
    def test_get_description_of_domain_with_range(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        geodatabase.get_path = MagicMock(return_value=None)

        class ItemFake(object):
            pass

        item_fake = ItemFake()
        item_fake.name = 'violations'
        item_fake.domainType = 'Range'
        item_fake.range = [1,100]
        domains_fake = [item_fake]
        geodatabase._arcpy.da.ListDomains = MagicMock(return_value=domains_fake)

        value = 1
        domain_name = "violations"
        result = geodatabase._get_description_of_domain(value, domain_name)

        expected = "Min: 1 | Máx: 100"
        self.assertEqual(result, expected)

    @patch('esri.geodatabase.Config')
    def test_get_description_of_domain_nothing_domainType(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        geodatabase.get_path = MagicMock(return_value=None)

        class ItemFake(object):
            pass

        item_fake = ItemFake()
        item_fake.name = 'violations'
        item_fake.domainType = None
        domains_fake = [item_fake]
        geodatabase._arcpy.da.ListDomains = MagicMock(return_value=domains_fake)

        value = 1
        domain_name = "violations"
        result = geodatabase._get_description_of_domain(value, domain_name)

        expected = 1
        self.assertEqual(result, expected)

    @patch('esri.geodatabase.Config')
    def test_get_description_of_domain_nothing_domainName(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        geodatabase.get_path = MagicMock(return_value=None)

        class ItemFake(object):
            pass

        item_fake = ItemFake()
        item_fake.name = None
        domains_fake = [item_fake]
        geodatabase._arcpy.da.ListDomains = MagicMock(return_value=domains_fake)

        value = 1
        domain_name = "violations"
        result = geodatabase._get_description_of_domain(value, domain_name)

        expected = 1
        self.assertEqual(result, expected)        

    @patch('esri.geodatabase.Config')
    def test_get_violated_domain(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)

        expected = "Max order"
        geodatabase._get_description_of_domain = MagicMock(return_value=expected)
        
        value = 1
        result = geodatabase.get_violated_domain(value)

        self.assertEqual(result, expected)
        geodatabase._get_description_of_domain.assert_called_with(value, "ViolatedConstraintDomain")    

    @patch('esri.geodatabase.Config')
    def test_calculate_data(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        feature = 'url/feature_name'
        field_name = 'year'
        expression = 2021
        geodatabase.calculate_data(feature, field_name, expression)

        geodatabase._arcpy.CalculateField_management.assert_called_with(feature, field_name, expression, "PYTHON3")

    @patch('esri.geodatabase.Config')
    def test_select_layer_by_attribute(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        feature = 'url/feature_name'
        where = 'id=1'
        geodatabase.select_layer_by_attribute(feature, where)

        geodatabase._arcpy.SelectLayerByAttribute_management.assert_called_with(feature, "NEW_SELECTION", where)

    @patch('esri.geodatabase.Config')
    def test_clear_selection_layer(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        geodatabase = Geodatabase(self.log_fake)
        geodatabase._arcpy = self._get_mock_arcpy()

        feature = 'url/feature_name'
        geodatabase.clear_selection_layer(feature)

        geodatabase._arcpy.SelectLayerByAttribute_management.assert_called_with(feature, "CLEAR_SELECTION")        


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