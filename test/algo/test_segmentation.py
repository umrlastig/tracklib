# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os.path
import random as r
import unittest

from tracklib import (Obs, ObsTime, ENUCoords, heading, Track,
                      segmentation, split, splitAR,
                      MODE_COMPARAISON_OR, MODE_COMPARAISON_AND,
                      findStops, findStopsLocal, MODE_STOPS_LOCAL,
                      findStopsGlobal, plotStops, MODE_STOPS_GLOBAL,
                      findStopsLocalWithAcceleration, MODE_STOPS_ACC,
                      retrieveNeighbors, stdbscan, computeAvgCluster,
                      splitReturnTripExhaustive)


class TestAlgoSegmentation(unittest.TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        #self.trace.estimate_speed()

    def testSegmentation(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        trace = Track([], 1)
        trace.addObs(Obs(ENUCoords(0, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(1, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(2, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(2, 1, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(3, 1, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(4, 1, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(5, 1, 0), ObsTime()))
        
        trace.addAnalyticalFeature(heading)
        trace.createAnalyticalFeature('Temp', [39,30,37,35,45,40,30])
        
        #  Segmentation 1
        segmentation(trace, ["Temp", "heading"], "decoup1", [35, 0], MODE_COMPARAISON_AND)
        T = trace.getAnalyticalFeature('decoup1')
        self.assertEqual(len(T), 7)
        self.assertListEqual(T, [1,1,1,0,1,1,1])
        
        #  Segmentation 2
        segmentation(trace, ["Temp", "heading"], "decoup2", [35, 0], MODE_COMPARAISON_OR)
        T = trace.getAnalyticalFeature('decoup2')
        self.assertEqual(len(T), 7)
        self.assertListEqual(T, [1,0,1,0,1,1,0])
        
        #  Segmentation 3
        segmentation(trace, "heading", "decoup3", 0)
        T = trace.getAnalyticalFeature('decoup3')
        self.assertEqual(len(T), 7)
        self.assertListEqual(T, [1,1,1,0,1,1,1])
    
        # split avec indice
        TRACES = split(trace, [0,2,5,6])
        self.assertEqual(len(TRACES), 3)
        self.assertEqual(TRACES[0].size(), 3)
        #print (TRACES[0])
        #self.assertEqual(TRACES[0][0], Obs(ENUCoords(0, 0, 0), ObsTime()))
        self.assertEqual(TRACES[1].size(), 4)
        self.assertEqual(TRACES[2].size(), 2)
        
        # split avec AF
        TRACES = split(trace, "decoup3")
        self.assertEqual(len(TRACES), 7)
        
        
    def testSplitAR(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        trace = Track([], 1)
        
        r.seed(10)
        for i in range(20):
            x = r.random() * 2 + 2
            y = r.random() * 2 + 2
            trace.addObs(Obs(ENUCoords(x, y, 0), ObsTime()))
        for i in range(30):
            x = r.random() * 2 + 5
            y = r.random() * 2 + 5
            trace.addObs(Obs(ENUCoords(x, y, 0), ObsTime()))
            
        trace.plot(type='POINT', sym='go', pointsize=50)
        
        pt1 = ENUCoords(3,3,0)
        plt.plot([3],[3], 'ro')
        pt2 = ENUCoords(6,6,0)
        plt.plot([6],[6], 'ro')
        tracks = splitAR(trace, pt1=pt1, pt2=pt2, radius=0.5, nb_min_pts=6)
        self.assertEqual(len(tracks), 2)
        
        trace1 = tracks[0]
        self.assertEqual(trace1.size(), 7)
        trace2 = tracks[1]
        self.assertEqual(trace2.size(), 7)
        
        trace1.plot(type='POINT', sym='mo', pointsize=30, append=True)
        trace2.plot(type='POINT', sym='bo', pointsize=30, append=True)
        
        plt.xlim([1,8])
        plt.ylim([1,8])
        plt.show()
        
        
    def testSplitReturnTripExhaustive(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        trace = Track([], 1)
        trace.addObs(Obs(ENUCoords(0*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:00")))
        trace.addObs(Obs(ENUCoords(2*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:10:00")))
        trace.addObs(Obs(ENUCoords(3*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:20:00")))
        trace.addObs(Obs(ENUCoords(6*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:30:00")))
        trace.addObs(Obs(ENUCoords(8*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:40:00")))
        
        tracks = splitReturnTripExhaustive(trace)
        print ('nombre sous-traces=', len(tracks))
        trace1 = tracks.getTrack(0)
        print (len(trace), len(trace1))

    def testSplitReturnTripFast(self):
        pass
    

    def testFindStopsGlocal(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        trace = Track([], 1)
        trace.addObs(Obs(ENUCoords(0*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:00")))
        trace.addObs(Obs(ENUCoords(1*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:10:00")))
        trace.addObs(Obs(ENUCoords(2*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:20:00")))
        trace.addObs(Obs(ENUCoords(3*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:30:00")))
        trace.addObs(Obs(ENUCoords(4*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:40:00")))
        
        trace.addObs(Obs(ENUCoords(5*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:50:00")))
        trace.addObs(Obs(ENUCoords(5*600+10, 0, 0), ObsTime.readTimestamp("2018-01-01 11:00:00")))
        #trace.addObs(Obs(ENUCoords(5*600+10, 0, 0), ObsTime.readTimestamp("2018-01-01 11:10:00")))
        
        trace.addObs(Obs(ENUCoords(6*600+10, 0, 0), ObsTime.readTimestamp("2018-01-01 11:10:00")))
        trace.addObs(Obs(ENUCoords(7*600+10, 0, 0), ObsTime.readTimestamp("2018-01-01 11:20:00")))
        trace.addObs(Obs(ENUCoords(8*600+10, 0, 0), ObsTime.readTimestamp("2018-01-01 11:30:00")))
        
        trace.plotProfil('TEMPORAL_SPEED_PROFIL')
        plt.ylim([0, 1.5])
        plt.show()
        
        stops = findStopsGlobal(trace, diameter=50, duration=15, downsampling=1)
        
        self.assertEqual(len(stops), 1, 'nb stop')
        self.assertTrue(abs(stops.getAnalyticalFeature('radius')[0]- 5.0) < 0.0001, 'taille de la pause en distance')
        self.assertTrue(abs(stops.getAnalyticalFeature('duration')[0]- 600.0) < 0.0001, 'taille de la pause en temps')
        self.assertEqual(stops.getAnalyticalFeature('nb_points')[0], 2, 'nb point 1er stop')
        
        self.assertEqual(stops.getAnalyticalFeature('id_ini')[0], 5, 'indice begin 1st stop')
        self.assertEqual(stops.getAnalyticalFeature('id_end')[0], 6, 'indice end 1st stop')
        
        self.assertTrue(abs(stops.getAnalyticalFeature('rmse')[0]- 5.0) < 0.0001, 'rmse')
        
        plotStops(stops)
        
        # rebelote
        stops2 = findStops(trace, 50, 15, MODE_STOPS_GLOBAL)
        self.assertEqual(len(stops), len(stops2), 'nb stop')
        

    def testFindStopsLocal(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        trace = Track([], 1)
        
        trace.addObs(Obs(ENUCoords(0*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:00")))
        trace.addObs(Obs(ENUCoords(1*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:10:00")))
        trace.addObs(Obs(ENUCoords(2*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:20:00")))
        trace.addObs(Obs(ENUCoords(3*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:30:00")))
        trace.addObs(Obs(ENUCoords(4*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:40:00")))
        
        trace.addObs(Obs(ENUCoords(5*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:50:00")))
        trace.addObs(Obs(ENUCoords(5*600+10, 0, 0), ObsTime.readTimestamp("2018-01-01 11:00:00")))
        #trace.addObs(Obs(ENUCoords(5*600+10, 0, 0), ObsTime.readTimestamp("2018-01-01 11:10:00")))
        
        trace.addObs(Obs(ENUCoords(6*600+10, 0, 0), ObsTime.readTimestamp("2018-01-01 11:10:00")))
        trace.addObs(Obs(ENUCoords(7*600+10, 0, 0), ObsTime.readTimestamp("2018-01-01 11:20:00")))
        trace.addObs(Obs(ENUCoords(8*600+10, 0, 0), ObsTime.readTimestamp("2018-01-01 11:30:00")))
        
        trace.plotProfil('TEMPORAL_SPEED_PROFIL')
        plt.ylim([0, 1.5])
        plt.show()
        
        #print (trace.getAnalyticalFeature('speed'))
        
        stops = findStopsLocal(trace, speed=0.6, duration=10)
        
        trace.plot(type='POINT', sym='ko', pointsize=50)
        stops.plot(type='POINT', sym='ro', pointsize=30)
        plt.xlim([-600, 5500])
        plt.show()
        
        self.assertEqual(len(stops), 1, 'nb stop')
        self.assertEqual(int(stops.getAnalyticalFeature('id_ini')[0]), 5)
        self.assertEqual(int(stops.getAnalyticalFeature('id_end')[0]), 6)
        self.assertEqual(stops.getAnalyticalFeature('nb_points')[0], 2)
        self.assertTrue(abs(stops.getAnalyticalFeature('duration')[0] - 600.0) < 0.001)
        self.assertTrue(abs(stops.getAnalyticalFeature('rmse')[0] - 5.0) < 0.001)
        
        # rebelote
        stops2 = findStops(trace, 0.6, 10, MODE_STOPS_LOCAL)
        self.assertEqual(len(stops), len(stops2), 'nb stop')
    
    
    def testFindStopsLocalWithAcceleration(self):

        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        trace = Track([], 1)
        
        trace.addObs(Obs(ENUCoords(0*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:00")))
        trace.addObs(Obs(ENUCoords(1*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:10:00")))
        trace.addObs(Obs(ENUCoords(2*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:20:00")))
        trace.addObs(Obs(ENUCoords(3*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:30:00")))
        trace.addObs(Obs(ENUCoords(4*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:40:00")))
        
        trace.addObs(Obs(ENUCoords(5*600, 0, 0), ObsTime.readTimestamp("2018-01-01 10:50:00")))
        trace.addObs(Obs(ENUCoords(5*600+10, 0, 0), ObsTime.readTimestamp("2018-01-01 11:00:00")))
        #trace.addObs(Obs(ENUCoords(5*600+10, 0, 0), ObsTime.readTimestamp("2018-01-01 11:10:00")))
        
        trace.addObs(Obs(ENUCoords(6*600+10, 0, 0), ObsTime.readTimestamp("2018-01-01 11:10:00")))
        trace.addObs(Obs(ENUCoords(7*600+10, 0, 0), ObsTime.readTimestamp("2018-01-01 11:20:00")))
        trace.addObs(Obs(ENUCoords(8*600+10, 0, 0), ObsTime.readTimestamp("2018-01-01 11:30:00")))
        
        trace.plotProfil('TEMPORAL_SPEED_PROFIL')
        plt.ylim([0, 1.5])
        plt.show()
        
        #print (trace.getAnalyticalFeature('speed'))
        
        stops = findStopsLocalWithAcceleration(trace, diameter=50, duration=15)
        
        self.assertEqual(len(stops), 1, 'nb stop')
        self.assertEqual(int(stops.getAnalyticalFeature('id_ini')[0]), 5)
        self.assertEqual(int(stops.getAnalyticalFeature('id_end')[0]), 6)
        self.assertEqual(stops.getAnalyticalFeature('nb_points')[0], 2)
        self.assertTrue(abs(stops.getAnalyticalFeature('duration')[0] - 600.0) < 0.001)
        self.assertTrue(abs(stops.getAnalyticalFeature('rmse')[0] - 5.0) < 0.001)
        
        # rebelote
        stops2 = findStops(trace, 50, 15, MODE_STOPS_ACC)
        self.assertEqual(len(stops), len(stops2), 'nb stop')
        
    
    def testSTdbscanPapier(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        trace1 = Track([], 1)
        
        r.seed(10)
        for i in range(16):
            x = r.random() * 3 + 1
            y = r.random() * 7 + 1
            trace1.addObs(Obs(ENUCoords(x, y, 0), ObsTime()))
        for i in range(18):
            x = r.random() * 4 + 3
            y = r.random() * 7 + 1
            trace1.addObs(Obs(ENUCoords(x, y, 0), ObsTime()))
        
        trace1.createAnalyticalFeature('Temp', [2,1,2,2,2,3,2,3,2,3,2,3,3,2,2,2,9,10,9,8,9,9,10,9,11,10,9,8,9,10,9,11,8,9])
        trace1.plotAsMarkers()
        plt.xlim([0,10])
        plt.ylim([0,10])
        #trace1.summary()
        
        stdbscan(trace1, 'Temp', 3.5, 4, 3, 2)
        
        for i in range(34):
            noise = trace1.getObsAnalyticalFeature('noise', i)
            self.assertEqual(noise, 0)
            
        print(computeAvgCluster(trace1, 'Temp', 1))
            
        self.assertTrue(abs(computeAvgCluster(trace1, 'Temp', 1) - 2.25) < 0.001)
        self.assertTrue(abs(computeAvgCluster(trace1, 'Temp', 2) - 9.277) < 0.001)
            
        for i in range(16):
            nocluster = trace1.getObsAnalyticalFeature('stdbscan', i)
            self.assertEqual(nocluster, 1)
        for i in range(16,34):
            nocluster = trace1.getObsAnalyticalFeature('stdbscan', i)
            self.assertEqual(nocluster, 2)
        
        t2 = trace1.query('SELECT * WHERE stdbscan == 1')
        t3 = trace1.query('SELECT * WHERE stdbscan == 2')
        t4 = trace1.query('SELECT * WHERE stdbscan == 3')
        t5 = trace1.query('SELECT * WHERE stdbscan == 4')
        
        plt.plot([t2.getX()], [t2.getY()], 'bo')
        plt.plot([t3.getX()], [t3.getY()], 'ro')
        plt.plot([t4.getX()], [t4.getY()], 'co')
        plt.plot([t5.getX()], [t5.getY()], 'yo')
        
        plt.show()
    
    def testSTdbscanMailYM(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        trace = Track([], 1)
        trace.addObs(Obs(ENUCoords(0, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(1, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(2, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(3, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(4, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(5, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(6, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(7, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(8, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(9, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(10, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(11, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(12, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(13, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(14, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(15, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(16, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(17, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(18, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(19, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(20, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(21, 0, 0), ObsTime()))
        
        trace.createAnalyticalFeature('Temp', [40,1,2,1,2,3,3,2,3,4,5,6,5,5,6,6,7,7,6,7,8,8])
        trace.plotAsMarkers()
        plt.ylim([-1,1])
        
        T = retrieveNeighbors(trace, 'Temp', 0, 1, 2)
        self.assertEqual(len(T), 0)
        self.assertListEqual(T, [])
        
        T = retrieveNeighbors(trace, 'Temp', 1, 1, 2)
        self.assertEqual(len(T), 1)
        self.assertListEqual(T, [2])
        
        T = retrieveNeighbors(trace, 'Temp', 9, 1, 2)
        self.assertEqual(len(T), 2)
        self.assertListEqual(T, [8, 10])
        
        T = retrieveNeighbors(trace, 'Temp', 10, 1, 2)
        self.assertEqual(len(T), 2)
        self.assertListEqual(T, [9,11])
        
        T = retrieveNeighbors(trace, 'Temp', 21, 1, 1)
        self.assertEqual(len(T), 1)
        self.assertListEqual(T, [20])
        
        stdbscan(trace, 'Temp', 1, 2, 2, 3, False)
        
        
        self.assertEqual(trace.getObsAnalyticalFeature('noise', 0), 1)
        for i in range(1,trace.size()):
            noise = trace.getObsAnalyticalFeature('noise', i)
            self.assertEqual(noise, 0)
        
        #print(trace.getAnalyticalFeature('noise'))
        #print ('')
        #print(trace3.getAnalyticalFeature('stdbscan'))
        
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 1), 1)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 2), 1)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 3), 1)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 4), 1)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 5), 1)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 6), 1)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 7), 1)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 8), 1)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 9), 1)
        
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 10), 2)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 11), 2)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 12), 2)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 13), 2)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 14), 2)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 15), 2)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 16), 2)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 17), 2)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 18), 2)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 19), 2)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 20), 2)
        self.assertEqual(trace.getObsAnalyticalFeature('stdbscan', 21), 2)
        
        t2 = trace.query('SELECT * WHERE stdbscan == 1')
        t3 = trace.query('SELECT * WHERE stdbscan == 2')
        t4 = trace.query('SELECT * WHERE stdbscan == 3')
        t5 = trace.query('SELECT * WHERE stdbscan == 4')
        
        plt.plot([t2.getX()], [t2.getY()], 'bo')
        plt.plot([t3.getX()], [t3.getY()], 'ro')
        plt.plot([t4.getX()], [t4.getY()], 'co')
        plt.plot([t5.getX()], [t5.getY()], 'yo')
        
        plt.show()
    
    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    
    # segmentation + split
    suite.addTest(TestAlgoSegmentation("testSegmentation"))
    suite.addTest(TestAlgoSegmentation("testSplitAR"))
    suite.addTest(TestAlgoSegmentation("testSplitReturnTripExhaustive"))
    suite.addTest(TestAlgoSegmentation("testSplitReturnTripFast"))
    
    # Find stops
    suite.addTest(TestAlgoSegmentation("testFindStopsGlocal"))
    suite.addTest(TestAlgoSegmentation("testFindStopsLocal"))
    suite.addTest(TestAlgoSegmentation("testFindStopsLocalWithAcceleration"))
    
    # ST-DBSCAN
    suite.addTest(TestAlgoSegmentation("testSTdbscanMailYM"))
    suite.addTest(TestAlgoSegmentation("testSTdbscanPapier"))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)