from unittest import TestCase, TestSuite, TextTestRunner
import os.path

from tracklib.core.ObsTime import ObsTime
from tracklib.core.ObsCoords import ENUCoords
from tracklib.core.Obs import Obs
from tracklib.core.Track import Track
from tracklib.core.TrackCollection import TrackCollection


class TestTrackCollection(TestCase):
    
    __epsilon = 0.001
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
    
    
    def test_collection1(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
                
        track = Track()
        p1 = Obs(ENUCoords(0, 0), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        track.addObs(p1)
        p2 = Obs(ENUCoords(2.5, 3), ObsTime.readTimestamp('2020-01-01 10:08:00'))
        track.addObs(p2)
        p3 = Obs(ENUCoords(2.5, 5), ObsTime.readTimestamp('2020-01-01 10:17:00'))
        track.addObs(p3)
        p4 = Obs(ENUCoords(7, 5), ObsTime.readTimestamp('2020-01-01 10:21:00'))
        track.addObs(p4)
        p5 = Obs(ENUCoords(10, 10), ObsTime.readTimestamp('2020-01-01 10:25:00'))
        track.addObs(p5)
                
        TRACES = []
        TRACES.append(track)
        collection = TrackCollection(TRACES)

        self.assertLessEqual (abs(collection.length() - 16.236), self.__epsilon, 
                              "Length of a collection")
        self.assertEqual(collection.duration(), 1500)
        
        collection.createSpatialIndex()
        
        collection.plot()
        collection.spatial_index.plot()
        
        
if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestTrackCollection("test_collection1"))
    runner = TextTestRunner()
    runner.run(suite)