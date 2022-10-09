#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import matplotlib.pyplot as plt
#import numpy as np

from tracklib.core import (GPSTime, Coords, Obs, Track, TrackCollection)
import tracklib.algo.Comparison as Comparison



class TestAlgoComparaisonMethods(unittest.TestCase):
    
    __epsilon = 0.001
    
    def setUp (self):
        GPSTime.GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        # ---------------------------------------------------------------------
        
        self.trace1 = Track.Track([], 1)
        
        c1 = Coords.ENUCoords(1, 3.0, 0)
        p1 = Obs.Obs(c1, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace1.addObs(p1)
        
        c2 = Coords.ENUCoords(2, 3.0, 0)
        p2 = Obs.Obs(c2, GPSTime.GPSTime.readTimestamp("2018-01-01 10:05:00"))
        self.trace1.addObs(p2)
        
        c3 = Coords.ENUCoords(3, 2.9, 0)
        p3 = Obs.Obs(c3, GPSTime.GPSTime.readTimestamp("2018-01-01 10:10:00"))
        self.trace1.addObs(p3)
        
        c4 = Coords.ENUCoords(3.8, 2.8, 0)
        p4 = Obs.Obs(c4, GPSTime.GPSTime.readTimestamp("2018-01-01 10:15:00"))
        self.trace1.addObs(p4)
        
        c5 = Coords.ENUCoords(4.2, 2.5, 0)
        p5 = Obs.Obs(c5, GPSTime.GPSTime.readTimestamp("2018-01-01 10:20:00"))
        self.trace1.addObs(p5)
        
        c6 = Coords.ENUCoords(4.6, 2.5, 0)
        p6 = Obs.Obs(c6, GPSTime.GPSTime.readTimestamp("2018-01-01 10:25:00"))
        self.trace1.addObs(p6)
        
        c7 = Coords.ENUCoords(5.0, 2.45, 0)
        p7 = Obs.Obs(c7, GPSTime.GPSTime.readTimestamp("2018-01-01 10:30:00"))
        self.trace1.addObs(p7)
        
        # ---------------------------------------------------------------------
        
        self.trace2 = Track.Track([], 2)
        
        d1 = Coords.ENUCoords(0.8, 1.8, 0)
        r1 = Obs.Obs(d1, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace2.addObs(r1)
        
        d2 = Coords.ENUCoords(1.5, 1.5, 0)
        r2 = Obs.Obs(d2, GPSTime.GPSTime.readTimestamp("2018-01-01 10:05:00"))
        self.trace2.addObs(r2)
        
        d3 = Coords.ENUCoords(2.2, 1.55, 0)
        r3 = Obs.Obs(d3, GPSTime.GPSTime.readTimestamp("2018-01-01 10:10:00"))
        self.trace2.addObs(r3)
        
        d4 = Coords.ENUCoords(3, 1.50, 0)
        r4 = Obs.Obs(d4, GPSTime.GPSTime.readTimestamp("2018-01-01 10:15:00"))
        self.trace2.addObs(r4)
        
        d5 = Coords.ENUCoords(3.8, 1.20, 0)
        r5 = Obs.Obs(d5, GPSTime.GPSTime.readTimestamp("2018-01-01 10:20:00"))
        self.trace2.addObs(r5)
        
        d6 = Coords.ENUCoords(4.2, 1.25, 0)
        r6 = Obs.Obs(d6, GPSTime.GPSTime.readTimestamp("2018-01-01 10:25:00"))
        self.trace2.addObs(r6)
        
        d7 = Coords.ENUCoords(4.8, 1.40, 0)
        r7 = Obs.Obs(d7, GPSTime.GPSTime.readTimestamp("2018-01-01 10:30:00"))
        self.trace2.addObs(r7)
        
    def plot(self):
        self.trace1.plot()
        self.trace1.plotAsMarkers()
        self.trace2.plot()
        self.trace2.plotAsMarkers()

        plt.xlim([0, 6])
        plt.ylim([0, 3.25])
        
        
    def testSynchronize(self):
        Comparison.synchronize(self.trace1, self.trace2)
        print('TODO')
        

    def testCompare(self):
        a = Comparison.compare(self.trace1, self.trace2)
        self.assertLessEqual(abs(a - 1.4925), self.__epsilon, "Comparaison")
            

    def testCentralTrack(self):
        TRACES = []
        TRACES.append(self.trace1)
        TRACES.append(self.trace2)
        collection = TrackCollection.TrackCollection(TRACES)
        self.plot()
        
        central = Comparison.centralTrack(collection)
        
        central.plot()
        central.plotAsMarkers(frg="k", bkg="w", sym_frg=" ", sym_bkg="o")
        
        plt.show()        
        
        
    def testDifference21ProfileNN(self):
        profile = Comparison.differenceProfile(self.trace2, self.trace1, 
                                               mode = "NN", p=2)
        self.trace1.plot('r-')
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

    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoComparaisonMethods("testSynchronize"))
    suite.addTest(TestAlgoComparaisonMethods("testCompare"))
    suite.addTest(TestAlgoComparaisonMethods("testCentralTrack"))
    suite.addTest(TestAlgoComparaisonMethods("testDifference21ProfileNN"))
    suite.addTest(TestAlgoComparaisonMethods("testDifference12ProfileNN"))
    suite.addTest(TestAlgoComparaisonMethods("testDifference21ProfileDTW"))
    suite.addTest(TestAlgoComparaisonMethods("testDifference21ProfileFDTW"))
    runner = unittest.TextTestRunner()
    runner.run(suite)


