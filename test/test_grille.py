# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.core import (
  Track, Obs, Coords, GPSTime, Grid)
from tracklib.algo import (Analytics)
from tracklib.algo import (Summarize) 
from tracklib.core.TrackCollection import TrackCollection


class TestGrille(TestCase):
    
    def test_summarize(self):

        GPSTime.GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        TRACES = []
        
        trace1 = Track.Track()
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
        
        TRACES.append(trace1)
        
        
        Xmin = 0
        Xmax = 400
        Ymin = 0
        Ymax = 250
            
        XSize = Xmax - Xmin
        YSize = Ymax - Ymin
        PixelSize = 50
        
        #  Construction de la grille
        grille = Grid.Grid(Xmin, Ymin, XSize, YSize, PixelSize)
        
        # 
        af_algos = [Analytics.speed] #, utils.stop_point]
        cell_operators = [Summarize.co_avg] #, utils.sum]
        grille.addAnalyticalFunctionForSummarize(TrackCollection(TRACES), af_algos, cell_operators)
        
        #grille.plot(utils.orientation, utils.co_dominant)
        grille.plot(Analytics.speed, Summarize.co_avg)


if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestGrille("test_summarize"))
    runner = TextTestRunner()
    runner.run(suite)
    
    