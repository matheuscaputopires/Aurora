# -*- encoding: utf-8 -*-
#!/usr/bin/python
import os

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

    @property
    def default_sr(self) -> SpatialReference:
        return SpatialReference(os.environ.get('DEFAULT_SR', 3857)) # WGS84 Web Mercator
    
    @property
    def delete_temp_files_while_processing(self) -> bool:
        return os.environ.get('DELETE_TEMP_FILES_WHILE_PROCESSING', False) == 'True'

    @property
    def delete_temp_files(self) -> bool:
        return os.environ.get('DELETE_TEMP_FILES', False) == 'True'

    @property
    def temp_dir(self) -> str:
        return os.environ.get('TEMP_DIR', TEMP_DIR)

    @property
    def temp_db(self) -> Database:
        if not self._temp_db:
            self._temp_db = Database(path=os.environ.get('TEMP_DB', self.temp_dir))
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
