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
import math
import sys
import matplotlib.pyplot as plt

from unittest import TestCase, TestSuite, TextTestRunner

sys.path.append('~/Bureau/KitYann/2-Tracklib/tracklib/tracklib')

from tracklib.core.GPSTime import GPSTime
from tracklib.io.FileReader import FileReader
#from tracklib.core.Kernel import DiracKernel
#from tracklib.core.Kernel import GaussianKernel
#from tracklib.core.Kernel import TriangularKernel
#from tracklib.core.Kernel import ExponentialKernel

#import tracklib.algo.Filtering as flt
import tracklib.algo.Interpolation as itp
#import tracklib.algo.Simplification as spf


class TestInterpolation(TestCase):
    
    # --------------------------------------------------------------------
    # Interpolation
    # --------------------------------------------------------------------
    
    __epsilon = 280
    
    def setUp(self):
        GPSTime.setPrintFormat("2D/2M/4Y 2h:2m:2s.3z")
        self.track = FileReader.readFromFile('data/trace0.gps') % 10
        self.track.plot('kx')
        print (self.track.size(), ', ', self.track.length())

    def view(self, sym):
        self.track.plot(sym); 
        #print(self.track);
        print("Nb pts = ", self.track.size())
        plt.show()

   
    # Interpolation lineaire en mode spatial : 1 pt / 10 m
    def test1(self, sym = 'r-'):
        self.track.resample(delta=1000)  
        for i in range(11):
            d = self.track.getObs(i).distanceTo(self.track.getObs(i+1))
            self.assertLessEqual(abs(1000 - d), self.__epsilon, 'erreur pour ' + str(i))
        self.view(sym)
        
    # Interpolation lineaire en mode temporel :  1 pt/s 
    def test2(self, sym = 'r-'):
        self.track.resample(delta=1, mode = itp.MODE_TEMPORAL)  
        self.view(sym)

    def test3(self, sym = 'r-'):
        '''
        Interpolation lineaire en mode temporel :  definition par timestamps
        '''
        temp = self.track.copy()
        a = int(self.track[0].timestamp.toAbsTime())
        b = int(self.track[-1].timestamp.toAbsTime())
        T = [GPSTime.readUnixTime(x) for x in range(a, b, 10)]
        temp.resample(delta=T, mode = itp.MODE_TEMPORAL)
        self.view(sym)
        
        
# # Interpolation lineaire en mode temporel :  definition // autre trace
# def test4(sym = 'r-'):
# 	temp = track.copy()
# 	temp %= 5
# 	temp.resample(delta=track, mode = itp.MODE_TEMPORAL)
# 	view(temp, sym)
# 	
# # Idem test 4 en raccourci
# def test5(sym = 'r-'):
# 	temp = track.copy()
# 	temp %= 5
# 	temp = temp // track   
# 	view(temp, sym)
# 	
# # Interpolation lineaire en mode spatial : en 100 pts
# def test6(sym = 'r-'):
# 	temp = track.copy()
# 	temp.resample(npts = 100)  
# 	view(temp, sym)
# 	
# # Interpolation lineaire en mode temporel : en 20 pts
# def test7(sym = 'r-'):
# 	temp = track.copy()
# 	temp.resample(npts = 80, mode = itp.MODE_TEMPORAL)  
# 	view(temp, sym)
# 	
# # Idem test7 en raccourci
# def test8(sym = 'r-'):
# 	temp = track.copy()
# 	temp = temp**80
# 	view(temp, sym)

# # Interpolation lineaire : sur-echantillonnage temporel facteur 5
# def test9(sym = 'r-'):
# 	temp = track.copy()
# 	temp.resample(factor = 5)  
# 	view(temp, sym)
# 	
# # Idem test9 en raccourci
# def test10(sym = 'r-'):
# 	temp = track.copy()
# 	temp = temp*5
# 	view(temp, sym)

# # Interpolation lineaire : sur-echantillonnage spatial facteur 2
# def test11(sym = 'r-'):
# 	temp = track.copy()
# 	temp.resample(factor = 2, mode = itp.MODE_SPATIAL)  
# 	view(temp, sym)
# 	
# # Interpolation par splines plaques minces en mode spatial : 1 pt / 10 m
# def test12(sym = 'r-'):
# 	temp = track.copy()
# 	temp.resample(delta=10, algo = itp.ALGO_THIN_SPLINES)  
# 	view(temp, sym)
# 	
# # Interpolation par splines plaques minces en mode temporel : 2 pt/s
# def test13(sym = 'r-'):
# 	temp = track.copy()
# 	temp.resample(delta=0.5, algo = itp.ALGO_THIN_SPLINES, mode = itp.MODE_TEMPORAL)  
# 	view(temp, sym)
# 	
# # Interpolation par B-splines en mode spatial : 1 pt / m
# def test14(sym = 'r-'):
# 	temp = track.copy()
# 	temp %= 5
# 	temp.resample(delta=1, algo = itp.ALGO_B_SPLINES)  
# 	view(temp, sym)
# 	
# # Interpolation par B-splines en mode temporel : 1 pt/s
# def test15(sym = 'r-'):
# 	temp = track.copy()
# 	temp %= 5
# 	temp.resample(delta=1, algo = itp.ALGO_B_SPLINES, mode = itp.MODE_TEMPORAL)  
# 	view(temp, sym)
# 	
# 	
# # Interpolation par processus gaussien en mode spatial : 1 pt / m
# def test16(sym = 'r-'):
# 	temp = track.copy()
# 	itp.GP_KERNEL = GaussianKernel(10)
# 	temp.resample(delta=100, algo = itp.ALGO_GAUSSIAN_PROCESS)  
# 	view(temp, sym)	
# 	
# # Interpolation par processus gaussien en mode temporel : 1 pt/s   
# def test17(sym = 'r-'):
# 	temp = track.copy()
# 	itp.GP_KERNEL = GaussianKernel(10)
# 	temp.resample(delta=1, algo = itp.ALGO_GAUSSIAN_PROCESS, mode = itp.MODE_TEMPORAL)  
# 	view(temp, sym)	
	        

# --------------------------------------------------------------------
# Interpolation + Lissage
# --------------------------------------------------------------------

# # Lissage/interpolation par splines plaques minces en mode spatial : 1 pt / 10 m
# def test18(sym = 'r-'):
# 	temp = track.copy()
# 	itp.SPLINE_PENALIZATION = 1e-2
# 	temp.resample(delta=10, algo = itp.ALGO_THIN_SPLINES)  
# 	view(temp, sym)
# 	
# # Lissage/interpolation par splines plaques minces en mode temporel : 1 pt/s
# def test19(sym = 'r-'):
# 	temp = track.copy()
# 	itp.SPLINE_PENALIZATION = 1e4
# 	temp.resample(delta=10, algo = itp.ALGO_THIN_SPLINES, mode = itp.MODE_TEMPORAL)  
# 	view(temp, sym)
# 	
# # Lissage/interpolation par processus gaussien en mode spatial : 1 pt / 10 m
# def test20(sym = 'r-'):
# 	temp = track.copy()
# 	itp.GP_KERNEL = GaussianKernel(100)
# 	itp.GP_SMOOTHING = 0.001
# 	temp.resample(delta=10, algo = itp.ALGO_GAUSSIAN_PROCESS)  
# 	view(temp, sym)	
# 	
# # Lissage/interpolation par processus gaussien en mode temporel : 1 pt/s    
# def test21(sym = 'r-'):
# 	temp = track.copy()
# 	itp.GP_KERNEL = GaussianKernel(100)
# 	itp.GP_SMOOTHING = 0.001
# 	temp.resample(delta=1, algo = itp.ALGO_GAUSSIAN_PROCESS, mode = itp.MODE_TEMPORAL)  
# 	view(temp, sym)	
# 	
# 	
# # --------------------------------------------------------------------
# # Lissage
# # --------------------------------------------------------------------

# # Filtrage par noyau fenetre glissante de taille 5
# def test22(sym = 'r-'):
# 	temp = flt.filter_seq(track, kernel=5, dim=flt.FILTER_XY)
# 	view(temp, sym)	
# 	
# # Filtrage par noyau 'user-defined'
# def test23(sym = 'r-'):
# 	temp = flt.filter_seq(track, kernel=[1,2,32,1], dim=["x","y"])
# 	view(temp, sym)	
# 	
# # Filtrage par noyau 'user-defined' pour faire un filtre 'avance'
# def test24(sym = 'r-'):
# 	temp = flt.filter_seq(track, kernel=[0,0,1], dim=["y"])
# 	view(temp, sym)	
# 	
# # Filtrage par noyau 'user-defined' pour faire un filtre 'retard'
# def test25(sym = 'r-'):
# 	temp = flt.filter_seq(track, kernel=[1,0,0], dim=["y"])
# 	view(temp, sym)	
# 	
# # Filtrage par noyau gaussien
# def test26(sym = 'r-'):
# 	temp = track.copy()
# 	temp *= 10
# 	temp = flt.filter_seq(temp, kernel=GaussianKernel(20), dim=flt.FILTER_XY)
# 	view(temp, sym)	

# # Filtrage par noyau exponentiel
# def test27(sym = 'r-'):
# 	temp = track.copy()
# 	temp *= 10
# 	temp = flt.filter_seq(temp, kernel=ExponentialKernel(20), dim=flt.FILTER_XY)
# 	view(temp, sym)	

# # Filtrage par noyau triangulaire
# def test28(sym = 'r-'):
# 	temp = track.copy()
# 	temp *= 10
# 	temp = flt.filter_seq(temp, kernel=TriangularKernel(20), dim=flt.FILTER_XY)
# 	view(temp, sym)	
# 	
# # Filtrage par noyau de Dirac (sans effet)
# def test29(sym = 'r-'):
# 	temp = track.copy()
# 	temp *= 10
# 	temp = flt.filter_seq(temp, kernel=DiracKernel(), dim=flt.FILTER_XY)
# 	view(temp, sym)	

# # Filtrage passe-bas par transformation de Fourier (frequence temporelle)
# def test30(sym = 'r-'):
#     temp = flt.filter_freq(track, 1, mode=flt.FILTER_TEMPORAL, type=flt.FILTER_LOW_PASS, dim=flt.FILTER_XY)
#     view(temp, sym)	
    
# # Filtrage passe-bas par transformation de Fourier (frequence spatiale)
# def test31(sym = 'r-'):
#     temp = track.copy()
#     temp *= 10
#     temp = flt.filter_freq(temp, 0.03, mode=flt.FILTER_SPATIAL, type=flt.FILTER_LOW_PASS, dim=flt.FILTER_XY)
#     view(temp, sym)	

# # Filtrage de Kalman (50 cm sur le GPS / 2 m.s-1 sur la vitesse)
# def test32(sym = 'r-'):
#     temp = flt.Kalman(track, 0.5, 2)
#     view(temp, sym)	
    
    
# # --------------------------------------------------------------------
# # Simplification
# # --------------------------------------------------------------------

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
    runner = TextTestRunner()
    runner.run(suite)



