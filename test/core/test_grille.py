# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.core import (
  Track, Obs, Coords, GPSTime, Grid)
from tracklib.algo import (Analytics)
from tracklib.algo import (Summarization) 
from tracklib.core.TrackCollection import TrackCollection


class TestGrille(TestCase):
    
    def setUp (self):
        
        GPSTime.GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        self.TRACES = []
        
        trace1 = Track.Track([], 1)
        c1 = Coords.ENUCoords(10, 10, 0)
        p1 = Obs.Obs(c1, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
        trace1.addObs(p1)
        c2 = Coords.ENUCoords(10, 110, 0)
        p2 = Obs.Obs(c2, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:12"))
        trace1.addObs(p2)
        c3 = Coords.ENUCoords(310, 110, 0)
        p3 = Obs.Obs(c3, GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:40"))
        trace1.addObs(p3)
        c4 = Coords.ENUCoords(360, 210, 0)
        p4 = Obs.Obs(c4, GPSTime.GPSTime.readTimestamp("2018-01-01 10:01:50"))
        trace1.addObs(p4)
        self.TRACES.append(trace1)
        
        trace2 = Track.Track([], 2)
        trace2.addObs(p1)
        trace2.addObs(p2)
        self.TRACES.append(trace2)
        
        Xmin = 0
        Xmax = 400
        Ymin = 0
        Ymax = 250
            
        PixelSize = 50
        
        #  Construction de la grille
        self.grille = Grid.Grid(Xmin, Ymin, Xmax, Ymax, PixelSize)
    
    
    def test_summarize_af(self):
        
        collection = TrackCollection(self.TRACES)
        collection.addAnalyticalFeature(Analytics.speed)

        # 
        af_algos = ['speed'] #, utils.stop_point]
        cell_operators = [Summarization.co_avg] #, utils.sum]
        self.grille.addAnalyticalFunctionForSummarize(collection, af_algos, cell_operators)
        
        #
        self.grille.plot(Analytics.speed, Summarization.co_avg)
        #print ('')
        
        sumPlot = self.grille.buildArray(Analytics.speed, Summarization.co_avg)
        
        self.assertEqual(sumPlot[0][0][0], 0)
        self.assertEqual(sumPlot[1][0][0], 0)
        self.assertEqual(sumPlot[2][0][0], 8)
        self.assertEqual(sumPlot[3][0][0], 0)
        self.assertEqual(sumPlot[4][0][0], 8)
        
        self.assertEqual(sumPlot[0][6][0], 0)
        self.assertEqual(sumPlot[1][6][0], 0)
        self.assertEqual(sumPlot[2][6][0], 3)
        self.assertEqual(sumPlot[3][6][0], 0)
        self.assertEqual(sumPlot[4][6][0], 0)
        
        self.assertEqual(sumPlot[0][7][0], 1)
        self.assertEqual(sumPlot[1][7][0], 0)
        self.assertEqual(sumPlot[2][7][0], 0)
        self.assertEqual(sumPlot[3][7][0], 0)
        self.assertEqual(sumPlot[4][7][0], 0)
        
    
    def test_summarize_aa(self):

        # 
        af_algos = [Analytics.speed] #, utils.stop_point]
        cell_operators = [Summarization.co_avg] #, utils.sum]
        self.grille.addAnalyticalFunctionForSummarize(TrackCollection(self.TRACES), af_algos, cell_operators)
        
        self.grille.plot(Analytics.speed, Summarization.co_avg)
        #print ('')
        
        sumPlot = self.grille.buildArray(Analytics.speed, Summarization.co_avg)
        
        self.assertEqual(sumPlot[0][0][0], 0)
        self.assertEqual(sumPlot[1][0][0], 0)
        self.assertEqual(sumPlot[2][0][0], 8)
        self.assertEqual(sumPlot[3][0][0], 0)
        self.assertEqual(sumPlot[4][0][0], 8)
        
        self.assertEqual(sumPlot[0][6][0], 0)
        self.assertEqual(sumPlot[1][6][0], 0)
        self.assertEqual(sumPlot[2][6][0], 3)
        self.assertEqual(sumPlot[3][6][0], 0)
        self.assertEqual(sumPlot[4][6][0], 0)
        
        self.assertEqual(sumPlot[0][7][0], 1)
        self.assertEqual(sumPlot[1][7][0], 0)
        self.assertEqual(sumPlot[2][7][0], 0)
        self.assertEqual(sumPlot[3][7][0], 0)
        self.assertEqual(sumPlot[4][7][0], 0)
        


    def test_sum_trace(self):
        
        af_algos = ['uid'] #, utils.stop_point]
        cell_operators = [Summarization.co_count] #, utils.sum]
        
        self.grille.addAnalyticalFunctionForSummarize(TrackCollection(self.TRACES), af_algos, cell_operators)
        
        self.grille.plot('uid', Summarization.co_count)
        #print ('')
        
        sumPlot = self.grille.buildArray('uid', Summarization.co_count)
        
        self.assertEqual(sumPlot[0][0][0], 0)
        self.assertEqual(sumPlot[1][0][0], 0)
        self.assertEqual(sumPlot[2][0][0], 2)
        self.assertEqual(sumPlot[3][0][0], 0)
        self.assertEqual(sumPlot[4][0][0], 2)
        
        self.assertEqual(sumPlot[0][6][0], 0)
        self.assertEqual(sumPlot[1][6][0], 0)
        self.assertEqual(sumPlot[2][6][0], 1)
        self.assertEqual(sumPlot[3][6][0], 0)
        self.assertEqual(sumPlot[4][6][0], 0)
        
        self.assertEqual(sumPlot[0][7][0], 1)
        self.assertEqual(sumPlot[1][7][0], 0)
        self.assertEqual(sumPlot[2][7][0], 0)
        self.assertEqual(sumPlot[3][7][0], 0)
        self.assertEqual(sumPlot[4][7][0], 0)
        
        
    def test_mixte_aa_af_uid(self):
        
        collection = TrackCollection(self.TRACES)
        collection.addAnalyticalFeature(Analytics.speed)
        
        af_algos = ['uid', 'speed', Analytics.speed]
        cell_operators = [Summarization.co_count, Summarization.co_avg, Summarization.co_avg] 
        
        self.grille.addAnalyticalFunctionForSummarize(collection, af_algos, cell_operators)
        
        self.grille.plot('uid', Summarization.co_count)
        #print ('')
        
        sumPlot = self.grille.buildArray('uid', Summarization.co_count)
        
        self.assertEqual(sumPlot[0][0][0], 0)
        self.assertEqual(sumPlot[1][0][0], 0)
        self.assertEqual(sumPlot[2][0][0], 2)
        self.assertEqual(sumPlot[3][0][0], 0)
        self.assertEqual(sumPlot[4][0][0], 2)
        
        self.assertEqual(sumPlot[0][6][0], 0)
        self.assertEqual(sumPlot[1][6][0], 0)
        self.assertEqual(sumPlot[2][6][0], 1)
        self.assertEqual(sumPlot[3][6][0], 0)
        self.assertEqual(sumPlot[4][6][0], 0)
        
        self.assertEqual(sumPlot[0][7][0], 1)
        self.assertEqual(sumPlot[1][7][0], 0)
        self.assertEqual(sumPlot[2][7][0], 0)
        self.assertEqual(sumPlot[3][7][0], 0)
        self.assertEqual(sumPlot[4][7][0], 0)


if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestGrille("test_summarize_aa"))
    suite.addTest(TestGrille("test_summarize_af"))
    suite.addTest(TestGrille("test_sum_trace"))
    suite.addTest(TestGrille("test_mixte_aa_af_uid"))
    runner = TextTestRunner()
    runner.run(suite)
    
    