# -*- coding: utf-8 -*-

import unittest

import matplotlib.pyplot as plt
import os.path

from tracklib.core.ObsTime import ObsTime
from tracklib.io.TrackReader import TrackReader
from tracklib.plot.Plot import Plot


class TestPlot(unittest.TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        gpxpath = os.path.join(self.resource_path, 'data/gpx/activity_5807084803.gpx')
        tracks = TrackReader.readFromGpx(gpxpath)
        self.trace = tracks.getTrack(0)
        self.trace.estimate_speed()
    
    def testPlotAnalyticalFeature(self):
        plot = Plot(self.trace)
        plot.plotAnalyticalFeature('speed', 'BOXPLOT')
        
    def testPlotProfil(self):
        plot = Plot(self.trace)
        plot.plotProfil('SPATIAL_SPEED_PROFIL')
        plt.show()
        plot.plotProfil('TEMPORAL_ALTI_PROFIL')
        plt.show()
        
    def testPlotMarker(self):
        self.trace.plotAsMarkers(frg="k", bkg="w", sym_frg=" ", sym_bkg="o")
        plt.show()
        
    
        
        

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestPlot("testPlotAnalyticalFeature"))
    suite.addTest(TestPlot("testPlotProfil"))
    suite.addTest(TestPlot("testPlotMarker"))
    runner = unittest.TextTestRunner()
    runner.run(suite)