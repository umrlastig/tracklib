"""
This module contains the class to manage bounding box and to manage bounding box
"""

# For type annotation
from __future__ import annotations
from typing import Union
import sys
import copy
import matplotlib.pyplot as plt

from tracklib.algo.Geometrics import Polygon
from tracklib.core import Coords


class Bbox:
    """Class to represent a boundary box"""

    def __init__(
        self,
        ll: Union[Coords.ENUCoords, Coords.ENUCoords, Coords.GeoCoords],
        ur: Union[Coords.ENUCoords, Coords.ENUCoords, Coords.GeoCoords],
    ):
        """__init__ Constructor of Bbox

        :param ll: lower left point
        :param ur: upper right point
        """
        self.ll = ll
        self.ur = ur

    def __str__(self) -> str:
        """__str__ String representation of bbox

        :return: String representation of bbox
        """
        output = "Bounding box: \n"
        output += " Lower left corner : " + str(self.ll) + "\n"
        output += " Upper right corner: " + str(self.ur)
        return output

    def copy(self) -> Bbox:
        """Copy the current object

        :return: Copy of bbox
        """
        return copy.deepcopy(self)

    def getLowerLeft(
        self,
    ) -> Union[Coords.ENUCoords, Coords.ENUCoords, Coords.GeoCoords]:
        """getLowerLeft Return the lower-left coordinates of bbox

        :return: Lower-left coordinates
        """
        return self.ll

    def getUpperRight(
        self,
    ) -> Union[Coords.ENUCoords, Coords.ENUCoords, Coords.GeoCoords]:
        """getUpperRight Return the upper-right coordinates of bbox

        :return: Upper-right coordinates
        """
        return self.ur

    def getXmin(self) -> float:
        """getXmin Return the min X coordinate"""
        return self.ll.getX()

    def getYmin(self) -> float:
        """getYmin Return the min Y coordinate"""
        return self.ll.getY()

    def getXmax(self) -> float:
        """getXmax Return the max X coordinate"""
        return self.ur.getX()

    def getYmax(self) -> float:
        """getYmax Return the max Y coordinate"""
        return self.ur.getY()

    def getDx(self) -> float:
        """getDx Return the difference of X coordinates"""
        return self.getXmax() - self.getXmin()

    def getDy(self) -> float:
        """getDy Return the difference of Y coordinates"""
        return self.getYmax() - self.getYmin()

    def getDimensions(self) -> tuple[float, float]:
        """getDimensions Return Dx and Dy

        :return: Tuple with structure : (Dx, Dy)
        """
        return (self.getDx(), self.getDy())

    def setXmin(self, xmin: float):
        """setXmin Set Xmin coordinate

        :param xmin: Xmin coordinate
        """
        self.ll.setX(xmin)

    def setYmin(self, ymin: float):
        """setYmin Set Ymin coordinate

        :param ymin: Ymin coordinate
        """
        return self.ll.setY(ymin)

    def setXmax(self, xmax: float):
        """setXmax Set Xmax coordinate

        :param xmax: Xmax coordinate
        """
        return self.ur.setX(xmax)

    def setYmax(self, ymax: float):
        """setYmax Set Ymax coordinate

        :param ymax: Ymax coordinate
        """
        return self.ur.setY(ymax)

    def plot(self, sym="b-"):
        """TODO"""
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

    def __add__(self, bbox: Bbox) -> Bbox:
        """__add__ Bounding boxes combination

        :param bbox: Bbox 2
        """
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
        """TODO"""
        return None  # TO DO

    def contains(self, point) -> bool:
        """contains Check if a point is in the bbox"""
        return self.geom().contains(point)

    def copy(self) -> Bbox:
        """Copy the current object

        :retrun: Copu of the current object
        """
        return copy.deepcopy(self)

    def translate(self, dx: float, dy: float):
        """translate Translation (2D) of shape

        :param dx: dx in ground units
        :param dy: dy in ground units
        """
        self.ll.translate(dx, dy)
        self.ur.translate(dx, dy)

    def rotate(self, theta: float):
        """rotate Rotation (2D) of shape

        :param theta: angle in radians
        """
        self.ll.rotate(theta)
        self.ur.rotate(theta)

    def scale(self, h: float):
        """scale Homothetic transformation (2D) of shape

        :param h: factor
        """
        self.ll.scale(h)
        self.ur.scale(h)

    def geom(self) -> Polygon:
        """geom Convert to Geometrics (Polygon)

        :return: Polygon
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

    def toECEFCoords(
        self, base: Union[Coords.ENUCoords, Coords.ENUCoords, Coords.GeoCoords] = None
    ):
        """toECEFCoords Coordinate transformation to :class:`core.Coords.ECEFCoords`

        :param base: base coordinates, defaults to None
        """
        self.ll.toECEFCoords(base)
        self.ur.toECEFCoords(base)

    def toGeoCoords(
        self, base: Union[Coords.ENUCoords, Coords.ENUCoords, Coords.GeoCoords] = None
    ):
        """toGeoCoords Coordinate transformation to :class:`core.Coords.GeoCoords`

        :param base: base coordinates, defaults to None
        """
        self.ll.toGeoCoords(base)
        self.ur.toGeoCoords(base)

    def toENUCoords(
        self, base: Union[Coords.ENUCoords, Coords.ENUCoords, Coords.GeoCoords] = None
    ):
        """toENUCoords Coordinate transformation to :class:`core.Coords.ENUCoords`

        :param base: base coordinates, defaults to None
        """
        self.ll.toENUCoords(base)
        self.ur.toENUCoords(base)

    def addMargin(self, margin: float = 0.05):
        """addMargin Adding margin (relative float) to bounding box

        :param margin: margin, defaults to 0.05
        """
        dx, dy = self.getDimensions()
        self.setXmin(self.getXmin() - margin * dx)
        self.setXmax(self.getXmax() + margin * dx)
        self.setYmin(self.getYmin() - margin * dy)
        self.setYmax(self.getYmax() + margin * dy)

    def __getitem__(self, index: int) -> float:
        """__getitem__ Get value by index

        - 0: xmin
        - 1: xmax
        - 2: ymin
        - 3: ymax

        :param index: index of coordinates
        :return: coordinate
        """
        if (index == 0) or (index == "xmin"):
            return self.getXmin()
        if (index == 1) or (index == "xmax"):
            return self.getXmax()
        if (index == 2) or (index == "ymin"):
            return self.getYmin()
        if (index == 3) or (index == "ymax"):
            return self.getYmax()

    def __setitem__(self, index: int, value: float):
        """__setitem__ Set value by index

        :param index: index of value
        :pram value: value to set
        """
        if (index == 0) or (index == "xmin"):
            self.setXmin(value)
        if (index == 1) or (index == "xmax"):
            self.setXmax(value)
        if (index == 2) or (index == "ymin"):
            self.setYmin(value)
        if (index == 3) or (index == "ymax"):
            self.setYmax(value)

    def asTuple(self) -> tuple[float, float, float, float]:
        """asTuple Transform the Bbox object in a tuple of coordinates

        :return: Tuple of coordinates with this structure (x min, x max, y min, y max)
        """
        return (self.getXmin(), self.getXmax(), self.getYmin(), self.getYmax())
