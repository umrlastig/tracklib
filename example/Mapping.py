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
# Example 0: 2D mapping of GPS and camera positions
# -----------------------------------------------------------------------

def example0():

    path_cam = "../data/hybridation_gnss_camera.dat"
    path_gps = "../data/hybridation_gnss_camera.pos"

    GPSTime.setReadFormat("2D/2M/4Y-2h:2m:2s.3z")
    track_cam = FileReader.readFromFile(path_cam, 1, 2, 3, 0, " ", srid="ENUCoords")
    track_gps = FileReader.readFromFile(path_gps, 1, 2, 3, 0, " ", srid="ENUCoords")
    track_cam.incrementTime(0, 18-3600)

    ini_time = GPSTime("06/06/2021-16:02:00.000")
    fin_time = GPSTime("06/06/2021-16:12:12.000")
    track_cam = track_cam.extractSpanTime(ini_time, fin_time)
    track_gps = track_gps.extractSpanTime(ini_time, fin_time)
    track_gps = track_gps // track_cam

    track_cam.rotate(0.2);
    Mapping.mapOn(track_cam, track_gps)

    track_cam.plot('r-')
    track_gps.plot('b+')
    plt.show()
    
example0()