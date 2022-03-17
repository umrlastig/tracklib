#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

import math
from tracklib.core import (Coords, Obs, Track, GPSTime)
import tracklib.algo.Analytics as Analytics
import tracklib.core.Utils as utils


class TestAlgoAnalyticsMethods(unittest.TestCase):
    
    def setUp (self):
        
        GPSTime.GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        self.trace1 = Track.Track([], 1)
        self.trace2 = Track.Track([], 1)

        # ---------------------------------------------------------------------
		
        c1 = Coords.ENUCoords(0, 0, 0)
        p1 = Obs.Obs(c1, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace1.addObs(p1)
        
        c2 = Coords.ENUCoords(10, 0, 0)
        p2 = Obs.Obs(c2, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:12"))
        self.trace1.addObs(p2)
        
        c3 = Coords.ENUCoords(10, 10, 0)
        p3 = Obs.Obs(c3, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:40"))
        self.trace1.addObs(p3)
        
        c4 = Coords.ENUCoords(10, 20, 0)
        p4 = Obs.Obs(c4, GPSTime.GPSTime.readTimestamp("2018-01-01 10:01:50"))
        self.trace1.addObs(p4)
		
        c5 = Coords.ENUCoords(0, 20, 0)
        p5 = Obs.Obs(c5, GPSTime.GPSTime.readTimestamp("2018-01-01 10:02:10"))
        self.trace1.addObs(p5)
		
        c6 = Coords.ENUCoords(0, 10, 0)
        p6 = Obs.Obs(c6, GPSTime.GPSTime.readTimestamp("2018-01-01 10:02:15"))
        self.trace1.addObs(p6)
		
        c7 = Coords.ENUCoords(0, 20, 0)
        p7 = Obs.Obs(c7, GPSTime.GPSTime.readTimestamp("2018-01-01 10:02:35"))
        self.trace1.addObs(p7)
		
        c8 = Coords.ENUCoords(5, 20, 0)
        p8 = Obs.Obs(c8, GPSTime.GPSTime.readTimestamp("2018-01-01 10:02:35"))
        self.trace1.addObs(p8)
		
        # ---------------------------------------------------------------------		
		
        c1 = Coords.ENUCoords(0, 0, 0)
        p1 = Obs.Obs(c1, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace2.addObs(p1)
		
        c2 = Coords.ENUCoords(0, 10, 0)
        p2 = Obs.Obs(c2, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:10"))
        self.trace2.addObs(p2)
		
        c3 = Coords.ENUCoords(0, 10, 0)
        p3 = Obs.Obs(c3, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:20"))
        self.trace2.addObs(p3)
		
        c4 = Coords.ENUCoords(0, 30, 0)
        p4 = Obs.Obs(c4, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:30"))
        self.trace2.addObs(p4)
		
		
    def testDS(self):
        self.assertLessEqual(3, 5)
    
    def testAbsCurv(self):
        self.assertLessEqual(3, 5)
        
    def testSpeed(self):
        self.assertLessEqual(3, 5)
    
    def testAcceleration(self):
        self.assertLessEqual(3, 5)
        
    def testAngleGeom(self):
		
        a = Analytics.anglegeom(self.trace1, 0)
        self.assertEqual(math.isnan(a), math.isnan(utils.NAN))
        
        a = Analytics.anglegeom(self.trace1, self.trace1.size() - 1)
        self.assertEqual(math.isnan(a), math.isnan(utils.NAN))
		
        a = Analytics.anglegeom(self.trace1, 1)
        self.assertTrue(abs(a - 90) < 0.000001)
		
        a = Analytics.anglegeom(self.trace1, 2)
        self.assertTrue(abs(a - 180) < 0.000001)
        
        a = Analytics.anglegeom(self.trace1, 3)
        self.assertTrue(abs(a - 90) < 0.000001)
		
        a = Analytics.anglegeom(self.trace1, 4)
        self.assertTrue(abs(a - 90) < 0.000001)
		
        a = Analytics.anglegeom(self.trace1, 5)
        self.assertTrue(abs(a - 0) < 0.000001)
		
        a = Analytics.anglegeom(self.trace1, 6)
        self.assertTrue(abs(a - 90) < 0.000001)
		
		
    def testCalculAngleOriente(self):
        
        a = Analytics.calculAngleOriente(self.trace1, 0)
        self.assertEqual(math.isnan(a), math.isnan(utils.NAN))
		
        a = Analytics.calculAngleOriente(self.trace1, self.trace1.size() - 1)
        self.assertEqual(math.isnan(a), math.isnan(utils.NAN))
		
        a = Analytics.calculAngleOriente(self.trace1, 1)
        self.assertTrue(abs(a + 90) < 0.000001)
        
        a = Analytics.calculAngleOriente(self.trace1, 2)
        self.assertTrue(abs(a - 180) < 0.000001)
        
        a = Analytics.calculAngleOriente(self.trace1, 3)
        self.assertTrue(abs(a + 90) < 0.000001)
		
        a = Analytics.calculAngleOriente(self.trace1, 4)
        self.assertTrue(abs(a + 90) < 0.000001)
		
        a = Analytics.calculAngleOriente(self.trace1, 5)
        self.assertTrue(abs(a - 0) < 0.000001)
		
        a = Analytics.calculAngleOriente(self.trace1, 6)
        self.assertTrue(abs(a - 90) < 0.000001)
		
		
    def testOrientation(self):
        
        a = Analytics.orientation(self.trace1, 0)
        self.assertEqual(math.isnan(a), math.isnan(utils.NAN))
		
        a = Analytics.orientation(self.trace1, self.trace1.size() - 1)
        self.assertEqual(math.isnan(a), math.isnan(utils.NAN))
		
        a = Analytics.orientation(self.trace1, 1)
        self.assertEqual(a, 1)
        
        a = Analytics.orientation(self.trace1, 2)
        self.assertEqual(a, 3)
        
        a = Analytics.orientation(self.trace1, 3)
        self.assertEqual(a, 3)
		
        a = Analytics.orientation(self.trace1, 4)
        self.assertEqual(a, 5)
		
        a = Analytics.orientation(self.trace1, 5)
        self.assertEqual(a, 7)
		
        a = Analytics.orientation(self.trace1, 6)
        self.assertEqual(a, 3)
		
		
    def testStopPointWithAccelerationCriteria(self):
		
        self.trace2.addAnalyticalFeature(Analytics.speed)
        self.trace2.addAnalyticalFeature(Analytics.acceleration)
        
        v1 = self.trace2.getObsAnalyticalFeature('speed', 1)
        a1 = self.trace2.getObsAnalyticalFeature('acceleration', 1)
        self.assertTrue(abs(v1 - 0.5) < 0.000001)
        self.assertTrue(abs(a1 + 0.0) < 0.000001)
        isSTP = Analytics.stop_point_with_acceleration_criteria(self.trace2, 1)
        print (v1, a1, isSTP)		
        self.assertEqual(isSTP, 0)
		
        v2 = self.trace2.getObsAnalyticalFeature('speed', 2)
        a2 = self.trace2.getObsAnalyticalFeature('acceleration', 2)
        self.assertTrue(abs(v2 - 1.0) < 0.000001)
        self.assertTrue(abs(a2 - 0.075) < 0.000001)
        isSTP = Analytics.stop_point_with_acceleration_criteria(self.trace2, 2)
        print (v2, a2, isSTP)		
        self.assertEqual(isSTP, 0)
        
		
    def testStopPointWithTimeWindowCriteria(self):
        self.assertLessEqual(3, 5)
    
	
if __name__ == '__main__':
    suite = unittest.TestSuite()
    #suite.addTest(TestAlgoAnalyticsMethods("testDS"))
    #suite.addTest(TestAlgoAnalyticsMethods("testAbsCurv"))
    #suite.addTest(TestAlgoAnalyticsMethods("testSpeed"))
    #suite.addTest(TestAlgoAnalyticsMethods("testAcceleration"))
    suite.addTest(TestAlgoAnalyticsMethods("testAngleGeom"))
    suite.addTest(TestAlgoAnalyticsMethods("testCalculAngleOriente"))
    suite.addTest(TestAlgoAnalyticsMethods("testOrientation"))
    suite.addTest(TestAlgoAnalyticsMethods("testStopPointWithAccelerationCriteria"))
    #suite.addTest(TestAlgoAnalyticsMethods("testStopPointWithTimeWindowCriteria"))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)

