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



Class to manage interpolation and smoothing functions

"""

# For type annotation
from __future__ import annotations   
from typing import Literal   

import sys
import math
import numpy as np

import tracklib as tracklib
from tracklib.core import (Obs, ENUCoords, ObsTime, 
                      makeCovarianceMatrixFromKernelOld,
                      makeDistanceMatrixOld)

MODE_SPATIAL = 1
MODE_TEMPORAL = 2

ALGO_LINEAR = 1
ALGO_THIN_SPLINES = 2
ALGO_B_SPLINES = 3
ALGO_GAUSSIAN_PROCESS = 4

SPLINE_PENALIZATION = 0
B_SPLINE_DEGREE = 3
B_SPLINE_RESOL = None
GP_KERNEL = None
GP_SMOOTHING = 0


def resample(track, delta, algo: Literal[1, 2, 3, 4]=1, mode:Literal[1, 2]=1):   
    """Resampling of a track with linear interpolation delta

    Interpolation interval (time in sec if temporal mode is selected,
    space in meters if spatial).

      Available modes are:

        - MODE_SPATIAL (*mode=1*)
        - MODE_TEMPORAL (*mode=2*)

      algorithm:

        - ALGO_LINEAR (*algo=1*)
        - ALGO_THIN_SPLINES (*algo=2*)
        - ALGO_B_SPLINES (*algo=3*)
        - ALGO_GAUSSIAN_PROCESS (*algo=4*)

      In temporal mode, argument may be:

        - an integer or float: interval in seconds
        - a list of timestamps where interpolation should be computed
        - a reference track

    :param algo: TODO
    :param mode: TODO
    """
    
    if mode == MODE_SPATIAL:
        if algo == ALGO_LINEAR:
            __resampleSpatial(track, delta)
        if algo == ALGO_THIN_SPLINES:
            __smooth_resample_spatial(track, delta)
        if algo == ALGO_B_SPLINES:
            __bsplines_spatial(track, delta, B_SPLINE_DEGREE, B_SPLINE_RESOL)
        if algo == ALGO_GAUSSIAN_PROCESS:
            if GP_KERNEL == None:
                sys.exit(
                    "Kernel must be defined with 'GP_KERNEL' before using gaussian process interpolation"
                )
            t = gaussian_process(track, delta, GP_KERNEL, 1, GP_SMOOTHING, mode=MODE_SPATIAL)
            track.setObsList(t.getObsList())

    if mode == MODE_TEMPORAL:
        if algo == ALGO_LINEAR:
            __resampleTemporal(track, delta)
        if algo == ALGO_THIN_SPLINES:
            __smooth_resample_temporal(track, delta)
        if algo == ALGO_B_SPLINES:
            __bsplines_temporal(track, delta, B_SPLINE_DEGREE, B_SPLINE_RESOL)
        if algo == ALGO_GAUSSIAN_PROCESS:
            if GP_KERNEL == None:
                sys.exit(
                    "Kernel must be defined with 'GP_KERNEL' before using gaussian process interpolation"
                )
            t = gaussian_process(track, delta, GP_KERNEL, 1, GP_SMOOTHING)
            track.setObsList(t.getObsList())

    track.__analyticalFeaturesDico = {}

def __resampleSpatial(track, ds):
    """TODO

    Resampling of a track with linear interpolation
    ds: curv abs interval (in m) between two samples"""

    S = [0]
    for i in range(1, track.size()):
        dl = track.getObs(i - 1).position.distance2DTo(track.getObs(i).position)
        S.append(S[i - 1] + dl)

    sini = S[0]
    sfin = S[len(S) - 1]
    N = (int)((sfin - sini) / ds)

    interp_points = [track.getFirstObs().copy()]
    interp_points[0].features = []
    running_id = 0

    for k in range(1, N + 1):

        s = k * ds + sini

        while S[running_id] < s:
            running_id += 1

        pt_bwd = track.getObs(running_id - 1)
        pt_fwd = track.getObs(running_id)
        sbwd = S[running_id - 1]
        sfwd = S[running_id]

        wbwd = (sfwd - s) / (sfwd - sbwd)
        wfwd = (s - sbwd) / (sfwd - sbwd)

        X = wbwd * pt_bwd.position.getX() + wfwd * pt_fwd.position.getX()
        Y = wbwd * pt_bwd.position.getY() + wfwd * pt_fwd.position.getY()
        Z = wbwd * pt_bwd.position.getZ() + wfwd * pt_fwd.position.getZ()
        T = wbwd * pt_bwd.timestamp.toAbsTime() + wfwd * pt_fwd.timestamp.toAbsTime()

        pi = Obs(ENUCoords(X, Y, Z), ObsTime.readUnixTime(T))

        interp_points.append(pi)

    track.setObsList(interp_points)



def __resampleSpatial2(track, ds):
    """
    Resampling of a track with linear interpolation
    ds: curv abs interval (in m) between two samples
    """
    S = [0]
    for i in range(1, track.size()):
        dl = track.getObs(i - 1).position.distance2DTo(track.getObs(i).position)
        S.append(S[i-1] + dl)

    N = (int)(track.length() / ds)

    interp_points = [track.getFirstObs().copy()]
    interp_points[0].features = []
    running_id = 0

    for k in range(1, N + 1):
        s = k * ds + S[0]

        while S[running_id] < s:
            running_id += 1

        pt_bwd = track.getObs(running_id - 1)
        pt_fwd = track.getObs(running_id)
        sbwd = S[running_id - 1]
        sfwd = S[running_id]

        wbwd = (sfwd - s) / (sfwd - sbwd)
        wfwd = (s - sbwd) / (sfwd - sbwd)

        X = wbwd * pt_bwd.position.getX() + wfwd * pt_fwd.position.getX()
        Y = wbwd * pt_bwd.position.getY() + wfwd * pt_fwd.position.getY()
        Z = wbwd * pt_bwd.position.getZ() + wfwd * pt_fwd.position.getZ()
        T = wbwd * pt_bwd.timestamp.toAbsTime() + wfwd * pt_fwd.timestamp.toAbsTime()

        pi = Obs(ENUCoords(X, Y, Z), ObsTime.readUnixTime(T))

        interp_points.append(pi)
    
    # And the last point
    interp_points.append(track.getLastObs().copy())

    track.setObsList(interp_points)


def __resampleTemporal(track, reference):
    """
    Resampling of a track with linear interpolation
    reference: list of timestamps, track or sec interval
    """

    T = []
    for i in range(track.size()):
        T.append(track.getObs(i).timestamp.toAbsTime())

    tini = T[0]
    tfin = T[len(T) - 1]

    # Preparing reference list
    REF = prepareTimeSampling(reference, tini, tfin)

    interp_points = []
    running_id = 0

    for k in range(len(REF)):
        t = REF[k]

        if t <= tini:
            continue
        if t > tfin:
            break

        while T[running_id] < t:
            running_id += 1

        pt_bwd = track.getObs(running_id - 1)
        pt_fwd = track.getObs(running_id)
        tbwd = T[running_id - 1]
        tfwd = T[running_id]

        wbwd = (tfwd - t) / (tfwd - tbwd)
        wfwd = (t - tbwd) / (tfwd - tbwd)

        X = wbwd * pt_bwd.position.getX() + wfwd * pt_fwd.position.getX()
        Y = wbwd * pt_bwd.position.getY() + wfwd * pt_fwd.position.getY()
        Z = wbwd * pt_bwd.position.getZ() + wfwd * pt_fwd.position.getZ()

        pi = Obs(ENUCoords(X, Y, Z), ObsTime.readUnixTime(t))

        interp_points.append(pi)

    track.setObsList(interp_points)


def gaussian_process(track, timestamps, kernel, factor=1.0, sigma=0.0, cp_var=False, mode=MODE_TEMPORAL):
    """Track interpolation and smoothing with Gaussian Process (GP)

    :param timestamps: points where interpolation must be computed.
        May be a list of timestamps, a track or a number of seconds
    :param kernel: a symetric function k(xi-xj) describing the statistical similarity
        between the coordinates X,Y,Z taken in two points :

        :math:`k(t2-t1) = Cov(X(t1), X(t2))`

        :math:`k(t2-t1) = Cov(Y(t1), Y(t2))`

        :math:`k(t2-t1) = Cov(Z(t1), Z(t2))`

    :param factor: unit factor of variance if the kernel must be scaled
    :param sigma: observation noise standard deviation (in coords units)
    :param cp_var: compute covariance matrix and store pointwise sigmas
    :param mode: MODE_TEMPORAL or MODE_SPATIAL
    :return: interpolated/smoothed track (without AF)
    """
    if mode==MODE_TEMPORAL:
        return gaussian_process_temporal(track, timestamps, kernel, factor, sigma, cp_var)
    else:
        return gaussian_process_spatial(track, timestamps, kernel, factor, sigma, cp_var)
    
	
def gaussian_process_spatial(track, delta, kernel, factor=1.0, sigma=0.0, cp_var=False):
	
    temp = track.copy()

    # Vector of observed and unknown points
    TO = temp.getT()
    temp.resample(delta, mode=MODE_SPATIAL)
    TU = temp.getT()
	
    return __gaussian_process(track, TO, TU, kernel, factor, sigma, cp_var)

def gaussian_process_temporal(track, timestamps, kernel, factor=1.0, sigma=0.0, cp_var=False):

    tini = track.getFirstObs().timestamp.toAbsTime()
    tfin = track.getLastObs().timestamp.toAbsTime()

    # Vector of observed and unknown points
    TO = prepareTimeSampling(track, tini, tfin)
    TU = prepareTimeSampling(timestamps, tini, tfin)
	
    return __gaussian_process(track, TO, TU, kernel, factor, sigma, cp_var)

def __gaussian_process(track, TO, TU, kernel, factor, sigma, cp_var):
    new_track = tracklib.Track()

    # Observations
    yx = np.array(track.getX())
    yy = np.array(track.getY())
    yz = np.array(track.getZ())

    # Debiasing
    bx = np.mean(yx)
    by = np.mean(yy)
    bz = np.mean(yz)
    yx = yx - bx
    yy = yy - by
    yz = yz - bz

    # Computing obs covariance matrix
    K = makeCovarianceMatrixFromKernelOld(kernel, TO, TO, factor)
    K = np.add(K, sigma ** 2 * np.identity(len(TO)))

    # Computing unknown sites covariance matrix
    KSS = makeCovarianceMatrixFromKernelOld(kernel, TU, TU, factor)

    # Computing obs - unknown sites covariance matrix
    KS = makeCovarianceMatrixFromKernelOld(kernel, TO, TU, factor)

    # Computing posterior distribution means
    MUX = np.matmul(KS.T, np.linalg.solve(K, yx))
    MUY = np.matmul(KS.T, np.linalg.solve(K, yy))
    MUZ = np.matmul(KS.T, np.linalg.solve(K, yz))

    # Computing posterior distribution covariances
    if cp_var:
        SIGMA_XYZ = KSS - np.matmul(KS.T, np.matmul(np.linalg.inv(K), KS))

    # Filling track
    for i in range(MUX.shape[0]):
        coords = ENUCoords(MUX[i] + bx, MUY[i] + by, MUZ[i] + bz)
        obs = Obs(coords, ObsTime.readUnixTime(TU[i]))
        new_track.addObs(obs)

    if cp_var:
        new_track.createAnalyticalFeature("@sigma_gp")
        for i in range(SIGMA_XYZ.shape[0]):
            sigma = math.sqrt(abs(SIGMA_XYZ[i, i])) * factor
            new_track.setObsAnalyticalFeature("@sigma_gp", i, sigma)

    return new_track


# --------------------------------------------------------------------------
# Function to prepare a list of timestamps for interpolation functions
# --------------------------------------------------------------------------
# Input :
#   - input ::     a list of timestamps (list), an interval in sec (float),
# 				   or a track
#   - tini  ::     Initial timestamp (only if input is an interval in sec)
#   - tfin  ::     Final timestamp (only if input is an interval in sec)
# --------------------------------------------------------------------------
# Output : a list of timestamps
# --------------------------------------------------------------------------
def prepareTimeSampling(input, tini=None, tfin=None):
    """
    Function to prepare a list of timestamps for interpolation functions.
    
    """
    output = []
    if isinstance(input, list):
        for i in range(len(input)):
            output.append(input[i].toAbsTime())
    if isinstance(input, tracklib.Track):
        for i in range(input.size()):
            output.append(input.getObs(i).timestamp.toAbsTime())
    if isinstance(input, int) or isinstance(input, float):
        time = tini
        while 1:
            output.append(time)
            time += input
            if time > tfin:
                break
    return output


def synchronize(track1, track2):
    """
    Function to synchronize two tracks.
    Note: method is symetric on track1 and track2
    
    Input :
    - track1 ::   track to synchronize
    - track2 ::   track to synchronize
    """

    # Merge timestamps of tracks
    timestamps = track1.getTimestamps() + [] + track2.getTimestamps()

    # Common time range
    tini = max(track1.getFirstObs().timestamp, track2.getFirstObs().timestamp)
    tfin = min(track1.getLastObs().timestamp, track2.getLastObs().timestamp)

    # Sort list of timestamps
    sort_index = np.argsort(np.array(timestamps))
    sorted = []
    for i in range(len(sort_index)):
        if timestamps[sort_index[i]] <= tini:
            continue
        if timestamps[sort_index[i]] >= tfin:
            continue
        sorted.append(timestamps[sort_index[i]])

    # Test unique timestamps
    for i in range(len(sorted) - 2, 0, -1):
        if sorted[i + 1] == sorted[i]:
            del sorted[i + 1]

    # Interpolation
    track1.resample(sorted, mode = MODE_TEMPORAL) 
    track2.resample(sorted, mode = MODE_TEMPORAL)


def __smooth_resample_spatial(track, ds):
    """TODO

    Resampling of a track with spline interpolation
    ds: curv abs interval (in m) between two samples"""

    S = [0]
    for i in range(1, track.size()):
        dl = track.getObs(i - 1).position.distance2DTo(track.getObs(i).position)
        S.append(S[i - 1] + dl)

    sini = S[0]
    sfin = S[len(S) - 1]
    N = (int)((sfin - sini) / ds)

    Si = sini + np.arange(0, sfin, ds)

    M = max(S)
    n = len(S)

    for i in range(len(S)):
        S[i] = S[i] / M

    for i in range(len(Si)):
        Si[i] = Si[i] / M

    D = makeDistanceMatrixOld(S, S)
    D = D ** 2 * np.log(D + 1e-100)

    for i in range(D.shape[0]):
        D[i, i] = SPLINE_PENALIZATION

    ONES = np.ones((n, 2))
    for i in range(n):
        ONES[i, 1] = S[i]
    ZEROS = np.zeros((2, 2))

    # Design matrix
    UP = np.concatenate((ONES, D), axis=1)
    BOTTOM = np.concatenate((ZEROS, ONES), axis=0).T
    K = np.concatenate((UP, BOTTOM), axis=0)

    # Observations
    Yx = np.array(track.getX())
    Yy = np.array(track.getY())
    Yz = np.array(track.getZ())
    Yt = np.array(track.getT())

    # Right-hand side
    Bx = np.concatenate((Yx, [0, 0]))
    By = np.concatenate((Yy, [0, 0]))
    Bz = np.concatenate((Yz, [0, 0]))
    Bt = np.concatenate((Yt, [0, 0]))

    # X coordinate
    CX = np.linalg.solve(K, Bx)
    bx = CX[2 : CX.shape[0] + 1]
    ax0 = CX[0]
    ax1 = CX[1]

    # Y coordinate
    CY = np.linalg.solve(K, By)
    by = CY[2 : CY.shape[0] + 1]
    ay0 = CY[0]
    ay1 = CY[1]

    # Z coordinate
    CZ = np.linalg.solve(K, Bz)
    bz = CZ[2 : CZ.shape[0] + 1]
    az0 = CZ[0]
    az1 = CZ[1]

    # Timestamps
    CT = np.linalg.solve(K, Bt)
    bt = CT[2 : CT.shape[0] + 1]
    at0 = CT[0]
    at1 = CT[1]

    PTS = np.array(S)
    Di = makeDistanceMatrixOld(Si, S)

    Xi = [0] * len(Si)
    Yi = [0] * len(Si)
    Zi = [0] * len(Si)
    Ti = [0] * len(Si)

    for i in range(len(Si)):
        h = Di[i, :] ** 2 * np.log(Di[i, :] + 1e-100)
        Xi[i] = ax0 + ax1 * Si[i] + np.sum(bx * h)
        Yi[i] = ay0 + ay1 * Si[i] + np.sum(by * h)
        Zi[i] = az0 + az1 * Si[i] + np.sum(bz * h)
        Ti[i] = at0 + at1 * Si[i] + np.sum(bt * h)

    OBS = []
    for i in range(len(Si)):
        OBS.append(Obs(ENUCoords(Xi[i], Yi[i], Zi[i]), ObsTime.readUnixTime(Ti[i])))

    track.setObsList(OBS)


def __smooth_resample_temporal(track, reference):
    """TODO

    Resampling of a track with spline interpolation
    reference: list of timestamps, track or sec interval"""

    T = []

    for i in range(track.size()):
        T.append(track.getObs(i).timestamp.toAbsTime())

    tini = T[0]
    tfin = T[len(T) - 1]

    # Preparing reference list
    REF = prepareTimeSampling(reference, tini, tfin)

    M = min(T)
    n = len(T)

    for i in range(len(T)):
        T[i] = T[i] - M

    for i in range(len(REF)):
        REF[i] = REF[i] - M

    D = makeDistanceMatrixOld(T, T)
    D = D ** 2 * np.log(D + 1e-100)

    for i in range(D.shape[0]):
        D[i, i] = SPLINE_PENALIZATION

    ONES = np.ones((n, 2))
    for i in range(n):
        ONES[i, 1] = T[i]
    ZEROS = np.zeros((2, 2))

    # Design matrix
    UP = np.concatenate((ONES, D), axis=1)
    BOTTOM = np.concatenate((ZEROS, ONES), axis=0).T
    K = np.concatenate((UP, BOTTOM), axis=0)

    # Observations
    Yx = np.array(track.getX())
    Yy = np.array(track.getY())
    Yz = np.array(track.getZ())

    # Right-hand side
    Bx = np.concatenate((Yx, [0, 0]))
    By = np.concatenate((Yy, [0, 0]))
    Bz = np.concatenate((Yz, [0, 0]))

    # X coefficients
    CX = np.linalg.solve(K, Bx)
    bx = CX[2 : CX.shape[0] + 1]
    ax0 = CX[0]
    ax1 = CX[1]

    # Y coefficients
    CY = np.linalg.solve(K, By)
    by = CY[2 : CY.shape[0] + 1]
    ay0 = CY[0]
    ay1 = CY[1]

    # Z coefficients
    CZ = np.linalg.solve(K, Bz)
    bz = CZ[2 : CZ.shape[0] + 1]
    az0 = CZ[0]
    az1 = CZ[1]

    PTS = np.array(T)
    Di = makeDistanceMatrixOld(REF, T)

    Xi = [0] * len(REF)
    Yi = [0] * len(REF)
    Zi = [0] * len(REF)

    for i in range(len(REF)):
        h = Di[i, :] ** 2 * np.log(Di[i, :] + 1e-100)
        Xi[i] = ax0 + ax1 * REF[i] + np.sum(bx * h)
        Yi[i] = ay0 + ay1 * REF[i] + np.sum(by * h)
        Zi[i] = az0 + az1 * REF[i] + np.sum(bz * h)

    OBS = []
    for i in range(len(REF)):
        OBS.append(
            Obs(ENUCoords(Xi[i], Yi[i], Zi[i]), ObsTime.readUnixTime(REF[i] + M))
        )

    track.setObsList(OBS)


def __phi(x, tab):
    """TODO"""
    n = (int)(len(tab) / 2)
    id = (int)(n + x * 400)
    if id < 0:
        return 0
    if id >= len(tab):
        return 0
    return tab[id]


def __bsplines_temporal(track, reference, degree=3, knots_nb=None):
    """TODO

    Resampling of a track with B-spline interpolation
    reference: list of timestamps, track or sec interval"""

    if degree > 3:
        sys.exit("Error: B-spline of order > 3 is not supported")

    T = track.getT()

    tini = T[0]
    tfin = T[len(T) - 1]

    # Preparing reference list
    REF = prepareTimeSampling(reference, tini, tfin)

    # Data reduction for numerical stability
    X = np.array(track.getX())
    Y = np.array(track.getY())
    Z = np.array(track.getZ())
    T = np.array(T)

    Mt = min(T)
    Mx = min(X)
    My = min(Y)
    Mz = min(Z)

    for i in range(len(X)):
        X[i] = X[i] - Mx
        Y[i] = Y[i] - My
        Z[i] = Z[i] - Mz
        T[i] = T[i] - Mt

    for i in range(len(REF)):
        REF[i] = REF[i] - Mt

    # Base resolution computation
    if knots_nb == None:
        knots_nb = (T[-1] - T[0]) / len(T)

    if knots_nb > T[-1] - T[0]:
        message = "Error: spline basis resolution (" + (str)(knots_nb) + ") "
        message += "is greater than track time duration (" + (str)(T[-1] - T[0]) + "). "
        sys.exit(message)

    BP = np.arange(0, T[-1], knots_nb)

    # Kernel computation
    phi0 = np.array([0] * 400 + [1] * 800 + [0] * 400)
    phi = np.array([0] * 400 + [1] * 800 + [0] * 400)
    for i in range(degree):
        phi = np.convolve(phi, phi0)
    phi = phi / max(phi)

    kfunc = np.vectorize(lambda t: __phi(t / knots_nb, phi))

    # Spline coefficients
    A = kfunc(makeDistanceMatrixOld(T, BP))
    DI = kfunc(makeDistanceMatrixOld(BP, REF))
    if A.shape[1] == X.shape[0]:
        C = np.linalg.solve(A, np.column_stack((X, Y, Z)))
    else:
        C = np.linalg.solve(A.T @ A, A.T @ np.column_stack((X, Y, Z)))

    # Interpolation
    XYZi = np.matmul(C.T, DI)

    OBS = []
    for i in range(len(REF)):
        x = XYZi[0, i] + Mx
        y = XYZi[1, i] + My
        z = XYZi[2, i] + Mz
        t = REF[i] + Mt
        OBS.append(Obs(ENUCoords(x, y, z), ObsTime.readUnixTime(t)))

    track.setObsList(OBS)

    if BP.shape[0] > X.shape[0]:
        message = "Warning: number of basis functions (" + (str)(BP.shape[0]) + ") "
        message += "is greater than number of constraints (" + (str)(X.shape[0]) + "). "
        message += (
            "Least squares problem is not tighly constrained: solution may be unstable."
        )
        print(message)


def __bsplines_spatial(track, ds, degree=3, knots_nb=None):
    """TODO

    Resampling of a track with spline interpolation
    ds: curv abs interval (in m) between two samples"""

    if degree > 3:
        sys.exit("Error: B-spline of order > 3 is not supported")

    S = [0]
    for i in range(1, track.size()):
        dl = track.getObs(i - 1).position.distance2DTo(track.getObs(i).position)
        S.append(S[i - 1] + dl)

    sini = S[0]
    sfin = S[len(S) - 1]

    Si = sini + np.arange(0, sfin, ds)

    M = max(S)

    for i in range(len(S)):
        S[i] = S[i] / M

    for i in range(len(Si)):
        Si[i] = Si[i] / M

    # Data reduction for numerical stability
    X = np.array(track.getX())
    Y = np.array(track.getY())
    Z = np.array(track.getZ())
    T = np.array(track.getT())
    S = np.array(S)

    Mx = min(X)
    My = min(Y)
    Mz = min(Z)
    Mt = min(T)

    for i in range(len(X)):
        X[i] = X[i] - Mx
        Y[i] = Y[i] - My
        Z[i] = Z[i] - Mz
        T[i] = T[i] - Mt

    # Base resolution computation
    if knots_nb == None:
        knots_nb = (S[-1] - S[0]) / (len(S) - 1)
    else:
        knots_nb = knots_nb / M

    if knots_nb > S[-1] - S[0]:
        message = "Error: spline basis resolution (" + (str)(knots_nb) + ") "
        message += "is greater than track length (" + (str)(S[-1] - S[0]) + "). "
        sys.exit(message)

    BP = np.arange(0, S[-1], knots_nb)

    # Kernel computation
    phi0 = np.array([0] * 400 + [1] * 800 + [0] * 400)
    phi = np.array([0] * 400 + [1] * 800 + [0] * 400)
    for i in range(degree):
        phi = np.convolve(phi, phi0)
    phi = phi / max(phi)

    kfunc = np.vectorize(lambda t: __phi(t / knots_nb, phi))

    # Spline coefficients
    A = kfunc(makeDistanceMatrixOld(S, BP))
    DI = kfunc(makeDistanceMatrixOld(BP, Si))
    if A.shape[1] == X.shape[0]:
        C = np.linalg.solve(A, np.column_stack((X, Y, Z, T)))
    else:
        C = np.linalg.solve(A.T @ A, A.T @ np.column_stack((X, Y, Z, T)))

    # Interpolation
    XYZi = np.matmul(C.T, DI)

    OBS = []
    for i in range(len(Si)):
        x = XYZi[0, i] + Mx
        y = XYZi[1, i] + My
        z = XYZi[2, i] + Mz
        t = XYZi[3, i] + Mt
        OBS.append(Obs(ENUCoords(x, y, z), ObsTime.readUnixTime(t)))

    track.setObsList(OBS)

    if BP.shape[0] > X.shape[0]:
        message = "Warning: number of basis functions (" + (str)(BP.shape[0]) + ") "
        message += "is greater than number of constraints (" + (str)(X.shape[0]) + "). "
        message += (
            "Least squares problem is not tighly constrained: solution may be unstable."
        )
        print(message)


def smooth_cv(track, smooth_function, params=[], verbose=True):
    """Cross validation for determining optimal parameters of
     smoothing/interpolating/simplifying functions

    Note that if params contains a single element, smooth_cv function is a simple
    statistical control. If no parameters are provided in input, a default set of 1000
    positive parameters sampled according to a logarithmic scale between 1e-9 and 1e9
    is considered.

    :param track: a (timestamped) track on which cross validation is performed
    :param smooth_function: any function with track as input and output
    :param params: a list of parameters to test in smooth_function
    :return: TODO
    """

    if verbose:
        print("-----------------------------------------------------")
        print(
            "CROSS VALIDATION OF SMOOTHING FUNCTION " + smooth_function.__name__.upper()
        )
        print("-----------------------------------------------------")

    track_train = track % [True, False]
    track_valid = track % [False, True]

    if not (str(type(params)) == "<class 'list'>"):
        params = [params]

    if len(params) == 0:
        l = (int)(math.log(1e9) / math.log(1.5))
        params = [1.5 ** p for p in range(-l, l)]

    opt_rmse = 1e300
    opt_param = 0

    for param in params:

        track_test = smooth_function(track_train, param)
        track_test //= track_valid

        RMSE = 0.0
        for i in range(track_test.size() - 1):
            RMSE += track_test.getObs(i).distance2DTo(track_valid.getObs(i)) ** 2

        RMSE = math.sqrt(RMSE / track_test.size())
        if RMSE < opt_rmse:
            opt_rmse = RMSE
            opt_param = param

        if verbose:
            message = smooth_function.__name__.upper() + " PARAMETER "
            message += (
                "{:18.7f}".format(param) + " -  RMSE = " + "{:7.3f}".format(RMSE) + " m"
            )
            print(message)

    if verbose:
        print("-----------------------------------------------------")
        print(
            "BEST PARAMETER "
            + "{:7.2f}".format(opt_param)
            + " -  RMSE = "
            + "{:6.3f}".format(opt_rmse)
            + " m"
        )
        print("-----------------------------------------------------")

    return opt_param
