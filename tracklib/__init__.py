# -*- coding: utf-8 -*-

#__version__ = '0.3'

#import matplotlib.pyplot as plt


__version__ = '0.5.1'


from tracklib.core import *
from tracklib.util import *
from tracklib.algo import *
#from tracklib.io import *




"""
from tracklib.core.ObsCoords import ENUCoords, GeoCoords, ECEFCoords
from tracklib.core.ObsTime import ObsTime
from tracklib.core.Obs import Obs
from tracklib.core.Track import Track
from tracklib.core.TrackCollection import TrackCollection
import tracklib.core.Utils as utils
from tracklib.io.TrackFormat import TrackFormat

from tracklib.io.TrackReader import TrackReader
"""

# -----------------------------------------------------------------------------
#   LOGGING
#from logging.config import fileConfig
#from os import path

#tracklib_path = path.dirname(path.abspath(__file__))
#resources_path = path.join(tracklib_path, "../resources/")
#log_file_path = path.join(resources_path, 'logging_config.ini')
#fileConfig(log_file_path)



# -----------------------------------------------------------------------------
#

#from .core.Coords import GeoCoords, ENUCoords, ECEFCoords
#from .core.GPSTime import GPSTime


#from tracklib.algo.Interpolation import ALGO_LINEAR, MODE_SPATIAL




#from .core.Track import Track


#from .core.core_utils import * 
#from .algo.AlgoAF import *


#from .core.Kernel import DiracKernel, UniformKernel, TriangularKernel
#from .core.Kernel import GaussianKernel, ExponentialKernel, EpanechnikovKernel
#from .core.Kernel import SincKernel

#from .core.Operator import Operator

#from .io.GpxReader import GpxReader
#from .io.FileReader import FileReader

#from .core_Interpolation import resample, gaussian_process, prepareTimeSampling, synchronize
#from .core_Simplification import simplify, visvalingam, douglas_peucker
#from .core_Grid import Grid
#from .core_Operator import UnaryOperator, BinaryOperator, UnaryVoidOperator, BinaryVoidOperator, ScalarOperator, ScalarVoidOperator
#from .core_Operator import Differentiator, Integrator, Identity
#from .core_Operator import Log, Exp, Sign, Diode, Sqrt, Square, Normalizer, Debiaser, Rectifier, Inverter, ShiftLeft, ShiftRight
#from .core_Operator import Convolution, PointwiseEqualer, Renormalizer, Derivator, Power, Divider, Multiplier, Substracter, Adder
#from .core_Operator import Mad, Rmse, Mse, StdDev, Variance, Averager, Sum, Zeros, Median, Argmax, Argmin, Max, Min
#from .core_Operator import Equal, LInfDiff, L2Diff, L1Diff, L0Diff, Correlator, Covariance
#from .core_Operator import Aggregate
#from .core_Operator import Random, Filter_FFT, Filter, Apply, Thresholder, ScalarPower, ScalarDivider, ScalarMuliplier, ScalarAdder, Shift
#from .core_Operator import Operator
#from .core_Operator import Kernel, DiracKernel, UniformKernel, TriangularKernel, GaussianKernel, ExponentialKernel, EpanechnikovKernel, SincKernel


#__all__ = ['GeoCoords', 'ENUCoords', 'ECEFCoords',
#		   'GPSTime', 'Obs', 'Track',
#          'resample', 'gaussian_process', 'prepareTimeSampling', 'synchronize',
#		   'simplify', 'visvalingam', 'douglas_peucker', 'Grid',
#		   'UnaryOperator', 'BinaryOperator', 'UnaryVoidOperator', 'BinaryVoidOperator',
#		   'ScalarOperator', 'ScalarVoidOperator',
#		   'Differentiator', 'Integrator', 'Identity',
#		   'Log', 'Exp', 'Sign', 'Diode', 'Sqrt', 'Square', 'Normalizer', 'Debiaser', 'Rectifier', 'Inverter', 'ShiftLeft', 'ShiftRight',
#		   'Convolution', 'PointwiseEqualer', 'Renormalizer', 'Derivator', 'Power', 'Divider', 'Multiplier', 'Substracter', 'Adder',
#		   'Mad', 'Rmse', 'Mse', 'StdDev', 'Variance', 'Averager', 'Sum', 'Zeros', 'Median', 'Argmax', 'Argmin', 'Max', 'Min',
#		   'Aggregate',
#		   'Equal', 'LInfDiff', 'L2Diff', 'L1Diff', 'L0Diff', 'Correlator', 'Covariance',
#		   'Random', 'Filter_FFT', 'Filter', 'Apply', 'Thresholder', 'ScalarPower', 'ScalarDivider', 'ScalarMuliplier', 'ScalarAdder', 'Shift',
#		   'Operator',
#		   'Kernel', 'DiracKernel', 'UniformKernel', 'TriangularKernel', 'GaussianKernel',
#		   'ExponentialKernel', 'EpanechnikovKernel', 'SincKernel']
