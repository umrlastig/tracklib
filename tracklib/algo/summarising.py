# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Marie-Dominique Van Damme
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



Operator to aggregate analytical features and create raster and render image

"""

from __future__ import annotations   
from typing import Union
#from tracklib.util.exceptions import *

import math

from tracklib.core import (listify, isnan, NAN,
                           TrackCollection,
                           Raster, RasterBand, NO_DATA_VALUE,
                           co_count)


def getMeasureName(af_algo:Union[int, str], aggregate=None):
    """
    Return the identifier of the measure defined by: af + aggregate operator
    """
    if af_algo != "uid":
        if isinstance(af_algo, str):
            cle = af_algo + "#" + aggregate.__name__
        else:
            cle = af_algo.__name__ + "#" + aggregate.__name__
    else:
        cle = "uid" + "#" + aggregate.__name__
            
    return cle


def createRaster(bbox, af_algos, aggregates,
                       resolution, margin:float=0.05):

    af_algos = listify(af_algos)
    aggregates = listify(aggregates)
    
    if len(af_algos) == 0:
        print("Error: af_algos is empty")
        return 0
    
    if len(af_algos) != len(aggregates):
        print("Error: af_names and aggregates must have the same number elements")
        return 0
    
    # Pour chaque algo-agg on crée une grille
    grilles = []
    for idx, af_algo in enumerate(af_algos):
        
        aggregate = aggregates[idx]
        cle = getMeasureName(af_algo, aggregate)

        grille = RasterBand(bbox, resolution, margin, name = cle)

        # ---------------------------------------------------------------------
        #  On ajoute les valeurs des af dans les cellules
        CUBE = []
        for i in range(grille.nrow):
            CUBE.append([])
            for j in range(grille.ncol):
                CUBE[i].append([])

        # ---------------------------------------------------------------------
        grilles.append(grille)
    
    raster = Raster(grilles)
    return (raster, CUBE)


def addTrackToRaster(raster, CUBE, trace):

    for i in range(raster.bandCount()):
        grille = raster.getRasterBand(i)
        names = grille.getName().split('#')
        af_algo = names[0]
        # aggregate = names[1]

        if not isinstance(af_algo, str):
            # On calcule l'AF si ce n'est pas fait
            trace.addAnalyticalFeature(af_algo)
        
        # On eparpille dans les cellules
        for i in range(trace.size()):
            obs = trace.getObs(i)
            
            (idx, idy) = grille.getCell(obs.position)
            # Cas des bordures
            if idx == grille.ncol:
                column = math.floor(idx) - 1
            else:
                column = math.floor(idx)
            
            if idy.is_integer() and int(idy) > -1:
                line = int(idy)
            elif idy.is_integer() and int(idy) == -1:
                line = int(idy) + 1
            else:
                line = math.floor(idy) + 1 # il faut arrondir par le dessus!
            
            if (
                    0 <= column
                    and column <= grille.ncol
                    and 0 <= line
                    and line <= grille.nrow
                ):
                if not isinstance(af_algo, str):
                    val = trace.getObsAnalyticalFeature(af_algo.__name__, i)
                elif af_algo != "uid":
                    val = trace.getObsAnalyticalFeature(af_algo, i)
                else:
                    val = trace.uid
                    # val = int(startpixel + (255 - startpixel) * (valmax - val) / valmax)
                    
                CUBE[line][column].append(val)

        return CUBE

def summ (raster, CUBE):

    for i in range(raster.bandCount()):
        grille = raster.getRasterBand(i)
        names = grille.getName().split('#')
        af_algo = names[0]
        aggregate = names[1]

        # On calcule les agregats
        # print (aggregates[0].__name__)
        for i in range(grille.nrow):
            for j in range(grille.ncol):
                #ii = grille.nrow - 1 - i
                tarray = CUBE[i][j]
                sumval = eval(aggregate + '(tarray)')
                
                # print (sumval)
                if isnan(sumval):
                    grille.grid[i][j] = NO_DATA_VALUE
                # # elif valmax != None and val > valmax:
                else:
                    grille.grid[i][j] = sumval



def summarize(collection: TrackCollection, af_algos, aggregates,
              resolution=None, margin:float=0.05, verbose:bool=True):
    """
    Example:
        af_algos = [algo.speed, algo.speed]
        cell_operators = [celloperator.co_avg, celloperator.co_max]
    
    """
    
    af_algos = listify(af_algos)
    aggregates = listify(aggregates)
    
    if len(af_algos) == 0:
        print("Error: af_algos is empty")
        return 0
    
    if len(af_algos) != len(aggregates):
        print("Error: af_names and aggregates must have the same number elements")
        return 0
    
    # Pour chaque algo-agg on crée une grille
    grilles = []
    for idx, af_algo in enumerate(af_algos):
        
        aggregate = aggregates[idx]
        
#        if isinstance(af_algo, str):
#            name = af_algo
#        else:
#            name = af_algo.__name__
#        cle = name + "#" + aggregate.__name__
        cle = getMeasureName(af_algo, aggregate)
        #print (cle)
            
        grille = RasterBand(collection.bbox(), resolution, margin, name = cle)
        #print (grille.name)
        
        # ---------------------------------------------------------------------
        #  On ajoute les valeurs des af dans les cellules
        CUBE = []
        for i in range(grille.nrow):
            CUBE.append([])
            for j in range(grille.ncol):
                CUBE[i].append([])
    
        #  On dispatch les valeurs de l'AF dans les cellules.
        #  Avant on vérifie si l'AF existe, sinon on la calcule.
        for trace in collection.getTracks():
            
            if not isinstance(af_algo, str):
                # On calcule l'AF si ce n'est pas fait
                trace.addAnalyticalFeature(af_algo)
            
            # On eparpille dans les cellules
            for i in range(trace.size()):
                obs = trace.getObs(i)
                
                (idx, idy) = grille.getCell(obs.position)
                # print (obs.position, idx, idy)
                
                # Cas des bordures
                if idx == grille.ncol:
                    column = math.floor(idx) - 1
                else:
                    column = math.floor(idx)
                
                if idy.is_integer() and int(idy) > -1:
                    line = int(idy)
                elif idy.is_integer() and int(idy) == -1:
                    line = int(idy) + 1
                else:
                    line = math.floor(idy) + 1 # il faut arrondir par le dessus!
                
                # print ('  ', obs.position, column, line)
                
                if (
                        0 <= column
                        and column <= grille.ncol
                        and 0 <= line
                        and line <= grille.nrow
                    ):
                    if not isinstance(af_algo, str):
                        val = trace.getObsAnalyticalFeature(af_algo.__name__, i)
                    elif af_algo != "uid":
                        val = trace.getObsAnalyticalFeature(af_algo, i)
                    else:
                        val = trace.uid
                        # val = int(startpixel + (255 - startpixel) * (valmax - val) / valmax)
                        
                    CUBE[line][column].append(val)
        
        # print (CUBE[0][0])

        # ---------------------------------------------------------------------
        # On calcule les agregats
        # print (aggregates[0].__name__)
        for i in range(grille.nrow):
            for j in range(grille.ncol):
                #ii = grille.nrow - 1 - i
                tarray = CUBE[i][j]
                sumval = aggregate(tarray)
                
                # print (sumval)
                if isnan(sumval):
                    grille.grid[i][j] = NO_DATA_VALUE
                # # elif valmax != None and val > valmax:
                else:
                    grille.grid[i][j] = sumval
        
        # ---------------------------------------------------------------------
        #   On ajoute la grille au tableau de grilles
        # print (grille.grid)
        grilles.append(grille)
        
    raster = Raster(grilles)
    return raster
    #return None






