"""Module core.Bbox

This module contains the class to manage bounding box and to manage bounding box
"""

import sys
import copy
import matplotlib.pyplot as plt

from tracklib.algo.Geometrics import Polygon


class Bbox:
    def __init__(self, ll, ur):
        """__init__ Initialisation of Bbox

        :param ll: lower left point
        :type ll: Coord object
        :param ur: upper right point
        :type ur: Coord object
        """
        self.ll = ll
        self.ur = ur

    def __str__(self):
        output = "Bounding box: \n"
        output += " Lower left corner : " + str(self.ll) + "\n"
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
        return self.getXmax() - self.getXmin()

    def getDy(self):
        return self.getYmax() - self.getYmin()

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

    def plot(self, sym="b-"):
        X = [
            self.getXmin(),
            self.getXmax(),
            self.getXmax(),
            self.getXmin(),
            self.getXmin(),
        ]
        Y = [
            self.getYmin(),
            self.getYmin(),
            self.getYmax(),
            self.getYmax(),
            self.getYmin(),
        ]
        plt.plot(X, Y, sym)

    def __add__(self, bbox):
        """__add__ Bounding boxes combination"""
        ll = self.ll.copy()
        ur = self.ur.copy()
        xmin = min(self.getXmin(), bbox.getXmin())
        ymin = min(self.getYmin(), bbox.getYmin())
        xmax = max(self.getXmax(), bbox.getXmax())
        ymax = max(self.getYmax(), bbox.getYmax())
        ll.setX(xmin)
        ll.setY(ymin)
        ur.setX(xmax)
        ur.setY(ymax)
        return Bbox(ll, ur)

    def __and__(self, bbox):
        return None  # TO DO

    def contains(self, point):
        return self.geom().contains(point)

    def copy(self):
        return copy.deepcopy(self)

    def translate(self, dx, dy):
        """translate Translation (2D) of shape

        :param dx: dx in ground units
        :type dx: float
        :param dy: dy in ground units
        :type dy: float
        """
        self.ll.translate(dx, dy)
        self.ur.translate(dx, dy)

    def rotate(self, theta):
        """rotate Rotation (2D) of shape

        :param theta: angle in radians
        :type theta: float
        """
        self.ll.rotate(theta)
        self.ur.rotate(theta)

    def scale(self, h):
        """scale Homothetic transformation (2D) of shape

        :param h: factor
        :type h: float
        """
        self.ll.scale(h)
        self.ur.scale(h)

    def geom(self):
        """geom Convert to Geometrics (Polygon)

        :return: Polygon
        :rtype: [type]
        """
        X = [
            self.getXmin(),
            self.getXmax(),
            self.getXmax(),
            self.getXmin(),
            self.getXmin(),
        ]
        Y = [
            self.getYmin(),
            self.getYmin(),
            self.getYmax(),
            self.getYmax(),
            self.getYmin(),
        ]
        return Polygon(X, Y)

    def toECEFCoords(self, base=None):
        """toECEFCoords Coordinate transformation

        :param base: [description], defaults to None
        :type base: [type], optional
        """
        self.ll.toECEFCoords(base)
        self.ur.toECEFCoords(base)

    def toGeoCoords(self, base=None):
        self.ll.toGeoCoords(base)
        self.ur.toGeoCoords(base)

    def toENUCoords(self, base=None):
        self.ll.toENUCoords(base)
        self.ur.toENUCoords(base)

    def addMargin(self, margin=0.05):
        """addMargin Adding margin (relative float) to bounding box

        :param margin: margin, defaults to 0.05
        :type margin: float, optional
        """
        dx, dy = self.getDimensions()
        self.setXmin(self.getXmin() - margin * dx)
        self.setXmax(self.getXmax() + margin * dx)
        self.setYmin(self.getYmin() - margin * dy)
        self.setYmax(self.getYmax() + margin * dy)

    def __getitem__(self, index):
        """__getitem__ Get and set: (for retrocompatibilty)

        - 0: xmin
        - 1: xmax
        - 2: ymin
        - 3: ymax

        :param index: index of coordinates
        :type index: int
        :return: coordinate
        :rtype: float
        """
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
        """asTuple Transform the Bbox object in a tuple of coordinates

        :return: Tuple of coordinates with this structure (x min, x max, y min, y max)
        :rtype: (float, float, float, float)
        """
        return (self.getXmin(), self.getXmax(), self.getYmin(), self.getYmax())
