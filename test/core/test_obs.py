# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner

from tracklib import (ENUCoords, Obs, ObsTime, Track,
                      ds, heading, speed)

class TestObs(TestCase):
    '''
    '''
    __epsilon = 0.001
    
    def test_copy(self):

        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        trace1 = Track([], 1)

        c1 = ENUCoords(1.0, 5.0, 0)
        p1 = Obs(c1, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        trace1.addObs(p1)

        c2 = ENUCoords(2.0, 6.0, 0)
        p2 = Obs(c2, ObsTime.readTimestamp("2018-01-01 10:00:05"))
        trace1.addObs(p2)
        
        c3 = ENUCoords(3.0, 7.0, 0)
        p3 = Obs(c3, ObsTime.readTimestamp("2018-01-01 10:00:10"))
        trace1.addObs(p3)

        trace1.addAnalyticalFeature(ds)
        trace1.addAnalyticalFeature(heading)
        trace1.addAnalyticalFeature(speed)

        trace2 = trace1.copy()
        self.assertEqual(len(trace2.getListAnalyticalFeatures()), 3)
        self.assertEqual(len(trace2[1].features), 3)

        trace2.resample(0.5)
        self.assertEqual(len(trace2.getListAnalyticalFeatures()), 0)

        trace2.addAnalyticalFeature(speed)
        print (trace2[1].features)
        print (trace2.getObsAnalyticalFeature('speed', 1))

        # trace2.resample(0.5)

        o1 = Obs(p2.position.copy(), ObsTime())
        print (o1.features)

        o3 = p2.copy()
        print (o3.features)


if __name__ == '__main__':
    suite = TestSuite()
    
    suite.addTest(TestObs("test_copy"))
    
    runner = TextTestRunner()
    runner.run(suite)