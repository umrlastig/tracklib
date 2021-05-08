"""
Kernels for filtering        
"""

import sys
import math
import numpy as np
import matplotlib.pyplot as plt


# -----------------------------------------------------------------------------
# Kernels for filtering, smoothing and stochastics simulations        
# -----------------------------------------------------------------------------
class Kernel:    
    
    __filter_boundary = True
    __kernel_function = None
    __support = None
    
    def __init__(self, function, support):
        self.function = Kernel.__kernel_function
        self.support = support
    
    def setFilterBoundary(self, bool):
        self.__filter_boundary = bool
        
    def filterBoundary(self):
        return self.__filter_boundary
    
    def setFunction(self, function):
        self.__kernel_function = function
        
    def getFunction(self):
        return self.__kernel_function
        
    def plot(self, append=False):
        dh = self.support/500.0
        h = np.arange(-self.support, self.support, dh)
        y = self.evaluate(h)
        plt.plot(h, y, 'b-')
        if not append:
            plt.show()
        
    def evaluate(self, x):
        f_support = lambda x : self.__kernel_function(x)*(abs(x) <= self.support)
        vfunc = np.vectorize(f_support)
        output = vfunc(x)
        if output.shape == ():
            return float(output)
        return output
    
    def toSlidingWindow(self):
        if self.support < 1:
            sys.exit("Error: kernel size must be > 1 to be transformed to sliding window")
        size = 2*(int)(self.support)+1
        values = [0]*size
        center = size/2.0
        norm = 0
        for i in range(size):
            x = center-i-0.5
            values[i] = self.evaluate(x)
            norm += values[i]
        for i in range(size):
            values[i] /= norm
        return values
    

class DiracKernel(Kernel):    
    def __init__(self):
        f = lambda x : 1*(abs(x)==0)
        self.setFunction(f)
        self.support = 500   # Arbitrary value for plot
    def __str__(self):
        return "Dirac kernel"
    
class UniformKernel(Kernel):    
    def __init__(self, size):
        f = lambda x : 1*(abs(x) <= size)/(2*size)
        self.setFunction(f)
        self.support = 2*size
    def __str__(self):
        return "Uniform kernel (width=" + str(self.support) + ")"
        
class TriangularKernel(Kernel):    
    def __init__(self, size):
        f = lambda x : (size-abs(x))*(abs(x) <= size)/(size**2)
        self.setFunction(f)
        self.support = 1.5*size
    def __str__(self):
        return "Triangular kernel (width=" + str(self.support/1.5) + ")"
    
class GaussianKernel(Kernel):    
    def __init__(self, sigma):
        f = lambda x : math.exp(-0.5*(x/sigma)**2)/(sigma*math.sqrt(2*math.pi))
        self.setFunction(f)
        self.support = 3*sigma
    def __str__(self):
        return "Gaussian kernel (sigma=" + str(self.support/3) + ")"
        
class ExponentialKernel(Kernel):    
    def __init__(self, sigma):
        f = lambda x : math.exp(-abs(x)/sigma)/(2*sigma)
        self.setFunction(f)
        self.support = 3*sigma        
    def __str__(self):
        return "Exponential kernel (tau=" + str(self.support/3) + ")"
        
class EpanechnikovKernel(Kernel):    
    def __init__(self, size):
        f = lambda x : 3/4*(1-(x/size)**2)*(abs(x) <= size)/size
        self.setFunction(f)
        self.support = 1.5*size    
    def __str__(self):
        return "Epanechnikov kernel (width=" + str(self.support/1.5) + ")"        
        
class SincKernel(Kernel):    
    def __init__(self, size):
        scale = 0.1*size
        f = lambda x : scale*math.sin((x+1e-300)/scale)/(x+1e-300)/(math.pi*scale)
        self.setFunction(f)
        self.support = 3*size    
    def __str__(self):
        return "Sinc kernel (width=" + str(self.support/3) + ")"



# ---------------------------------------------------------
# Non-parametric estimator of Kernel based on GPS tracks.
# The experimental covariogram kernel is initialized with 
# a maximal scope dmax and an optional resolution (both 
# given in ground units as a distance along curvilinear 
# abscissa or traks. The comparison between pairs of tracks 
# is performed with either Nearest Neighbor (NN) or Dynamic 
# Time Warping (DTM) method. Some tests are still to be 
# conducted to determine which one is more suitable for a 
# robust covariance estimation. If no resolution is input, 
# the covariogram is estimated in 30 points as a default 
# value. The covariogram is incrementally estimated with 
# each data input with addSamples(track_collection) or 
# addTrackPair(track1, track2). Note that track collection 
# input into addSamples must contain at least two tracks.
# ---------------------------------------------------------
# Once an experimental covariogram has been estimated, it 
# is possible to fit a parametric estimation on a one of 
# the kernel models provided above (except UniformKernel 
# which is not a positive-definite function). 
# The estimation is performed with fit(kernel) function. 
# The fitted kernel is returned as standard output.
# ---------------------------------------------------------
class ExperimentalKernel:
    
    def __init__(self, dmax, method="DTW", r=None):
        import tracklib.algo.Comparison as Comparison
        self.dmax = dmax
        self.method = method
        self.r = r
        if r is None:
            r = int(self.dmax/30.0)+1
        N = int(dmax/r)+1
        self.GAMMA = [0]*N
        self.COUNT = [0]*N
        self.H = [0]*N 
        for i in range(N):
            self.H[i] = i*r

    def addSamples(self, trackCollection): 
        N = trackCollection.size()
        for i in range(N-1):
            track1 = trackCollection[i]
            for j in range(i+1,N): 
                track2 = trackCollection[j]
                self.addTrackPair(track1, track2)
        return 0

    def addTrackPair(self, track1, track2):
        track1.compute_abscurv()
        profile = Comparison.differenceProfile(track1, track2, self.method, False, p=4)
        N = len(profile)
        for i in range(N-1):
            si = track1.getObsAnalyticalFeature("abs_curv", i)
            yi = profile.getObsAnalyticalFeature("diff", i) 
            for j in range(i+1,N):
                sj = track1.getObsAnalyticalFeature("abs_curv", j)
                yj = profile.getObsAnalyticalFeature("diff", j) 
                d =  abs(si-sj) 
                idx = int(d/self.r)
                if idx >= len(self.GAMMA):
                    continue
                self.GAMMA[idx] += (yi-yj)**2
                self.COUNT[idx] +=  1

    def __getGamma(self, scale=1):
        x = self.GAMMA
        for i in range(len(x)):
            if self.COUNT[i] != 0:
                x[i] /= self.COUNT[i]
        gamma_max = np.max(x)
        for i in range(len(x)):
             x[i] = (gamma_max-x[i])*scale	
        return x

    def plot(self, sym='k+'):
        gamma = self.__getGamma(0.02)
        N = len(gamma)
        x = [i * (-1) for i in list(reversed(self.H))] + self.H
        y = list(reversed(gamma)) + gamma 
        plt.plot(x, y, sym)









			