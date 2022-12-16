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
        
        # ---------------------------------------------------------------------
        self.trace2 = Track.Track([], 1)
        c1 = Coords.ENUCoords(1.0, 5.0, 0)
        p1 = Obs.Obs(c1, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace2.addObs(p1)
        
        c2 = Coords.ENUCoords(2.0, 5.0, 0)
        p2 = Obs.Obs(c2, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:05"))
        self.trace2.addObs(p2)
        
        c3 = Coords.ENUCoords(3.0, 5.0, 0)
        p3 = Obs.Obs(c3, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:10"))
        self.trace2.addObs(p3)
        
        c4 = Coords.ENUCoords(5.0, 5.0, 0)
        p4 = Obs.Obs(c4, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:20"))
        self.trace2.addObs(p4)
        
        
        
    def test_str(self):
        obs = self.trace1.getFirstObs()
        txt = str(self.trace1)
        self.assertEqual(txt[0:19], str(obs.timestamp).strip()[0:19])
        pos = txt[:len(txt)-2].split('[')[1].split(',')
        self.assertEqual(float(pos[0].split('=')[1].strip()), obs.position.getX())
        self.assertEqual(float(pos[1].split('=')[1].strip()), obs.position.getY())
        self.assertEqual(float(pos[2].split('=')[1].strip()), obs.position.getZ())
        
        
    def test_timezone(self):
        self.assertEqual(0, self.trace1.getTimeZone())
        
        self.trace1.setTimeZone(1)
        self.assertEqual(1, self.trace1.getTimeZone())
        
        self.trace1.convertToTimeZone(2)
        self.assertEqual(2, self.trace1.getTimeZone())
        #self.assertEqual(self.trace1.getFirstObs().timestamp, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.assertEqual("01/01/2018 11:00:00", str(self.trace1.getFirstObs().timestamp).strip()[0:19])
        
        
    def test_interval(self):
        f = self.trace2.interval()
        self.assertEqual(f, 5.00)

        f = self.trace2.interval(mode='spatial')
        self.assertEqual(f, 1.0)
        

if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestTrack("test_str"))
    suite.addTest(TestTrack("test_timezone"))
    suite.addTest(TestTrack("test_interval"))
    runner = TextTestRunner()
    runner.run(suite)