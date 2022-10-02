# -*- coding: utf-8 -*-

import os.path
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.core.GPSTime import GPSTime
from tracklib.core.Track import Track
from tracklib.core.TrackCollection import TrackCollection
from tracklib.io.TrackReader import TrackReader


class TestTrackReader(TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")

    def test_read_wkt_polygon(self):
        # =============================================================
        csvpath = os.path.join(self.resource_path, 'data/wkt/bati.wkt')
        TRACES = TrackReader.readFromWKTFile(csvpath, 0)
        self.assertIsInstance(TRACES, TrackCollection)
        self.assertEqual(2312, TRACES.size())


    def test_read_wkt_linestring(self):
        # =============================================================
        csvpath = os.path.join(self.resource_path, 'data/wkt/iti.wkt')
        TRACES = TrackReader.readFromWKTFile(csvpath, 0, -1, -1, "#", 1, "ENUCoords", None, True)
        # id_user=-1, id_track=-1, separator=";", h=0, srid="ENUCoords", bboxFilter=None
        self.assertIsInstance(TRACES, TrackCollection)
        self.assertEqual(3, TRACES.size())
        

    def test_read_gpx(self):
        path = os.path.join(self.resource_path, 'data/vincennes.gpx')
        GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        tracks = TrackReader.readFromGpx(path, srid='ENU')
        trace = tracks[0]
        self.assertEqual(5370, trace.size())
        self.assertIsInstance(trace, Track)



if __name__ == '__main__':
    #unittest.main()
    suite = TestSuite()
    suite.addTest(TestTrackReader("test_read_wkt_polygon"))
    suite.addTest(TestTrackReader("test_read_wkt_linestring"))
    suite.addTest(TestTrackReader("test_read_gpx"))
    runner = TextTestRunner()
    runner.run(suite)

