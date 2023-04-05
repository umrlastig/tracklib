# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

#import math
from tracklib.core import (Obs, Track, ObsTime)
from tracklib.core import ObsCoords as Coords
import tracklib.algo.Analytics as Analytics
from tracklib.algo.Analytics import BIAF_ABS_CURV
import tracklib.algo.Cinematics as Cinematics

#import tracklib.core.Utils as utils


class TestAlgoCinematicsMethods(unittest.TestCase):
    
    __epsilon = 0.001
    
    def setUp (self):
        
        ObsTime.ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        self.trace1 = Track.Track([], 1)

        c1 = Coords.ENUCoords(0, 0, 0)
        p1 = Obs.Obs(c1, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace1.addObs(p1)
        
        c2 = Coords.ENUCoords(10, 0, 0)
        p2 = Obs.Obs(c2, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:12"))
        self.trace1.addObs(p2)
        
        c3 = Coords.ENUCoords(10, 10, 0)
        p3 = Obs.Obs(c3, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:40"))
        self.trace1.addObs(p3)
        
        c4 = Coords.ENUCoords(20, 10, 0)
        p4 = Obs.Obs(c4, ObsTime.ObsTime.readTimestamp("2018-01-01 10:01:50"))
        self.trace1.addObs(p4)
		
        c5 = Coords.ENUCoords(20, 20, 0)
        p5 = Obs.Obs(c5, ObsTime.ObsTime.readTimestamp("2018-01-01 10:02:10"))
        self.trace1.addObs(p5)
        
        c6 = Coords.ENUCoords(30, 20, 0)
        p6 = Obs.Obs(c6, ObsTime.ObsTime.readTimestamp("2018-01-01 10:02:35"))
        self.trace1.addObs(p6)
        
        c7 = Coords.ENUCoords(30, 30, 0)
        p7 = Obs.Obs(c7, ObsTime.ObsTime.readTimestamp("2018-01-01 10:02:43"))
        self.trace1.addObs(p7)
        
        c8 = Coords.ENUCoords(40, 30, 0)
        p8 = Obs.Obs(c8, ObsTime.ObsTime.readTimestamp("2018-01-01 10:02:55"))
        self.trace1.addObs(p8)
        
        c9 = Coords.ENUCoords(60, 30, 0)
        p9 = Obs.Obs(c9, ObsTime.ObsTime.readTimestamp("2018-01-01 10:03:25"))
        self.trace1.addObs(p9)
        
        # -----------------
        
        ObsTime.ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        self.trace2 = Track.Track([], 1)

        c1 = Coords.ENUCoords(0, 0, 0)
        p1 = Obs.Obs(c1, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace2.addObs(p1)
        
        c2 = Coords.ENUCoords(10, 0, 10)
        p2 = Obs.Obs(c2, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:12"))
        self.trace2.addObs(p2)
        
        c3 = Coords.ENUCoords(10, 10, 10)
        p3 = Obs.Obs(c3, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:40"))
        self.trace2.addObs(p3)
        
        c4 = Coords.ENUCoords(10, 20, 15)
        p4 = Obs.Obs(c4, ObsTime.ObsTime.readTimestamp("2018-01-01 10:01:50"))
        self.trace2.addObs(p4)
		
        c5 = Coords.ENUCoords(0, 20, 10)
        p5 = Obs.Obs(c5, ObsTime.ObsTime.readTimestamp("2018-01-01 10:02:10"))
        self.trace2.addObs(p5)
		
        c6 = Coords.ENUCoords(0, 10, 0)
        p6 = Obs.Obs(c6, ObsTime.ObsTime.readTimestamp("2018-01-01 10:02:15"))
        self.trace2.addObs(p6)
		
        c7 = Coords.ENUCoords(0, 20, 0)
        p7 = Obs.Obs(c7, ObsTime.ObsTime.readTimestamp("2018-01-01 10:02:35"))
        self.trace2.addObs(p7)
		
        c8 = Coords.ENUCoords(5, 20, 0)
        p8 = Obs.Obs(c8, ObsTime.ObsTime.readTimestamp("2018-01-01 10:02:35"))
        self.trace2.addObs(p8)
        

    def testAFInflexion(self):
        self.trace1.plot()
        self.trace1.addAnalyticalFeature(Cinematics.inflection)
        afIsInflexion = self.trace1.getAnalyticalFeature('inflection')
        #print (afIsInflexion)
        self.assertEqual(afIsInflexion[0], 0)
        self.assertEqual(afIsInflexion[1], 0)
        self.assertEqual(afIsInflexion[2], 1)
        self.assertEqual(afIsInflexion[3], 1)
        self.assertEqual(afIsInflexion[4], 1)
        self.assertEqual(afIsInflexion[5], 1)
        self.assertEqual(afIsInflexion[6], 0)
        self.assertEqual(afIsInflexion[7], 0)


    def testAFvertex(self):
        self.trace1.addAnalyticalFeature(Cinematics.inflection)
        self.trace1.addAnalyticalFeature(Cinematics.vertex)
        afVertex = self.trace1.getAnalyticalFeature('vertex')
        #print (afVertex)
        self.assertEqual(afVertex[0], 0)
        self.assertEqual(afVertex[1], 1)
        self.assertEqual(afVertex[2], 0)
        self.assertEqual(afVertex[3], 0)
        self.assertEqual(afVertex[4], 0)
        self.assertEqual(afVertex[5], 0)
        self.assertEqual(afVertex[6], 0)
        self.assertEqual(afVertex[7], 0)

        
    def testSmoothedSpeedCalculation(self):
        Cinematics.smoothed_speed_calculation(self.trace1, 2)
        speeds = self.trace1.getAnalyticalFeature('speed')
        Cinematics.computeAbsCurv(self.trace1)
        
        ds8 = self.trace1.getObsAnalyticalFeature('abs_curv', 8)
        ds4 = self.trace1.getObsAnalyticalFeature('abs_curv', 4)
        ds = ds8 - ds4
        dt = self.trace1.getObs(8).timestamp - self.trace1.getObs(4).timestamp

        err = abs(speeds[6] - ds/dt)
        self.assertLessEqual(err, self.__epsilon, 'erreur pour 6')
        
        
    def testCompareAbsCurv(self):
        speeds1 = Cinematics.computeAbsCurv(self.trace1)
        #print (speeds1)
        
        Cinematics.computeAbsCurv(self.trace1)
        for i in range(self.trace1.size()):
            self.assertEqual(speeds1[i], 
                self.trace1.getObsAnalyticalFeature(BIAF_ABS_CURV, i))
            
            
    def testEstimateHeading(self):
        
        import math
        
        Cinematics.estimate_heading(self.trace2)
        
        s0 = self.trace2.getObsAnalyticalFeature('heading', 0)
        s1 = self.trace2.getObsAnalyticalFeature('heading', 1)
        s2 = self.trace2.getObsAnalyticalFeature('heading', 2)
        s3 = self.trace2.getObsAnalyticalFeature('heading', 3)
        s4 = self.trace2.getObsAnalyticalFeature('heading', 4)
        s5 = self.trace2.getObsAnalyticalFeature('heading', 5)
        s6 = self.trace2.getObsAnalyticalFeature('heading', 6)
        s7 = self.trace2.getObsAnalyticalFeature('heading', 7)
        
        self.assertEqual(s0, s1)
        self.assertEqual(s1, math.atan2(10, 0))
        self.assertEqual(s2, math.atan2(0, 10))
        self.assertEqual(s3, math.atan2(0, 10))
        self.assertEqual(s4, math.atan2(-10, 0))
        self.assertEqual(s5, math.atan2(0, -10))
        self.assertEqual(s6, math.atan2(0, 10))
        self.assertEqual(s7, math.atan2(5, 0))
        
    
    def testComputeAvgSpeed(self):
        
        a = Cinematics.computeAvgSpeed(self.trace2)
        self.assertLessEqual(abs(a - 0.419354), self.__epsilon, 'ComputeAvgSpeed')


    def testComputeNetDeniv(self):
        
        a = Cinematics.computeNetDeniv(self.trace2)
        self.assertLessEqual(abs(a - 0), self.__epsilon, 'ComputeAvgSpeed')
        
        a = Cinematics.computeNetDeniv(self.trace2, 0, 3)
        self.assertLessEqual(abs(a - 15), self.__epsilon, 'ComputeAvgSpeed')
        
        
    def testComputeAscDeniv(self):
        
        a = Cinematics.computeAscDeniv(self.trace2)
        self.assertLessEqual(abs(a - 15), self.__epsilon, 'ComputeAscDeniv')
        a = Cinematics.computeAscDeniv(self.trace2, 0, 3)
        self.assertLessEqual(abs(a - 15), self.__epsilon, 'ComputeAscDeniv')
        a = Cinematics.computeAscDeniv(self.trace2, 3)
        self.assertLessEqual(abs(a - 0), self.__epsilon, 'ComputeAscDeniv')
    
    
    def testComputeDescDeniv(self):
        
        a = Cinematics.computeDescDeniv(self.trace2)
        self.assertLessEqual(abs(a + 15), self.__epsilon, 'computeDescDeniv')
        a = Cinematics.computeDescDeniv(self.trace2, 0, 3)
        self.assertLessEqual(abs(a - 0), self.__epsilon, 'computeDescDeniv')
        a = Cinematics.computeDescDeniv(self.trace2, 4)
        self.assertLessEqual(abs(a + 10), self.__epsilon, 'computeDescDeniv')
        
        
    def testComputeRadialSignature(self):
        pass
        

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoCinematicsMethods("testAFInflexion"))
    suite.addTest(TestAlgoCinematicsMethods("testAFvertex"))
    suite.addTest(TestAlgoCinematicsMethods("testSmoothedSpeedCalculation"))
    suite.addTest(TestAlgoCinematicsMethods("testCompareAbsCurv"))
    suite.addTest(TestAlgoCinematicsMethods("testEstimateHeading"))
    suite.addTest(TestAlgoCinematicsMethods("testComputeNetDeniv"))
    suite.addTest(TestAlgoCinematicsMethods("testComputeAscDeniv"))
    suite.addTest(TestAlgoCinematicsMethods("testComputeDescDeniv"))
    suite.addTest(TestAlgoCinematicsMethods("testComputeRadialSignature"))
    runner = unittest.TextTestRunner()
    runner.run(suite)


