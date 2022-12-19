# -*- coding: utf-8 -*-

#import matplotlib.pyplot as plt
import os.path

from tracklib.core.ObsTime import ObsTime
from tracklib.io.FileReader import FileReader
from tracklib.core.Kernel import GaussianKernel

import tracklib.algo.Filtering as flt
import tracklib.algo.Interpolation as itp


resource_path = os.path.join(os.path.split(__file__)[0], "..")
csvpath = os.path.join(resource_path, 'data/trace0.gps')
ObsTime.setPrintFormat("2D/2M/4Y 2h:2m:2s.3z")
track = FileReader.readFromFile(csvpath)%10
track = track.extract(20, 45)
track.plot('kx')
print("Nb pts = ", track.size())


def view(track, sym):
	track.plot(sym)
	#print(track)
	print("Nb pts = ", track.size())


# =============================================================================


# Interpolation par processus gaussien en mode spatial : 1 pt / m
def test16(sym = 'r-'):
	#temp = track.copy()
	itp.GP_KERNEL = GaussianKernel(10)
	track.resample(delta=100, algo = itp.ALGO_GAUSSIAN_PROCESS)  
	view(track, sym)	
    
    
# Lissage/interpolation par processus gaussien en mode spatial : 1 pt / 10 m
def test20(sym = 'r-'):
	temp = track.copy()
	itp.GP_KERNEL = GaussianKernel(100)
	itp.GP_SMOOTHING = 0.001
	temp.resample(delta=10, algo = itp.ALGO_GAUSSIAN_PROCESS)  
	view(temp, sym)	
    
    
# Filtrage par noyau gaussien
def test26(sym = 'r-'):
	temp = track.copy()
	temp *= 10
	temp = flt.filter_seq(temp, kernel=GaussianKernel(20), dim=flt.FILTER_XY)
	view(temp, sym)	
    

if __name__ == '__main__':
    print ('-------')
    test16()
