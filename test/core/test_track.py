# -*- coding: utf-8 -*-
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.core import (Track, Obs, Coords, GPSTime)
from tracklib.algo.Geometrics import Polygon


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
        
        # ---------------------------------------------------------------------
        self.trace3 = Track.Track([], 1)
        self.trace3.addObs(p1)
        self.trace3.addObs(p2)
        self.trace3.addObs(p3)
        self.trace3.addObs(p4)
        
        c5 = Coords.ENUCoords(7.0, 5.0, 0)
        p5 = Obs.Obs(c5, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:45"))
        self.trace3.addObs(p5)
        
        
        
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
        self.assertEqual("01/01/2018 11:00:00", 
                         str(self.trace1.getFirstObs().timestamp).strip()[0:19])
        
        
    def test_interval(self):
        f = self.trace2.interval()
        self.assertEqual(f, 5.00)

        f = self.trace2.interval(mode='spatial')
        self.assertEqual(f, 1.0)
        
        
    def test_coord(self):
        self.assertEqual(self.trace1.getX(), [1.0])
        self.assertEqual(self.trace1.getX(0), 1.0)
        
        self.assertEqual(self.trace1.getY(), [5.0])
        self.assertEqual(self.trace1.getY(0), 5.0)
        
        self.assertEqual(self.trace1.getZ(), [0.0])
        self.assertEqual(self.trace1.getZ(0), 0.0)
        
        self.assertEqual(self.trace1.getT(), [1514800800.0])
        self.assertEqual(self.trace1.getT(0), 1514800800.0)
        
        self.assertEqual(str(self.trace1.getTimestamps(0)).strip()[0:19], 
                         "01/01/2018 10:00:00")
        tab = self.trace1.getTimestamps()
        self.assertEqual(len(tab), 1)
        self.assertEqual(tab[0], 
                         GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        
        
    def test_enclosed_polygon(self):
        poly = self.trace2.getEnclosedPolygon()
        self.assertIsInstance(poly, Polygon)
        self.assertEqual(poly.X, [1.0, 2.0, 3.0, 5.0, 1.0])
        self.assertEqual(poly.Y, [5.0, 5.0, 5.0, 5.0, 5.0])
        
        
    def test_shift_to(self):
        t1 = self.trace2.copy()
        
        t1.shiftTo(0)
        self.assertEqual(t1.getObs(0).position.getX(), 0.0)
        self.assertEqual(t1.getObs(1).position.getX(), 1.0)
        self.assertEqual(t1.getObs(2).position.getX(), 2.0)
        self.assertEqual(t1.getObs(3).position.getX(), 4.0)
        
        t2 = self.trace2.copy()
        pos = Coords.ENUCoords(3.0, 4.0, 0.0)
        t2.shiftTo(1, pos)
        self.assertEqual(t2.getObs(0).position.getX(), 2.0)
        self.assertEqual(t2.getObs(0).position.getY(), 4.0)
        self.assertEqual(t2.getObs(1).position.getX(), 3.0)
        self.assertEqual(t2.getObs(1).position.getY(), 4.0)
        self.assertEqual(t2.getObs(2).position.getX(), 4.0)
        self.assertEqual(t2.getObs(2).position.getY(), 4.0)
        self.assertEqual(t2.getObs(3).position.getX(), 6.0)
        self.assertEqual(t2.getObs(3).position.getY(), 4.0)
        
        
    def test_make_odd(self):
        self.trace2.makeOdd()
        self.trace3.makeOdd()
        
        self.assertEqual(self.trace2.size(), 3)
        self.assertEqual(self.trace3.size(), 5)
        
        self.assertEqual(self.trace2.getObs(0).position.getX(), 1.0)
        self.assertEqual(self.trace2.getObs(0).position.getY(), 5.0)
        self.assertEqual(self.trace2.getObs(1).position.getX(), 2.0)
        self.assertEqual(self.trace2.getObs(1).position.getY(), 5.0)
        self.assertEqual(self.trace2.getObs(2).position.getX(), 3.0)
        self.assertEqual(self.trace2.getObs(2).position.getY(), 5.0)
        
        self.assertEqual(self.trace3.getObs(0).position.getX(), 1.0)
        self.assertEqual(self.trace3.getObs(0).position.getY(), 5.0)
        self.assertEqual(self.trace3.getObs(1).position.getX(), 2.0)
        self.assertEqual(self.trace3.getObs(1).position.getY(), 5.0)
        self.assertEqual(self.trace3.getObs(2).position.getX(), 3.0)
        self.assertEqual(self.trace3.getObs(2).position.getY(), 5.0)
        self.assertEqual(self.trace3.getObs(3).position.getX(), 5.0)
        self.assertEqual(self.trace3.getObs(3).position.getY(), 5.0)
        self.assertEqual(self.trace3.getObs(4).position.getX(), 7.0)
        self.assertEqual(self.trace3.getObs(4).position.getY(), 5.0)
        
    def test_make_even(self):
        self.trace2.makeEven()
        self.trace3.makeEven()
        
        self.assertEqual(self.trace2.size(), 4)
        self.assertEqual(self.trace3.size(), 4)
        
        self.assertEqual(self.trace2.getObs(0).position.getX(), 1.0)
        self.assertEqual(self.trace2.getObs(0).position.getY(), 5.0)
        self.assertEqual(self.trace2.getObs(1).position.getX(), 2.0)
        self.assertEqual(self.trace2.getObs(1).position.getY(), 5.0)
        self.assertEqual(self.trace2.getObs(2).position.getX(), 3.0)
        self.assertEqual(self.trace2.getObs(2).position.getY(), 5.0)
        self.assertEqual(self.trace2.getObs(3).position.getX(), 5.0)
        self.assertEqual(self.trace2.getObs(3).position.getY(), 5.0)
        
        self.assertEqual(self.trace3.getObs(0).position.getX(), 1.0)
        self.assertEqual(self.trace3.getObs(0).position.getY(), 5.0)
        self.assertEqual(self.trace3.getObs(1).position.getX(), 2.0)
        self.assertEqual(self.trace3.getObs(1).position.getY(), 5.0)
        self.assertEqual(self.trace3.getObs(2).position.getX(), 3.0)
        self.assertEqual(self.trace3.getObs(2).position.getY(), 5.0)
        self.assertEqual(self.trace3.getObs(3).position.getX(), 5.0)
        self.assertEqual(self.trace3.getObs(3).position.getY(), 5.0)

    
    def test_loop(self):
        t1 = self.trace2.copy()
        
        t1.loop(add=False)
        self.assertEqual(t1.size(), 4)
        self.assertEqual(t1.getObs(0).position.getX(), t1.getObs(3).position.getX())
        self.assertEqual(t1.getObs(0).position.getY(), t1.getObs(3).position.getY())
        self.assertEqual(t1.getObs(0).position.getZ(), t1.getObs(3).position.getZ())
        
        self.trace2.loop(add=True)
        self.assertEqual(self.trace2.size(), 5)
        self.assertEqual(self.trace2.getObs(0).position.getX(), self.trace2.getObs(4).position.getX())
        self.assertEqual(self.trace2.getObs(0).position.getY(), self.trace2.getObs(4).position.getY())
        self.assertEqual(self.trace2.getObs(0).position.getZ(), self.trace2.getObs(4).position.getZ())


    def test_afs(self):
        import tracklib.algo.Analytics as Analytics
        self.trace2.addAnalyticalFeature(Analytics.ds)
        self.trace2.addAnalyticalFeature(Analytics.heading)
        self.trace2.addAnalyticalFeature(Analytics.speed)
        
        T = self.trace2.getAnalyticalFeatures('speed')
        self.assertListEqual(T[0], [0.2, 0.2, 0.2, 0.2])
        
        T = self.trace2.getAnalyticalFeatures(['speed'])
        self.assertListEqual(T[0], [0.2, 0.2, 0.2, 0.2])
        
        T = self.trace2.getAnalyticalFeatures(['speed', 'ds'])
        self.assertListEqual(T[0], [0.2, 0.2, 0.2, 0.2])
        self.assertListEqual(T[1], [0.0, 1.0, 1.0, 2.0])



if __name__ == '__main__':
    suite = TestSuite()
    
    suite.addTest(TestTrack("test_str"))
    suite.addTest(TestTrack("test_timezone"))
    suite.addTest(TestTrack("test_interval"))
    suite.addTest(TestTrack("test_coord"))
    suite.addTest(TestTrack("test_enclosed_polygon"))
    suite.addTest(TestTrack("test_shift_to"))
    suite.addTest(TestTrack("test_make_odd"))
    suite.addTest(TestTrack("test_make_even"))
    suite.addTest(TestTrack("test_loop"))
    
    suite.addTest(TestTrack("test_afs"))
    
    runner = TextTestRunner()
    runner.run(suite)