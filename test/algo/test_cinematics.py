# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from numpy import pi
import os
import unittest

from tracklib import (Obs, ObsTime, ENUCoords, getColorMap,
                      BIAF_ABS_CURV, 
                      Operator,
                      computeInflection, 
                      computeInflectionLevel2,
                      computeVertex, 
                      computeBend,
                      computeSwitchbacks,
                      smoothed_speed_calculation,
                      computeAbsCurv,
                      estimate_heading,
                      computeAvgSpeed,
                      computeAvgAscSpeed,
                      computeNetDeniv,
                      computeAscDeniv,
                      computeDescDeniv,
                      Track,
                      TrackReader, 
                      computeRadialSignature,
                      averageDeviationPositions,
                      averageDistanceBetweenInflectionPoint)


class TestAlgoCinematicsMethods(unittest.TestCase):
    
    __epsilon = 0.001
    
    def setUp (self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        self.trace1 = Track([], 1)

        p1 = Obs(ENUCoords(0, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace1.addObs(p1)
        
        p2 = Obs(ENUCoords(10, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:12"))
        self.trace1.addObs(p2)
        
        p3 = Obs(ENUCoords(10, 10, 0), ObsTime.readTimestamp("2018-01-01 10:00:40"))
        self.trace1.addObs(p3)
        
        p4 = Obs(ENUCoords(20, 10, 0), ObsTime.readTimestamp("2018-01-01 10:01:50"))
        self.trace1.addObs(p4)
		
        p5 = Obs(ENUCoords(20, 20, 0), ObsTime.readTimestamp("2018-01-01 10:02:10"))
        self.trace1.addObs(p5)
        
        p6 = Obs(ENUCoords(30, 20, 0), ObsTime.readTimestamp("2018-01-01 10:02:35"))
        self.trace1.addObs(p6)
        
        p7 = Obs(ENUCoords(30, 30, 0), ObsTime.readTimestamp("2018-01-01 10:02:43"))
        self.trace1.addObs(p7)
        
        p8 = Obs(ENUCoords(40, 30, 0), ObsTime.readTimestamp("2018-01-01 10:02:55"))
        self.trace1.addObs(p8)
        
        p9 = Obs(ENUCoords(60, 30, 0), ObsTime.readTimestamp("2018-01-01 10:03:25"))
        self.trace1.addObs(p9)
        
        # -----------------
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        self.trace2 = Track([], 1)

        p1 = Obs(ENUCoords(0, 0, 0), 
                 ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace2.addObs(p1)
        
        p2 = Obs(ENUCoords(10, 0, 10), 
                 ObsTime.readTimestamp("2018-01-01 10:00:12"))
        self.trace2.addObs(p2)
        
        p3 = Obs(ENUCoords(10, 10, 10), 
                 ObsTime.readTimestamp("2018-01-01 10:00:40"))
        self.trace2.addObs(p3)
        
        p4 = Obs(ENUCoords(10, 20, 15), 
                 ObsTime.readTimestamp("2018-01-01 10:01:50"))
        self.trace2.addObs(p4)
		
        p5 = Obs(ENUCoords(0, 20, 10), 
                 ObsTime.readTimestamp("2018-01-01 10:02:10"))
        self.trace2.addObs(p5)
		
        p6 = Obs(ENUCoords(0, 10, 0), 
                 ObsTime.readTimestamp("2018-01-01 10:02:15"))
        self.trace2.addObs(p6)
		
        p7 = Obs(ENUCoords(0, 20, 0), 
                 ObsTime.readTimestamp("2018-01-01 10:02:35"))
        self.trace2.addObs(p7)
		
        p8 = Obs(ENUCoords(5, 20, 0), 
                 ObsTime.readTimestamp("2018-01-01 10:02:35"))
        self.trace2.addObs(p8)
        
        # -----------------
        #   Pour les virages et lacets
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        self.trace3 = Track([], 1)
        
        self.trace3.addObs(Obs(ENUCoords(-39, 24, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(-33, 22, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(-20, 21, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(-15, 20, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(-10, 18, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(-8, 15, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(-1, 4, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(3, 1, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(7, 0, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(10, 1, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(12, 3, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(14, 8, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(20, 13, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(23, 15, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(29, 16.5, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(33, 17, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(37, 16.5, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(40, 15, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(48, 10, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(51, 8, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(54, 8, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(58, 11, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(63, 15, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(65, 17, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(67, 18, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(72, 19, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(103, 17, 0), ObsTime()))
        self.trace3.addObs(Obs(ENUCoords(108, 16, 0), ObsTime()))
        
        # Pour le dessin
        self.COLS_ROUGE = getColorMap((220, 220, 220), (255, 0, 0))
        self.COLS_BLEU = getColorMap((220, 220, 220), (0, 0, 255))
        self.COLS_VERT = getColorMap((220, 220, 220), (0, 255, 0))
        
        # ---------------------------------------------------------------------
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        self.trace4 = Track([], 1)
        self.trace4.addObs(Obs(ENUCoords(-50, 55, 0), ObsTime()))
        self.trace4.addObs(Obs(ENUCoords(0, 50, 0), ObsTime()))
        self.trace4.addObs(Obs(ENUCoords(30, 40, 0), ObsTime()))
        self.trace4.addObs(Obs(ENUCoords(50, 20, 0), ObsTime()))
        self.trace4.addObs(Obs(ENUCoords(60, 0, 0), ObsTime()))
        self.trace4.addObs(Obs(ENUCoords(70, -2, 0), ObsTime()))
        self.trace4.addObs(Obs(ENUCoords(80, 0, 0), ObsTime()))
        self.trace4.addObs(Obs(ENUCoords(90, 20, 0), ObsTime()))
        self.trace4.addObs(Obs(ENUCoords(110, 40, 0), ObsTime()))
        self.trace4.addObs(Obs(ENUCoords(140, 50, 0), ObsTime()))
        self.trace4.addObs(Obs(ENUCoords(190, 55, 0), ObsTime()))
        self.trace4.addObs(Obs(ENUCoords(260, 60, 0), ObsTime()))

    def testAFInflexion(self):
        plt.figure(figsize = (8,4))
        
        self.trace1.plot()
        computeInflection(self.trace1)
        afIsInflexion = self.trace1.getAnalyticalFeature('inflection')
        #print (afIsInflexion)
        self.trace1.plot(type='POINT', af_name='inflection', append = True, 
            cmap = self.COLS_ROUGE, pointsize=40)
        plt.show()
        
        T = [0, 1, 1, 1, 1, 1, 0, 0, 0]
        self.assertEqual(afIsInflexion, T) 
        
    def testAFInflexionLevel2(self):
        plt.figure(figsize = (8,4))
        
        self.trace3.plot()
        computeInflectionLevel2(self.trace3)
        afIsInflexion = self.trace3.getAnalyticalFeature('inflection')
        #print (afIsInflexion)
        self.trace3.plot(type='POINT', af_name='inflection', append = True, 
            cmap = self.COLS_ROUGE, pointsize=40)
        plt.show()
        
        T = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 
             0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0]
        self.assertEqual(afIsInflexion, T) 
        
        # ----------------------------------------------------------------------
        
        self.trace1.plot()
        computeInflectionLevel2(self.trace1)
        afIsInflexion = self.trace1.getAnalyticalFeature('inflection')
        #print (afIsInflexion)
        self.trace1.plot(type='POINT', af_name='inflection', append = True, 
            cmap = self.COLS_ROUGE, pointsize=40)
        plt.show()
        
        T = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(afIsInflexion, T) 
        
        
    def testAFvertex(self):
        plt.figure(figsize = (8,4))
        self.trace3.plot()
        
        computeInflectionLevel2(self.trace3)
        computeVertex(self.trace3)
        afVertex = self.trace3.getAnalyticalFeature('vertex')
        #print (afVertex)
        self.trace3.plot(type='POINT', af_name='vertex', append = True, 
            cmap = self.COLS_BLEU, pointsize=50)
        plt.show()
        
        T = [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 
             0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]
        self.assertEqual(afVertex, T) 
        
        
    def testBends(self):
        plt.figure(figsize = (8,4))
        self.trace3.plot()
        
        computeInflectionLevel2(self.trace3)
        computeBend(self.trace3, angle_min = 130*pi/180)
        afBend = self.trace3.getAnalyticalFeature('bend')
        #print (afBend)
        self.trace3.plot(type='POINT', af_name='bend', append = True, 
            cmap = self.COLS_VERT, pointsize=50)
        plt.show()
        
        T = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
             1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
        self.assertEqual(afBend, T) 

        
    def testSwitchbacks(self):
        plt.figure(figsize = (8,4))
        self.trace3.plot()
        
        computeInflectionLevel2(self.trace3)
        computeBend(self.trace3, angle_min = 130*pi/180)
        computeSwitchbacks(self.trace3, nb_virage_min=3, 
                                      dist_max=200)
        afSwitchbacks = self.trace3.getAnalyticalFeature('switchbacks')
        #print (afSwitchbacks)
        
        self.trace3.plot(type='POINT', af_name='switchbacks', append = True, 
            cmap = self.COLS_BLEU, pointsize=50)
        plt.show()
        
        T = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
             1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
        self.assertEqual(afSwitchbacks, T) 
        
        
    def testSmoothedSpeedCalculation(self):
        smoothed_speed_calculation(self.trace1, 2)
        speeds = self.trace1.getAnalyticalFeature('speed')
        computeAbsCurv(self.trace1)
        
        ds8 = self.trace1.getObsAnalyticalFeature('abs_curv', 8)
        ds4 = self.trace1.getObsAnalyticalFeature('abs_curv', 4)
        ds = ds8 - ds4
        dt = self.trace1.getObs(8).timestamp - self.trace1.getObs(4).timestamp

        err = abs(speeds[6] - ds/dt)
        self.assertLessEqual(err, self.__epsilon, 'erreur pour 6')
        
        
    def testCompareAbsCurv(self):
        speeds1 = computeAbsCurv(self.trace1)
        #print (speeds1)
        
        computeAbsCurv(self.trace1)
        for i in range(self.trace1.size()):
            self.assertEqual(speeds1[i], 
                self.trace1.getObsAnalyticalFeature(BIAF_ABS_CURV, i))
            
            
    def testEstimateHeading(self):
        
        import math
        
        estimate_heading(self.trace2)
        
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
        
        a = computeAvgSpeed(self.trace2)
        self.assertLessEqual(abs(a - 0.419354), self.__epsilon, 'ComputeAvgSpeed')
        
        
    def testComputeAvgAscSpeed(self):
        
        a = computeAvgAscSpeed(self.trace2)
        self.assertLessEqual(abs(a - 0.096774), self.__epsilon, 'computeAvgAscSpeed')


    def testComputeNetDeniv(self):
        
        a = computeNetDeniv(self.trace2)
        self.assertLessEqual(abs(a - 0), self.__epsilon, 'ComputeAvgSpeed')
        
        a = computeNetDeniv(self.trace2, 0, 3)
        self.assertLessEqual(abs(a - 15), self.__epsilon, 'ComputeAvgSpeed')
        
        
    def testComputeAscDeniv(self):
        
        a = computeAscDeniv(self.trace2)
        self.assertLessEqual(abs(a - 15), self.__epsilon, 'ComputeAscDeniv')
        a = computeAscDeniv(self.trace2, 0, 3)
        self.assertLessEqual(abs(a - 15), self.__epsilon, 'ComputeAscDeniv')
        a = computeAscDeniv(self.trace2, 3)
        self.assertLessEqual(abs(a - 0), self.__epsilon, 'ComputeAscDeniv')
    
    
    def testComputeDescDeniv(self):
        
        a = computeDescDeniv(self.trace2)
        self.assertLessEqual(abs(a + 15), self.__epsilon, 'computeDescDeniv')
        a = computeDescDeniv(self.trace2, 0, 3)
        self.assertLessEqual(abs(a - 0), self.__epsilon, 'computeDescDeniv')
        a = computeDescDeniv(self.trace2, 4)
        self.assertLessEqual(abs(a + 10), self.__epsilon, 'computeDescDeniv')
        
        
    def testComputeRadialSignature(self):
        resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        path = os.path.join(resource_path, 'data/wkt/chambord.wkt')
        TRACES = TrackReader.readFromWkt(path, id_geom=0, separator="#", h=1, doublequote=True)

        trace = TRACES[0]
        #trace.plot('c-')
        #plt.show()

        trace1 = computeRadialSignature(trace)
        R = trace1.getAnalyticalFeature('r')
        plt.plot(R, color="royalblue", linestyle='--')
        
    
    def testAverageDeviationPositions(self):
        ind = averageDeviationPositions(self.trace1)
        self.assertLessEqual(abs(ind - 2.1875), self.__epsilon)

        #computeAbsCurv(trace1)
        #trace1.operate(Operator.DIFFERENTIATOR, "abs_curv", "dist")
        #print (trace1['dist'])
        #trace1.operate(Operator.DEBIASER, "dist", "dmd")
        #trace1.operate(Operator.RMSE, "dist", "rmse_abs_curv")
        
        
    def testAverageDistanceBetweenInflectionPoint(self):
        # TRACE 4
        ind2 = averageDistanceBetweenInflectionPoint(self.trace4)
        # print (ind2)
        self.assertLessEqual(abs(ind2 - 42.757), self.__epsilon)
        self.trace4.plot('k-', append=False)
        self.trace4.plot('ko', append=True)
        self.trace4.plot(type='POINT', af_name='inflection', append=True, 
            cmap = self.COLS_ROUGE, pointsize=8)
        plt.show()
        
        
        # TRACE 3
        self.trace3.plot('k-', append=False)
        self.trace3.plot('ko', append=True)
        ind2 = averageDistanceBetweenInflectionPoint(self.trace3)
        #print (ind2)
        self.assertLessEqual(abs(ind2 - 29.999), self.__epsilon)
        self.trace3.plot(type='POINT', af_name='inflection', append=True, 
            cmap = self.COLS_ROUGE, pointsize=8)
        plt.show()
        
        # TRACE 1
        self.trace1.plot('k-', append=False)
        self.trace1.plot('ko', append=True)
        ind2 = averageDistanceBetweenInflectionPoint(self.trace1)
        self.assertLessEqual(abs(ind2 - 0.000), self.__epsilon)
        self.trace1.plot(type='POINT', af_name='inflection', append=True, 
            cmap = self.COLS_ROUGE, pointsize=8)
        plt.show()
        
        
if __name__ == '__main__':
    
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoCinematicsMethods("testAFInflexion"))
    suite.addTest(TestAlgoCinematicsMethods("testAFInflexionLevel2"))
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
    suite.addTest(TestAlgoCinematicsMethods("testAverageDeviationPositions"))
    suite.addTest(TestAlgoCinematicsMethods("testAverageDistanceBetweenInflectionPoint"))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)


