# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Yann Méneroux
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



Algorithm to create Analytical features: ds, speed, abs_curv.

"""

#from typing import Iterable, Literal, Union   

import math
import numpy as np

from tracklib.core import NAN
from tracklib.util import angleBetweenThreePoints


# Liste des AF algo intégrés à disposition
BIAF_DS = "ds"
BIAF_SPEED = "speed"
BIAF_HEADING = "heading"
BIAF_ABS_CURV = "abs_curv"
BUILT_IN_AF = [BIAF_DS, BIAF_SPEED, BIAF_ABS_CURV, BIAF_HEADING]


def ds(track, i):
    """TODO"""
    if i == 0:
        return 0
    return track.getObs(i).distance2DTo(track.getObs(i - 1))


def heading(track, i):
    """
    Heading is the direction track is pointed in

    Parameters
    ----------
    track : Track
        trace on which the computation of heading is done.
    i : int
        i-th observation

    Returns
    -------
    float
        heading of the i-th observation of the track.

    """
    
    if i == 0:
        return heading(track, 1)
    
    return track.getObs(i-1).position.azimuthTo(track.getObs(i).position)


def speed(track, i):
    """
    Méthode calculant le paramètre 'speed' pour chaque point de la trace
    """

    # On attribut au point d'indice [0] la vitesse du point d'indice [1]
    if i == 0:
        ds0 = track.getObs(1).position.distance2DTo(track.getObs(0).position)
        dt0 = track.getObs(1).timestamp - track.getObs(0).timestamp
        if dt0 == 0:
            return NAN
        else:
            return ds0 / dt0

    # On attribut au point d'indice [N-1] la vitesse du point d'indice [N-2]
    N = track.size()
    if i == N - 1:
        dsN = track.getObs(N - 1).position.distance2DTo(track.getObs(N - 2).position)
        dtN = track.getObs(N - 1).timestamp - track.getObs(N - 2).timestamp
        if dtN == 0:
            return NAN
        else:
            return dsN / dtN

    # Pour les autres points :
    ds = track.getObs(i + 1).position.distance2DTo(track.getObs(i - 1).position)
    dt = track.getObs(i + 1).timestamp - track.getObs(i - 1).timestamp

    # La vitesse est obtenue en divisant la distance entre deux points successifs
    # par le temps les séparant
    if dt == 0:
        return NAN
    else:
        return ds / dt


def acceleration(track, i):
    """
    Acceleration instantannée de la trace
    """

    if i == 0:
        return NAN

    N = track.size()
    if i == N - 1:
        d = speed(track, i) - speed(track, i - 1)
        dt = track.getObs(i).timestamp - track.getObs(i - 1).timestamp

        if dt == 0:
            return NAN
        return d / dt

    d = speed(track, i + 1) - speed(track, i - 1)
    dt = track.getObs(i + 1).timestamp - track.getObs(i - 1).timestamp

    if dt == 0:
        return NAN

    return d / dt


def slope(track, i):
    
    if i == 0:
        return NAN
    
    z2 = track.getObs(i).position.getZ()
    z1 = track.getObs(i-1).position.getZ()
    rise = z2 - z1
    run = track.getObs(i).distance2DTo(track.getObs(i-1))
    #print (rise, run)
    
    if run <= 0:
        return NAN
    
    # return rise/run * 100
    return math.atan(rise/run)*180/np.pi
    


# =============================================================================
#    Des AF algo sur les angles
# =============================================================================
def anglegeom(track, i) -> float:
    """
    Mesure l'angle  géométrique (non orienté) intérieur abc.
    :return: Angle abc (degrees)
    """
    if i == 0:
        return NAN

    N = track.size()
    if i == N - 1:
        return NAN
    
    return angleBetweenThreePoints(track.getObs(i-1), track.getObs(i), track.getObs(i+1))


def calculAngleOriente(track, i):
    """Mesure l'angle orienté dans le sens trigonométrique abc."""

    if i == 0:
        return NAN

    N = track.size()
    if i == N - 1:
        return NAN

    a = track.getObs(i - 1).position
    b = track.getObs(i).position
    c = track.getObs(i + 1).position

    angleRadian = math.atan2(c.getY() - b.getY(), c.getX() - b.getX())
    angleRadian -= math.atan2(a.getY() - b.getY(), a.getX() - b.getX())
    angleDegree = math.degrees(angleRadian)
    if angleDegree == -180:
        return 180
    elif angleDegree < -180:
        return 180 - (abs(angleDegree) - 180)
    elif angleDegree > 180:
        return -180 + (angleDegree - 180)
    else:
        return angleDegree


def orientation(track, i):
    """Calcul l'orientation d'un point de la trace"""
    """orientation_dictionnary = {
        1: [-(1 / 8) * math.pi, (1 / 8) * math.pi],
        2: [(1 / 8) * math.pi, (3 / 8) * math.pi],
        3: [(3 / 8) * math.pi, (5 / 8) * math.pi],
        4: [(5 / 8) * math.pi, (7 / 8) * math.pi],
        5: [(-7 / 8) * math.pi, (7 / 8) * math.pi],
        6: [-(7 / 8) * math.pi, -(5 / 8) * math.pi],
        7: [-(5 / 8) * math.pi, -(3 / 8) * math.pi],
        8: [-(3 / 8) * math.pi, -(1 / 8) * math.pi],
    }"""

    orientation_dictionnary = {
        1: [0, 22.5 + 0*45],
        2: [22.5 + 0*45, 22.5 + 1*45],
        3: [22.5 + 1*45, 22.5 + 2*45],
        4: [22.5 + 2*45, 22.5 + 3*45],
        5: [22.5 + 3*45, 22.5 + 4*45],
        6: [22.5 + 4*45, 22.5 + 5*45],
        7: [22.5 + 5*45, 22.5 + 6*45],
        8: [22.5 + 6*45, 22.5 + 7*45],
        9: [22.5 + 7*45, 360],
    }
    # 1:E, 2:NE, 3:N, 4:NW, 5:W, 6:SW, 7:S, 8:SE

    cap = NAN

    if i == 0:
        # On calcule pour le point1 et on prend cette valeur
        x0 = float(track.getObs(0).position.getX())
        y0 = float(track.getObs(0).position.getY())
        dx = float(track.getObs(1).position.getX()) - x0
        dy = float(track.getObs(1).position.getY()) - y0
    else:
        xim1 = float(track.getObs(i - 1).position.getX())
        yim1 = float(track.getObs(i - 1).position.getY())
        dx = float(track.getObs(i).position.getX()) - xim1
        dy = float(track.getObs(i).position.getY()) - yim1
        
    orientation = math.atan2(dy, dx)
    #print (orientation)
    angle = math.degrees(orientation)
    if angle < 0:
        angle += 360
    #print (angle)

    # On convertit la valeur calculée en orientation relative
    cap = NAN

    for direction in orientation_dictionnary:
        binf = orientation_dictionnary[direction][0]
        bsup = orientation_dictionnary[direction][1]
        if angle >= binf and angle < bsup:
            cap = direction

    if cap == 9:
        cap = 1

    #print (cap)
    return cap


# =============================================================================
#    Des AF algo sur le timestamp
# =============================================================================
def diffJourAnneeTrace(track, i):
    """For divide tracks by year day"""
    if i == 0:
        return 0
    return track.getObs(i).timestamp.day - track.getObs(i - 1).timestamp.day


