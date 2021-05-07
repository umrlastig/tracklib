# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.core.Coords import ENUCoords
from tracklib.core.Obs import Obs
from tracklib.core.Track import Track
from tracklib.core.GPSTime import GPSTime

from tracklib.algo import (Analytics)

class TestQuery(TestCase):
    
    __epsilon = 0.001
    
    def setUp(self):
        
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        self.track = Track()
        p1 = Obs(ENUCoords(0, 0), GPSTime.readTimestamp('2020-01-01 10:00:00'))
        self.track.addObs(p1)
        p2 = Obs(ENUCoords(0, 1), GPSTime.readTimestamp('2020-01-01 10:00:01'))
        self.track.addObs(p2)
        p3 = Obs(ENUCoords(1, 1), GPSTime.readTimestamp('2020-01-01 10:00:02'))
        self.track.addObs(p3)
        p4 = Obs(ENUCoords(1, 2), GPSTime.readTimestamp('2020-01-01 10:00:03'))
        self.track.addObs(p4)
        p5 = Obs(ENUCoords(2, 2), GPSTime.readTimestamp('2020-01-01 10:00:04'))
        self.track.addObs(p5)
        p6 = Obs(ENUCoords(2, 3), GPSTime.readTimestamp('2020-01-01 10:00:06'))
        self.track.addObs(p6)
        p7 = Obs(ENUCoords(3, 3), GPSTime.readTimestamp('2020-01-01 10:00:08'))
        self.track.addObs(p7)
        p8 = Obs(ENUCoords(3, 4), GPSTime.readTimestamp('2020-01-01 10:00:10'))
        self.track.addObs(p8)
        p9 = Obs(ENUCoords(4, 4), GPSTime.readTimestamp('2020-01-01 10:00:12'))
        self.track.addObs(p9)
        
        # self.track.plotAsMarkers()
    
    def test_selectstar(self):
        
        self.track.addAnalyticalFeature(Analytics.speed)
        trace = self.track.query("SELECT *")
        self.assertEqual(9, trace.size())
        self.assertTrue(trace.hasAnalyticalFeature('speed'))
        self.assertLessEqual((0.7071 - trace.getObsAnalyticalFeatures('speed', 1)[0]), self.__epsilon, 'erreur de vitesse obs1')
        self.assertLessEqual((0.2070 - trace.getObsAnalyticalFeatures('speed', 8)[0]), self.__epsilon, 'erreur de vitesse obs8')
    
    def test_selectwhere1(self):
        
        self.track.addAnalyticalFeature(Analytics.speed)
        trace = self.track.query("SELECT * WHERE speed < 0.5")
        self.assertEqual(4, trace.size())
        self.assertTrue(trace.hasAnalyticalFeature('speed'))
        self.assertLessEqual((0.2070 - trace.getObsAnalyticalFeatures('speed', 0)[0]), self.__epsilon, 'erreur de vitesse 0')
        self.assertLessEqual((0.2070 - trace.getObsAnalyticalFeatures('speed', 1)[0]), self.__epsilon, 'erreur de vitesse 1')
        self.assertLessEqual((0.2070 - trace.getObsAnalyticalFeatures('speed', 2)[0]), self.__epsilon, 'erreur de vitesse 2')
        self.assertLessEqual((0.2070 - trace.getObsAnalyticalFeatures('speed', 3)[0]), self.__epsilon, 'erreur de vitesse 3')

    def test_selectwhere2(self):
        
        self.track.addAnalyticalFeature(Analytics.speed)
        trace = self.track.query("SELECT * WHERE speed > 0.5")
        self.assertEqual(4, trace.size())
        self.assertTrue(trace.hasAnalyticalFeature('speed'))
        self.assertLessEqual((0.7071 - trace.getObsAnalyticalFeatures('speed', 0)[0]), self.__epsilon, 'erreur de vitesse 0')
        self.assertLessEqual((0.7071 - trace.getObsAnalyticalFeatures('speed', 1)[0]), self.__epsilon, 'erreur de vitesse 1')
        self.assertLessEqual((0.7071 - trace.getObsAnalyticalFeatures('speed', 2)[0]), self.__epsilon, 'erreur de vitesse 2')
        self.assertLessEqual((0.7071 - trace.getObsAnalyticalFeatures('speed', 3)[0]), self.__epsilon, 'erreur de vitesse 3')


if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestQuery("test_selectstar"))
    suite.addTest(TestQuery("test_selectwhere1"))
    suite.addTest(TestQuery("test_selectwhere2"))
    runner = TextTestRunner()
    runner.run(suite)