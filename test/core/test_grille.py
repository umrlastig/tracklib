# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner
import matplotlib.pyplot as plt

from tracklib.core import (Track, Obs, Coords, GPSTime, Grid)
from tracklib.algo import (Analytics)
from tracklib.algo import (Summarising) 
from tracklib.core.TrackCollection import TrackCollection


class TestGrille(TestCase):
    
    def setUp (self):
        
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
        
        c4 = Coords.ENUCoords(360, 210, 0)
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
        
        #  Construction de la grille
        #self.grille = Grid.Grid(Xmin, Ymin, Xmax, Ymax, PixelSize)
        marge = 0.05
        self.grille = Grid.Grid(self.collection, (60,60), marge)
        self.grille.plot()
        plt.show()
        
        self.assertEqual(self.grille.xmin, 10.0 - marge*(360-10))
        self.assertEqual(self.grille.xmax, 360.0 + marge*(360-10))
        self.assertEqual(self.grille.ymin, 10.0 - marge*(210-10))
        self.assertEqual(self.grille.ymax, 210.0 + marge*(210-10))
        
        self.assertEqual(self.grille.ncol, int (((360-10) + marge*(360-10)) / 60))
        self.assertEqual(self.grille.nrow, int (((210-10) + marge*(210-10)) / 60))
    
        self.assertEqual(self.grille.XPixelSize, ((360-10) + 2*marge*(360-10)) / self.grille.ncol)
        self.assertEqual(self.grille.YPixelSize, ((210-10) + 2*marge*(210-10)) / self.grille.nrow)
    
    
    def test_summarize_af(self):
        
        self.collection.addAnalyticalFeature(Analytics.speed)
        
        af_algos = ['speed'] #, utils.stop_point]
        cell_operators = [Summarising.co_avg] #, utils.sum]
        
        raster = Summarising.summarize(self.grille, af_algos, cell_operators)
        raster.plot(Analytics.speed, Summarising.co_avg)
        
        rasterBand = raster.getRasterBand(Analytics.speed, Summarising.co_avg)
        
        speedTrace1 = self.collection.getTrack(0).getAnalyticalFeature('speed')
        speedTrace2 = self.collection.getTrack(1).getAnalyticalFeature('speed')
        
        self.assertEqual(rasterBand[0][0], 0)
        self.assertEqual(rasterBand[1][0], speedTrace1[1])
        self.assertEqual(rasterBand[2][0], (speedTrace1[0] + speedTrace2[0]) / 2)
        
        self.assertEqual(rasterBand[0][1], 0)
        self.assertEqual(rasterBand[1][1], 0)
        self.assertEqual(rasterBand[2][1], 0)
        self.assertEqual(rasterBand[0][2], 0)
        self.assertEqual(rasterBand[1][2], 0)
        self.assertEqual(rasterBand[2][2], 0)
        self.assertEqual(rasterBand[0][3], 0)
        self.assertEqual(rasterBand[1][3], 0)
        self.assertEqual(rasterBand[2][3], 0)
        
        self.assertEqual(rasterBand[0][4], 0)
        self.assertEqual(rasterBand[1][4], (speedTrace1[2] + speedTrace2[1]) / 2)
        self.assertEqual(rasterBand[2][4], 0)
        
        self.assertEqual(rasterBand[0][5], speedTrace1[3])
        self.assertEqual(rasterBand[1][5], 0)
        self.assertEqual(rasterBand[2][5], speedTrace2[2])
        
    
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


if __name__ == '__main__':
    suite = TestSuite()
    #suite.addTest(TestGrille("test_summarize_aa"))
    suite.addTest(TestGrille("test_summarize_af"))
    #suite.addTest(TestGrille("test_sum_trace"))
    #suite.addTest(TestGrille("test_mixte_aa_af_uid"))
    runner = TextTestRunner()
    runner.run(suite)
    
    