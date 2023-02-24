"""Moduke to manage mapping of GPS tracks on geographic features"""

# For type annotation
from __future__ import annotations   

import math
import progressbar
import numpy as np
import matplotlib.pyplot as plt

import tracklib.util.Geometry as Geometry
import tracklib.algo.Cinematics as Cinematics
import tracklib.algo.Dynamics as Dynamics

from tracklib.core.Obs import Obs
from tracklib.core.ObsCoords import ENUCoords
from tracklib.core.Operator import Operator
from tracklib.core.Track import Track
from tracklib.core.TrackCollection import TrackCollection

# --------------------------------------------------------------------------
# Utils function for map-matching
# --------------------------------------------------------------------------
def __projOnTrack(point, track):
    """TODO"""
    # distmin, xproj, yproj, iproj
    proj = Geometry.proj_polyligne(
        track.getX(), track.getY(), point.getX(), point.getY()
    )
    # ENUCoords projete, distmin, iproj
    return ENUCoords(proj[1], proj[2], 0), proj[0], proj[3]


def __distToNode(track, coord, i, end=0):
    """TODO"""
    si1 = track["abs_curv", i]
    si2 = track["abs_curv", i + 1]
    if end == 0:
        return si1 + track[i].position.distance2DTo(coord)
    if end == 1:
        return (
            track["abs_curv", len(track) - 1]
            - si2
            + track[i + 1].position.distance2DTo(coord)
        )
    return None


# --------------------------------------------------------------------------
# Map-matching of a track on a network with Hidden Markov Model
# Based on popular Newson & Krumm paper
# --------------------------------------------------------------------------
def __states(track, k):
    """TODO"""
    return STATES[k]


def __obs_log(s, y, k, track):
    """TODO"""
    obs_noise = track["obs_noise", k]
    return math.exp(-((s[0].distance2DTo(y) / obs_noise) ** 2))


def __tst_log(s1, s2, k, track):
    """TODO"""
    dtopo = net.distanceBtwPts(s1[1], s1[2], s2[1], s2[2])
    dgeom = s1[0].distance2DTo(s2[0])
    return math.exp(-(dtopo - dgeom) / 10.0)


def __mapOnNetwork (
    track, network, obs_noise=50, transition_cost=10, search_radius=50, 
    debug=False):
    """TODO"""
    
    # print (search_radius, obs_noise, transition_cost)

    if debug:
        f1 = open("observation.dat", "a")
        #f2 = open("transition.dat", "a")

    track.createAnalyticalFeature("obs_noise", obs_noise)
    verbose = True
    global STATES
    global net
    STATES = []
    net = network
    to_run = range(len(track))
    
    if verbose:
        print("Map-matching preparation...")
        to_run = progressbar.progressbar(to_run)
    
    for i in to_run:
        STATES.append([])
        p = track[i].position
        E = network.spatial_index.neighborhood(p, unit=1)
        if E != None:
            for elem in E:
                eg = network.EDGES[network.getEdgeId(elem)].geom
                p, d, v = __projOnTrack(track[i].position, eg)
                if d < search_radius:
                    STATES[-1].append (
                        (p, elem, __distToNode(eg, p, v, 0), __distToNode(eg, p, v, 1))
                    )
                    if debug:
                        wkt = Track([Obs(track[i].position), Obs(p)]).toWKT()
                        f1.write(str(i) + ' "' + wkt + '" ' + str(d) + "\n")
    
    model = Dynamics.HMM()
    model.setStates(__states)
    model.setTransitionModel(__tst_log)
    model.setObservationModel(__obs_log)
    
    model.estimate(
        track,
        obs=["x", "y"],
        mode=Dynamics.MODE_OBS_AS_2D_POSITIONS,
        verbose=verbose * Dynamics.MODE_VERBOSE_PROGRESS,
    )
    
    #for k in progressbar.progressbar(range(len(track))):
    #    X = [track[k].position.getX(), track["hmm_inference", k][0].getX()]
    #    Y = [track[k].position.getY(), track["hmm_inference", k][0].getY()]
    #    plt.plot(X, Y, "r--", linewidth=1.4)
    #    track[k].position.setX(track["hmm_inference", k][0].getX())
    #    track[k].position.setY(track["hmm_inference", k][0].getY())
    

    """
    for k in range(len(STATES)-1):
        S1 = __states(track, k)
        S2 = __states(track, k+1)
        for s1 in S1:
            for s2 in S2:
                transition = __tst_log(s1, s2, k, track)
                observation = __obs_log(s1, track[k].position, k, track)
                if debug:
                    wkt = Track([Obs(s1[0]), Obs(s2[0])]).toWKT()
                    f2.write(str(k) + " \""+wkt+"\" " + str(transition) + "\n")
    """
    if debug:
        f1.close()
        #f2.close()
    

def mapOnNetwork(
    tracks, network, gps_noise=50, transition_cost=10, search_radius=50, debug=False
):
    """
    Map-matching on a network.
    """
    
    if isinstance(tracks, Track):
        tracks = TrackCollection([tracks])
    for track in tracks:
        __mapOnNetwork(track, network, gps_noise, transition_cost, search_radius, debug)


def mapOnRaster(track, raster):
    """
    Raster data transfer to track.
    Add an analytical feature for each grid in the raster. 
    
    :return: void
    """
    
    # create a new empty analytical feature for each raster band
    for i in range(1, len(raster.bands)+1):
        band = raster.getRasterBand(i)
        name = band.name
        track.createAnalyticalFeature(name)


    # for each point         
    for j in range(track.size()):
        pos = track.getObs(j).position
        
        # for each band        
        for i in range(1, len(raster.bands)+1):
            name = raster.getRasterBand(i).name
            
            cell = band.getCell(pos)
            
            if cell == None:
                message = "Warning: point is not located in the spatial grid. "
                print(message)
                continue
            
            cx = math.floor(cell[0])
            cy = math.floor(cell[1])
            val = band.grid[cx][cy]
            
            track.setObsAnalyticalFeature(name, j, val)
            

def mapOn(
    track,
    reference,
    TP1=[],
    TP2=[],
    init=[],
    apply: bool = True,
    N_ITER_MAX: int = 20,
    NPTS: int = 30,
    mode: str = "2D",
    verbose: bool = True,
):
    """Geometric affine transformation to align two tracks with different
    coordinate systems.

    For "2D" mode, coordinates must be ENU or Geo. For "3D" mode, any type of
    coordinates is valid. In general, it is recommended to avoid usage of non-metric
    Geo coordinates for mapping operation, since it is relying on an isotropic error
    model.

    TP1 and TP2 must have same size. Adjustment is performed with least squares. The
    general transformation from point X to point X' is provided below:

    .. math::

        X' = kRX + T

    with: :math:`k` a positive real value, :math:`R` a 2D or 3D rotation matrix and
    :math:`T` a 2D or 3D translation vector. Transformation parameters are returned in
    standard output in the following format: [theta, k, tx, ty] (theta in radians).

    Track argument may also be replaced by a list of points. If TP1 is an empty list or
    if it is not specified, adjustment is performed with iterative closest point (ICP)
    algorithm, to solve both the transfo and the data association problems in a single
    framework. This method requires however that the "initial guess" (i.e. scale
    difference and rotation between both datasets) be not too far from reality, in
    order to reach a good solution. For standard least squares, time complexity of the
    method is :math:`O(n^2)` with :math:`n` the number of points used for data matching.
    For ICP, data association step is :math:`O(n^2)` and least squares resolution
    is :math:`O(n^2)` hence an overall complexity equal to N_ITER_MAX * O(NPTS^2).
    In general NPTS = 30 performs fair enough.

    Note that mapOn does not handle negative determinant (symetries not allowed)

    :param reference: another track we want to align on or a list of points
    :param TP1: list of tie points indices (relative to track)
    :param TP2: list of tie points indices (relative to reference). If TP2 is not
        specified, it is assumed equal to TP1.
    :param init: "initial guess" vector : [rotation angle, scale, tx, ty]
    :param N_ITER_MAX: maximal number of iterations (in least squares or ICP)
    :param apply: boolean value to specify if estimated transfo must be performed
    :param mode: could be "2D" (default) or "3D"
    :param NPTS: integer specifying number of points to consider (for ICP only)

    :return: transformation parameters in the following format: [theta, k, tx, ty]
    """

    if len(TP2) == 0:
        TP2 = TP1
    if not (len(TP1) == len(TP2)):
        print("Error: tie points lists must have same size")
        exit()

    # --------------------------------------------------------------------------
    # 2D mode with non-linear least squares. Initial guess needs to be not
    # too far from reality. If tie points are not provided, iterative closest
    # point (ICP) algorithm is performed to find both data association and
    # rotation/translation/scale parameters.
    # --------------------------------------------------------------------------

    if mode == "2D":

        if len(TP1) == 0:  # Recursive solution

            track_copy = track.copy()

            # Initial guess (if provided)
            if len(init) == 4:
                track_copy.rotate(init[0, 0])
                track_copy.scale(init[1, 0])
                track_copy.translate(init[2, 0], init[3, 0])

            # Match data by rough scale factor
            Cinematics.computeAbsCurv(track_copy)
            Cinematics.computeAbsCurv(reference)
            track_copy.operate(Operator.DIFFERENTIATOR, "abs_curv", "ds")
            reference.operate(Operator.DIFFERENTIATOR, "abs_curv", "ds")
            f = reference.operate(Operator.AVERAGER, "ds") / track_copy.operate(
                Operator.AVERAGER, "ds"
            )
            track_copy.scale(f)

            # Match data by rough translation
            t = track_copy.getCentroid() - reference.getCentroid()
            track_copy.translate(t.getX(), t.getY())

            resolution_steps = range(N_ITER_MAX)
            if verbose:
                resolution_steps = progressbar.progressbar(resolution_steps)

            # Iterative closest point
            for step in resolution_steps:

                # -------------------------------------------------
                # Data association step
                # -------------------------------------------------
                TP1 = []
                TP2 = []
                for i in range(0, len(track_copy), (int)(len(track_copy) / NPTS)):
                    dmin = 1e300
                    jmin = 0
                    for j in range(len(reference)):
                        dist = track_copy[i].position.distance2DTo(
                            reference[j].position
                        )
                        if dist < dmin:
                            dmin = dist
                            jmin = j
                    TP1.append(i)
                    TP2.append(jmin)

                # -------------------------------------------------
                # Recursive data adjustment step
                # -------------------------------------------------
                mapOn(track_copy, reference, TP1, TP2, N_ITER_MAX=1, verbose=False)

            # Data association application
            track.createAnalyticalFeature("pair", -1)
            for k in range(len(TP1)):
                track.setObsAnalyticalFeature("pair", TP1[k], TP2[k])

            # Adjustement application
            return mapOn(
                track, reference, TP1, TP2, apply=apply, N_ITER_MAX=20, verbose=verbose
            )

        if len(init) == 0:
            init = [0, 1, 0, 0]

        P1 = [track.getObs(i).position.copy() for i in TP1]

        if isinstance(reference, Track):
            P2 = [reference.getObs(i).position.copy() for i in TP2]
        else:
            P2 = reference

        n = len(P1)

        if verbose:
            print("-----------------------------------------------------------------")
            print("NUMBER OF TIE POINTS: " + str(len(TP1)))
            print("-----------------------------------------------------------------")
            N = int(math.log(track.size()) / math.log(10)) + 1
            for i in range(len(TP1)):
                message = "POINT " + ("{:0" + str(N) + "d}").format(TP1[i]) + "   "
                message += str(track.getObs(TP1[i]).timestamp) + "   ERROR = "
                message += str("{:10.2f}".format(P1[i].distance2DTo(P2[i]))) + " m"
                print(message)
            print("-----------------------------------------------------------------")

        J = np.zeros((2 * n, 4))
        B = np.zeros((2 * n, 1))
        X = np.matrix([init[1], init[0], init[2], init[3]]).transpose()

        track_copy = track.copy()

        # Iterations
        for iter in range(N_ITER_MAX):

            # Current parameters
            k = X[0, 0]
            tx = X[1, 0]
            ty = X[2, 0]
            a = X[3, 0]
            ca = math.cos(a)
            sa = math.sin(a)

            for i in range(0, 2 * n, 2):
                x1 = P1[int(i / 2)].getX()
                y1 = P1[int(i / 2)].getY()
                x2 = P2[int(i / 2)].getX()
                y2 = P2[int(i / 2)].getY()
                x2_th = k * (ca * x1 - sa * y1) + tx
                y2_th = k * (sa * x1 + ca * y1) + ty
                J[i, 0] = ca * x1 - sa * y1
                J[i, 1] = 1
                J[i, 2] = 0
                J[i, 3] = -k * (sa * x1 + ca * y1)
                B[i] = x2 - x2_th
                J[i + 1, 0] = sa * x1 + ca * y1
                J[i + 1, 1] = 0
                J[i + 1, 2] = 1
                J[i + 1, 3] = +k * (ca * x1 - sa * y1)
                B[i + 1] = y2 - y2_th

            dX = np.linalg.solve(J.transpose() @ J, J.transpose() @ B)
            X = X + dX
            cv_param = max(
                max(max(abs(dX[0, 0]) * 1e4, abs(dX[1, 0]) * 1e4), abs(dX[2, 0]) * 1e4),
                abs(dX[3, 0]) * 1e4,
            )
            if cv_param < 1:
                break

            if verbose:
                N = int(math.log(N_ITER_MAX - 1) / math.log(10)) + 1
                message = "ITERATION " + ("{:0" + str(N) + "d}").format(iter) + "  "
                message += (
                    "RMSE = "
                    + "{:10.5f}".format(math.sqrt(B.transpose() @ B / (2 * n)))
                    + " m    "
                )
                message += "MAX = " + "{:10.5f}".format(np.max(B)) + " m    "
                print(message)

        if verbose:
            print("-----------------------------------------------------------------")
            print("CONVERGENCE REACHED AFTER " + str(iter) + " ITERATIONS")
            glob_res = 0.0
            for l in range(0, 2 * n, 2):
                res = math.sqrt(B[l] ** 2 + B[l + 1] ** 2)
                glob_res += res
                message = "RESIDUAL (2D) POINT " + str(int(l / 2)) + ":  "
                message += "{:4.3f}".format(res) + " m"
                print(message)
            print(
                "GLOBAL 2D RESIDUAL ON TIE POINTS: "
                + "{:5.3f}".format(glob_res / n)
                + " m"
            )
            print("-----------------------------------------------------------------")
            message = (
                "Theta = "
                + "{:3.2f}".format(X[3, 0])
                + " rad   k = "
                + "{:5.3f}".format(X[0, 0])
            )
            message += (
                "  Tx = "
                + "{:8.3f}".format(X[1, 0])
                + " m  Ty = "
                + "{:8.3f}".format(X[2, 0])
                + " m"
            )
            print(message)
            print("-----------------------------------------------------------------")

        if apply:
            track.rotate(X[3, 0])
            track.scale(X[0, 0])
            track.translate(X[1, 0], X[2, 0])

        return [X[3, 0], X[0, 0], X[1, 0], X[2, 0]]

    # --------------------------------------------------------------------------
    # 3D mode with singular value decomposition. Scale factor is first estimated
    # by correlations of 3D distances computed on all couples of tie points.
    # Then dataset are scaled and translated to an approximate match. Optimal
    # rotation is subsequently computed throuh SVD decomposition of normalized
    # coordinates H = UDV' where H is 'covariance matrix'. Rotation is set as
    # R = VU'. If tie points are not provided, iterative closest point (ICP)
    # algorithm is performed to find both data association and 3D rotation/
    # translation/scale parameters.
    # --------------------------------------------------------------------------
    if mode == "3D":

        # Scale estimation
        N = 0
        D = 0
        v = 0
        W = []
        D1 = []
        D2 = []
        for i in range(len(TP1) - 1):
            for j in range(i + 1, len(TP1)):
                W.append(1)
                D1.append(track[TP1[i]].distanceTo(track[TP1[j]]))
                D2.append(reference[TP2[i]].distanceTo(reference[TP2[j]]))
        for i in range(len(D1)):
            N += W[i] * D1[i] * D2[i]
            D += W[i] * D1[i] * D1[i]
        scale = N / D
        for i in range(len(D1)):
            v += (D1[i] * scale - D2[i]) ** 2
        v = math.sqrt(v / len(D1))
        if verbose:
            print(
                "------------------------------------------------------------------------------"
            )
            print(
                "SCALE = ",
                "{:5.3f}".format(scale),
                "    (RMSE = ",
                "{:5.3f}".format(v),
                "GROUND UNITS)",
            )
            print(
                "------------------------------------------------------------------------------"
            )

        # Centers of mass estimations
        cm1 = [0, 0, 0]
        cm2 = [0, 0, 0]
        for i in range(len(TP1)):
            cm1[0] += track[TP1[i]].position.getX()
            cm2[0] += reference[TP2[i]].position.getX()
            cm1[1] += track[TP1[i]].position.getY()
            cm2[1] += reference[TP2[i]].position.getY()
            cm1[2] += track[TP1[i]].position.getZ()
            cm2[2] += reference[TP2[i]].position.getZ()
        cm1[0] /= len(TP1)
        cm2[0] /= len(TP2)
        cm1[1] /= len(TP1)
        cm2[1] /= len(TP2)
        cm1[2] /= len(TP1)
        cm2[2] /= len(TP2)

        cm1 = ENUCoords(cm1[0], cm1[1], cm1[2])
        cm2 = ENUCoords(cm2[0], cm2[1], cm2[2])

        if verbose:
            print("TRK CENTER OF MASS: ", cm1)
            print("REF CENTER OF MASS: ", cm2)
            print(
                "------------------------------------------------------------------------------"
            )

        # Translation and scale applications
        track.translate(-cm1.getX(), -cm1.getY(), -cm1.getZ())
        reference.translate(-cm2.getX(), -cm2.getY(), -cm2.getZ())
        track.scale(scale)

        # Rotation computation
        H = np.zeros((3, 3))
        for i in range(len(TP1)):
            ai = track[TP1[i]].position
            bi = reference[TP2[i]].position
            H[0, 0] += ai.getX() * bi.getX()
            H[0, 1] += ai.getX() * bi.getY()
            H[0, 2] += ai.getX() * bi.getZ()
            H[1, 0] += ai.getY() * bi.getX()
            H[1, 1] += ai.getY() * bi.getY()
            H[1, 2] += ai.getY() * bi.getZ()
            H[2, 0] += ai.getZ() * bi.getX()
            H[2, 1] += ai.getZ() * bi.getY()
            H[2, 2] += ai.getZ() * bi.getZ()

        U, D, Vt = np.linalg.svd(H, full_matrices=True)
        R = (U @ Vt).transpose()

        # Rotation application
        track.rotate3D(R)

        # Retranslation
        track.translate(cm2.getX(), cm2.getY(), cm2.getZ())
        reference.translate(cm2.getX(), cm2.getY(), cm2.getZ())

        # Data association application
        track.createAnalyticalFeature("pair", -1)
        for k in range(len(TP1)):
            track.setObsAnalyticalFeature("pair", TP1[k], TP2[k])

        return [R, cm2 - cm1, scale]

    print("Unknown mode " + mode)
    return None
