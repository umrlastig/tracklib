# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os.path
import random as r
import unittest
#import matplotlib.pyplot as plt

from tracklib.core.Obs import Obs
from tracklib.core.ObsCoords import ENUCoords
from tracklib.core.ObsTime import ObsTime
from tracklib.core.Track import Track
from tracklib.io.TrackReader import TrackReader
#from tracklib.io.FileReader import FileReader

from tracklib.algo.Segmentation import findStopsGlobal#, findStopsLocal
from tracklib.algo.Segmentation import retrieveNeighbors, stdbscan, computeAvgCluster

class TestAlgoSegmentationMethods(unittest.TestCase):
    
#    def setUp (self):
#        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
#
#
#    def testStopsAFaire(self):
#        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
#        #chemin = os.path.join(self.resource_path, './data/trace1.dat')
#        #trace = FileReader.readFromCsv(chemin, 2, 3, -1, 4, separator=",")
#        
#
#    def testFindStopsLocal(self):
#        resource_path = os.path.join(os.path.split(__file__)[0], "../..")
#        gpxpath = os.path.join(resource_path, 'data/gpx/vincennes.gpx')
#        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
#        tracks = TrackReader.readFromGpx(gpxpath, srid='ENU')
#        trace = tracks.getTrack(0)
#        #trace = trace.extract(1150, 2500)
#        print (trace.size())
#
#        
#        #trace.summary()
#
#        #plot = Plot(trace)
#        #plot.plotProfil('SPATIAL_SPEED_PROFIL')
#        
#        #trace.plot()
#        
#        stops = findStopsGlobal(trace, downsampling=5)
#        print (type(stops), len(stops))
#        
#        
#        #COLS = utils.getColorMap((220, 220, 220), (255, 0, 0))
#        #trace.plot(type='POINT', af_name='virage', append = False, cmap = COLS)
#    
#        #plt.plot(stops.getX(), stops.getY(), 'ro')
#    
#    
#        #self.assertLessEqual(3, 5)
#        
#    # def testStopPointWithAccelerationCriteria(self):
#	# 	
#    #     v1 = self.trace2.getObsAnalyticalFeature('speed', 1)
#    #     a1 = self.trace2.getObsAnalyticalFeature('acceleration', 1)
#    #     self.assertTrue(abs(v1 - 0.5) < 0.000001)
#    #     self.assertTrue(abs(a1 + 0.0) < 0.000001)
#    #     isSTP = Analytics.stop_point_with_acceleration_criteria(self.trace2, 1)
#    #     #print (v1, a1, isSTP)		
#    #     self.assertEqual(isSTP, 0)
#	# 	
#    #     v2 = self.trace2.getObsAnalyticalFeature('speed', 2)
#    #     a2 = self.trace2.getObsAnalyticalFeature('acceleration', 2)
#    #     self.assertTrue(abs(v2 - 1.0) < 0.000001)
#    #     self.assertTrue(abs(a2 - 0.075) < 0.000001)
#    #     isSTP = Analytics.stop_point_with_acceleration_criteria(self.trace2, 2)
#    #     #print (v2, a2, isSTP)		
#    #     self.assertEqual(isSTP, 0)
#        
#		
#    # def testStopPointWithTimeWindowCriteria(self):
#    #     self.assertLessEqual(3, 5)
    
    
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
    
    #suite.addTest(TestAlgoSegmentationMethods("testFindStopsLocal"))
    #suite.addTest(TestAlgoSegmentationMethods("testStopPointWithAccelerationCriteria"))
    #suite.addTest(TestAlgoSegmentationMethods("testStopPointWithTimeWindowCriteria"))
    
    # ST-DBSCAN
    suite.addTest(TestAlgoSegmentationMethods("testSTdbscanMailYM"))
    suite.addTest(TestAlgoSegmentationMethods("testSTdbscanPapier"))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)