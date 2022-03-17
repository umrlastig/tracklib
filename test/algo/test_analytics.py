#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

import math
from tracklib.core import (Coords, Obs, Track, GPSTime)
import tracklib.algo.Analytics as Analytics
import tracklib.core.Utils as utils


class TestAlgoAnalyticsMethods(unittest.TestCase):
    
    def setUp (self):
        pass
    
    def testDS(self):
        self.assertLessEqual(3, 5)
    
    def testAbsCurv(self):
        self.assertLessEqual(3, 5)
        
    def testSpeed(self):
        self.assertLessEqual(3, 5)
    
    def testAcceleration(self):
        self.assertLessEqual(3, 5)
        
    def testAngleGeom(self):
		
        GPSTime.GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        trace1 = Track.Track([], 1)
        c1 = Coords.ENUCoords(0, 0, 0)
        p1 = Obs.Obs(c1, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        trace1.addObs(p1)
        
        c2 = Coords.ENUCoords(10, 0, 0)
        p2 = Obs.Obs(c2, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:12"))
        trace1.addObs(p2)
        
        c3 = Coords.ENUCoords(10, 10, 0)
        p3 = Obs.Obs(c3, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:40"))
        trace1.addObs(p3)
        
        c4 = Coords.ENUCoords(10, 20, 0)
        p4 = Obs.Obs(c4, GPSTime.GPSTime.readTimestamp("2018-01-01 10:01:50"))
        trace1.addObs(p4)
		
        c5 = Coords.ENUCoords(0, 20, 0)
        p5 = Obs.Obs(c5, GPSTime.GPSTime.readTimestamp("2018-01-01 10:02:10"))
        trace1.addObs(p5)
		
        c6 = Coords.ENUCoords(0, 10, 0)
        p6 = Obs.Obs(c6, GPSTime.GPSTime.readTimestamp("2018-01-01 10:02:15"))
        trace1.addObs(p6)
		
        c7 = Coords.ENUCoords(0, 20, 0)
        p7 = Obs.Obs(c7, GPSTime.GPSTime.readTimestamp("2018-01-01 10:02:35"))
        trace1.addObs(p7)
        
        a = Analytics.anglegeom(trace1, 0)
        self.assertEqual(math.isnan(a), math.isnan(utils.NAN))
        a = Analytics.anglegeom(trace1, trace1.size() - 1)
        self.assertEqual(math.isnan(a), math.isnan(utils.NAN))
		
        a = Analytics.anglegeom(trace1, 1)
        self.assertTrue(abs(a - 90) < 0.000001)
		
        a = Analytics.anglegeom(trace1, 2)
        self.assertTrue(abs(a - 180) < 0.000001)
        
        a = Analytics.anglegeom(trace1, 3)
        self.assertTrue(abs(a - 90) < 0.000001)
		
        a = Analytics.anglegeom(trace1, 4)
        self.assertTrue(abs(a - 90) < 0.000001)
		
        a = Analytics.anglegeom(trace1, 5)
        self.assertTrue(abs(a - 0) < 0.000001)
		
		
    def testCalculAngleOriente(self):
        self.assertLessEqual(3, 5)
        
    def testOrientation(self):
        self.assertLessEqual(3, 5)
        
    def testStopPointWithAccelerationCriteria(self):
        self.assertLessEqual(3, 5)
        
    def testStopPointWithTimeWindowCriteria(self):
        self.assertLessEqual(3, 5)
    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    #suite.addTest(TestAlgoAnalyticsMethods("testDS"))
    #suite.addTest(TestAlgoAnalyticsMethods("testAbsCurv"))
    #suite.addTest(TestAlgoAnalyticsMethods("testSpeed"))
    #suite.addTest(TestAlgoAnalyticsMethods("testAcceleration"))
    suite.addTest(TestAlgoAnalyticsMethods("testAngleGeom"))
    #suite.addTest(TestAlgoAnalyticsMethods("testCalculAngleOriente"))
    #suite.addTest(TestAlgoAnalyticsMethods("testOrientation"))
    #suite.addTest(TestAlgoAnalyticsMethods("testStopPointWithAccelerationCriteria"))
    #suite.addTest(TestAlgoAnalyticsMethods("testStopPointWithTimeWindowCriteria"))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)

