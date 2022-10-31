import arcpy
from arcpy.na import (AddLocations, AddVehicleRoutingProblemRoutes,
                      MakeVehicleRoutingProblemAnalysisLayer, Solve)

from core._constants import *
from core.instances.Feature import Feature
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

        routing_layer, name = self.create_routing_layer(CONFIGS.ROUTER)
        self.add_pois(poi=origens, name=name)
        self.add_pois(poi=destinos, name=name)
        self.add_routes(name=name)
        self.solve()
        print(destinos)

    def create_routing_layer(self, router):
        arcpy.env.workspace = self.temp_db.full_path
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
        ), "Vehicle Routing Problem"

    def add_pois(self, poi, name):
        fields_string = "Name # #;Description # #;ServiceTime # #;TimeWindowStart # #;TimeWindowEnd # #;MaxViolationTime # #;TimeWindowStart2 # #;TimeWindowEnd2 # #;MaxViolationTime2 # #;InboundArriveTime # #;OutboundDepartTime # #;DeliveryQuantity_1 # #;DeliveryQuantity_2 # #;DeliveryQuantity_3 # #;DeliveryQuantity_4 # #;DeliveryQuantity_5 # #;DeliveryQuantity_6 # #;DeliveryQuantity_7 # #;DeliveryQuantity_8 # #;DeliveryQuantity_9 # #;PickupQuantity_1 # #;PickupQuantity_2 # #;PickupQuantity_3 # #;PickupQuantity_4 # #;PickupQuantity_5 # #;PickupQuantity_6 # #;PickupQuantity_7 # #;PickupQuantity_8 # #;PickupQuantity_9 # #;Revenue # #;AssignmentRule # 3;RouteName # #;Sequence # #;CurbApproach # 0"
        AddLocations(
            name,
            "Orders",
            poi.full_path,
            fields_string,
            "5000 Meters",
            None,
            "Routing_Streets SHAPE;Routing_Streets_Override NONE;Routing_ND_Junctions NONE",
            "MATCH_TO_CLOSEST",
            "APPEND",
            "NO_SNAP",
            "5 Meters",
            "EXCLUDE",
            None,
            "ALLOW"
        )

    def add_routes(self, name):
        AddVehicleRoutingProblemRoutes(
            name,
            7,
            "Route",
            "1",
            "1",
            "08:00:00",
            "10:00:00",
            30,
            None,
            None,
            "# # 1 # #",
            None,
            "APPEND"
        )
    
    def solve(self, name):
        Solve(
            name,
            "HALT",
            "TERMINATE",
            None,
            ''
        )

if __name__ == '__main__':
    Main().main()
