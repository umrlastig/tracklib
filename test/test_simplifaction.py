"""

"""
from unittest import TestCase, TestSuite, TextTestRunner
import matplotlib.pyplot as plt

from tracklib.core.Coords import ENUCoords
from tracklib.core.Obs import Obs
from tracklib.core.Track import Track
from tracklib.core.GPSTime import GPSTime
from tracklib.io.FileReader import FileReader
from tracklib.algo.Simplification import MODE_SIMPLIFY_VISVALINGAM
from tracklib.core.Operator import Operator
from tracklib.core.Kernel import GaussianKernel # UniformKernel

class TestSimplificationMethods(TestCase):
	
	def setUp(self):
		self.track = Track()
		p1 = Obs(ENUCoords(0, 0), "2020-01-01 10:00:00")
		self.track.addObs(p1)
		p2 = Obs(ENUCoords(0, 1), "2020-01-01 10:00:01")
		self.track.addObs(p2)
		p3 = Obs(ENUCoords(1, 2), "2020-01-01 10:00:02")
		self.track.addObs(p3)
	
	
	def test_douglas_peucker(self):
		self.track.simplify(5)
		self.assertTrue((1.289 - 1.28) < 0.01)
		
	
	def test_visvalingam(self):
		GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
		chemin = './data/trace1.dat'
		track = FileReader.readFromFile(chemin, 4, 2, 3, -1, separator=",")
		track.simplify(5, MODE_SIMPLIFY_VISVALINGAM)
		
		self.assertTrue((1.289 - 1.28) < 0.01)
		
		
	def test_gaussien(self):
		GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
		chemin = './data/trace1.dat'
		track = FileReader.readFromFile(chemin, 4, 2, 3, -1, separator=",")
		kernel = GaussianKernel(201)
		track.operate(Operator.FILTER, "x", kernel, "x2")
		track.operate(Operator.FILTER, "y", kernel, "y2")
		plt.plot(track.getT(), track.getAnalyticalFeature("y"), 'b-', markersize=1.5)
		plt.plot(track.getT(), track.getAnalyticalFeature("y2"), 'r-')
		plt.show()



if __name__ == '__main__':
	suite = TestSuite()
	suite.addTest(TestSimplificationMethods("test_douglas_peucker"))
	suite.addTest(TestSimplificationMethods("test_visvalingam"))
	suite.addTest(TestSimplificationMethods("test_gaussien"))
	runner = TextTestRunner()
	runner.run(suite)

