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



Class to manage general operations on a track

"""

import copy
import logging
import math
import matplotlib.pyplot as plt
import numpy as np
import random
import sys

import tracklib as tracklib
from tracklib.core import ENUCoords, co_median, co_avg
from . import (right, inclusion, collinear, isSegmentIntersects,
                      transform, transform_inverse)

MODE_ENCLOSING_BBOX = 0
MODE_ENCLOSING_MBR = 1
MODE_ENCLOSING_CIRCLE = 2
MODE_ENCLOSING_CONVEX = 3

logger = logging.getLogger()


class Circle:
    """
    A circle is defined by a center point with a radius
    
    .. code-block:: python
    
       moncircle = Geometrics.Circle(ENUCoords(3.55, 48.2), 3)
    """

    def __init__(self, center, radius):
        """
        Constructs a circle by defining the center and the radius.

        Parameters
        ----------
        center : Coords
            The center of the circle
            
        radius : float
            The radius of the circle
        """

        self.center = center
        self.radius = radius
        
    def __str__(self):
        """Transform the circle in string"""
        txt  = "Circle with \n"
        txt += "      center at " + str(self.center)  + "\n"
        txt += "      and radius equal to " + str(self.radius)
        return txt

    def plot(self, sym="r-", append=plt, linewidth=0.5):
        """
        Draw the circle.
        """

        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(12, 6))
        else:
            ax1 = append

        X = [0] * 100
        Y = [0] * 100
        for t in range(len(X) - 1):
            X[t] = self.radius * math.cos(2 * math.pi * t / len(X)) + self.center.getX()
            Y[t] = self.radius * math.sin(2 * math.pi * t / len(Y)) + self.center.getY()
        X[len(X) - 1] = X[0]
        Y[len(Y) - 1] = Y[0]
        ax1.plot(X, Y, sym, linewidth=linewidth)

        return ax1

    def contains(self, point):
        """
        Returns true if the point is in the cercle, false otherwise. 
        
        Parameters
        ----------
        point: ENUCoords
            The point to test
            
        Return
        ------
        
        type: bool
        """
        
        return (point.getX() - self.center.getX()) ** 2 + (
            point.getY() - self.center.getY() ) ** 2 <= self.radius ** 2

    def select(self, track):
        """
        TODO

        Parameters
        ----------
        track : TYPE
            DESCRIPTION.

        Returns
        -------
        t : TYPE
            DESCRIPTION.

        """
        t = tracklib.Track(user_id=track.uid, track_id=track.tid, base=track.base)
        for obs in track:
            if self.contains(obs.position):
                t.addObs(obs)
        return t

    def copy(self):
        """TODO"""
        return copy.deepcopy(self)

    def translate(self, dx, dy):
        """TODO"""
        self.center.translate(dx, dy)


class Rectangle:
    """
    A rectangle is defined by two points
    
    .. code-block:: python
    
       ll = ENUCoords(Xmin, Ymin)
       ur = ENUCoords(Xmax, Ymax)
       bbox = Geometrics.Rectangle(ll, ur)
       
    """

    def __init__(self, pmin, pmax):
        """
        Construct a rectangle from two points.

        Parameters
        ----------
        pmin : ENUCoords
            first point, for example the left lower point of the rectangle
        pmax : ENUCoords
            second point, for example the right upper point of the rectangle

        """
        
        self.pmin = pmin
        self.pmax = pmax
        
    def __str__(self):
        """Transform the rectangle in string"""
        txt  = "Rectangle with \n"
        txt += "      lower left coordinate " + str(self.pmin)  + "\n"
        txt += "      and upper right coordinate " + str(self.pmax)
        return txt

    def plot(self, sym="r-", append=plt):
        """
        Draw the rectangle
        """
        
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(12, 6))
        else:
            ax1 = append
            
        XR = [
            self.pmin.getX(),
            self.pmax.getX(),
            self.pmax.getX(),
            self.pmin.getX(),
            self.pmin.getX(),
        ]
        YR = [
            self.pmin.getY(),
            self.pmin.getY(),
            self.pmax.getY(),
            self.pmax.getY(),
            self.pmin.getY(),
        ]
        ax1.plot(XR, YR, sym)
        
        return ax1

    def contains(self, point):
        """
        Returns true if the point is in the rectangle, false otherwise. 
        
        Parameters
        ----------
        point: ENUCoords
            The point to test
            
        Return
        ------
        
        type: bool
        """
        inside_x = (self.pmin.getX() < point.getX()) and (
            point.getX() < self.pmax.getX()
        )
        inside_y = (self.pmin.getY() < point.getY()) and (
            point.getY() < self.pmax.getY()
        )
        return inside_x and inside_y
    
    def select(self, track):
        """
        TODO

        Parameters
        ----------
        track : TYPE
            DESCRIPTION.

        Returns
        -------
        t : TYPE
            DESCRIPTION.

        """
        t = tracklib.Track(user_id=track.uid, track_id=track.tid, base=track.base)
        for obs in track:
            if self.contains(obs.position):
                t.addObs(obs)
        return t

    def copy(self):
        """TODO"""
        return copy.deepcopy(self)

    # --------------------------------------------------
    # Translation (2D) of shape (dx, dy in ground units)
    # --------------------------------------------------
    def translate(self, dx, dy):
        """TODO"""
        self.pmin.translate(dx, dy)
        self.pmax.translate(dx, dy)

    # --------------------------------------------------
    # Rotation (2D) of shape (theta in radians)
    # --------------------------------------------------
    def rotate(self, theta):
        """TODO"""
        self.pmin.rotate(theta)
        self.pmax.rotate(theta)

    # --------------------------------------------------
    # Homothetic transformation (2D) of shape
    # --------------------------------------------------
    def scale(self, h):
        """TODO"""
        self.pmin.scale(h)
        self.pmax.scale(h)
        

class Polygon:
    """
    A polygon is defined by two list of 
    
    .. code-block:: python
    
       ll = ENUCoords(Xmin, Ymin)
       ur = ENUCoords(Xmax, Ymax)
       bbox = Geometrics.Rectangle(ll, ur)
       
    """

    def __init__(self, X, Y):
        """
        """
        self.X = X
        self.Y = Y
        if not ((self.X[-1] == self.X[0]) and (self.Y[-1] == self.Y[0])):
            self.X.append(self.X[0])
            self.Y.append(self.Y[0])
            
    def __str__(self):
        """Transform the polygon in string"""
        txt  = "Polygon with vertex: \n"
        for i in range(len(self.X)):
            txt += "      [" + str(self.X[i]) + "," + str(self.Y[i])  + "]\n"
        return txt

    def plot(self, sym="r-", append=plt):
        """TODO"""
        
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(12, 6))
        else:
            ax1 = append
            
        ax1.plot(self.X, self.Y, sym)
        
        return ax1

    def contains(self, point):
        """TODO"""
        return inclusion(self.X, self.Y, point.getX(), point.getY())

    def select(self, track):
        """
        TODO

        Parameters
        ----------
        track : TYPE
            DESCRIPTION.

        Returns
        -------
        t : TYPE
            DESCRIPTION.

        """
        t = tracklib.Track(user_id=track.uid, track_id=track.tid, base=track.base)
        for obs in track:
            if self.contains(obs.position):
                t.addObs(obs)
        return t
    
    def copy(self):
        """TODO"""
        return copy.deepcopy(self)

    # --------------------------------------------------
    # Translation (2D) of shape (dx, dy in ground units)
    # --------------------------------------------------
    def translate(self, dx, dy):
        """TODO"""
        for i in range(len(self.X)):
            self.X[i] = self.X[i] + dx
            self.Y[i] = self.Y[i] + dy

    # --------------------------------------------------
    # Rotation (2D) of shape (theta in radians)
    # --------------------------------------------------
    def rotate(self, theta):
        """TODO"""
        cr = math.cos(theta)
        sr = math.sin(theta)
        for i in range(len(self.X)):
            xr = +cr * self.X[i] - sr * self.Y[i]
            yr = +sr * self.X[i] + cr * self.Y[i]
            self.X[i] = xr
            self.Y[i] = yr

    # --------------------------------------------------
    # Homotehtic transformation (2D) of shape
    # --------------------------------------------------
    def scale(self, h):
        """TODO"""
        for i in range(len(self.X)):
            self.X[i] *= h
            self.Y[i] *= h

    # --------------------------------------------------
    # Polygon area
    # --------------------------------------------------
    def area(self):
        """TODO"""
        aire = 0
        for i in range(len(self.X) - 1):
            aire += self.X[i] * self.Y[i + 1] - self.X[i + 1] * self.Y[i]
        return abs(aire / 2)

    # --------------------------------------------------
    # Polygon centroid
    # --------------------------------------------------
    def centroid(self):
        """
        

        Returns
        -------
        center : array[2]
            DESCRIPTION.

        """
        
        aire = 0
        center = [0, 0]
        dx = self.X[0]
        dy = self.Y[0]
        self.translate(-dx, -dy)
        for i in range(len(self.X) - 1):
            factor = self.X[i] * self.Y[i + 1] - self.X[i + 1] * self.Y[i]
            aire += factor
            center[0] += (self.X[i] + self.X[i + 1]) * factor
            center[1] += (self.Y[i] + self.Y[i + 1]) * factor
        center[0] /= 3 * aire
        center[1] /= 3 * aire
        center[0] += dx
        center[1] += dy
        self.translate(dx, dy)
        return center

    # --------------------------------------------------
    # Test if a polygon is star-shaped
    # --------------------------------------------------
    def isStarShaped(self):
        """TODO"""
        eps = 1e-6
        c = self.centroid()
        # self.plot('k-')
        # plt.plot(c[0], c[1], 'ro')
        for i in range(len(self.X) - 1):
            visee = [
                self.X[i] - eps * (self.X[i] - c[0]),
                self.Y[i] - eps * (self.Y[i] - c[1]),
            ]
            S1 = [c[0], c[1], visee[0], visee[1]]
            intersection = False
            for j in range(len(self.X) - 1):
                S2 = [self.X[j], self.Y[j], self.X[j + 1], self.Y[j + 1]]
                if isSegmentIntersects(S1, S2):
                    intersection = True
                    break
            if intersection:
                # plt.plot([c[0],visee[0]], [c[1],visee[1]], 'r--')
                return False
            # else:
            # plt.plot([c[0],visee[0]], [c[1],visee[1]], 'k--')
        return True

    # --------------------------------------------------
    # Computes angular ratio of polygon star-shaped
    # --------------------------------------------------
    def starShapedRatio(self, resolution=1, inf=1e3):
        """TODO"""
        eps = inf
        c = self.centroid()
        # self.plot('k-')
        N = 0.0
        D = 0.0
        for theta in range(0, 360, math.floor(resolution)):
            visee = [
                c[0] + eps * math.cos(theta * math.pi / 180),
                c[1] + eps * math.sin(theta * math.pi / 180),
            ]
            S1 = [c[0], c[1], visee[0], visee[1]]
            count = 0
            D += 1
            for j in range(len(self.X) - 1):
                S2 = [self.X[j], self.Y[j], self.X[j + 1], self.Y[j + 1]]
                if isSegmentIntersects(S1, S2):
                    count += 1
                if count == 2:
                    N += 1
                    # plt.plot([c[0],visee[0]], [c[1],visee[1]], 'r--')
                    break
            if count == 0:
                N += 1
                # plt.plot([c[0],visee[0]], [c[1],visee[1]], 'r--')
        return 1.0 - N / D

    # --------------------------------------------------
    # Radial signature of a polygon
    # --------------------------------------------------
    def signature(self):
        """
        Radial signature of a polygon
        """
        C = self.centroid()
        S = [0]
        R = [math.sqrt((C[0] - self.X[0]) ** 2 + (C[1] - self.Y[0]) ** 2)]
        N = R[0]
        for i in range(1, len(self.X)):
            S.append(
                math.sqrt(
                    (self.X[i - 1] - self.X[i]) ** 2 + (self.Y[i - 1] - self.Y[i]) ** 2
                )
                + S[i - 1]
            )
            R.append(math.sqrt((C[0] - self.X[i]) ** 2 + (C[1] - self.Y[i]) ** 2))
            N = max(N, R[-1])
        for i in range(len(S)):
            S[i] /= S[-1]
            R[i] /= N
        return [S, R]


# ----------------------------------------
# Function to get enclosing shape
# ----------------------------------------
def boundingShape(track, mode=MODE_ENCLOSING_BBOX):
    """TODO"""
    if mode == MODE_ENCLOSING_BBOX:
        return track.bbox()
    if mode == MODE_ENCLOSING_MBR:
        return minimumBoundingRectangle(track)
    if mode == MODE_ENCLOSING_CIRCLE:
        return minCircle(track)
    if mode == MODE_ENCLOSING_CONVEX:
        return convexHull(track)


def __convexHull(T):
    """TODO

    Finds the convex hull of a set of coordinates, returned as
    a list of x an y coordinates : [x1, y1, x2, y2,...]
    Computation is performed with Jarvis march algorithm
    with O(n^2) time complexity. It may be needed to resample
    track if computation is too long."""

    X = [p[0] for p in T]
    H = [X.index(min(X))]

    while (len(H) < 3) or (H[-1] != H[0]):
        H.append(0)
        for i in range(len(T)):
            if not (right(T[H[-2]], T[H[-1]], T[i])):
                H[-1] = i

    return H


def convexHull(track):
    """TODO

    Finds the convex hull of a track, returned as
    a list of x an y coordinates : [x1, y1, x2, y2,...]
    Computation is performed with Jarvis march algorithm
    with O(n^2) time complexity. It may be needed to resample
    track if computation is too long."""

    T = []
    for i in range(len(track)):
        T.append([track[i].position.getX(), track[i].position.getY()])

    CH = __convexHull(T)

    T2 = []
    for i in range(len(CH)):
        T2.append(T[CH[i]][0])
        T2.append(T[CH[i]][1])
    return T2


def diameter(track):
    """TODO

    Finds longest distance between points on track
    The two selected points are returned in a vector
    along with the minimal distance : [min_dist, idx_p1, idx_p2].
    Exhaustive search in O(n^2) time complexity"""

    dmax = 0
    idmax = [0, 0]

    for i in range(len(track)):
        for j in range(len(track)):
            d = track.getObs(i).distance2DTo(track.getObs(j))
            if d > dmax:
                dmax = d
                idmax = [i, j]
    return [dmax, idmax[0], idmax[1]]


def __circle(p1, p2=None, p3=None):
    """TODO

    Finds circle through 1, 2 or 3 points
    Returns Circle(C, R)
    """
    if not isinstance(p1, ENUCoords):
        print("Error: ENU coordinates are required for min circle computation")
        exit()
    if p2 is None:
        return Circle(p1, 0.0)
    if p3 is None:
        centre = p1 + p2
        centre.scale(0.5)
        return Circle(centre, p1.distance2DTo(p2) / 2)
        
    if collinear(
        [p1.getX(), p1.getY()], [p2.getX(), p2.getY()], [p3.getX(), p3.getY()]
    ):
        logger.warning(str(p1) + "," + str(p2) + "," + str(p3) + " are collinear")
        return None

    if p1.distance2DTo(p2) == 0:
        p2.setX(p2.getX() + random.random() * 1e-10)
        p2.setY(p2.getY() + random.random() * 1e-10)

    if p1.distance2DTo(p3) == 0:
        p3.setX(p3.getX() + random.random() * 1e-10)
        p3.setY(p3.getY() + random.random() * 1e-10)

    if p2.distance2DTo(p3) == 0:
        p3.setX(p3.getX() + random.random() * 1e-10)
        p3.setY(p3.getY() + random.random() * 1e-10)

    C12 = __circle(p1, p2)
    C23 = __circle(p2, p3)
    C13 = __circle(p1, p3)
    CANDIDATS = []

    if C12.center.distance2DTo(p3) < C12.radius:
        CANDIDATS.append(C12)
    if C23.center.distance2DTo(p1) < C23.radius:
        CANDIDATS.append(C23)
    if C13.center.distance2DTo(p2) < C13.radius:
        CANDIDATS.append(C13)

    if len(CANDIDATS) > 0:
        min = CANDIDATS[0].radius
        argmin = 0
        for i in range(len(CANDIDATS)):
            if CANDIDATS[i].radius < min:
                min = CANDIDATS[i].radius
                argmin = i
        return CANDIDATS[argmin]

    x = np.complex(p1.getX(), p1.getY())
    y = np.complex(p2.getX(), p2.getY())
    z = np.complex(p3.getX(), p3.getY())

    w = z - x
    w /= y - x
    c = (x - y) * (w - abs(w) ** 2) / 2j / np.imag(w) - x
    centre = p1.copy()
    centre.setX(-np.real(c))
    centre.setY(-np.imag(c))

    return Circle(centre, np.abs(c + x))


def __welzl(C):
    """
    Finds minimal bounding circle with Welzl's algorithm
    """

    P = C.center
    P = P.copy()
    R = C.radius
    R = R.copy()

    if (len(P) == 0) or (len(R) == 3):
        if len(R) == 0:
            return Circle(ENUCoords(0, 0, 0), 0)
        if len(R) == 1:
            return __circle(R[0])
        if len(R) == 2:
            return __circle(R[0], R[1])
        
        return __circle(R[0], R[1], R[2])
    
    id = random.randint(0, len(P) - 1)
    p = P[id]
    P2 = []
    for i in range(len(P)):
        if i == id:
            continue
        P2.append(P[i])
    P = P2
    D = __welzl(Circle(P, R))

    if D is None:
        return None
    elif p.distance2DTo(D.center) < D.radius:
        return D
    else:
        if not p in R:
            R.append(p)
        return __welzl(Circle(P, R))


def plotPolygon(P, color=[1, 0, 0, 1]):
    """
    Function to plot a polygon from a vector:
    R = [x1,y1,x2,y2,x3,y3,...x1,y1]
    Needs to call plt.show() after this function
    """
    XR = P[::2]
    YR = P[1::2]
    plt.plot(XR, YR, color=color)


def minCircleOfPoints(points):
    """
    Finds minimal bounding circle with Welzl's recursive
    algorithm in O(n) complexity. 
    Output is given as a list [p, R], where p is a Coords object defining circle center
    and R is its radius. Due to recursion limits, only tracks
    with fewer than 800 points can be processed
    """
    if len(points) > 0.5 * sys.getrecursionlimit():
        message = ("Error: too many points in dataset to compute minimal enclosing circle. ")
        message += 'Downsample dataset size, or use "sys.setrecursionlimit('
        message += str(int((2 * len(points)) / 1000) * 1000 + 1000) + ') or higher"'
        print(message)
        exit()
    return __welzl(Circle(points, []))

def minCircle(track):
    """
    Finds minimal bounding circle with Welzl's recursive
    algorithm in O(n) complexity. 
    Output is given as a list [p, R], where p is a Coords object defining circle center
    and R is its radius. Due to recursion limits, only tracks
    with fewer than 800 points can be processed
    """
    
    if not track.getSRID() == "ENU":
        print("Error: ENU coordinates are required for min circle computation")
        exit()

    # centre = track.getFirstObs().position.copy()

    return minCircleOfPoints([obs.position for obs in track])


def minCircleMatrix(track):
    """TODO

    Computes matrix of all min circles in a track.
    M[i,j] gives the radius of the min circle enclosing
    points in track from obs i to obs j (included)"""

    M = np.zeros((track.size(), track.size()))
    for i in range(track.size()):
        # print(i, "/", track.size())
        for j in range(i, track.size() - 1):
            M[i, j] = minCircle(track.extract(i, j)).radius
    M = M + np.transpose(M)
    return M


def fitCircle(track, iter_max=100, epsilon=1e-10):
    """
    
    .. code-block:: python

        circle1 = Geometrics.fitCircle(trace2)
        circle1.plot()
        circle2 = Geometrics.minCircle(trace2)
        circle2.plot()
    
    """

    X = np.ones((3, 1))
    c = track.getCentroid()
    N = track.size()
    X[0] = c.getX()
    X[1] = c.getY()
    J = np.zeros((N, 3))
    B = np.zeros((N, 1))

    for k in range(iter_max):
        for i in range(N):
            obs = track[i].position
            x = obs.getX()
            y = obs.getY()
            R = math.sqrt((x - X[0]) ** 2 + (y - X[1]) ** 2)
            J[i, 0] = 2 * (X[0, 0] - x)
            J[i, 1] = 2 * (X[1, 0] - y)
            J[i, 2] = -2 * R
            B[i, 0] = X[2] - R
        try:
            dX = np.linalg.solve(np.transpose(J) @ J, np.transpose(J) @ B)
            X = X + dX
        except np.linalg.LinAlgError as err:
            print(err)
            return Circle(ENUCoords(0, 0), 0)

        if X[0] != 0:
            NX0 = abs(dX[0] / X[0])
        else:
            NX0 = 0
        if X[1] != 0:
            NX1 = abs(dX[1] / X[1])
        else:
            NX1 = 0
        if X[2] != 0:
            NX2 = abs(dX[2] / X[2])
        else:
            NX2 = 0
        if max(max(NX0, NX1), NX2) < epsilon:
            break

    residuals = [0] * len(track)
    for i in range(len(residuals)):
        residuals[i] = (
            (track[i].position.getX() - X[0]) ** 2
            + (track[i].position.getY() - X[1]) ** 2
            - X[2] ** 2
        )
        sign = -1 * (residuals[i] < 0) + 1 * (residuals[i] > 0)
        residuals[i] = sign * math.sqrt(abs(residuals[i]))
    track.createAnalyticalFeature("#circle_residual", residuals)

    return Circle(ENUCoords(X[0], X[1]), X[2])


"""   
def fitCircle(track):
    #Computes optimal circle fit on track
    #Beta version, with Kalman filter 
    I = np.identity(3)
    P = I*1e10
    H = -1*np.ones((1,3))
    X = np.zeros((3,1)); 
    c = track.getCentroid()
    X[0,0] = c.getX(); X[1,0] = c.getY(); 
    w = 1e-20
    
    L = list(range(len(track)))
    random.shuffle(L)

    for i in L:
        obs = track[i].position; x = obs.getX(); y = obs.getY()
        R = math.sqrt((x-X[0])**2 + (y-X[1])**2)
        z = np.matrix(X[2]-R)
        H[0,0] = (X[0]-x)/R;   H[0,1] = (X[1]-y)/R; 
        K =  P @ np.transpose(H) @ np.linalg.inv(H @ P @ np.transpose(H) + w)
        X = X + K@z
        P = (I - K@H) @ P
            
    return Circle(ENUCoords(X[0,0], X[1,0]), X[2,0])
"""

# ------------------------------------------------------------
# Output :     R = [[x1,y1],[x2,y2],[x3,y3],[x4,y4], area, l, L]
# ------------------------------------------------------------
def __mbr(COORDS):
    """TODO"""

    HULL = __convexHull(COORDS)
    XH = [COORDS[p][0] for p in HULL]
    YH = [COORDS[p][1] for p in HULL]

    BEST_RECTANGLE = []
    RECTANGLE_AREA = 10 ** 301
    BEST_l = 0
    BEST_L = 0

    for i in range(len(HULL) - 1):

        # param = cartesienne([XH[i], YH[i], XH[i+1], YH[i+1]])
        theta = math.atan((YH[i + 1] - YH[i]) / (XH[i + 1] - XH[i]))

        # 3 parameters transformation
        XHR, YHR = transform(theta, XH[i], YH[i], XH, YH)

        mx = min(XHR)
        my = min(YHR)
        if max(YHR) > abs(min(YHR)):
            my = max(YHR)
        Mx = max(XHR)

        XRR = [mx, Mx, Mx, mx, mx]
        YRR = [0, 0, my, my, 0]

        # 3 parameters inverse transformation
        XR, YR = transform_inverse(theta, XH[i], YH[i], XRR, YRR)

        new_area = (Mx - mx) * abs(my)
        if new_area < RECTANGLE_AREA:
            BEST_RECTANGLE = [
                [XR[0], YR[0]],
                [XR[1], YR[1]],
                [XR[2], YR[2]],
                [XR[3], YR[3]],
                [XR[0], YR[0]],
            ]
            RECTANGLE_AREA = new_area
            BEST_l = Mx - mx
            BEST_L = abs(my)

    if BEST_L < BEST_l:
        G = BEST_l
        BEST_l = BEST_L
        BEST_L = G

    return [BEST_RECTANGLE, RECTANGLE_AREA, BEST_l, BEST_L]


def minimumBoundingRectangle(track):
    """TODO"""

    T = []
    for i in range(len(track)):
        T.append([track[i].position.getX(), track[i].position.getY()])

    return __mbr(T)
    
# ------------------------------------------------------------
# Geometric median of a set of points (ENUCoords) is a point 
# in 2D space whose L1 sum of L2 distances to all other points 
# is minimal. Computation is done with Weiszfeld's algorithm.
# Output is the median of points as an ENUCoords point
# ------------------------------------------------------------
def geometricMedian(points, N_ITER_MAX = 100, epsilon_factor = 1e-10):
	
    if (len(points) == 1):
        return points[0].copy
    if (len(points) == 2):
        x0 = 0.5*(points[0].E + points[1].E)
        y0 = 0.5*(points[0].N + points[1].N)
        return ENUCoords(x0, y0)
	
    # Initialization
    xmin = points[0].getX()
    ymin = points[0].getY()
    xmax = points[0].getX()
    ymax = points[0].getY()
    for i in range(1, len(points)):
        xmin = min(xmin, points[i].getX())
        xmax = max(xmax, points[i].getX())
        ymin = min(ymin, points[i].getY())
        ymax = max(ymax, points[i].getY())     
    epsilon = epsilon_factor*math.sqrt((xmax-xmin)**2 + (ymax-ymin)**2)
    x0 = xmin + (xmax-xmin)*random.random()
    y0 = ymin + (ymax-ymin)*random.random()

    # Median computation
    for k in range(N_ITER_MAX):
        xnew = 0; ynew = 0; Z = 0
        for i in range(len(points)):
            di = math.sqrt((x0-points[i].getX())**2 + (y0-points[i].getY())**2)
            xnew += points[i].getX()/di
            ynew += points[i].getY()/di
            Z += 1.0/di
        xnew /= Z
        ynew /= Z
        disp = max(abs(xnew-x0), abs(ynew-y0))

        if (disp < epsilon):
            return ENUCoords(xnew, ynew)
         
        x0 = xnew
        y0 = ynew
        
    print("WARNING: geometric median did not reach convergence")     
    return ENUCoords(xnew, ynew)
     

# ------------------------------------------------------------
# Generic function to get center of a set of points
# ------------------------------------------------------------
MODE_AGG_MEDIAN = 300  # Component-wise median of coordinates
MODE_AGG_L1     = 301  # Geometric median of points
MODE_AGG_L2     = 302  # Standard barycenter of points
MODE_AGG_LInf   = 303  # Center of minimum enclosing circle
# ------------------------------------------------------------
# MODE_MEDIAN and MODE_L2 are computed in 3D. MODE_L1 and 
# MODE_L2 are computed in 2D. MODE_Lp is the "generalized 
# barycenter" of a set of points, and refers to the point 
# (in 2D or 3D space) minimizing the sum of p-th power of 
# distances towards all points in the dataset.
# ------------------------------------------------------------
def centerOfPoints(coordSet, mode=MODE_AGG_L2):

    # ----------------------------------------------
    # Calcul de la médiane marginale
    # ----------------------------------------------
    if mode == MODE_AGG_MEDIAN:
        N = len(coordSet)
        X = []; Y = []; Z = []
        for i in range(N):
            X.append(coordSet[i].E)
            Y.append(coordSet[i].N)
            Z.append(coordSet[i].U)
        x = co_median(X)
        y = co_median(Y)
        z = co_median(Z)
        return ENUCoords(x, y, z)

    # ----------------------------------------------
    # L1 (geometric median) -> Weiszfeld's algorithm
    # ----------------------------------------------
    if mode == MODE_AGG_L1:
        return geometricMedian(coordSet)

    # ----------------------------------------------
    # L2 (geometric mean) -> simple average
    # ----------------------------------------------
    if mode == MODE_AGG_L2:
        N = len(coordSet)
        X = []; Y = []; Z = []
        for i in range(N):
            X.append(coordSet[i].E)
            Y.append(coordSet[i].N)
            Z.append(coordSet[i].U)
        x = co_avg(X)
        y = co_avg(Y)
        z = co_avg(Z)
        return ENUCoords(x, y, z)
        
    
    # ----------------------------------------------
    # LInf (Radius of enclosing circle) -> 
    # ----------------------------------------------
    if mode == MODE_AGG_LInf:
        return minCircleOfPoints(coordSet).center

    print("Unknown mode in 'centerOfPoints' function")
    sys.exit(1)
