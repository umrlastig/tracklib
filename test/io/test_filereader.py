# -*- coding: utf-8 -*-

import unittest

from tracklib.io.FileReader import FileReader
from tracklib.core.TrackCollection import TrackCollection

class TestFileReader(unittest.TestCase):

    def test_read_wkt_polygon(self):
        # =============================================================
        csvpath = '../../data/wkt/bati.wkt'
        TRACES = FileReader.readFromWKTFile(csvpath, 0)
        self.assertIsInstance(TRACES, TrackCollection)
        self.assertEqual(2312, TRACES.size())

    def test_read_wkt_linestring(self):
        # =============================================================
        csvpath = '../../data/wkt/iti.wkt'
        TRACES = FileReader.readFromWKTFile(csvpath, 0, -1, -1, "#", 1, "ENUCoords", None, True)
        # id_user=-1, id_track=-1, separator=";", h=0, srid="ENUCoords", bboxFilter=None
        self.assertIsInstance(TRACES, TrackCollection)
        self.assertEqual(3, TRACES.size())



if __name__ == '__main__':
    #unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestFileReader("test_read_wkt_polygon"))
    suite.addTest(TestFileReader("test_read_wkt_linestring"))
    runner = unittest.TextTestRunner()
    runner.run(suite)

