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
# Example 0: DTW computation with HMM
# -----------------------------------------------------------------------

def example0():

    track1 = Synthetics.generate(1e-1, dt=30)
    track2 = track1.noise(10, GaussianKernel(25))

	
    S = lambda track, k: [p for p in range(max(0,k-30),  min(len(track2)-1, k+30))]
    #S = lambda t, k: [p for p in range(0, len(track2)-1)]
    Q = lambda i,j,k,t: (j<i+30)*(j>=i)*1
    P = lambda s,y,k,t: math.exp(-track2[s].position.distance2DTo(y))

    Dynamics.HMM(S, Q, P).estimate(track1, ["x","y"], mode=Dynamics.MODE_OBS_AS_2D_POSITIONS, verbose=2)
	 

    track1.plot('r-')
    track2.plot('b-')
    Comparison.plotDifferenceProfile(track1, track2, "hmm_inference")
    plt.show()