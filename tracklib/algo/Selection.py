# --------------------------- Selection ---------------------------------------
# Class to manage selection of of GPS tracks
# -----------------------------------------------------------------------------

import sys
import numpy as np

import tracklib.core.Track as Track
import tracklib.core.Utils as utils
import tracklib.core.Operator as Operator
import tracklib.algo.Dynamics as Dynamics

from tracklib.core.GPSTime import GPSTime
from tracklib.algo.Geometrics import Rectangle


MODE_CROSSES = 0
MODE_INSIDE = 1
MODE_GETS_IN = 2
MODE_GETS_OUT = 3

TYPE_SELECT = 0
TYPE_CUT_AND_SELECT = 1

class Selector:

    def __init__(self, shape=None, mode=MODE_CROSSES, type=TYPE_SELECT, srid="ENU"):
        if shape is None:
            if srid.upper in ["GEO", "GeoCoords"]:
                shape = Rectangle(GeoCoords(-180,-90), GeoCoords(180,90))
            else:
                shape = Rectangle(ENUCoords(-1e300,-1e300), GeoCoords(1e300,1e300))
        self.shape = shape
        self.mode = mode
        self.type = type
        self.minTimestamp = GPSTime(0,0,0,0,0,0)
        self.maxTimestamp = GPSTime(2100,0,0,0,0,0)

    def setShape(self, shape):
        self.shape = shape

    def setMinTimestamp(self, timestamp):
        self.minTimestamp = timestamp

    def setMaxTimestamp(self, timestamp):
        self.maxTimestamp = timestamp      

    def contains(self, track):
        if not str(type(self.shape))[33:-2] in ["Circle", "Rectangle", "Polygon"]:
            return False
        if self.mode == MODE_CROSSES:
            for i in range(len(track)):
                if self.shape.contains(track[i].position):
                    return True
            return False
        if self.mode == MODE_INSIDE:
            for i in range(len(track)):
                if not self.shape.contains(track[i].position):
                    return False
            return True
        if self.mode == MODE_GETS_IN:
            if not self.shape.contains(track[0].position):
                for i in range(1,len(track)):
                    if self.shape.contains(track[i].position):
                        return True
            return False
        if self.mode == MODE_GETS_OUT:
            if self.shape.contains(track[0].position):
                for i in range(1,len(track)):
                    if not self.shape.contains(track[i].position):
                        return True
            return False            
        
    def select(self, tracks):  # TO DO (in track collection)
        if self.type == TYPE_SELECT:
            return tracks
        if self.type == TYPE_CUT_AND_SELECT:
            return tracks 
        