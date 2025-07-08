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
import math

from tracklib.core import (AFMap, TrackCollection, listify,
                           Raster, BBOX_ALIGN_LL)



def summarize(collection, af_algos, aggregates,
              resolution=None, margin:float=0.05, align=BBOX_ALIGN_LL, verbose:bool=True):
    """
    Example:
        af_algos = [algo.speed, algo.speed]
        cell_operators = [celloperator.co_avg, celloperator.co_max]
    
    """

    af_algos = listify(af_algos)
    aggregates = listify(aggregates)

    if len(af_algos) == 0:
        raise WrongArgumentError("First parameter (af_algos) is empty.")

    if len(af_algos) != len(aggregates):
        print("Error: af_names and aggregates must have the same number elements")
        return 0

    raster = Raster(bbox=collection.bbox(), resolution=resolution, margin=margin, align=align)

    # Pour chaque algo-agg on crée une grille vide
    for idx, af_algo in enumerate(af_algos):
        aggregate = aggregates[idx]
        cle = AFMap.getMeasureName(af_algo, aggregate)
        raster.addAFMap(cle)

    raster.addCollectionToRaster(collection)
    print ('--- fin du add ---')
    # compute aggregate
    raster.computeAggregates()
    print ('--- fin du aggregate ---')

    return raster







