# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner
import matplotlib.pyplot as plt
import os.path

from tracklib.io.TrackReader import TrackReader

from tracklib.core import (Track, Obs, Coords, GPSTime, RasterBand)
from tracklib.algo import (Analytics)
from tracklib.algo import (Summarising) 
from tracklib.core.TrackCollection import TrackCollection


class TestGrille(TestCase):
    
    def setUp (self):
        
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        
        GPSTime.GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        self.TRACES = []
        
        # ---------------------------------------------------------------------
        trace1 = Track.Track([], 1)
        c1 = Coords.ENUCoords(10, 10, 0)
        p1 = Obs.Obs(c1, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        trace1.addObs(p1)
        
        c2 = Coords.ENUCoords(10, 110, 0)
        p2 = Obs.Obs(c2, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:12"))
        trace1.addObs(p2)
        
        c3 = Coords.ENUCoords(270, 110, 0)
        p3 = Obs.Obs(c3, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:40"))
        trace1.addObs(p3)
        
        c4 = Coords.ENUCoords(370, 190, 0)
        p4 = Obs.Obs(c4, GPSTime.GPSTime.readTimestamp("2018-01-01 10:01:50"))
        trace1.addObs(p4)
        
        self.TRACES.append(trace1)
        
        # ---------------------------------------------------------------------
        trace2 = Track.Track([], 2)
        c7 = Coords.ENUCoords(25, 10, 0)
        p7 = Obs.Obs(c7, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:15"))
        trace2.addObs(p7)
        
        c6 = Coords.ENUCoords(280, 90, 0)
        p6 = Obs.Obs(c6, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:45"))
        trace2.addObs(p6)
        
        c5 = Coords.ENUCoords(330, 20, 0)
        p5 = Obs.Obs(c5, GPSTime.GPSTime.readTimestamp("2018-01-01 10:01:55"))
        trace2.addObs(p5)
        
        self.TRACES.append(trace2)
        
        self.collection = TrackCollection(self.TRACES)
        
    
    def test_summarize_af(self):
        
        self.collection.addAnalyticalFeature(Analytics.speed)
        
        af_algos = ['speed'] #, utils.stop_point]
        cell_operators = [Summarising.co_avg] #, utils.sum]
        
        #  Construction du raster
        marge = 0.0
        raster = Summarising.summarize(self.collection, 
                                       af_algos, cell_operators, (60, 60), marge)
        
        grille = raster.getRasterBand('speed', Summarising.co_avg)
        grille.plot()
        plt.show()
        raster.setColor((255, 255, 255), (0, 0, 0))
        raster.plot(Analytics.speed, Summarising.co_avg, no_data_values=0)
        plt.show()
        
        # ---------------------------------------------------------------------
        # On teste la construction de la grille
        
        self.assertEqual(grille.xmin, 10.0 - marge*(370-10))
        self.assertEqual(grille.xmax, 370.0 + marge*(370-10))
        self.assertEqual(grille.ymin, 10.0 - marge*(190-10))
        self.assertEqual(grille.ymax, 190.0 + marge*(190-10))
        
        self.assertEqual(grille.ncol, int (((370-10) + marge*(370-10)) / 60))
        self.assertEqual(grille.nrow, int (((190-10) + marge*(190-10)) / 60))
    
        self.assertEqual(grille.XPixelSize, ((370-10) + 2*marge*(370-10)) / grille.ncol)
        self.assertEqual(grille.YPixelSize, ((190-10) + 2*marge*(190-10)) / grille.nrow)
        
        
        # ---------------------------------------------------------------------
        # On teste les valeurs de la grille
        
        rasterBand = raster.getRasterBand(Analytics.speed, Summarising.co_avg)
        
        speedTrace1 = self.collection.getTrack(0).getAnalyticalFeature('speed')
        speedTrace2 = self.collection.getTrack(1).getAnalyticalFeature('speed')
        
        self.assertEqual(rasterBand.grid[2][0], (speedTrace1[0] + speedTrace2[0]) / 2)
        self.assertEqual(rasterBand.grid[1][0], speedTrace1[1])
        self.assertEqual(rasterBand.grid[0][0], RasterBand.NO_DATA_VALUE)
        
        self.assertEqual(rasterBand.grid[2][1], RasterBand.NO_DATA_VALUE)
        self.assertEqual(rasterBand.grid[1][1], RasterBand.NO_DATA_VALUE)
        self.assertEqual(rasterBand.grid[0][1], RasterBand.NO_DATA_VALUE)
        
        self.assertEqual(rasterBand.grid[2][2], RasterBand.NO_DATA_VALUE)
        self.assertEqual(rasterBand.grid[1][2], RasterBand.NO_DATA_VALUE)
        self.assertEqual(rasterBand.grid[0][2], RasterBand.NO_DATA_VALUE)
        
        self.assertEqual(rasterBand.grid[2][3], RasterBand.NO_DATA_VALUE)
        self.assertEqual(rasterBand.grid[1][3], RasterBand.NO_DATA_VALUE)
        self.assertEqual(rasterBand.grid[0][3], RasterBand.NO_DATA_VALUE)
        
        self.assertEqual(rasterBand.grid[2][4], RasterBand.NO_DATA_VALUE)
        self.assertEqual(rasterBand.grid[1][4], (speedTrace1[2] + speedTrace2[1]) / 2)
        self.assertEqual(rasterBand.grid[0][4], RasterBand.NO_DATA_VALUE)
        
        self.assertEqual(rasterBand.grid[0][5], speedTrace1[3])
        self.assertEqual(rasterBand.grid[1][5], RasterBand.NO_DATA_VALUE)
        self.assertEqual(rasterBand.grid[2][5], speedTrace2[2])
    

        
    
    # def test_summarize_aa(self):

    #     # 
    #     af_algos = [Analytics.speed] #, utils.stop_point]
    #     cell_operators = [Summarising.co_avg] #, utils.sum]
    #     self.grille.addAnalyticalFunctionForSummarize(TrackCollection(self.TRACES), af_algos, cell_operators)
        
    #     self.grille.plot(Analytics.speed, Summarising.co_avg)
    #     #print ('')
        
    #     sumPlot = self.grille.buildArray(Analytics.speed, Summarising.co_avg)
        
    #     self.assertEqual(sumPlot[0][0][0], 0)
    #     self.assertEqual(sumPlot[1][0][0], 0)
    #     self.assertEqual(sumPlot[2][0][0], 8)
    #     self.assertEqual(sumPlot[3][0][0], 0)
    #     self.assertEqual(sumPlot[4][0][0], 8)
        
    #     self.assertEqual(sumPlot[0][6][0], 0)
    #     self.assertEqual(sumPlot[1][6][0], 0)
    #     self.assertEqual(sumPlot[2][6][0], 3)
    #     self.assertEqual(sumPlot[3][6][0], 0)
    #     self.assertEqual(sumPlot[4][6][0], 0)
        
    #     self.assertEqual(sumPlot[0][7][0], 1)
    #     self.assertEqual(sumPlot[1][7][0], 0)
    #     self.assertEqual(sumPlot[2][7][0], 0)
    #     self.assertEqual(sumPlot[3][7][0], 0)
    #     self.assertEqual(sumPlot[4][7][0], 0)
        


    # def test_sum_trace(self):
        
    #     af_algos = ['uid'] #, utils.stop_point]
    #     cell_operators = [Summarising.co_count] #, utils.sum]
        
    #     self.grille.addAnalyticalFunctionForSummarize(TrackCollection(self.TRACES), af_algos, cell_operators)
        
    #     self.grille.plot('uid', Summarising.co_count)
    #     #print ('')
        
    #     sumPlot = self.grille.buildArray('uid', Summarising.co_count)
        
    #     self.assertEqual(sumPlot[0][0][0], 0)
    #     self.assertEqual(sumPlot[1][0][0], 0)
    #     self.assertEqual(sumPlot[2][0][0], 2)
    #     self.assertEqual(sumPlot[3][0][0], 0)
    #     self.assertEqual(sumPlot[4][0][0], 2)
        
    #     self.assertEqual(sumPlot[0][6][0], 0)
    #     self.assertEqual(sumPlot[1][6][0], 0)
    #     self.assertEqual(sumPlot[2][6][0], 1)
    #     self.assertEqual(sumPlot[3][6][0], 0)
    #     self.assertEqual(sumPlot[4][6][0], 0)
        
    #     self.assertEqual(sumPlot[0][7][0], 1)
    #     self.assertEqual(sumPlot[1][7][0], 0)
    #     self.assertEqual(sumPlot[2][7][0], 0)
    #     self.assertEqual(sumPlot[3][7][0], 0)
    #     self.assertEqual(sumPlot[4][7][0], 0)
        
        
    # def test_mixte_aa_af_uid(self):
        
    #     collection = TrackCollection(self.TRACES)
    #     collection.addAnalyticalFeature(Analytics.speed)
        
    #     af_algos = ['uid', 'speed', Analytics.speed]
    #     cell_operators = [Summarising.co_count, Summarising.co_avg, Summarising.co_avg] 
        
    #     self.grille.addAnalyticalFunctionForSummarize(collection, af_algos, cell_operators)
        
    #     self.grille.plot('uid', Summarising.co_count)
    #     #print ('')
        
    #     sumPlot = self.grille.buildArray('uid', Summarising.co_count)
        
    #     self.assertEqual(sumPlot[0][0][0], 0)
    #     self.assertEqual(sumPlot[1][0][0], 0)
    #     self.assertEqual(sumPlot[2][0][0], 2)
    #     self.assertEqual(sumPlot[3][0][0], 0)
    #     self.assertEqual(sumPlot[4][0][0], 2)
        
    #     self.assertEqual(sumPlot[0][6][0], 0)
    #     self.assertEqual(sumPlot[1][6][0], 0)
    #     self.assertEqual(sumPlot[2][6][0], 1)
    #     self.assertEqual(sumPlot[3][6][0], 0)
    #     self.assertEqual(sumPlot[4][6][0], 0)
        
    #     self.assertEqual(sumPlot[0][7][0], 1)
    #     self.assertEqual(sumPlot[1][7][0], 0)
    #     self.assertEqual(sumPlot[2][7][0], 0)
    #     self.assertEqual(sumPlot[3][7][0], 0)
    #     self.assertEqual(sumPlot[4][7][0], 0)
    
    
    def test_quickstart(self):

        GPSTime.GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        gpxpath = os.path.join(self.resource_path, 'data/gpx/activity_5807084803.gpx')
        tracks = TrackReader.readFromGpxFiles(gpxpath)
        trace = tracks.getTrack(0)
        # Transformation GEO coordinates to ENU
        trace.toENUCoords()
        # Display
        trace.plot()
        # speed
        trace.estimate_speed()
        
        collection = TrackCollection([trace])
        
        af_algos = [Analytics.speed, Analytics.speed, Analytics.speed]
        cell_operators = [Summarising.co_avg, Summarising.co_min, Summarising.co_max]
        marge = 0.000005
        raster = Summarising.summarize(collection, af_algos, cell_operators, margin = marge)

        raster.setColor((0, 0, 0), (255, 255, 255))
        raster.plot(Analytics.speed, Summarising.co_avg, no_data_values = 0)
        raster.plot(Analytics.speed, Summarising.co_min, no_data_values = 0)
        raster.plot(Analytics.speed, Summarising.co_max, no_data_values = 0)
        plt.show()


if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestGrille("test_summarize_af"))
    suite.addTest(TestGrille("test_quickstart"))
    runner = TextTestRunner()
    runner.run(suite)
    
    