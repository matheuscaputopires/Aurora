from config import Config

class Tool():
    def __init__(self, logger):
        self.logger = logger
        self.params = Config().get_params()
        self._arcpy = __import__("arcpy") if Config().get_env() != "test" else None

    def intersect(self, in_feature_1, in_feature_2, out_feature_class):
        self._arcpy.analysis.Intersect(
            "%s #;%s #" % (in_feature_1, in_feature_2),
            out_feature_class,
            "ALL", None, "INPUT")
    
    def geocode(self, table_address_geocode, out_feature_class):
        self.logger.info("Geocodificando endereços")
        self._arcpy.geocoding.GeocodeAddresses(
            table_address_geocode,
            self.params['path_locator'],
            "'Single Line Input' enderecocompleto VISIBLE NONE",
            out_feature_class,
            "STATIC", None, "ROUTING_LOCATION", "Subaddress;'Point Address';'Street Address';'Distance Marker';'Street Name'", "ALL")