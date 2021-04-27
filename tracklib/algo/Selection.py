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

COMBINATION_AND = 0
COMBINATION_OR = 1
COMBINATION_XOR = 2

class TimeConstraint:

    def __init__(self, begin=None, end=None):
        if begin is None:
            self.minTimestamp = GPSTime(0,0,0,0,0,0)
        else:
            self.minTimestamp = begin
        if end is None:
            self.maxTimestamp = GPSTime(2100,0,0,0,0,0)
        else:
           self.maxTimestamp = end 
           
    def __str__(self):
        output  = "Temporal constraint: " 
        output += str(self.minTimestamp) + " <= t <= " 
        output += str(self.maxTimestamp)
        return output
       
    def setMinTimestamp(self, timestamp):
        self.minTimestamp = timestamp

    def setMaxTimestamp(self, timestamp):
        self.maxTimestamp = timestamp              

    def contains(self, timestamp):
       return (self.minTimestamp <= timestamp) and (timestamp <= self.maxTimestamp)        


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
        output  = str(type(self.shape))[33:-2] + "-shaped selecting constraint"
        if self.time.minTimestamp - GPSTime(0,0,0,0,0,0) == 0:
            if self.time.maxTimestamp - GPSTime(2100,0,0,0,0,0) == 0:
                return output                
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
        
    def select(self, tracks):  # TO DO (in track collection)
        if self.type == TYPE_SELECT:
            return tracks
        if self.type == TYPE_CUT_AND_SELECT:
            return tracks 
            
    def plot(self, sym):
        self.shape.plot(sym)


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
        
    def addSelector(self, selector):    
        self.selectors.append(selector)    
        
    def setCombinationMode(self, combination):
        self.combination = combination    