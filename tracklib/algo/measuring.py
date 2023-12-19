# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Marie-Dominique Van Damme
Creation date: 19th december 2023

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

Class to propose measures on GPS tracks in particular intrinsics measures.

"""

import tracklib as tracklib
from . import (douglas_peucker, compare)


def compareWithDouglasPeuckerSimplification(track, threshold):
    '''
    retourne le nombre de points de la plus ligne la plus généralisée 
    avec Douglas Peucker et qui respecte une qualité données avec threshold.
    '''
    
    # On prend tous les seuils de 1m à longueur de la bbox ?
    sup = max(int(track.bbox().getDx()), int(track.bbox().getDy()))
    
    S = []
    for tolerance in range(1, sup):
        track1 = douglas_peucker(track, tolerance)
        err = compare(track, track1)
        if err < threshold:
            S.append(tolerance)
            print (err)
        else:
            # La fonction compare est croissante, donc on peut stopper quand
            # on a dépassé le seuil
            break

    index_max = max(range(len(S)), key=S.__getitem__)
    track1 = douglas_peucker(track, S[index_max])
    
    return track1.size()


def distanceDirectionMatrix():
    return 0
    
def buttenfieldTree():
    # TODO
    return 0

def ff():
    '''
    Ecart moyen rapporté à la moyenne des distances entre les points
    '''
    
def blackness():
    '''
    longueur * largeur du symbole / aire du rectangle englobant
    '''
    return 0


# La dimension fractale
# Mesure d'entropie
# Analyse des fréquences = ondelettes
# Changements de direction
# Curvilinéarité
# La longueur du rectangle englobant  



    




