#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

from tracklib.core.GPSTime import GPSTime
from tracklib.core.Coords import ENUCoords
from tracklib.core.Obs import Obs
from tracklib.core.Track import Track
# from tracklib.io.GpxReader import GpxReader
from tracklib.algo.AlgoAF import calculAngleOriente

from tracklib.core.Operator import Operator
# from tracklib.core.Kernel import GaussianKernel

# kernel = GaussianKernel(21)
# track.operate(Operator.FILTER, "x", kernel, "x2")
# track.operate(Operator.FILTER, "y", kernel, "y2")

#path = '../data/vincennes.gpx'
#GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
#tracks = GpxReader.readFromGpx(path)
#trace = tracks[0]
#trace.summary()

trace = Track()

GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
time = GPSTime.readTimestamp("2018-05-30 14:31:25")
trace.addObs(Obs(ENUCoords(3, 0, 0), time))
trace.addObs(Obs(ENUCoords(5, 0, 0), time))
trace.addObs(Obs(ENUCoords(5, 5, 0), time))
trace.addObs(Obs(ENUCoords(8, 5, 0), time))
trace.addObs(Obs(ENUCoords(8, 6, 0), time))
trace.addObs(Obs(ENUCoords(9, 6, 0), time))
trace.addObs(Obs(ENUCoords(9, 9, 0), time))
trace.addObs(Obs(ENUCoords(11, 9, 0), time))
trace.addObs(Obs(ENUCoords(11, 11, 0), time))
trace.addObs(Obs(ENUCoords(9, 11, 0), time))
trace.addObs(Obs(ENUCoords(9, 15, 0), time))
trace.addObs(Obs(ENUCoords(1, 15, 0), time))
trace.addObs(Obs(ENUCoords(1, 13, 0), time))
trace.addObs(Obs(ENUCoords(0, 13, 0), time))
trace.addObs(Obs(ENUCoords(0, 9, 0), time))
trace.addObs(Obs(ENUCoords(2, 9, 0), time))
trace.addObs(Obs(ENUCoords(2, 7, 0), time))
trace.addObs(Obs(ENUCoords(0, 7, 0), time))
trace.addObs(Obs(ENUCoords(0, 5, 0), time))
trace.addObs(Obs(ENUCoords(3, 5, 0), time))
trace.addObs(Obs(ENUCoords(3, 0, 0), time))



#trace = trace.extract(0, 500)
trace.addAnalyticalFeature(calculAngleOriente)
trace.operate(Operator.INTEGRATOR, 'calculAngleOriente', 'turning_function')
trace.plotAnalyticalFeature('turning_function')

