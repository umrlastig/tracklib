"""
Kernels for filtering        
"""

import math
import matplotlib.pyplot as plt
import numpy as np
import sys

# -----------------------------------------------------------------------------
#  Kernels for filtering        
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
        
    def plot(self):
        dh = self.support/500.0
        h = np.arange(-self.support, self.support, dh)
        y = self.evaluate(h)
        plt.plot(h, y, 'b-')
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