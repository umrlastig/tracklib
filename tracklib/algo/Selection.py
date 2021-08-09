# --------------------------- Selection ---------------------------------------
# Class to manage selection of of GPS tracks
# -----------------------------------------------------------------------------
# Overall picture of selection process : selection is performed by a selector 
# object, containing an arbitrary number of constraints, combined by OR, AND or 
# XOR operator. Since only a single operator is allowed in the selector, a 
# "global selector" is provided to the users to combine the output of several 
# individual selectors. Again, the output may be combined with OR, AND or XOR.
# For example, given two circles C1 and C2, and two rectangles R1 and R2, to 
# select tracks crossing either C1 or C2, and either R1 or R2, we would like to 
# write the following combination of constraints : F = (C1 + C2).(R1 + R2), 
# where + and . operators denote OR and AND respectively. Such a constraint 
# requires two different combination rules, and therefore cannot be expressed 
# with a single selector. A solution is to create two disjonctive (OR) type 
# selectors S1 and S2 with S1 = C1 + C2 and S2 = R1 + R2. Then S1 and S2 are 
# combined in a conjunctive (AND) type global selector. Note that boolean 
# algebraic rules show that it is possible as well to combine 4 conjunctive-
# type selectors (C1.R1, C1.R2, C2.R1 and C2.R2) in a disjunctive-type global 
# selector. 
# Constraints may be based on:
#    - a geometrical shape (Rectangle, circle or polygon in Geometrics). This 
#      is the standard type of constraint. Different modes are:
#         - MODE_CROSSES: tracks crossing shape interior/boundary are selected
#         - MODE_INSIDE : tracks remaining fully inside the shape are selected
#         - MODE_GETS_IN: tracks getting in (at least once) shape are selected
#         - MODE_INSIDE : tracks getting out (at least once) shape are selected
#    - a track t as a reference. Available modes are:
#         - MODE_CROSSES : tracks  intersecting t (at least once) are selected
#         - MODE_PARALLEL: tracks  following t are selected
#    - a "toll gate" segment, defined by two Coords objects: tracks crossing 
#         (at least once) the toll gate are selected 
# All these constraint may be provided with an additional time constraint, 
# specifying the time interval (between two GPSTime dates) where crossing /
# containing / getting in / getting out... operations are tested. 
# Besides, there are two types of selection:
#    - TYPE_SELECT: tracks abiding by constraints are returned as they are
#    - TYPE_CUT_AND_SELECT: tracks abiding by constraints are cut and returned
# -----------------------------------------------------------------------------
# General constraint syntax:
# t1 = TimeConstraint(initial_date, final_date, options)
# ...
# c1 = Constraint(shape, t1, options)
# c2 = TrackConstraint(track, t2, options)
# c3 = TollGateConstraint(shape, t3, options)
# ...
# s1 = Selector(c1, c2, ..., options)
# s2 = Selector(c3, c4, ..., options)
# ...
# selector = GlobalSelector([s1, s2, ...], options)
# -----------------------------------------------------------------------------

import sys
import numpy as np
import matplotlib.pyplot as plt

from tracklib.core.Track import Track
from tracklib.core.TrackCollection import TrackCollection
from tracklib.core.Obs import Obs

import tracklib.core.Utils as utils
import tracklib.core.Operator as Operator
import tracklib.algo.Dynamics as Dynamics
import tracklib.algo.Geometrics as Geometrics

from tracklib.core.GPSTime import GPSTime
from tracklib.algo.Geometrics import Rectangle


MODE_CROSSES = 0
MODE_INSIDE = 1
MODE_GETS_IN = 2
MODE_GETS_OUT = 3

MODE_CROSSES = 0
MODE_PARALLEL = 1

TYPE_SELECT = 0
TYPE_CUT_AND_SELECT = 1

COMBINATION_AND = 0
COMBINATION_OR = 1
COMBINATION_XOR = 2

def printMode(constraint):
    if constraint.mode == MODE_CROSSES:
        return "CROSS"
    if constraint.mode == MODE_INSIDE:
        return "INSIDE"
    if constraint.mode == MODE_GETS_IN:
        return "GETS IN"
    if constraint.mode == MODE_GETS_OUT:
        return "GETS OUT"

# ------------------------------- TIME CONSTRAINTS ----------------------------
class TimeConstraint:

    def __init__(self, begin=None, end=None, pattern=None):
        if begin is None:
            self.minTimestamp = GPSTime(0,0,0,0,0,0)
        else:
            self.minTimestamp = begin
        if end is None:
            self.maxTimestamp = GPSTime(2100,0,0,0,0,0)
        else:
           self.maxTimestamp = end 
        self.pattern = pattern
           
    def __str__(self):
        output  = "Temporal constraint: \n" 
        if self.minTimestamp - GPSTime(0,0,0,0,0,0) != 0:
            if self.maxTimestamp - GPSTime(2100,0,0,0,0,0) != 0:
                output += "    -" + str(self.minTimestamp) + " <= t <= " 
                output += str(self.maxTimestamp) + "\n"
        if not self.pattern is None:
            output += "    - timestamp pattern: " + self.pattern
        return output
       
    def setMinTimestamp(self, timestamp):
        self.minTimestamp = timestamp

    def setMaxTimestamp(self, timestamp):
        self.maxTimestamp = timestamp              

    def contains(self, timestamp):
        output = (self.minTimestamp <= timestamp) and (timestamp <= self.maxTimestamp)
        if not (self.pattern is None):
            output = output & utils.compLike(str(timestamp), self.pattern)
        return output

# ------------------------------- CONSTRAINTS ----------------------------

# -------------------------------------------------
# Special case of constraint defined by a track 
# -------------------------------------------------
class TrackConstraint:

    def __init__(self, track, res=1, buffer=10, prop=0.5, length=0, time=None, mode=MODE_PARALLEL, type=TYPE_SELECT):
        self.track = track
        self.time = time
        self.type = type
        self.prop = prop
        self.mode = mode
        self.length = length
        self.segments = []
        for i in range(1,len(track),1):
            pt1 = track[i].position.copy()
            pt2 = pt1.copy()
            dx = track[i].position.getX()-track[i-1].position.getX()
            dy = track[i].position.getY()-track[i-1].position.getY()
            R = (dx*dx+dy*dy)**(0.5)
            if R == 0:
                continue
            pt1.translate(+buffer*dy/R, -buffer*dx/R)
            pt2.translate(-buffer*dy/R, +buffer*dx/R)
            self.segments.append(Track([Obs(pt1), Obs(pt2)]))

    def __str__(self):
        output = "Track-based selecting constraint (mode '"+printMode(self)+"')"              
        output += " with " + str(self.time).lower()        
        return output

    def plot(self, sym='r-'):
        plt.plot(self.track.getX(), self.track.getY(), sym)
        for i in range(len(self.segments)):
            plt.plot(self.segments[i].getX(), self.segments[i].getY(), sym)
        
    def contains(self, track):  
        if self.mode == MODE_PARALLEL:
            counter = 0
            lgth = 0
            for i in range(len(self.segments)):
                if Geometrics.intersects(self.segments[i], track):
                    counter += 1
                    lgth += self.track[i].position.distance2DTo(self.track[i+1].position)
                    if ((counter > self.prop*len(self.segments)) and (lgth > self.length)):
                        return True
            return False 
        else:
            return Geometrics.intersects(self.track, track)
        
    def select(self, tracks): 
        if self.type == TYPE_SELECT:
            output = TrackCollection()
            for track in tracks: 
                if self.contains(track):
                    output.addTrack(track)
            return output
        if self.type == TYPE_CUT_AND_SELECT:
            return tracks  
        
# -------------------------------------------------
# Special case of constraint defined by a segment
# -------------------------------------------------
class TollGateConstraint:

    def __init__(self, pt1, pt2, time=None, type=TYPE_SELECT):
        self.gate = Track([Obs(pt1), Obs(pt2)])
        self.time = time
        self.type = type

    def __str__(self):
        output = "Toll gate selecting constraint"  
        if not self.time is None:
            output += " with " + str(self.time).lower()
        return output
        
    def plot(self, sym='ro-'):
        plt.plot(self.gate.getX(), self.gate.getY(), sym)
        
    def contains(self, track):
        return Geometrics.intersects(self.gate, track)
        
    def select(self, tracks):
        if self.type == TYPE_SELECT:
            output = TrackCollection()
            for track in tracks: 
                if self.contains(track):
                    output.addTrack(track)
            return output
        if self.type == TYPE_CUT_AND_SELECT:
            return tracks 
        

class Constraint:

    def __init__(self, shape=None, time=None, mode=MODE_CROSSES, type=TYPE_SELECT, srid="ENU"):
        if shape is None:
            if srid.upper in ["GEO", "GeoCoords"]:
                shape = Rectangle(GeoCoords(-180,-90), GeoCoords(180,90))
            else:
                shape = Rectangle(ENUCoords(-1e300,-1e300), GeoCoords(1e300,1e300))
        self.shape = shape
        self.mode = mode
        self.type = type
        if time is None:
            self.time = TimeConstraint()
        else:
            self.time = time

    def __str__(self):
        output  = str(type(self.shape))[33:-2] + "-shaped selecting constraint "
        output += "(mode '"+ str(printMode(self)) +"')"              
        output += " with " + str(self.time).lower()
        return output

    def setShape(self, shape):
        self.shape = shape
   
    def contains(self, track):
        if not str(type(self.shape))[33:-2] in ["Circle", "Rectangle", "Polygon"]:
            return False
        if self.mode == MODE_CROSSES:
            for i in range(len(track)):
                if self.shape.contains(track[i].position):
                    if self.time.contains(track[i].timestamp):
                        return True
            return False
        if self.mode == MODE_INSIDE:
            for i in range(len(track)):
                if not self.shape.contains(track[i].position):
                    return False
                if not self.time.contains(track[i].timestamp):
                    return False
            return True
        if self.mode == MODE_GETS_IN:
            if not self.shape.contains(track[0].position):
                for i in range(1,len(track)):
                    if self.shape.contains(track[i].position):
                        if self.time.contains(track[i].timestamp):
                            return True
            return False
        if self.mode == MODE_GETS_OUT:
            if self.shape.contains(track[0].position):
                for i in range(1,len(track)):
                    if not self.shape.contains(track[i].position):
                        if self.time.contains(track[i].timestamp):
                            return True
            return False            
        
    def select(self, tracks): 
        if self.type == TYPE_SELECT:
            output = TrackCollection()
            for track in tracks: 
                if self.contains(track):
                    output.addTrack(track)
            return output
        if self.type == TYPE_CUT_AND_SELECT:
            return tracks 
            
    def plot(self, sym):
        self.shape.plot(sym)

# ------------------------------- SELECTOR ----------------------------

class Selector:

    def __init__(self, constraints, combination=COMBINATION_AND):
        self.constraints = utils.listify(constraints)
        self.combination = combination
    
    def __len__(self):
        return len(self.constraints)
 
    def __str__(self):
        if self.combination == COMBINATION_AND:
            output = "Conjunctive"
        if self.combination == COMBINATION_OR:
            output = "Disjonctive"
        if self.combination == COMBINATION_XOR:
            output = "Exclusive disjonction"
        output += " selector with following constraint(s):\n"
        for i in range(len(self)):
            output += "   (" + str(i+1) + ") " + str(self.constraints[i]) + "\n"        
        return output

    def setCombinationMode(self, combination):
        self.combination = combination    
        
    def addConstraint(self, constraint):    
        self.constraints.append(constraints)  

    def plot(self, sym=['r-', 'g-', 'b-']):
        sym = utils.listify(sym)
        for i in range(len(self)):
            self.constraints[i].plot(sym[i%len(sym)])   
    
    def __combine(self, bool1, bool2):
        if self.combination == COMBINATION_AND:
            return bool1 and bool2
        if self.combination == COMBINATION_OR:
            return bool1 or bool2
        if self.combination == COMBINATION_XOR:
            return (bool1 and not(bool2)) or (not(bool1) and bool2)
    
    def __initCombination(self):
        if self.combination == COMBINATION_AND:
            return True    
        if self.combination == COMBINATION_OR:
            return False    
        if self.combination == COMBINATION_XOR:
            return False            
            
    def contains(self, track):
        inside = self.__initCombination()
        for c in self.constraints:
            inside = self.__combine(inside, c.contains(track))
        return inside

# --------------------------- GLOBAL SELECTOR ---------------------------

class GlobalSelector:

    def __init__(self, selectors, combination=COMBINATION_AND):
        self.selectors = utils.listify(selectors)
        self.combination = combination

    def __len__(self):
        return len(self.selectors)
        
    def numberOfConstraints(self):
        count = 0
        for i in range(len(self)):
            count += len(self. selectors)
        return count
 
    def __str__(self):
        alphabet = ['a','b','c','d','e','f','g','h','i']
        if self.combination == COMBINATION_AND:
            output = "Conjunctive"
        if self.combination == COMBINATION_OR:
            output = "Disjonctive"
        if self.combination == COMBINATION_XOR:
            output = "Exclusive disjonction"
        output += " global selector with following selector(s):\n"
        for i in range(len(self)):
            output += " ("+alphabet[i].upper() +") " + str(self.selectors[i])    
        return output 
        
    def plot(self):
        for i in range(len(self.selectors)):
            self.selectors[i].plot()

    def __combine(self, bool1, bool2):
        if self.combination == COMBINATION_AND:
            return bool1 and bool2
        if self.combination == COMBINATION_OR:
            return bool1 or bool2
        if self.combination == COMBINATION_XOR:
            return (bool1 and not(bool2)) or (not(bool1) and bool2)
    
    def __initCombination(self):
        if self.combination == COMBINATION_AND:
            return True    
        if self.combination == COMBINATION_OR:
            return False    
        if self.combination == COMBINATION_XOR:
            return False 
        
    def addSelector(self, selector):    
        self.selectors.append(selector)    
        
    def setCombinationMode(self, combination):
        self.combination = combination   
        
    def contains(self, track):
        inside = self.__initCombination()
        for s in self.selectors:
            inside = self.__combine(inside, s.contains(track))
        return inside