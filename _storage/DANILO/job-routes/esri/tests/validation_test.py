from unittest import TestCase
from mock import patch, MagicMock
from esri.validation import Validation

@patch('esri.validation.Config')
class TestValidation(TestCase):

    def test_extension_network_is_available(self, mock_Config):

        mock_Config.return_value.get_env = MagicMock(return_value="test")

        log_fake = MagicMock(return_value=LogFake())
        validation = Validation(log_fake)
        validation._arcpy = MagicMock(return_value=ArcpyFake())

        validation._arcpy.CheckExtension = MagicMock(return_value="Available")
        validation._arcpy.CheckOutExtension = MagicMock(return_value=[True])

        validation.validate_extension_network()

        validation._arcpy.CheckExtension.assert_called_with("network")
        validation._arcpy.CheckOutExtension.assert_called_with("network")

    def test_extension_network_not_available(self, mock_Config):

        mock_Config.return_value.get_env = MagicMock(return_value="test")

        log_fake = MagicMock(return_value=LogFake())
        validation = Validation(log_fake)
        validation._arcpy = MagicMock(return_value=ArcpyFake())

        validation._arcpy.CheckExtension = MagicMock(return_value=None)

        with self.assertRaises(BaseException):
            validation.validate_extension_network()

        validation._arcpy.CheckExtension.assert_called_with("network")
        validation._arcpy.ExecuteError.assert_called_with("Network Analyst Extension license is not available.")        


class ArcpyFake:
    pass

class LogFake:
    pass