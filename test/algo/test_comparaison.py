#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import math
import matplotlib.pyplot as plt

from tracklib import (Obs, ObsTime, ENUCoords, 
                      Track, TrackCollection,
                      compare, 
                      differenceProfile, 
                      plotDifferenceProfile,
                      premiereComposanteHausdorff,
                      hausdorff, discreteFrechet,
                      centralTrack,
                      arealStandardizedBetweenTwoTracks,
                      aggregateCoordSet)



class TestAlgoComparaisonMethods(unittest.TestCase):
    
    __epsilon = 0.001
    
    def setUp (self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        # ---------------------------------------------------------------------
        
        self.trace1 = Track([], 1)
        
        p1 = Obs(ENUCoords(1.0, 5.0, 0), ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace1.addObs(p1)
        
        p2 = Obs(ENUCoords(2.0, 5.0, 0), ObsTime.readTimestamp("2018-01-01 10:00:05"))
        self.trace1.addObs(p2)
        
        p3 = Obs(ENUCoords(3.0, 6.0, 0), ObsTime.readTimestamp("2018-01-01 10:00:10"))
        self.trace1.addObs(p3)
        
        p4 = Obs(ENUCoords(4.0, 6.0, 0), ObsTime.readTimestamp("2018-01-01 10:00:15"))
        self.trace1.addObs(p4)
        
        p5 = Obs(ENUCoords(5.0, 5.0, 0), ObsTime.readTimestamp("2018-01-01 10:00:20"))
        self.trace1.addObs(p5)
        
        p6 = Obs(ENUCoords(6.0, 5.0, 0), ObsTime.readTimestamp("2018-01-01 10:00:25"))
        self.trace1.addObs(p6)
        
        p7 = Obs(ENUCoords(7.0, 4.0, 0), ObsTime.readTimestamp("2018-01-01 10:00:30"))
        self.trace1.addObs(p7)
        
        p8 = Obs(ENUCoords(8.0, 5.0, 0), ObsTime.readTimestamp("2018-01-01 10:00:35"))
        self.trace1.addObs(p8)
        
        p9 = Obs(ENUCoords(9.0, 5.0, 0), ObsTime.readTimestamp("2018-01-01 10:00:40"))
        self.trace1.addObs(p9)
        
        p10 = Obs(ENUCoords(10.0, 5.0, 0), ObsTime.readTimestamp("2018-01-01 10:00:45"))
        self.trace1.addObs(p10)
        
        p11 = Obs(ENUCoords(11.0, 5.0, 0), ObsTime.readTimestamp("2018-01-01 10:00:50"))
        self.trace1.addObs(p11)
        
        # ---------------------------------------------------------------------
        
        self.trace2 = Track([], 2)
        
        r1 = Obs(ENUCoords(1.0, 1.0, 0), ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace2.addObs(r1)
        
        d2 = ENUCoords(2.0, 1.0, 0)
        r2 = Obs(d2, ObsTime.readTimestamp("2018-01-01 10:00:05"))
        self.trace2.addObs(r2)
        
        d3 = ENUCoords(3.0, 1.0, 0)
        r3 = Obs(d3, ObsTime.readTimestamp("2018-01-01 10:00:10"))
        self.trace2.addObs(r3)
        
        d4 = ENUCoords(4.0, 1.0, 0)
        r4 = Obs(d4, ObsTime.readTimestamp("2018-01-01 10:00:15"))
        self.trace2.addObs(r4)
        
        d5 = ENUCoords(5.0, 2.0, 0)
        r5 = Obs(d5, ObsTime.readTimestamp("2018-01-01 10:00:20"))
        self.trace2.addObs(r5)
        
        d6 = ENUCoords(6.0, 2.0, 0)
        r6 = Obs(d6, ObsTime.readTimestamp("2018-01-01 10:00:25"))
        self.trace2.addObs(r6)
        
        d7 = ENUCoords(7.0, 1.0, 0)
        r7 = Obs(d7, ObsTime.readTimestamp("2018-01-01 10:00:30"))
        self.trace2.addObs(r7)
        
        d8 = ENUCoords(8.0, 1.0, 0)
        r8 = Obs(d8, ObsTime.readTimestamp("2018-01-01 10:00:35"))
        self.trace2.addObs(r8)
        
        d9 = ENUCoords(9.0, 1.0, 0)
        r9 = Obs(d9, ObsTime.readTimestamp("2018-01-01 10:00:40"))
        self.trace2.addObs(r9)
        
        d10 = ENUCoords(10.0, 0.0, 0)
        r10 = Obs(d10, ObsTime.readTimestamp("2018-01-01 10:00:40"))
        self.trace2.addObs(r10)
        
        d11 = ENUCoords(11.0, 0.5, 0)
        r11 = Obs(d11, ObsTime.readTimestamp("2018-01-01 10:00:45"))
        self.trace2.addObs(r11)
        
        d12 = ENUCoords(12.0, 1.0, 0)
        r12 = Obs(d12, ObsTime.readTimestamp("2018-01-01 10:00:50"))
        self.trace2.addObs(r12)
        
        d13 = ENUCoords(13.0, 1.0, 0)
        r13 = Obs(d13, ObsTime.readTimestamp("2018-01-01 10:00:55"))
        self.trace2.addObs(r13)
        
    def plot(self):
        self.trace1.plot()
        self.trace1.plotAsMarkers()
        self.trace2.plot()
        self.trace2.plotAsMarkers()

        plt.xlim([0, 6])
        plt.ylim([0, 3.25])
        
        
    def testCompare(self):
        a = compare(self.trace1, self.trace2)
        self.assertLessEqual(abs(a - 4.0280), self.__epsilon, "Comparaison")


    def testDifference21ProfileNN(self):
        profile = differenceProfile(self.trace2, self.trace1, 
                                               mode = "NN", p=2)
        self.trace1.plot('b-')
        self.trace2.plot('r-')
        plotDifferenceProfile(profile, self.trace1)
        plt.show()
        
        
    def testDifference12ProfileNN(self):
        profile = differenceProfile(self.trace1, self.trace2, 
                                               mode = "NN", p=2)
        self.trace1.plot('r-')
        self.trace2.plot('r-')
        plotDifferenceProfile(profile, self.trace2)
        plt.show()
        
        
    def testDifference21ProfileDTW(self):
        profile = differenceProfile(self.trace2, self.trace1, 
                                               mode = "DTW", p=2)
        self.trace1.plot('r-')
        self.trace2.plot('r-')
        plotDifferenceProfile(profile, self.trace1)
        plt.show()
    
    
    def testDifference21ProfileFDTW(self):
        profile = differenceProfile(self.trace2, self.trace1, 
                                               mode = "FDTW", p=2)
        self.trace1.plot('r-')
        self.trace2.plot('r-')
        plotDifferenceProfile(profile, self.trace1)
        plt.show()
        
        
    def testHausdorffSimilarity(self):
        trackA = Track([], 1)
        c = ENUCoords(1.0, 0.0, 0)
        p = Obs(c, ObsTime())
        trackA.addObs(p)
        c = ENUCoords(0.0, 1.0, 0)
        p = Obs(c, ObsTime())
        trackA.addObs(p)
        c = ENUCoords(-1.0, 0.0, 0)
        p = Obs(c, ObsTime())
        trackA.addObs(p)
        c = ENUCoords(0.0, -1.0, 0)
        p = Obs(c, ObsTime())
        trackA.addObs(p)

        trackB = Track([], 1)
        c = ENUCoords(2.0, 0.0, 0)
        p = Obs(c, ObsTime())
        trackB.addObs(p)
        c = ENUCoords(0.0, 2.0, 0)
        p = Obs(c, ObsTime())
        trackB.addObs(p)
        c = ENUCoords(-2.0, 0.0, 0)
        p = Obs(c, ObsTime())
        trackB.addObs(p)
        c = ENUCoords(0.0, -4.0, 0)
        p = Obs(c, ObsTime())
        trackB.addObs(p)

        dAB = premiereComposanteHausdorff(trackA, trackB)
        dBA = premiereComposanteHausdorff(trackB, trackA)
        self.assertLessEqual(abs(dBA-2.12132), self.__epsilon)
        self.assertLessEqual(abs(dAB-1.34164), self.__epsilon)
        d = hausdorff(trackA, trackB)
        self.assertLessEqual(abs(d - 2.12132), self.__epsilon)
        
    def testFrechetSimilarity(self):
        trackA = Track([], 1)
        c = ENUCoords(2.0, 1.0, 0)
        p = Obs(c, ObsTime())
        trackA.addObs(p)
        c = ENUCoords(3.0, 1.0, 0)
        p = Obs(c, ObsTime())
        trackA.addObs(p)
        c = ENUCoords(4.0, 2.0, 0)
        p = Obs(c, ObsTime())
        trackA.addObs(p)
        c = ENUCoords(5.0, 1.0, 0)
        p = Obs(c, ObsTime())
        trackA.addObs(p)

        trackB = Track([], 1)
        c = ENUCoords(2.0, 0.0, 0)
        p = Obs(c, ObsTime())
        trackB.addObs(p)
        c = ENUCoords(3.0, 0.0, 0)
        p = Obs(c, ObsTime())
        trackB.addObs(p)
        c = ENUCoords(4.0, 0.0, 0)
        p = Obs(c, ObsTime())
        trackB.addObs(p)

        self.assertEqual(discreteFrechet(trackA, trackB), 2.0)
        
    def testCentralNNTrack(self):
        TRACES = []
        TRACES.append(self.trace1)
        TRACES.append(self.trace2)
        collection = TrackCollection(TRACES)
        self.plot()
        
        central = centralTrack(collection)
        
        central.plot()
        central.plotAsMarkers(frg="k", bkg="w", sym_frg=" ", sym_bkg="o")
        
        plt.title('central NN')
        plt.xlim([0, 14])
        plt.ylim([-1, 7])
        plt.show()        
        
    def testCentralDTWTrack(self):
        TRACES = []
        TRACES.append(self.trace1)
        TRACES.append(self.trace2)
        collection = TrackCollection(TRACES)
        self.plot()
        
        central = centralTrack(collection, mode = "DTW")
        
        central.plot()
        central.plotAsMarkers(frg="k", bkg="w", sym_frg=" ", sym_bkg="o")
        
        plt.title('central DTW')
        plt.xlim([0, 14])
        plt.ylim([-1, 7])
        plt.show()   

    def testArealStandardizedBetweenTwoTracks(self):
        trace4 = Track([], 1)
        trace4.addObs(Obs(ENUCoords(0, 50, 0), ObsTime()))
        trace4.addObs(Obs(ENUCoords(10, 50, 0), ObsTime()))
        trace4.addObs(Obs(ENUCoords(10, 60, 0), ObsTime()))
        trace4.addObs(Obs(ENUCoords(20, 60, 0), ObsTime()))
        trace4.addObs(Obs(ENUCoords(20, 50, 0), ObsTime()))
        trace4.addObs(Obs(ENUCoords(30, 50, 0), ObsTime()))
        #trace4.plot('k-')
        
        trace3 = Track([], 1)
        trace3.addObs(Obs(ENUCoords(0, 40, 0), ObsTime()))
        trace3.addObs(Obs(ENUCoords(10, 40, 0), ObsTime()))
        trace3.addObs(Obs(ENUCoords(10, 30, 0), ObsTime()))
        trace3.addObs(Obs(ENUCoords(20, 30, 0), ObsTime()))
        trace3.addObs(Obs(ENUCoords(20, 40, 0), ObsTime()))
        trace3.addObs(Obs(ENUCoords(30, 40, 0), ObsTime()))
        #trace3.plot('k-', append=True)
        
        S1 = arealStandardizedBetweenTwoTracks(trace3, trace4)
        S2 = arealStandardizedBetweenTwoTracks(trace4, trace3)
        
        self.assertEqual(S1, 10.0)
        self.assertEqual(S2, 10.0)
        
        # ----------------------------------------------------
        
        trace3.translate(0, 10)
        
        trace4.addObs(Obs(ENUCoords(30, 40, 0), ObsTime()))
        trace4.addObs(Obs(ENUCoords(40, 40, 0), ObsTime()))
        trace4.addObs(Obs(ENUCoords(40, 50, 0), ObsTime()))
        trace4.addObs(Obs(ENUCoords(50, 50, 0), ObsTime()))
        
        trace3.addObs(Obs(ENUCoords(30, 60, 0), ObsTime()))
        trace3.addObs(Obs(ENUCoords(40, 60, 0), ObsTime()))
        trace3.addObs(Obs(ENUCoords(40, 50, 0), ObsTime()))
        trace3.addObs(Obs(ENUCoords(50, 50, 0), ObsTime()))
        
        trace4.plot('b-')
        trace3.plot('r-', append=True)
        plt.xlim([-5, 60])
        plt.ylim([20, 70])
        
        S = arealStandardizedBetweenTwoTracks(trace3, trace4)
        self.assertEqual(S, 0.0)
        
        
    def testAggregatCluster(self):
        trackC = Track([], 1)
        trackC.addObs(Obs(ENUCoords(0, 0), ObsTime()))
        trackC.addObs(Obs(ENUCoords(1, 0), ObsTime()))
        trackC.addObs(Obs(ENUCoords(1, 1), ObsTime()))
        trackC.addObs(Obs(ENUCoords(0, 1), ObsTime()))
        
        coords = trackC.getCoord()
        d1 = aggregateCoordSet(coords, p=1, constraint=False)
        self.assertEqual(d1.E, 0.5)
        self.assertEqual(d1.N, 0.5)
        self.assertEqual(d1.U, 0.0)
        
        d2 = aggregateCoordSet(coords, p=2, constraint=False)
        self.assertEqual(d2.E, math.sqrt(2)/2)
        self.assertEqual(d2.N, math.sqrt(2)/2)
        self.assertEqual(d2.U, 0.0)
        
        d3 = aggregateCoordSet(coords, p=3, constraint=False)
        self.assertEqual(d3.E, (1/2)**(1.0/3))
        self.assertEqual(d3.N, (2/4)**(1.0/3))
        self.assertEqual(d3.U, 0.0)
        
    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoComparaisonMethods("testCompare"))
    suite.addTest(TestAlgoComparaisonMethods("testDifference21ProfileNN"))
    suite.addTest(TestAlgoComparaisonMethods("testDifference12ProfileNN"))
    suite.addTest(TestAlgoComparaisonMethods("testDifference21ProfileDTW"))
    suite.addTest(TestAlgoComparaisonMethods("testDifference21ProfileFDTW"))
    suite.addTest(TestAlgoComparaisonMethods("testHausdorffSimilarity"))
    suite.addTest(TestAlgoComparaisonMethods("testFrechetSimilarity"))
    suite.addTest(TestAlgoComparaisonMethods("testCentralNNTrack"))
    suite.addTest(TestAlgoComparaisonMethods("testCentralDTWTrack"))
    suite.addTest(TestAlgoComparaisonMethods("testArealStandardizedBetweenTwoTracks"))
    suite.addTest(TestAlgoComparaisonMethods("testAggregatCluster"))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)


