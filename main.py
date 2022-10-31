from core.instances.Feature import Feature
from core._constants import *
from arcpy.na import MakeVehicleRoutingProblemAnalysisLayer
from core.libs.BaseProperties import BaseProperties

class Settings:
    ORIGENS = os.path.join(ROOT_DIR, r'Input\Sample\origens.csv')
    DESTINOS = os.path.join(ROOT_DIR, r'Input\Sample\destinos.csv')
    ROUTER = r'C:\Projects\Imagem\Aurora\Aurora_Projeto\FGDB\FGDB\StreetMap_Data\LatinAmerica.gdb\Routing\Routing_ND'

CONFIGS = Settings()

class Main(BaseProperties):
    def main(self):
        origens = Feature(CONFIGS.ORIGENS)
        origens.geocode_addresses()
        
        destinos = Feature(CONFIGS.DESTINOS)
        destinos.geocode_addresses()

        routing_layer = self.create_routing_layer(CONFIGS.ROUTER)
        
        print(destinos)

    def create_routing_layer(self, router):
        self.temp_db
        return MakeVehicleRoutingProblemAnalysisLayer(
            router,
            "Vehicle Routing Problem",
            "Driving Time",
            "Minutes",
            "Miles",
            None,
            "LOCAL_TIME_AT_LOCATIONS",
            "ALONG_NETWORK",
            "Medium",
            "Medium",
            "DIRECTIONS",
            "CLUSTER",
            "HALT"
        )

if __name__ == '__main__':
    Main().main()