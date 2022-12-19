#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import matplotlib.pyplot as plt
#import numpy as np

from tracklib.core import (GPSTime, Obs, Track, TrackCollection)
from tracklib.core import ObsCoords as Coords
import tracklib.algo.Comparison as Comparison


class TestAlgoComparaisonMethods(unittest.TestCase):
    
    __epsilon = 0.001
    
    def setUp (self):
        GPSTime.GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        # ---------------------------------------------------------------------
        
        self.trace1 = Track.Track([], 1)
        
        c1 = Coords.ENUCoords(1.0, 5.0, 0)
        p1 = Obs.Obs(c1, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace1.addObs(p1)
        
        c2 = Coords.ENUCoords(2.0, 5.0, 0)
        p2 = Obs.Obs(c2, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:05"))
        self.trace1.addObs(p2)
        
        c3 = Coords.ENUCoords(3.0, 6.0, 0)
        p3 = Obs.Obs(c3, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:10"))
        self.trace1.addObs(p3)
        
        c4 = Coords.ENUCoords(4.0, 6.0, 0)
        p4 = Obs.Obs(c4, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:15"))
        self.trace1.addObs(p4)
        
        c5 = Coords.ENUCoords(5.0, 5.0, 0)
        p5 = Obs.Obs(c5, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:20"))
        self.trace1.addObs(p5)
        
        c6 = Coords.ENUCoords(6.0, 5.0, 0)
        p6 = Obs.Obs(c6, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:25"))
        self.trace1.addObs(p6)
        
        c7 = Coords.ENUCoords(7.0, 4.0, 0)
        p7 = Obs.Obs(c7, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:30"))
        self.trace1.addObs(p7)
        
        c8 = Coords.ENUCoords(8.0, 5.0, 0)
        p8 = Obs.Obs(c8, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:35"))
        self.trace1.addObs(p8)
        
        c9 = Coords.ENUCoords(9.0, 5.0, 0)
        p9 = Obs.Obs(c9, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:40"))
        self.trace1.addObs(p9)
        
        c10 = Coords.ENUCoords(10.0, 5.0, 0)
        p10 = Obs.Obs(c10, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:45"))
        self.trace1.addObs(p10)
        
        c11 = Coords.ENUCoords(11.0, 5.0, 0)
        p11 = Obs.Obs(c11, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:50"))
        self.trace1.addObs(p11)
        
        # ---------------------------------------------------------------------
        
        self.trace2 = Track.Track([], 2)
        
        d1 = Coords.ENUCoords(1.0, 1.0, 0)
        r1 = Obs.Obs(d1, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace2.addObs(r1)
        
        d2 = Coords.ENUCoords(2.0, 1.0, 0)
        r2 = Obs.Obs(d2, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:05"))
        self.trace2.addObs(r2)
        
        d3 = Coords.ENUCoords(3.0, 1.0, 0)
        r3 = Obs.Obs(d3, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:10"))
        self.trace2.addObs(r3)
        
        d4 = Coords.ENUCoords(4.0, 1.0, 0)
        r4 = Obs.Obs(d4, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:15"))
        self.trace2.addObs(r4)
        
        d5 = Coords.ENUCoords(5.0, 2.0, 0)
        r5 = Obs.Obs(d5, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:20"))
        self.trace2.addObs(r5)
        
        d6 = Coords.ENUCoords(6.0, 2.0, 0)
        r6 = Obs.Obs(d6, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:25"))
        self.trace2.addObs(r6)
        
        d7 = Coords.ENUCoords(7.0, 1.0, 0)
        r7 = Obs.Obs(d7, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:30"))
        self.trace2.addObs(r7)
        
        d8 = Coords.ENUCoords(8.0, 1.0, 0)
        r8 = Obs.Obs(d8, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:35"))
        self.trace2.addObs(r8)
        
        d9 = Coords.ENUCoords(9.0, 1.0, 0)
        r9 = Obs.Obs(d9, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:40"))
        self.trace2.addObs(r9)
        
        d10 = Coords.ENUCoords(10.0, 0.0, 0)
        r10 = Obs.Obs(d10, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:40"))
        self.trace2.addObs(r10)
        
        d11 = Coords.ENUCoords(11.0, 0.5, 0)
        r11 = Obs.Obs(d11, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:45"))
        self.trace2.addObs(r11)
        
        d12 = Coords.ENUCoords(12.0, 1.0, 0)
        r12 = Obs.Obs(d12, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:50"))
        self.trace2.addObs(r12)
        
        d13 = Coords.ENUCoords(13.0, 1.0, 0)
        r13 = Obs.Obs(d13, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:55"))
        self.trace2.addObs(r13)
        
    def plot(self):
        self.trace1.plot()
        self.trace1.plotAsMarkers()
        self.trace2.plot()
        self.trace2.plotAsMarkers()

        plt.xlim([0, 6])
        plt.ylim([0, 3.25])
        
        
    def testCompare(self):
        a = Comparison.compare(self.trace1, self.trace2)
        self.assertLessEqual(abs(a - 4.0280), self.__epsilon, "Comparaison")


    def testDifference21ProfileNN(self):
        profile = Comparison.differenceProfile(self.trace2, self.trace1, 
                                               mode = "NN", p=2)
        self.trace1.plot('b-')
        self.trace2.plot('r-')
        Comparison.plotDifferenceProfile(profile, self.trace1)
        plt.show()
        
        
    def testDifference12ProfileNN(self):
        profile = Comparison.differenceProfile(self.trace1, self.trace2, 
                                               mode = "NN", p=2)
        self.trace1.plot('r-')
        self.trace2.plot('r-')
        Comparison.plotDifferenceProfile(profile, self.trace2)
        plt.show()
        
        
    def testDifference21ProfileDTW(self):
        profile = Comparison.differenceProfile(self.trace2, self.trace1, 
                                               mode = "DTW", p=2)
        self.trace1.plot('r-')
        self.trace2.plot('r-')
        Comparison.plotDifferenceProfile(profile, self.trace1)
        plt.show()
    
    
    def testDifference21ProfileFDTW(self):
        profile = Comparison.differenceProfile(self.trace2, self.trace1, 
                                               mode = "FDTW", p=2)
        self.trace1.plot('r-')
        self.trace2.plot('r-')
        Comparison.plotDifferenceProfile(profile, self.trace1)
        plt.show()
        
        
    def testHausdorffSimilarity(self):
        trackA = Track.Track([], 1)
        c = Coords.ENUCoords(1.0, 0.0, 0)
        p = Obs.Obs(c, GPSTime.GPSTime())
        trackA.addObs(p)
        c = Coords.ENUCoords(0.0, 1.0, 0)
        p = Obs.Obs(c, GPSTime.GPSTime())
        trackA.addObs(p)
        c = Coords.ENUCoords(-1.0, 0.0, 0)
        p = Obs.Obs(c, GPSTime.GPSTime())
        trackA.addObs(p)
        c = Coords.ENUCoords(0.0, -1.0, 0)
        p = Obs.Obs(c, GPSTime.GPSTime())
        trackA.addObs(p)

        trackB = Track.Track([], 1)
        c = Coords.ENUCoords(2.0, 0.0, 0)
        p = Obs.Obs(c, GPSTime.GPSTime())
        trackB.addObs(p)
        c = Coords.ENUCoords(0.0, 2.0, 0)
        p = Obs.Obs(c, GPSTime.GPSTime())
        trackB.addObs(p)
        c = Coords.ENUCoords(-2.0, 0.0, 0)
        p = Obs.Obs(c, GPSTime.GPSTime())
        trackB.addObs(p)
        c = Coords.ENUCoords(0.0, -4.0, 0)
        p = Obs.Obs(c, GPSTime.GPSTime())
        trackB.addObs(p)

        dAB = Comparison.premiereComposanteHausdorff(trackA, trackB)
        dBA = Comparison.premiereComposanteHausdorff(trackB, trackA)
        
        import numpy as np
        from scipy.spatial.distance import directed_hausdorff
        u = np.array([(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)])
        v = np.array([(2.0, 0.0), (0.0, 2.0), (-2.0, 0.0), (0.0, -4.0)])
        
        duv = directed_hausdorff(u, v)[0]
        dvu = directed_hausdorff(v, u)[0]
        
        self.assertEqual(dAB, duv)
        self.assertEqual(dBA, dvu)
        self.assertEqual(Comparison.hausdorff(trackA, trackB), 
                         max(directed_hausdorff(u, v)[0], directed_hausdorff(v, u)[0]))
        
    def testFrechetSimilarity(self):
        trackA = Track.Track([], 1)
        c = Coords.ENUCoords(2.0, 1.0, 0)
        p = Obs.Obs(c, GPSTime.GPSTime())
        trackA.addObs(p)
        c = Coords.ENUCoords(3.0, 1.0, 0)
        p = Obs.Obs(c, GPSTime.GPSTime())
        trackA.addObs(p)
        c = Coords.ENUCoords(4.0, 2.0, 0)
        p = Obs.Obs(c, GPSTime.GPSTime())
        trackA.addObs(p)
        c = Coords.ENUCoords(5.0, 1.0, 0)
        p = Obs.Obs(c, GPSTime.GPSTime())
        trackA.addObs(p)

        trackB = Track.Track([], 1)
        c = Coords.ENUCoords(2.0, 0.0, 0)
        p = Obs.Obs(c, GPSTime.GPSTime())
        trackB.addObs(p)
        c = Coords.ENUCoords(3.0, 0.0, 0)
        p = Obs.Obs(c, GPSTime.GPSTime())
        trackB.addObs(p)
        c = Coords.ENUCoords(4.0, 0.0, 0)
        p = Obs.Obs(c, GPSTime.GPSTime())
        trackB.addObs(p)

        self.assertEqual(Comparison.discreteFrechet(trackA, trackB), 2.0)
        
    
    def testCentralNNTrack(self):
        TRACES = []
        TRACES.append(self.trace1)
        TRACES.append(self.trace2)
        collection = TrackCollection.TrackCollection(TRACES)
        self.plot()
        
        central = Comparison.centralTrack(collection)
        
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
        collection = TrackCollection.TrackCollection(TRACES)
        self.plot()
        
        central = Comparison.centralTrack(collection, mode = "DTW")
        
        central.plot()
        central.plotAsMarkers(frg="k", bkg="w", sym_frg=" ", sym_bkg="o")
        
        plt.title('central DTW')
        plt.xlim([0, 14])
        plt.ylim([-1, 7])
        plt.show()   

    
    def testMedoidHausdorffTrack(self):
        TRACES = []
        TRACES.append(self.trace1)
        TRACES.append(self.trace2)
        collection = TrackCollection.TrackCollection(TRACES)
        self.plot()
        
        medoid = Comparison.medoid(collection, mode = "Hausdorff")

    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    #suite.addTest(TestAlgoComparaisonMethods("testCompare"))
    #suite.addTest(TestAlgoComparaisonMethods("testDifference21ProfileNN"))
    #suite.addTest(TestAlgoComparaisonMethods("testDifference12ProfileNN"))
    #suite.addTest(TestAlgoComparaisonMethods("testDifference21ProfileDTW"))
    #suite.addTest(TestAlgoComparaisonMethods("testDifference21ProfileFDTW"))
    #suite.addTest(TestAlgoComparaisonMethods("testHausdorffSimilarity"))
    #suite.addTest(TestAlgoComparaisonMethods("testFrechetSimilarity"))
    suite.addTest(TestAlgoComparaisonMethods("testCentralNNTrack"))
    suite.addTest(TestAlgoComparaisonMethods("testCentralDTWTrack"))
    #suite.addTest(TestAlgoComparaisonMethods("testMedoidHausdorffTrack"))
    runner = unittest.TextTestRunner()
    runner.run(suite)


