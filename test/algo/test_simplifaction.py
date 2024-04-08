"""

"""
from unittest import TestCase, TestSuite, TextTestRunner
import matplotlib.pyplot as plt
import os.path

from tracklib import (ObsTime, GaussianKernel, Operator, TrackReader,
                      ENUCoords, Track, Obs,
                      simplify,  
                      MODE_SIMPLIFY_DOUGLAS_PEUCKER,
                      MODE_SIMPLIFY_VISVALINGAM,
                      MODE_SIMPLIFY_SQUARING,
                      MODE_SIMPLIFY_MINIMIZE_ELONGATION_RATIO,
                      MODE_SIMPLIFY_PRECLUDE_LARGE_DEVIATION,
                      compareWithDouglasPeuckerSimplification,
                      averageOffsetDistance)



class TestSimplificationMethods(TestCase):
    
    __epsilon = 0.001
    
    def setUp(self):
        # Trace
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        self.csvpath = os.path.join(self.resource_path, 'data/trace0.gps')
        ObsTime.setPrintFormat("2D/2M/4Y 2h:2m:2s.3z")
        self.track = TrackReader.readFromCsv(self.csvpath) % 10
        #self.track.plot('kx')
        
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
    

    def testCompareWithDouglasPeuckerSimplification(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        trace1 = Track([], 1)

        trace1.addObs(Obs(ENUCoords(0, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:00")))
        trace1.addObs(Obs(ENUCoords(10, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:12")))
        trace1.addObs(Obs(ENUCoords(10, 10, 0), ObsTime.readTimestamp("2018-01-01 10:00:40")))
        trace1.addObs(Obs(ENUCoords(20, 10, 0), ObsTime.readTimestamp("2018-01-01 10:01:50")))
        trace1.addObs(Obs(ENUCoords(20, 20, 0), ObsTime.readTimestamp("2018-01-01 10:02:10")))
        trace1.addObs(Obs(ENUCoords(30, 20, 0), ObsTime.readTimestamp("2018-01-01 10:02:35")))
        trace1.addObs(Obs(ENUCoords(30, 30, 0), ObsTime.readTimestamp("2018-01-01 10:02:43")))
        trace1.addObs(Obs(ENUCoords(40, 30, 0), ObsTime.readTimestamp("2018-01-01 10:02:55")))
        trace1.addObs(Obs(ENUCoords(60, 30, 0), ObsTime.readTimestamp("2018-01-01 10:03:25")))
        
        trace1.plot('k-')
        
        borneinf = min(int(trace1.bbox().getDx()), int(trace1.bbox().getDy())) / 4 # 25%
        self.assertEqual(borneinf, 7.5)
        
        ind1 = compareWithDouglasPeuckerSimplification(trace1, borneinf)
        self.assertEqual(ind1, 8)
        
        
    def testAverageOffsetDistance(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        trace1 = Track([], 1)
        trace1.addObs(Obs(ENUCoords(0, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:00")))
        trace1.addObs(Obs(ENUCoords(10, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:12")))
        trace1.addObs(Obs(ENUCoords(10, 10, 0), ObsTime.readTimestamp("2018-01-01 10:00:40")))
        trace1.addObs(Obs(ENUCoords(20, 10, 0), ObsTime.readTimestamp("2018-01-01 10:01:50")))
        trace1.addObs(Obs(ENUCoords(20, 20, 0), ObsTime.readTimestamp("2018-01-01 10:02:10")))
        trace1.addObs(Obs(ENUCoords(30, 20, 0), ObsTime.readTimestamp("2018-01-01 10:02:35")))
        trace1.addObs(Obs(ENUCoords(30, 30, 0), ObsTime.readTimestamp("2018-01-01 10:02:43")))
        trace1.addObs(Obs(ENUCoords(40, 30, 0), ObsTime.readTimestamp("2018-01-01 10:02:55")))
        trace1.addObs(Obs(ENUCoords(60, 30, 0), ObsTime.readTimestamp("2018-01-01 10:03:25")))
        
        trace1.plot('k-')
        
        ind2 = averageOffsetDistance(trace1, 7.5)
        self.assertLessEqual(abs(ind2 - 1.849), self.__epsilon)
        

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
    
    suite.addTest(TestSimplificationMethods("testCompareWithDouglasPeuckerSimplification"))
    suite.addTest(TestSimplificationMethods("testAverageOffsetDistance"))
    
    runner = TextTestRunner()
    runner.run(suite)

