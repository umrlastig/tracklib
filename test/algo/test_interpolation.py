# --------------------------------------------------------------------
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
# --------------------------------------------------------------------
import sys
import matplotlib.pyplot as plt

from unittest import TestCase, TestSuite, TextTestRunner

#sys.path.append('~/Bureau/KitYann/2-Tracklib/tracklib/tracklib')

from tracklib.core.GPSTime import GPSTime
from tracklib.io.FileReader import FileReader
from tracklib.core.Kernel import DiracKernel
from tracklib.core.Kernel import GaussianKernel
from tracklib.core.Kernel import TriangularKernel
from tracklib.core.Kernel import ExponentialKernel

import tracklib.algo.Filtering as flt
import tracklib.algo.Interpolation as itp
#import tracklib.algo.Simplification as spf


class TestInterpolation(TestCase):
    
    __epsilon = 280
    
    def setUp(self):
        GPSTime.setPrintFormat("2D/2M/4Y 2h:2m:2s.3z")
        self.track = FileReader.readFromFile('data/trace0.gps') % 10
        self.track.plot('kx')
        #print (self.track.size(), ', ', self.track.length())

    def view(self, sym):
        self.track.plot(sym); 
        #print(self.track);
        #print("Nb pts = ", self.track.size())
        plt.show()

    # =========================================================================
    # --------------------------------------------------------------------
    # Interpolation
    # --------------------------------------------------------------------
    
    def test1(self, sym = 'r-'):
        '''
        Interpolation lineaire en mode spatial : 1 pt / 10 m
        '''
        self.track.resample(delta=1000)  
        for i in range(11):
            d = self.track.getObs(i).distanceTo(self.track.getObs(i+1))
            self.assertLessEqual(abs(1000 - d), self.__epsilon, 'erreur pour ' + str(i))
        self.view(sym)

        
    def test2(self, sym = 'r-'):
        '''
        Interpolation lineaire en mode temporel :  1 pt/s 
        '''
        self.track.resample(delta=1, mode = itp.MODE_TEMPORAL)  
        self.view(sym)
        self.assertEqual(self.track.size(), 452)


    def test3(self, sym = 'r-'):
        '''
        Interpolation lineaire en mode temporel :  definition par timestamps
        '''
        #temp = self.track.copy()
        a = int(self.track[0].timestamp.toAbsTime())
        b = int(self.track[-1].timestamp.toAbsTime())
        T = [GPSTime.readUnixTime(x) for x in range(a, b, 10)]
        self.track.resample(delta=T, mode = itp.MODE_TEMPORAL)
        self.view(sym)
        

    def test4(self, sym = 'r-'):
        '''
        Interpolation lineaire en mode temporel :  definition // autre trace
        '''
        temp = self.track.copy()
        self.track %= 5
        self.track.resample(delta=self.track, mode = itp.MODE_TEMPORAL)
        self.view(sym)

        
    def test5(self, sym = 'r-'):
        '''
        Idem test 4 en raccourci
        '''
        temp = self.track.copy()
        temp %= 5
        temp = temp // self.track   
        self.view(sym)

        
    def test6(self, sym = 'r-'):
        '''
        Interpolation lineaire en mode spatial : en 100 pts
        '''
        #temp = self.track.copy()
        self.track.resample(npts = 100)  
        self.view(sym)

        
    def test7(self, sym = 'r-'):
        '''
        Interpolation lineaire en mode temporel : en 20 pts
        '''
        #temp = track.copy()
        self.track.resample(npts = 80, mode = itp.MODE_TEMPORAL)  
        self.view(sym)

        
    def test8(self, sym = 'r-'):
        '''
        Idem test7 en raccourci
        '''
        #temp = track.copy()
        self.track = self.track**80
        self.view(sym)


    def test9(self, sym = 'r-'):
        '''
        Interpolation lineaire : sur-echantillonnage temporel facteur 5
        '''
 	    #temp = track.copy()
        self.track.resample(factor = 5)  
        self.view(sym)
 	

    def test10(self, sym = 'r-'):
        '''
        Idem test9 en raccourci
        '''
 	    #temp = track.copy()
        self.track = self.track*5
        self.view(sym)


    def test11(self, sym = 'r-'):
        '''
        Interpolation lineaire : sur-echantillonnage spatial facteur 2
        '''
        #temp = track.copy()
        self.track.resample(factor = 2, mode = itp.MODE_SPATIAL)  
        self.view(sym)

        
    def test12(self, sym = 'r-'):
        '''
        Interpolation par splines plaques minces en mode spatial : 1 pt / 10 m
        '''
        # temp = track.copy()
        self.track.resample(delta=10, algo = itp.ALGO_THIN_SPLINES)  
        self.view(sym)

        
    def test13(self, sym = 'r-'):
        '''
        Interpolation par splines plaques minces en mode temporel : 2 pt/s
        '''
        # temp = track.copy()
        self.track.resample(delta=0.5, algo = itp.ALGO_THIN_SPLINES, mode = itp.MODE_TEMPORAL)  
        self.view(sym)
 	

    def test14(self, sym = 'r-'):
        '''
        Interpolation par B-splines en mode spatial : 1 pt / m
        '''
        # temp = track.copy()
        self.track %= 5
        self.track.resample(delta=1, algo = itp.ALGO_B_SPLINES)  
        self.view(sym)

        
    def test15(self, sym = 'r-'):
        '''
        Interpolation par B-splines en mode temporel : 1 pt/s
        '''
        # temp = track.copy()
        self.track %= 5
        self.track.resample(delta=1, algo = itp.ALGO_B_SPLINES, mode = itp.MODE_TEMPORAL)  
        self.view(sym)
 	
 	
    def test16(self, sym = 'r-'):
        '''
        Interpolation par processus gaussien en mode spatial : 1 pt / m
        '''
        # temp = track.copy()
        itp.GP_KERNEL = GaussianKernel(10)
        self.track.resample(delta=100, algo = itp.ALGO_GAUSSIAN_PROCESS)  
        self.view(sym)	

        
    def test17(self, sym = 'r-'):
        '''
        Interpolation par processus gaussien en mode temporel : 1 pt/s   
        '''
        # temp = track.copy()
        itp.GP_KERNEL = GaussianKernel(10)
        self.track.resample(delta=1, algo = itp.ALGO_GAUSSIAN_PROCESS, mode = itp.MODE_TEMPORAL)  
        self.view(sym)	
	        
        
        
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
        self.view(sym)
 	

    def test19(self, sym = 'r-'):
         '''
         Lissage/interpolation par splines plaques minces en mode temporel : 1 pt/s
         '''
         # temp = track.copy()
         itp.SPLINE_PENALIZATION = 1e4
         self.track.resample(delta=10, algo = itp.ALGO_THIN_SPLINES, mode = itp.MODE_TEMPORAL)  
         self.view(sym)
 	

    def test20(self, sym = 'r-'):
        '''
        Lissage/interpolation par processus gaussien en mode spatial : 1 pt / 10 m
        '''
        # temp = track.copy()
        itp.GP_KERNEL = GaussianKernel(100)
        itp.GP_SMOOTHING = 0.001
        self.track.resample(delta=10, algo = itp.ALGO_GAUSSIAN_PROCESS)  
        self.view(sym)	
 	

    def test21(self, sym = 'r-'):
        '''
        Lissage/interpolation par processus gaussien en mode temporel : 1 pt/s    
        '''
        # temp = track.copy()
        itp.GP_KERNEL = GaussianKernel(100)
        itp.GP_SMOOTHING = 0.001
        self.track.resample(delta=1, algo = itp.ALGO_GAUSSIAN_PROCESS, mode = itp.MODE_TEMPORAL)  
        self.view(sym)	
 	
 	
     
     # =========================================================================
     # --------------------------------------------------------------------
     # Lissage
     # --------------------------------------------------------------------

    def test22(self, sym = 'r-'):
        '''
        Filtrage par noyau fenetre glissante de taille 5
        '''
        self.track = flt.filter_seq(self.track, kernel=5, dim=flt.FILTER_XY)
        self.view(sym)	
	

    def test23(self, sym = 'r-'):
        '''
        Filtrage par noyau 'user-defined'
        '''
        self.track = flt.filter_seq(self.track, kernel=[1,2,32,2,1], dim=["x","y"])
        self.view(sym)	
 	

    def test24(self, sym = 'r-'):
        '''
        Filtrage par noyau 'user-defined' pour faire un filtre 'avance'
        '''
        self.track = flt.filter_seq(self.track, kernel=[0,0,1], dim=["y"])
        self.view(sym)	
 	

    def test25(self, sym = 'r-'):
        '''
        Filtrage par noyau 'user-defined' pour faire un filtre 'retard'
        '''
        self.track = flt.filter_seq(self.track, kernel=[1,0,0], dim=["y"])
        self.view(sym)	
 	

    def test26(self, sym = 'r-'):
        '''
        Filtrage par noyau gaussien
        '''
        self.track = self.track.copy()
        self.track *= 10
        self.track = flt.filter_seq(self.track, kernel=GaussianKernel(20), dim=flt.FILTER_XY)
        self.view(sym)	


    def test27(self, sym = 'r-'):
        '''
        Filtrage par noyau exponentiel
        '''
        self.track = self.track.copy()
        self.track *= 10
        self.track = flt.filter_seq(self.track, kernel=ExponentialKernel(20), dim=flt.FILTER_XY)
        self.view(sym)	


    def test28(self, sym = 'r-'):
        '''
        Filtrage par noyau triangulaire
        '''
        self.track = self.track.copy()
        self.track *= 10
        self.track = flt.filter_seq(self.track, kernel=TriangularKernel(20), dim=flt.FILTER_XY)
        self.view(sym)	
 	
        
    def test29(self, sym = 'r-'):
         '''
         Filtrage par noyau de Dirac (sans effet)
         '''
         self.track = self.track.copy()
         self.track *= 10
         self.track = flt.filter_seq(self.track, kernel=DiracKernel(), dim=flt.FILTER_XY)
         self.view(sym)	


    def test30(self, sym = 'r-'):
        '''
        Filtrage passe-bas par transformation de Fourier (frequence temporelle)
        '''
        self.track = flt.filter_freq(self.track, 1, mode=flt.FILTER_TEMPORAL, 
                                     type=flt.FILTER_LOW_PASS, dim=flt.FILTER_XY)
        self.view(sym)	
    
    
    def test31(self, sym = 'r-'):
        '''
        Filtrage passe-bas par transformation de Fourier (frequence spatiale)
        '''
        self.track *= 10
        self.track = flt.filter_freq(self.track, 0.03, 
                                     mode=flt.FILTER_SPATIAL, 
                                     type=flt.FILTER_LOW_PASS, 
                                     dim=flt.FILTER_XY)
        self.view(sym)	


    def test32(self, sym = 'r-'):
        '''
        Filtrage de Kalman (50 cm sur le GPS / 2 m.s-1 sur la vitesse)
        '''
        self.track = flt.Kalman(self.track, 0.5, 2)
        self.view(sym)	
    
    
    # =========================================================================
    # --------------------------------------------------------------------
    # Simplification
    # --------------------------------------------------------------------

# # Douglas-Peucker, tolerance 50 m
# def test33(sym = 'r-'):
#     temp = track.copy()
#     temp *= 10
#     temp = spf.simplify(temp, 50, mode = spf.MODE_SIMPLIFY_DOUGLAS_PEUCKER)
#     view(temp, sym)	
    
# # Vis-Valingam, tolerance 500 m2
# def test34(sym = 'r-'):
#     temp = track.copy()
#     temp *= 10
#     temp = spf.simplify(temp, 5e2, mode = spf.MODE_SIMPLIFY_VISVALINGAM)
#     view(temp, sym)	
    
# # Equarissage, tolerance 50 m
# def test35(sym = 'r-'):
#     temp = spf.simplify(track, 50, mode = spf.MODE_SIMPLIFY_SQUARING)
#     view(temp, sym)	

# # Minimisation des elongations par segment  
# def test36(sym = 'r-'):
#     temp = spf.simplify(track, 0.05, mode = spf.MODE_SIMPLIFY_MINIMIZE_ELONGATION_RATIO)
#     view(temp, sym)	
    
# # Minimisation des deviations
# def test37(sym = 'r-'):
#     temp = spf.simplify(track, 0.05, mode = spf.MODE_SIMPLIFY_PRECLUDE_LARGE_DEVIATION)
#     view(temp, sym)	
    
# test15() 



if __name__ == '__main__':
    suite = TestSuite()
    
    suite.addTest(TestInterpolation("test1"))
    suite.addTest(TestInterpolation("test2"))
    suite.addTest(TestInterpolation("test3"))
    suite.addTest(TestInterpolation("test4"))
    suite.addTest(TestInterpolation("test5"))
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
    
    suite.addTest(TestInterpolation("test22"))
    suite.addTest(TestInterpolation("test23"))
    suite.addTest(TestInterpolation("test24"))
    suite.addTest(TestInterpolation("test25"))
    suite.addTest(TestInterpolation("test26"))
    suite.addTest(TestInterpolation("test27"))
    suite.addTest(TestInterpolation("test28"))
    suite.addTest(TestInterpolation("test29"))
    suite.addTest(TestInterpolation("test30"))
    suite.addTest(TestInterpolation("test31"))
    suite.addTest(TestInterpolation("test32"))
    
    runner = TextTestRunner()
    runner.run(suite)



