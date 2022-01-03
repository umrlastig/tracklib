# ------------------------- Simplification -------------------------------------
# Class to manage simplification of GPS tracks
# -----------------------------------------------------------------------------

import sys

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
MODE_SIMPLIFY_MINIMIZE_LARGEST_DEVIATION = 3
MODE_SIMPLIFY_MINIMIZE_ELONGATION_RATIO = 4
MODE_SIMPLIFY_PRECLUDE_LARGE_DEVIATION = 5
MODE_SIMPLIFY_FREE = 6
MODE_SIMPLIFY_FREE_MAXIMIZE = 7

# --------------------------------------------------------------------------
# Generic method to simplify a track
# Tolerance is in the unit of track observation coordinates
#     MODE_SIMPLIFY_DOUGLAS_PEUCKER (1)*
#       - tolerance is max allowed deviation with respect to straight line
#   MODE_SIMPLIFY_VISVALINGAM (2)
#       - tolerance is maximal triangle area of 3 consecutive points
#   MODE_SIMPLIFY_MINIMIZE_LARGEST_DEVIATION (3)
#       - tolerance is typical max deviation with respect to straight line
#   MODE_SIMPLIFY_MINIMIZE_ELONGATION_RATIO (4)
#       - tolerance is typical elongation ratio of min bounding rectangle
#   MODE_SIMPLIFY_PRECLUDE_LARGE_DEVIATION (5)
#       - tolerance is max allowed deviation with respect to straight line
#   MODE_SIMPLIFY_FREE (6)
#       - tolerance is a customed function to minimize
#   MODE_SIMPLIFY_FREE_MAXIMIZE (7)
#       - tolerance is a customed function to maximize
# --------------------------------------------------------------------------
def simplify(track, tolerance, mode=MODE_SIMPLIFY_DOUGLAS_PEUCKER, verbose=True):
    """TODO

    Simplify a track"""
    if mode == MODE_SIMPLIFY_DOUGLAS_PEUCKER:
        return douglas_peucker(track, tolerance)
    if mode == MODE_SIMPLIFY_VISVALINGAM:
        return visvalingam(track, tolerance)
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


# --------------------------------------------------------------------------
# Function to simplify a GPS track with Visvalingam algorithm
# --------------------------------------------------------------------------
# Input :
#   - track ::     GPS track
#   - eps   ::     length threshold epsilon (sqrt of triangle area)
# --------------------------------------------------------------------------
# Output : simplified
# --------------------------------------------------------------------------
def visvalingam(track, eps):
    """TODO"""
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


# --------------------------------------------------------------------------
# Function to simplify a GPS track with Douglas-Peucker algorithm
# --------------------------------------------------------------------------
# Input :
#   - track ::     GPS track
#   - eps   ::     length threshold epsilon
# --------------------------------------------------------------------------
# Output : simplified
# --------------------------------------------------------------------------
def douglas_peucker(track, eps):
    """TODO"""

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
