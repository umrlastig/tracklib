#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import unittest

import tracklib as tkl



class TestAlgoStochastics(unittest.TestCase):
    
    def setUp (self):
        pass
        
		
    def testNoise(self):
        #N = 5
        
        tkl.seed(122)
        sentier = tkl.generate(kernel=tkl.SincKernel(7))
        sentier["y"] = lambda track, i : i*2
        tkl.computeAbsCurv(sentier)
        sentier["z"] = lambda track, i : track["abs_curv", i]*math.atan(10*math.pi/180)
        #sentier = sentier[80:]
        sentier.plot('r-')

        #expkernel = tkl.ExponentialKernel(5)
        #tracks = tkl.TrackCollection([sentier]*3)
        #tracks.noise(3, expkernel)
        #print ('nb traces = ', tracks.size())
        
        s = [1]
        k = [tkl.DiracKernel()]
        d = tkl.DISTRIBUTION_UNIFORM
        m = 'linear'
        n = tkl.noise(sentier, sigma=s, kernel=k, distribution=d, mode=m, 
              force=False, cycle=False, control=[10, 12], n=3)
        n.plot('b-')
        self.assertIsInstance(n, tkl.TrackCollection)
        
        
    		
		
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoStochastics("testNoise"))
    runner = unittest.TextTestRunner()
    runner.run(suite)

