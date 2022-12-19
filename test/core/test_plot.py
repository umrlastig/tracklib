# -*- coding: utf-8 -*-

import unittest

import matplotlib.pyplot as plt
import os.path

from tracklib.core.ObsTime import GPSTime
from tracklib.io.TrackReader import TrackReader
from tracklib.core.Plot import Plot


class TestPlot(unittest.TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
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
        
    def testPlotSegmentation(self):
        
        from tracklib.core.Operator import Operator
        import tracklib.algo.Segmentation as segmentation
        #import tracklib.algo.Interpolation as interp
        
        self.trace.operate(Operator.DIFFERENTIATOR, "speed", "dv")
        self.trace.operate(Operator.RECTIFIER, "dv", "absdv")

        #  Segmentation
        segmentation.segmentation(self.trace, ["absdv"], "speed_decoup", [1.5])
        
        TAB_AFS = ['speed_decoup']
        plot = Plot(self.trace)
        plot.plotProfil('SPATIAL_SPEED_PROFIL', TAB_AFS)
        plt.show()
        
        

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestPlot("testPlotAnalyticalFeature"))
    suite.addTest(TestPlot("testPlotProfil"))
    suite.addTest(TestPlot("testPlotMarker"))
    suite.addTest(TestPlot("testPlotSegmentation"))
    runner = unittest.TextTestRunner()
    runner.run(suite)