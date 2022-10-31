# -*- encoding: utf-8 -*-
#!/usr/bin/python
import os

import yaml
from arcpy import Exists, SpatialReference
from arcpy.management import Delete
from core._constants import *
from core._logs import *
from core.instances.Database import Database
from core.libs.Base import BasePath
from core.libs.CustomExceptions import DeletionError


class BaseProperties(BasePath):
    _temp_db: Database = None
    _image_storage: str = None

    def __init__(self, *args, **kwargs):
        self.load_env_variables()
        super().__init__(*args, **kwargs)

    def load_env_variables(self):
        env_file = self.get_files_by_extension(ROOT_DIR,'env.yaml')
        for file in env_file:
            with open(file) as f:
                env_vars = yaml.safe_load(f)
                for var in env_vars:
                    if env_vars.get(var) and env_vars.get(var) != 'None':
                        os.environ[var]=str(env_vars.get(var))

    @property
    def default_sr(self) -> SpatialReference:
        return SpatialReference(int(os.environ.get('DEFAULT_SR', 4326))) # WGS84
    
    @property
    def delete_temp_files_while_processing(self) -> bool:
        return os.environ.get('DELETE_TEMP_FILES_WHILE_PROCESSING', False) == 'True'

    @property
    def delete_temp_files(self) -> bool:
        return os.environ.get('DELETE_TEMP_FILES', False) == 'True'

    @property
    def temp_dir(self) -> str:
        temp_dir = os.environ.get('TEMP_DIR')
        if not temp_dir:
            return TEMP_DIR
        return temp_dir

    @property
    def temp_db(self) -> Database:
        if not self._temp_db:
            temp_db_folder = os.environ.get('TEMP_DB', self.temp_dir)
            self._temp_db = Database(path=temp_db_folder, name=os.path.basename(temp_db_folder))
        return self._temp_db

    @property
    def n_cores(self) -> int:
        n_cores = int(os.environ.get('N_CORES', 0))
        if not n_cores:
            n_cores = os.cpu_count()
        return n_cores
        
    @property
    def use_arcpy_append(self) -> bool:
        return os.environ.get('USE_ARCPY_APPEND', 'True') == 'True'

    def delete_temporary_content(self) -> None:
        if self.delete_temp_files:
            if Exists(self.temp_dir):
                try:
                    aprint(f'Removendo arquivos temporários de processamento:\n{self.temp_dir}')
                    Delete(self.temp_dir)
                except Exception as e:
                    DeletionError(path=self.temp_dir)
            if Exists(self.temp_db):
                try:
                    Delete(self.temp_db)
                except Exception as e:
                    DeletionError(path=self.temp_db)
