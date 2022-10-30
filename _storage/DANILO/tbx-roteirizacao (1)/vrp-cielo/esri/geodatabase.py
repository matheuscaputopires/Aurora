import json
import re
import os

class Geodatabase():
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self._arcpy = __import__("arcpy") if self.config.get_env_run() != "test" else None
    
    def _join_path(self, path, feature):
        return os.path.join(path, feature)
    
    def _validate_geometry_key(self, feature, feature_fields):
        feature_geometry = ''

        if 'SHAPE@JSON' in feature_fields:
            if 'SHAPE@JSON' in feature:
                feature_geometry = feature['SHAPE@JSON']
            else:
                if 'spatialReference' not in feature['geometry']:
                    feature['geometry']['spatialReference'] = {'wkid': 4326} #{'wkid': 3857}
                feature_geometry = json.dumps(feature['geometry'])
        else:
            feature_geometry = tuple([feature['geometry']['x'], feature['geometry']['y']])
        
        return feature_geometry

    def search_data(self, fgdb_path, feature, fields, where="1=1", order_by = None):
        result_found = []
        sr = self._arcpy.SpatialReference(4326)
        feature = self._join_path(fgdb_path, feature)
        with self._arcpy.da.SearchCursor(feature, fields, where, spatial_reference=sr, sql_clause=(None, order_by)) as cursor:
            for row in cursor:
                item = {}
                for field in fields:        
                    item[field] = row[fields.index(field)]        
                result_found.append(item)

        return result_found

    def delete_rows(self, fgdb_path, feature, list_remove, field = "OBJECTID"):
        #self.logger.info("Removendo itens de "+ str(feature) +"...")
        feature = self._join_path(fgdb_path, feature)
        with self._arcpy.da.UpdateCursor(feature, field) as cursor:
            for row in cursor:
                for list in list_remove:
                    if row[0] == list[field]:
                        cursor.deleteRow()
    
    def create(self, folder_out, name):
        #self.logger.info("Criando gdb "+ str(name) +"...")
        self._arcpy.CreateFileGDB_management(folder_out, name)
    
    # types: POINT / MULTIPOINT / POLYGON / POLYLINE / MULTIPATCH
    def create_feature(self, fgdb_path, name, type, fields):
        #self.logger.info("Criando feature "+ str(name) +"...")

        feature = re.sub("[^a-zA-Z]", "", name)

        sr = self._arcpy.SpatialReference(3857)
        self._arcpy.CreateFeatureclass_management(fgdb_path, feature, type, "", "DISABLED", "DISABLED", sr)

        self._arcpy.env.workspace = fgdb_path

        for field in fields:
            self._arcpy.AddField_management(feature, field, "TEXT", field_length=1024, field_alias=field, field_is_nullable="NULLABLE")

    def update_data(self, fgdb_path, feature, fields, where, rows_to_update, field_key):
        #self.logger.info("Atualizando feature "+ str(feature) +"...")
        feature = self._join_path(fgdb_path, feature)
        with self._arcpy.da.UpdateCursor(feature, fields, where) as cursor:
            for row in cursor:
                item_filtered = [item for item in rows_to_update if item[field_key] == row[fields.index(field_key)]]
                if len(item_filtered) > 0:
                    for field in fields:
                        if field != field_key:
                            row[fields.index(field)] = item_filtered[0][field]
                    cursor.updateRow(row)                    
    
    def prepare_row(self, row, fields):
        feature_row = []

        contains_field_shape = any('SHAPE@' in field for field in fields)

        if contains_field_shape == True:
            feature_geometry = self._validate_geometry_key(row, fields)

        for key in fields:
            if "SHAPE@" not in key:
                feature_row.append(row[key])
        
        if contains_field_shape == True:
            feature_row.append(feature_geometry)
        
        return tuple(feature_row)        
    
    def insert_data(self, fgdb_path, feature, fields, rows):
        #self.logger.info("Populando feature "+ str(feature) +"...")

        feature = self._join_path(fgdb_path, feature)
        with self._arcpy.da.InsertCursor(feature, fields) as cursor:
            for row in rows:
                feature_row = []

                contains_field_shape = any('SHAPE@' in field for field in fields)

                if contains_field_shape == True:
                    feature_geometry = self._validate_geometry_key(row, fields)

                for key in fields:
                    if "SHAPE@" not in key:
                        feature_row.append(row[key])
                
                if contains_field_shape == True:
                    feature_row.append(feature_geometry)
                
                feature_row = tuple(feature_row)
                cursor.insertRow(feature_row)

    def export_to_json(self, fgdb_path, feature, path_out):
        self._arcpy.conversion.FeaturesToJSON(self._join_path(fgdb_path, feature), path_out, "FORMATTED", "NO_Z_VALUES", "NO_M_VALUES", "GEOJSON", "WGS84", "USE_FIELD_NAME")

    def export_to_csv(self, feature, path_out, name_out):
        self._arcpy.conversion.TableToTable(feature, path_out, name_out+".csv") 

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
    
    def _get_description_of_domain(self, value, domain_name, path, file_gdb):
        gdb = os.path.join(path, file_gdb)

        domains = self._arcpy.da.ListDomains(gdb)
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

    def get_violated_domain(self, value, path, file_gdb):
        return self._get_description_of_domain(value, "ViolatedConstraintDomain", path, file_gdb)
    
    def clear_objects(self, names):
        for name in names:
            feature_path = self.get_path_feature(name)
            self._arcpy.management.TruncateTable(feature_path)

    def copy_feature(self, feature_template, out_path, out_feature_name, geom_type = "Point"):
        spatial_reference = self._arcpy.Describe(feature_template).spatialReference
        self._arcpy.management.CreateFeatureclass(out_path=out_path, out_name=out_feature_name, geometry_type=geom_type, template=feature_template, has_m="DISABLED", has_z="DISABLED", spatial_reference=spatial_reference)

    def append_data(self, input_layers, output_layer):
        self._arcpy.Append_management(input_layers, output_layer, "NO_TEST")

    def count(self, feature):
        return int(self._arcpy.management.GetCount(feature)[0])

    def exists(self, feature):
        return self._arcpy.Exists(feature)