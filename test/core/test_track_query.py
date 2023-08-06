# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner
import math
import numpy as np

from tracklib import (ENUCoords, ObsTime, Obs, Track,
                      speed, heading, orientation)


class TestTrackQuery(TestCase):
    
    __epsilon = 0.001
    
    def setUp(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        self.track = Track()
        p1 = Obs(ENUCoords(0, 0), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        self.track.addObs(p1)
        p2 = Obs(ENUCoords(0, 1), ObsTime.readTimestamp('2020-01-01 10:00:01'))
        self.track.addObs(p2)
        p3 = Obs(ENUCoords(1, 1), ObsTime.readTimestamp('2020-01-01 10:00:02'))
        self.track.addObs(p3)
        p4 = Obs(ENUCoords(1, 2), ObsTime.readTimestamp('2020-01-01 10:00:03'))
        self.track.addObs(p4)
        p5 = Obs(ENUCoords(2, 2), ObsTime.readTimestamp('2020-01-01 10:00:04'))
        self.track.addObs(p5)
        p6 = Obs(ENUCoords(2, 3), ObsTime.readTimestamp('2020-01-01 10:00:06'))
        self.track.addObs(p6)
        p7 = Obs(ENUCoords(3, 3), ObsTime.readTimestamp('2020-01-01 10:00:08'))
        self.track.addObs(p7)
        p8 = Obs(ENUCoords(3, 4), ObsTime.readTimestamp('2020-01-01 10:00:10'))
        self.track.addObs(p8)
        p9 = Obs(ENUCoords(4, 4), ObsTime.readTimestamp('2020-01-01 10:00:12'))
        self.track.addObs(p9)
        
        # self.track.plotAsMarkers()
    
    def test_selectstar(self):
        
        self.track.addAnalyticalFeature(speed)
        trace = self.track.query("SELECT *")
        self.assertEqual(9, trace.size())
        self.assertTrue(trace.hasAnalyticalFeature('speed'))
        self.assertLessEqual((0.7071 - trace.getObsAnalyticalFeatures('speed', 1)[0]), self.__epsilon, 'erreur de vitesse obs1')
        self.assertLessEqual((0.2070 - trace.getObsAnalyticalFeatures('speed', 8)[0]), self.__epsilon, 'erreur de vitesse obs8')
    
    def test_selectwhere1(self):
        
        self.track.addAnalyticalFeature(speed)
        trace = self.track.query("SELECT * WHERE speed < 0.5")
        self.assertEqual(4, trace.size())
        self.assertTrue(trace.hasAnalyticalFeature('speed'))
        self.assertLessEqual((0.2070 - trace.getObsAnalyticalFeatures('speed', 0)[0]), self.__epsilon, 'erreur de vitesse 0')
        self.assertLessEqual((0.2070 - trace.getObsAnalyticalFeatures('speed', 1)[0]), self.__epsilon, 'erreur de vitesse 1')
        self.assertLessEqual((0.2070 - trace.getObsAnalyticalFeatures('speed', 2)[0]), self.__epsilon, 'erreur de vitesse 2')
        self.assertLessEqual((0.2070 - trace.getObsAnalyticalFeatures('speed', 3)[0]), self.__epsilon, 'erreur de vitesse 3')
        
        self.track.addAnalyticalFeature(speed)
        trace = self.track.query("SELECT * WHERE speed <= 0.5")
        self.assertEqual(5, trace.size())

    def test_selectwhere2(self):
        
        self.track.addAnalyticalFeature(speed)
        trace = self.track.query("SELECT * WHERE speed > 0.5")
        self.assertEqual(4, trace.size())
        self.assertTrue(trace.hasAnalyticalFeature('speed'))
        self.assertLessEqual((0.7071 - trace.getObsAnalyticalFeatures('speed', 0)[0]), self.__epsilon, 'erreur de vitesse 0')
        self.assertLessEqual((0.7071 - trace.getObsAnalyticalFeatures('speed', 1)[0]), self.__epsilon, 'erreur de vitesse 1')
        self.assertLessEqual((0.7071 - trace.getObsAnalyticalFeatures('speed', 2)[0]), self.__epsilon, 'erreur de vitesse 2')
        self.assertLessEqual((0.7071 - trace.getObsAnalyticalFeatures('speed', 3)[0]), self.__epsilon, 'erreur de vitesse 3')
        
        trace = self.track.query("SELECT * WHERE speed == 0.5")
        self.assertEqual(1, trace.size())
        
        trace = self.track.query("SELECT * WHERE speed != 0.5")
        self.assertEqual(8, trace.size())
        
        
    def test_selectagg(self):
        
        self.track.addAnalyticalFeature(speed)
        speeds = self.track.getAnalyticalFeature('speed')
        
        # AVG
        avgspeed = self.track.query("SELECT AVG(speed)")
        self.assertEquals(avgspeed, np.mean(speeds))
        
        # SUM
        sumspeed = self.track.query("SELECT SUM(speed)")
        self.assertEquals(sumspeed, np.sum(speeds))
        
        # MIN
        minspeed = self.track.query("SELECT MIN(speed)")
        self.assertEquals(minspeed, np.min(speeds))
        
        # MAX
        maxspeed = self.track.query("SELECT MAX(speed)")
        self.assertEquals(maxspeed, np.max(speeds))
        
        # COUNT
        countspeed = self.track.query("SELECT COUNT(speed)")
        self.assertEquals(countspeed, len(speeds))
        
        # VAR
        varspeed = self.track.query("SELECT VAR(speed)")
        self.assertEquals(varspeed, np.var(speeds))
        
        # MEDIAN
        meanspeed = self.track.query("SELECT MEDIAN(speed)")
        self.assertEquals(meanspeed, np.median(speeds))
        
        # ARGMIN
        argminspeed = self.track.query("SELECT ARGMIN(speed)")
        self.assertEquals(argminspeed, np.argmin(speeds))
        
        # ARGMAX
        argmaxspeed = self.track.query("SELECT ARGMAX(speed)")
        self.assertEquals(argmaxspeed, np.argmax(speeds))
        
    def test_selectcolumn(self):
        self.track.addAnalyticalFeature(speed)
        self.track.addAnalyticalFeature(heading)
        self.track.addAnalyticalFeature(orientation)
        
        # 
        manymax = self.track.query("SELECT MAX(x), MAX(y), MAX(z), MAX(t)")
        self.assertEquals(manymax, [4, 4, 0, 1577872812.0])
        
        tab = self.track.query("SELECT speed, heading WHERE speed >= 0.5")
        self.assertEquals(tab[0], [1.0, 0.7071067811865476, 
                          0.7071067811865476, 0.7071067811865476, 0.5])
        self.assertEquals(tab[1], [0.0, 0.0, 
                          1.5707963267948966, 0.0, 1.5707963267948966])
    
    
        query  = " SELECT speed, heading "
        query += " WHERE speed >= 0.3 AND heading > 1.0 "
        tab = self.track.query(query)
        self.assertEquals(tab[0],[0.7071067811865476, 0.47140452079103173, 
                          0.3535533905932738, 0.5])
        self.assertEquals(tab[1], [1.5707963267948966, 1.5707963267948966, 
                          1.5707963267948966, 1.5707963267948966])
    
        query  = " SELECT AVG(speed) "
        query += " WHERE timestamp >= 2020-01-01 10:00:03 "
        query += "   AND timestamp <= 2020-01-01 10:00:08 "
        avgspeed = self.track.query(query)
        self.assertTrue(abs(avgspeed - 0.47140) < 0.0001)

        query  = " SELECT COUNT(speed) "
        query += " WHERE orientation = 1 "
        obsOrientation1 = self.track.query(query)
        self.assertEquals(obsOrientation1, 4)
        
        
    def test_query_with_parenthesis(self):
        self.track.addAnalyticalFeature(speed)
        self.track.addAnalyticalFeature(heading)
        self.track.addAnalyticalFeature(orientation)
        
        with self.assertRaises(SystemExit):
            self.track.query("SELECT * WHERE (speed > 0.5 or orientation = 1) and heading > 1")
        
        
    def test_agg_zeros(self):
        self.track.addAnalyticalFeature(heading)
        H = self.track.getAnalyticalFeature('heading')
        
        query  = " SELECT ZEROS(heading) "
        tab = self.track.query(query)
        self.assertListEqual(tab, [0, 1, 3, 5, 7])
        
        query  = " SELECT RMSE(heading) "
        val = self.track.query(query)
        vale = math.sqrt(4 * 1.57**2 / 9)
        self.assertTrue(abs(val - vale) < 0.001)
        
        query  = " SELECT STDDEV(heading) "
        val = self.track.query(query)
        self.assertTrue(abs(val - math.sqrt(np.var(H))) < 0.001)
        
        query  = " SELECT MAD(heading) "
        val = self.track.query(query)
        self.assertTrue(abs(val - np.median(H)) < 0.001)
        
        

if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestTrackQuery("test_selectstar"))
    suite.addTest(TestTrackQuery("test_selectwhere1"))
    suite.addTest(TestTrackQuery("test_selectwhere2"))
    suite.addTest(TestTrackQuery("test_selectagg"))
    suite.addTest(TestTrackQuery("test_selectcolumn"))
    suite.addTest(TestTrackQuery("test_query_with_parenthesis"))
    suite.addTest(TestTrackQuery("test_agg_zeros"))
    runner = TextTestRunner()
    runner.run(suite)


