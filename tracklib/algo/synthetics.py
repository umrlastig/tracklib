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



Class to manage GPS tracks synthetic generations

"""

import random

import tracklib as tracklib
from tracklib.core import (ENUCoords, 
                           ObsTime, 
                           Obs, 
                           GaussianKernel)


def generate (x_t=0.3, y_t=None, z_t=None, date_ini=None, date_fin=None, dt=None, 
              verbose=True, N=1):
    """
    Generate analytical track
    """
    randomTrack = y_t is None
    
    if randomTrack:
        if N > 1:
            tracks = tracklib.TrackCollection()
            for i in range(N):
                tracks.addTrack(generate(x_t, N=1, verbose=verbose))
            return tracks
    
    if randomTrack:
        scope = 100 * x_t
        x1 = random.random() * 100
        y1 = random.random() * 100
        x2 = random.random() * 100
        y2 = random.random() * 100
        x_t = lambda t: x1 * (1 - t) + x2 * t
        y_t = lambda t: y1 * (1 - t) + y2 * t
    
    if date_ini is None:
        date_ini = ObsTime.random()
    if date_fin is None:
        date_fin = date_ini.addHour(1)
    if dt is None:
        dt = (date_fin - date_ini) / 100
    
    track = tracklib.Track()
    tps = date_ini.copy()
    N = (date_fin - date_ini) / dt
    if verbose:
        print("Generating track from", date_ini, "to", date_fin)
    for i in range((int)(N)):
        t = i / (N - 1.0)
        tps = tps.addSec(dt)
        if z_t == None:
            obs = Obs(ENUCoords(x_t(t), y_t(t)), tps)
        else:
            obs = Obs(ENUCoords(x_t(t), y_t(t), z_t(t)), tps)
        track.addObs(obs)
    if randomTrack:
        track = track.noise(50, GaussianKernel(scope))
    
    return track


def generateDataSet(vx, vy, N=100, pmin=(0, 0), pmax=(100, 100), Nbmax=1000):
    """
    Generate field of tracks from integral curves of vector field.
    """

    TRACKS = []
    for i in range(N):

        track = tracklib.Track()
        xini = random.random() * (pmax[0] - pmin[0]) + pmin[0]
        yini = random.random() * (pmax[1] - pmin[1]) + pmin[1]
        date_ini = ObsTime.random()

        xi = xini
        yi = yini
        date = date_ini
        track.addObs(Obs(ENUCoords(xi, yi), date))
        
        while 1:
            dx = vx(xi, yi)
            dy = vy(xi, yi)
            xi += dx
            yi += dy
            
            if (xi < pmin[0]) or (xi > pmax[0]):
                break
            if (yi < pmin[1]) or (yi > pmax[1]):
                break
            
            date = date.copy()
            date = date.addSec(1)
            track.addObs(Obs(ENUCoords(xi, yi), date))
            
            if track.size() > Nbmax / 2:
                break

        TRACKS.append(track)

    return TRACKS
