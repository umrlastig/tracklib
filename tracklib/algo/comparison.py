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
import random
import datetime
import numpy as np
import progressbar
import matplotlib
import matplotlib.pyplot as plt


import tracklib as tracklib
#from tracklib.util.exceptions import *
from tracklib.util import dist_point_to_segment, Polygon, centerOfPoints
from . import synchronize, computeRadialSignature
from tracklib.core import (ENUCoords, TrackCollection, 
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
# Specific parameters for fusion algorithm
# ------------------------------------------------------------------------
# List of available methods to choose representative point selection
MODE_REP_BARYCENTRE   = 201   # Average of coordinates
MODE_REP_MEDIAN_TIME  = 202   # Position at median time of observations
MODE_REP_FURTHEST_OBS = 203   # Furthest point from master track 
# ------------------------------------------------------------------------
# List of available aggregate points in cluster
MODE_AGG_MEDIAN = 300         # Component-wise median of coordinates
MODE_AGG_L1     = 301         # Geometric median of points
MODE_AGG_L2     = 302         # Standard barycenter of points
MODE_AGG_LInf   = 303         # Center of minimum enclosing circle
# ------------------------------------------------------------------------
# List of available methods to choose representative point selection
MODE_MASTER_RANDOM = -200       # Random track
MODE_MASTER_MEDIAN_LEN = -100   # Closest to the median of track lengths
MODE_MASTER_MEDIAN_GEOM = -300  # Minimizes the sum of distances to other tracks
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
    raise UnknownModeError("Unavailable mode for comparison of 2 tracks")



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
    raise UnknownModeError("Unavailable mode for matching of 2 tracks")


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
        raise SizeError("Error: tracks must have same size to be compared with pointwise method")
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
            
    for j in range(len(matching)):
        matching["pair", j] = sorted(matching["pair", j])
  
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
    #N2 = track2.size()
   
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
    #step_to_run = range(1, N1)
    if verbose:
        counter = 0
        #bar = progressbar.ProgressBar(max_value=N1-1)

    while(1):
        node = F.pop_smallest(); i = node[0]; j = node[1]; 
        if verbose:
            counter = max(i, counter); 
            #bar.update(counter)
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
    if ((p == 0) or (p == float('inf')) or ('function' in str(type(p)))):
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
    for i in range(len(S)-1, -1, -1):
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
def plotMatching(matching, track2, af_name="pair", sym="k--", linewidth=.5, 
                 NO_DATA_VALUE: int = -1, append=False):
    # 
    if isinstance(append, bool):
        if append:
            ax1 = plt.gca()
        else:
            fig, ax1 = plt.subplots(figsize=(10, 3))
    elif isinstance(append, matplotlib.axes._axes.Axes):
        ax1 = append
    else:
        ax1 = plt

    for i in range(matching.size()):
        if matching.getObsAnalyticalFeature(af_name, i) == NO_DATA_VALUE:
            continue
        x1 = matching.getObs(i).position.getX()
        y1 = matching.getObs(i).position.getY()
        pairs = matching.getObsAnalyticalFeature(af_name, i)
        for pair in pairs:
            x2 = track2.getObs(pair).position.getX()
            y2 = track2.getObs(pair).position.getY()
            ax1.plot([x1, x2], [y1, y2], sym, linewidth=linewidth)


# -----------------------------------------------------------------------------
# [B1] On cherche l'index de la trace dont la longueur est la plus proche
# de la valeur médiane des longueurs de la collection des traces
# Inputs:
#   - a collection of tracks
#   - ref: index of track in list or:
# MODE_MASTER_RANDOM: random master track
# MODE_MASTER_MEDIAN_LEN: track with length closest to median of lengths
# MODE_MASTER_MEDIAN_GEOM: track that minimizes the sum of distances to the others
# -----------------------------------------------------------------------------
def _getMasterTrack(tracks, mode, mode_compare=MODE_COMPARISON_DTW, p=1):
    if mode == MODE_MASTER_MEDIAN_LEN:
        L = tracks.getLenth()
        m = co_median(L)
        imed = 0
        dmed = abs(L[0] - m)
        for k in range(1, tracks.size()):
            d = abs(L[k] - m)
            if d < dmed:
                imed = k
        ref = imed
        return ref
    if mode == MODE_MASTER_RANDOM:
        return random.sample(range(len(tracks)), 1)[0]
    if mode == MODE_MASTER_MEDIAN_GEOM:
        smax = sys.float_info.max
        ref = -1
        for k in range(0, tracks.size()):
            S = 0
            for l in range(0, tracks.size()):
                if l == k:
                    continue
                track1 = tracks[k]
                track2 = tracks[l]
                d = compare(track1, track2, mode=mode_compare, p=p, verbose=False)
                S += d
            if S < smax:
                smax = S
                ref = k
        return ref
    return mode

# ------------------------------------------------------------------------
# [B3] Method to find representative center for fusion algorithm
# Inputs: a list of matched index in an homologue track
# Input pos is an optional ENUCoords for MODE_REP_FURTHEST_OBS
# Output: ENUCoords of aggregated point
# ------------------------------------------------------------------------
def _representative(pairs, track, represent_method=MODE_REP_BARYCENTRE, pos=None):
    P = tracklib.Track([track[i] for i in pairs])
    if represent_method == MODE_REP_BARYCENTRE:
        return P.getCentroid()
    if represent_method == MODE_REP_MEDIAN_TIME:
        return P.getMedianObsInTime().position
    if represent_method == MODE_REP_FURTHEST_OBS:
        if pos is None:
            raise MissingArgumentError("Reference position must be specified for MODE_REP_FURTHEST_OBS in _representative")
        return P.getFurthestObs(pos).position
    raise UnknownModeError("Unknown mode " + str(represent_method) +" for representative of track section")
    
# ------------------------------------------------------------------------
# [B4] Auxiliary function for aggregation and potential constraint
# Constraint = map on existing point in cluster. Available modes are:
# MODE_AGG_MEDIAN: median of coordinates in x and y
# MODE_AGG_L1: geometric median
# MODE_AGG_L2: geometric mean
# MODE_AGG_LInf: center of smallest enclosing circle
# ------------------------------------------------------------------------
def _aggregate(cluster, mode=MODE_AGG_MEDIAN, constraint=False, anchors=None):
    center = centerOfPoints(cluster, mode=mode)
    if constraint:
       center = _constrain_center(center, anchors)
    return center
    
# ------------------------------------------------------------------------
# [B4] Auxiliary function to map center on on anchors
# ------------------------------------------------------------------------
def _constrain_center(position, anchors):
    d = sys.float_info.max; pos = -1
    for i in range(len(anchors)):
        if _distance(anchors[i], position, 2) < d:
            pos = i
            d = _distance(anchors[i], position, 2)
    return anchors[pos].copy()


# ------------------------------------------------------------------------
# Debugging tool to print details of matching
# ------------------------------------------------------------------------
def printMatching(matching):
    print("----------------------------------------------------")
    print("MATCHING DETAILS")
    print("----------------------------------------------------")
    for i in range(len(matching)):
        print(i, "->", matching[i, "pair"])
    print("----------------------------------------------------")


# ------------------------------------------------------------------------
# One iteration for fusion algorithm
# ------------------------------------------------------------------------
def _fusion_iteration(central, tracks, mode, p, dim, represent_method, agg_method, constraint, verbose):

    matchings = tracklib.TrackCollection()
    for i in range(len(tracks)):
        matching = match(central, tracks[i], mode=mode, p=p, dim=dim, verbose=verbose)
        matching.createAnalyticalFeature("homologous")
        for j in range(len(central)):
            matching[j, "homologous"] = _representative(matching[j, "pair"], tracks[i], represent_method, pos=central.getObs(j))
        matchings.addTrack(matching)

    CLS = []
    for j in range(len(central)):
        cluster = [matchings[i]["homologous", j] for i in range(len(matchings))]
        anchors = [tracks[k][i].position for k in range(len(tracks)) for i in matchings[k][j, "pair"]]
        central[j].position = _aggregate(cluster, agg_method, constraint, anchors)
        CLS.append(cluster)
    central.clusters.append(CLS)

# ------------------------------------------------------------------------
# Algorithme fusion L. Etienne : trajectoire médiane
# ------------------------------------------------------------------------
def _fusion(tracks, mode, master, p, dim, represent_method, agg_method, constraint, iter_max, verbose):

    start_time = datetime.datetime.now()

    master = _getMasterTrack(tracks, mode=master)
    central = tracks[master].copy()
    
    central.clusters    = []       # logging
    central.iterations  = []       # logging
    central.convergence = []       # logging

    for iteration in range(iter_max):

        if verbose:
            print("[" + str(datetime.datetime.now()) + "]   ITERATION", iteration)
            
        central.iterations.append(tracklib.Track([obs.copy() for obs in central]))
        central_before = central.copy()

        _fusion_iteration(central, tracks, mode, p, dim, represent_method, agg_method, constraint, verbose)

        evolution = compare(central, central_before, mode=MODE_COMPARISON_POINTWISE, p=1)
        central.convergence.append(evolution)
        
        if verbose:
            print("CV = ", evolution)
        if (evolution < 1e-16):
            break
         
    if ((iteration == iter_max-1) and (evolution > 0)):
        print("WARNING: TRAJECTORY FUSION HAS NOT CONVERGED (#ITER = " + str(iter_max) + " - CV = " + str(central.convergence[-1]) + ")")    
    
    end_time = datetime.datetime.now()
    
    if verbose:
        print("[" + str(end_time) + "]    COMPUTATION DONE IN " + str(end_time-start_time))
    
    central.iteration = iteration
    central.master = master
    central.time = str(end_time-start_time)

    return central


# ------------------------------------------------------------------------
# Algorithme récursif fusion L. Etienne : trajectoire médiane
# ------------------------------------------------------------------------ 
def fusion(tracks, mode=MODE_MATCHING_DTW, master=MODE_MASTER_MEDIAN_LEN, p=1, dim=2,
           represent_method=MODE_REP_BARYCENTRE, agg_method=MODE_AGG_MEDIAN, constraint=True,
           recursive=1e300, iter_max=100, verbose=True):
    
    N = len(tracks)

    # Terminal case
    if N <= recursive:
        return _fusion(tracks, mode=mode, master=master, p=p, dim=dim, represent_method=represent_method, agg_method=agg_method, constraint=constraint, iter_max=iter_max, verbose=verbose)

    # Recursive call
    else: 
       Npg = int(N/recursive)
       subtracks = TrackCollection()
       for i in range(recursive):
           ini = Npg*i; fin = Npg*(i+1)
           if i == (recursive-1):
               fin = len(tracks)
           subtracks.addTrack(fusion(tracks[ini:fin], mode=mode, master=master, p=p, dim=dim, represent_method=represent_method, constraint=constraint, agg_method=agg_method, recursive=recursive, verbose=verbose))
       return fusion(subtracks, mode=mode, master=master, p=p, dim=dim, represent_method=represent_method, constraint=constraint, agg_method=agg_method, recursive=recursive, verbose=verbose)


