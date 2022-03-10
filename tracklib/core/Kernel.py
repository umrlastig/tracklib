"""
Kernels for filtering, smoothing and stochastics simulations       
"""

# For type annotation
from __future__ import annotations   
from typing import Any, Union
from collections.abc import Callable

import sys
import math
from typing import Callable
import numpy as np
import matplotlib.pyplot as plt

from tracklib.core.TrackCollection import TrackCollection


class Kernel:
    """Generic kernel class"""

    __filter_boundary = True  #: TODO
    __kernel_function = None  #: TODO
    __support = None  #: TODO

    def __init__(self, function: Callable[[float], float], support: float):   
        """Kernel constructor

        :param function: Kernel function
        :param support: Kernel support
        """
        self.function = Kernel.__kernel_function
        self.support = support

    def setFilterBoundary(self, bool: bool):   
        """Set filter boundary

        :param bool: TODO
        """
        self.__filter_boundary = bool

    def filterBoundary(self) -> bool:   
        """Return the `filterBoundary` parameter value

        :return: `filterBoundary` value
        """
        return self.__filter_boundary

    def setFunction(self, function: Callable[[float], float]):   
        """Set the function used by Kernel

        :param function: A kernel function
        """
        self.__kernel_function = function

    def getFunction(self) -> Callable[[float], float]:   
        """Return the function used by the kernel

        :return: A kernel function
        """
        return self.__kernel_function

    def plot(self, append: bool = False):   
        """Plot the kernel

        :param append: TODO
        """
        dh = self.support / 500.0
        h = np.arange(-self.support, self.support, dh)
        y = self.evaluate(h)
        plt.plot(h, y, "b-")
        if not append:
            plt.show()

    def evaluate(self, x: float) -> float:   
        """Evaluate the kernel for a given value

        :param x: Value to evaluate
        :retun: Kernel value
        """
        f_support = lambda x: self.__kernel_function(x) * (abs(x) <= self.support)
        vfunc = np.vectorize(f_support)
        output = vfunc(x)
        if output.shape == ():
            return float(output)
        return output

    def toSlidingWindow(self) -> list[int]:   
        """Transform the kernel in a sliding windows

        :return: A sliding windows
        """
        if self.support < 1:
            sys.exit(
                "Error: kernel size must be > 1 to be transformed to sliding window"
            )
        size = 2 * (int)(self.support) + 1
        values = [0] * size
        center = size / 2.0
        norm = 0
        for i in range(size):
            x = center - i - 0.5
            values[i] = self.evaluate(x)
            norm += values[i]
        for i in range(size):
            values[i] /= norm
        return values


class DiracKernel(Kernel):
    """Define a DiracKernel"""

    def __init__(self):
        """Constructor of a dirac kernel"""

        f = lambda x: 1 * (abs(x) == 0)
        self.setFunction(f)
        self.support = 500  # Arbitrary value for plot

    def __str__(self) -> str:   
        """Print the kernel type"""
        return "Dirac kernel"


class UniformKernel(Kernel):
    """Define a unifomr kernel"""

    def __init__(self, size: float):   
        """Constructor of a Uniform kernel

        The kernel's function is :

        .. math::

            f(x)=\\frac{1}{2 \\cdot s}

        For a :math:`\|x\| \leq 1` support

        :param size: The size (:math:`s`) of the kernel
        """
        f = lambda x: 1 * (abs(x) <= size) / (2 * size)
        self.setFunction(f)
        self.support = 2 * size

    def __str__(self) -> str:   
        """Print the kernel type"""
        return "Uniform kernel (width=" + str(self.support) + ")"


class TriangularKernel(Kernel):
    """Define a triangular kernel"""

    def __init__(self, size: float):   
        """Constructor of triangular Kernel

        The kernel's function is :

        .. math::

            f(x)= \\frac{s - \|x\|}{s^2}

        For a :math:`\|x\| \leq 1` support

        :param size: The size (:math:`s`) of the kernel
        """
        f = lambda x: (size - abs(x)) * (abs(x) <= size) / (size ** 2)
        self.setFunction(f)
        self.support = 1.5 * size

    def __str__(self) -> str:   
        """Print the kernel type"""
        return "Triangular kernel (width=" + str(self.support / 1.5) + ")"


class GaussianKernel(Kernel):
    """Define a Gaussian Kernel"""

    def __init__(self, sigma: float):   
        """Constructor of Gaussian kernel

        The kernel's function is :

        .. math::

            f(x)=\\frac{e^{-0.5 \\cdot \\left(x/\sigma \\right)^2}}
            {\\sigma \\cdot \\sqrt{2 \\cdot \\pi}}

        :param sigma: The sigma value (:math:`\sigma`) for the kernel
        """
        f = lambda x: math.exp(-0.5 * (x / sigma) ** 2) / (
            sigma * math.sqrt(2 * math.pi)
        )
        self.setFunction(f)
        self.support = 3 * sigma

    def __str__(self) -> str:   
        """Print the kernel type"""
        return "Gaussian kernel (sigma=" + str(self.support / 3) + ")"


class ExponentialKernel(Kernel):
    """Define an Exponential Kernel"""

    def __init__(self, sigma: float):   
        """Constructor of Exponential Kernel

        The Kernel function is:

            .. math::

                f(x) = \\frac{e^{-\|x\| / \sigma}}{2 \cdot \sigma}

        :param sigma: The sigma value (:math:`\\sigma`) for the kernel

        """
        f = lambda x: math.exp(-abs(x) / sigma) / (2 * sigma)
        self.setFunction(f)
        self.support = 3 * sigma

    def __str__(self) -> str:   
        """Print the kernel type"""
        return "Exponential kernel (tau=" + str(self.support / 3) + ")"


class EpanechnikovKernel(Kernel):
    """Define a Epanechnikov Kernel"""

    def __init__(self, size: float):   
        """Constructor of a Epanechnikov Kernel

        The kernel function is :

            .. math::

                f(x) = \\frac{3}{4} \cdot \\left(1 - \\left( \\frac{x}{s} \\right) ^2 \\right)
                \cdot \\frac{1}{s}

        For a :math:`\|x\| \leq 1` support

        :param size: The size parameter (:math:`s`) for the kernel

        """
        f = lambda x: 3 / 4 * (1 - (x / size) ** 2) * (abs(x) <= size) / size
        self.setFunction(f)
        self.support = 1.5 * size

    def __str__(self) -> str:   
        """Print the kernel type"""
        return "Epanechnikov kernel (width=" + str(self.support / 1.5) + ")"


class SincKernel(Kernel):
    """Define a Sinc Kernel"""

    def __init__(self, size: float):   
        """Constructor of a Sinc Kernel

        The kernel function is :

            .. math::

                f(x) = S \cdot \sin \left( \\frac{x + \epsilon}{s} \\right)
                \cdot \\frac{1}{x + \epsilon}
                \cdot \\frac{1}{\pi \cdot S}

        With :math:`S` the scale (:math:`S = s / 10`) and :math:`\epsilon` a minimal
        non nul value

        :param s: The size parameter (:math:`s`) for the kernel
        """
        scale = 0.1 * size
        f = (
            lambda x: scale
            * math.sin((x + 1e-300) / scale)
            / (x + 1e-300)
            / (math.pi * scale)
        )
        self.setFunction(f)
        self.support = 3 * size

    def __str__(self) -> str:   
        """Print the kernel type"""
        return "Sinc kernel (width=" + str(self.support / 3) + ")"


class ExperimentalKernel:
    """Non-parametric estimator of Kernel based on GPS tracks.

    The experimental covariogram kernel is initialized with a maximal scope
    dmax and an optional resolution, both given in ground units as a distance
    along curvilinear abscissa or traks. The comparison between pairs of tracks
    is performed with either Nearest Neighbor (NN) or Dynamic Time Warping (DTM)
    method. Some tests are still to be conducted to determine which one is more
    suitable for a robust covariance estimation. If no resolution is input,
    the covariogram is estimated in 30 points as a default value. The covariogram
    is incrementally estimated with each data input with addSamples
    (track_collection) or addTrackPair(track1, track2). Note that track collection
    input into addSamples must contain at least two tracks.

    Once an experimental covariogram has been estimated, it is possible to fit
    a parametric estimation on one of the kernel models provided above (except
    UniformKernel which is not a positive-definite function). The estimation is
    performed with fit(kernel) function.

    The fitted kernel is returned as standard output.
    """

    def __init__(self, dmax: float, method: str = "DTW", r: float = None):   
        """Constructor of Experimental kernel

        :param dmax: TODO
        :param method: TODO
        :param r: TODO
        """
        import tracklib.algo.Comparison as Comparison

        self.dmax = dmax
        self.method = method
        if r is None:
            r = int(self.dmax / 30.0) + 1
        self.r = r
        N = int(dmax / r) + 1
        self.GAMMA = [0] * N
        self.COUNT = [0] * N
        self.H = [0] * N
        for i in range(N):
            self.H[i] = i * r

    def addTrackPair(self, track1, track2):
        """TODO"""
        self.addTrackCollection(TrackCollection([track1, track2]))

    def addTrackCollection(self, trackCollection, verbose=False):
        """TODO"""
        import tracklib.algo.Comparison as Comparison  # <- Assez moche... A voir comment resoudre

        N = trackCollection.size()
        for i in range(N - 1):
            print("Reference set on track [" + str(i + 1) + "/" + str(N - 1) + "]")
            t1 = trackCollection[i]
            for j in range(i + 1, N):
                t2 = trackCollection[j]
                pf = Comparison.differenceProfile(
                    t1, t2, mode=self.method, ends=True, p=1, verbose=verbose
                )
                self.addDifferenceProfile(pf)

    def addDifferenceProfile(self, profile: Any):   
        """add a Difference Profile

        :param profile: TODO
        """
        N = len(profile)
        for i in range(N - 1):
            si = profile.getObsAnalyticalFeature("abs_curv", i)
            yix = profile.getObsAnalyticalFeature("ex", i)
            yiy = profile.getObsAnalyticalFeature("ey", i)
            for j in range(i + 1, N):
                sj = profile.getObsAnalyticalFeature("abs_curv", j)
                yjx = profile.getObsAnalyticalFeature("ex", j)
                yjy = profile.getObsAnalyticalFeature("ey", j)
                d = abs(si - sj)
                idx = int(d / self.r)
                if idx >= len(self.GAMMA):
                    continue
                self.GAMMA[idx] += (yix - yjx) ** 2 + (yiy - yjy) ** 2
                self.COUNT[idx] += 2

    def __getGamma(self, scale: int = 1) -> float:   
        """Return gamma value

        :param scale: Scale value
        :return: Gamma value
        """
        x = self.GAMMA
        for i in range(len(x)):
            if self.COUNT[i] != 0:
                x[i] /= self.COUNT[i]
        for i in range(len(x)):
            x[i] = x[i] * scale
        return x

    def plot(self, sym="k+"):
        """Plot the kernel"""
        gamma = self.__getGamma()
        N = len(gamma)
        x = [i * (-1) for i in list(reversed(self.H))] + self.H
        y = list(reversed(gamma)) + gamma
        y = (np.max(y) - y)/np.max(y)
        plt.plot(x, y, sym)
