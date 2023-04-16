# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from numpy import pi
import unittest

from tracklib.core import (Obs, Track, ObsTime)
from tracklib.core import ObsCoords as Coords
from tracklib.algo.Analytics import BIAF_ABS_CURV
import tracklib.algo.Cinematics as Cinematics
import tracklib.core.Utils as utils


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
        
        
        # -----------------
        #   Pour les virages et lacets
        
        ObsTime.ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        self.trace3 = Track.Track([], 1)
        
        cm1 = Coords.ENUCoords(-5, 18, 0)
        pm1 = Obs.Obs(cm1, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace3.addObs(pm1)
        
        c0 = Coords.ENUCoords(-3, 15, 0)
        p0 = Obs.Obs(c0, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace3.addObs(p0)
        
        c1 = Coords.ENUCoords(-3, 7, 0)
        p1 = Obs.Obs(c1, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace3.addObs(p1)
        
        c2 = Coords.ENUCoords(0, 2, 0)
        p2 = Obs.Obs(c2, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace3.addObs(p2)
        
        c3 = Coords.ENUCoords(10, 0, 0)
        p3 = Obs.Obs(c3, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:12"))
        self.trace3.addObs(p3)
        
        c4 = Coords.ENUCoords(17, 1, 0)
        p4 = Obs.Obs(c4, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:40"))
        self.trace3.addObs(p4)
        
        c5 = Coords.ENUCoords(20, 6, 0)
        p5 = Obs.Obs(c5, ObsTime.ObsTime.readTimestamp("2018-01-01 10:01:50"))
        self.trace3.addObs(p5)
		
        c6 = Coords.ENUCoords(21, 11, 0)
        p6 = Obs.Obs(c6, ObsTime.ObsTime.readTimestamp("2018-01-01 10:02:10"))
        self.trace3.addObs(p6)
        
        c7 = Coords.ENUCoords(25, 15, 0)
        p7 = Obs.Obs(c7, ObsTime.ObsTime.readTimestamp("2018-01-01 10:02:35"))
        self.trace3.addObs(p7)
        
        c8 = Coords.ENUCoords(28, 17, 0)
        p8 = Obs.Obs(c8, ObsTime.ObsTime.readTimestamp("2018-01-01 10:02:43"))
        self.trace3.addObs(p8)
        
        c9 = Coords.ENUCoords(33, 18, 0)
        p9 = Obs.Obs(c9, ObsTime.ObsTime.readTimestamp("2018-01-01 10:02:55"))
        self.trace3.addObs(p9)
        
        c10 = Coords.ENUCoords(42, 17, 0)
        p10 = Obs.Obs(c10, ObsTime.ObsTime.readTimestamp("2018-01-01 10:03:25"))
        self.trace3.addObs(p10)
        
        c11 = Coords.ENUCoords(45, 15, 0)
        p11 = Obs.Obs(c11, ObsTime.ObsTime.readTimestamp("2018-01-01 10:03:25"))
        self.trace3.addObs(p11)
        
        c12 = Coords.ENUCoords(48, 10, 0)
        p12 = Obs.Obs(c12, ObsTime.ObsTime.readTimestamp("2018-01-01 10:03:25"))
        self.trace3.addObs(p12)
        
        c13 = Coords.ENUCoords(51, 8, 0)
        p13 = Obs.Obs(c13, ObsTime.ObsTime.readTimestamp("2018-01-01 10:03:25"))
        self.trace3.addObs(p13)
        
        c14 = Coords.ENUCoords(54, 8, 0)
        p14 = Obs.Obs(c14, ObsTime.ObsTime.readTimestamp("2018-01-01 10:03:25"))
        self.trace3.addObs(p14)
        
        c15 = Coords.ENUCoords(58, 11, 0)
        p15 = Obs.Obs(c15, ObsTime.ObsTime.readTimestamp("2018-01-01 10:03:25"))
        self.trace3.addObs(p15)
        
        c16 = Coords.ENUCoords(63, 15, 0)
        p16 = Obs.Obs(c16, ObsTime.ObsTime.readTimestamp("2018-01-01 10:03:25"))
        self.trace3.addObs(p16)
        
        c17 = Coords.ENUCoords(65, 17, 0)
        p17 = Obs.Obs(c17, ObsTime.ObsTime.readTimestamp("2018-01-01 10:03:25"))
        self.trace3.addObs(p17)
        
        c18 = Coords.ENUCoords(63, 20, 0)
        p18 = Obs.Obs(c18, ObsTime.ObsTime.readTimestamp("2018-01-01 10:03:25"))
        self.trace3.addObs(p18)
        
        
        # Pour le dessin
        self.COLS_ROUGE = utils.getColorMap((220, 220, 220), (255, 0, 0))
        self.COLS_BLEU = utils.getColorMap((220, 220, 220), (0, 0, 255))
        self.COLS_VERT = utils.getColorMap((220, 220, 220), (0, 255, 0))

    def testAFInflexion(self):
        plt.figure(figsize = (8,4))
        self.trace3.plot()
        self.trace3.addAnalyticalFeature(Cinematics.inflection)
        afIsInflexion = self.trace3.getAnalyticalFeature('inflection')
        #print (afIsInflexion)
        self.trace3.plot(type='POINT', af_name='inflection', append = True, 
            cmap = self.COLS_ROUGE, pointsize=50)
        plt.show()
        
        self.assertEqual(afIsInflexion[0], 0)
        self.assertEqual(afIsInflexion[1], 1)
        self.assertEqual(afIsInflexion[2], 0)
        self.assertEqual(afIsInflexion[3], 0)
        self.assertEqual(afIsInflexion[4], 0)
        self.assertEqual(afIsInflexion[5], 0)
        self.assertEqual(afIsInflexion[6], 1)
        self.assertEqual(afIsInflexion[7], 0)
        self.assertEqual(afIsInflexion[8], 0)
        self.assertEqual(afIsInflexion[9], 0)
        self.assertEqual(afIsInflexion[10], 0)
        self.assertEqual(afIsInflexion[11], 0)
        self.assertEqual(afIsInflexion[12], 1)
        self.assertEqual(afIsInflexion[13], 0)
        self.assertEqual(afIsInflexion[14], 0)
        self.assertEqual(afIsInflexion[15], 0)
        self.assertEqual(afIsInflexion[15], 0)
        self.assertEqual(afIsInflexion[16], 0)
        self.assertEqual(afIsInflexion[17], 0)
        self.assertEqual(afIsInflexion[18], 0)
        self.assertEqual(afIsInflexion[19], 0)

    def testAFvertex(self):
        plt.figure(figsize = (8,4))
        self.trace3.plot()
        Cinematics.setVertexAF(self.trace3)
        afVertex = self.trace3.getAnalyticalFeature('vertex')
        # print (afVertex)
        self.trace3.plot(type='POINT', af_name='vertex', append = True, 
            cmap = self.COLS_BLEU, pointsize=50)
        plt.show()
        
        self.assertEqual(afVertex[0], 0)
        self.assertEqual(afVertex[1], 1)
        self.assertEqual(afVertex[2], 0)
        self.assertEqual(afVertex[3], 0)
        self.assertEqual(afVertex[4], 0)
        self.assertEqual(afVertex[5], 1)
        self.assertEqual(afVertex[6], 0)
        self.assertEqual(afVertex[7], 1)
        self.assertEqual(afVertex[8], 0)
        self.assertEqual(afVertex[9], 0)
        self.assertEqual(afVertex[10], 0)
        self.assertEqual(afVertex[11], 0)
        self.assertEqual(afVertex[12], 0)
        self.assertEqual(afVertex[13], 0)
        self.assertEqual(afVertex[14], 0)
        self.assertEqual(afVertex[15], 0)
        self.assertEqual(afVertex[16], 0)
        self.assertEqual(afVertex[17], 0)
        self.assertEqual(afVertex[18], 1)
        self.assertEqual(afVertex[19], 0)
        
    def testBends(self):
        plt.figure(figsize = (8,4))
        self.trace3.plot()
        
        Cinematics.setBendAsAF(self.trace3, angle_min = 115*pi/180)
        afBend = self.trace3.getAnalyticalFeature('bend')
        self.trace3.plot(type='POINT', af_name='bend', append = True, 
            cmap = self.COLS_VERT, pointsize=50)
        plt.show()
        
        self.assertEqual(afBend[0], 0)
        self.assertEqual(afBend[1], 1)
        self.assertEqual(afBend[2], 1)
        self.assertEqual(afBend[3], 1)
        self.assertEqual(afBend[4], 1)
        self.assertEqual(afBend[5], 1)
        self.assertEqual(afBend[6], 1)
        self.assertEqual(afBend[7], 1)
        self.assertEqual(afBend[8], 1)
        self.assertEqual(afBend[9], 1)
        self.assertEqual(afBend[10], 1)
        self.assertEqual(afBend[11], 1)
        self.assertEqual(afBend[12], 1)
        self.assertEqual(afBend[13], 1)
        self.assertEqual(afBend[14], 1)
        self.assertEqual(afBend[15], 1)
        self.assertEqual(afBend[16], 1)
        self.assertEqual(afBend[17], 1)
        self.assertEqual(afBend[18], 1)
        self.assertEqual(afBend[19], 1)
        
        
    def testSwitchbacks(self):
        plt.figure(figsize = (8,4))
        self.trace3.plot()
        
        Cinematics.setSwitchbacksAsAF(self.trace3, nb_virage_min = 1, dist_max = 50)
        afSwitchbacks = self.trace3.getAnalyticalFeature('switchbacks')
        print (afSwitchbacks)
        
        self.trace3.plot(type='POINT', af_name='switchbacks', append = True, 
            cmap = self.COLS_BLEU, pointsize=50)
        plt.show()
        
        
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
        
        
    def testComputeAvgAscSpeed(self):
        
        a = Cinematics.computeAvgAscSpeed(self.trace2)
        self.assertLessEqual(abs(a - 0.096774), self.__epsilon, 'computeAvgAscSpeed')


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
    suite.addTest(TestAlgoCinematicsMethods("testBends"))
    suite.addTest(TestAlgoCinematicsMethods("testSwitchbacks"))
    
    suite.addTest(TestAlgoCinematicsMethods("testSmoothedSpeedCalculation"))
    suite.addTest(TestAlgoCinematicsMethods("testCompareAbsCurv"))
    suite.addTest(TestAlgoCinematicsMethods("testEstimateHeading"))
    suite.addTest(TestAlgoCinematicsMethods("testComputeNetDeniv"))
    suite.addTest(TestAlgoCinematicsMethods("testComputeAscDeniv"))
    suite.addTest(TestAlgoCinematicsMethods("testComputeDescDeniv"))
    suite.addTest(TestAlgoCinematicsMethods("testComputeAvgAscSpeed"))
    suite.addTest(TestAlgoCinematicsMethods("testComputeRadialSignature"))
    runner = unittest.TextTestRunner()
    runner.run(suite)


