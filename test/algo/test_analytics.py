#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

import math
from numpy import pi

#import tracklib
#from tracklib.core import ENUCoords, Bbox, Polygon

from tracklib import (Obs, ObsTime, ENUCoords, NAN,
                      speed, acceleration, ds, heading, slope,
                      anglegeom, orientation, calculAngleOriente)
from tracklib.core import Track




class TestAlgoAnalyticsMethods(unittest.TestCase):
    
    def setUp (self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        self.trace1 = Track([], 1)
        self.trace2 = Track([], 1)
        self.trace3 = Track([], 1)

        # ---------------------------------------------------------------------
		
        p1 = Obs(ENUCoords(0, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace1.addObs(p1)
        
        p2 = Obs(ENUCoords(10, 0, 10), ObsTime.readTimestamp("2018-01-01 10:00:12"))
        self.trace1.addObs(p2)
        
        p3 = Obs(ENUCoords(10, 10, 10), ObsTime.readTimestamp("2018-01-01 10:00:40"))
        self.trace1.addObs(p3)
        
        p4 = Obs(ENUCoords(10, 20, 15), ObsTime.readTimestamp("2018-01-01 10:01:50"))
        self.trace1.addObs(p4)
		
        p5 = Obs(ENUCoords(0, 20, 10), ObsTime.readTimestamp("2018-01-01 10:02:10"))
        self.trace1.addObs(p5)
		
        p6 = Obs(ENUCoords(0, 10, 0), ObsTime.readTimestamp("2018-01-01 10:02:15"))
        self.trace1.addObs(p6)
		
        p7 = Obs(ENUCoords(0, 20, 0), ObsTime.readTimestamp("2018-01-01 10:02:35"))
        self.trace1.addObs(p7)
		
        p8 = Obs(ENUCoords(5, 20, 0), ObsTime.readTimestamp("2018-01-01 10:02:35"))
        self.trace1.addObs(p8)
		
        # ---------------------------------------------------------------------		
		
        p1 = Obs(ENUCoords(0, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace2.addObs(p1)
		
        p2 = Obs(ENUCoords(0, 10, 0), ObsTime.readTimestamp("2018-01-01 10:00:10"))
        self.trace2.addObs(p2)
		
        p3 = Obs(ENUCoords(0, 10, 0), ObsTime.readTimestamp("2018-01-01 10:00:20"))
        self.trace2.addObs(p3)
		
        p4 = Obs(ENUCoords(0, 30, 0), ObsTime.readTimestamp("2018-01-01 10:00:30"))
        self.trace2.addObs(p4)
		
        self.trace2.addAnalyticalFeature(speed)
        self.trace2.addAnalyticalFeature(acceleration)
        
        
        # ---------------------------------------------------------------------		
		
        p1 = Obs(ENUCoords(0, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace3.addObs(p1)
		
        p2 = Obs(ENUCoords(0, 10, 0), ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace3.addObs(p2)
		
        p3 = Obs(ENUCoords(0, 10, 0), ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace3.addObs(p3)
		
        p4 = Obs(ENUCoords(0, 30, 0), ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace3.addObs(p4)
		
        self.trace3.addAnalyticalFeature(speed)
        self.trace3.addAnalyticalFeature(acceleration)
		
		
    def testDS(self):
        self.trace3.addAnalyticalFeature(ds)
        ds30 = self.trace3.getObsAnalyticalFeature('ds', 0)
        self.assertEqual(ds30, 0)
        
        ds31 = self.trace3.getObsAnalyticalFeature('ds', 1)
        self.assertEqual(ds31, self.trace3.getObs(1).distanceTo(self.trace3.getObs(0)))
        
        ds32 = self.trace3.getObsAnalyticalFeature('ds', 2)
        self.assertEqual(ds32, self.trace3.getObs(2).distanceTo(self.trace3.getObs(1)))
        
        ds33 = self.trace3.getObsAnalyticalFeature('ds', 3)
        self.assertEqual(ds33, self.trace3.getObs(3).distanceTo(self.trace3.getObs(2)))
        
    def testHeading(self):
        
        self.trace1.addAnalyticalFeature(heading)
        
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
        self.assertEqual(math.isnan(a0), math.isnan(NAN))

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
        
    def testOrientation(self):
        
        a = orientation(self.trace1, 0)
        self.assertEqual(a, 1)
		
        a = orientation(self.trace1, self.trace1.size() - 1)
        self.assertEqual(a, 1)
		
        a = orientation(self.trace1, 1)
        self.assertEqual(a, 1)
        
        a = orientation(self.trace1, 2)
        self.assertEqual(a, 3)
        
        a = orientation(self.trace1, 3)
        self.assertEqual(a, 3)
		
        a = orientation(self.trace1, 4)
        self.assertEqual(a, 5)
		
        a = orientation(self.trace1, 5)
        self.assertEqual(a, 7)
		
        a = orientation(self.trace1, 6)
        self.assertEqual(a, 3)
        
    def testSlope(self):
        
        self.trace1.addAnalyticalFeature(slope)
        
        s0 = self.trace1.getObsAnalyticalFeature('slope', 0)
        s1 = self.trace1.getObsAnalyticalFeature('slope', 1)
        s2 = self.trace1.getObsAnalyticalFeature('slope', 2)
        s3 = self.trace1.getObsAnalyticalFeature('slope', 3)
        s4 = self.trace1.getObsAnalyticalFeature('slope', 4)
        s5 = self.trace1.getObsAnalyticalFeature('slope', 5)
        s6 = self.trace1.getObsAnalyticalFeature('slope', 6)
        
        self.assertEqual(math.isnan(s0), math.isnan(NAN))
        self.assertEqual(s1, 45.0)
        self.assertEqual(s2, 0.0)
        self.assertTrue(abs(s3 - 26.56) < 0.01)
        self.assertTrue(abs(s4 + 26.56) < 0.01)
        self.assertTrue(abs(s5 + 45.0) < 0.01)
        self.assertEqual(s6, 0.0)
		
		
    def testAngleGeom(self):
		
        a = anglegeom(self.trace1, 0)
        self.assertEqual(math.isnan(a), math.isnan(NAN))
        
        a = anglegeom(self.trace1, self.trace1.size() - 1)
        self.assertEqual(math.isnan(a), math.isnan(NAN))
		
        a = anglegeom(self.trace1, 1)
        self.assertTrue(abs(a - pi/2) < 0.000001)
		
        a = anglegeom(self.trace1, 2)
        self.assertTrue(abs(a - pi) < 0.000001)
        
        a = anglegeom(self.trace1, 3)
        self.assertTrue(abs(a - pi/2) < 0.000001)
		
        a = anglegeom(self.trace1, 4)
        self.assertTrue(abs(a - pi/2) < 0.000001)
		
        a = anglegeom(self.trace1, 5)
        self.assertTrue(abs(a - 0) < 0.000001)
		
        a = anglegeom(self.trace1, 6)
        self.assertTrue(abs(a - pi/2) < 0.000001)
		
		
    def testCalculAngleOriente(self):
        
        a = calculAngleOriente(self.trace1, 0)
        self.assertEqual(math.isnan(a), math.isnan(NAN))
		
        a = calculAngleOriente(self.trace1, self.trace1.size() - 1)
        self.assertEqual(math.isnan(a), math.isnan(NAN))
		
        a = calculAngleOriente(self.trace1, 1)
        self.assertTrue(abs(a + 90) < 0.000001)
        
        a = calculAngleOriente(self.trace1, 2)
        self.assertTrue(abs(a - 180) < 0.000001)
        
        a = calculAngleOriente(self.trace1, 3)
        self.assertTrue(abs(a + 90) < 0.000001)
		
        a = calculAngleOriente(self.trace1, 4)
        self.assertTrue(abs(a + 90) < 0.000001)
		
        a = calculAngleOriente(self.trace1, 5)
        self.assertTrue(abs(a - 0) < 0.000001)
		
        a = calculAngleOriente(self.trace1, 6)
        self.assertTrue(abs(a - 90) < 0.000001)
		
		
if __name__ == '__main__':
    
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoAnalyticsMethods("testDS"))
    suite.addTest(TestAlgoAnalyticsMethods("testHeading"))
    suite.addTest(TestAlgoAnalyticsMethods("testSpeed"))
    suite.addTest(TestAlgoAnalyticsMethods("testAcceleration"))
    suite.addTest(TestAlgoAnalyticsMethods("testOrientation"))
    suite.addTest(TestAlgoAnalyticsMethods("testSlope"))
    suite.addTest(TestAlgoAnalyticsMethods("testAngleGeom"))
    suite.addTest(TestAlgoAnalyticsMethods("testCalculAngleOriente"))
    runner = unittest.TextTestRunner()
    runner.run(suite)

