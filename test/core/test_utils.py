#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from tracklib.core import (ObsTime, Obs, Track)
from tracklib.core import ObsCoords as Coords
import tracklib.algo.Cinematics as Cinematics
import tracklib.core.Utils as Utils

class TestUtils(unittest.TestCase):
    
    def setUp (self):
        ObsTime.ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        self.trace1 = Track.Track([], 1)
        
        c1 = Coords.ENUCoords(1.0, 5.0, 0)
        p1 = Obs.Obs(c1, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace1.addObs(p1)
        
        c2 = Coords.ENUCoords(2.0, 5.0, 0)
        p2 = Obs.Obs(c2, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:05"))
        self.trace1.addObs(p2)
        
        c3 = Coords.ENUCoords(3.0, 6.0, 0)
        p3 = Obs.Obs(c3, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:10"))
        self.trace1.addObs(p3)
        
        Cinematics.computeAbsCurv(self.trace1)
    
    
    def testMakeDistanceMatrixModeLinear(self):
        mode = 'linear'
        m = Utils.makeDistanceMatrix(self.trace1, mode)
        
        self.assertEqual(m[0][0], 0, "matrice des distances: [0,0]")
        self.assertEqual(m[1][1], 0, "matrice des distances: [1,1]")
        self.assertEqual(m[2][2], 0, "matrice des distances: [2,2]")
        
        
        #self.assertEqual(m[0][1], 0, "matrice des distances: [0,1]")
        
        print (m)
        
        
        # makeDistanceMatrixOld


    

    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestUtils("testMakeDistanceMatrixModeLinear"))
    runner = unittest.TextTestRunner()
    runner.run(suite)



