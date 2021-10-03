# -*- coding: utf-8 -*-

import os.path
import unittest

from tracklib.core.GPSTime import GPSTime
from tracklib.io.FileReader import FileReader

from tracklib.algo.Segmentation import findStopsLocal

class TestAlgoSegmentationMethods(unittest.TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")

    def testFindStopsLocal(self):
        
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        chemin = os.path.join(self.resource_path, './data/trace1.dat')
        trace = FileReader.readFromFile(chemin, 2, 3, -1, 4, separator=",")
        stops = findStopsLocal(trace)
        self.assertLessEqual(3, 5)
    
    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoSegmentationMethods("testFindStopsLocal"))
    runner = unittest.TextTestRunner()
    runner.run(suite)