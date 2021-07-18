#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Algorithme de calcul des Analytical Features.
Plus quelques fonctions utilitaires
"""

import math
import numpy as np

from tracklib.core.Coords import GeoCoords
from tracklib.core.Coords import ENUCoords
from tracklib.core.Coords import ECEFCoords

import matplotlib.colors as mcolors

from heapq import heapify, heappush, heappop



# =============================================================================
#   Gestion des valeurs non renseignées et non calculées  
# =============================================================================

NAN = float('nan')

def isnan(number):
    return number != number

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# Make to list if needed
def listify(input):
    if not isinstance(input, list):
        input = [input]   
    return input

# Remove list if needed
def unlistify(input):
    if len(input) == 1:
        input = input[0]   
    return input

# LIKE comparisons
def compLike(s1, s2):
    tokens = s2.split('%')
    if len(tokens) == 1:
        return s1 in s2  # 'in' or 'equal' yet to be decided 
    occ = []
    s = s1
    d = len(s)
    for tok in tokens:
        id = s.find(tok)
        if id < 0:
            return False
        occ.append(id)
        s = s[id+len(tok):len(s)]
    return True    


# =============================================================================
''' Pour calculer l'aire des triangles dans Visvalingam '''
def aire_visval(track, i):
    x0 = track.getObs(i-1).position.getX()
    y0 = track.getObs(i-1).position.getY()
    x1 = track.getObs(i).position.getX()
    y1 = track.getObs(i).position.getY()
    x2 = track.getObs(i+1).position.getX()
    y2 = track.getObs(i+1).position.getY()
    return triangle_area(x0,y0,x1,y1,x2,y2)

# --------------------------------------------------------------------------
# Function to form coords object from (x,y,z) data
# --------------------------------------------------------------------------
# Input : 
#   - x       ::     1st coordinate (X, lon or E)
#   - y       ::     2nd coordinate (Y, lat or N)
#    - z       ::     3rd coordinate (Z, hgt or U)
#   - srid    ::     Id of coord system (ECEF, GEO or ENU)
# --------------------------------------------------------------------------
# Output : Coords object in the proper srid
# --------------------------------------------------------------------------
def makeCoords(x, y, z, srid):
    if (srid.upper() in ["ENUCOORDS", "ENU"]):
        return ENUCoords(x, y, z)
    if (srid.upper() in ["GEOCOORDS", "GEO"]):
        return GeoCoords(x, y, z)
    if (srid.upper() in ["ECEFCOORDS", "ECEF"]):
        return ECEFCoords(x, y, z)

# --------------------------------------------------------------------------
# Function to compute area of triangle with cross product
# --------------------------------------------------------------------------
# Input : 
#   - x0, y0         ::     point 1 coordinates
#   - x1, y1         ::     point 2 coordinates
#    - x2, y2         ::     point 3 coordinates
# --------------------------------------------------------------------------
# Output : area of P1P2P3 in coordinate units
# --------------------------------------------------------------------------
def triangle_area(x0,y0,x1,y1,x2,y2):
    return 0.5*abs((x1-x0)*(y2-y1)-(x2-x1)*(y1-y0))
    
    
# --------------------------------------------------------------------------
# Function to compute distance between a point and a segment
# --------------------------------------------------------------------------
# Input : 
#   - x0, y0         ::     point coordinates
#   - x1, y1         ::     segment first point
#    - x2, y2         ::     segment second point
# --------------------------------------------------------------------------
# Output : distance between point and projection coordinates
# --------------------------------------------------------------------------
def distance_to_segment(x0, y0, x1, y1, x2, y2):

    # Segment length
    l = math.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))

    # Normalized scalar product
    psn = ((x0-x1)*(x2-x1) + (y0-y1)*(y2-y1))/l
    
    X = max(x1, x2)
    Y = max(y1, y2)
    
    x = min(x1, x2)
    y = min(y1, y2)
    
    xproj = x1 + psn/l*(x2-x1)
    yproj =    y1 + psn/l*(y2-y1)
    
    xproj = min(max(xproj, x), X)
    yproj = min(max(yproj, y), Y)
    
    # Compute distance
    d = math.sqrt((x0-xproj)*(x0-xproj)+(y0-yproj)*(y0-yproj))
    
    return d     
    
# --------------------------------------------------------------------------
# Function to form distance matrix
# --------------------------------------------------------------------------
# Input : 
#   - T1     :: a list of points
#   - T2     :: a list of points
# --------------------------------------------------------------------------
# Output : numpy distance matrix between T1 and T2
# --------------------------------------------------------------------------    
def makeDistanceMatrix(T1, T2):
    
    T1 = np.array(T1)
    T2 = np.array(T2)
    
    # Signal stationnarity
    base = min(np.concatenate((T1,T2)))
    T1 = T1 - base
    T2 = T2 - base
    T1 = T1.T
    T2 = T2.T

    return np.sqrt((T1**2).reshape(-1, 1) + (T2**2) - 2 * (T1.reshape(-1, 1)*T2.T))
    
# --------------------------------------------------------------------------
# Function to form covariance matrix from kernel
# --------------------------------------------------------------------------
# Input : 
#   - kernel :: a function describing statistical similarity between points
#   - T1     :: a list of points
#   - T2     :: a list of points
#   - factor :: unit factor of std dev (default 1.0)
# --------------------------------------------------------------------------
# Output : numpy covariance matrix between T1 and T2
# --------------------------------------------------------------------------    
def makeCovarianceMatrixFromKernel(kernel, T1, T2, factor=1.0):
    
    D = makeDistanceMatrix(T1,T2)
    kfunc = np.vectorize(kernel.getFunction())
    
    return factor**2*kfunc(D)

# --------------------------------------------------------------------------
# Function to convert RGBA color to hexadecimal
# --------------------------------------------------------------------------
# Input : 
#   - color :: a 3 or 4-element array R, G, B [,alpha]
# Each color and transparency channel is in [0,1]
# --------------------------------------------------------------------------
# Output : a string containing color in hexadecimal
# --------------------------------------------------------------------------
def rgbToHex(color):
    if len(color) == 3:
        color.append(1)
    R = hex((int)(color[0]*255))[2:]
    G = hex((int)(color[1]*255))[2:]
    B = hex((int)(color[2]*255))[2:]
    A = hex((int)(color[3]*255))[2:]
    if (len(R) < 2):
        R = "0"+R
    if (len(G) < 2):
        G = "0"+G
    if (len(B) < 2):
        B = "0"+B
    if (len(A) < 2):
        A = "0"+A
    return "0x"+A+B+G+R

# --------------------------------------------------------------------------
# Function to interpolate RGBA (or RGB) color between two values
# --------------------------------------------------------------------------
# Input : 
#   - v: a float value
#   - vmin: minimal value of v (color cmin)
#   - vmax: maximal value of v (color cmax)
#   - cmin : a 3 or 4-element array R, G, B [,alpha]
#   - cmax : a 3 or 4-element array R, G, B [,alpha]
# --------------------------------------------------------------------------
# Output : a 4-element array 
# --------------------------------------------------------------------------
def interpColors(v, vmin, vmax, cmin, cmax):
    # norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    O = []
    O.append(((vmax-v)*cmin[0] + (v-vmin)*cmax[0])/(vmax-vmin))
    O.append(((vmax-v)*cmin[1] + (v-vmin)*cmax[1])/(vmax-vmin))
    O.append(((vmax-v)*cmin[2] + (v-vmin)*cmax[2])/(vmax-vmin))
    if len(cmin) == 4:
        O.append( ((vmax-v)*cmin[3] + (v-vmin)*cmax[3]) / (vmax-vmin))
    return O


def getColorMap(cmin, cmax):
   
    # On définit la map color
    cdict = {'red': [], 'green': [], 'blue': []}
    cdict['red'].append([0.0, None, cmin[0]/255])
    cdict['red'].append([1.0, cmax[0]/255, None])
    cdict['green'].append([0.0, None, cmin[1]/255])
    cdict['green'].append([1.0, cmax[1]/255, None])
    cdict['blue'].append([0.0, None, cmin[2]/255])
    cdict['blue'].append([1.0, cmax[2]/255, None])
    
    cmap = mcolors.LinearSegmentedColormap('CustomMap', cdict)

    return cmap


def getOffsetColorMap(cmin, cmax, part):
   
    # On définit la map color
    cdict = {'red': [], 'green': [], 'blue': []}
    cdict['red'].append([0.0, None, cmin[0]/255])
    cdict['red'].append([part, cmin[0]/255, cmin[0]/255])
    cdict['red'].append([1.0, cmax[0]/255, None])
    
    cdict['green'].append([0.0, None, cmin[1]/255])
    cdict['green'].append([part, cmin[1]/255, cmin[1]/255])
    cdict['green'].append([1.0, cmax[1]/255, None])
    
    cdict['blue'].append([0.0, None, cmin[2]/255])
    cdict['blue'].append([part, cmin[2]/255, cmin[2]/255])
    cdict['blue'].append([1.0, cmax[2]/255, None])
    
    cmap = mcolors.LinearSegmentedColormap('CustomMap', cdict)

    return cmap

# ----------------------------------------
# Fonction equation cartesienne
# Entree : segment
# Sortie : liste de parametres (a,b,c)
# ----------------------------------------
def cartesienne(segment):
    
    parametres = list();
    
    x1 = segment[0]
    y1 = segment[1]
    x2 = segment[2]
    y2 = segment[3]
    
    u1 = x2-x1
    u2 = y2-y1
    
    b = -u1
    a = u2
    
    c = -(a*x1+b*y1)
    
    parametres.append(a)
    parametres.append(b)
    parametres.append(c)
    
    return parametres
    
# ----------------------------------------
# Fonction distance point-droite
# Entree : paramètres a,b,c d'une droite, 
# coordonnées x et y du point
# Sortie : distance du point à la droite
# ----------------------------------------
def dist_point_droite(param, x, y):
    
    a = param[0]
    b = param[1]
    c = param[2]

    distance = math.fabs(a*x+b*y+c)
    distance /= math.sqrt(a*a+b*b)
    
    return distance
    

# ----------------------------------------
# Fonction projection orthogonal sur une 
# droite, coordonnées x et y
# Entree : paramètres a,b,c d'une droite
# Sortie : coordonnée xproj et yproj du 
# point projeté
# ----------------------------------------
def projection_droite(param, x, y):
    
    a = param[0]
    b = param[1]
    c = param[2]
    
    xv = -b 
    yv = a
    
    norm = math.sqrt(xv*xv+yv*yv)
    
    xb = 0
    yb = -c/b
    
    BH = ((x-xb)*xv+(y-yb)*yv)/norm
    
    xproj = xb + BH*xv/norm
    yproj = yb + BH*yv/norm   
    
    return xproj, yproj
    
# ----------------------------------------
# Fonction complète de projection
# Entree : segment, coordonnées x et y du 
# point
# Sortie : distance du point au segment et 
# coordonnées du projeté
# ----------------------------------------
def proj_segment(segment, x, y):
    
    param = cartesienne(segment)    
    
    a = param[0]
    b = param[1]
    c = param[2]

    distance = math.fabs(a*x+b*y+c)
    distance /= math.sqrt(a*a+b*b)
    
    # Récupération des coordonnées du projeté
    xproj, yproj =  projection_droite(param, x, y)
    
    # Test d'inclusion dans le segment

    x1 = segment[0]
    y1 = segment[1]
    x2 = segment[2]
    y2 = segment[3]    
    
    boolx1 = (xproj >= x1) and (xproj <= x2)    
    boolx2 = (xproj <= x1) and (xproj >= x2)
    boolx = boolx1 or boolx2
    
    booly1 = (yproj >= y1)&(yproj <= y2)    
    booly2 = (yproj <= y1)&(yproj >= y2)
    booly = booly1 or booly2
    
    bool_include = (boolx and booly)
    
     # Si le projeté est dans le segment
    if (bool_include):

        a = param[0]
        b = param[1]
        c = param[2]
    
        xv = -b 
        yv = a
        
        norm = math.sqrt(xv*xv+yv*yv)
    
        xb = 0
        yb = -c/b
    
        BH = ((x-xb)*xv+(y-yb)*yv)/norm
    
        xproj = xb + BH*xv/norm
        yproj = yb + BH*yv/norm   
            
        
        return distance, xproj, yproj
    
    else:
        distance1 = math.sqrt((x-x1)*(x-x1)+(y-y1)*(y-y1))
        distance2 = math.sqrt((x-x2)*(x-x2)+(y-y2)*(y-y2))
        
        if (distance1 <= distance2):
            return distance1, x1, y1
        else:
            return distance2, x2, y2
            
# ----------------------------------------
# Fonction complète de projection entre un
# point et une polyligne
# Entree : polyligne, coordonnées x et y du 
# point
# Sortie : distance du point ) la polyligne
# et coordonnées du projeté
# ----------------------------------------
def proj_polyligne(Xp, Yp, x, y):     
    
    distmin = 1e300
    
    for i in range(len(Xp)-1):
    
        x1 = Xp[i]
        y1 = Yp[i]
        x2 = Xp[i+1]
        y2 = Yp[i+1]

        dist, xp, yp = proj_segment([x1, y1, x2, y2], x, y)
        
        if dist < distmin:
            distmin = dist
            xproj = xp
            yproj = yp
            iproj = i
            
    return distmin, xproj, yproj, iproj

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
        if key not in self:
            self[key] = val
            return val
        return self[key]

    def update(self, *args, **kwargs):
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
			
