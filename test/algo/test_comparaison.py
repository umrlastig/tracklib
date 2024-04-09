#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import matplotlib.pyplot as plt
import math
import os.path
import random
from tracklib import (Obs, ObsTime, ENUCoords, Track,
                      TrackReader,
                      averagingCoordSet, compare, match,
                      plotMatching, MARKERS_TYPE_WARNING,
                      MODE_COMPARISON_HAUSDORFF,
                      MODE_COMPARISON_POINTWISE,
                      MODE_COMPARISON_DTW,
                      MODE_COMPARISON_FRECHET,
                      MODE_COMPARISON_AREAL,
                      MODE_MATCHING_DTW,
                      MODE_MATCHING_FRECHET,
                      MODE_MATCHING_FDTW,
                      generate, GaussianKernel)


class TestAlgoComparaisonMethods(unittest.TestCase):
    
    __epsilon = 0.001
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        
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
        
        #self.plot()
        
        
    def plot(self):
        self.trace1.plot()
        self.trace1.plotAsMarkers()
        self.trace2.plot()
        self.trace2.plotAsMarkers()

        plt.xlim([0, 14])
        plt.ylim([-1, 7])
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

        d = compare(trackA, trackB, mode=MODE_COMPARISON_HAUSDORFF)
        self.assertLessEqual(abs(d - 2.12132), self.__epsilon)
        
        
    def testMatchDTWL2(self):
        chemin1 = os.path.join(self.resource_path, 'test/data/compare/dtw1.csv')
        trace1 = TrackReader.readFromCsv(chemin1, 0, 1, 2, 3, separator=",",read_all=True, h=1)
        trace1.plot('m-')
        trace1.plotAsMarkers(type=MARKERS_TYPE_WARNING)
        
        chemin2 = os.path.join(self.resource_path, 'test/data/compare/dtw2.csv')
        trace2 = TrackReader.readFromCsv(chemin2, 0, 1, 2, 3, separator=",",read_all=True, h=1)
        trace2.plot('c-')
        trace2.plotAsMarkers(bkg='w', frg='c', sym_frg = " ", sym_bkg = "v")

        profile = match(trace1, trace2, mode=MODE_MATCHING_DTW, 
                        p=2, dim=2, verbose=False, plot=False)
        plotMatching(profile, trace2)
        plt.xlim([-1, 12])
        plt.ylim([-1, 5.5])
        plt.show()

        self.assertCountEqual([0], profile[0, "pair"])
        self.assertListEqual([0], profile[0, "pair"])
        
        self.assertCountEqual([2,1], profile[1, "pair"])
        self.assertListEqual([2,1], profile[1, "pair"])
        
        self.assertCountEqual([3], profile[2, "pair"])
        self.assertListEqual([3], profile[2, "pair"])
        
        self.assertCountEqual([4], profile[3, "pair"])
        self.assertListEqual([4], profile[3, "pair"])
        self.assertCountEqual([4], profile[4, "pair"])
        self.assertListEqual([4], profile[4, "pair"])
        self.assertCountEqual([4], profile[5, "pair"])
        self.assertListEqual([4], profile[5, "pair"])
        
        self.assertCountEqual([5], profile[6, "pair"])
        self.assertListEqual([5], profile[6, "pair"])
        
        self.assertCountEqual([6], profile[7, "pair"])
        self.assertListEqual([6], profile[7, "pair"])
        
        diff = abs(profile.score - 14.52)
        self.assertLessEqual(diff, self.__epsilon, "Score")
        
    def testMatchDTWL1(self):
        chemin1 = os.path.join(self.resource_path, 'test/data/compare/dtw1.csv')
        trace1 = TrackReader.readFromCsv(chemin1, 0, 1, 2, 3, separator=",",read_all=True, h=1)
        trace1.plot('m-')
        trace1.plotAsMarkers(type=MARKERS_TYPE_WARNING)
        
        chemin2 = os.path.join(self.resource_path, 'test/data/compare/dtw2.csv')
        trace2 = TrackReader.readFromCsv(chemin2, 0, 1, 2, 3, separator=",",read_all=True, h=1)
        trace2.plot('c-')
        trace2.plotAsMarkers(bkg='w', frg='c', sym_frg = " ", sym_bkg = "v")
        
        profile = match(trace1, trace2, mode=MODE_MATCHING_DTW, 
                        p=1, dim=2, verbose=False, plot=False)
        plotMatching(profile, trace2)
        plt.xlim([-1, 12])
        plt.ylim([-1, 5.5])
        plt.show()
        
        self.assertCountEqual([0], profile[0, "pair"])
        self.assertListEqual([0], profile[0, "pair"])
        
        self.assertCountEqual([2,1], profile[1, "pair"])
        self.assertListEqual([2,1], profile[1, "pair"])
        
        self.assertCountEqual([3], profile[2, "pair"])
        self.assertListEqual([3], profile[2, "pair"])
        
        self.assertCountEqual([4], profile[3, "pair"])
        self.assertListEqual([4], profile[3, "pair"])
        self.assertCountEqual([4], profile[4, "pair"])
        self.assertListEqual([4], profile[4, "pair"])
        self.assertCountEqual([4], profile[5, "pair"])
        self.assertListEqual([4], profile[5, "pair"])
        
        self.assertCountEqual([5], profile[6, "pair"])
        self.assertListEqual([5], profile[6, "pair"])
        
        self.assertCountEqual([6], profile[7, "pair"])
        self.assertListEqual([6], profile[7, "pair"])
        
        diff = abs(profile.score - 10.357)
        self.assertLessEqual(diff, self.__epsilon, "Score")
        
    def testMatchDTWLInf(self):
        chemin1 = os.path.join(self.resource_path, 'test/data/compare/dtw1.csv')
        trace1 = TrackReader.readFromCsv(chemin1, 0, 1, 2, 3, separator=",",read_all=True, h=1)
        trace1.plot('m-')
        trace1.plotAsMarkers(type=MARKERS_TYPE_WARNING)
        
        chemin2 = os.path.join(self.resource_path, 'test/data/compare/dtw2.csv')
        trace2 = TrackReader.readFromCsv(chemin2, 0, 1, 2, 3, separator=",",read_all=True, h=1)
        trace2.plot('c-')
        trace2.plotAsMarkers(bkg='w', frg='c', sym_frg = " ", sym_bkg = "v")
        
        profile = match(trace1, trace2, mode=MODE_MATCHING_DTW, 
                        p=math.inf, dim=2, verbose=False, plot=False)
        plotMatching(profile, trace2)
        plt.xlim([-1, 12])
        plt.ylim([-1, 5.5])
        plt.show()
        
        self.assertCountEqual([0], profile[0, "pair"])
        self.assertListEqual([0], profile[0, "pair"])
        
        self.assertCountEqual([2,1], profile[1, "pair"])
        self.assertListEqual([2,1], profile[1, "pair"])
        
        self.assertCountEqual([3], profile[2, "pair"])
        self.assertListEqual([3], profile[2, "pair"])
        
        self.assertCountEqual([4], profile[3, "pair"])
        self.assertListEqual([4], profile[3, "pair"])
        self.assertCountEqual([4], profile[4, "pair"])
        self.assertListEqual([4], profile[4, "pair"])
        self.assertCountEqual([4], profile[5, "pair"])
        self.assertListEqual([4], profile[5, "pair"])
        
        self.assertCountEqual([5], profile[6, "pair"])
        self.assertListEqual([5], profile[6, "pair"])
        
        self.assertCountEqual([6], profile[7, "pair"])
        self.assertListEqual([6], profile[7, "pair"])
        
        diff = abs(profile.score - 2.502)
        self.assertLessEqual(diff, self.__epsilon, "Score")
        
    def testMatchFDTWL2(self):
        chemin1 = os.path.join(self.resource_path, 'test/data/compare/dtw1.csv')
        trace1 = TrackReader.readFromCsv(chemin1, 0, 1, 2, 3, separator=",",read_all=True, h=1)
        trace1.plot('m-')
        trace1.plotAsMarkers(type=MARKERS_TYPE_WARNING)
        
        chemin2 = os.path.join(self.resource_path, 'test/data/compare/dtw2.csv')
        trace2 = TrackReader.readFromCsv(chemin2, 0, 1, 2, 3, separator=",",read_all=True, h=1)
        trace2.plot('c-')
        trace2.plotAsMarkers(bkg='w', frg='c', sym_frg = " ", sym_bkg = "v")
        
        profile = match(trace1, trace2, mode=MODE_MATCHING_FDTW, 
                        p=2, dim=2, verbose=False, plot=False)
        plotMatching(profile, trace2)
        plt.xlim([-1, 12])
        plt.ylim([-1, 5.5])
        plt.show()
        
        self.assertCountEqual([0], profile[0, "pair"])
        self.assertListEqual([0], profile[0, "pair"])
        
        self.assertCountEqual([2,1], profile[1, "pair"])
        self.assertListEqual([2,1], profile[1, "pair"])
        
        self.assertCountEqual([3], profile[2, "pair"])
        self.assertListEqual([3], profile[2, "pair"])
        
        self.assertCountEqual([4], profile[3, "pair"])
        self.assertListEqual([4], profile[3, "pair"])
        self.assertCountEqual([4], profile[4, "pair"])
        self.assertListEqual([4], profile[4, "pair"])
        self.assertCountEqual([4], profile[5, "pair"])
        self.assertListEqual([4], profile[5, "pair"])
        
        self.assertCountEqual([5], profile[6, "pair"])
        self.assertListEqual([5], profile[6, "pair"])
        
        self.assertCountEqual([6], profile[7, "pair"])
        self.assertListEqual([6], profile[7, "pair"])
        
        diff = abs(profile.score - 14.52)
        self.assertLessEqual(diff, self.__epsilon, "Score")
        
    def testTestEqualFDTWandDTW(self):
        for i in range(1000):
            track1 = generate(0.2, dt=500, verbose=False)
            track2 = track1.noise(10, GaussianKernel(10))
            prand = 10*random.random()
            m1 = match(track1, track2, MODE_MATCHING_DTW, p=prand, verbose=False)
            m2 = match(track1, track2, MODE_MATCHING_FDTW, p=prand, verbose=False)
            # print(i, "[p = "+str(prand)+"]", m1.score == m2.score)
            self.assertTrue(m1.score == m2.score)
            
    def testDTWDim1L2(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")

        chemin1 = os.path.join(self.resource_path, 'test/data/compare/dtw3.csv')
        trace1 = TrackReader.readFromCsv(chemin1, 0, 1, 2, 3, separator=",",read_all=True, h=1)

        chemin2 = os.path.join(self.resource_path, 'test/data/compare/dtw4.csv')
        trace2 = TrackReader.readFromCsv(chemin2, 0, 1, 2, 3, separator=",",read_all=True, h=1)

        trace1.plot('m-')
        trace1.plotAsMarkers(type=MARKERS_TYPE_WARNING)
        trace2.plot('c-')
        trace2.plotAsMarkers(bkg='w', frg='c', sym_frg = " ", sym_bkg = "v")
        
        profile = match(trace1, trace2, mode=MODE_MATCHING_DTW, 
                        p=2, dim=1, verbose=False, plot=False)
        plotMatching(profile, trace2)
        
        d = match(trace1, trace2, mode=MODE_MATCHING_DTW, 
                        p=2, dim=1, verbose=False, plot=False)
        print (d)
        print (profile.score)
        
        plt.xlim([0, 7.5])
        plt.ylim([-0.5, 2.5])
        plt.show()

    def testMatchFrechet(self):
        chemin1 = os.path.join(self.resource_path, 'test/data/compare/dtw1.csv')
        trace1 = TrackReader.readFromCsv(chemin1, 0, 1, 2, 3, separator=",",read_all=True, h=1)
        trace1.plot('m-')
        trace1.plotAsMarkers(type=MARKERS_TYPE_WARNING)
        
        chemin2 = os.path.join(self.resource_path, 'test/data/compare/dtw2.csv')
        trace2 = TrackReader.readFromCsv(chemin2, 0, 1, 2, 3, separator=",",read_all=True, h=1)
        trace2.plot('c-')
        trace2.plotAsMarkers(bkg='w', frg='c', sym_frg = " ", sym_bkg = "v")
        
        trace1.plot('m-')
        trace1.plotAsMarkers(type=MARKERS_TYPE_WARNING)
        trace2.plot('c-')
        trace2.plotAsMarkers(bkg='w', frg='c', sym_frg = " ", sym_bkg = "v")

        profile = match(trace1, trace2, mode=MODE_MATCHING_FRECHET, 
                        dim=2, verbose=False, plot=False)
        plotMatching(profile, trace2)
        plt.xlim([-1, 12])
        plt.ylim([-1, 5.5])
        plt.show()
        
        self.assertCountEqual([0], profile[0, "pair"])
        self.assertListEqual([0], profile[0, "pair"])
        
        self.assertCountEqual([2,1], profile[1, "pair"])
        self.assertListEqual([2,1], profile[1, "pair"])
        
        self.assertCountEqual([3], profile[2, "pair"])
        self.assertListEqual([3], profile[2, "pair"])
        
        self.assertCountEqual([4], profile[3, "pair"])
        self.assertListEqual([4], profile[3, "pair"])
        self.assertCountEqual([4], profile[4, "pair"])
        self.assertListEqual([4], profile[4, "pair"])
        self.assertCountEqual([4], profile[5, "pair"])
        self.assertListEqual([4], profile[5, "pair"])
        
        self.assertCountEqual([5], profile[6, "pair"])
        self.assertListEqual([5], profile[6, "pair"])
        
        self.assertCountEqual([6], profile[7, "pair"])
        self.assertListEqual([6], profile[7, "pair"])
        
        diff = abs(profile.score - 2.502)
        self.assertLessEqual(diff, self.__epsilon, "Score")

    
    def testCompareFrechet(self):
        chemin1 = os.path.join(self.resource_path, 'test/data/compare/dtw1.csv')
        trace1 = TrackReader.readFromCsv(chemin1, 0, 1, 2, 3, separator=",",read_all=True, h=1)
        chemin2 = os.path.join(self.resource_path, 'test/data/compare/dtw2.csv')
        trace2 = TrackReader.readFromCsv(chemin2, 0, 1, 2, 3, separator=",",read_all=True, h=1)
        
        a = compare(trace1, trace2, mode=MODE_COMPARISON_FRECHET, 
                    dim=2)
        diff = abs(a - 2.502)
        self.assertLessEqual(diff, self.__epsilon, "Distance")
        
    def testCompareDTW(self):
        chemin1 = os.path.join(self.resource_path, 'test/data/compare/dtw1.csv')
        trace1 = TrackReader.readFromCsv(chemin1, 0, 1, 2, 3, separator=",",read_all=True, h=1)
        chemin2 = os.path.join(self.resource_path, 'test/data/compare/dtw2.csv')
        trace2 = TrackReader.readFromCsv(chemin2, 0, 1, 2, 3, separator=",",read_all=True, h=1)
        
        b = compare(trace1, trace2, mode=MODE_COMPARISON_DTW,
                    p=math.inf, dim=2)
        diff = abs(b - 2.502)
        self.assertLessEqual(diff, self.__epsilon, "Distance")
    
    def testCompareHausdorff(self):
        # Hausdorff
        b = compare(self.trace1, self.trace2, mode=MODE_COMPARISON_HAUSDORFF)
        self.assertLessEqual(abs(b - 2.121), self.__epsilon, "Comparaison")
        
    def testComparePointWise(self):
        # Pointwise
        a = compare(self.trace1, self.trace2[0:self.trace1.size()], 
                                             mode=MODE_COMPARISON_POINTWISE, 
                                             p=2)
        self.assertLessEqual(abs(a - 4.11483), self.__epsilon, "Comparaison")
        
        b = compare(self.trace1, self.trace2[0:self.trace1.size()], 
                                             mode=MODE_COMPARISON_POINTWISE, 
                                             p=1)
        self.assertLessEqual(abs(b - 4.045), self.__epsilon, "Comparaison")
        
        c = compare(self.trace1, self.trace2[0:self.trace1.size()], 
                                             mode=MODE_COMPARISON_POINTWISE, 
                                             p=math.inf)
        self.assertLessEqual(abs(c - 5.0), self.__epsilon, "Comparaison")
        
    def testCompareWithAreal(self):
        c = compare(self.trace1, self.trace2, mode=MODE_COMPARISON_AREAL)
        self.assertLessEqual(abs(c - 3.541), self.__epsilon, "Comparaison")


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
        
        S1 = compare(trace3, trace4, mode=MODE_COMPARISON_AREAL)
        S2 = compare(trace4, trace3, mode=MODE_COMPARISON_AREAL)
        
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
        
        S = compare(trace3, trace4, mode=MODE_COMPARISON_AREAL)
        self.assertEqual(S, 0.0)
        
    
    def testAggregatCluster(self):
        trackC = Track([], 1)
        trackC.addObs(Obs(ENUCoords(0, 0), ObsTime()))
        trackC.addObs(Obs(ENUCoords(1, 0), ObsTime()))
        trackC.addObs(Obs(ENUCoords(1, 1), ObsTime()))
        trackC.addObs(Obs(ENUCoords(0, 1), ObsTime()))
        coords = trackC.getCoord()
        
        
        d1 = averagingCoordSet(coords, constraint=False)
        self.assertEqual(d1.E, 0.5)
        self.assertEqual(d1.N, 0.5)
        self.assertEqual(d1.U, 0.0)
        
        '''
        d8 = averagingCoordSet(coords, p=1, constraint=True)
        self.assertEqual(d8.E, 0.0)
        self.assertEqual(d8.N, 0.0)
        self.assertEqual(d8.U, 0.0)
        
        d2 = averagingCoordSet(coords, p=2, constraint=False)
        self.assertEqual(d2.E, math.sqrt(2)/2)
        self.assertEqual(d2.N, math.sqrt(2)/2)
        self.assertEqual(d2.U, 0.0)
        
        d7 = averagingCoordSet(coords, p=2, constraint=True)
        self.assertEqual(d7.E, 1.0)
        self.assertEqual(d7.N, 1.0)
        self.assertEqual(d7.U, 0.0)
        
        d3 = averagingCoordSet(coords, p=3, constraint=False)
        self.assertEqual(d3.E, (1/2)**(1.0/3))
        self.assertEqual(d3.N, (2/4)**(1.0/3))
        self.assertEqual(d3.U, 0.0)
        d6 = averagingCoordSet(coords, p=3, constraint=True)
        self.assertEqual(d6.E, 1.0)
        self.assertEqual(d6.N, 1.0)
        self.assertEqual(d6.U, 0.0)
        
        d4 = averagingCoordSet(coords, p=math.inf, constraint=False)
        self.assertEqual(d4.E, 1.0)
        self.assertEqual(d4.N, 1.0)
        self.assertEqual(d4.U, 0.0)
        d5 = averagingCoordSet(coords, p=math.inf, constraint=True)
        self.assertEqual(d5.E, 1.0)
        self.assertEqual(d5.N, 1.0)
        self.assertEqual(d4.U, 0.0)
        '''
        
    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    
    suite.addTest(TestAlgoComparaisonMethods("testMatchDTWL2"))
    suite.addTest(TestAlgoComparaisonMethods("testMatchDTWL1"))
    suite.addTest(TestAlgoComparaisonMethods("testMatchDTWLInf"))
    suite.addTest(TestAlgoComparaisonMethods("testMatchFDTWL2"))
    suite.addTest(TestAlgoComparaisonMethods("testMatchFrechet"))
    suite.addTest(TestAlgoComparaisonMethods("testTestEqualFDTWandDTW"))
    suite.addTest(TestAlgoComparaisonMethods("testDTWDim1L2"))
    
    suite.addTest(TestAlgoComparaisonMethods("testCompareWithAreal"))
    suite.addTest(TestAlgoComparaisonMethods("testCompareDTW"))
    suite.addTest(TestAlgoComparaisonMethods("testCompareFrechet"))
    suite.addTest(TestAlgoComparaisonMethods("testCompareHausdorff"))
    suite.addTest(TestAlgoComparaisonMethods("testComparePointWise"))
    
    suite.addTest(TestAlgoComparaisonMethods("testHausdorffSimilarity"))
    suite.addTest(TestAlgoComparaisonMethods("testArealStandardizedBetweenTwoTracks"))
    suite.addTest(TestAlgoComparaisonMethods("testAggregatCluster"))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)


