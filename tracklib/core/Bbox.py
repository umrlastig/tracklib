# --------------------------- Bbox -------------------------------
# Class to manage bounding box
# Used for Track, TrackCollection and Network
# ----------------------------------------------------------------
import sys
import copy
import matplotlib.pyplot as plt

from tracklib.algo.Geometrics import Polygon


class Bbox:
    
    # --------------------------------------------------
    # Bounding box:
    #  - ll: lower left point (Coord object)
    #  - ur: upper right point (Coord object)
    # --------------------------------------------------
    def __init__(self, ll, ur):
        self.ll = ll
        self.ur = ur
        
    def __str__(self):
        output  = "Bounding box: \n"
        output += " Lower left corner : " + str(self.ll) +"\n"
        output += " Upper right corner: " + str(self.ur)
        return output
    
    def copy(self):
        return copy.deepcopy(self)
        
    def getLowerLeft(self):
        return self.ll

    def getUpperRight(self):
        return self.ur
        
    def getXmin(self):
        return self.ll.getX()

    def getYmin(self):
        return self.ll.getY()    

    def getXmax(self):
        return self.ur.getX()

    def getYmax(self):
        return self.ur.getY()

    def getDx(self):
        return self.getXmax()-self.getXmin()
        
    def getDy(self):
        return self.getYmax()-self.getYmin()
        
    def getDimensions(self):
        return (self.getDx(), self.getDy())

    def setXmin(self, xmin):
        self.ll.setX(xmin)

    def setYmin(self, ymin):
        return self.ll.setY(ymin)    

    def setXmax(self, xmax):
        return self.ur.setX(xmax)

    def setYmax(self, ymax):
        return self.ur.setY(ymax)   

    def plot(self, sym='b-'):
        X = [self.getXmin(), self.getXmax(), self.getXmax(), self.getXmin(), self.getXmin()]
        Y = [self.getYmin(), self.getYmin(), self.getYmax(), self.getYmax(), self.getYmin()]
        plt.plot(X, Y, sym)	
        
    # ------------------------------------------------------------
    # Bounding boxes combination
    # ------------------------------------------------------------    
    def __add__(self, bbox):
        ll = self.ll.copy()
        ur = self.ur.copy()
        xmin = min(self.getXmin(), bbox.getXmin());
        ymin = min(self.getYmin(), bbox.getYmin())
        xmax = max(self.getXmax(), bbox.getXmax())
        ymax = max(self.getYmax(), bbox.getYmax())
        ll.setX(xmin); ll.setY(ymin)
        ur.setX(xmax); ur.setY(ymax)
        return Bbox(ll, ur)

    def __and__(self, bbox):
        return None # TO DO

    def contains(self, point):
        return self.geom().contains(point)

    def copy(self):
        return copy.deepcopy(self)
        
    # --------------------------------------------------
    # Translation (2D) of shape (dx, dy in ground units)
    # --------------------------------------------------
    def translate(self, dx, dy):
       self.ll.translate(dx, dy)    
       self.ur.translate(dx, dy)
       
    # --------------------------------------------------
    # Rotation (2D) of shape (theta in radians)
    # --------------------------------------------------
    def rotate(self, theta):
        self.ll.rotate(theta)
        self.ur.rotate(theta)
    
    # --------------------------------------------------
    # Homothetic transformation (2D) of shape
    # --------------------------------------------------
    def scale(self, h):
        self.ll.scale(h)
        self.ur.scale(h)
		
    # --------------------------------------------------
    # Convert to Geometrics (Polygon)
    # --------------------------------------------------
    def geom(self):
        X = [self.getXmin(), self.getXmax(), self.getXmax(), self.getXmin(), self.getXmin()]
        Y = [self.getYmin(), self.getYmin(), self.getYmax(), self.getYmax(), self.getYmin()]
        return Polygon(X, Y)		
    
    # ------------------------------------------------------------
    # Adding margin (relative float) to bounding box 
    # Default value is +5%
    # ------------------------------------------------------------   
    def addMargin(self, margin=0.05):
        dx, dy = self.getDimensions()    
        self.setXmin(self.getXmin - margin*dx)
        self.setXmax(self.getXmax + margin*dx)
        self.setYmin(self.getYmin - margin*dy)
        self.setYmax(self.getYmax + margin*dy)

    # ------------------------------------------------------------
    # [[n]] Get and set: (for retrocompatibilty)
    #   - 0: xmin
    #   - 1: xmax
    #   - 2: ymin
    #   - 3: ymax
    # ------------------------------------------------------------    
    def __getitem__(self, index):
        if (index == 0) or (index == "xmin"):
            return self.getXmin()
        if (index == 1) or (index == "xmax"):
            return self.getXmax()
        if (index == 2) or (index == "ymin"):
            return self.getYmin()
        if (index == 3) or (index == "ymax"):
            return self.getYmax()
    def __setitem__(self, index, value):
        if (index == 0) or (index == "xmin"):
            self.setXmin(value)
        if (index == 1) or (index == "xmax"):
            self.setXmax(value)
        if (index == 2) or (index == "ymin"):
            self.setYmin(value)
        if (index == 3) or (index == "ymax"):
            self.setYmax(value)
    def asTuple(self):
        return (self.getXmin(), self.getXmax(), self.getYmin(), self.getXmax())	
