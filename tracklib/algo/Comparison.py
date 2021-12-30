"""Class to manage comparisons of GPS tracks"""


import sys
import math
from typing import Iterable, Literal, Union
import progressbar
import numpy as np
import matplotlib.pyplot as plt

from tracklib.core.TrackCollection import TrackCollection
from tracklib.core.Track import Track

import tracklib.algo.Dynamics as Dynamics
import tracklib.algo.Interpolation as Interpolation


def plotDifferenceProfile(
    profile, track2, af_name="pair", sym="g--", NO_DATA_VALUE: int = -1
):
    """Difference profile plot

    :param profile: TODO
    :param track2: TODO
    :param af_name: TODO
    :param sym: TODO
    :param NO_DATA_VALUE: TODO
    """
    for i in range(profile.size()):
        if profile.getObsAnalyticalFeature(af_name, i) == NO_DATA_VALUE:
            continue
        x1 = profile.getObs(i).position.getX()
        y1 = profile.getObs(i).position.getY()
        x2 = track2.getObs(profile.getObsAnalyticalFeature(af_name, i)).position.getX()
        y2 = track2.getObs(profile.getObsAnalyticalFeature(af_name, i)).position.getY()
        plt.plot([x1, x2], [y1, y2], sym, linewidth=0.5)


def differenceProfile(track1, track2, mode: Literal["NN", "DTW", "FDTW"] = "NN", ends=False, p=1, verbose: bool = True):
    """Profile of difference between two traces

    Three possible modes:

    - **NN** (Nearest Neighbour): :math:`O(n^2)` time and :math:`O(n)` space
    - **DTW** (Dynamic Time Warping): :math:`O(n^3)` time and :math:`O(n^2)` space
    - **FDTW** (Fast Dynamic Time Warping): same as DTW with reduced search space. In this
      particular case, 'ends' parameter is an integer giving the number of points to
      search for a match ahead and behind the current point. E.g. for ends=0, there is a
      strict matching track1[i] <-> track2[i] for each epoch i. For ends=10 for example,
      each point track[i] can be matched with any point chronologically between the
      bounds track2[i-10] and track2[i+10]. Default is equal to 3, meaning that track1
      may be at most 3 times faster or slower than track2 on ant given sub-interval.
      Note that this method is designed for pairs of tracks having about same number of
      points. Otherwise, it is strongly advised to perform a spatial resampling before
      applying FDTW

    :param track1: TODO
    :param track2: TODO
    :param mode: Mode for the interpolation. Three modes are possible : NN, DTW and FDTW
    :param ends: TODO
    :param p: TODO
    :param verbose: Verbose mode
    :return: A track objet, with an analytical feature diff containing shortest distance
             of each point of track t1, to the points of track t2. We may get profile as
             a list with :func:`output.getAbsCurv()` and
             :func:`output.getAnalyticalFeature("diff")` The selected candidate in
             registerd in AF "pair" Set "ends" parameter to True to force end points to
             meet p is Minkowski's exponent for distance computation. Default value is
             1 for summation of distances, 2 for least squares solution and 10 for an
             approximation of Frechet solution.
    """

    output = track1.copy()
    output.createAnalyticalFeature("diff")
    output.createAnalyticalFeature("pair")
    output.createAnalyticalFeature("ex")
    output.createAnalyticalFeature("ey")

    # --------------------------------------------------------
    # Nearest Neighbor (NN) algorithm
    # --------------------------------------------------------
    if mode == "NN":
        to_run = range(output.size())
        if verbose:
            to_run = progressbar.progressbar(to_run)
        for i in to_run:
            val_min = sys.float_info.max
            id_min = 0
            for j in range(track2.size()):
                distance = output.getObs(i).distance2DTo(track2.getObs(j))
                if distance < val_min:
                    val_min = distance
                    id_min = j
            output.setObsAnalyticalFeature("diff", i, val_min)
            output.setObsAnalyticalFeature("pair", i, id_min)
            ex = (
                track1.getObs(i).position.getX() - track2.getObs(id_min).position.getX()
            )
            ey = (
                track1.getObs(i).position.getY() - track2.getObs(id_min).position.getY()
            )
            output.setObsAnalyticalFeature("ex", i, ex)
            output.setObsAnalyticalFeature("ey", i, ey)

    # --------------------------------------------------------
    # Dynamic time warping (DTW) algorithm
    # --------------------------------------------------------
    if mode == "DTW":

        p = max(min(p, 15), 1e-2)

        track1 = track1.copy()
        track2 = track2.copy()

        # Forming distance matrix
        D = np.zeros((track1.size(), track2.size()))
        for i in range(track1.size()):
            for j in range(track2.size()):
                D[i, j] = track1.getObs(i).distance2DTo(track2.getObs(j)) ** p

        # Optimal path with dynamic programming
        T = np.zeros((track1.size(), track2.size()))
        M = np.zeros((track1.size(), track2.size()))
        T[0, 0] = D[0, 0]
        M[0, 0] = -1

        # Forward step
        step_to_run = range(1, T.shape[0])
        if verbose:
            step_to_run = progressbar.progressbar(step_to_run)
        for i in step_to_run:
            T[i, 0] = T[i - 1, 0] + D[i, 0]
            M[i, 0] = 0
            for j in range(1, T.shape[1]):
                K = D[i, 0 : (j + 1)]
                for k in range(j - 1, -1, -1):
                    K[k] = K[k] + K[k + 1]
                V = T[i - 1, 0 : (j + 1)] + K
                M[i, j] = np.argmin(V)
                T[i, j] = V[int(M[i, j])]

        # Backward step
        S = [0] * (track1.size())
        if ends:
            S[track1.size() - 1] = int(M[track1.size() - 1, track2.size() - 1])
        else:
            S[track1.size() - 1] = np.argmin(T[track1.size() - 1, :])
        for i in range(track1.size() - 2, -1, -1):
            S[i] = int(M[i + 1, S[i + 1]])

        # print((T[track1.size()-1, S[track1.size()-1]] / track1.size())**(1.0/p))

        # plt.plot(S, 'r-')
        # plt.imshow(M)

        __fillAFProfile(track1, track2, output, S)

    # --------------------------------------------------------
    # Fast Dynamic time warping (FDTW) algorithm
    # --------------------------------------------------------
    if mode == "FDTW":

        if isinstance(ends, bool):
            if not ends:
                ends = 12

        S = lambda track, k: [
            p for p in range(max(0, k - ends), min(len(track2) - 1, k + ends))
        ]
        Q = lambda i, j, k, t: (j < i + 30) * (j >= i) * 1
        P = lambda s, y, k, t: math.exp(-track2[s].position.distance2DTo(y))

        Dynamics.HMM(S, Q, P).estimate(
            output,
            ["x", "y"],
            mode=Dynamics.MODE_OBS_AS_2D_POSITIONS,
            verbose=2 * verbose,
        )

        __fillAFProfile(track1, track2, output, output["hmm_inference"])

    output.compute_abscurv()
    return output


def __fillAFProfile(track1, track2, output, S):
    """TODO

    :param track1: TODO
    :param track2: TODO
    :param output: TODO
    :param S: TODO
    """
    for i in range(track1.size()):
        x1 = track1.getObs(i).position.getX()
        y1 = track1.getObs(i).position.getY()
        x2 = track2.getObs(S[i]).position.getX()
        y2 = track2.getObs(S[i]).position.getY()
        d = track1.getObs(i).distance2DTo(track2.getObs(S[i]))
        ex = track1.getObs(i).position.getX() - track2.getObs(S[i]).position.getX()
        ey = track1.getObs(i).position.getY() - track2.getObs(S[i]).position.getY()
        output.setObsAnalyticalFeature("diff", i, d)
        output.setObsAnalyticalFeature("pair", i, S[i])
        output.setObsAnalyticalFeature("ex", i, ex)
        output.setObsAnalyticalFeature("ey", i, ey)


def synchronize(self, track):
    """Resampling of 2 tracks with linear interpolation on a common base of
    timestamps

    :param track: track to synchronize with
    """
    Interpolation.synchronize(self, track)


def compare(track1, track2) -> float:
    """Comparison of 2 tracks.

    Tracks are interpolated linearly on a common base of timestamps

    :param track1: track to compare with
    :param track2: track to compare with

    :return: TODO
    """

    trackA = track1.copy()
    trackB = track2.copy()

    track2.synchronize(track3)

    rmse = 0
    for i in range(trackA.size()):
        rmse += trackA.getObs(i).distanceTo(trackB.getObs(i)) ** 2

    return math.sqrt(rmse / trackA.size())


def centralTrack(tracks: Union[TrackCollection, Iterable[Track]], mode: Literal["NN", "DTW", "FDTW"] = "NN", verbose: bool = True) -> Track:
    """Computes central track of a track collection

    :param tracks: TrackCollection or list of tracks
    :param mode: "NN", "DTW" or "FDTW" for track pair matching (see the documentation
                  of :func:`differenceProfile` function for more infos on modes)
    :return: The central track
    """

    tracks = tracks.copy()

    if isinstance(tracks, list):
        tracks = TrackCollection(tracks)
    base = tracks.toENUCoordsIfNeeded()
    central = tracks[0].copy()

    for i in range(1, len(tracks)):
        diff = differenceProfile(tracks[0], tracks[i], mode=mode, verbose=verbose)

        for j in range(len(central)):
            dx = tracks[i][diff["pair", j]].position.getX()
            dy = tracks[i][diff["pair", j]].position.getY()
            dz = tracks[i][diff["pair", j]].position.getZ()
            central[j].position.translate(dx, dy, dz)

    for j in range(len(central)):
        central[j].position.scale(1.0 / len(tracks))

    if not base is None:
        central.toGeoCoords(base)

    return central
