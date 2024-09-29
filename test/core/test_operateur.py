#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import random
import unittest

from tracklib import (Track, Obs, ENUCoords, ObsTime, 
                      Operator, GaussianKernel,
                      TrackReader, TrackFormat,
                      segmentation, split,
                      computeAbsCurv,
                      generate,
                      diffJourAnneeTrace,
                      MODE_SPATIAL,
                      NAN)


def x(t):
    return 10 * math.cos(4 * math.pi * t)*(1 + math.cos(3.5 * math.pi * t))
def y(t):
    return t
def prob():
    return random.random()-0.5


class TestOperateurMethods(unittest.TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
    
    def mafonct(self, track, af_name):
        for i in range(len(track.getAnalyticalFeature(af_name))):
            val = track.getObsAnalyticalFeature(af_name, i)
            if val == 0:
                track.setObsAnalyticalFeature(af_name, i, 1)
            else:
                track.setObsAnalyticalFeature(af_name, i, 0)
        
    def test_abs_curv1(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        chemin = os.path.join(self.resource_path, 'data/trace1.dat')
        param = TrackFormat({'ext': 'CSV',
                             'id_E': 2,
                             'id_N': 3,
                             'id_U': -1,
                             'id_T': 4,
                             'separator': ',',
                             'cmt': '#',
                             'time_ini': -1,
                             'no_data_value': -999999,
                             'srid': 'ENUCoords',
                             'header': 0,
                             'srid': 'ENU'})
        track = TrackReader.readFromFile(chemin, param)
        
        track.addAnalyticalFeature(diffJourAnneeTrace)
        track.operate(Operator.INVERTER, "diffJourAnneeTrace", "rando_jour_neg")
        
        segmentation(track, ["rando_jour_neg"], "rando_jour", [-1])
        self.mafonct(track, "rando_jour")
        TRACES = split(track, "rando_jour")
        
        self.assertTrue(len(TRACES) == 4)
        
        if len(TRACES) > 0:
            trace = TRACES[1]
            # trace.summary()
            computeAbsCurv(trace)
            
            trace.resample(3, MODE_SPATIAL)
            computeAbsCurv(trace)
            Sigma = trace.getAbsCurv()
            trace.estimate_speed()
            Speed = trace.getAnalyticalFeature('speed')
            #print (Speed)
            #print (trace.getListAnalyticalFeatures())
            tabAF = trace.getListAnalyticalFeatures()
            tabAF.sort()
            self.assertEqual(2, len(tabAF))
            self.assertEqual('abs_curv', tabAF[0])
            self.assertEqual('speed', tabAF[1])
            
            # =============================================================================
            # ============================================================================
            #
            fig, ax1 = plt.subplots(figsize=(15, 3))
            #plt.plot(trace.getAnalyticalFeature("sigma"), trace.getAnalyticalFeature("speed2"), '-', color='gold')
            plt.plot(Sigma, Speed, '-', color='skyblue')
            plt.show()

    
    def test_random(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        #track = core_Track.Track.generate(TestOperateurMethods.x, TestOperateurMethods.y)
        track = generate(x, y)

        track.createAnalyticalFeature("a")

        track.operate(Operator.RANDOM, ("a","a"), prob, ("x_noised","y_noised"))
        track.operate(Operator.INTEGRATOR, ("x_noised","y_noised"))
        track.operate(Operator.SCALAR_MULTIPLIER, ("x_noised","y_noised"), 0.02)
        track.operate(Operator.ADDER, ("x_noised","y_noised"), ("x","y"))

        kernel = GaussianKernel(21)
        kernel.setFilterBoundary(True)

        track.operate(Operator.FILTER, ("x_noised", "y_noised"), kernel, ("x_filtered", "y_filtered"))

        #plt.plot(track.getX(), track.getY(), 'k--')
        #plt.plot(track.getAnalyticalFeature("x_noised"), track.getAnalyticalFeature("y_noised"), 'b-')
        #plt.plot(track.getAnalyticalFeature("x_filtered"), track.getAnalyticalFeature("y_filtered"), 'r-')
        #plt.show()    
        
        
    def x2(t):
        return 10*math.cos(2*math.pi*t)*(1+math.cos(2*math.pi*t))
    def y2(t):
        return 10*math.sin(2*math.pi*t)*(1+math.cos(2*math.pi*t))    

    def test_generate(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        #track = core_Track.Track.generate(TestOperateurMethods.x2, TestOperateurMethods.y2)
        track = generate(TestOperateurMethods.x2, TestOperateurMethods.y2)
        
        track.createAnalyticalFeature("a")
        track.operate(Operator.RANDOM, "a", prob, "randx")
        track.operate(Operator.RANDOM, "a", prob, "randy")

        track.operate(Operator.INTEGRATOR, "randx", "randx")
        track.operate(Operator.INTEGRATOR, "randy", "randy")

        track.operate(Operator.SCALAR_MULTIPLIER, "randx", 0.5, "noisex")
        track.operate(Operator.SCALAR_MULTIPLIER, "randx", 0.5, "noisey")

        track.operate(Operator.ADDER, "x", "noisex", "x_noised")
        track.operate(Operator.ADDER, "y", "noisey", "y_noised")

        kernel = GaussianKernel(31)

        track.operate(Operator.FILTER, "x_noised", kernel, "x_filtered")
        track.operate(Operator.FILTER, "y_noised", kernel, "y_filtered")


        plt.plot(track.getAnalyticalFeature("x"), track.getAnalyticalFeature("y"), 'k--')
        plt.plot(track.getAnalyticalFeature("x_noised"), track.getAnalyticalFeature("y_noised"), 'b-')
        plt.plot(track.getAnalyticalFeature("x_filtered"), track.getAnalyticalFeature("y_filtered"), 'r-')

        plt.show()


    def test_import(self):
        
        # ----------------------------------------------
        # Trajectoire calculee par GPS (mode standard)
        # ----------------------------------------------
        path = os.path.join(self.resource_path, 'data/rawGps1Data.pos')
        track1 = TrackReader.readFromFile(path, "RTKLIB")     # Lecture du fichier
        track1.toProjCoords(2154)                             # Projection Lambert 93
        track1 = track1 > 400                                 # Suppression 400 derniers points

        # ----------------------------------------------
        # Trajectoire de reference IMU
        # ----------------------------------------------
        path = os.path.join(self.resource_path, "data/imu_opk_Vincennes1909121306.txt")
        track3 = TrackReader.readFromFile(path, "IMU_STEREOPOLIS")   # Lecture du fichier
        track3 = track3 < 400                                       # Suppression 400 derniers points
        track3.incrementTime(0, 18)                                 # Ajout 18 secondes UTC -> GPS Time
        track3.translate(0, 0, 47.66)                               # Conversion altitude -> hauteur
        #track3 = track3 // track1                                   # Synchronisation sur track1                              


        # ----------------------------------------------
        # Calcul RMSE dans chaque direction
        # ----------------------------------------------
        track1.createAnalyticalFeature("x2", track3.getX())
        track1.createAnalyticalFeature("y2", track3.getY())
        track1.createAnalyticalFeature("z2", track3.getZ())

        std_e = track1.operate(Operator.L2, "x", "x2")
        std_n = track1.operate(Operator.L2, "y", "y2")
        std_u = track1.operate(Operator.L2, "z", "z2")

        #print("E std = " + '{:5.3f}'.format(std_e) + " m")
        self.assertEqual('{:5.3f}'.format(std_e), '63.055')
        #print("N std = " + '{:5.3f}'.format(std_n) + " m")
        self.assertEqual('{:5.3f}'.format(std_n), '116.343')
        #print("U std = " + '{:5.3f}'.format(std_u) + " m")
        self.assertEqual('{:5.3f}'.format(std_u), '8.616')
        
        
    def test_unary_void_operator(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        trace = Track([], 1)
        trace.addObs(Obs(ENUCoords(0, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(1, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(2, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(3, 1, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(4, 1, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(5, 1, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(6, 1, 0), ObsTime()))
        #trace.plot('bo')
        
        trace["op1"] = [1, -1, 1, -2, 2, -2, 2]
        self.assertListEqual([1, -1, 1, -2, 2, -2, 2], trace.getAnalyticalFeature('op1'))
        
        trace.operate(Operator.IDENTITY, "op1", "op2")
        self.assertListEqual([1, -1, 1, -2, 2, -2, 2], trace.getAnalyticalFeature('op2'))
        
        trace.operate(Operator.RECTIFIER, "op1", "op3")
        self.assertListEqual([1, 1, 1, 2, 2, 2, 2], trace.getAnalyticalFeature('op3'))
        
        trace.operate(Operator.FORWARD_FINITE_DIFF, "op1", "op4")
        self.assertListEqual([-2, 2, -3, 4, -4, 4, NAN], trace.getAnalyticalFeature('op4'))

        trace.operate(Operator.CENTERED_FINITE_DIFF, "op1", "op5")
        self.assertListEqual([NAN, 0, -1, 1, 0, 0, NAN], trace.getAnalyticalFeature('op5'))
        
        trace.operate(Operator.BACKWARD_FINITE_DIFF, "op1", "op6")
        self.assertListEqual([NAN, -2, 2, -3, 4, -4, 4], trace.getAnalyticalFeature('op6'))
        
        trace.operate(Operator.SECOND_ORDER_FINITE_DIFF, "op1", "op7")
        self.assertListEqual([NAN, 4, -5, 7, -8, 8, NAN], trace.getAnalyticalFeature('op7'))
        
        trace.operate(Operator.SHIFT_CIRCULAR_RIGHT, "op1", "op8")
        self.assertListEqual([2, 1, -1, 1, -2, 2, -2], trace.getAnalyticalFeature('op8'))
        
        trace.operate(Operator.SHIFT_CIRCULAR_LEFT, "op1", "op9")
        self.assertListEqual([-1, 1, -2, 2, -2, 2, 1], trace.getAnalyticalFeature('op9'))
        
        trace.operate(Operator.INVERSER, "op1", "op10")
        self.assertListEqual([1, -1, 1, -0.5, 0.5, -0.5, 0.5], trace.getAnalyticalFeature('op10'))
        
        trace.operate(Operator.REVERSER, "op1", "op11")
        vt = [2, -2, 2, -2, 1, -1, 1]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op11'))
        
        trace.operate(Operator.DEBIASER, "op1", "op12")
        mean = np.mean([1, -1, 1, -2, 2, -2, 2])
        vt = [1-mean, -1-mean, 1-mean, -2-mean, 2-mean, -2-mean, 2-mean]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op12'))
        
        trace.operate(Operator.NORMALIZER, "op1", "op13")
        mean = np.mean([1, -1, 1, -2, 2, -2, 2])
        sigma = math.sqrt(np.var([1, -1, 1, -2, 2, -2, 2]))
        vt = [(1-mean)/sigma, (-1-mean)/sigma, (1-mean)/sigma, (-2-mean)/sigma, (2-mean)/sigma, (-2-mean)/sigma, (2-mean)/sigma]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op13'))
        
        trace.operate(Operator.DIODE, "op1", "op14")
        self.assertListEqual([1, 0, 1, 0, 2, 0, 2], trace.getAnalyticalFeature('op14'))
        
        trace.operate(Operator.SIGN, "op1", "op15")
        self.assertListEqual([1, -1, 1, -1, 1, -1, 1], trace.getAnalyticalFeature('op15'))
        
        trace.operate(Operator.EXP, "op1", "op16")
        vt = [math.exp(1), math.exp(-1), math.exp(1), math.exp(-2), math.exp(2), math.exp(-2), math.exp(2)]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op16'))
        
        trace.operate(Operator.COS, "op1", "op17")
        vt = [math.cos(1), math.cos(-1), math.cos(1), math.cos(-2), math.cos(2), math.cos(-2), math.cos(2)]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op17'))
        
        trace.operate(Operator.SIN, "op1", "op18")
        vt = [math.sin(1), math.sin(-1), math.sin(1), math.sin(-2), math.sin(2), math.sin(-2), math.sin(2)]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op18'))
        
        trace.operate(Operator.TAN, "op1", "op19")
        vt = [math.tan(1), math.tan(-1), math.tan(1), math.tan(-2), math.tan(2), math.tan(-2), math.tan(2)]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op19'))
        
        trace.operate(Operator.LOG, "op1", "op20")
        vt = [math.log(1), 0, math.log(1), 0, math.log(2), 0, math.log(2)]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op20'))

        
    def test_binary_void_operator(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        trace = Track([], 1)
        trace.addObs(Obs(ENUCoords(0, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(1, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(2, 0, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(3, 1, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(4, 1, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(5, 1, 0), ObsTime()))
        trace.addObs(Obs(ENUCoords(6, 1, 0), ObsTime()))
        
        trace["a"] = [1, -1, 1, -2, 2, -3, 2]
        trace["b"] = [3,  2, 1, -4, 5, -2, 3]
        self.assertListEqual([1, -1, 1, -2, 2, -3, 2], trace.getAnalyticalFeature('a'))
        self.assertListEqual([3, 2, 1, -4, 5, -2, 3], trace.getAnalyticalFeature('b'))
        A = trace.getAnalyticalFeature('a')
        B = trace.getAnalyticalFeature('b')
        
        trace.operate(Operator.MULTIPLIER, "a", "b", "op1")
        vt = [3, -2, 1, 8, 10, 6, 6]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op1'))
        
        trace.operate(Operator.POWER, "a", "b", "op2")
        vt = [1, 1, 1, 0.0625, 32, 0.1111111111111111, 8]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op2'))
        
        trace.operate(Operator.MODULO, "a", "b", "op3")
        vt = [1, 1, 0, -2, 2, -1, 2]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op3'))
        
        trace.operate(Operator.ABOVE, "a", "b", "op4")
        vt = [0, 0, 0, 1, 0, 0, 0]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op4'))
        
        trace.operate(Operator.BELOW, "a", "b", "op5")
        vt = [1, 1, 0, 0, 1, 1, 1]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op5'))
        
        trace.operate(Operator.DERIVATOR, "a", "b", "op6")
        vt = [0, 2, -2, 0.6, 4/9, -5/-7, 1]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op6'))
        
        trace.operate(Operator.RENORMALIZER, "a", "b", "op7")
        m1 = np.average(A)
        m2 = np.average(B)
        s1 = math.sqrt(np.var(A))
        s2 = math.sqrt(np.var(B))
        vt = [(A[0]-m1)*s2/s1+m2, (A[1]-m1)*s2/s1+m2, (A[2]-m1)*s2/s1+m2, (A[3]-m1)*s2/s1+m2, (A[4]-m1)*s2/s1+m2, (A[5]-m1)*s2/s1+m2, (A[6]-m1)*s2/s1+m2]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op7'))
        
        trace.operate(Operator.POINTWISE_EQUALER, "a", "b", "op8")
        vt = [0, 0, 1, 0, 0, 0, 0]
        self.assertListEqual(vt, trace.getAnalyticalFeature('op8'))
        
        #trace.operate(Operator.CONVOLUTION, "a", "b", "op9")
        #vt = [NAN, 1, 0, 0, 1, 1, 1]
        #self.assertListEqual(vt, trace.getAnalyticalFeature('op9'))
        
        #trace.operate(Operator.CORRELATOR, "a", "b", "op10")
        #print (trace.getAnalyticalFeature('op10')[0])
        #print (np.cov(A[0], B[0]))
        #c11 = np.cov(A[0], B[0])[0][1] / (math.sqrt(np.var(A[0])) * np.sqrt(np.var(B[0])))
        #print (c11)
        #vt = [c11, 1, 0, 0, 1, 1, 1]
        #self.assertListEqual(vt, trace.getAnalyticalFeature('op10'))
        
        
        
        
        
        
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestOperateurMethods("test_random"))
    suite.addTest(TestOperateurMethods("test_generate"))
    suite.addTest(TestOperateurMethods("test_import"))
    suite.addTest(TestOperateurMethods("test_abs_curv1"))
    suite.addTest(TestOperateurMethods("test_unary_void_operator"))
    suite.addTest(TestOperateurMethods("test_binary_void_operator"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
    