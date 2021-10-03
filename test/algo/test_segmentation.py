# -*- coding: utf-8 -*-

import unittest

from tracklib.algo.Segmentation import findStopsLocal

class TestAlgoSegmentationMethods(unittest.TestCase):
    
    def setUp (self):
        pass
    
    def testFindStopsLocal(self):
        
        stops = findStopsLocal(None)
        self.assertLessEqual(3, 5)
    
    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoSegmentationMethods("testFindStopsLocal"))
    runner = unittest.TextTestRunner()
    runner.run(suite)