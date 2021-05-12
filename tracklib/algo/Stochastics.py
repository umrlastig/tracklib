# --------------------------- Stochastics -------------------------------------
# Class to manage random operations of GPS tracks
# -----------------------------------------------------------------------------

import sys
import random
import numpy as np
import matplotlib.pyplot as plt

from tracklib.core.Obs import Obs

from tracklib.core.Kernel import DiracKernel

import tracklib.core.Utils as utils
import tracklib.algo.Analytics as Analytics
import tracklib.algo.Interpolation as Interpolation
import tracklib.core.Kernel as Kernel

DISTRIBUTION_NORMAL = 1
DISTRIBUTION_UNIFORM = 2
DISTRIBUTION_LAPLACE = 3

class NoiseProcess:

    def __init__(self, amps=None, kernels=None, distribution=DISTRIBUTION_NORMAL):
		
        if amps is None:
           self.amplitudes = [1]
           self.kernels = [DiracKernel()]
        else:
           self.amplitudes = utils.listify(amps)
           self.kernels = utils.listify(kernels)

        self.distribution = distribution

        if len(self.amplitudes) != len(self.kernels): 
            print("Error: amplitude and kernel lists must have same size in NoiseProcess")
            exit()

    def __str__(self):
        output = "Noise process: "
        for i in range(len(self.amplitudes)):
            output += "[" +str(self.amplitudes[i])+"-unit-amplitude "+str(self.kernels[i])+"] "
            if (i < len(self.amplitudes)-1):
                output += "\n + "
        return output
		
    def noise(self, track):
        return noise(track, self.amplitudes, self.kernels, self.distribution) 
		
    def plot(self):
        dh = self.kernels[0].support/500.0
        h = np.arange(-self.kernels[0].support, self.kernels[0].support, dh)
        y = self.amplitudes[0]*self.kernels[0].evaluate(h)/self.kernels[0].evaluate(0)
        for i in range(1,len(self.amplitudes)):
            y =  y + self.amplitudes[i]*self.kernels[i].evaluate(h)/self.kernels[i].evaluate(0)
        plt.plot(h, y, 'b-')
        plt.show()
        
def seed(integer):
    random.seed(integer)
    np.random.seed(integer)

def gaussian_process(self, timestamps, kernel, factor=1.0, sigma=0.0, cp_var=False):
    '''Track interpolation and smoothing with Gaussian Process (GP)
    self: a track to smooth (not modified by this function)
    timestamps: points where interpolation must be computed. May be
    a list of timestamps, a track or a number of seconds
    kernel: a symetric function k(xi-xj) describing the statistical
    similarity between the coordinates X,Y,Z taken in two points : 
                    k(t2-t1) = Cov(X(t1), X(t2))
                    k(t2-t1) = Cov(Y(t1), Y(t2))
                    k(t2-t1) = Cov(Z(t1), Z(t2))
    factor: unit factor of variance if the kernel must be scaled
    sigma: observation noise standard deviation (in coords units)
    cp_var: compute covariance matrix and store pointwise sigmas
    returns: interpolated/smoothed track (without AF)'''
    
    return Interpolation.gaussian_process(self, timestamps, kernel, factor, sigma, cp_var)
	
def randomColor():
    return [random.random(),random.random(),random.random()]
	
def noise(track, sigma=[1], kernel=[Kernel.DiracKernel()], distribution=DISTRIBUTION_NORMAL):
    '''Track noising with Cholesky factorization of gaussian 
    process covariance matrix: h(x2-x1)=exp(-((x2-x1)/scope)**2)
    If X is a gaussian white noise, Cov(LX) = L^t*L => if L is a 
    Cholesky factorization of a semi-postive-definite matrix S,
    then Cov(LX) = L^T*L = S and Y=LX has S as covariance matrix.
    track: the track to be smoothed (input track is not modified)
    sigma: noise amplitude(s) (in observation coordinate units)
    kernel: noise autocovariance function(s)'''
	
    sigma = utils.listify(sigma)
    kernel = utils.listify(kernel)       

    if len(sigma) != len(kernel):
        sys.exit("Error: amplitude and kernel arrays must have same size in 'noise' function")
    
    N = track.size()
    track.compute_abscurv()
    
    noised_track = track.copy()
    
    for n in range(len(sigma)):

        S = track.getAnalyticalFeature(Analytics.BIAF_ABS_CURV)
        SIGMA_S = utils.makeCovarianceMatrixFromKernel(kernel[n], S, S)
        SIGMA_S += np.identity(N)*1e-12
        SIGMA_S *= sigma[n]**2/SIGMA_S[0,0]
    
        # Cholesky decomposition
        L = np.linalg.cholesky(SIGMA_S)
   
        # Noise simulation
        if distribution == DISTRIBUTION_NORMAL:
            Xx = np.random.normal(0.0, 1.0, N)
            Xy = np.random.normal(0.0, 1.0, N)
            Xz = np.random.normal(0.0, 1.0, N)
        if distribution == DISTRIBUTION_UNIFORM:
            Xx = np.random.uniform(-1.73205, 1.73205, N)
            Xy = np.random.uniform(-1.73205, 1.73205, N)
            Xz = np.random.uniform(-1.73205, 1.73205, N)
        if distribution == DISTRIBUTION_LAPLACE:
            Xx = np.random.laplace(0.0, 0.5, N)
            Xy = np.random.laplace(0.0, 0.5, N)
            Xz = np.random.laplace(0.0, 0.5, N)
        Yx = np.matmul(L, Xx)
        Yy = np.matmul(L, Xy)
        Yz = np.matmul(L, Xz)
 
        # Building noised track
        for i in range(N):
            pt = noised_track.getObs(i).position
            pt.setX(pt.getX()+Yx[i])
            pt.setY(pt.getY()+Yy[i])
            pt.setZ(pt.getZ()+Yz[i])
            obs = Obs(pt, track.getObs(i).timestamp)
        
    return noised_track
        
    
def randomizer(input, f, sigma=[7], kernel=[Kernel.GaussianKernel(650)], N=10):
    '''Randomizing traces for sensitivity analysis on output f
    input: a track, or list of tracks to be randomized
    f: a function taking a list of tracks as input 
    sigma: noise amplitude (in observation coordinate units)
    N: number of simulations to generate (default is 100)
    scope_s: spatial autocorrelation scope (measured along track 
        curvilinear abscissa in observation coordinate units)'''
    
    noised_output = []
    
    if not isinstance(input, list):
        input = [input]
        
    for i in range(N):
        noised_input = []
        print("  Randomizing tracks:", ('{}/'+(str)(N)+'\r').format(i+1), end="")
        for j in range(len(input)):
            noised_track = input[j].noise(sigma, kernel)
            noised_input.append(noised_track)    
        noised_output.append(f(noised_input))
    print("")

    return noised_output
        

