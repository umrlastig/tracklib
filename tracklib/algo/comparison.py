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
"""

"""to manage comparisons of GPS tracks"""


import sys
import math
from typing import Literal
import progressbar
import numpy as np
import matplotlib.pyplot as plt

import tracklib as tracklib
from tracklib.util import dist_point_to_segment
from . import computeAbsCurv, synchronize, HMM, MODE_OBS_AS_2D_POSITIONS


MODE_COMPARAISON_NEAREST_NEIGHBOUR = 1
MODE_COMPARAISON_DTW = 2
MODE_COMPARAISON_FDTW = 3


def plotDifferenceProfile(
    profile, track2, af_name="pair", sym="g--", NO_DATA_VALUE: int = -1):
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
        plt.plot([x1, x2], [y1, y2], sym, linewidth=2)


def _minCumul(vec):
	out = vec.copy()
	mark = [0]*len(vec)
	for i in range(1, len(vec)):
		out[i]  = min(out[i], out[i-1])
		mark[i] = mark[i-1]*(out[i] >= out[i-1]) + i*(out[i] < out[i-1])
	return [out, mark]


def differenceProfile2(track1, track2, weight = lambda A, B : A + B, verbose = True):   
	
    """Profile of difference between two traces
    
    :return: A track objet, with an analytical feature diff containing shortest distance
             of each point of track t1, to the points of track t2. We may get profile as
             a list with :func:`output.getAbsCurv()` and
             :func:`output.getAnalyticalFeature("diff")` 
             The selected candidate in registerd in AF "pair" 
             Set "ends" parameter to True to force end points to
             meet p is Minkowski's exponent for distance computation. Default value is
             - 1 for summation of distances, 
             - 2 for least squares solution 
             - and 10 for an approximation of Frechet solution.
    """

    output = track1.copy()

    output.createAnalyticalFeature("diff")
    output.createAnalyticalFeature("pair")
    output.createAnalyticalFeature("ex")
    output.createAnalyticalFeature("ey")

    N1 = track1.size()
    N2 = track2.size()

    step_to_run = range(1, N1)
    if verbose:
        step_to_run = progressbar.progressbar(step_to_run)

    # Forming distance matrix
    D = np.zeros((N2, N1))
    for i in range(N2):
        for j in range(N1):
            D[i, j] = track2.getObs(i).distance2DTo(track1.getObs(j))

	# ----------------------------------------------------------
    # Optimal path with dynamic programming
	# ----------------------------------------------------------
	
    T = np.zeros((N2, N1))
    M = np.zeros((N2, N1))
    T[:, 0] = D[:, 0]
        
    # Forward step
    for j in step_to_run:
        MC = _minCumul(T[:, j-1])
        T[:, j] = weight(MC[0], D[:, j])
        M[:, j] = MC[1]
        
    # Backward step
    S = [0] * (track1.size())  
    S[N1-1] = np.argmin(T[:, N1-1])
    for i in range(N1-2, -1, -1):
        S[i] = int(M[S[i+1], i+1])

    # plt.plot(S, 'r-')   
    # plt.imshow(T)
    # plt.show()
    
    __fillAFProfile(track1, track2, output, S)
    
    output.score = T[S[N1-1], N1-1]

    return output



def differenceProfile(track1, track2, mode: Literal["NN", "DTW", "FDTW"] = "NN", 
                      ends=False, p=1, verbose: bool = True):   
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
             :func:`output.getAnalyticalFeature("diff")` 
             The selected candidate in registerd in AF "pair" 
             Set "ends" parameter to True to force end points to
             meet p is Minkowski's exponent for distance computation. Default value is
             - 1 for summation of distances, 
             - 2 for least squares solution 
             - and 10 for an approximation of Frechet solution.
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
            ex = track1.getObs(i).position.getX() - track2.getObs(id_min).position.getX()
            ey = track1.getObs(i).position.getY() - track2.getObs(id_min).position.getY()
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

        HMM(S, Q, P).estimate(
            output,
            ["x", "y"],
            mode=MODE_OBS_AS_2D_POSITIONS,
            verbose=2 * verbose,
        )

        __fillAFProfile(track1, track2, output, output["hmm_inference"])

    computeAbsCurv(output)
    return output


def __fillAFProfile(track1, track2, output, S):
    """TODO

    :param track1: TODO
    :param track2: TODO
    :param output: TODO
    :param S: TODO
    """
    for i in range(track1.size()):
        d = track1.getObs(i).distance2DTo(track2.getObs(S[i]))
        ex = track1.getObs(i).position.getX() - track2.getObs(S[i]).position.getX()
        ey = track1.getObs(i).position.getY() - track2.getObs(S[i]).position.getY()
        output.setObsAnalyticalFeature("diff", i, d)
        output.setObsAnalyticalFeature("pair", i, S[i])
        output.setObsAnalyticalFeature("ex", i, ex)
        output.setObsAnalyticalFeature("ey", i, ey)


#def synchronize(track1, track2):
#    """Resampling of 2 tracks with linear interpolation on a common base of
#    timestamps
#
#    :param track: track to synchronize with
#    """
#
#    synchronize(track1, track2)
#

def compare(track1, track2) -> float:   
    """Comparison of 2 tracks.

    Tracks are interpolated linearly on a common base of timestamps

    :param track1: track to compare with
    :param track2: track to compare with

    :return: TODO
    """

    trackA = track1.copy()
    trackB = track2.copy()

    synchronize(trackA, trackB)

    rmse = 0
    for i in range(trackA.size()):
        rmse += trackA.getObs(i).distanceTo(trackB.getObs(i)) ** 2

    return math.sqrt(rmse / trackA.size())


# Union[TrackCollection, Iterable[Track]]
# Literal["NN", "DTW", "FDTW"]
# bool
# -> Track
def centralTrack(tracks, mode="NN", verbose=True):   
    """Computes central track of a track collection

    :param tracks: TrackCollection or list of tracks
    :param mode: "NN", "DTW" or "FDTW" for track pair matching (see the documentation
                  of :func:`differenceProfile` function for more infos on modes)
    :return: The central track
    """

    tracks = tracks.copy()

    if isinstance(tracks, list):
        tracks = tracklib.TrackCollection(tracks)
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


def premiereComposanteHausdorff(track1, track2):
    '''
    Première composante de Hausdorff.

    Parameters
    ----------
    track1 : Track
        the first track
    track2 : Track
        the second track

    Returns
    -------
    double
        directed Hausdorff distance

    '''
    result = 0
    for p in range(track1.size()):
        point = track1.getObs(p)
        distmin = track2.getFirstObs().distanceTo(point);
        for i in range(0, track2.size() - 1): 
            obs2i = track2.getObs(i)
            obs2ip1 = track2.getObs(i+1)
            dist = dist_point_to_segment(point.position, 
                        [obs2i.position.getX(), obs2i.position.getY(), 
                        obs2ip1.position.getX(), obs2ip1.position.getY()])
            distmin = min(dist, distmin)
        result = max(distmin, result)
    return result
  

def hausdorff(track1, track2):
    '''
    General Hausdorff distance between two tracks.

    Parameters
    ----------
    track1 : Track
        the first track
    track2 : Track
        the second track

    Returns
    -------
    double
        Hausdorff distance

    '''
    return max(premiereComposanteHausdorff(track1, track2),
        premiereComposanteHausdorff(track2, track1))


def discreteFrechet(track1, track2):
    
    sizeP = track1.size()
    sizeQ = track2.size()
    
    ca = []
    for i in range(sizeP):
        ca.append([])
        for j in range(sizeQ):
            ca[i].append(-1)
    
    d = discreteFrechetCouplingMeasure(track1, track2, sizeP - 1, sizeQ - 1, ca);
    return d;


def discreteFrechetCouplingMeasure(track1, track2, i, j, ca):
    if ca[i][j] > -1:
        return ca[i][j]

    d = track1.getObs(i).distanceTo(track2.getObs(j))
    if i == 0 and j == 0:
        ca[i][j] = d
        return d

    if i > 0 and j == 0:
       ca[i][j] = max(
           discreteFrechetCouplingMeasure(track1, track2, i - 1, j, ca), d)
       return ca[i][j]
   
    if i == 0 and j > 0:
        ca[i][j] = max(discreteFrechetCouplingMeasure(track1, track2, i, j - 1, ca), d)
        return ca[i][j]
    
    if i > 0 and j > 0:
         ca[i][j] = max(
           min(discreteFrechetCouplingMeasure(track1, track2, i - 1, j, ca), 
               min(discreteFrechetCouplingMeasure(track1, track2, i - 1, j - 1, ca),
                   discreteFrechetCouplingMeasure(track1, track2, i, j - 1, ca))), d)
         return ca[i][j]

    ca[i][j] = sys.float_info.max
    return ca[i][j]


def __meanTrack(cluster):
    N = len(cluster)
    x = cluster[0].E
    y = cluster[0].N
    z = cluster[0].U
    for i in range(1, len(cluster)):
        x += cluster[i].E
        y += cluster[i].N
        z += cluster[i].U
    return tracklib.core.obs_coords.ENUCoords(x/N, y/N, z/N)


def fusion(tracks, weight=lambda A, B : A + B**2, ref=0):

    ITER_MAX = 100

    central = tracks[ref].copy()    
    

    for iteration in range(ITER_MAX):
        
        print("ITERATION", iteration)
        
        profiles = tracklib.TrackCollection()
        central_before = central.copy()
    
        for i in range(len(tracks)):
            profile = tracklib.algo.comparison.differenceProfile2(central, tracks[i], weight, verbose=True)
            profiles.addTrack(profile)
            
        for j in range(len(central)):
            cluster = []
            for i in range(len(profiles)):
                cluster.append(tracks[i][profiles[i]["pair", j]].position)
            central[j].position = __meanTrack(cluster)
        
        profile = tracklib.algo.comparison.differenceProfile2(central, central_before, weight, verbose=True)
        print("CV = ", profile.score)
        if (profile.score < 1e-16):
            break
        
    print("END OF COMPUTATION")
                
    return central
    
 
