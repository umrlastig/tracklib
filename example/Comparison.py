import os
import sys
import math
import random
import numpy as np
import matplotlib.pyplot as plt

from tracklib.core.Operator import Operator
from tracklib.io.FileReader import FileReader
from tracklib.io.FileWriter import FileWriter
from tracklib.core.GPSTime import GPSTime
from tracklib.core.Track import Track
from tracklib.core.Coords import ECEFCoords
from tracklib.core.Coords import GeoCoords
from tracklib.core.Coords import ENUCoords

from tracklib.algo.Selection import TrackConstraint
import tracklib.algo.Stochastics as Stochastics
import tracklib.algo.Synthetics as Synthetics
import tracklib.algo.Geometrics as Geometrics
import tracklib.algo.Comparison as Comparison
import tracklib.algo.Cinematics as Cinematics
import tracklib.algo.Dynamics as Dynamics
import tracklib.algo.Interpolation as Interpolation
import tracklib.algo.Simplification as Simplification
import tracklib.algo.Segmentation as Segmentation
import tracklib.algo.Mapping as Mapping
import tracklib.algo.Filtering as Filtering
from tracklib.algo.Dynamics import Kalman
from tracklib.algo.Stochastics import NoiseProcess

from tracklib.io.KmlWriter import KmlWriter
from tracklib.core.Coords import ENUCoords

from tracklib.io.GpxWriter import GpxWriter
from tracklib.io.GpxReader import GpxReader
from tracklib.core.TrackCollection import TrackCollection
from tracklib.core.Kernel import DiracKernel
from tracklib.core.Kernel import GaussianKernel
from tracklib.core.Kernel import ExponentialKernel
from tracklib.core.Kernel import ExperimentalKernel

from tracklib.core.Obs import Obs
import tracklib.core.Plot as Plot
from tracklib.core.Network import Node
from tracklib.core.Network import Edge
from tracklib.core.Network import Network
from tracklib.io.NetworkReader import NetworkReader

# -----------------------------------------------------------------------
# Example 0: comparison between two tracks
# Mode:
#   - 'NN'   :  Fast but sometimes incorrect + artifacts problem
#   - 'DTW'  :  Very slow but optimal 
#   - 'FDTW' :  Fast and nearly optimal for well-behaved inputs
# -----------------------------------------------------------------------

def example0(mode='FDTW'):

    Stochastics.seed(1234)

    track1 = Synthetics.generate(2e-1, dt=30)
    track2 = track1.noise(10, GaussianKernel(25))
	
    track1.plot('r-')
    track2.plot('r-')
	
    profile = Comparison.differenceProfile(track2, track1, mode, p=2)
    Comparison.plotDifferenceProfile(profile, track1)
	
    plt.show()

	
	

# -----------------------------------------------------------------------
# Example 1: central profile of a track collection
# Mode:
#   - 'NN'   :  Fast but sometimes incorrect + artifacts problem
#   - 'DTW'  :  Very slow but optimal 
#   - 'FDTW' :  Fast and nearly optimal for well-behaved inputs
# N is the number of tracks to generate
# -----------------------------------------------------------------------

def example1(mode='FDTW', N=5):

    track = Synthetics.generate(1e-1, dt=30)
    tracks = NoiseProcess(5, GaussianKernel(5)).noise(track, N)

    central = Comparison.centralTrack(tracks, mode=mode)

    tracks.plot('r-')
    central.plot('b-')
    plt.show()
    