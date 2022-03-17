# -*- coding: utf-8 -*-

import os.path
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.io.GpxReader import GpxReader
from tracklib.core.GPSTime import GPSTime
from tracklib.core.Track import Track


class TestGpxReader(TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")


    def test_read_gpx(self):
        
        path = os.path.join(self.resource_path, 'data/vincennes.gpx')
        GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        tracks = GpxReader.readFromGpx(path, srid='ENU')
        trace = tracks[0]
        self.assertEqual(5370, trace.size())
        self.assertIsInstance(trace, Track)



if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestGpxReader("test_read_gpx"))
    runner = TextTestRunner()
    runner.run(suite)


