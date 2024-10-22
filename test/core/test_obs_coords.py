# -*- coding: utf-8 -*-
from unittest import TestCase, TestSuite, TextTestRunner

from math import degrees 
from tracklib import (ENUCoords)

class TestCoords(TestCase):
    '''
    '''
    __epsilon = 0.001
    
    def test_azimuth(self):
        c1 = ENUCoords(0.0, 0.0, 0)
        c2 = ENUCoords(1.0, 0.0, 0)
        self.assertEqual(degrees(c1.azimuthTo(c2)), 90.0)
        self.assertEqual(degrees(c2.azimuthTo(c1)), -90.0)
        
        c1 = ENUCoords(25.0, 45.0, 0)
        c2 = ENUCoords(75.0, 100.0, 0)
        self.assertTrue(abs(degrees(c1.azimuthTo(c2)) - 42.273) < self.__epsilon)
        self.assertTrue(abs(degrees(c2.azimuthTo(c1)) - 222.273 + 360) < self.__epsilon)
    


if __name__ == '__main__':
    suite = TestSuite()
    
    suite.addTest(TestCoords("test_azimuth"))
    
    runner = TextTestRunner()
    runner.run(suite)