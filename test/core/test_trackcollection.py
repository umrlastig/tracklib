from unittest import TestCase, TestSuite, TextTestRunner
import os.path

from tracklib import (ENUCoords, ObsTime, Obs, 
                      Track, TrackCollection,
                      TrackReader,
                      Bbox,
                      heading)


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
        
        collection.summary()
        
        
    def test_collection_filter_bbox(self):
        path = os.path.join(self.resource_path, 'data/gpx/geo')
        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        tracks = TrackReader.readFromGpx(path, srid='GEO', type='trk')
        self.assertIsInstance(tracks, TrackCollection)
        self.assertEqual(2, tracks.size())
        
        tracks.plot()
        
        bbox = tracks.bbox()
        self.assertTrue(abs(bbox.getLowerLeft().getX() - 6.274) < 0.001)
        self.assertTrue(abs(bbox.getUpperRight().getX() - 6.996) < 0.001)
        self.assertTrue(abs(bbox.getLowerLeft().getY() - 44.684) < 0.001)
        self.assertTrue(abs(bbox.getUpperRight().getY() - 44.844) < 0.001)
        
        Xmin = 6.97
        Ymin = 44.68
        Xmax = 7.0
        Ymax = 44.7
        ll = ENUCoords(Xmin, Ymin)
        ur = ENUCoords(Xmax, Ymax)
        bbox = Bbox(ll, ur)
        
        tracks.filterOnBBox(bbox)
        self.assertIsInstance(tracks, TrackCollection)
        self.assertEqual(1, tracks.size())


    def test_collection_operation(self):
        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        path = os.path.join(self.resource_path, 'data/gpx/geo')
        tracks1 = TrackReader.readFromGpx(path, srid='GEO', type='trk')
        path = os.path.join(self.resource_path, 'data/gpx/activity_5807084803.gpx')
        tracks2 = TrackReader.readFromGpx(path)
        
        self.assertIsInstance(tracks1, TrackCollection)
        self.assertEqual(2, tracks1.size())
        self.assertIsInstance(tracks2, TrackCollection)
        self.assertEqual(1, tracks2.size())
        
        # Addition
        T1 = tracks1 + tracks2
        self.assertIsInstance(T1, TrackCollection)
        self.assertEqual(3, T1.size())
        
        # >
        T2 = tracks1 > 100
        self.assertEqual(T2[0].size(), tracks1[0].size()-100)
        self.assertEqual(T2[1].size(), tracks1[1].size()-100)
        T2 = tracks2 > 100
        self.assertEqual(T2[0].size(), tracks2[0].size()-100)
        
        
    def test_collection_segmentation(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        trace1 = Track([], 1)
        trace1.addObs(Obs(ENUCoords(0, 0, 0), ObsTime()))
        trace1.addObs(Obs(ENUCoords(1, 0, 0), ObsTime()))
        trace1.addObs(Obs(ENUCoords(2, 0, 0), ObsTime()))
        trace1.addObs(Obs(ENUCoords(2, 1, 0), ObsTime()))
        trace1.addObs(Obs(ENUCoords(3, 1, 0), ObsTime()))
        trace1.addObs(Obs(ENUCoords(4, 1, 0), ObsTime()))
        trace1.addObs(Obs(ENUCoords(5, 1, 0), ObsTime()))
        
        trace1.addAnalyticalFeature(heading)
        trace1.createAnalyticalFeature('Temp', [39,30,37,35,45,40,30])
        
        trace2 = trace1.copy()
        
        TRACES = TrackCollection([trace1, trace2])
        
        TRACES.segmentation("heading", "decoup3", 0)
        for trace in TRACES:
            T = trace.getAnalyticalFeature('decoup3')
            self.assertEqual(len(T), 7)
            self.assertListEqual(T, [1,1,1,0,1,1,1])
        
        
        collection = TRACES.split_segmentation("decoup3")
        self.assertEqual(collection.size(), 14)
        
        
if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestTrackCollection("test_collection1"))
    suite.addTest(TestTrackCollection("test_collection_filter_bbox"))
    suite.addTest(TestTrackCollection("test_collection_operation"))
    suite.addTest(TestTrackCollection("test_collection_segmentation"))
    runner = TextTestRunner()
    runner.run(suite)