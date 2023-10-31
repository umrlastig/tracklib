# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Yann Méneroux
Creation date: 1th november 2020

tracklib library provides a variety of tools, operators and 
functions to manipulate GPS trajectories. It is a open source contribution 
of the LASTIG laboratory at the Institut National de l'Information 
Géographique et Forestière (the French National Mapping Agency).
See: https://tracklib.readthedocs.io
 
This software is governed by the CeCILL-C license under French law and
abiding by the rules of distribution of free software. You can  use, 
modify and/ or redistribute the software under the terms of the CeCILL-C
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info". 

As a counterpart to the access to the source code and rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability. 

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or 
data to be ensured and,  more generally, to use and operate it in the 
same conditions as regards security. 

The fact that you are presently reading this means that you have had
knowledge of the CeCILL-C license and that you accept its terms.



This module contains the class to manage bounding box
"""

# For type annotation
from __future__ import annotations
from typing import Union

import copy
import matplotlib.pyplot as plt

from tracklib.core import ENUCoords, GeoCoords, ECEFCoords
from tracklib.util import Polygon


class Bbox:
    """Class to represent a boundary box"""

    def __init__(self, ll: Union[ENUCoords, ECEFCoords, GeoCoords], 
                 ur: Union[ENUCoords, ECEFCoords, GeoCoords]):
        """Constructor of :class:`Bbox`

        :param ll: lower left point
        :param ur: upper right point
        """
        self.ll = ll
        self.ur = ur

    def __str__(self) -> str:
        """String representation of :class:`Bbox`

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
    ) -> Union[ENUCoords, ECEFCoords, GeoCoords]:
        """Return the lower-left coordinates of :class:`Bbox`

        :return: Lower-left coordinates
        """
        return self.ll

    def getUpperRight(
        self,
    ) -> Union[ENUCoords, ECEFCoords, GeoCoords]:
        """Return the upper-right coordinates of :class:`Bbox`

        :return: Upper-right coordinates
        """
        return self.ur

    def getXmin(self) -> float:
        """Return the min X coordinate"""
        return self.ll.getX()

    def getYmin(self) -> float:
        """Return the min Y coordinate"""
        return self.ll.getY()

    def getXmax(self) -> float:
        """Return the max X coordinate"""
        return self.ur.getX()

    def getYmax(self) -> float:
        """Return the max Y coordinate"""
        return self.ur.getY()

    def getDx(self) -> float:
        """Return the difference of X coordinates"""
        return self.getXmax() - self.getXmin()

    def getDy(self) -> float:
        """Return the difference of Y coordinates"""
        return self.getYmax() - self.getYmin()

    def getDimensions(self) -> tuple[float, float]:
        """Return Dx and Dy

        :return: Tuple with structure : (Dx, Dy)
        """
        return (self.getDx(), self.getDy())

    def setXmin(self, xmin: float):
        """Set Xmin coordinate

        :param xmin: Xmin coordinate
        """
        self.ll.setX(xmin)

    def setYmin(self, ymin: float):
        """Set Ymin coordinate

        :param ymin: Ymin coordinate
        """
        return self.ll.setY(ymin)

    def setXmax(self, xmax: float):
        """Set Xmax coordinate

        :param xmax: Xmax coordinate
        """
        return self.ur.setX(xmax)

    def setYmax(self, ymax: float):
        """Set Ymax coordinate

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
        """Bounding boxes combination

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
        """Check if a point is in the bbox"""
        return self.geom().contains(point)

    def translate(self, dx: float, dy: float):
        """Translation (2D) of shape

        :param dx: dx in ground units
        :param dy: dy in ground units
        """
        self.ll.translate(dx, dy)
        self.ur.translate(dx, dy)

    def rotate(self, theta: float):
        """Rotation (2D) of shape

        :param theta: angle in radians
        """
        self.ll.rotate(theta)
        self.ur.rotate(theta)

    def scale(self, h: float):
        """Homothetic transformation (2D) of shape

        :param h: factor
        """
        self.ll.scale(h)
        self.ur.scale(h)

    def geom(self) -> Polygon:
        """Convert to Geometrics (Polygon)

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

    def toECEFCoords(self, base: Union[ENUCoords, ECEFCoords, GeoCoords] = None):
        """Coordinate transformation to :class:`core.Coords.ECEFCoords`

        :param base: base coordinates, defaults to None
        """
        self.ll.toECEFCoords(base)
        self.ur.toECEFCoords(base)

    def toGeoCoords(self, base: Union[ENUCoords, ECEFCoords, GeoCoords] = None):
        """Coordinate transformation to :class:`core.Coords.GeoCoords`

        :param base: base coordinates, defaults to None
        """
        self.ll.toGeoCoords(base)
        self.ur.toGeoCoords(base)

    def toENUCoords(self, base: Union[ENUCoords, ECEFCoords, GeoCoords] = None):
        """Coordinate transformation to :class:`core.Coords.ENUCoords`

        :param base: base coordinates, defaults to None
        """
        self.ll.toENUCoords(base)
        self.ur.toENUCoords(base)

    def addMargin(self, margin: float = 0.05):
        """Adding margin (relative float) to bounding box

        :param margin: margin, defaults to 0.05
        """
        dx, dy = self.getDimensions()
        self.setXmin(self.getXmin() - margin * dx)
        self.setXmax(self.getXmax() + margin * dx)
        self.setYmin(self.getYmin() - margin * dy)
        self.setYmax(self.getYmax() + margin * dy)

    def __getitem__(self, index: int) -> float:
        """Get value by index

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
        """Set value by index

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
        """Transform the Bbox object in a tuple of coordinates

        :return: Tuple of coordinates with this structure (x min, x max, y min, y max)
        """
        return (self.getXmin(), self.getXmax(), self.getYmin(), self.getYmax())
