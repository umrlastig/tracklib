# -*- coding: utf-8 -*-

import os.path
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.core.GPSTime import GPSTime
from tracklib.core.Track import Track
from tracklib.core.TrackCollection import TrackCollection
from tracklib.io.TrackReader import TrackReader


class TestTrackReader(TestCase):
    
    __epsilon = 1
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")

    def test_read_wkt_polygon(self):
        csvpath = os.path.join(self.resource_path, 'data/wkt/bati.wkt')
        TRACES = TrackReader.readFromWKTFile(csvpath, 0)
        self.assertIsInstance(TRACES, TrackCollection)
        self.assertEqual(2312, TRACES.size())
        
        bbox = [655791, 6868715, 656055, 6868856]
        TRACES = TrackReader.readFromWKTFile(csvpath, 0, bboxFilter=bbox)
        self.assertIsInstance(TRACES, TrackCollection)
        self.assertEqual(109, TRACES.size())

    def test_read_wkt_linestring(self):
        csvpath = os.path.join(self.resource_path, 'data/wkt/iti.wkt')
        TRACES = TrackReader.readFromWKTFile(csvpath, 0, -1, -1, "#", 1, "ENUCoords", None, True)
        # id_user=-1, id_track=-1, separator=";", h=0, srid="ENUCoords", bboxFilter=None
        self.assertIsInstance(TRACES, TrackCollection)
        self.assertEqual(3, TRACES.size())
        

    def test_read_gpx_enu_trk(self):
        path = os.path.join(self.resource_path, 'data/gpx/vincennes.gpx')
        GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        tracks = TrackReader.readFromGpx(path, srid='ENU', type="trk")
        trace = tracks[0]
        self.assertEqual(5370, trace.size())
        self.assertIsInstance(trace, Track)
        self.assertLessEqual(abs(trace.length() - 10139), self.__epsilon, "Longueur gpx enu")
        
    def test_read_default_gpx(self):
        path = os.path.join(self.resource_path, 'data/gpx/activity_5807084803.gpx')
        GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        tracks = TrackReader.readFromGpx(path)
        trace = tracks[0]
        self.assertEqual(190, trace.size())
        self.assertIsInstance(trace, Track)
        self.assertLessEqual(abs(trace.length() - 2412), self.__epsilon, "Longueur gpx geo")
        
    def test_read_gpx_geo_trk(self):
        path = os.path.join(self.resource_path, 'data/gpx/activity_5807084803.gpx')
        GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        tracks = TrackReader.readFromGpx(path, srid='GEO', type="trk")
        trace = tracks[0]
        self.assertEqual(190, trace.size())
        self.assertIsInstance(trace, Track)
        self.assertLessEqual(abs(trace.length() - 2412), self.__epsilon, "Longueur gpx geo")

    def test_read_gpx_geo_rte(self):
        path = os.path.join(self.resource_path, 'data/gpx/903313.gpx')
        GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        tracks = TrackReader.readFromGpx(path, srid='GEO', type='rte')
        trace = tracks[0]
        self.assertEqual(1275, trace.size())
        self.assertIsInstance(trace, Track)
        self.assertLessEqual(abs(trace.length() - 12848), self.__epsilon, "Longueur gpx geo")
        
    def test_read_gpx_dir(self):
        path = os.path.join(self.resource_path, 'data/gpx/geo')
        GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        tracks = TrackReader.readFromGpx(path, srid='GEO', type='trk')
        self.assertEqual(2, tracks.size())
        self.assertIsInstance(tracks, TrackCollection)
        
        path = os.path.join(self.resource_path, 'data/gpx/geo/')
        GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        tracks = TrackReader.readFromGpx(path, srid='GEO', type='trk')
        self.assertEqual(2, tracks.size())
        self.assertIsInstance(tracks, TrackCollection)
        
        
    def testReadGpxWithAF(self):
        path = os.path.join(self.resource_path, 'data/test/12.gpx')
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        tracks = TrackReader.readFromGpx(path, srid='ENU', type='trk', read_all=True)
        
        self.assertEqual(1, tracks.size())
        self.assertIsInstance(tracks, TrackCollection)
    
        trace = tracks.getTrack(0)
        self.assertEqual(13, trace.size())
        
        self.assertEqual(trace.getListAnalyticalFeatures(), ['speed', 'abs_curv'])
        self.assertEqual(trace.getObsAnalyticalFeature('speed', 0), 0.25)
        v1 = trace.getObsAnalyticalFeature('speed', 1)
        self.assertTrue(abs(v1 - 0.1285) < 0.001)
        self.assertEqual(trace.getObsAnalyticalFeature('abs_curv', 0), 
                [0, 1.0, 2.0, 3.0, 5.0, 6.0, 9.0, 10.0, 14.0, 15.0, 20.0, 21.0, 27.0])
        
        
    def testReadCsvWithAFTrack(self):
        GPSTime.setReadFormat("2D/2M/4Y 2h:2m:2s")
        chemin = os.path.join(self.resource_path, 'data/test/ecrins_interpol4.csv')
        track = TrackReader.readFromCsv(chemin, 0, 1, 2, 3, separator=";",read_all=True)
        
        self.assertIsInstance(track, Track)
        self.assertEqual(1593, track.size())
        self.assertEqual(track.getListAnalyticalFeatures(), 
                ['anglegeom', 'angledeg', 'sommet', 'sommet2', 'virage', 'serie'])
        
    
    def testReadCsvDir(self):
        GPSTime.setReadFormat("2D/2M/4Y 2h:2m:2s")
        chemin = os.path.join(self.resource_path, 'data/test/csv')
        collection = TrackReader.readFromCsv(chemin, 1, 2, -1, -1, separator=",")
        
        self.assertIsInstance(collection, TrackCollection)
        self.assertEqual(collection.size(), 2)


if __name__ == '__main__':
    #unittest.main()
    suite = TestSuite()
    
    # CSV
    suite.addTest(TestTrackReader("testReadCsvWithAFTrack"))
    suite.addTest(TestTrackReader("testReadCsvDir"))
    
    # WKT
    suite.addTest(TestTrackReader("test_read_wkt_polygon"))
    suite.addTest(TestTrackReader("test_read_wkt_linestring"))
    
    # GPX
    suite.addTest(TestTrackReader("test_read_default_gpx"))
    suite.addTest(TestTrackReader("test_read_gpx_enu_trk"))
    suite.addTest(TestTrackReader("test_read_gpx_geo_trk"))
    suite.addTest(TestTrackReader("test_read_gpx_geo_rte"))
    suite.addTest(TestTrackReader("test_read_gpx_dir"))
    suite.addTest(TestTrackReader("testReadGpxWithAF"))
    
    runner = TextTestRunner()
    runner.run(suite)

