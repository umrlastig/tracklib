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



**Simplification of GPS tracks**

"""


import sys
import math
import numpy as np

import tracklib as tracklib
from tracklib.util import (aire_visval, 
                           distance_to_segment,
                           boundingShape, MODE_ENCLOSING_MBR)
from tracklib.core import Operator
from tracklib.algo import (MODE_SEGMENTATION_MINIMIZE, MODE_SEGMENTATION_MAXIMIZE,
                           optimalSegmentation, compare,
                           MODE_COMPARISON_POINTWISE)


MODE_SIMPLIFY_DOUGLAS_PEUCKER = 1
MODE_SIMPLIFY_VISVALINGAM = 2
MODE_SIMPLIFY_SQUARING = 3
MODE_SIMPLIFY_MINIMIZE_LARGEST_DEVIATION = 4
MODE_SIMPLIFY_MINIMIZE_ELONGATION_RATIO = 5
MODE_SIMPLIFY_PRECLUDE_LARGE_DEVIATION = 6
MODE_SIMPLIFY_FREE = 7
MODE_SIMPLIFY_FREE_MAXIMIZE = 8

SQUARING_RECALL = 0.1


def simplify(track, tolerance, mode=MODE_SIMPLIFY_DOUGLAS_PEUCKER, verbose=True):
    """
    Generic method to simplify a track. The process "Track simplification" 
    generally returns a new simplified track. Tolerance is in the unit 
    of track observation coordinates.
    
    Differents modes of simplification are implemented in tracklib:
        
    - MODE_SIMPLIFY_DOUGLAS_PEUCKER (1)
          tolerance is max allowed deviation with respect to straight line
    - MODE_SIMPLIFY_VISVALINGAM (2)
          tolerance is maximal triangle area of 3 consecutive points
    - MODE_SIMPLIFY_SQUARING (3)
          tolerance is threshold on flat and right angles
    - MODE_SIMPLIFY_MINIMIZE_LARGEST_DEVIATION (4)
          tolerance is typical max deviation with respect to straight line
    - MODE_SIMPLIFY_MINIMIZE_ELONGATION_RATIO (5)
          tolerance is typical elongation ratio of min bounding rectangle
    - MODE_SIMPLIFY_PRECLUDE_LARGE_DEVIATION (6)
          tolerance is max allowed deviation with respect to straight line
    - MODE_SIMPLIFY_FREE (7)
          tolerance is a customed function to minimize
    - MODE_SIMPLIFY_FREE_MAXIMIZE (8)
          tolerance is a customed function to maximize

    """
    if mode == MODE_SIMPLIFY_DOUGLAS_PEUCKER:
        return douglas_peucker(track, tolerance)
    if mode == MODE_SIMPLIFY_VISVALINGAM:
        return visvalingam(track, tolerance)
    if mode == MODE_SIMPLIFY_SQUARING:
        return squaring(track, tolerance)
    if mode == MODE_SIMPLIFY_MINIMIZE_LARGEST_DEVIATION:
        return optimalSimplification(
            track, __cost_largest_deviation, tolerance, verbose
        )
    if mode == MODE_SIMPLIFY_MINIMIZE_ELONGATION_RATIO:
        return optimalSimplification(track, __cost_mbr_ratio, tolerance, verbose)
    if mode == MODE_SIMPLIFY_PRECLUDE_LARGE_DEVIATION:
        return optimalSimplification(
            track, __cost_largest_deviation_strict, tolerance, verbose
        )
    if mode == MODE_SIMPLIFY_FREE:
        return optimalSimplification(track, tolerance, None, verbose)
    if mode == MODE_SIMPLIFY_FREE_MAXIMIZE:
        max = MODE_SEGMENTATION_MAXIMIZE
        return optimalSimplification(track, tolerance, None, max, verbose)
    sys.exit("Error: track simplification mode " + (str)(mode) + " not implemented yet")



def visvalingam (track, eps):
    """
    Function to simplify a GPS track with Visvalingam algorithm.

    The Visvalingram algorithm simplify the geometry of the track by reducing
    the number of points but the result presents less angular results than
    the Douglas-Peucker algorithm.

    Parameters
    ----------
    :param track Track: GPS track
    :param eps float: length threshold epsilon (sqrt of triangle area)
    :return Track: simplified track

    """
    eps **= 2
    output = track.copy()
    output.addAnalyticalFeature(aire_visval, "@aire")
    while 1:
        id = output.operate(Operator.ARGMIN, "@aire")
        if output.getObsAnalyticalFeature("@aire", id) > eps:
            break
        output.removeObs(id)
        if id > 1:
            output.setObsAnalyticalFeature(
                "@aire", id - 1, aire_visval(output, id - 1)
            )
        if id < output.size() - 1:
            output.setObsAnalyticalFeature(
                "@aire", id, aire_visval(output, id)
            )
    output.removeAnalyticalFeature("@aire")
    return output



def douglas_peucker (track, eps):
    """
    Function to simplify a GPS track with Douglas-Peucker algorithm.

    The Douglas-Peucker algorithm reduce the number of a line by reducing
    the number of points. The result should keep the original shape.

    Parameters
    ----------
    :param track Track: GPS track
    :param eps float: length threshold epsilon (sqrt of triangle area)
    :return Track: simplified track

    """

    L = track.getObsList()

    n = len(L)
    if n <= 2:
        return tracklib.Track(L)

    dmax = 0
    imax = 0

    for i in range(0, n):
        x0 = L[i].position.getX()
        y0 = L[i].position.getY()
        xa = L[0].position.getX()
        ya = L[0].position.getY()
        xb = L[n - 1].position.getX()
        yb = L[n - 1].position.getY()
        d = distance_to_segment(x0, y0, xa, ya, xb, yb)
        if d > dmax:
            dmax = d
            imax = i

    if dmax < eps:
        return tracklib.Track(
            [L[0], L[n - 1]], user_id=track.uid, track_id=track.tid, base=track.base
        )
    else:
        XY1 = tracklib.Track(L[0:imax], user_id=track.uid, track_id=track.tid, base=track.base)
        XY2 = tracklib.Track(L[imax:n], user_id=track.uid, track_id=track.tid, base=track.base)
        return douglas_peucker(XY1, eps) + douglas_peucker(XY2, eps)


# --------------------------------------------------------------------------
#
# --------------------------------------------------------------------------
# Input :
#   - track ::     GPS track
#   - cost  ::     A cost function that should be minimized or maximized
#   - eps   ::     A threshold (used as global parameter in cost function
#   - mode  ::     To specify if cost must be minimized or maximized
# --------------------------------------------------------------------------
# Output : simplified
# --------------------------------------------------------------------------
def optimalSimplification(track, cost, eps, mode=MODE_SEGMENTATION_MINIMIZE):
    """
    Function to simplify a GPS track with dynamic programming.

    """

    simplified = tracklib.Track(user_id=track.uid, track_id=track.tid, base=track.base)
    segmentation = optimalSegmentation(track, cost, eps)

    for i in range(len(segmentation)):
        simplified.addObs(track.getObs(segmentation[i]).copy())

    return simplified


# --------------------------------------------------------------------------
# A list of cost functions for free segmentation
# --------------------------------------------------------------------------

# ------------------------------------------------------------
# Constraint on largest deviation:
# Width of MBR + offset penalty (used with MINIMIZATION)
# ------------------------------------------------------------
def __cost_largest_deviation(track, i, j, offset):
    """TODO"""
    if j <= i + 1:
        return offset
    else:
        R = boundingShape(track.extract(i, j), MODE_ENCLOSING_MBR)
        return min(R[2], R[3]) + offset


# ------------------------------------------------------------
# Constraint on track elongation
# l/L ratio of MBR + offset penalty (used with MINIMIZATION)
# ------------------------------------------------------------
def __cost_mbr_ratio(track, i, j, offset):
    """TODO"""
    if j <= i + 1:
        return offset
    else:
        R = boundingShape(track.extract(i, j), MODE_ENCLOSING_MBR)
        l = min(R[2], R[3])
        L = max(R[2], R[3])
        return l / L + offset


# ------------------------------------------------------------
# Strinct constraint on largest deviation
# Width should be lower than offset + unit penalty (used with MINIMIZATION)
# ------------------------------------------------------------
def __cost_largest_deviation_strict(track, i, j, offset):
    """TODO"""
    if j <= i + 1:
        return offset
    else:
        R = boundingShape(track.extract(i, j), MODE_ENCLOSING_MBR)
        l = min(R[2], R[3])
        return 1e300 * (l > offset) + 1



def squaring (track, eps):
    '''
    Function to simplify a GPS track with squaring algorithm.

    Parameters
    ----------
    :param track Track: GPS track
    :param eps float: angle threshold on right and flat angles (radians)
    :return Track: simplified track

    '''

    N = len(track)

    CR = []
    for i in range(0, N-1):
        p0 = track[(i-1)%N].position
        p1 = track[i].position
        p2 = track[(i+1)%N].position
        du = p0.distanceTo(p1)
        dv = p1.distanceTo(p2)
        x0 = p0.getX(); x1 = p1.getX(); x2 = p2.getX()
        y0 = p0.getY(); y1 = p1.getY(); y2 = p2.getY()
        ux = x1-x0; uy = y1-y0
        vx = x2-x1; vy = y2-y1
        if du*dv != 0:
            arg = max(min((ux*vx + uy*vy)/(du*dv), 1), -1)
            angle = math.acos(arg)
            #if abs(angle) < eps:
                #p1.plot('go')
                #print(i, "FLAT")
            if abs(angle-math.pi/2) < eps:
                #p1.plot('ro')
                CR.append(i)
        else:  # on a que 2 points
            print("Warning: identical points")

    X = [v for pair in zip(track.getX(), track.getY()) for v in pair]

    for iter in range(5):
        J = SQUARING_RECALL*np.eye(2*N)
        B = [v for pair in zip(track.getX(), track.getY()) for v in pair]
        B = [SQUARING_RECALL*(B[j] - X[j]) for j in range(len(X))]
        for idx in CR:
            x0 = X[2*(idx-1)];   x1 = X[2*idx];   x2 = X[2*(idx+1)]
            y0 = X[2*(idx-1)+1]; y1 = X[2*idx+1]; y2 = X[2*(idx+1)+1]
            constraint = [0]*(2*N)
            constraint[2*idx-2] = -(x2-x1)
            constraint[2*idx-1] = -(y2-y1)
            constraint[2*idx-0] =  (x2-2*x1+x0)
            constraint[2*idx+1] =  (y2-2*y1+y0)
            constraint[2*idx+2] =  (x1-x0)
            constraint[2*idx+3] =  (y1-y0)
            J = np.vstack([J, constraint])
            B.append(-((x1-x0)*(x2-x1) + (y1-y0)*(y2-y1)))
        B = np.array(B)
        dX = np.linalg.solve(J.transpose()@J, J.transpose()@B)
        #print(dX)
        for i in range(len(X)):
            X[i] += dX[i]
    output = track.copy()
    for i in range(len(output)):
        output[i].position.setX(X[2*i])
        output[i].position.setY(X[2*i+1])
    return output

'''
    for iter in range(5):
        print("ITER ", iter)
        J = np.eye(2*N)
        B = [v for pair in zip(track.getX(), track.getY()) for v in pair]
        B = [B[j] - X[j] for j in range(len(X))]
        for i in range(0,N-1):
            p0 = track[(i-1)%N].position
            p1 = track[i].position
            p2 = track[(i+1)%N].position
            du = p0.distanceTo(p1)
            dv = p1.distanceTo(p2)
            x0 = p0.getX(); x1 = p1.getX(); x2 = p2.getX()
            y0 = p0.getY(); y1 = p1.getY(); y2 = p2.getY()
            ux = x1-x0; uy = y1-y0
            vx = x2-x1; vy = y2-y1
            angle = math.acos((ux*vx + uy*vy)/(du*dv))
            #if abs(angle) < eps:
                #p1.plot('go')
                #print(i, "FLAT")
            if abs(angle-math.pi/2) < eps:
                p1.plot('ro')
                constraint = [0]*(2*N)
                constraint[2*i-2] = -(x2-x1)
                constraint[2*i-1] = -(y2-y1)
                constraint[2*i-0] =  (x2-2*x1+x0)
                constraint[2*i+1] =  (y2-2*y1+y0)
                constraint[2*i+2] =  (x1-x0)
                constraint[2*i+3] =  (y1-y0)
                J = np.vstack([J, constraint])
                B.append(-((x1-x0)*(x2-x1) + (y1-y0)*(y2-y1)))
                #print(i, "RIGHT")
        B = np.array(B)
        dX = np.linalg.solve(J.transpose()@J, J.transpose()@B)
        print(B)
        for i in range(len(X)):
            X[i] += dX[i]
    output = track.copy()
    for i in range(len(output)):
        output[i].position.setX(X[2*i])
        output[i].position.setY(X[2*i+1])
    #output.loop()
'''

# =============================================================================
#    MEASURES

def compareWithDouglasPeuckerSimplification(track, threshold):
    '''
    retourne le nombre de points de la ligne la plus généralisée 
    avec Douglas Peucker et qui respecte une qualité donnée avec threshold.
    
    :param track: TODO
    :param threshold: qualité à ne pas dépasser, détermine le seuil pour DP
    '''
    
    # On prend tous les seuils de 1m à longueur de la bbox ?
    sup = max(int(track.bbox().getDx()), int(track.bbox().getDy()))
    
    S = []
    for tolerance in range(1, sup):
        track1 = douglas_peucker(track, tolerance)
        #print (track.size(), track1.size(), tolerance)
        # TODO: à revoir (modif dans comparaison)
        m = min(track.size(), track1.size())
        err = compare(track[0:m], track1[0:m], mode=MODE_COMPARISON_POINTWISE, p=2)
        if err != None and err < threshold:
            S.append(tolerance)
        else:
            # La fonction compare est croissante, donc on peut stopper quand
            # on a dépassé le seuil
            break

    if len(S) > 0:
        index_max = max(range(len(S)), key=S.__getitem__)
        print ('index max:', index_max)
        track1 = douglas_peucker(track, S[index_max])
        return track1.size()
    else:
        return 


def averageOffsetDistance(track, threshold):
    '''
    Strength of Line Simplification.
    Song, Jia & Miao, Ru. (2016). A Novel Evaluation Approach for Line Simplification 
    Algorithms towards Vector Map Visualization. ISPRS International Journal of 
    Geo-Information. 5. 223. 10.3390/ijgi5120223. 
    '''
    
    trackSimplified = douglas_peucker(track, threshold)
    trackSimplified.plot('r-')
    
    offsetDistance = 0
    for o in track:
        # On cherche la plus petite distance à TS
        di = sys.float_info.max
        for i in range(0, trackSimplified.size()-1):
            p1ts = trackSimplified.getObs(i).position
            p2ts = trackSimplified.getObs(i+1).position
            d = distance_to_segment(o.position.getX(), o.position.getY(), 
                                    p1ts.getX(), p1ts.getY(), p2ts.getX(), p2ts.getY())
            if d < di:
                di = d
        
        offsetDistance += di
    
    return offsetDistance / track.size()




