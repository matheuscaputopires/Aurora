from unittest import TestCase
from helper.errors import Error

class TestError(TestCase):
    
    def test__init__(self):
        msg = 'Error'
        self.assertRaises(Exception, Error(msg))