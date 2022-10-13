# -----------------------------------------------------------------------------
# Script pour tester toutes les fonctions d'interpolation, lissage, 
# filtrage et simplification. 
#
# Pour memoire :
#
#    - Interpolation : ajoute, supprime ou modifie les sequences de 
#      points. Implique necessairement la suppression ou la creation 
#      de timestamps. Necessite une modelisation/description de la 
#      trajectoire afin d'etre capable de calculer une nouvelle   
#      observation theorique en tout point de la sequence.
#
#    - Lissage : ne modifie pas la sequence de points, mais modifie 
#      les positions geometriques des observations. 
#
#    - Filtrage : un type de lissage local (Kalman, Fourier, noyau etc)
#
#    - Simplification : toutes les fonctions qui visent a conserver 
#      la forme globale de la trace en réduisant le nombre de points
# -----------------------------------------------------------------------------
import math
import matplotlib.pyplot as plt
import os.path

from unittest import TestCase, TestSuite, TextTestRunner

#import sys
#sys.path.append('~/Bureau/KitYann/2-Tracklib/tracklib/tracklib')

from tracklib.core.GPSTime import GPSTime
from tracklib.io.TrackReader import TrackReader
from tracklib.core.Kernel import GaussianKernel

import tracklib.algo.Interpolation as itp



# changer aussi R dans setUp
def x_t(t):
    return 100 * math.cos(2*math.pi*t)
def y_t(t):
    return 100 * math.sin(2*math.pi*t)

    


class TestInterpolation(TestCase):
    '''
    L'erreur sur la longueur de l'intervalle entre deux points 
    (suivant qu'on les considère sur l'arc de cercle ou sur la corde) vaut :

        en = (2pi)^3/12 * (1/n)³

    ce qui fait environ :  en = 20.67 / n³

    Donc, par exemple, si tu demandes un cercle de rayon R = 100 m 
    ré-échantillonné en n = 50 points, l'erreur maximale doit être :

        e50 = 20.67/50³ R = 1.7 cm  (sur chaque tronçon)
    '''
    
    __epsilon = 1
    
    def setUp(self):
        
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        self.csvpath = os.path.join(self.resource_path, 'data/trace0.gps')
        
        GPSTime.setPrintFormat("2D/2M/4Y 2h:2m:2s.3z")
        self.track = TrackReader.readFromCsvFiles(self.csvpath) % 10
        self.track.plot('kx')
        

    def view(self, track, sym):
        track.plot(sym)
        

    # =========================================================================
    # --------------------------------------------------------------------
    # Interpolation
    # --------------------------------------------------------------------
    
    # def test1(self, sym = 'r-'):
    #     '''
    #     Interpolation lineaire en mode spatial.
    #     Trajectoire est un cercle, interpolation spatiale arc de cercle 
    #                 dont on sait calculer l'écart.
    #     '''
    #     R = 100
    #     for z in range(2, R):
    #         self.trackCercle = Synthetics.generate(x_t, y_t, dt=5, verbose=False) % 10
    #         self.trackCercle.resample(delta=z, mode=1)  
        
    #         ei = 20.67 / self.trackCercle.size()**3 * R
    #         epsilon = ei + R
        
    #         self.view(self.trackCercle, sym)
    #         for i in range(self.trackCercle.size() - 2):
    #             d = self.trackCercle.getObs(i).distanceTo(self.trackCercle.getObs(i+1))
    #             self.assertLessEqual(d, epsilon, 'erreur pour ' + str(i))

        
    # def test2(self, sym = 'r-'):
    #     '''
    #     Interpolation lineaire en mode temporel :  1 pt/s 
    #     '''
    #     R = 100
    #     for z in range(2, R):
    #         self.trackCercle = Synthetics.generate(x_t, y_t, dt=5, verbose=False) % 10
    #         self.trackCercle.plot('kx') # , append = False
    #         self.trackCercle.resample(delta=z, mode = itp.MODE_TEMPORAL)  
    #         self.view(self.trackCercle, sym)
    #         for i in range(self.trackCercle.size() - 2):
    #             d = self.trackCercle.getObs(i).distanceTo(self.trackCercle.getObs(i+1))
    #             err = abs(d - 2*3.1415*100/self.trackCercle.size())
    #             self.assertLessEqual(err, self.__epsilon, 'erreur pour ' + str(i))


    # def test3(self, sym = 'r-'):
    #     '''
    #     Interpolation lineaire en mode temporel :  definition par timestamps
    #     '''
    #     R = 100
    #     for z in range(2, R):
    #         self.trackCercle = Synthetics.generate(x_t, y_t, dt=z, verbose=False) % 10
    #         self.trackCercle.plot('kx')
        
    #         a = int(self.trackCercle[0].timestamp.toAbsTime())
    #         b = int(self.trackCercle[-1].timestamp.toAbsTime())
    #         T = [GPSTime.readUnixTime(x) for x in range(a, b, 10)]
        
    #         self.trackCercle.resample(delta=T, mode = itp.MODE_TEMPORAL)
    #         self.view(self.trackCercle, sym)
    #         for i in range(self.trackCercle.size() - 2):
    #             d = self.trackCercle.getObs(i).distanceTo(self.trackCercle.getObs(i+1))
    #             err = abs(d - 2*3.1415*100/self.trackCercle.size())
    #             self.assertLessEqual(err, self.__epsilon, 'erreur pour ' + str(i))
        

    # def test4(self, sym = 'r-'):
    #     '''
    #     Interpolation lineaire en mode temporel :  definition // autre trace
    #     '''
    #     R = 100
    #     for z in range(2, R):
    #         self.trackCercle = Synthetics.generate(x_t, y_t, dt=z, verbose=False) % 10
    #         self.trackCercle.plot('kx')
            
    #         temp = self.trackCercle.copy()
    #         temp %= 5
    #         if temp.size() < 2:
    #             continue
    #         temp.resample(delta=self.trackCercle, mode = itp.MODE_TEMPORAL)
    #         self.view(temp, sym)
            

    # def test5(self, sym = 'r-'):
    #     '''
    #     Idem test 4 en raccourci
    #     '''
    #     R = 100
    #     for z in range(2, R):
    #         self.trackCercle = Synthetics.generate(x_t, y_t, dt=z, verbose=False) % 10
    #         self.trackCercle.plot('kx')
        
    #         temp = self.trackCercle.copy()
    #         temp %= 5
    #         if temp.size() < 2:
    #             continue
    #         temp = temp // self.trackCercle   
    #         self.view(temp, sym)

        
    def test6(self, sym = 'r-'):
        '''
        Interpolation lineaire en mode spatial : en 100 pts
        '''
        #temp = self.track.copy()
        self.track.resample(npts = 100)  
        self.view(self.track, sym)

        
    def test7(self, sym = 'r-'):
        '''
        Interpolation lineaire en mode temporel : en 20 pts
        '''
        #temp = track.copy()
        self.track.resample(npts = 80, mode = itp.MODE_TEMPORAL)  
        self.view(self.track, sym)

        
    def test8(self, sym = 'r-'):
        '''
        Idem test7 en raccourci
        '''
        #temp = track.copy()
        self.track = self.track**80
        self.view(self.track, sym)


    def test9(self, sym = 'r-'):
        '''
        Interpolation lineaire : sur-echantillonnage temporel facteur 5
        '''
 	    #temp = track.copy()
        self.track.resample(factor = 5)  
        self.view(self.track, sym)
 	

    def test10(self, sym = 'r-'):
        '''
        Idem test9 en raccourci
        '''
 	    #temp = track.copy()
        self.track = self.track*5
        self.view(self.track, sym)


    def test11(self, sym = 'r-'):
        '''
        Interpolation lineaire : sur-echantillonnage spatial facteur 2
        '''
        #temp = track.copy()
        self.track.resample(factor = 2, mode = itp.MODE_SPATIAL)  
        self.view(self.track, sym)

        
    def test12(self, sym = 'r-'):
        '''
        Interpolation par splines plaques minces en mode spatial : 1 pt / 10 m
        '''
        # temp = track.copy()
        self.track.resample(delta=10, algo = itp.ALGO_THIN_SPLINES)  
        self.view(self.track, sym)

        
    def test13(self, sym = 'r-'):
        '''
        Interpolation par splines plaques minces en mode temporel : 2 pt/s
        '''
        # temp = track.copy()
        self.track.resample(delta=0.5, algo = itp.ALGO_THIN_SPLINES, mode = itp.MODE_TEMPORAL)  
        self.view(self.track, sym)
 	

    def test14(self, sym = 'r-'):
        '''
        Interpolation par B-splines en mode spatial : 1 pt / m
        '''
        # temp = track.copy()
        self.track %= 5
        self.track.resample(delta=1, algo = itp.ALGO_B_SPLINES)  
        self.view(self.track, sym)

        
    def test15(self, sym = 'r-'):
        '''
        Interpolation par B-splines en mode temporel : 1 pt/s
        '''
        # temp = track.copy()
        self.track %= 5
        self.track.resample(delta=1, algo = itp.ALGO_B_SPLINES, mode = itp.MODE_TEMPORAL)  
        self.view(self.track, sym)
 	
 	
    def test16(self, sym = 'r-'):
        '''
        Interpolation par processus gaussien en mode spatial : 1 pt / m
        '''
        # temp = track.copy()
        itp.GP_KERNEL = GaussianKernel(10)
        self.track.resample(delta=100, algo = itp.ALGO_GAUSSIAN_PROCESS)  
        self.view(self.track, sym)	

        
    def test17(self, sym = 'r-'):
        '''
        Interpolation par processus gaussien en mode temporel : 1 pt/s   
        '''
        # temp = track.copy()
        itp.GP_KERNEL = GaussianKernel(10)
        self.track.resample(delta=1, algo = itp.ALGO_GAUSSIAN_PROCESS, mode = itp.MODE_TEMPORAL)  
        self.view(self.track, sym)	
	        
        
        
    # =========================================================================
    # --------------------------------------------------------------------
    # Interpolation + Lissage
    # --------------------------------------------------------------------

    def test18(self, sym = 'r-'):
        '''
        Lissage/interpolation par splines plaques minces en mode spatial : 1 pt / 10 m
        '''
        # temp = track.copy()
        itp.SPLINE_PENALIZATION = 1e-2
        self.track.resample(delta=10, algo = itp.ALGO_THIN_SPLINES)  
        self.view(self.track, sym)
 	

    def test19(self, sym = 'r-'):
         '''
         Lissage/interpolation par splines plaques minces en mode temporel : 1 pt/s
         '''
         # temp = track.copy()
         itp.SPLINE_PENALIZATION = 1e4
         self.track.resample(delta=10, algo = itp.ALGO_THIN_SPLINES, mode = itp.MODE_TEMPORAL)  
         self.view(self.track, sym)
 	

    def test20(self, sym = 'r-'):
        '''
        Lissage/interpolation par processus gaussien en mode spatial : 1 pt / 10 m
        '''
        # temp = track.copy()
        itp.GP_KERNEL = GaussianKernel(100)
        itp.GP_SMOOTHING = 0.001
        self.track.resample(delta=10, algo = itp.ALGO_GAUSSIAN_PROCESS)  
        self.view(self.track, sym)	
 	

    def test21(self, sym = 'r-'):
        '''
        Lissage/interpolation par processus gaussien en mode temporel : 1 pt/s    
        '''
        # temp = track.copy()
        itp.GP_KERNEL = GaussianKernel(100)
        itp.GP_SMOOTHING = 0.001
        self.track.resample(delta=1, algo = itp.ALGO_GAUSSIAN_PROCESS, mode = itp.MODE_TEMPORAL)  
        self.view(self.track, sym)	
 	
 	
     
     
 	

    


    
    
    
if __name__ == '__main__':
    suite = TestSuite()
    
    #suite.addTest(TestInterpolation("test1"))
    #suite.addTest(TestInterpolation("test2"))
    #suite.addTest(TestInterpolation("test3"))
    #suite.addTest(TestInterpolation("test4"))
    #suite.addTest(TestInterpolation("test5"))
    suite.addTest(TestInterpolation("test6"))
    suite.addTest(TestInterpolation("test7"))
    suite.addTest(TestInterpolation("test8"))
    suite.addTest(TestInterpolation("test9"))
    suite.addTest(TestInterpolation("test10"))
    suite.addTest(TestInterpolation("test11"))
    suite.addTest(TestInterpolation("test12"))
    suite.addTest(TestInterpolation("test13"))
    suite.addTest(TestInterpolation("test14"))
    suite.addTest(TestInterpolation("test15"))
    suite.addTest(TestInterpolation("test16"))
    suite.addTest(TestInterpolation("test17"))
    
    suite.addTest(TestInterpolation("test18"))
    suite.addTest(TestInterpolation("test19"))
    suite.addTest(TestInterpolation("test20"))
    suite.addTest(TestInterpolation("test21"))
    
    runner = TextTestRunner()
    runner.run(suite)



