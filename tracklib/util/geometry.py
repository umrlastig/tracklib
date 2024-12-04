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



Definition of some geometric functions

# -------------------------- Geometry Functions -------------------------------
# Geometry Functions  like:
#    - cartesienne
#    - __eval
#    - __right

#    - dist_point_droite
#    - dist_point_to_segment
#    - distance_to_segment

#    - projection_droite
#    - proj_segment
#    - proj_polyligne

#    - triangle_area
#    - aire_visval

#    - isSegmentIntersects
#    - intersection
#    - intersects

#    - inclusion

#    - transform
#    - transform_inverse
#
#    - angleBetweenThreePoints
#    -
# ----------------------------------------------------------------
"""


# For type annotation
from __future__ import annotations   

import math
import numpy as np

import tracklib as tracklib
from tracklib.core import ObsTime, Obs, makeCoords


def cartesienne(segment) -> list[float, float, float, float]:   
    """Fonction equation cartesienne

    :return: liste de paramètres
    """

    parametres = list()

    x1 = segment[0]
    y1 = segment[1]
    x2 = segment[2]
    y2 = segment[3]

    u1 = x2 - x1
    u2 = y2 - y1

    b = -u1
    a = u2

    c = -(a * x1 + b * y1)

    parametres.append(a)
    parametres.append(b)
    parametres.append(c)

    return parametres


# ----------------------------------------
# Fonction de test d'equation de droite
# Entrees : paramatres et coords (x,y)
# Sortie : en particulier 0 si le point
# appartient a la droite
# ----------------------------------------
def __eval(param, x, y):

    a = param[0]
    b = param[1]
    c = param[2]

    return a * x + b * y + c


def right(a, b, c):
    return (a == c) or (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]) < 0


def direction(a, b, c):
    return (c[0] - a[0]) * (b[1] - a[1]) - (b[0] - a[0]) * (c[1] - a[1])


# ----------------------------------------
# Fonction distance point-droite
# Entree : paramètres a,b,c d'une droite,
# coordonnées x et y du point
# Sortie : distance du point à la droite
# ----------------------------------------
def dist_point_droite(param, x, y):

    a = param[0]
    b = param[1]
    c = param[2]

    distance = math.fabs(a * x + b * y + c)
    
    # TODO: ajouter test si a = 0 et b = 0
    #if a * a + b * b == 0:
    #    return -1
    distance /= math.sqrt(a * a + b * b)

    return distance


def dist_point_to_segment(point, segment):
    return dist_point_droite(cartesienne(segment), point.getX(), point.getY())


def distance_to_segment(x0: float, y0: float, x1: float, y1: float, x2: float, y2: float) -> float:   
    """Function to compute distance between a point and a segment

    :param x0: point coordinate X
    :param y0: point coordinate Y
    :param x1: segment first point X
    :param y1: segment first point Y
    :param x2: segment second point X
    :param y2: segment second point Y

    :return: Distance between point and projection coordinates
    """

    # Segment length
    l = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))

    # Normalized scalar product
    psn = ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / l

    X = max(x1, x2)
    Y = max(y1, y2)

    x = min(x1, x2)
    y = min(y1, y2)

    xproj = x1 + psn / l * (x2 - x1)
    yproj = y1 + psn / l * (y2 - y1)

    xproj = min(max(xproj, x), X)
    yproj = min(max(yproj, y), Y)

    # Compute distance
    d = math.sqrt((x0 - xproj) * (x0 - xproj) + (y0 - yproj) * (y0 - yproj))

    return d


def projection_droite(param: tuple[float, float, float], x: float, y: float) -> tuple[float, float]:   
    """
    Fonction projection orthogonale sur une droite

    :param param: Paramètres a,b,c d'une droite
    :param x: X du point à projeter
    :param y: Y du point à projeter
    :return: coordonnée xproj et yproj du point projeté
    """
    a = param[0]
    b = param[1]
    c = param[2]
    
    if b == 0:
        return (x, a)

    xv = -b
    yv = a

    norm = math.sqrt(xv * xv + yv * yv)

    xb = 0
    yb = -c / b

    BH = ((x - xb) * xv + (y - yb) * yv) / norm

    xproj = xb + BH * xv / norm
    yproj = yb + BH * yv / norm

    return xproj, yproj


# ----------------------------------------
# Fonction complète de projection
# Entree : segment, coordonnées x et y du
# point
# Sortie : distance du point au segment et
# coordonnées du projeté
# ----------------------------------------
def proj_segment(segment, x, y):

    param = cartesienne(segment)

    a = param[0]
    b = param[1]
    c = param[2]

    distance = math.fabs(a * x + b * y + c)
    distance /= math.sqrt(a * a + b * b)

    # Récupération des coordonnées du projeté
    xproj, yproj = projection_droite(param, x, y)

    # Test d'inclusion dans le segment

    x1 = segment[0]
    y1 = segment[1]
    x2 = segment[2]
    y2 = segment[3]

    boolx1 = (xproj >= x1) and (xproj <= x2)
    boolx2 = (xproj <= x1) and (xproj >= x2)
    boolx = boolx1 or boolx2

    booly1 = (yproj >= y1) & (yproj <= y2)
    booly2 = (yproj <= y1) & (yproj >= y2)
    booly = booly1 or booly2

    bool_include = boolx and booly

    # Si le projeté est dans le segment
    if bool_include:

        a = param[0]
        b = param[1]
        c = param[2]

        xv = -b
        yv = a

        norm = math.sqrt(xv * xv + yv * yv)

        xb = 0
        yb = -c / b

        BH = ((x - xb) * xv + (y - yb) * yv) / norm

        xproj = xb + BH * xv / norm
        yproj = yb + BH * yv / norm

        return distance, xproj, yproj

    else:
        distance1 = math.sqrt((x - x1) * (x - x1) + (y - y1) * (y - y1))
        distance2 = math.sqrt((x - x2) * (x - x2) + (y - y2) * (y - y2))

        if distance1 <= distance2:
            return distance1, x1, y1
        else:
            return distance2, x2, y2


# -----------------------------------------------
# Fonction complète de projection entre un
#          point et une polyligne
#
# Entree : polyligne, coordonnées x et y du point
# Sortie : distance du point ) la polyligne
#          et coordonnées du projeté
# -----------------------------------------------
def proj_polyligne(Xp, Yp, x, y):

    distmin = 1e400

    for i in range(len(Xp) - 1):

        x1 = Xp[i]
        y1 = Yp[i]
        x2 = Xp[i + 1]
        y2 = Yp[i + 1]
        
        if (abs(x1-x2) + abs(y1-y2) < 1e-16):
            continue

        dist, xp, yp = proj_segment([x1, y1, x2, y2], x, y)
        if dist < distmin:
            distmin = dist
            xproj = xp
            yproj = yp
            iproj = i

    return distmin, xproj, yproj, iproj


# --------------------------------------------------------------------------
# Function to detect if a point is on left or right side of track
# --------------------------------------------------------------------------
# Input :
#   - track       :: Track
#   - x,y         :: coordinate of the point we want to detect the side
# --------------------------------------------------------------------------
# Output : list of sides
#          0 if P is on the line
#         +1 if P is on left side of the track
#         -1 if P is on right side of the track
# --------------------------------------------------------------------------
def detect_side(track, x, y, seuilMemeProj=0.1):
    SIDES = []

    Xp = track.getX()
    Yp = track.getY()

    distmin = 1e400
    INDICES = []
    for i in range(len(Xp) - 1):
        x1 = Xp[i]
        y1 = Yp[i]
        x2 = Xp[i + 1]
        y2 = Yp[i + 1]
        
        if (abs(x1-x2) + abs(y1-y2) < 1e-16):
            continue

        dist, xp, yp = proj_segment([x1, y1, x2, y2], x, y)

        if abs(dist - distmin) < seuilMemeProj:
            if dist < distmin:
                distmin = dist
            INDICES.append(i)
        elif dist < distmin:
            distmin = dist
            INDICES = []
            INDICES.append(i)

    for iproj in INDICES:
        xa = track[iproj].position.getX()
        ya = track[iproj].position.getY()
        xb = track[iproj+1].position.getX()
        yb = track[iproj+1].position.getY()

        pdt = (xb-xa)*(y-ya) - (yb-ya)*(x-xa)

        dist, xp, yp = proj_segment([xa, ya, xb, yb], x, y)

        if pdt > 0:
            SIDES.append((dist, xp, yp, 1, iproj))
        elif pdt < 0:
            SIDES.append((dist, xp, yp, -1, iproj))
        else:
            SIDES.append((dist, xp, yp, 0, iproj))

    return SIDES


# --------------------------------------------------------------------------
# Function to compute area of triangle with cross product
# --------------------------------------------------------------------------
# Input :
#   - x0, y0         ::     point 1 coordinates
#   - x1, y1         ::     point 2 coordinates
#    - x2, y2         ::     point 3 coordinates
# --------------------------------------------------------------------------
# Output : area of P1P2P3 in coordinate units
# --------------------------------------------------------------------------
def triangle_area(x0, y0, x1, y1, x2, y2):
    return 0.5 * abs((x1 - x0) * (y2 - y1) - (x2 - x1) * (y1 - y0))


# =============================================================================
""" Pour calculer l'aire des triangles dans Visvalingam """


def aire_visval(track, i):
    x0 = track.getObs(i - 1).position.getX()
    y0 = track.getObs(i - 1).position.getY()
    x1 = track.getObs(i).position.getX()
    y1 = track.getObs(i).position.getY()
    x2 = track.getObs(i + 1).position.getX()
    y2 = track.getObs(i + 1).position.getY()
    return triangle_area(x0, y0, x1, y1, x2, y2)


# ----------------------------------------
# Fonction booleenne d'intersection
# Entrees : segment1 et segment2
# Sortie : true s'il y a intersection
# ----------------------------------------
def isSegmentIntersects(segment1, segment2):

    param_1 = cartesienne(segment1)
    param_2 = cartesienne(segment2)

    # a1 = param_1[0]
    # b1 = param_1[1]
    # c1 = param_1[2]

    # a2 = param_2[0]
    # b2 = param_2[1]
    # c2 = param_2[2]

    x11 = segment1[0]
    y11 = segment1[1]
    x12 = segment1[2]
    y12 = segment1[3]

    x21 = segment2[0]
    y21 = segment2[1]
    x22 = segment2[2]
    y22 = segment2[3]

    val11 = __eval(param_1, x21, y21)
    val12 = __eval(param_1, x22, y22)

    val21 = __eval(param_2, x11, y11)
    val22 = __eval(param_2, x12, y12)

    val1 = val11 * val12
    val2 = val21 * val22

    return (val1 <= 0) & (val2 <= 0)


# ----------------------------------------
# Intersection between 2 tracks
# withTime: time constraint (in secs)
# (-1 if no time constraint)
# ----------------------------------------
def intersection(track1, track2, withTime=-1):

    if not (track1.getSRID() == track2.getSRID()):
        print("Error: tracks must have same SRID to compute intersections")
        exit()

    I = tracklib.Track()
    TMP_I = []
    TMP_J = []
    TMP_TPS2 = []

    for i in range(len(track1) - 1):

        x11 = track1[i].position.getX()
        y11 = track1[i].position.getY()
        x12 = track1[i + 1].position.getX()
        y12 = track1[i + 1].position.getY()
        seg1 = [x11, y11, x12, y12]

        for j in range(len(track2) - 1):

            x21 = track2[j].position.getX()
            y21 = track2[j].position.getY()
            x22 = track2[j + 1].position.getX()
            y22 = track2[j + 1].position.getY()
            seg2 = [x21, y21, x22, y22]

            if isSegmentIntersects(seg1, seg2):
                P1 = cartesienne(seg1)
                P2 = cartesienne(seg2)
                A = np.zeros((2, 2))
                B = np.zeros((2, 1))
                A[0, 0] = P1[0]
                A[0, 1] = P1[1]
                B[0, 0] = -P1[2]
                A[1, 0] = P2[0]
                A[1, 1] = P2[1]
                B[1, 0] = -P2[2]

                X = np.linalg.solve(A, B)

                x = X[0, 0]
                y = X[1, 0]
                p = makeCoords(x, y, 0, track1.getSRID())

                # Linear interpolation on track 1
                w1 = p.distance2DTo(track1[i].position)
                w2 = p.distance2DTo(track1[i + 1].position)
                p.setZ(
                    (
                        w1 * track1[i + 1].position.getZ()
                        + w2 * track1[i].position.getZ()
                    )
                    / (w1 + w2)
                )
                t1 = track1[i].timestamp.toAbsTime()
                t2 = track1[i].timestamp.toAbsTime()
                ta = (w1 * t2 + w2 * t1) / (w1 + w2)

                # Linear interpolation on track 2
                w1 = p.distance2DTo(track2[j].position)
                w2 = p.distance2DTo(track2[j + 1].position)
                t1 = track2[i].timestamp.toAbsTime()
                t2 = track2[i].timestamp.toAbsTime()
                tb = (w1 * t2 + w2 * t1) / (w1 + w2)

                # Add intersection
                if (withTime == -1) or (abs(tb - ta) < withTime):
                    I.addObs(Obs(p, ObsTime.readUnixTime(ta)))
                    TMP_TPS2.append(ObsTime.readUnixTime(tb))
                    TMP_I.append(i)
                    TMP_J.append(j)

    if I.size() > 0:
        I.createAnalyticalFeature("timestamp2", TMP_TPS2)
        I.createAnalyticalFeature("id1", TMP_I)
        I.createAnalyticalFeature("id2", TMP_J)

    return I


# ----------------------------------------
# Intersection between 2 tracks (boolean)
# ----------------------------------------
def intersects(track1, track2):

    for i in range(len(track1) - 1):

        x11 = track1[i].position.getX()
        y11 = track1[i].position.getY()
        x12 = track1[i + 1].position.getX()
        y12 = track1[i + 1].position.getY()
        seg1 = [x11, y11, x12, y12]

        for j in range(len(track2) - 1):

            x21 = track2[j].position.getX()
            y21 = track2[j].position.getY()
            x22 = track2[j + 1].position.getX()
            y22 = track2[j + 1].position.getY()
            seg2 = [x21, y21, x22, y22]

            if isSegmentIntersects(seg1, seg2):
                return True

    return False


# --------------------------------------------------------
# Fonction booleenne d'inlcusion d'un pt dans un polygone
# Un polygone est defini comme une liste de points :
# --------------------------------------------------------
def inclusion(X, Y, x, y):

    cmax = 2 * max(np.max(X), np.max(Y))
    segment = list()

    segment.append(x)
    segment.append(y)
    segment.append(cmax)
    segment.append(cmax)

    n = 0  # Number of intersections

    for i in range(len(X) - 1):

        edge = list()
        edge.append(X[i])
        edge.append(Y[i])
        edge.append(X[i + 1])
        edge.append(Y[i + 1])

        if isSegmentIntersects(segment, edge):
            n += 1

    return n % 2 == 1


def transform(theta, tx, ty, X, Y):

    XR = [0] * len(X)
    YR = [0] * len(Y)

    ct = math.cos(theta)
    st = math.sin(theta)

    for j in range(len(X)):
        XR[j] = ct * (X[j] - tx) + st * (Y[j] - ty)
        YR[j] = -st * (X[j] - tx) + ct * (Y[j] - ty)

    return XR, YR


def transform_inverse(theta, tx, ty, X, Y):

    XR = [0] * len(X)
    YR = [0] * len(Y)

    ct = math.cos(theta)
    st = math.sin(theta)

    for j in range(len(X)):
        XR[j] = ct * X[j] - st * Y[j] + tx
        YR[j] = st * X[j] + ct * Y[j] + ty

    return XR, YR


# Fonction de calcul de l'azimut (en °)
# Entrées : coordonnées de P1 et P2
# Sortie : azimut (en °) de P1 vers P2
def azimut(x1, y1, x2, y2):

    dx = x2 - x1
    dy = y2 - y1

    if (dx == 0) and (dy == 0):
        print("Erreur : les points p1 et p2 doivent être distincts")
        return 0

    q = math.sqrt(dx * dx + dy * dy) + dy
    if q == 0:
        azimut = 0
    else:
        azimut = 2 * math.atan(dx / q) * 180 / math.pi

    if azimut < 0:
        azimut += 360

    return azimut


def collinear(p1, p2, p3):
    """
    Parameters
    ----------
    p1, p2, p3 : [x, y]

    Returns
    -------
    bool
        DESCRIPTION.

    """
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    x3 = p3[0]
    y3 = p3[1]

    xVectP1P2 = x2 - x1
    yVectP1P2 = y2 - y1
    xVectP1P3 = x3 - x1
    yVectP1P3 = y3 - y1

    if xVectP1P2 * yVectP1P3 - xVectP1P3 * yVectP1P2 == 0:
        # points are collinear
        return True
    else:
        # Not collinear
        return False


def angleBetweenThreePoints(o1, o2, o3):
    """
    Compute angle between three points (the angle is calculated for the middle point).

    :param float o_1: first point
    :param float o_2: second point
    :param float o_3: third point
    :return: angle in radian
    """
    
    x1 = o1.position.getX()
    x2 = o2.position.getX()
    x3 = o3.position.getX()
    y1 = o1.position.getY()
    y2 = o2.position.getY()
    y3 = o3.position.getY()

    # 3 points confondus
    if x1 == x2 and x2 == x3 and y1 == y2 and y2 == y3:
        return 0
    
    # 2 points confondus
    if x1 == x2 and y1 == y2:
        return 0
    if x1 == x3 and y1 == y3:
        return 0
    if x2 == x3 and y2 == y3:
        return 0
    
    # print (x1, x2, x3, y1, y2, y3)
    
    num = (x1 - x2) * (x3 - x2) + (y1 - y2) * (y3 - y2)
    den = math.sqrt((x1-x2)**2 + (y1-y2)**2) * math.sqrt((x3-x2)**2 + (y3-y2)**2)
    
    r = num / den
    if r > 1:
        r = 1
    if r < -1:
        r = -1
        
    return math.acos(r)
