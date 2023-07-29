"""

"""
from unittest import TestCase, TestSuite, TextTestRunner
import matplotlib.pyplot as plt
import os.path

from tracklib import (ObsTime, GaussianKernel, Operator, TrackReader,
                      simplify,
                      MODE_SIMPLIFY_DOUGLAS_PEUCKER,
                      MODE_SIMPLIFY_VISVALINGAM,
                      MODE_SIMPLIFY_SQUARING,
                      MODE_SIMPLIFY_MINIMIZE_ELONGATION_RATIO,
                      MODE_SIMPLIFY_PRECLUDE_LARGE_DEVIATION)



class TestSimplificationMethods(TestCase):
    
    def setUp(self):
        # Trace
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        self.csvpath = os.path.join(self.resource_path, 'data/trace0.gps')
        ObsTime.setPrintFormat("2D/2M/4Y 2h:2m:2s.3z")
        self.track = TrackReader.readFromCsv(self.csvpath) % 10
        #self.track2.plot('kx')
        
    def view(self, track, sym):
        track.plot(sym)
    
    
    def test_douglas_peucker(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        chemin = os.path.join(self.resource_path, 'data/trace1.dat')
        track = TrackReader.readFromCsv(chemin, 2, 3, -1, 4, separator=",")
        track = simplify(track, 5, mode=MODE_SIMPLIFY_DOUGLAS_PEUCKER)
        
    
    def test_visvalingam(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        chemin = os.path.join(self.resource_path, 'data/trace1.dat')
        track = TrackReader.readFromCsv(chemin, 2, 3, -1, 4, separator=",")
        track = simplify(track, 5, mode=MODE_SIMPLIFY_VISVALINGAM)
        
        
    def test_gaussien(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        chemin = os.path.join(self.resource_path, 'data/trace1.dat')
        track = TrackReader.readFromCsv(chemin, 2, 3, -1, 4, separator=",")
        kernel = GaussianKernel(201)
        track.operate(Operator.FILTER, "x", kernel, "x2")
        track.operate(Operator.FILTER, "y", kernel, "y2")
        plt.plot(track.getT(), track.getAnalyticalFeature("y"), 'b-', markersize=1.5)
        plt.plot(track.getT(), track.getAnalyticalFeature("y2"), 'r-')
        plt.show()


    def test33(self, sym = 'r-'):
        '''
        Douglas-Peucker, tolerance 50 m
        '''
        self.track *= 10
        self.track = simplify(self.track, 50, mode=MODE_SIMPLIFY_DOUGLAS_PEUCKER)
        self.view(self.track, sym)    
    

    def test34(self, sym = 'r-'):
        '''
        Vis-Valingam, tolerance 500 m2
        '''
        self.track *= 10
        self.track = simplify(self.track, 5e2, mode=MODE_SIMPLIFY_VISVALINGAM)
        self.view(self.track, sym)    
    

    def test35(self, sym = 'r-'):
        '''
        Equarissage, tolerance 50 m
        '''
        self.track = simplify(self.track, 50, mode=MODE_SIMPLIFY_SQUARING)
        self.view(self.track, sym)    


    def test36(self, sym = 'r-'):
        '''
        Minimisation des elongations par segment  
        '''
        self.track = simplify(self.track, 0.05, mode=MODE_SIMPLIFY_MINIMIZE_ELONGATION_RATIO)
        self.view(self.track, sym)    
    
    
    def test37(self, sym = 'r-'):
        '''
        Minimisation des deviations
        '''
        self.track = simplify(self.track, 0.05, mode=MODE_SIMPLIFY_PRECLUDE_LARGE_DEVIATION)
        self.view(self.track, sym)    
    


if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestSimplificationMethods("test_douglas_peucker"))
    suite.addTest(TestSimplificationMethods("test_visvalingam"))
    suite.addTest(TestSimplificationMethods("test_gaussien"))
    
    suite.addTest(TestSimplificationMethods("test33"))
    suite.addTest(TestSimplificationMethods("test34"))
    suite.addTest(TestSimplificationMethods("test35"))
    suite.addTest(TestSimplificationMethods("test36"))
    suite.addTest(TestSimplificationMethods("test37"))
    runner = TextTestRunner()
    runner.run(suite)

