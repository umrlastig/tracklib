# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.core import (ObsTime, Obs, Track)
from tracklib.core import ObsCoords as Coords
import tracklib.algo.Interpolation as itp



class TestInterpolation2(TestCase):
    
    __epsilon = 1
    
    def setUp(self):
        
        ObsTime.GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        # ---------------------------------------------------------------------
        
        self.trace1 = Track.Track([], 1)
        
        c1 = Coords.ENUCoords(0.0, 0.0, 0)
        p1 = Obs.Obs(c1, ObsTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace1.addObs(p1)
        
        c2 = Coords.ENUCoords(0.0, 2.0, 0)
        p2 = Obs.Obs(c2, ObsTime.GPSTime.readTimestamp("2018-01-01 10:02:00"))
        self.trace1.addObs(p2)
        
        c3 = Coords.ENUCoords(0.0, 5.0, 0)
        p3 = Obs.Obs(c3, ObsTime.GPSTime.readTimestamp("2018-01-01 10:05:00"))
        self.trace1.addObs(p3)
        
        c4 = Coords.ENUCoords(0.0, 9.0, 0)
        p4 = Obs.Obs(c4, ObsTime.GPSTime.readTimestamp("2018-01-01 10:09:00"))
        self.trace1.addObs(p4)
        
        # ---------------------------------------------------------------------
        
        self.trace2 = Track.Track([], 2)
        
        d1 = Coords.ENUCoords(0.0, 1.0, 0)
        r1 = Obs.Obs(d1, ObsTime.GPSTime.readTimestamp("2018-01-01 10:01:00"))
        self.trace2.addObs(r1)
        
        d2 = Coords.ENUCoords(0.0, 2.0, 0)
        r2 = Obs.Obs(d2, ObsTime.GPSTime.readTimestamp("2018-01-01 10:02:00"))
        self.trace2.addObs(r2)
        
        d3 = Coords.ENUCoords(0.0, 4.0, 0)
        r3 = Obs.Obs(d3, ObsTime.GPSTime.readTimestamp("2018-01-01 10:04:00"))
        self.trace2.addObs(r3)
        
        d4 = Coords.ENUCoords(0.0, 6.0, 0)
        r4 = Obs.Obs(d4, ObsTime.GPSTime.readTimestamp("2018-01-01 10:06:00"))
        self.trace2.addObs(r4)
        
        d5 = Coords.ENUCoords(0.0, 7.0, 0)
        r5 = Obs.Obs(d5, ObsTime.GPSTime.readTimestamp("2018-01-01 10:07:00"))
        self.trace2.addObs(r5)
        
        
    def testSynchronize(self):
        
        
        
        itp.synchronize(self.trace1, self.trace2)
        self.assertEqual(self.trace1.size(), 5)
        self.assertEqual(self.trace2.size(), 5)
        
        #self.assertEqual(self.trace1)
        
        for i in range(len(self.trace1)):
            print (self.trace1.getObs(i).position, self.trace2.getObs(i).position)
            
            

if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestInterpolation2("testSynchronize"))
    runner = TextTestRunner()
    runner.run(suite)