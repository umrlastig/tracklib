# -*- coding: utf-8 -*-

import os.path
import unittest

class TestTracklib(unittest.TestCase):
    
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName) 
        self.resource_path = os.path.join(os.path.split(__file__)[0], "..")
        
        