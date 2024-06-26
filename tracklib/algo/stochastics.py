# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Yann Méneroux
Creation date: 1th november 2020

tracklib library provides a variety of tools, operators and 
functions to manipulate GPS trajectories. It is a open source contribution 
of the LASTIG laboratory at the Institut National de l'Information 
Géographique et Forestière (the French National Mapping Agency).
See: https://tracklib.readthedocs.io
 
This software is governed by the CeCILL-C license under French law and
abiding by the rules of distribution of free software. You can  use, 
modify and/ or redistribute the software under the terms of the CeCILL-C
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info". 

As a counterpart to the access to the source code and rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability. 

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or 
data to be ensured and,  more generally, to use and operate it in the 
same conditions as regards security. 

The fact that you are presently reading this means that you have had
knowledge of the CeCILL-C license and that you accept its terms.



Class to manage random operations of GPS tracks

"""

import sys
import random
import numpy as np
import matplotlib.pyplot as plt
#from tracklib.util.exceptions import *

from tracklib.core import (Obs, 
                           listify, 
                           makeCovarianceMatrixFromKernel,
                           DiracKernel, GaussianKernel,
                           TrackCollection)

# gaussian_process
from . import (computeAbsCurv)


DISTRIBUTION_NORMAL = 1
DISTRIBUTION_UNIFORM = 2
DISTRIBUTION_LAPLACE = 3

__KHI_SQUARED_TABLE = [
    # 0.10 	 0.05 	 0.025 	  0.01 	 0.005
    [2.7060, 3.8410, 5.0240, 6.6350, 7.8790],
    [4.6050, 5.9910, 7.3780, 9.2100, 10.597],
    [6.2510, 7.8150, 9.3480, 11.345, 12.838],
    [7.7790, 9.4880, 11.143, 13.277, 14.860],
    [9.2360, 11.070, 12.833, 15.086, 16.750],
    [10.645, 12.592, 14.449, 16.812, 18.548],
    [12.017, 14.067, 16.013, 18.475, 20.278],
    [13.362, 15.507, 17.535, 20.090, 21.955],
    [14.684, 16.919, 19.023, 21.666, 23.589],
    [15.987, 18.307, 20.483, 23.209, 25.188],
    [17.275, 19.675, 21.920, 24.725, 26.757],
    [18.549, 21.026, 23.337, 26.217, 28.300],
    [19.812, 22.362, 24.736, 27.688, 29.819],
    [21.064, 23.685, 26.119, 29.141, 31.319],
    [22.307, 24.996, 27.488, 30.578, 32.801],
    [23.542, 26.296, 28.845, 32.000, 34.267],
    [24.769, 27.587, 30.191, 33.409, 35.718],
    [25.989, 28.869, 31.526, 34.805, 37.156],
    [27.204, 30.144, 32.852, 36.191, 38.582],
    [28.412, 31.410, 34.170, 37.566, 39.997],
    [29.615, 32.671, 35.479, 38.932, 41.401],
    [30.813, 33.924, 36.781, 40.289, 42.796],
    [32.007, 35.172, 38.076, 41.638, 44.181],
    [33.196, 36.415, 39.364, 42.980, 45.559],
    [34.382, 37.652, 40.646, 44.314, 46.928],
    [35.563, 38.885, 41.923, 45.642, 48.290],
    [36.741, 40.113, 43.195, 46.963, 49.645],
    [37.916, 41.337, 44.461, 48.278, 50.993],
    [39.087, 42.557, 45.722, 49.588, 52.336],
    [40.256, 43.773, 46.979, 50.892, 53.672],
]


def khi2cdf(dof, prob=0.05):
    """TODO"""
    if prob == 1:
        return 1e300
    if dof > 30:
        print("Error: khi square distribution limited to 30 degrees of freedom")
        exit(1)
    if (prob > 0.10) or (prob < 0.005):
        print("Error: khi square distribution only defined on [0.005; 0.10]")
        exit(1)
    PROBS = [0.10, 0.05, 0.025, 0.01, 0.005]
    idx = PROBS.index(prob)
    return __KHI_SQUARED_TABLE[dof - 1][idx]


def khi2test(X, SIGMA, prob=0.05):
    """TODO"""
    return X.transpose() @ np.linalg.inv(SIGMA) @ X > khi2cdf(SIGMA.shape[0], prob)


class NoiseProcess:
    """TODO"""
    
    SEED = None

    def __init__(self, amps=None, kernels=None, distribution=DISTRIBUTION_NORMAL):
        """TODO"""

        if amps is None:
            self.amplitudes = [1]
            self.kernels = [DiracKernel()]
        else:
            self.amplitudes = listify(amps)
            self.kernels = listify(kernels)

        self.distribution = distribution

        if len(self.amplitudes) != len(self.kernels):
            print(
                "Error: amplitude and kernel lists must have same size in NoiseProcess"
            )
            exit()

    def __str__(self):
        """TODO"""
        output = "Noise process: "
        for i in range(len(self.amplitudes)):
            output += (
                "["
                + str(self.amplitudes[i])
                + "-unit-amplitude "
                + str(self.kernels[i])
                + "] "
            )
            if i < len(self.amplitudes) - 1:
                output += "\n + "
        return output

    def noise(self, track, N=1, mode='linear', force=False):
        """TODO"""
        if N == 1:
            return noise(track, self.amplitudes, self.kernels, self.distribution, mode=mode, force=force)
        else:
            collection = TrackCollection()
            for i in range(N):
                collection.addTrack(
                    noise(track, self.amplitudes, self.kernels, self.distribution, mode=mode, force=force)
                )
            return collection

    def plot(self):
        """TODO"""
        dh = self.kernels[0].support / 500.0
        h = np.arange(-self.kernels[0].support, self.kernels[0].support, dh)
        y = (
            self.amplitudes[0]
            * self.kernels[0].evaluate(h)
            / self.kernels[0].evaluate(0)
        )
        for i in range(1, len(self.amplitudes)):
            y = y + self.amplitudes[i] * self.kernels[i].evaluate(h) / self.kernels[
                i
            ].evaluate(0)
        plt.plot(h, y, "b-")
        plt.show()


# ----------------------------------------------------------------------
# Method to generate seed for random generation. If no seed is specified 
# the seed is chosen at random at function call, and can then be 
# retrieved with getseed function
# ----------------------------------------------------------------------
def seed(integer = None):
    """
    Initialize the random number generator.
    :param integer: number (optional)
    """
    if integer is None:
        integer = random.randrange(2**32)
    random.seed(integer)
    np.random.seed(integer)
    NoiseProcess.SEED = integer

def getseed():
    return NoiseProcess.SEED


def __randomSampler(N, distribution):
    if distribution == DISTRIBUTION_NORMAL:
        return np.random.normal(0.0, 1.0, N)
    if distribution == DISTRIBUTION_UNIFORM:
        return np.random.uniform(-1.73205, 1.73205, N)
    if distribution == DISTRIBUTION_LAPLACE:
        return np.random.laplace(0.0, 0.5, N)



# Modes for distance computation
MODE_DISTANCE_LINEAR    = 'linear'
MODE_DISTANCE_EUCLIDIAN = 'euclidian'
MODE_DISTANCE_CIRCULAR  = 'circular'

# Modes for direction of noise
MODE_DIRECTION_X     = 4   # 0100
MODE_DIRECTION_Y     = 2   # 0010
MODE_DIRECTION_Z     = 1   # 0001
MODE_DIRECTION_XY    = 6   # 0110
MODE_DIRECTION_YZ    = 3   # 0011
MODE_DIRECTION_XZ    = 5   # 0101
MODE_DIRECTION_XYZ   = 7   # 0111
MODE_DIRECTION_ORTHO = 8   # 1000

# ----------------------------------------------------------------------
# Function to add noise to a Track. A new track is returned. 
# Inputs:
#    - sigma: amplitude of noise (in track coordinate units). 
#    - kernel: a model of kernel (a kernel shape, accepting as parameter 
#      the length of auto-correlation in track coordinate units). Any 
#      object deriving from core.Kernel class is accepted. If kernel 
#      function is not definite-postive, it can be forced as so with 
#      'force' argument set to True ; in that case, all negative 
#      eigen values of the covariance matrix generated from the kernel
#      on the dataset, are thresholded to zero. Example: a kernel model 
#      set to GaussianKernel(200) means that correlation of noise values 
#      on points in the track will follow a gaussian function and that 
#      noise values are started to get decorelated as distance between 
#      points is above 200 m (assuming track coordinate unit is meters).
#      How distance is computed bewteen points is specified in mode 
#      argument.  
#    - distribution: probability distribution of individual noise. Can
#      be one of the three followong models:
#          - DISTRIBUTION_NORMAL (default)
#          - DISTRIBUTION_UNIFORM
#          - DISTRIBUTION_LAPLACE (symetric decreasing exponential)
#    - mode: specifies how distances between points are computed to 
#      generate covariance matrix from kernel. Available modes are:
#		   - MODE_DISTANCE_LINEAR: distance is computed as difference of 
#            curvilinear abscissa on track. The value d(p,q) corresponds 
#            to the distance along the track between points p and q. 
#            This parameter is useful to model spatio-temporal 
#            correlation noise (noise values are getting decorelated 
#            between points in track as much as they are separated by a 
#            a long spatial distance or a long time interval). 
#          - MODE_DISTANCE_EUCLIDIAN: distance d(p,q) is computed as 
#            the 2D euclidian distance between p and q. This models a 
#            noise with purely geometric decorrelation pattern.
#          - MODE_DISTANCE_CIRCULAR: similar to MODE_DISTANCE_LINEAR, 
#            but distance is computed modulo half-length of track. It 
#            is useful to model noise on a loop. 
#    - force: if True, all negative eigen values of covariance matrix 
#      generated from the kernel on the dataset, are thresholded to zero 
#      Enables to consider non definite positive "kernel" model and to 
#      deal with numerical errors in matrice algebraic operations. 
#    - cycle: if True, first and last position of track share same noise 
#      values. Enables to keep consistent noise generation on loops, and 
#      must be used with MODE_DISTANCE_CIRCULAR.
#    - control: an array of tuples to specify point control points on
#      the noise model. Each tuple has the form (i, p) where i is an 
#      integer specifying the index of the point on which the constrain 
#      is enforced and p is an ENUCoords specifying the value of the 
#      point of index i after noise. Note that control points are
#      applied on a per-component basis, i.e. each noise contribution 
#      will be constrained so that point of index i passes through p. 
#      As a default, p=None, means that point of index i should not be 
#      modified by noise. Then, for noising a track (i, None) is 
#      equivalent to (i, track[i].position). For example:
#      [(0, None), [97, ENUCoords(10, 10, 10), (-1, None)] means that: 
#      (1) first point in track (index 0) and last point in track (index
#      -1) must not be modified by noise and (2) that the noise on point
#      of index 97 must be constrained so that noised point has coords 
#      (E = 10, N = 10, U = 10).
#      - direction: the direction in wich noise is applied. Direction is
#      given in the 3D local reference frame, except for special mode 
#      MODE_DIRECTION_ORTHO, where noise is added in an orthonormal 
#      direction with respect to the track.
#      - n: number of noised tracks to generate (default 1). Returns 
#      a TrackCollection otherwise. 
# If multiple noises are to be added to the track, sigma and kernel 
# arguments are given as arrays (array of floats for sigma, and array of 
# kernel models for kernel).
# ----------------------------------------------------------------------
def noise(
    track, sigma=[1], kernel=[DiracKernel()], distribution=DISTRIBUTION_NORMAL, mode=MODE_DISTANCE_LINEAR, force=False, cycle=False, control=[], direction=MODE_DIRECTION_XYZ, n=1
):
    """Track noising with Cholesky factorization of gaussian process covariance matrix:

    .. math::

        h(x2-x1)=\\exp-\\left(\\frac{x2-x1}{scope}\\right)^2

    If :math:`X` is a gaussian white noise, :math:`Cov(LX) = L^t*L` => if :math:`L` is a
    Cholesky factorization of a semi-postive-definite matrix :math:`S`,
    :math:`then Cov(LX) = L^T*L = S` and :math:`Y=LX`` has :math:`S` as covariance matrix.

    :param track: the track to be smoothed (input track is not modified)
    :param sigma: noise amplitude(s) (in observation coordinate units)
    :param kernel: noise autocovariance function(s)
	:param mode: 'linear' (default), 'circular' or 'euclidian'
	:param force: force definite-positive matrix with removal of negative eigen values
    :param control: control points (list of coords) for conditional simulations 
    :param N: number of tracks to generate (returns track collection if N > 1)"""

    if n == 1:
        return __noise(track, sigma, kernel, distribution, mode, force, cycle, control, direction)
    else:
        tracks = TrackCollection()
        for i in range(n):
            tracks.addTrack(__noise(track, sigma, kernel, distribution, mode, force, cycle, control, direction))
        return tracks


def __noise(
    track, sigma=[1], kernel=[DiracKernel()], distribution=DISTRIBUTION_NORMAL, mode='linear', force=False, cycle=False, control=[], direction = MODE_DIRECTION_XYZ
):
    """Track noising with Cholesky factorization of gaussian process covariance matrix:

    .. math::

        h(x2-x1)=\\exp-\\left(\\frac{x2-x1}{scope}\\right)^2

    If :math:`X` is a gaussian white noise, :math:`Cov(LX) = L^t*L` => if :math:`L` is a
    Cholesky factorization of a semi-postive-definite matrix :math:`S`,
    :math:`then Cov(LX) = L^T*L = S` and :math:`Y=LX`` has :math:`S` as covariance matrix.

    :param track: the track to be smoothed (input track is not modified)
    :param sigma: noise amplitude(s) (in observation coordinate units)
    :param kernel: noise autocovariance function(s)
    :param mode: 'linear' (default), 'circular' or 'euclidian'
    :param force: force definite-positive matrix with removal of negative eigen values
    :param control: control points (list of coords) for conditional simulations """

    sigma = listify(sigma)
    kernel = listify(kernel)
    
    if (len(control) > 0):
        if not ('tuple' in str(type(control[0]))):
            control_bis = []
            for cp in control:
                control_bis.append((cp, track[cp].position))
            control = control_bis

    if len(sigma) != len(kernel):
        raise SizeError(
            "Error: amplitude and kernel arrays must have same size in 'noise' function"
        )

    N  = track.size()
    Nc = len(control)
    noised_track = track.copy()
    computeAbsCurv(noised_track)
    Xc = np.zeros(Nc)
    Yc = np.zeros(Nc)
    Zc = np.zeros(Nc)
    
    # Constraints (if any)
    for ip in range(len(control)):
        if (control[ip][1] is not None):
            Xc[ip] = control[ip][1].getX() - track[control[ip][0]].position.getX()
            Yc[ip] = control[ip][1].getY() - track[control[ip][0]].position.getY()
            Zc[ip] = control[ip][1].getZ() - track[control[ip][0]].position.getZ()

    # Loop on kernel models
    for ik in range(len(sigma)):

        # Zero-amplitude case
        if (sigma[ik] == 0):
            continue

        # Building covariance matrix
        SIGMA_S  = makeCovarianceMatrixFromKernel(kernel[ik], noised_track, force=force, mode=mode, control=control)
        SIGMA_S += np.identity(SIGMA_S.shape[0]) * 1e-12
        SIGMA_S *= sigma[ik] ** 2 / SIGMA_S[0, 0]

        # Cholesky decomposition
        L = np.linalg.cholesky(SIGMA_S)
        L22 = L[Nc:  , Nc:  ]
        L11 = L[  :Nc,   :Nc]
        L12 = L[Nc:  ,   :Nc]
        
        # Noise initialization
        Yx = np.zeros((N,))
        Yy = np.zeros((N,))
        Yz = np.zeros((N,))
       
        # Noise simulation
        if (direction in [MODE_DIRECTION_X, MODE_DIRECTION_XY, MODE_DIRECTION_XZ, MODE_DIRECTION_XYZ]):   
            Yx = np.matmul(L22, __randomSampler(N, distribution)) + np.matmul(L12, np.linalg.solve(L11, Xc))
        if (direction in [MODE_DIRECTION_Y, MODE_DIRECTION_XY, MODE_DIRECTION_YZ, MODE_DIRECTION_XYZ]):
            Yy = np.matmul(L22, __randomSampler(N, distribution)) + np.matmul(L12, np.linalg.solve(L11, Yc))
        if (direction in [MODE_DIRECTION_Z, MODE_DIRECTION_YZ, MODE_DIRECTION_XZ, MODE_DIRECTION_XYZ, MODE_DIRECTION_ORTHO]):
            Yz = np.matmul(L22, __randomSampler(N, distribution)) + np.matmul(L12, np.linalg.solve(L11, Zc))
        
        # Building noised track
        if (direction == MODE_DIRECTION_ORTHO):
            for i in range(N-1):
                dE = track[i+1].position.E - track[i].position.E
                dN = track[i+1].position.N - track[i].position.N
                norm = (dE**2 + dN**2)**0.5
                noised_track.getObs(i).position.translate(Yz[i]*dN/norm, -Yz[i]*dE/norm, 0)
            noised_track.getObs(N-1).position.translate(Yz[i]*dN/norm, -Yz[i]*dE/norm, 0)
        else:
            for i in range(N):
                noised_track.getObs(i).position.translate(Yx[i], Yy[i], Yz[i])
           
        if mode == 'circular':
            noised_track.loop()
            
    noised_track.removeAnalyticalFeature("abs_curv")
          
    return noised_track

def randomizer(input, f, sigma=[7], kernel=[GaussianKernel(650)], N=10):
    """Randomizing traces for sensitivity analysis on output `f`

    :param input: a track, or list of tracks to be randomized
    :param f: a function taking a list of tracks as input
    :param sigma: noise amplitude (in observation coordinate units)
    :param N: number of simulations to generate (default is 100)
    :param scope_s: spatial autocorrelation scope (measured along track
        curvilinear abscissa in observation coordinate units)
    """

    noised_output = []

    if not isinstance(input, list):
        input = [input]

    for i in range(N):
        noised_input = []
        print("  Randomizing tracks:", ("{}/" + (str)(N) + "\r").format(i + 1), end="")
        for j in range(len(input)):
            noised_track = input[j].noise(sigma, kernel)
            noised_input.append(noised_track)
        noised_output.append(f(noised_input))
    print("")

    return noised_output

