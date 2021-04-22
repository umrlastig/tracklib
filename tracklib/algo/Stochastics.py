# --------------------------- Stochastics -------------------------------------
# Class to manage random operations of GPS tracks
# -----------------------------------------------------------------------------

import sys
import progressbar
import numpy as np

from tracklib.core.Obs import Obs
from tracklib.core.TrackCollection import TrackCollection
from tracklib.core.Kernel import GaussianKernel

import tracklib.core.Utils as utils
import tracklib.algo.Analytics as Analytics
import tracklib.algo.Geometrics as Geometrics
import tracklib.algo.Interpolation as Interpolation
import tracklib.core.Operator as Operator
import tracklib.core.Kernel as Kernel

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
	
	
def noise(track, sigma=[7], kernel=[Kernel.GaussianKernel(650)]):
    '''Track noising with Cholesky factorization of gaussian 
    process covariance matrix: h(x2-x1)=exp(-((x2-x1)/scope)**2)
    If X is a gaussian white noise, Cov(LX) = L^t*L => if L is a 
    Cholesky factorization of a semi-postive-definite matrix S,
    then Cov(LX) = L^T*L = S and Y=LX has S as covariance matrix.
    track: the track to be smoothed (input track is not modified)
    sigma: noise amplitude(s) (in observation coordinate units)
    kernel: noise autocovariance function(s)'''

    if not isinstance(sigma, list):
        sigma = [sigma]
        
    if not isinstance(kernel, list):
        kernel = [kernel]
        
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
        Xx = np.random.normal(0.0, 1.0, N)
        Xy = np.random.normal(0.0, 1.0, N)
        Xz = np.random.normal(0.0, 1.0, N)
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
        

