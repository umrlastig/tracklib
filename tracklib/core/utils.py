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



This module contains an algorithm of Analytical Features calculation and 
some utility functions.
"""

# For type annotation
from __future__ import annotations   
from typing import Any, Optional, Union
#from tracklib.util.exceptions import *

import json
import sys
import numpy as np

import matplotlib.colors as mcolors

from heapq import heapify, heappush, heappop

import math
import random
import itertools
import matplotlib.pyplot as plt

try:
    import shapely
except ImportError:
    print ('Code running in a no shapely environment')


# =============================================================================
#   Gestion des valeurs non renseignées et non calculées
# =============================================================================

NAN = float("nan")


def isnan(number: Union[int, float]) -> bool:   
    """Check if two numbers are different"""
    return number != number

def removeNan(T:list) -> list:
    newList = list()
    for element in T:
        if not isnan(element):
            newList.append(element)
    return newList

def isfloat(value: Any) -> bool:   
    """Check is a value is a float"""
    try:
        float(value)
        return True
    except ValueError:
        return False
    
def islist(value: Any) -> bool:   
    """Check is a value is a list"""
    try:
        tab = json.loads(value)
        return type(tab) == list
    except ValueError:
        return False


def listify(input) -> list[Any]:   
    """Make to list if needed"""
    if not isinstance(input, list):
        input = [input]
    return input


def unlistify(input):
    """Remove list if needed

    :param input: TODO
    :return: TODO
    """
    if len(input) == 1:
        input = input[0]
    return input


def compLike(s1, s2) -> bool:   
    """LIKE comparisons.
    
    Examples:
        compLike("3", "['1234', '4567', '9090']")
        compLike("abcdefg", "%bcd")

    :param s1: TODO
    :param s2: TODO
    :return: TODO
    """
    tokens = s2.split("%")
    if len(tokens) == 1:
        return s1 in s2  # 'in' ('equal' yet to be decided)
    occ = []
    s = s1
    for tok in tokens:
        id = s.find(tok)
        if id < 0:
            return False
        occ.append(id)
        s = s[id + len(tok) : len(s)]
    return True


def addListToAF(track, af_name, array):
    """TODO"""
    if af_name == None:
        return
    for i in range(track.size()):
        track.setObsAnalyticalFeature(af_name, i, array[i])
        
        
def makeRPN(expression: str) -> str:   
    """Applying operators through algebraic expressions.
    
    .. code-block:: python
    
       tab = makeRPN('a*(b+c/2)')

    :param expression: An RPN expression
    :return: array
    """
    s = expression
    for operator in ["=", "<>", "+-", "!", "*/", "%", "^", "@", "&$"]:
        depth = 0
        for p in range(len(s) - 1, -1, -1):
            if s[p] == ")":
                depth += 1
            if s[p] == "(":
                depth -= 1
            if not depth and s[p] in operator:
                return (makeRPN(s[:p]) + makeRPN(s[p + 1 :])) + [s[p]]
    s = s.strip()
    if s[0] == "(":
        return makeRPN(s[1:-1])
    return [s]

        

# --------------------------------------------------------------------------
# Function to form distance matrix (old version)
# --------------------------------------------------------------------------
# Input :
#   - T1     :: a list of points
#   - T2     :: a list of points
# --------------------------------------------------------------------------
# Output : numpy distance matrix between T1 and T2
# --------------------------------------------------------------------------    
def makeDistanceMatrixOld(T1, T2):
    
    T1 = np.array(T1)
    T2 = np.array(T2)
    
    # Signal stationnarity
    base = min(np.concatenate((T1,T2)))
    T1 = T1 - base
    T2 = T2 - base
    T1 = T1.T
    T2 = T2.T

    return np.sqrt((T1**2).reshape(-1, 1) + (T2**2) - 2 * (T1.reshape(-1, 1)*T2.T))
    
def makeDistanceMatrix(track, mode = 'linear'):
    """Function to form distance matrix

    :param track: a track
	:mode: computation mode ('linear', 'circular' or 'euclidian')
    :return: numpy distance matrix with a track
    """
    if mode not in ['linear', 'circular', 'euclidian']:
       raise UnknownModeError("Error: unknown mode: "+str(mode))
    if mode in ['linear', 'circular']:
        S = np.array(track.getAnalyticalFeature("abs_curv"))
        z = np.array([complex(s, 0) for s in S])	
    if mode == 'euclidian':
	    z = np.array([complex(obs.position.getX(), obs.position.getY()) for obs in track])
    m, n = np.meshgrid(z, z)
    D = abs(m-n)
    if mode == 'circular':
        D = np.minimum(D, np.max(D)-D)
    return D


def makeCovarianceMatrixFromKernelOld(kernel, T1: list[tuple[float, float]], T2: list[tuple[float, float]], factor: float = 1.0, force: bool = False, cycle: bool = False):
    """Function to form covariance matrix from kernel
    :param kernel: A function describing statistical similarity between points
    :param T1: A list of points
    :param T2: A list of points
    :param factor: Unit factor of std dev (default 1.0)
    """

    D = makeDistanceMatrixOld(T1, T2)
    kfunc = np.vectorize(kernel.getFunction())
    SIGMA = factor ** 2 * kfunc(D)
    if force:
        w, v = np.linalg.eig(SIGMA)
        for i in range(w.shape[0]):
            if w[i] < 0:
                w[i] = 0
        SIGMA = v @ np.diag(w) @ v.transpose()
    return SIGMA


def makeCovarianceMatrixFromKernel(kernel, track, factor = 1.0, mode = 'linear', force = False, control = False):   
    """Function to form covariance matrix from kernel

    :param kernel: A function describing statistical similarity between points
    :param track: A track
	:mode: computation mode ('linear', 'circular' or 'euclidian')
    :param factor: Unit factor of std dev (default 1.0)
    """
    track2 = track.copy()
    for icp in range(len(control)-1,-1,-1):
        track2.insertObs(track[control[icp][0]].copy(), i=0)
    D = makeDistanceMatrix(track2, mode)

    kfunc = np.vectorize(kernel.getFunction())
    SIGMA = factor ** 2 * kfunc(D)
    if force:
        w, v = np.linalg.eig(SIGMA)
        for i in range(w.shape[0]):
            if w[i] < 0:
                w[i] = 0
        SIGMA = v @ np.diag(w) @ v.transpose()
    return SIGMA

def randomColor():
    """TODO"""
    return [random.random(), random.random(), random.random()]

def rgbToHex(color: list[float, float, float, Optional[float]]) -> str:   
    """Function to convert RGBA color to hexadecimal

    :param color: A 3 or 4-element array R, G, B [,alpha]. Each color and transparency
        channel is in [0,1]
    :return: A string containing color in hexadecimal
    """
    if len(color) == 3:
        color.append(1)
    R = hex((int)(color[0] * 255))[2:]
    G = hex((int)(color[1] * 255))[2:]
    B = hex((int)(color[2] * 255))[2:]
    A = hex((int)(color[3] * 255))[2:]
    if len(R) < 2:
        R = "0" + R
    if len(G) < 2:
        G = "0" + G
    if len(B) < 2:
        B = "0" + B
    if len(A) < 2:
        A = "0" + A
    return "0x" + A + B + G + R


def interpColors(v: float, vmin: float, vmax: float, cmin: list[float, float, float, Optional[float]], cmax: list[float, float, float, Optional[float]]) -> list[float, float, float, float]:   
    """
    Function to interpolate RGBA (or RGB) color between two values

    :param v: a float value
    :param vmin: minimal value of v (color cmin)
    :param vmax: maximal value of v (color cmin)
    :param cmin: a 3 or 4-element array R, G, B [,alpha]
    :param cmax: a 3 or 4-element array R, G, B [,alpha]

    :return: A 4-element array
    """
    # norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    O = []
    O.append(((vmax - v) * cmin[0] + (v - vmin) * cmax[0]) / (vmax - vmin))
    O.append(((vmax - v) * cmin[1] + (v - vmin) * cmax[1]) / (vmax - vmin))
    O.append(((vmax - v) * cmin[2] + (v - vmin) * cmax[2]) / (vmax - vmin))
    if len(cmin) == 4:
        O.append(((vmax - v) * cmin[3] + (v - vmin) * cmax[3]) / (vmax - vmin))
    return O


def getColorMap(cmin, cmax):
    """TODO

    :param cmin: TODO
    :param cmax: TODO
    :return: TODO
    """

    # On définit la map color
    cdict = {"red": [], "green": [], "blue": []}
    cdict["red"].append([0.0, None, cmin[0] / 255])
    cdict["red"].append([1.0, cmax[0] / 255, None])
    cdict["green"].append([0.0, None, cmin[1] / 255])
    cdict["green"].append([1.0, cmax[1] / 255, None])
    cdict["blue"].append([0.0, None, cmin[2] / 255])
    cdict["blue"].append([1.0, cmax[2] / 255, None])

    cmap = mcolors.LinearSegmentedColormap("CustomMap", cdict)

    return cmap


def getOffsetColorMap(cmin, cmax, part):
    """TODO

    :param cmin: TODO
    :param cmax: TODO
    :param part: TODO
    :return: TODO
    """

    # On définit la map color
    cdict = {"red": [], "green": [], "blue": []}
    cdict["red"].append([0.0, None, cmin[0] / 255])
    cdict["red"].append([part, cmin[0] / 255, cmin[0] / 255])
    cdict["red"].append([1.0, cmax[0] / 255, None])

    cdict["green"].append([0.0, None, cmin[1] / 255])
    cdict["green"].append([part, cmin[1] / 255, cmin[1] / 255])
    cdict["green"].append([1.0, cmax[1] / 255, None])

    cdict["blue"].append([0.0, None, cmin[2] / 255])
    cdict["blue"].append([part, cmin[2] / 255, cmin[2] / 255])
    cdict["blue"].append([1.0, cmax[2] / 255, None])

    cmap = mcolors.LinearSegmentedColormap("CustomMap", cdict)

    return cmap


# --------------------------------------------------------------------------
# Priority heap
# --------------------------------------------------------------------------
# Source code from Matteo Dell'Amico
# https://gist.github.com/matteodellamico/4451520
# --------------------------------------------------------------------------
class priority_dict(dict):
    """Dictionary that can be used as a priority queue.

    Keys of the dictionary are items to be put into the queue, and values
    are their respective priorities. All dictionary methods work as expected.
    The advantage over a standard heapq-based priority queue is
    that priorities of items can be efficiently updated (amortized O(1))
    using code as 'thedict[item] = new_priority.'

    The 'smallest' method can be used to return the object with lowest
    priority, and 'pop_smallest' also removes it.

    The 'sorted_iter' method provides a destructive sorted iterator.
    """

    def __init__(self, *args, **kwargs):
        super(priority_dict, self).__init__(*args, **kwargs)
        self._rebuild_heap()

    def _rebuild_heap(self):
        self._heap = [(v, k) for k, v in self.items()]
        heapify(self._heap)

    def smallest(self):
        """Return the item with the lowest priority.

        Raises IndexError if the object is empty.
        """

        heap = self._heap
        v, k = heap[0]
        while k not in self or self[k] != v:
            heappop(heap)
            v, k = heap[0]
        return k

    def pop_smallest(self):
        """Return the item with the lowest priority and remove it.

        Raises IndexError if the object is empty.
        """

        heap = self._heap
        v, k = heappop(heap)
        while k not in self or self[k] != v:
            v, k = heappop(heap)
        del self[k]
        return k

    def __setitem__(self, key, val):
        """TODO"""
        # We are not going to remove the previous value from the heap,
        # since this would have a cost O(n).
        super(priority_dict, self).__setitem__(key, val)
        if len(self._heap) < 2 * len(self):
            heappush(self._heap, (val, key))
        else:
            # When the heap grows larger than 2 * len(self), we rebuild it
            # from scratch to avoid wasting too much memory.
            self._rebuild_heap()

    def setdefault(self, key, val):
        """TODO"""
        if key not in self:
            self[key] = val
            return val
        return self[key]

    def update(self, *args, **kwargs):
        """TODO"""
        # Reimplementing dict.update is tricky -- see e.g.
        # http://mail.python.org/pipermail/python-ideas/2007-May/000744.html
        # We just rebuild the heap from scratch after passing to super.

        super(priority_dict, self).update(*args, **kwargs)
        self._rebuild_heap()

    def sorted_iter(self):
        """Sorted iterator of the priority dictionary items.

        Beware: this will destroy elements as they are returned.
        """

        while self:
            yield self.pop_smallest()


# ------------------------------------------------------------------------------
#    Aggregate array values Functions
#    co : cell_operator
# ------------------------------------------------------------------------------
def co_sum(tarray):
    """TODO"""
    tarray = listify(tarray)
    somme = 0
    for i in range(len(tarray)):
        val = tarray[i]
        if isnan(val):
            continue
        somme += val
    return somme


def co_min(tarray):
    """TODO"""
    tarray = listify(tarray)
    if len(tarray) <= 0:
        return NAN
    min = tarray[0]
    for i in range(1, len(tarray)):
        val = tarray[i]
        if isnan(val):
            continue
        if val < min:
            min = val
    return min


def co_max(tarray):
    """TODO"""
    tarray = listify(tarray)
    if len(tarray) <= 0:
        return NAN
    max = tarray[0]
    for i in range(1, len(tarray)):
        val = tarray[i]
        if isnan(val):
            continue
        if val > max:
            max = val
    return max


def co_count(tarray):
    """TODO"""
    tarray = listify(tarray)
    count = 0
    for i in range(len(tarray)):
        val = tarray[i]
        if isnan(val):
            continue
        count += 1
    return count


def co_count_distinct(tarray):
    """TODO"""
    tarray = set(listify(tarray))
    count = 0
    for val in tarray:
        if isnan(val):
            continue
        count += 1
    return count


def co_avg(tarray):
    """TODO"""
    tarray = listify(tarray)
    if len(tarray) <= 0:
        return NAN
    mean = 0
    count = 0
    for i in range(len(tarray)):
        val = tarray[i]
        if isnan(val):
            continue
        count += 1
        mean += val
    if count == 0:
        return NAN
    return mean / count


def co_dominant(tarray):
    """TODO"""
    tarray = listify(tarray)
    if len(tarray) <= 0:
        return NAN

    # Dico : clé - nb occurence
    cles_count_dictionnary = {}

    # On alimente le dictionnaire
    for val in tarray:
        if val not in cles_count_dictionnary:
            cles_count_dictionnary[val] = 1
        else:
            cles_count_dictionnary[val] += 1

    # On cherche le plus fréquent i.e. celui qui a le max d'occurence
    nbocc = 0
    dominant_value = ""
    for val in cles_count_dictionnary:
        if cles_count_dictionnary[val] > nbocc:
            nbocc = cles_count_dictionnary[val]
            dominant_value = val
    return dominant_value


def co_median(tarray):
    """TODO""" 
    tarray = listify(tarray)
    if len(tarray) <= 0:
        return NAN
    
    # On retire les NAN
    tarray2 = []
    for i in range(len(tarray)):
        val = tarray[i]
        if isnan(val):
            continue
        tarray2.append(val)

    n = len(tarray2)
    # on tri le tableau pour trouver le milieu
    tab_sort = []
    for i in range(n):
        valmin = tarray2[0]
        # Recherche du min
        for val in tarray2:
            if val <= valmin:
                valmin = val
        tarray2.remove(valmin)
        tab_sort.append(valmin)
        
    # Gestion n pair/impair
    if n % 2 == 1:
        mediane = tab_sort[int ((n - 1) / 2)]
    else:
        index1 = int(n/2)
        index2 = int(n/2 - 1)
        mediane = 0.5 * (tab_sort[index1] + tab_sort[index2])

    return mediane
    



# ---------------------------------------------------------------------------------
# Elastic conflation of segment geometries on a network
# ---------------------------------------------------------------------------------
# Inputs: - geom      : a collection of geometries (TrackCollection)
#         - network   : network containing reference nodes
#         - threshold : distance btw ending points above which conflation aborted
#		  - h         : covariance distance of elastic correction
# Output: a collection of geometries (TrackCollection) preserving the shape of the 
# input geometries while enforcing constraints on ending points defined by network
# Each object in geom must have a tid matching with edge ids of the network
# ---------------------------------------------------------------------------------
# Conflation is performed with 'colocation least squares' method and gaussian 
# covariogram of standard deviation h
# ---------------------------------------------------------------------------------
def conflateOnNetwork(geom, network, threshold=1e300, h=30, verbose=True):
	
	from tracklib.core import TrackCollection
	from tracklib.algo.interpolation import conflate
	from tracklib.algo.comparison import compare, MODE_COMPARISON_POINTWISE
	
	out = TrackCollection()
	if (verbose):
		print("-----------------------------------------------------------------------------------------")
		print("CORRECTION ELASTIQUE DE LA GEOMETRIE DU RESEAU")
		print("-----------------------------------------------------------------------------------------")
	max_total = 0
	rmse_total = 0
	matched = 0
	
	for segment in geom:
		edge = network.getEdge(segment.tid)
		p1 = edge.source.coord
		p2 = edge.target.coord
		
		h11 = p1.distance2DTo(segment[ 0].position); h12 = p2.distance2DTo(segment[-1].position); h1 = (h11**2+h12**2)**0.5/1.414
		h21 = p1.distance2DTo(segment[-1].position); h22 = p2.distance2DTo(segment[ 0].position); h2 = (h21**2+h22**2)**0.5/1.141
		HMIN = min(h1, h2)
	
		if (h2 < h1):
			ptemp = p1; p1 = p2; p2 = ptemp
		
		
		if (HMIN < threshold):
		
			conflated = conflate(segment, [p1, p2], [0, -1], h)
				
			MED = compare(segment, conflated, mode=MODE_COMPARISON_POINTWISE, p=1)
			MSE = compare(segment, conflated, mode=MODE_COMPARISON_POINTWISE, p=2)
			MAX = compare(segment, conflated, mode=MODE_COMPARISON_POINTWISE, p=float('inf'))
			if (verbose):
				print("#{:6s}      MED: {:6.3f} m      RMSE: {:6.3f} m      MAX: {:6.3f} m      MATCH: {:6.3f} m".format(segment.tid, MED, MSE, MAX, HMIN))
			rmse_total += MSE**2
			max_total = max(max_total, MAX)
			matched += 1
			
		else:
			conflated = segment.copy()
			
		conflated.tid = segment.tid	
		out.addTrack(conflated)
	
	if (len(geom) > 2):
		rmse_total = (rmse_total/len(geom)-1)**0.5
		if (verbose):
			print("-----------------------------------------------------------------------------------------")
			print("Number of conflated segments :     ",   matched, "      ({:2.2f}%)".format(matched/len(geom)*100))
			print("Total distorsion RMSE        :  {:6.3f} m     (MAX: {:6.3f} m)".format(rmse_total, max_total))
	if (verbose):
		print("-----------------------------------------------------------------------------------------")
	
	return out




# -----------------------------------------------------------------------------
# Essais élasticité
# -----------------------------------------------------------------------------

eps = 1e-10

random.seed(123457)

class Segment:
	
	def __init__(self, fx, fy, ti, tf):
		self.fx = fx
		self.fy = fy
		self.ti = ti
		self.tf = tf
	
	def eval(self, T):
		out = []
		for t in T:
			out.append((self.fx(t), self.fy(t)))
		return out

	def discretize(self, dt, ti=None, tf=None):
		if ti == None:
			ti = self.ti
		if tf == None:
			tf = self.tf
		T = np.arange(ti, tf+dt, dt*(tf-ti)/abs(tf-ti))
		return self.eval(T)

	def plot(self, dt, ti=None, tf=None, sym='ko', lwd=1, markersize=1):
		if ti == None:
			ti = self.ti
		if tf == None:
			tf = self.tf
		pts = self.discretize(dt, ti, tf)
		X = [p[0] for p in pts]
		Y = [p[1] for p in pts]
		plt.plot(X, Y, sym, markersize, lwd)

class Border:
	
	def __init__(self, segments = []):
		self.segments = segments
		
	def addSegment(self, segment):
		self.segments.append(segment)
		
	def discretize(self, dt):
		out = []
		for s in self.segments:
			for p in s.discretize(dt)[:-1]:
				out.append(p)
		return out
		
	def plot(self, dt, sym='ko', lwd=1, markersize=1):
		pts = self.discretize(dt)
		X = [p[0] for p in pts]
		Y = [p[1] for p in pts]
		X.append(X[0])
		Y.append(Y[0])
		plt.plot(X, Y, sym, linewidth=lwd, markersize=markersize)


class Domain:
	
	def __init__(self, outer, inner=[]):
		self.outer = outer
		self.inner = inner
		
	def setOuter(self, outer):
		self.outer = outer
	
	def addInner(self, inner):
		self.inner.append(inner)
	
	def discretize(self, dt):
		outer_dis = self.outer.discretize(dt)
		inner_dis = [inner.discretize(dt) for inner in self.inner]
		return (outer_dis, inner_dis)

	def plot(self, dt, sym='ko', lwd=1, markersize=1):
		self.outer.plot(dt, sym, lwd, markersize)
		for border in self.inner:
			border.plot(dt, sym, lwd, markersize)

	def triangulate(self, h, rand=True):
		shell = self.outer.discretize(h)
		holes = [inner.discretize(h) for inner in self.inner]
		holes = [hole for hole in holes if (len(hole) > 3)]
		polygon = shapely.Polygon(shell=shell, holes=holes)
		xmin = np.min(polygon.exterior.xy[0])
		xmax = np.max(polygon.exterior.xy[0])
		ymin = np.min(polygon.exterior.xy[1])
		ymax = np.max(polygon.exterior.xy[1])
		for ix in np.arange(xmin+h, xmax, h):
			for jy in np.arange(ymin+h, ymax, h):
				x = ix + rand*(random.random()-0.5)*h/2.0
				y = jy + rand*(random.random()-0.5)*h/2.0
				triangle = shapely.Polygon([(x-eps, y), (x+eps, y), (x, y+eps)])
				if (triangle.within(polygon)):
					holes.append(((x-eps, y), (x+eps, y), (x, y+eps)))
		polygon = shapely.Polygon(shell=shell, holes=holes)
		return Triangulation(shapely.constrained_delaunay_triangles(polygon), h)
		

class Triangulation:
	
	def __init__(self, triangles, resolution):
		
		self.geom = triangles
		self.nodes = []
		self.faces = []
		self.edges = []
		self.resolution = resolution
		
		
		X = []; Y = []; count = 0
		for triangle in shapely.get_parts(self.geom):
			x,y = triangle.exterior.xy
			X.append(x[0]); Y.append(y[0]);
			X.append(x[1]); Y.append(y[1]);
			X.append(x[2]); Y.append(y[2]);
			self.faces.append((count, count+1, count+2)); count += 3

		index  = shapely.STRtree([shapely.Point(X[i], Y[i]) for i in range(len(X))]);
		assoc = [i for i in range(len(X))]

		for i in range(len(X)):
			assoc[i] = np.min(index.query(shapely.box(X[i]-3*eps, Y[i]-3*eps, X[i]+3*eps, Y[i]+3*eps)))	

		indices = sorted(list(set(assoc)))	
		rename_indices = {}
		for i in range(len(indices)):
			rename_indices[indices[i]] = i

		for i in range(len(indices)):
			self.nodes.append((X[indices[i]], Y[indices[i]]))
		
		edges_dict = {}
		faces = []
		for i in range(len(self.faces)):
			fold = self.faces[i] 
			fnew = (rename_indices[assoc[fold[0]]], rename_indices[assoc[fold[1]]], rename_indices[assoc[fold[2]]])
			self.faces[i] = fnew	
			if (fnew[0] != fnew[1]):
				if (fnew[1] != fnew[2]):
					if (fnew[2] != fnew[0]):
						faces.append(fnew)
						edges_dict[tuple(sorted([fnew[0], fnew[1]]))] = 1
						edges_dict[tuple(sorted([fnew[1], fnew[2]]))] = 1
						edges_dict[tuple(sorted([fnew[2], fnew[0]]))] = 1
		self.faces = faces
		self.edges = list(edges_dict.keys())
		


	def plot(self, sym='k-', lwd=0.2, markersize=2, edge_color=False):
		if (edge_color):
			umin = np.min(self.node_values)
			umax = np.max(self.node_values)
			for e in self.edges:
				t1 = (self.node_values[e[0]] - umin)/(umax-umin)
				t2 = (self.node_values[e[1]] - umin)/(umax-umin)
				t  = (t1+t2)/2
				plt.plot([self.nodes[e[0]][0], self.nodes[e[1]][0]], [self.nodes[e[0]][1], self.nodes[e[1]][1]], sym[-1], linewidth=lwd, markersize=markersize, color=[1-t, t, 0])
		else:
			for e in self.edges:
				plt.plot([self.nodes[e[0]][0], self.nodes[e[1]][0]], [self.nodes[e[0]][1], self.nodes[e[1]][1]], sym, linewidth=lwd, markersize=markersize)	
			
			
		
	def summary(self):
		txt  = "------------------------------------------------------\r\n"
		txt += "DOMAIN MESH TRIANGULATION                             \r\n"
		txt += "------------------------------------------------------\r\n"
		txt += "Number of nodes: " + str(len(self.nodes)) +          "\r\n"
		txt += "Number of edges: " + str(len(self.edges)) +          "\r\n"
		txt += "Number of faces: " + str(len(self.faces)) +          "\r\n"
		txt += "------------------------------------------------------\r\n"
		txt += "Epsilon      : " + str(eps)               +          "\r\n"
		txt += "Resolution   : " + str(self.resolution)   +          "\r\n"
		txt += "------------------------------------------------------\r\n"
		print(txt)


class Treillis:
	
	def __init__(self, triangulation):
		
		# ---------------------------------------------------------
		# Partial Differential Equation problem input data
		# ---------------------------------------------------------
		self.triangulation = triangulation
		self.E = []								                 # Young modules of beams (in Pa or N/mm2)
		self.S = []								                 # Beam sections (in m2)		
		self.L = []												 # Beam length (in m)
		self.DIRICHLET = {}                                      # Dictionnary of Dirichlet boundary conditions (imposed displacements in m)
		self.NEUMANN   = {}                                      # Dictionnary of Neumann boundary conditions (imposed stress in N)
		
		# ---------------------------------------------------------
		# Solution
		# ---------------------------------------------------------
		self.disp_u   = [0]*self.getNumberOfNodes()         # Displacement solution in x direction (in m) 
		self.disp_v   = [0]*self.getNumberOfNodes()         # Displacement solution in v direction (in m) 
		self.stress   = [0]*self.getNumberOfEdges()         # Stress solution in beams (in Pa)
		self.strain   = [0]*self.getNumberOfEdges()         # Strain solution in beams (w/o unit)
		self.REACTION = {}							        # Solution reaction on imposed nodes (in N)
				
		
	def getNumberOfEdges(self):
		return len(self.triangulation.edges)
		
	def getNumberOfNodes(self):
		return len(self.triangulation.nodes)
		
	def getEdge(self, i):
		return self.triangulation.edges[i]
		
	def getNode(self, i):
		return self.triangulation.nodes[i]
		
	def setYoungModules(self, E):
		self.E = E
		
	def setBeamSections(self, S):
		self.S = S

	def setDirichletConditionOnNode(self, i, dx=None, dy=None):
		self.DIRICHLET[i] = (dx, dy)
		
	def setNeumannConditionOnNode(self, i, fx=None, fy=None):
		self.NEUMANN[i] = (fx, fy)

	def makeRigidityMatrix(self):
		N = self.getNumberOfNodes()
		R = np.zeros((2*N, 2*N))
		self.L = [0]*self.getNumberOfEdges()
		for i in range(self.getNumberOfEdges()):
			i1 = self.getEdge(i)[0] ; i2 = self.getEdge(i)[1]
			x1 = self.getNode(i1)[0]; x2 = self.getNode(i2)[0]
			y1 = self.getNode(i1)[1]; y2 = self.getNode(i2)[1]
			self.L[i] = ((x2-x1)**2+(y2-y1)**2)**0.5
			phi = math.atan2(y2-y1, x2-x1)
			c = math.cos(phi);s = math.sin(phi)
			c2 = c*c; s2 = s*s; cs = c*s
			k = self.E[i] * self.S[i] / self.L[i]

			R[2*i1+0][2*i1+0] +=  c2*k;  R[2*i1+0][2*i1+1] +=  cs*k;  R[2*i1+0][2*i2+0] += -c2*k;  R[2*i1+0][2*i2+1] += -cs*k;
			R[2*i1+1][2*i1+0] +=  cs*k;  R[2*i1+1][2*i1+1] +=  s2*k;  R[2*i1+1][2*i2+0] += -cs*k;  R[2*i1+1][2*i2+1] += -s2*k;
			R[2*i2+0][2*i1+0] += -c2*k;  R[2*i2+0][2*i1+1] += -cs*k;  R[2*i2+0][2*i2+0] +=  c2*k;  R[2*i2+0][2*i2+1] +=  cs*k;
			R[2*i2+1][2*i1+0] += -cs*k;  R[2*i2+1][2*i1+1] += -s2*k;  R[2*i2+1][2*i2+0] +=  cs*k;  R[2*i2+1][2*i2+1] +=  s2*k;

		R = (np.abs(R)>1e-10)*R

		return R
		
	def makeRightHandVector(self):
		N = self.getNumberOfNodes()
		F = np.zeros((2*N, 1))
		for i in self.NEUMANN:
			F[2*i  , 0] = self.NEUMANN[i][0]
			F[2*i+1, 0] = self.NEUMANN[i][1]
		return F
		
		
	def solve(self, R, F):
		
		K = R.copy()
		G = F.copy()
		
		# -----------------------------------------------------------
		# Méthode du terme diagonal unité
		# -----------------------------------------------------------
		for i in self.DIRICHLET:
			G[:,0] = G[:,0] + K[2*i  ,:]*self.DIRICHLET[i][0]
			G[:,0] = G[:,0] + K[2*i+1,:]*self.DIRICHLET[i][1]
		for i in self.DIRICHLET:
			K[2*i  , :] = 0; K[:,2*i  ] = 0; K[2*i  , 2*i  ] = 1
			K[2*i+1, :] = 0; K[:,2*i+1] = 0; K[2*i+1, 2*i+1] = 1
			G[2*i  , 0] = self.DIRICHLET[i][0]
			G[2*i+1, 0] = self.DIRICHLET[i][1]
		# -----------------------------------------------------------
			
		U = np.linalg.solve(K, G)
		FF = R @ U
		for i in self.DIRICHLET:
			self.REACTION[i] = (FF[2*i][0], FF[2*i+1][0])

		self.disp_u = U[0::2,0]
		self.disp_v = U[1::2,0]
		
		for i in range(self.getNumberOfEdges()):
			n1 = self.getEdge(i)[0]; u1 = self.disp_u[n1]; v1 = self.disp_v[n1]; x1 = self.getNode(n1)[0]; y1 = self.getNode(n1)[1]
			n2 = self.getEdge(i)[1]; u2 = self.disp_u[n2]; v2 = self.disp_v[n2]; x2 = self.getNode(n2)[0]; y2 = self.getNode(n2)[1]
			LL = (((x1+u1) - (x2+u2))**2 + ((y1+v1) - (y2+v2))**2)**0.5
			dL = LL-self.L[i]
			self.strain[i] = dL/self.L[i]
			self.stress[i] = self.E[i]*self.strain[i]
			
	def print_solution(self, Rlim=1e300):
		ok = True
		print("                      SOLUTION                        ")
		print("======================================================")
		print("Nodes displacements:")
		print("======================================================")
		for i in range(self.getNumberOfNodes()):
			u = self.disp_u[i]
			v = self.disp_v[i]
			if ((u != 0) or (v != 0)):
				print("Node #{:d}  u = {:5.3f} mm   v = {:5.3f} mm".format(i, self.disp_u[i]*1e3, self.disp_v[i]*1e3))
		print("------------------------------------------------------\r\n")
		
		print("======================================================")
		print("Beam strain:")
		print("======================================================")
		for i in range(self.getNumberOfEdges()):
			e = self.getEdge(i)
			sym = '[+]'
			if (self.strain[i] < 0):
				sym = '[-]'
			if (self.strain[i] != 0):
				print("Beam #{:d} [from nodes {:d} to {:d}]  {:7.1f} ppm    ".format(i, e[0], e[1], abs(self.strain[i])*1e6) + sym)
		print("------------------------------------------------------\r\n")
		
		print("======================================================")
		print("Beam stress:")
		print("======================================================")
		for i in range(self.getNumberOfEdges()):
			e = self.getEdge(i)
			sym     = '[+]'
			warning = ''
			if (self.stress[i] < 0):
				sym = '[-]'
			if (abs(self.stress[i]) > Rlim):
				warning = '[!]'
				ok = False
			if (self.stress[i] != 0):
				print("Beam #{:d} [from nodes {:d} to {:d}]  {:7.1f} MPa    ".format(i, e[0], e[1], abs(self.stress[i])*1e-6) + sym + "  " + warning)
		print("------------------------------------------------------\r\n")
		
		
		print("======================================================")
		print("Reactions on constrained nodes:")
		print("======================================================")
		for i in self.REACTION:
			Rx = self.REACTION[i][0]
			Ry = self.REACTION[i][1]
			print("Node #{:d}  Rx = {:12.3f} N   Ry = {:12.3f} N".format(i, Rx, Ry))
		print("------------------------------------------------------\r\n")
		
		print("======================================================")
		if (ok):
			print("All beam stress within structural limits")
		else:
			print("Warning: one or more beams are above structural limits")
		print("======================================================")
			
	def plot_solution(self, sym='ko', lwd=0.5, disp_factor=1e3, relax=True):
		stress_min = np.min(self.stress)
		stress_max = np.max(self.stress)
		for i in range(self.getNumberOfEdges()):
			if (self.stress[i] >= 0):
				t = self.stress[i]/stress_max
				color = [t, 1-t, 0.5*(1-t)]
			else:
				t = self.stress[i]/stress_min
				color = [1-t, t, 0.5*(1-t)]
			e = self.getEdge(i)
			n1 = self.getNode(e[0]); u1 = disp_factor*self.disp_u[e[0]]; u2 = disp_factor*self.disp_u[e[1]];
			n2 = self.getNode(e[1]); v1 = disp_factor*self.disp_v[e[0]]; v2 = disp_factor*self.disp_v[e[1]];
			if relax:
				plt.plot([n1[0], n2[0]], [n1[1], n2[1]], '-', linewidth=lwd, color=[t, 1-t, 0])
				plt.plot(n1[0], n1[1], sym)
				plt.plot(n2[0], n2[1], sym)
			plt.plot([n1[0] + u1, n2[0] + u2], [n1[1] + v1, n2[1] + v2], '-', linewidth=lwd, color=color)
			plt.plot(n1[0] + u1, n1[1] + v1, sym)
			plt.plot(n2[0] + u2, n2[1] + v2, sym)
		
	def plot(self, sym='k-', lwd=0.2, markersize=2, stress_factor=1e-5, strain_factor=1e5):
		smin = np.min(self.S)
		smax = np.max(self.S) + 0.001
		for i in range(self.getNumberOfEdges()):
			e = self.getEdge(i)
			lwd = 0.1 + (self.S[i]-smin)/(smax-smin)*10
			plt.plot([self.getNode(e[0])[0], self.getNode(e[1])[0]], [self.getNode(e[0])[1], self.getNode(e[1])[1]], sym, linewidth=lwd, markersize=markersize)	
		for i in self.DIRICHLET.keys():
			imposed = self.DIRICHLET[i]
			if (imposed[0] == 0 and imposed[1] == 0):
				plt.plot(self.getNode(i)[0], self.getNode(i)[1], 'ko')
			else:
				plt.plot(self.getNode(i)[0], self.getNode(i)[1], 'bo')
				plt.arrow(self.getNode(i)[0], self.getNode(i)[1], imposed[0]*strain_factor, imposed[1]*strain_factor, head_width=1e-2, color='b')
		for i in self.NEUMANN.keys():
			stress = self.NEUMANN[i]
			plt.plot(self.getNode(i)[0], self.getNode(i)[1], 'ro')
			plt.arrow(self.getNode(i)[0], self.getNode(i)[1], stress[0]*stress_factor, stress[1]*stress_factor, head_width=1e-2, color='r')


def Main_elasticity_1():
	
	Rh = [0.03, 0.05, 0.02, 0.03]
	Xh = [0.10, 0.50, 0.70, 0.85]
	Yh = [0.05, 0.10, 0.15, 0.06]

	s1 = Segment(lambda t : t  , lambda t : 0    , 0, 1)
	s2 = Segment(lambda t : 1  , lambda t : t    , 0, 0.2)
	s3 = Segment(lambda t : 1-t, lambda t : 0.2  , 0, 1)
	s4 = Segment(lambda t : 0  , lambda t : 0.2-t, 0, 0.2)

	outer = Border([s1, s2, s3, s4])

	inner = [Border([Segment(lambda t, i=i: Xh[i] + Rh[i]*math.cos(t/Rh[i]), lambda t, i=i : Yh[i] + Rh[i]*math.sin(t/Rh[i]), 0, 2*math.pi*Rh[i])]) for i in range(len(Rh))]
	domain = Domain(outer, inner)

	Th = domain.triangulate(0.02)

	plt.xlim(-0.05, 1.05)
	plt.ylim(-0.05, 0.25)	
	domain.plot(0.01, 'k-', lwd=1)
	Th.plot('k-')

	plt.show()



def Main_elasticity_2():
	
	np.set_printoptions(precision=3)

	s1 = Segment(lambda t : t  , lambda t : 0    , 0, 1)
	s2 = Segment(lambda t : 1  , lambda t : t    , 0, 0.2)
	s3 = Segment(lambda t : 1-t, lambda t : 0.2  , 0, 1)
	s4 = Segment(lambda t : 0  , lambda t : 0.2-t, 0, 0.2)

	domain = Domain(Border([s1, s2, s3, s4]))

	Th = domain.triangulate(0.02)
	
	Th.nodes = [(0,0), (0.5,3**0.5/2), (1,0)]
	Th.edges = [(0,1), (2,1)]
	Th.faces = []


	plt.xlim(-0.05, 1.05)
	plt.ylim(-0.05, 1.05)	

	Th.summary()

	model = Treillis(Th)
	model.setYoungModules([100*1e9]*model.getNumberOfEdges())
	model.setBeamSections([100*1e-6]*model.getNumberOfEdges())
	model.setDirichletConditionOnNode(0, 0, 0)
	model.setDirichletConditionOnNode(2, 0, 0)
	model.setNeumannConditionOnNode(1, 0, 10000) 

	R = model.makeRigidityMatrix()
	F = model.makeRightHandVector()

	model.plot('k-', stress_factor=5e-6)

	model.solve(R, F)

	model.plot_solution(relax=False, disp_factor=2e2)
	
	model.print_solution()

	plt.show()
