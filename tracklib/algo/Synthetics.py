"""Class to manage GPS tracks synthetic generations"""

import random

from tracklib import (ENUCoords, ObsTime, Obs)
from tracklib.core.Track import Track
from tracklib.core.TrackCollection import TrackCollection
import tracklib.core.Kernel as Kernel

# =========================================================================
# Generate analytical track
# =========================================================================
def generate(
    x_t=0.3,
    y_t=None,
    z_t=None,
    date_ini=None,
    date_fin=None,
    dt=None,
    verbose=True,
    N=1,
):
    """TODO"""
    randomTrack = y_t is None
    if randomTrack:
        if N > 1:
            tracks = TrackCollection()
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
    if date_ini == None:
        date_ini = ObsTime.random()
    if date_fin == None:
        date_fin = date_ini.addHour(1)
    if dt == None:
        dt = (date_fin - date_ini) / 100
    track = Track()
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
        track = track.noise(50, Kernel.GaussianKernel(scope))
    return track


# =========================================================================
# Generate field of tracks from integral curves of vector field
# =========================================================================
def generateDataSet(vx, vy, N=100, pmin=(0, 0), pmax=(100, 100), Nbmax=1000):
    """TODO"""

    TRACKS = []
    for i in range(N):

        track = Track()
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
