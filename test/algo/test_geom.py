# -*- coding: utf-8 -*-

import unittest

from tracklib.core import (
  Track, Obs, Coords, GPSTime)

import tracklib.algo.Geometrics as geom

class TestAlgoGeometricsMethods(unittest.TestCase):
    
    __epsilon = 0.001
    
    def setUp (self):
        GPSTime.GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        self.trace1 = Track.Track()
        c1 = Coords.ENUCoords(200,  0, 0)
        p1 = Obs.Obs(c1, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace1.addObs(p1)
        c2 = Coords.ENUCoords(100, 100, 0)
        p2 = Obs.Obs(c2, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:12"))
        self.trace1.addObs(p2)
        c3 = Coords.ENUCoords(0, 0, 0)
        p3 = Obs.Obs(c3, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:40"))
        self.trace1.addObs(p3)
        c4 = Coords.ENUCoords(100, -100, 0)
        p4 = Obs.Obs(c4, GPSTime.GPSTime.readTimestamp("2018-01-01 10:01:50"))
        self.trace1.addObs(p4)

    
    def test1(self):
        
        #P = [obs.position for obs in self.trace1]
        #R = []
        # C = geom.__welzl(P, R)
        C = geom.minCircle(self.trace1)
        # print (C[0].getX(), C[0].getY(), C[1])
        
        self.assertLessEqual((100 - C[1]), self.__epsilon, "Rayon du cercle")
        self.assertIsInstance(C[0], Coords.ENUCoords)
        self.assertLessEqual((100 - C[0].getX()), self.__epsilon, "coord x du centre cercle")
        self.assertLessEqual((0 - C[0].getY()), self.__epsilon, "coord y du centre cercle")



if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoGeometricsMethods("test1"))
    runner = unittest.TextTestRunner()
    runner.run(suite)