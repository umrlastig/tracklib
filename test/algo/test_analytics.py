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
        self.trace3 = Track.Track([], 1)

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
		
        self.trace2.addAnalyticalFeature(Analytics.speed)
        self.trace2.addAnalyticalFeature(Analytics.acceleration)
        
        
        # ---------------------------------------------------------------------		
		
        c1 = Coords.ENUCoords(0, 0, 0)
        p1 = Obs.Obs(c1, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace3.addObs(p1)
		
        c2 = Coords.ENUCoords(0, 10, 0)
        p2 = Obs.Obs(c2, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace3.addObs(p2)
		
        c3 = Coords.ENUCoords(0, 10, 0)
        p3 = Obs.Obs(c3, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace3.addObs(p3)
		
        c4 = Coords.ENUCoords(0, 30, 0)
        p4 = Obs.Obs(c4, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace3.addObs(p4)
		
        self.trace3.addAnalyticalFeature(Analytics.speed)
        self.trace3.addAnalyticalFeature(Analytics.acceleration)
		
		
    def testDS(self):
        self.trace3.addAnalyticalFeature(Analytics.ds)
        ds30 = self.trace3.getObsAnalyticalFeature('ds', 0)
        self.assertEqual(ds30, 0)
        
        ds31 = self.trace3.getObsAnalyticalFeature('ds', 1)
        self.assertEqual(ds31, self.trace3.getObs(1).distanceTo(self.trace3.getObs(0)))
        
        ds32 = self.trace3.getObsAnalyticalFeature('ds', 2)
        self.assertEqual(ds32, self.trace3.getObs(2).distanceTo(self.trace3.getObs(1)))
        
        ds33 = self.trace3.getObsAnalyticalFeature('ds', 3)
        self.assertEqual(ds33, self.trace3.getObs(3).distanceTo(self.trace3.getObs(2)))
        
    def testHeading(self):
        self.trace1.addAnalyticalFeature(Analytics.heading)
        
        s0 = self.trace1.getObsAnalyticalFeature('heading', 0)
        s1 = self.trace1.getObsAnalyticalFeature('heading', 1)
        s2 = self.trace1.getObsAnalyticalFeature('heading', 2)
        s3 = self.trace1.getObsAnalyticalFeature('heading', 3)
        s4 = self.trace1.getObsAnalyticalFeature('heading', 4)
        s5 = self.trace1.getObsAnalyticalFeature('heading', 5)
        s6 = self.trace1.getObsAnalyticalFeature('heading', 6)
        s7 = self.trace1.getObsAnalyticalFeature('heading', 7)
        
        self.assertEqual(s0, s1)
        self.assertEqual(s1, math.atan2(10, 0))
        self.assertEqual(s2, math.atan2(0, 10))
        self.assertEqual(s3, math.atan2(0, 10))
        self.assertEqual(s4, math.atan2(-10, 0))
        self.assertEqual(s5, math.atan2(0, -10))
        self.assertEqual(s6, math.atan2(0, 10))
        self.assertEqual(s7, math.atan2(5, 0))
        
    def testAbsCurv(self):
        
        self.trace1.addAnalyticalFeature(Analytics.abs_curv)
        s1 = self.trace1.getObsAnalyticalFeature('abs_curv', 3)
        self.assertEqual(s1, [0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 65.0])
        
        self.trace2.addAnalyticalFeature(Analytics.abs_curv)
        s2 = self.trace2.getObsAnalyticalFeature('abs_curv', 3)
        self.assertEqual(s2, [0, 10.0, 10.0, 30.0])
        
    def testSpeed(self):
        
        v0 = self.trace2.getObsAnalyticalFeature('speed', 0)
        self.assertTrue(abs(v0 - 10 / 10) < 0.000001)

        v1 = self.trace2.getObsAnalyticalFeature('speed', 1)
        self.assertTrue(abs(v1 - 10 / 20) < 0.000001)
        
        v2 = self.trace2.getObsAnalyticalFeature('speed', 2)
        self.assertTrue(abs(v2 - 20 / 20) < 0.000001)
    
        v3 = self.trace2.getObsAnalyticalFeature('speed', 3)
        self.assertTrue(abs(v3 - 20 / 10) < 0.000001)
        
        v30 = self.trace3.getObsAnalyticalFeature('speed', 0)
        self.assertTrue(math.isnan(v30))
        v31 = self.trace3.getObsAnalyticalFeature('speed', 1)
        self.assertTrue(math.isnan(v31))
        v32 = self.trace3.getObsAnalyticalFeature('speed', 2)
        self.assertTrue(math.isnan(v32))
        v33 = self.trace3.getObsAnalyticalFeature('speed', 3)
        self.assertTrue(math.isnan(v33))


    def testAcceleration(self):
		
        v0 = self.trace2.getObsAnalyticalFeature('speed', 0)
        v1 = self.trace2.getObsAnalyticalFeature('speed', 1)
        v2 = self.trace2.getObsAnalyticalFeature('speed', 2)
        v3 = self.trace2.getObsAnalyticalFeature('speed', 3)
        
        a0 = self.trace2.getObsAnalyticalFeature('acceleration', 0)
        self.assertEqual(math.isnan(a0), math.isnan(utils.NAN))

        a1 = self.trace2.getObsAnalyticalFeature('acceleration', 1)
        self.assertTrue(abs(a1 - (v2-v0)/20) < 0.000001)
		
        a2 = self.trace2.getObsAnalyticalFeature('acceleration', 2)
        self.assertTrue(abs(a2 - (v3-v1)/20) < 0.000001)
		
        a3 = self.trace2.getObsAnalyticalFeature('acceleration', 3)
        self.assertTrue(abs(a3 - (v3-v2)/10) < 0.000001)
        
        v30 = self.trace3.getObsAnalyticalFeature('acceleration', 0)
        self.assertTrue(math.isnan(v30))
        v31 = self.trace3.getObsAnalyticalFeature('acceleration', 1)
        self.assertTrue(math.isnan(v31))
        v32 = self.trace3.getObsAnalyticalFeature('acceleration', 2)
        self.assertTrue(math.isnan(v32))
        v33 = self.trace3.getObsAnalyticalFeature('acceleration', 3)
        self.assertTrue(math.isnan(v33))
		
		
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
        self.assertEqual(a, 1)
		
        a = Analytics.orientation(self.trace1, self.trace1.size() - 1)
        self.assertEqual(a, 1)
		
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
		
		
    # def testStopPointWithAccelerationCriteria(self):
	# 	
    #     v1 = self.trace2.getObsAnalyticalFeature('speed', 1)
    #     a1 = self.trace2.getObsAnalyticalFeature('acceleration', 1)
    #     self.assertTrue(abs(v1 - 0.5) < 0.000001)
    #     self.assertTrue(abs(a1 + 0.0) < 0.000001)
    #     isSTP = Analytics.stop_point_with_acceleration_criteria(self.trace2, 1)
    #     #print (v1, a1, isSTP)		
    #     self.assertEqual(isSTP, 0)
	# 	
    #     v2 = self.trace2.getObsAnalyticalFeature('speed', 2)
    #     a2 = self.trace2.getObsAnalyticalFeature('acceleration', 2)
    #     self.assertTrue(abs(v2 - 1.0) < 0.000001)
    #     self.assertTrue(abs(a2 - 0.075) < 0.000001)
    #     isSTP = Analytics.stop_point_with_acceleration_criteria(self.trace2, 2)
    #     #print (v2, a2, isSTP)		
    #     self.assertEqual(isSTP, 0)
        
		
    # def testStopPointWithTimeWindowCriteria(self):
    #     self.assertLessEqual(3, 5)
    
	
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoAnalyticsMethods("testDS"))
    suite.addTest(TestAlgoAnalyticsMethods("testAbsCurv"))
    suite.addTest(TestAlgoAnalyticsMethods("testHeading"))
    suite.addTest(TestAlgoAnalyticsMethods("testSpeed"))
    suite.addTest(TestAlgoAnalyticsMethods("testAcceleration"))
    suite.addTest(TestAlgoAnalyticsMethods("testAngleGeom"))
    suite.addTest(TestAlgoAnalyticsMethods("testCalculAngleOriente"))
    suite.addTest(TestAlgoAnalyticsMethods("testOrientation"))
    
    #suite.addTest(TestAlgoAnalyticsMethods("testStopPointWithAccelerationCriteria"))
    #suite.addTest(TestAlgoAnalyticsMethods("testStopPointWithTimeWindowCriteria"))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)

