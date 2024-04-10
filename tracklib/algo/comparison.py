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


to manage:
    - comparisons of GPS tracks 
    - track distance measures 

"""


import sys
import math
from typing import Literal
import progressbar
import numpy as np
import matplotlib.pyplot as plt

import tracklib as tracklib
from tracklib.util import dist_point_to_segment, Polygon, centerOfPoints
from . import synchronize, computeRadialSignature
from tracklib.core import (ENUCoords, TrackCollection, 
                           Obs, ObsTime,
                           priority_dict, co_median)


# ------------------------------------------------------------------------------
# List of available matching methods
# Methods indexed by [p] are parameterized with Lp norm (default p = 1)
# Methods indexed by [s] are symetric (match(t1, t2) = match(t2, t1))
# For infinite norm: set p = float('inf')
# All methods are parameterized by a distance d.
# ------------------------------------------------------------------------------
MODE_MATCHING_NN      = 1   # Nearest Neighbour                           
MODE_MATCHING_DTW     = 2   # Dynamic Time Warping (with Lp norm)      [p][s]
MODE_MATCHING_FDTW    = 3   # Fast (and approximate) DTW               [p][s]
MODE_MATCHING_FRECHET = 4   # Discrete Frechet macthing                   [s]
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# List of available distances (or pseudo-distances) between tracks
# Methods indexed by [p] are parameterized with Lp norm (default p = 1)
# Methods indexed by [m] are based on the output of a matching
# Methods indexed by [s] are symetric (compare(t1, t2) = compare(t2, t1))
# For infinite norm: set p = float('inf')
# All methods (except aeral distance) are parameterized by a distance d.
# ------------------------------------------------------------------------------
MODE_COMPARISON_POINTWISE = 101 # Distances btw points at each index [p][m][s]
MODE_COMPARISON_NN        = 102 # Distances btw nearest neighbours   [p][m]
MODE_COMPARISON_HAUSDORFF = 103 # Haussdorf distance                       [s]
MODE_COMPARISON_AREAL     = 104 # Mac Master aeral distance                [s]
MODE_COMPARISON_RADIAL    = 105 # Radial distance (for closed loops)       [s]
MODE_COMPARISON_DTW       = 106 # Distances between DTW pairs        [p][m][s]
MODE_COMPARISON_FDTW      = 107 # Distances between FDTW pairs       [p][m][s]
MODE_COMPARISON_FRECHET   = 108 # Distance between Frechet pairs        [m][s] 
MODE_COMPARISON_SYNC      = 109 # Time-synchronized comparison       [p][m][s]
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------
# Parameters for fusion algorithm
# ------------------------------------------------------------------------
# List of available methods to choose representative point selection
MODE_BARYCENTRE   = 201      # Average of coordinates
MODE_MEDIAN_TIME  = 202      # Position at median time of observations
MODE_FURTHEST_OBS = 203      # Furthest point from master track 
# ------------------------------------------------------------------------
# List of available methods to choose representative point selection
MODE_MEDIAN = 300            # Component-wise median of coordinates
MODE_L1     = 301            # Geometric median of points
MODE_L2     = 302            # Standard barycenter of points
MODE_LInf   = 303            # Center of minimum enclosing circle
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Compare two tracks to measure a distance (or pseudo-distance) between them.
# Available distances are: pointwise comparison, haussdorf and discrete Frechet.
# Other available methods are: radial distance (pseudo-distance), aeral distance 
# (semi-distance) and dynamic time warping (semi-distance) and nearest neigbour 
# comparison (no distance property). Note that dicrete frechet distance is 
# obtained equivalently by DTW with Lp norm set to p = float('inf'). 
# ------------------------------------------------------------------------------
def compare(track1, track2, mode=MODE_COMPARISON_POINTWISE, p=1, dim=2, verbose=True, plot=False) -> float:
    if (mode == MODE_COMPARISON_POINTWISE):
        return _compare_pointwise(track1, track2, p, dim)
    if (mode == MODE_COMPARISON_SYNC):
        return _synchronized_comparison(track1, track2, p, dim)       
    if (mode == MODE_COMPARISON_NN):
        return _nn_comparison(track1, track2, p, dim, verbose)
    if (mode == MODE_COMPARISON_HAUSDORFF):
        return _hausdorff(track1, track2)
    if (mode == MODE_COMPARISON_AREAL):
        return _arealStandardizedBetweenTwoTracks(track1, track2)
    if (mode == MODE_COMPARISON_RADIAL):
        return _radial_comparison(track1, track2)
    if (mode == MODE_COMPARISON_FRECHET):
        return _dtw_comparison(track1, track2, float('inf'), dim, verbose, plot)
    if (mode == MODE_COMPARISON_DTW):
        return _dtw_comparison(track1, track2, p, dim, verbose, plot)
    if (mode == MODE_COMPARISON_FDTW):
        return _fdtw_comparison(track1, track2, p, dim, verbose, plot)
    print("Unavailable mode for comparison of 2 tracks")
    sys.exit(0)


# ------------------------------------------------------------------------------
# Match two tracks: returns an n:m coupling between track points. Each point has 
# at least one homologue point. Available methods are: Nearest Neihbour, 
# (discrete) Frechet distance, dynamic time warping and fast approximate dynamic
# time warping. Note that dicrete Frechet matching is obtained equivalently by 
# DTW matching with Lp norm set to p = float('inf'). 
# Output: a track with size of track1 and with links towards track2
# ------------------------------------------------------------------------------
def match(track1, track2, mode=MODE_MATCHING_DTW, p=1, dim=2, verbose=True, plot=False):
    if (mode == MODE_MATCHING_NN):
        return _nn(track1, track2, dim, verbose)
    if (mode == MODE_MATCHING_FRECHET):
        return _dtw_matching(track1, track2, float('inf'), dim, verbose, plot)
    if (mode == MODE_MATCHING_DTW):
        return _dtw_matching(track1, track2, p, dim, verbose, plot)
    if (mode == MODE_MATCHING_FDTW):
        return _fdtw_matching(track1, track2, p, dim, verbose, plot)
    print("Unavailable mode for matching of 2 tracks")
    sys.exit(0)


# ------------------------------------------------------------------------------
# Generic function for geometric distance between 2 points p1 and p2
# dim = 1: 1D altimetric euclidian distance
# dim = 2: 2D planimetric euclidian distance
# dim = 3: 3D distance euclidian distance
# lambda function between ENUCoords: direct application of lambda function
# ------------------------------------------------------------------------------
def _distance(p1, p2, dim):
    if (dim == 1):
        return abs(p1.U - p2.U)
    if (dim == 2): 
        return p1.distance2DTo(p2)
    if (dim == 3):
        return p1.distanceTo(p2)
    if ('function' in str(type(dim))):
        return dim(p1, p2)

# ------------------------------------------------------------------------------
# Pointwise distance: Lp norm average of pointwised distances
# Exponent p should nominally be in [0, Inf], but negative values are accepted
# ------------------------------------------------------------------------------
def _compare_pointwise(track1, track2, p, dim) -> float:
    if (len(track1) != len(track2)):
        print("Error: tracks must have same size to be compared with pointwise method")
        sys.exit(1)
    N = len(track1)
    d = 0
    if p == 0:
        for i in range(N):
            d += (_distance(track1[i].position, track2[i].position, dim) > 0)*1
        return d
    if p == float('inf'): 
        for i in range(N):
            d = max(d, _distance(track1[i].position, track2[i].position, dim))
        return d
    for i in range(N):
        d += _distance(track1[i].position, track2[i].position, dim)**p
    return (d/N)**(1.0/p)
            


# ------------------------------------------------------------------------------
# Auxiliary function for Haussdorf computation
# ------------------------------------------------------------------------------
def _premiereComposanteHausdorff(track1, track2):
    result = 0
    for p in range(track1.size()):
        point = track1.getObs(p)
        distmin = track2.getFirstObs().distance2DTo(point);
        for i in range(0, track2.size() - 1): 
            obs2i = track2.getObs(i)
            obs2ip1 = track2.getObs(i+1)
            
            if isinstance(obs2ip1.position, ENUCoords):
                if obs2ip1.position == obs2i.position:
                    continue
            
            dist = dist_point_to_segment(point.position, 
                        [obs2i.position.getX(), obs2i.position.getY(), 
                        obs2ip1.position.getX(), obs2ip1.position.getY()])
            distmin = min(dist, distmin)
        result = max(distmin, result)
    return result
  

# ------------------------------------------------------------------------------
# Haussdorf distance computation
# ------------------------------------------------------------------------------
def _hausdorff(track1, track2):
    return max(_premiereComposanteHausdorff(track1, track2),
        _premiereComposanteHausdorff(track2, track1))

# ------------------------------------------------------------------------------
# Aeral distance computation
# ------------------------------------------------------------------------------
def _arealStandardizedBetweenTwoTracks(track1, track2):
    '''
    Areal between track1 and track2. We divide by the average of the tracks lengths 
    to make the measure independent with any other tracks.
    
    Robert B. McMaster (1986) A Statistical Analysis of Mathematical Measures 
    for Linear Simplification, The American Cartographer, 13:2, 103-116, 
    DOI: 10.1559/152304086783900059
    '''
    
    # create polygon
    d1 = track1.getLastObs().distanceTo(track2.getFirstObs())
    d2 = track1.getLastObs().distanceTo(track2.getLastObs())
    if (d1 < d2):
        X = track1.getX() + track2.getX()
        Y = track1.getY() + track2.getY()
    else:
        nt = track2.reverse()
        X = track1.getX() + nt.getX()
        Y = track1.getY() + nt.getY()
    p = Polygon(X, Y)
    
    return 2*p.area() / (track1.length() + track2.length())


# ------------------------------------------------------------------------------
# Synchronization of two track for pointwise comparison
# ------------------------------------------------------------------------------
def _synchronized_comparison(track1, track2, p, dim):
    trackA = track1.copy()
    trackB = track2.copy()
    synchronize(trackA, trackB)
    
    N = len(trackA)

    if N <= 0:
        return 

    d = 0

    if p == 0:
        for i in range(N):
            d += (_distance(trackA.getObs(i).position, trackB.getObs(i).position, dim) > 0)*1
        return d
    if p == float('inf'): 
        for i in range(N):
            d = max(d, _distance(trackA.getObs(i).position, trackB.getObs(i).position, dim))
        return d
    for i in range(N):
        d += _distance(trackA.getObs(i).position, trackB.getObs(i).position, dim)**p
    return (d/N)**(1.0/p)
    

# ------------------------------------------------------------------------------
# Radial (semi) distance comparison
# ------------------------------------------------------------------------------
def _radial_comparison(track1, track2):
    signature1 = computeRadialSignature(track1)
    signature2 = computeRadialSignature(track2)
    plt.plot(signature1['s'], signature1['r'], 'r-')
    plt.plot(signature2['s'], signature2['r'], 'b-')

# ------------------------------------------------------------------------------
# Comparison based on Nearest Neighbor
# ------------------------------------------------------------------------------
def _nn_comparison(track1, track2, p, dim, verbose):
    matching = _nn(track1, track2, dim, verbose)
    N = len(matching)
    d = 0
    if p == 0:
        for i in range(N):
            d += (matching["diff", i] > 0)*1
        return d
    if p == float('inf'): 
        for i in range(N):
            d = max(d, matching["diff", i])
        return d
    for i in range(N):
        d += matching["diff", i]**p
    return (d/N)**(1.0/p)


# ------------------------------------------------------------------------------
# Bi-directional Nearest Neighbor computation
# ------------------------------------------------------------------------------
def _nn(track1, track2, dim, verbose):
    # 1 -> 2 matching
    matching = _nn_mono(track1, track2, dim, verbose)

    # 2 -> 1 matching
    matching_reverse = _nn_mono(track2, track1, dim, verbose)
   
    matching_in_2 = {}
    for i in range(len(matching)):
        matching_in_2[matching[i, "pair"][0]] = 0
    for j in range(len(matching_reverse)):
        if not j in matching_in_2:
            matching[matching_reverse[j, "pair"][0], "pair"].append(j)
  
    return matching

# ------------------------------------------------------------------------------
# Mono-directional Nearest Neighbor computation
# ------------------------------------------------------------------------------
def _nn_mono(track1, track2, dim, verbose):

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
    to_run = range(output.size())
    if verbose:
        to_run = progressbar.progressbar(to_run)
    for i in to_run:
        val_min = sys.float_info.max
        id_min = 0
        for j in range(track2.size()):
            distance = _distance(output.getObs(i).position, track2.getObs(j).position, dim)
            if distance < val_min:
                val_min = distance
                id_min = j
        output.setObsAnalyticalFeature("diff", i, val_min)
        output.setObsAnalyticalFeature("pair", i, [id_min])
        ex = track1.getObs(i).position.getX() - track2.getObs(id_min).position.getX()
        ey = track1.getObs(i).position.getY() - track2.getObs(id_min).position.getY()
        output.setObsAnalyticalFeature("ex", i, ex)
        output.setObsAnalyticalFeature("ey", i, ey)

    return output


# ------------------------------------------------------------------------------
# Weight (possible) conversion auxiliary function: p -> weight
# ------------------------------------------------------------------------------
def _p2weight(p):
    if 'function' in str(type(p)):
        weight = p
    if ('int' in str(type(p))) or ('float' in str(type(p))):
        weight = lambda A, B : A + B**p
    if (p == 0):
        weight = lambda A, B : A + (B != 0)*1
    if (p == float('inf')):
        weight = lambda A, B : max(A, B) 
    return weight

# ------------------------------------------------------------------------------
# Comparison based on Fast Dynamic Time Warping
# ------------------------------------------------------------------------------
def _fdtw_comparison(track1, track2, p, dim, verbose, plot):
    matching = _fdtw_matching(track1, track2, p, dim, verbose, plot)
    if ((p == 0) or (p == float('inf'))):
        return matching.score
    return (matching.score/matching.nb_links)**(1.0/p)

# ------------------------------------------------------------------------------
# Matching based on Fast Dynamic Time Warping
# ------------------------------------------------------------------------------
def _fdtw_matching(track1, track2, p, dim, verbose, plot):
    return _fdtw(track1, track2, _p2weight(p), dim, verbose, plot)

# ------------------------------------------------------------------------------
# Fast Dynamic Time Warping computation
# For classical Lp norm, set the weight function as follows:
#    - p = 0                  weight = lambda A, B : A + (B != 0)*1
#    - p = 1                  weight = lambda A, B : A + B**1
#    - p = 2                  weight = lambda A, B : A + B**2
#    - p = float('inf')       weight = lambda A, B : max(A, B)
# ------------------------------------------------------------------------------
def _fdtw(track1, track2, weight = lambda A, B : A + B, dim=2, verbose = True, plot=False):   
    
    output = track1.copy()

    output.createAnalyticalFeature("diff")
    output.createAnalyticalFeature("pair")
    output.createAnalyticalFeature("ex")
    output.createAnalyticalFeature("ey")

    N1 = track1.size()
    N2 = track2.size()
    
    if (plot):
        D = np.zeros((N2, N1))

    # ----------------------------------------------------------
    # Optimal path with dynamic programming
    # ----------------------------------------------------------
    T = np.zeros((N2, N1)); T[0,0] = weight(0, _distance(track2.getObs(0).position, track1.getObs(0).position, dim))
    F = priority_dict({(0,0): 0})
    V =  priority_dict()
    A = dict({(0,0): (-1, -1)})
    if (plot):
        D[0,0] = T[0,0]

    # Forward step 
    counter = 0
    step_to_run = range(1, N1)
    if verbose:
        counter = 0
        bar = progressbar.ProgressBar(max_value=N1-1)

    while(1):
        node = F.pop_smallest(); i = node[0]; j = node[1]; 
        if verbose:
            counter = max(i, counter); 
            bar.update(counter)
        V[node] = 1
        if ((i == N2-1) and (j == N1-1)):
            break
        if ((i < N2-1) and (j < N1-1)): 
            dist = _distance(track2.getObs(i+1).position, track1.getObs(j+1).position, dim)
            _update_node(F, T, (i+1, j+1), weight(T[i,j], dist), V, A, node)
            if (plot):
                D[i+1, j+1] = dist
        if (j < N1-1):
            dist = _distance(track2.getObs(i  ).position, track1.getObs(j+1).position, dim)
            _update_node(F, T, (i  , j+1), weight(T[i,j], dist), V, A, node)
            if (plot):
                D[i, j+1] = dist
        if (i < N2-1):       
            dist =  _distance(track2.getObs(i+1).position, track1.getObs(j  ).position, dim)
            _update_node(F, T, (i+1, j  ), weight(T[i,j], dist), V, A, node) 
            if (plot):
                D[i+1, j] = dist
    
    # Backward step
    S = [(N2-1, N1-1)] 
    while((S[-1][0] > 0) or (S[-1][1] > 0)):
        S.append(A[S[-1]])

    if (plot):
        plt.imshow(T)
        for i in range(len(S)):
            plt.plot(S[i][1], S[i][0], 'r.', markersize=2)
        plt.show()

    return _fillAF_dtw(output, track1, track2, S, T, dim)
    
# ------------------------------------------------------------------------------
# Auxiliary function for Fast Dynamic Time Warping
# ------------------------------------------------------------------------------    
def _update_node(F, T, node, new_cost, V, A, ant):
    if node in V:
        return
    if not node in F:
        F[node] = 1e300
    if new_cost < F[node]:
        F[node] = new_cost
        A[node] = ant
        T[node[0], node[1]] = new_cost


# ------------------------------------------------------------------------------
# Comparison based on Dynamic Time Warping
# ------------------------------------------------------------------------------
def _dtw_comparison(track1, track2, p, dim, verbose, plot):
    matching = _dtw_matching(track1, track2, p, dim, verbose, plot)
    if ((p == 0) or (p == float('inf'))):
        return matching.score
    return (matching.score/matching.nb_links)**(1.0/p)

# ------------------------------------------------------------------------------
# Matching based on Dynamic Time Warping
# ------------------------------------------------------------------------------
def _dtw_matching(track1, track2, p, dim, verbose, plot):
    return _dtw(track1, track2, _p2weight(p), dim, verbose, plot)

# ------------------------------------------------------------------------------
# Dynamic Time Warping computation
# For classical Lp norm, set the weight function as follows:
#    - p = 0                  weight = lambda A, B : A + (B != 0)*1
#    - p = 1                  weight = lambda A, B : A + B**1
#    - p = 2                  weight = lambda A, B : A + B**2
#    - p = float('inf')       weight = lambda A, B : max(A, B)
# ------------------------------------------------------------------------------
def _dtw(track1, track2, weight = lambda A, B : A + B, dim=2, verbose = True, plot=False):   
    
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
            D[i, j] = _distance(track2.getObs(i).position, track1.getObs(j).position, dim)

    # ----------------------------------------------------------
    # Optimal path with dynamic programming
    # ----------------------------------------------------------
    T = np.zeros((N2, N1))
    M = np.ones( (N2, N1)) * (-1 + (-1)*1j)

    T[0, 0] = weight(0, D[0, 0])
    for i in range(1, N2):
        T[i,0] = weight(T[i-1,0], D[i,0])
        M[i,0] = (i-1) + 0*1j
    for j in range(1, N1):
        T[0,j] = weight(T[0,j-1], D[0,j])
        M[0,j] = 0 + (j-1)*1j

    # Forward step
    for j in step_to_run:
        for i in range(1, N2):
            l = T[i, j-1]; u = T[i-1,j]; ul = T[i-1,j-1]
            T[i,j] = weight(min(ul, min(u, l)), D[i,j])
            M[i,j] = (i-(l>=min(ul, u))) + (j-(u>=min(ul, l)))*1j

    # Backward step
    S = [(N2-1, N1-1)] 
    while((S[-1][0] > 0) or (S[-1][1] > 0)):
        m = M[S[-1][0], S[-1][1]]
        S.append((int(np.real(m)), int(np.imag(m))))

    if (plot):
        plt.imshow(T)
        for i in range(len(S)):
            plt.plot(S[i][1], S[i][0], 'r.', markersize=2)
        plt.show()

    return _fillAF_dtw(output, track1, track2, S, T, dim)
    

# ------------------------------------------------------------------------------
# Auxiliary function for Dynamic Time Warping and Fast Dynamic Time Warping
# ------------------------------------------------------------------------------    
def _fillAF_dtw(output, track1, track2, S, T, dim):
    output.nb_links = 0 
    for i in range(len(output)):
        output.setObsAnalyticalFeature("pair", i, [])
    for i in range(len(S)):
        d =  _distance(track1.getObs(S[i][1]).position, track2.getObs(S[i][0]).position, dim)
        ex = track1.getObs(S[i][1]).position.getX() - track2.getObs(S[i][0]).position.getX()
        ey = track1.getObs(S[i][1]).position.getY() - track2.getObs(S[i][0]).position.getY()
        output.setObsAnalyticalFeature("diff", S[i][1], d)
        output.getObsAnalyticalFeature("pair", S[i][1]).append(S[i][0]); output.nb_links += 1
        output.setObsAnalyticalFeature("ex", S[i][1], ex)
        output.setObsAnalyticalFeature("ey", S[i][1], ey)
    output.score = T[-1, -1]
    return output

# ------------------------------------------------------------------------------
# Function to plot matching output from 'match' method
# ------------------------------------------------------------------------------
def plotMatching(matching, track2, af_name="pair", sym="k--", linewidth=.5, NO_DATA_VALUE: int = -1):
    for i in range(matching.size()):
        if matching.getObsAnalyticalFeature(af_name, i) == NO_DATA_VALUE:
            continue
        x1 = matching.getObs(i).position.getX()
        y1 = matching.getObs(i).position.getY()
        pairs = matching.getObsAnalyticalFeature(af_name, i)
        for pair in pairs:
            x2 = track2.getObs(pair).position.getX()
            y2 = track2.getObs(pair).position.getY()
            plt.plot([x1, x2], [y1, y2], sym, linewidth=linewidth)



# ------------------------------------------------------------------------
# Auxiliary function to map center of cluster on existing point
# ------------------------------------------------------------------------
def _constrain_center(position, cluster):
    d = sys.float_info.max; pos = -1
    for i in range(N):
        if _distance(cluster[i], position, 2) < d:
            pos = i
            d = _distance(cluster[i], position, 2)
    return cluster[pos].copy()


# ------------------------------------------------------------------------
# Algorithme fusion L. Etienne : trajectoire médiane
# ------------------------------------------------------------------------
def __fusion(tracks, mode=MODE_MATCHING_DTW, ref=0, p=2, dim=2,
             represent_method=MODE_BARYCENTRE, agg_method=MODE_L2, 
             constraint=False, verbose=True, plot=False):

    central = tracks[ref].copy()
    
    ITER_MAX = 100
    TAB_CLS = {} # logging
    TAB_FUSION = {} # logging
    for iteration in range(ITER_MAX):
        if verbose:
            print("ITERATION", iteration)
        
        profiles = tracklib.TrackCollection()
        central_before = central.copy()
    
        for i in range(len(tracks)):
            profile = match(central, tracks[i], mode=mode, p=p, dim=dim, 
                            verbose=verbose, plot=plot)
            profile.createAnalyticalFeature("homologous")
            for j in range(len(central)):
                # On sélecionne le sous-ensemble Pi des positions de CTm appariés à pri
                PAIRS = profile[j, "pair"]
                if len(PAIRS) == 1:
                    profile[j, "homologous"] = tracks[i].getObs(PAIRS[0]).position
                elif len(PAIRS) > 1:
                    PAIRS.sort()
                    Pi = tracklib.Track()
                    for ind in PAIRS:
                        Pi.addObs(tracks[i].getObs(ind))
                    
                    if represent_method == MODE_BARYCENTRE:
                        profile[j, "homologous"] = Pi.getCentroid()
                    elif represent_method == MODE_MEDIAN_TIME:
                        profile[j, "homologous"] = Pi.getMedianObsInTime().position
                    elif represent_method == MODE_FURTHEST_OBS:
                        o = central.getObs(j)
                        profile[j, "homologous"] = Pi.getFurthestObs(o).position
                else:
                    profile[j, "homologous"] = profile[j, "pair"]
            profiles.addTrack(profile)
            
        CLS = []
        for j in range(len(central)):
            cluster = []
            for i in range(len(profiles)):
                cluster.append(profiles[i]["homologous", j])
            CLS.append(cluster)
            central[j].position =  centerOfPoints(cluster, mode=agg_method)
            if constraint:
                central[j].position = _constrain_center(central[j].position)
        TAB_CLS[iteration] = CLS
        
        profile = match(central, central_before, mode=mode, p=p, dim=dim, 
                        verbose=verbose, plot=plot)
        TAB_FUSION[iteration] = profile
        # central.plot('c--', append=True, pointsize=1.0)
        
        if verbose:
            print("CV = ", profile.score)
        if (profile.score < 1e-16):
            break
        
    if verbose:
        print("END OF COMPUTATION")
    
    central.score = profile.score
    central.iteration = iteration
    central.fusions = TAB_FUSION
    central.clusters = TAB_CLS
    
    return central


    
# ------------------------------------------------------------------------
# Algorithme récursif fusion L. Etienne : trajectoire médiane
# ------------------------------------------------------------------------ 
def fusion(tracks, mode=MODE_MATCHING_DTW, ref=0, p=2, dim=2,  
           represent_method=MODE_BARYCENTRE, agg_method=MODE_L2, constraint=False,
           recursive=1e300, verbose=True, plot=False):
    
    N = len(tracks)
    if N <= recursive:
        return __fusion(tracks, mode=mode, ref=ref, p=p, dim=dim, 
                        represent_method=represent_method, constraint=constraint,
                        verbose=verbose, plot=plot)
    else:
       Npg = int(N/recursive)
       subtracks = TrackCollection()
       for i in range(recursive):
           ini = Npg*i
           fin = Npg*(i+1)
           if i == (recursive-1):
               fin = len(tracks)
           subtracks.addTrack(fusion(tracks[ini:fin], weight=weight, ref=ref, p=p, constraint=constraint, agg_method=agg_method, recursive=recursive, verbose=verbose))
       return fusion(subtracks, weight=weight, ref=ref, p=p, constraint=constraint, agg_method=agg_method, recursive=recursive, verbose=verbose)


