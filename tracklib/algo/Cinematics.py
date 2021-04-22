# --------------------------- Cinematics --------------------------------------
# Class to manage cinematic computations on GPS tracks
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