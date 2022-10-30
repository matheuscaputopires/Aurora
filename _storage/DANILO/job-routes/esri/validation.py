import os
from config import Config

class Validation():
    def __init__(self, logger):
        self.logger = logger
        self._arcpy = __import__("arcpy") if Config().get_env() != "test" else None

    def validate_extension_network(self):
        self.logger.info("Validando extensões do ambiente...")
        # Check out Network Analyst license if available. Fail if the Network Analyst license is not available.
        if self._arcpy.CheckExtension("network") == "Available":
            self._arcpy.CheckOutExtension("network")
        else:
            raise self._arcpy.ExecuteError("Network Analyst Extension license is not available.")