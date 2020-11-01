# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.core import (
  Track, Obs, Coords, GPSTime, Grid)
from tracklib.algo import (AlgoAF)
from tracklib.util import (CellOperator) 

class TestGrille(TestCase):
	
	def test_summarize(self):

		GPSTime.GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
		TRACES = []
		
		trace1 = Track.Track()
		p1 = Obs.Obs(Coords.ENUCoords(10, 10, 0), GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:00"))
		trace1.addObs(p1)
		p2 = Obs.Obs(Coords.ENUCoords(10, 110, 0), GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:12"))
		trace1.addObs(p2)
		p3 = Obs.Obs(Coords.ENUCoords(310, 110, 0), GPSTime.GPSTime.readTimestamp("2018-01-01 10:00:40"))
		trace1.addObs(p3)
		p4 = Obs.Obs(Coords.ENUCoords(360, 210, 0), GPSTime.GPSTime.readTimestamp("2018-01-01 10:01:50"))
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
		af_algos = [AlgoAF.speed] #, utils.stop_point]
		cell_operators = [CellOperator.co_avg] #, utils.sum]
		grille.addAnalyticalFunctionForSummarize(TRACES, af_algos, cell_operators)
		
		#grille.plot(utils.orientation, utils.co_dominant)
		grille.plot(AlgoAF.speed, CellOperator.co_avg)


if __name__ == '__main__':
	suite = TestSuite()
	suite.addTest(TestGrille("test_summarize"))
	runner = TextTestRunner()
	runner.run(suite)
	
	