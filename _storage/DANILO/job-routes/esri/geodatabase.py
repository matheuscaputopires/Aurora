import os
from config import Config
from helper import utils
import json

FILE_GDB = 'fGDB.gdb'
class Geodatabase():
    def __init__(self, logger):
        self.logger = logger
        self.config = Config()
        self._arcpy = __import__("arcpy") if self.config.get_env() != "test" else None

    def prepare_item(self, columns, item):
        new_item = {}
        for column in columns:
            new_item[column['to']] = utils.timestamp_to_datetime(item[column['from']]) if column['format'] == 'date' else item[column['from']]

        return new_item

    def construct_where(self, key, items):
        where = "("
        for item in items:
            where += (",%s" % item[key])
        
        where = where.replace("(,", "(")
        return ("%s in " % key) + where + ")"

    def _setup_workspace_arcpy(self):
        self.logger.info("Configurando variáveis do ambiente arcpy...")
        self._arcpy.env.overwriteOutput = True
        self._arcpy.env.workspace = self.get_path()

    def create(self):
        self.logger.info("Criando gdb temporário...")
        self.config.create_folder_temp()
        path_folder_temp = self.config.get_folder_temp()
        self._arcpy.CreateFileGDB_management(path_folder_temp, FILE_GDB)
        self._setup_workspace_arcpy()

    def get_path(self):
        path_folder_temp = self.config.get_folder_temp()
        return os.path.join(path_folder_temp, FILE_GDB)

    def create_feature(self, name, fields, type="POINT", spatial_reference=3857):
        """``name`` exemplo: cliente, empresas"
        ``fields`` exemplo: [{'name': 'id', 'type': 'LONG'}, {'name': 'endereco', 'type': 'TEXT'}]"
        ``type`` opcional, por padrão é POINT, outros valores MULTIPOINT, POLYGON, POLYLINE, MULTIPATCH
        ``spatial_reference`` por padrão é 3857
        """        
        self.logger.info("Criando feature "+ name +"...")

        sr = self._arcpy.SpatialReference(spatial_reference)
        self._arcpy.CreateFeatureclass_management(self.get_path(), name, type, "", "DISABLED", "DISABLED", sr)

        for field in fields:
            self._arcpy.AddField_management(name, field['name'], field['type'], "", "", "", field['name'], "NULLABLE", "NON_REQUIRED")


    def _validate_geometry_key(self, feature, feature_fields):
        if 'SHAPE@JSON' in feature_fields:
            if 'spatialReference' not in feature['geometry']:
                feature['geometry']['spatialReference'] = {'wkid': 3857}
            feature_geometry = json.dumps(feature['geometry'])
        else:
            feature_geometry = tuple([feature['geometry']['x'], feature['geometry']['y']])
        
        return feature_geometry
        
    def insert_data(self, input_data, feature_local_gdb, feature_fields):
        with self._arcpy.da.InsertCursor(feature_local_gdb, feature_fields) as cursor:
            for feature in input_data:
                feature_row = []

                contains_field_shape = any('SHAPE@' in field for field in feature_fields)

                if contains_field_shape == True:
                    feature_geometry = self._validate_geometry_key(feature, feature_fields)

                for key in feature_fields:
                    if "SHAPE@" not in key:
                            feature_row.append(feature['attributes'][key])
                
                if contains_field_shape == True:
                    feature_row.append(feature_geometry)
                
                feature_row = tuple(feature_row)
                cursor.insertRow(feature_row)

    def update_data(self, feature, fields, where, rows_to_update, field_key):
        with self._arcpy.da.UpdateCursor(feature, fields, where) as cursor:
            for row in cursor:
                item_filtered = [item for item in rows_to_update if item[field_key] == row[fields.index(field_key)]]
                if len(item_filtered) > 0:
                    for field in fields:
                        if field != field_key:
                            row[fields.index(field)] = item_filtered[0][field]
                    cursor.updateRow(row)

    def _get_datasets(self, names):
        datasets = ['']
        for name in names:
            datasets_found = self._arcpy.ListDatasets(name ,"Feature")
            datasets = datasets + (datasets_found if datasets_found is not None else [])
        return datasets

    def get_path_feature(self, name):
        datasets = self._get_datasets(["Route*", "VehicleRoutingProblem*"])

        feature_selected = None
        for ds in datasets:
            for feature in self._arcpy.ListFeatureClasses(feature_dataset=ds):
                path = os.path.join(ds, feature)
                if path.find(name) > -1:
                    feature_selected = path

        return feature_selected

    def _prepare_list(self, fields, cursor):
        items = []
        for row in cursor:
            item = {}
            for field in fields:        
                item[field] = row[fields.index(field)]        
            items.append(item)        

        return items

    def _prepare_list_dict(self, fields, cursor, key):
        items_dict = {}
        for row in cursor:
            item = {}
            for field in fields:        
                item[field] = row[fields.index(field)]
            items_dict[row[fields.index(key)]] = item

        return items_dict
    
    def search_data(self, feature, fields, where="1=1", distinct=None, order_by=None, dict_key=None):
        result_found = []
        if distinct != None:
            distinct = "DISTINCT " + distinct
        with self._arcpy.da.SearchCursor(feature, fields, where, sql_clause=(distinct, order_by)) as cursor:
            result_found = self._prepare_list(fields, cursor) if dict_key == None else self._prepare_list_dict(fields, cursor, dict_key)

        return result_found

    def copy_template_feature_to_temp_gdb(self, feature_name, out_feature_name=None, geom_type = "Point"):
        out_feature_name = out_feature_name if out_feature_name != None else feature_name
        feature_template = os.path.join(self.config.get_folder_template(), "template.gdb", feature_name)
        spatial_reference = self._arcpy.Describe(feature_template).spatialReference
        gdb_path = self.get_path()
        self._arcpy.management.CreateFeatureclass(out_path=gdb_path, out_name=out_feature_name, geometry_type=geom_type, template=feature_template, has_m="DISABLED", has_z="DISABLED", spatial_reference=spatial_reference)

    def copy_template_table_to_temp_gdb(self, table_name, out_table_name=None):
        out_table_name = out_table_name if out_table_name != None else table_name
        table_template = os.path.join(self.config.get_folder_template(), "template.gdb", table_name)
        gdb_path = self.get_path()
        self._arcpy.management.CreateTable(out_path=gdb_path, out_name=out_table_name, template=table_template)

    def delete_data(self, feature, where):
        with self._arcpy.da.UpdateCursor(in_table=feature, field_names='*', where_clause=where) as cursor:
            for _ in cursor:
                cursor.deleteRow()                    

    def clear_objects(self, names):
        for name in names:
            feature_path = self.get_path_feature(name)
            self._arcpy.management.TruncateTable(feature_path)

    def _get_description_of_domain(self, value, domain_name):
        domains = self._arcpy.da.ListDomains(self.get_path())
        for domain in domains:
            if domain.name == domain_name:
                if domain.domainType == 'CodedValue':
                    coded_values = domain.codedValues
                    for val, desc in coded_values.items():
                        if val == value:
                            return desc
                elif domain.domainType == 'Range':
                    return 'Min: %s | Máx: %s' % (domain.range[0], domain.range[1])

        return value

    def get_violated_domain(self, value):
        return self._get_description_of_domain(value, "ViolatedConstraintDomain")

    def calculate_data(self, feature, field_name, expression, expression_type="PYTHON3"):
      self._arcpy.CalculateField_management(feature, field_name, expression, expression_type)

    def select_layer_by_attribute(self, feature, where, selection_type="NEW_SELECTION"):
        return self._arcpy.SelectLayerByAttribute_management(feature, selection_type, where)

    def clear_selection_layer(self, feature):
        self._arcpy.SelectLayerByAttribute_management(feature, "CLEAR_SELECTION")