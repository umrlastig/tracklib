# -*- coding: utf-8 -*-
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.core import (Track, Obs, Coords, GPSTime)

class TestTrack(TestCase):
    '''
    '''
    
    def setUp (self):
        
        GPSTime.GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        # ---------------------------------------------------------------------
        self.trace1 = Track.Track([], 1)
        c1 = Coords.ENUCoords(1.0, 5.0, 0)
        p1 = Obs.Obs(c1, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace1.addObs(p1)
        
    def test_str(self):
        txt = '01/01/2018 10:00:00  [E=       1.000, N=       5.000, U=       0.000]'
        self.assertEqual(txt.strip(), str(self.trace1).strip())
        
        
    def test_timezone(self):
        self.assertEqual(0, self.trace1.getTimeZone())
        
        self.trace1.setTimeZone(1)
        self.assertEqual(1, self.trace1.getTimeZone())

        
if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestTrack("test_str"))
    suite.addTest(TestTrack("test_timezone"))
    runner = TextTestRunner()
    runner.run(suite)