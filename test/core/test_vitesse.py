#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

import math
import os.path
import unittest

from tracklib import ObsTime, Operator, TrackReader


class TestVitesseMethods(unittest.TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")

    def test_tableau_af_rmse_1(self):

        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        chemin = os.path.join(self.resource_path, './data/trace1.dat')
        track = TrackReader.readFromCsv(chemin, 2, 3, -1, 4, separator=",")

        track.estimate_speed()

        track.operate(Operator.DIFFERENTIATOR, "x", "dx")
        track.operate(Operator.DIFFERENTIATOR, "y", "dy")
        track.operate(Operator.SQUARE, "dx", "dx2")
        track.operate(Operator.SQUARE, "dy", "dy2")
        track.operate(Operator.ADDER, "dx2", "dy2", "dx2+dy2")
        track.operate(Operator.SQRT, "dx2+dy2", "ds")

        track.operate(Operator.SHIFT_RIGHT, "t", "t1")
        track.operate(Operator.SUBSTRACTER, "t", "t1", "dt")
        track.operate(Operator.DIVIDER, "ds", "dt", "ds/dt")

        #print (track.getListAnalyticalFeatures())
        self.assertEqual(len(track.getListAnalyticalFeatures()), 10)
        L = ['speed', 'dx', 'dy', 'dx2', 'dy2', 'dx2+dy2', 'ds', 't1', 'dt', 'ds/dt']
        L.sort()
        T = track.getListAnalyticalFeatures()
        T.sort()
        self.assertEqual(T, L)

        track.operate(Operator.SUBSTRACTER, "speed", "ds/dt", "err")
        track.operate(Operator.SQUARE, "err", "err2")
        mse = track.operate(Operator.AVERAGER, "err2", "merr2")
        rmse = math.sqrt(mse)
        self.assertTrue((rmse - 1.28) < 0.01)


    def test_tableau_af_rmse_2(self):

        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        chemin = os.path.join(self.resource_path, './data/trace0.gps')
        track = TrackReader.readFromCsv(chemin, 2, 3, -1, 1, separator=",")

        track.estimate_speed()

        track.operate(Operator.DIFFERENTIATOR, "x", "dx")
        track.operate(Operator.DIFFERENTIATOR, "y", "dy")
        track.operate(Operator.SQUARE, "dx", "dx2")
        track.operate(Operator.SQUARE, "dy", "dy2")
        track.operate(Operator.ADDER, "dx2", "dy2", "dx2+dy2")
        track.operate(Operator.SQRT, "dx2+dy2", "ds")

        track.operate(Operator.SHIFT_RIGHT, "t", "t1")
        track.operate(Operator.SUBSTRACTER, "t", "t1", "dt")
        track.operate(Operator.DIVIDER, "ds", "dt", "ds/dt")
        
        self.assertEqual(len(track.getListAnalyticalFeatures()), 10)
        L = ['speed', 'dx', 'dy', 'dx2', 'dy2', 'dx2+dy2', 'ds', 't1', 'dt', 'ds/dt']
        L.sort()
        T = track.getListAnalyticalFeatures()
        T.sort()
        self.assertEqual(T, L)

        track.operate(Operator.SUBSTRACTER, "speed", "ds/dt", "err")
        track.operate(Operator.SQUARE, "err", "err2")
        mse = track.operate(Operator.AVERAGER, "err2", "merr2")
        rmse = math.sqrt(mse)
        # print("RMSE =", math.sqrt(mse), "m/s")
        self.assertTrue((rmse - 2.36) < 0.01)
        
        #plt.plot(track.getT(), track.getAnalyticalFeature("ds/dt"), 'b-')
        #plt.plot(track.getT(), track.getAnalyticalFeature("speed"), 'r-')
        

    def test_compare_calculs_vitesse(self):
        '''
        '''
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        chemin = os.path.join(self.resource_path, './data/trace0.gps')
        track = TrackReader.readFromCsv(chemin, 2, 3, -1, 1, separator=",")
        
        # 1ère méthode
        track.estimate_speed()
        # print (track.getListAnalyticalFeatures())
        self.assertEqual(len(track.getListAnalyticalFeatures()), 1)
        L = ['speed']
        self.assertEqual(track.getListAnalyticalFeatures(), L)
        
        #2ème méthode
        track.operate(Operator.SHIFT_RIGHT, "x", "x1")
        track.operate(Operator.SHIFT_LEFT, "x", "x2")
        track.operate(Operator.SUBSTRACTER, "x2", "x1", "dx")
        
        track.operate(Operator.SHIFT_RIGHT, "y", "y1")
        track.operate(Operator.SHIFT_LEFT, "y", "y2")
        track.operate(Operator.SUBSTRACTER, "y2", "y1", "dy")
        
        track.operate(Operator.SQUARE, "dx", "dx2")
        track.operate(Operator.SQUARE, "dy", "dy2")
        track.operate(Operator.ADDER, "dx2", "dy2", "dx2+dy2")
        track.operate(Operator.SQRT, "dx2+dy2", "ds")

        track.operate(Operator.SHIFT_RIGHT, "t", "t1")
        track.operate(Operator.SHIFT_LEFT, "t", "t2")
        track.operate(Operator.SUBSTRACTER, "t2", "t1", "dt")
        track.operate(Operator.DIVIDER, "ds", "dt", "ds/dt")
        
        #print (track.getListAnalyticalFeatures())
        
        #print (track.getObsAnalyticalFeature('speed', 10))
        #print (track.getObsAnalyticalFeature('ds/dt', 10))
        
        VM1 = track.getAnalyticalFeature("speed")
        #print (VM1[0:10])
        VM2 = track.getAnalyticalFeature("ds/dt")
        #print (VM2[0:10])
        self.assertEqual(VM1[1:len(VM1)-1], VM2[1:len(VM2)-1])
        
        track.operate(Operator.SUBSTRACTER, "speed", "ds/dt", "err")
        track.operate(Operator.SQUARE, "err", "err2")
        mse = track.operate(Operator.AVERAGER, "err2", "merr2")
        # print("RMSE =", math.sqrt(mse), "m/s")
        self.assertTrue(math.sqrt(mse) < 0.000001)
        
        
if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestVitesseMethods("test_tableau_af_rmse_1"))
	suite.addTest(TestVitesseMethods("test_tableau_af_rmse_2"))
	suite.addTest(TestVitesseMethods("test_compare_calculs_vitesse"))
	runner = unittest.TextTestRunner()
	runner.run(suite)