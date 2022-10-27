# -*- coding: utf-8 -*-

import unittest

import os.path

from tracklib.core.GPSTime import GPSTime
from tracklib.io.TrackReader import TrackReader
from tracklib.core.Plot import Plot


class TestPlot(unittest.TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
    
    def testPlotAnalyticalFeature(self):
        gpxpath = os.path.join(self.resource_path, 'data/gpx/activity_5807084803.gpx')
        tracks = TrackReader.readFromGpxFiles(gpxpath)
        trace = tracks.getTrack(0)
        trace.estimate_speed()
        plot = Plot(trace)
        plot.plotAnalyticalFeature('speed', 'BOXPLOT')
        
        

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestPlot("testPlotAnalyticalFeature"))
    runner = unittest.TextTestRunner()
    runner.run(suite)