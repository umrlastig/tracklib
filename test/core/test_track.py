# -*- coding: utf-8 -*-
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib import (ENUCoords, ObsTime, Obs)
from tracklib.core import (Track)
from tracklib.util import Polygon
import tracklib.algo.Cinematics as Cinematics


class TestTrack(TestCase):
    '''
    '''
    
    __epsilon = 0.001
    
    def setUp (self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        # ---------------------------------------------------------------------
        self.trace1 = Track.Track([], 1)
        c1 = ENUCoords(1.0, 5.0, 0)
        p1 = Obs(c1, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace1.addObs(p1)
        
        # ---------------------------------------------------------------------
        self.trace2 = Track.Track([], 1)
        c1 = ENUCoords(1.0, 5.0, 0)
        p1 = Obs(c1, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace2.addObs(p1)
        
        c2 = ENUCoords(2.0, 5.0, 0)
        p2 = Obs(c2, ObsTime.readTimestamp("2018-01-01 10:00:05"))
        self.trace2.addObs(p2)
        
        c3 = ENUCoords(3.0, 5.0, 0)
        p3 = Obs(c3, ObsTime.readTimestamp("2018-01-01 10:00:10"))
        self.trace2.addObs(p3)
        
        c4 = ENUCoords(5.0, 5.0, 0.4)
        p4 = Obs(c4, ObsTime.readTimestamp("2018-01-01 10:00:20"))
        self.trace2.addObs(p4)
        
        # ---------------------------------------------------------------------
        self.trace3 = Track.Track([], 1)
        self.trace3.addObs(p1)
        self.trace3.addObs(p2)
        self.trace3.addObs(p3)
        self.trace3.addObs(p4)
        
        c5 = ENUCoords(7.0, 5.0, 0)
        p5 = Obs(c5, ObsTime.readTimestamp("2018-01-01 10:00:45"))
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
        self.assertLessEqual(abs(1.009 - f), self.__epsilon)
        
        
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
                         ObsTime.readTimestamp("2018-01-01 10:00:00"))
        
        
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
        pos = ENUCoords(3.0, 4.0, 0.0)
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


    def test_af_xyztidx(self):
        Z = self.trace2.getAnalyticalFeature("z")
        self.assertListEqual(Z, [0, 0, 0, 0.4])
        
        T = self.trace2.getAnalyticalFeature("t")
        self.assertListEqual(T, [1514800800.0, 1514800805.0, 1514800810.0, 1514800820.0])
        
        TPS = self.trace2.getAnalyticalFeature("timestamp")
        self.assertEqual(str(TPS[0]).strip()[0:19], "01/01/2018 10:00:00")
        self.assertEqual(str(TPS[1]).strip()[0:19], "01/01/2018 10:00:05")
        self.assertEqual(str(TPS[2]).strip()[0:19], "01/01/2018 10:00:10")
        self.assertEqual(str(TPS[3]).strip()[0:19], "01/01/2018 10:00:20")
        
        IDX = self.trace2.getAnalyticalFeature("idx")
        self.assertListEqual(IDX, [0, 1, 2, 3])
        
        
    def test_obs_af(self):
        tps = self.trace2.getObsAnalyticalFeature('timestamp', 0)
        self.assertEqual(str(tps).strip()[0:19], "01/01/2018 10:00:00")
        tps = self.trace2.getObsAnalyticalFeature('timestamp', 1)
        self.assertEqual(str(tps).strip()[0:19], "01/01/2018 10:00:05")
        tps = self.trace2.getObsAnalyticalFeature('timestamp', 2)
        self.assertEqual(str(tps).strip()[0:19], "01/01/2018 10:00:10")
        tps = self.trace2.getObsAnalyticalFeature('timestamp', 3)
        self.assertEqual(str(tps).strip()[0:19], "01/01/2018 10:00:20")
        
        idx = self.trace2.getObsAnalyticalFeature('idx', 0)
        self.assertEqual(idx, 0)
        idx = self.trace2.getObsAnalyticalFeature('idx', 1)
        self.assertEqual(idx, 1)
        idx = self.trace2.getObsAnalyticalFeature('idx', 2)
        self.assertEqual(idx, 2)
        idx = self.trace2.getObsAnalyticalFeature('idx', 3)
        self.assertEqual(idx, 3)
        
        
    def test_set_obs_af(self):
        self.trace2.setObsAnalyticalFeature("z", 2, 1)
        self.assertEqual(self.trace2.getObsAnalyticalFeature("z", 2), 1)


    def test_sort(self):
        self.assertTrue(self.trace2.isSorted())
        c1 = ENUCoords(0.0, 5.0, 0.5)
        p1 = Obs(c1, ObsTime.readTimestamp("2018-01-01 09:59:55"))
        self.trace2.addObs(p1)
        self.assertFalse(self.trace2.isSorted())
        self.trace2.sort()
        
        self.assertEqual(self.trace2.getX(), [0.0, 1.0, 2.0, 3.0, 5.0])
        self.assertEqual(self.trace2.getY(), [5.0, 5.0, 5.0, 5.0, 5.0])
        self.assertEqual(self.trace2.getZ(), [0.5, 0.0, 0.0, 0.0, 0.4])
        
        self.assertEqual(str(self.trace2.getTimestamps(0)).strip()[0:19], 
                         "01/01/2018 09:59:55")
        self.assertEqual(str(self.trace2.getTimestamps(1)).strip()[0:19], 
                         "01/01/2018 10:00:00")
        self.assertEqual(str(self.trace2.getTimestamps(2)).strip()[0:19], 
                         "01/01/2018 10:00:05")
        self.assertEqual(str(self.trace2.getTimestamps(3)).strip()[0:19], 
                         "01/01/2018 10:00:10")
        self.assertEqual(str(self.trace2.getTimestamps(4)).strip()[0:19], 
                         "01/01/2018 10:00:20")
        
        
        self.assertTrue(self.trace2.isSorted())
        
        
    def test_remove_obs(self):
        
        self.trace2.removeObsList([])
        self.assertEqual(self.trace2.size(), 4)
        
        self.trace2.removeObsList([1,3])
        self.assertEqual(self.trace2.size(), 2)
        self.assertEqual(self.trace2.getX(), [1.0, 3.0])
        self.assertEqual(self.trace2.getY(), [5.0, 5.0])
        self.assertEqual(self.trace2.getZ(), [0.0, 0.0])
        self.assertEqual(str(self.trace2.getTimestamps(0)).strip()[0:19], 
                         "01/01/2018 10:00:00")
        self.assertEqual(str(self.trace2.getTimestamps(1)).strip()[0:19], 
                         "01/01/2018 10:00:10")
        
        self.trace2.removeObsList([ObsTime.readTimestamp("2018-01-01 10:00:00")])
        self.assertEqual(self.trace2.size(), 1)
        self.assertEqual(self.trace2.getX(), [3.0])
        self.assertEqual(self.trace2.getY(), [5.0])
        self.assertEqual(self.trace2.getZ(), [0.0])
        self.assertEqual(str(self.trace2.getTimestamps(0)).strip()[0:19], 
                         "01/01/2018 10:00:10")
        
        self.trace2.popObs(0)
        self.assertEqual(self.trace2.size(), 0)
        
        
    def test_tid(self):
        self.assertEqual (self.trace2.tid, 0)
        self.trace2.setTid(10)
        self.assertEqual (self.trace2.tid, 10)
        
        
    def test_sort_radix(self):
        self.trace2.sortRadix()
        # TODO
        
        
    def test_remove_tpsDup(self):
        self.trace2.removeTpsDup()
    
    
    def test_export(self):
        import tracklib.algo.Analytics as Analytics
        self.trace2.addAnalyticalFeature(Analytics.ds)
        self.trace2.addAnalyticalFeature(Analytics.heading)
        self.trace2.addAnalyticalFeature(Analytics.speed)
        #self.trace2.print(['speed'])
        
        self.trace2.summary()
        
        wkt = self.trace1.toWKT()
        self.assertEquals(wkt, "LINESTRING(1.0 5.0)")
        
    
    def test_create_and_init_af(self):
        
        # ajoute un nouvel AF de nom new_AF_name et lui affecte la valeur 2 à chaque époque.
        self.trace2["AF_2"] = 2
        T = self.trace2.getAnalyticalFeature('AF_2')
        self.assertCountEqual (T, [2,2,2,2])
        self.assertListEqual (T, [2,2,2,2])

        # ajoute un nouvel AF en lui passant une liste
        self.trace2["AF_LIST"] = [3]*len(self.trace2)
        T = self.trace2.getAnalyticalFeature('AF_LIST')
        self.assertCountEqual (T, [3,3,3,3])
        self.assertListEqual (T, [3,3,3,3])
        
        # ajoute un nouvel AF de nom new_AF_name et lui affecte la valeur de 0 à n-1 
        self.trace2["AF_LIST_2"] = [i for i in range(len(self.trace2))]
        T = self.trace2.getAnalyticalFeature('AF_LIST_2')
        self.assertCountEqual (T, [0,1,2,3])
        self.assertListEqual (T, [0,1,2,3])
        
        
    def test_insert_obs(self):
        
        self.trace2.getObs(0).position.setZ(0)
        self.trace2.getObs(1).position.setZ(0)
        self.trace2.getObs(2).position.setZ(0)
        self.trace2.getObs(3).position.setZ(0)
        
        self.assertEqual(4, self.trace2.size())
        self.assertLessEqual(abs(self.trace2.length() - 4.0000), self.__epsilon)
        
        A = Cinematics.computeAbsCurv(self.trace2)
        self.assertEqual(0.0, self.trace2.getObsAnalyticalFeature('abs_curv', 0))
        self.assertEqual(A[0], self.trace2.getObsAnalyticalFeature('abs_curv', 0))
        self.assertEqual(1.0, self.trace2.getObsAnalyticalFeature('abs_curv', 1))
        self.assertEqual(A[1], self.trace2.getObsAnalyticalFeature('abs_curv', 1))
        self.assertEqual(2.0, self.trace2.getObsAnalyticalFeature('abs_curv', 2))
        self.assertEqual(A[2], self.trace2.getObsAnalyticalFeature('abs_curv', 2))
        self.assertEqual(4.0, self.trace2.getObsAnalyticalFeature('abs_curv', 3))
        self.assertEqual(A[3], self.trace2.getObsAnalyticalFeature('abs_curv', 3))
        
        self.trace2.removeAnalyticalFeature('abs_curv')
        
        c4 = ENUCoords(3.0, 4.0, 0)
        p4 = Obs(c4, ObsTime.readTimestamp("2018-01-01 10:00:13"))
        self.trace2.insertObs(p4, 3)
        
        c5 = ENUCoords(5.0, 4.0, 0)
        p5 = Obs(c5, ObsTime.readTimestamp("2018-01-01 10:00:17"))
        self.trace2.insertObs(p5)
                
        self.assertEqual(6, self.trace2.size())
        self.assertLessEqual(abs(self.trace2.length() - 6.0000), self.__epsilon)
        
        #self.trace2.plotAsMarkers()
        A = Cinematics.computeAbsCurv(self.trace2)
        self.assertEqual(0.0, self.trace2.getObsAnalyticalFeature('abs_curv', 0))
        self.assertEqual(A[0], self.trace2.getObsAnalyticalFeature('abs_curv', 0))
        self.assertEqual(1.0, self.trace2.getObsAnalyticalFeature('abs_curv', 1))
        self.assertEqual(A[1], self.trace2.getObsAnalyticalFeature('abs_curv', 1))
        self.assertEqual(2.0, self.trace2.getObsAnalyticalFeature('abs_curv', 2))
        self.assertEqual(A[2], self.trace2.getObsAnalyticalFeature('abs_curv', 2))
        self.assertEqual(3.0, self.trace2.getObsAnalyticalFeature('abs_curv', 3))
        self.assertEqual(A[3], self.trace2.getObsAnalyticalFeature('abs_curv', 3))
        self.assertEqual(5.0, self.trace2.getObsAnalyticalFeature('abs_curv', 4))
        self.assertEqual(A[4], self.trace2.getObsAnalyticalFeature('abs_curv', 4))
        self.assertEqual(6.0, self.trace2.getObsAnalyticalFeature('abs_curv', 5))
        self.assertEqual(A[5], self.trace2.getObsAnalyticalFeature('abs_curv', 5))
        
        
    def test_insert_obs2(self):
        
        ObsTime.setReadFormat("2D/2M/4Y 2h:2m:2s")
        
        track = Track.Track([], 1)
        p = Obs(ENUCoords(904145.257, 6435910.726, 1228.000), ObsTime.readTimestamp("01/01/1970 00:00:00"))
        track.addObs(p)
        p = Obs(ENUCoords(904135.886, 6435924.287, 1230.000), ObsTime.readTimestamp("01/01/1970 00:00:00"))
        track.addObs(p)
        p = Obs(ENUCoords(904131.695, 6435940.496, 1232.000), ObsTime.readTimestamp("01/01/1970 00:00:00"))
        track.addObs(p)
        p = Obs(ENUCoords(904124.752, 6435949.758, 1234.000), ObsTime.readTimestamp("01/01/1970 00:00:00"))
        track.addObs(p)
        p = Obs(ENUCoords(904121.474, 6435953.784, 1235.000), ObsTime.readTimestamp("01/01/1970 00:00:00"))
        track.addObs(p)
        p = Obs(ENUCoords(904112.641, 6435964.640, 1237.000), ObsTime.readTimestamp("01/01/1970 00:00:00"))
        track.addObs(p)
        p = Obs(ENUCoords(904112.033, 6435956.730, 1239.000), ObsTime.readTimestamp("01/01/1970 00:00:00"))
        track.addObs(p)
        p = Obs(ENUCoords(904110.988, 6435953.029, 1240.000), ObsTime.readTimestamp("01/01/1970 00:00:00"))
        track.addObs(p)
        p = Obs(ENUCoords(904108.868, 6435945.536, 1242.000), ObsTime.readTimestamp("01/01/1970 00:00:00"))
        track.addObs(p)
        self.assertLessEqual(abs(track.length() - 84.83257), self.__epsilon)
        
        p = Obs(ENUCoords(904113.755, 6435963.271, 1236), ObsTime.readTimestamp("01/01/1970 00:00:00"))
        track.insertObs(p, 5)
        self.assertLessEqual(abs(track.length() - 84.994800), self.__epsilon)
        
        

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
    suite.addTest(TestTrack("test_af_xyztidx"))
    suite.addTest(TestTrack("test_obs_af"))
    suite.addTest(TestTrack("test_set_obs_af"))
    suite.addTest(TestTrack("test_create_and_init_af"))

    suite.addTest(TestTrack("test_sort"))
    suite.addTest(TestTrack("test_remove_obs"))
    suite.addTest(TestTrack("test_tid"))
    suite.addTest(TestTrack("test_sort_radix"))
    
    suite.addTest(TestTrack("test_remove_tpsDup"))
    suite.addTest(TestTrack("test_export"))
    
    suite.addTest(TestTrack("test_insert_obs"))
    suite.addTest(TestTrack("test_insert_obs2"))
    
    runner = TextTestRunner()
    runner.run(suite)
