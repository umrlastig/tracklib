"""Class to manage random operations of GPS tracks"""

import sys
import random
import numpy as np
import matplotlib.pyplot as plt

from tracklib.core.Obs import Obs
from tracklib.core.Kernel import DiracKernel
from tracklib.core.TrackCollection import TrackCollection

import tracklib.core.Utils as utils
import tracklib.core.Kernel as Kernel

from tracklib.algo.Analytics import BIAF_ABS_CURV
from tracklib.algo.Interpolation import (
    gaussian_process as interpolation_gaussian_process,
)


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

    def __init__(self, amps=None, kernels=None, distribution=DISTRIBUTION_NORMAL):
        """TODO"""

        if amps is None:
            self.amplitudes = [1]
            self.kernels = [DiracKernel()]
        else:
            self.amplitudes = utils.listify(amps)
            self.kernels = utils.listify(kernels)

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

    def noise(self, track, N=1):
        """TODO"""
        if N == 1:
            return noise(track, self.amplitudes, self.kernels, self.distribution)
        else:
            collection = TrackCollection()
            for i in range(N):
                collection.addTrack(
                    noise(track, self.amplitudes, self.kernels, self.distribution)
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


def seed(integer):
    """TODO"""
    random.seed(integer)
    np.random.seed(integer)


def gaussian_process(self, timestamps, kernel, factor=1.0, sigma=0.0, cp_var=False):
    """Track interpolation and smoothing with Gaussian Process (GP)

    :param timestamps: points where interpolation must be computed. May be a list of
        timestamps, a track or a number of seconds
    :param kernel: a symetric function k(xi-xj) describing the statistical similarity
        between the coordinates X,Y,Z taken in two points :

        .. math::

            k(t2-t1) = Cov(X(t1), X(t2))

            k(t2-t1) = Cov(X(t1), X(t2))

            k(t2-t1) = Cov(Z(t1), Z(t2))


    :param factor: unit factor of variance if the kernel must be scaled
    :param sigma: observation noise standard deviation (in coords units)
    :param cp_var: compute covariance matrix and store pointwise sigmas

    :return: interpolated/smoothed track (without AF)"""

    return interpolation_gaussian_process(
        self, timestamps, kernel, factor, sigma, cp_var
    )


def randomColor():
    """TODO"""
    return [random.random(), random.random(), random.random()]


def noise(
    track, sigma=[1], kernel=[Kernel.DiracKernel()], distribution=DISTRIBUTION_NORMAL
):
    """Track noising with Cholesky factorization of gaussian process covariance matrix:

    .. math::

        h(x2-x1)=\\exp-\\left(\\frac{x2-x1}{scope}\\right)^2

    If :math:`X` is a gaussian white noise, :math:`Cov(LX) = L^t*L` => if :math:`L` is a
    Cholesky factorization of a semi-postive-definite matrix :math:`S`,
    :math:`then Cov(LX) = L^T*L = S` and :math:`Y=LX`` has :math:`S` as covariance matrix.

    :param track: the track to be smoothed (input track is not modified)
    :param sigma: noise amplitude(s) (in observation coordinate units)
    :param kernel: noise autocovariance function(s)"""

    sigma = utils.listify(sigma)
    kernel = utils.listify(kernel)

    if len(sigma) != len(kernel):
        sys.exit(
            "Error: amplitude and kernel arrays must have same size in 'noise' function"
        )

    N = track.size()
    track.compute_abscurv()

    noised_track = track.copy()

    for n in range(len(sigma)):

        S = track.getAnalyticalFeature(BIAF_ABS_CURV)
        SIGMA_S = utils.makeCovarianceMatrixFromKernel(kernel[n], S, S)
        SIGMA_S += np.identity(N) * 1e-12
        SIGMA_S *= sigma[n] ** 2 / SIGMA_S[0, 0]

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
            pt.setX(pt.getX() + Yx[i])
            pt.setY(pt.getY() + Yy[i])
            pt.setZ(pt.getZ() + Yz[i])
            obs = Obs(pt, track.getObs(i).timestamp)

    return noised_track


def randomizer(input, f, sigma=[7], kernel=[Kernel.GaussianKernel(650)], N=10):
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
