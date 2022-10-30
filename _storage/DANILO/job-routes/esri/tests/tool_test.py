from unittest import TestCase
from mock import patch, MagicMock
from esri.tool import Tool
import os

@patch('esri.tool.Config')
class TestTool(TestCase):

    def test_intersect(self, mock_Config):

        mock_Config.return_value.get_env = MagicMock(return_value="test")

        log_fake = MagicMock(return_value=LogFake())
        tool = Tool(log_fake)
        tool._arcpy = MagicMock(return_value=ArcpyFake())

        in_feature_1 = "ft_company"
        in_feature_2 = "ft_work_area"
        out_feature_class = "ft_intersect"
        tool.intersect(in_feature_1, in_feature_2, out_feature_class)

        tool._arcpy.analysis.Intersect.assert_called_with(
            "ft_company #;ft_work_area #",
            "ft_intersect",
            "ALL", None, "INPUT")
    
    def test_geocode(self, mock_Config):
        mock_Config.return_value.get_env = MagicMock(return_value="test")
        
        PARAMS_FAKE = {
            "path_locator": "path/folder/locator",
            "company_geocode": "GeocodificacaoEmpresas"
        }

        mock_Config.return_value.get_params = MagicMock(return_value=PARAMS_FAKE)
    
        log_fake = MagicMock(return_value=LogFake())
        tool = Tool(log_fake)
        tool._arcpy = MagicMock(return_value=ArcpyFake())

        path_fake = 'path_gdb'
        path_company_to_geocod = os.path.join(path_fake, PARAMS_FAKE['company_geocode'])
        path_company_geocoded = os.path.join(path_fake, "GEOCODE_RESULT")
        tool._arcpy.geocoding.GeocodeAddresses = MagicMock(return_value=None)

        tool.geocode(path_company_to_geocod, path_company_geocoded)

        tool._arcpy.geocoding.GeocodeAddresses.assert_called_with(
            path_company_to_geocod,
            PARAMS_FAKE['path_locator'],
            "'Single Line Input' enderecocompleto VISIBLE NONE",
            path_company_geocoded,
            "STATIC", None, "ROUTING_LOCATION", "Subaddress;'Point Address';'Street Address';'Distance Marker';'Street Name'", "ALL")


class ArcpyFake:
    pass

class LogFake:
    pass