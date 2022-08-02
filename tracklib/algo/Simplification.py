# ------------------------- Simplification -------------------------------------
# Class to manage simplification of GPS tracks
# -----------------------------------------------------------------------------

import sys
import math
import numpy as np

import tracklib.util.Geometry as Geometry
import tracklib.core.Operator as Operator

import tracklib.algo.Geometrics as Geometrics
from tracklib.algo.Segmentation import (
    MODE_SEGMENTATION_MINIMIZE,
    MODE_SEGMENTATION_MAXIMIZE,
)
from tracklib.algo.Segmentation import optimalSegmentation

# --------------------------------------------------------------------------
# Circular import (not satisfying solution)
# --------------------------------------------------------------------------
from tracklib.core.Track import Track

MODE_SIMPLIFY_DOUGLAS_PEUCKER = 1
MODE_SIMPLIFY_VISVALINGAM = 2
MODE_SIMPLIFY_SQUARING = 3
MODE_SIMPLIFY_MINIMIZE_LARGEST_DEVIATION = 4
MODE_SIMPLIFY_MINIMIZE_ELONGATION_RATIO = 5
MODE_SIMPLIFY_PRECLUDE_LARGE_DEVIATION = 6
MODE_SIMPLIFY_FREE = 7
MODE_SIMPLIFY_FREE_MAXIMIZE = 8

SQUARING_RECALL = 0.1

# --------------------------------------------------------------------------
# Generic method to simplify a track
# Tolerance is in the unit of track observation coordinates
#     MODE_SIMPLIFY_DOUGLAS_PEUCKER (1)*
#       - tolerance is max allowed deviation with respect to straight line
#   MODE_SIMPLIFY_VISVALINGAM (2)
#       - tolerance is maximal triangle area of 3 consecutive points
#   MODE_SIMPLIFY_SQUARING (3)
#       - tolerance is threshold on flat and right angles
#   MODE_SIMPLIFY_MINIMIZE_LARGEST_DEVIATION (4)
#       - tolerance is typical max deviation with respect to straight line
#   MODE_SIMPLIFY_MINIMIZE_ELONGATION_RATIO (5)
#       - tolerance is typical elongation ratio of min bounding rectangle
#   MODE_SIMPLIFY_PRECLUDE_LARGE_DEVIATION (6)
#       - tolerance is max allowed deviation with respect to straight line
#   MODE_SIMPLIFY_FREE (7)
#       - tolerance is a customed function to minimize
#   MODE_SIMPLIFY_FREE_MAXIMIZE (8)
#       - tolerance is a customed function to maximize
# --------------------------------------------------------------------------
def simplify(track, tolerance, mode=MODE_SIMPLIFY_DOUGLAS_PEUCKER, verbose=True):
    """
    The process "Track simplification" generally returns a new simplified track. 
    Tolerance is in the unit of track observation coordinates.

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
    
    Example:

    .. code-block:: python
    
      tolerance = 50
      trace3 = Simplification.simplify(trace, tolerance, 
    			 Simplification.MODE_SIMPLIFY_VISVALINGAM)
      trace.plot(append = False, sym='g-', label='original track')
      trace3.plot(append = True, sym='b-', label='simplify:visvalingam')
      plt.legend()


    .. figure:: ../../../../_images/simplify_visvalingam.png
       :width: 450px
       :align: center
    
       Figure 1 : Simplification with Visvalingram

    .. note:: Reference: M. Visvalingam & J. D. Whyatt (1993) Line generalisation by repeated elimination of points, The Cartographic Journal, 30:1, 46-51, DOI: 
              `10.1179/000870493786962263 <10.1179/000870493786962263>`_
    
    
    Parameters
    ----------
    :param track Track: GPS track
    :param eps float: length threshold epsilon (sqrt of triangle area)
    :return Track: simplified track

    """
    eps **= 2
    output = track.copy()
    output.addAnalyticalFeature(Geometry.aire_visval, "@aire")
    while 1:
        id = output.operate(Operator.Operator.ARGMIN, "@aire")
        if output.getObsAnalyticalFeature("@aire", id) > eps:
            break
        output.removeObs(id)
        if id > 1:
            output.setObsAnalyticalFeature(
                "@aire", id - 1, Geometry.aire_visval(output, id - 1)
            )
        if id < output.size() - 1:
            output.setObsAnalyticalFeature(
                "@aire", id, Geometry.aire_visval(output, id)
            )
    output.removeAnalyticalFeature("@aire")
    return output



def douglas_peucker(track, eps):
    """
    Function to simplify a GPS track with Douglas-Peucker algorithm.
    
    The Douglas-Peucker algorithm reduce the number of a line by reducing 
    the number of points. The result should keep the original shape.
    
    Example:

    .. code-block:: python
    
      tolerance = 20
      trace2 = Simplification.simplify(trace, tolerance, 
    			 Simplification.MODE_SIMPLIFY_DOUGLAS_PEUCKER)
      trace.plot(append = False, sym='g-')
      trace2.plot(append = True, sym='b-')


    .. figure:: .../../../../_images/simplify_douglaspeucker.png
       :width: 450px
       :align: center
    
       Figure 2 : Simplification with Douglas Peucker


    .. note:: Reference: David Douglas, Thomas Peucker: Algorithms for the 
            reduction of the number of points required to represent a digitized 
            line or its caricature. In Cartographica: The International Journal 
            for Geographic Information and Geovisualization. 
            Volume 10, Issue 2, Pages 112–122, 1973, 
            `https://utpjournals.press/doi/10.3138/FM57-6770-U75U-7727 <https://utpjournals.press/doi/10.3138/FM57-6770-U75U-7727>`_
    		
    Parameters
    ----------
    :param track Track: GPS track
    :param eps float: length threshold epsilon (sqrt of triangle area)
    :return Track: simplified track
    
    """

    L = track.getObsList()

    n = len(L)
    if n <= 2:
        return Track(L)

    dmax = 0
    imax = 0

    for i in range(0, n):
        x0 = L[i].position.getX()
        y0 = L[i].position.getY()
        xa = L[0].position.getX()
        ya = L[0].position.getY()
        xb = L[n - 1].position.getX()
        yb = L[n - 1].position.getY()
        d = Geometry.distance_to_segment(x0, y0, xa, ya, xb, yb)
        if d > dmax:
            dmax = d
            imax = i

    if dmax < eps:
        return Track(
            [L[0], L[n - 1]], user_id=track.uid, track_id=track.tid, base=track.base
        )
    else:
        XY1 = Track(L[0:imax], user_id=track.uid, track_id=track.tid, base=track.base)
        XY2 = Track(L[imax:n], user_id=track.uid, track_id=track.tid, base=track.base)
        return douglas_peucker(XY1, eps) + douglas_peucker(XY2, eps)


# --------------------------------------------------------------------------
# Function to simplify a GPS track with dynamic programming
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
    """TODO"""

    simplified = Track(user_id=track.uid, track_id=track.tid, base=track.base)
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
        R = Geometrics.boundingShape(track.extract(i, j), Geometrics.MODE_ENCLOSING_MBR)
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
        R = Geometrics.boundingShape(track.extract(i, j), Geometrics.MODE_ENCLOSING_MBR)
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
        R = Geometrics.boundingShape(track.extract(i, j), Geometrics.MODE_ENCLOSING_MBR)
        l = min(R[2], R[3])
        return 1e300 * (l > offset) + 1


# --------------------------------------------------------------------------
# 
# --------------------------------------------------------------------------
# Input :
#   - track ::     GPS track
#   - eps   ::     angle threshold on right and flat angles (radians)
# --------------------------------------------------------------------------
# Output : simplified
# --------------------------------------------------------------------------
def squaring(track, eps):
    '''
    Function to simplify a GPS track with squaring algorithm.
    
    
    .. note:: Reference: Lokhat, Imran & Touya, Guillaume. (2016). 
              Enhancing building footprints with squaring operations. 
              Journal of Spatial Information Science. 13. 
              `10.5311/JOSIS.2016.13.276 <http://dx.doi.org/10.5311/JOSIS.2016.13.276>`_


    Parameters
    ----------
    track : TYPE
        DESCRIPTION.
    eps : TYPE
        DESCRIPTION.

    Returns
    -------
    output : TYPE
        DESCRIPTION.

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

