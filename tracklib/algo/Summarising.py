"""Operator to aggregate analytical features and create raster and render image"""

import math

import tracklib.core.Utils as utils

from tracklib.core.Raster import Raster
from tracklib.core.Grid import Grid
from tracklib.core.Grid import NO_DATA_VALUE
from tracklib.core.TrackCollection import TrackCollection


def summarize(collection: TrackCollection, af_algos, aggregates, 
              resolution=None, margin: float = 0.05, verbose: bool = True,):
    """
    Example :
        af_algos = [algo.speed, algo.speed]
        cell_operators = [celloperator.co_avg, celloperator.co_max]
    
    """
    
    af_algos = utils.listify(af_algos)
    aggregates = utils.listify(aggregates)
    
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
        
        if isinstance(af_algo, str):
            name = af_algo
        else:
            name = af_algo.__name__
        cle = name + "#" + aggregate.__name__
            
        grille = Grid(collection, resolution, margin, name = cle)
        #print (grille.name)
        
        # ---------------------------------------------------------------------
        #  On ajoute les valeurs des af dans les cellules
        CUBE = []
        for i in range(grille.ncol):
            CUBE.append([])
            for j in range(grille.nrow):
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
                column = math.floor(idx)
                line = math.floor(idy)
                # print (column, line)
                
                if (
                        0 <= column
                        and column < grille.ncol
                        and 0 <= line
                        and line < grille.nrow
                    ):

                    if not isinstance(af_algo, str):
                        val = trace.getObsAnalyticalFeature(name, i)
                    elif af_algo != "uid":
                        val = trace.getObsAnalyticalFeature(af_algo, i)
                    else:
                        val = trace.uid
                        # val = int(startpixel + (255 - startpixel) * (valmax - val) / valmax)

                    CUBE[column][line].append(val)
                    
        # ---------------------------------------------------------------------
        # On calcule les agregats
        # print (aggregates[0].__name__)
        for i in range(grille.nrow):
            for j in range(grille.ncol):
                #ii = grille.nrow - 1 - i
                tarray = CUBE[j][i]
                    
                sumval = aggregate(tarray)
                if utils.isnan(sumval):
                    grille.grid[j][i] = NO_DATA_VALUE
                # # elif valmax != None and val > valmax:
                else:
                    grille.grid[j][i] = sumval
        
        
        # ---------------------------------------------------------------------
        #   On ajoute la grille au tableau de grilles
        grilles.append(grille)
        
        
    raster = Raster(grilles)
    return raster


def co_sum(tarray):
    """TODO"""
    tarray = utils.listify(tarray)
    somme = 0
    for i in range(len(tarray)):
        val = tarray[i]
        if utils.isnan(val):
            continue
        somme += val
    return somme


def co_min(tarray):
    """TODO"""
    tarray = utils.listify(tarray)
    if len(tarray) <= 0:
        return utils.NAN
    min = tarray[0]
    for i in range(1, len(tarray)):
        val = tarray[i]
        if utils.isnan(val):
            continue
        if val < min:
            min = val
    return min


def co_max(tarray):
    """TODO"""
    tarray = utils.listify(tarray)
    if len(tarray) <= 0:
        return utils.NAN
    max = tarray[0]
    for i in range(1, len(tarray)):
        val = tarray[i]
        if utils.isnan(val):
            continue
        if val > max:
            max = val
    return max


def co_count(tarray):
    """TODO"""
    tarray = utils.listify(tarray)
    count = 0
    for i in range(len(tarray)):
        val = tarray[i]
        if utils.isnan(val):
            continue
        count += 1
    return count


def co_avg(tarray):
    """TODO"""
    tarray = utils.listify(tarray)
    if len(tarray) <= 0:
        return utils.NAN
    mean = 0
    count = 0
    for i in range(len(tarray)):
        val = tarray[i]
        if utils.isnan(val):
            continue
        count += 1
        mean += val
    if count == 0:
        return utils.NAN
    return mean / count


def co_dominant(tarray):
    """TODO"""
    tarray = utils.listify(tarray)
    if len(tarray) <= 0:
        return utils.NAN

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
    tarray = utils.listify(tarray)
    if len(tarray) <= 0:
        return utils.NAN

    n = len(tarray)
    # on tri le tableau pour trouver le milieu
    tab_sort = []
    for i in range(n):
        valmin = tarray[0]
        # Recherche du min
        for val in tarray:
            if val <= valmin:
                valmin = val
        tarray.remove(valmin)
        tab_sort.append(valmin)

    # Gestion n pair/impair
    if n % 2 == 1:
        mediane = tab_sort[(n - 1) / 2]
    else:
        mediane = 0.5 * (tab_sort[n / 2] + tab_sort[n / 2 - 1])

    return mediane
