"""Class to manage cinematic computations on GPS tracks"""

from tracklib.algo.Analytics import BIAF_SPEED, speed
from tracklib.algo.Analytics import BIAF_HEADING, heading
from tracklib.algo.Analytics import BIAF_DS, ds
from tracklib.algo.Analytics import BIAF_ABS_CURV
import tracklib.core.Operator as Operator


def estimate_speed(track):
    """
    Compute and return speed for each point
    Difference finie arriere-avant
    """
    if track.hasAnalyticalFeature(BIAF_SPEED):
        return track.getAnalyticalFeature(BIAF_SPEED)
    else:
        return track.addAnalyticalFeature(speed)


# --------------------------------------------------
# Difference finie centree lissee
# --------------------------------------------------
def smoothed_speed_calculation(track, width):
    """TODO

    :param track: TODO
    :param width: TODO
    :return: TODO
    """
    S = track.compute_abscurv()
    track.estimate_speed()

    if track.size() < width:
        print("warning:not enough point in track for this width")
        return None

    for i in range(width, len(S) - width):
        ds = S[i + width] - S[i - width]
        dt = track[i + width].timestamp - track[i - width].timestamp

        if dt != 0:
            track.setObsAnalyticalFeature("speed", i, ds / dt)

    for i in range(width):
        track.setObsAnalyticalFeature("speed", i, track["speed"][width])
    for i in range(len(S) - width, len(S)):
        track.setObsAnalyticalFeature("speed", i, track["speed"][len(S) - width])


def estimate_heading(track):
    """
    Compute and return speed for each point
    Difference finie arriere-avant
    """
    if track.hasAnalyticalFeature(BIAF_HEADING):
        return track.getAnalyticalFeature(BIAF_HEADING)
    else:
        return track.addAnalyticalFeature(heading)


# --------------------------------------------------
# Difference finie centree lissee
# --------------------------------------------------
def smoothed_speed_calculation(track, width):
    """TODO

    :param track: TODO
    :param width: TODO
    :return: TODO
    """

    S = track.compute_abscurv()
    track.estimate_speed()

    if track.size() < width:
        print("warning:not enough point in track for this width")
        return None

    for i in range(width, len(S) - width):
        ds = S[i + width] - S[i - width]
        dt = track[i + width].timestamp - track[i - width].timestamp

        if dt != 0:
            track.setObsAnalyticalFeature("speed", i, ds / dt)

    for i in range(width):
        track.setObsAnalyticalFeature("speed", i, track["speed"][width])
    for i in range(len(S) - width, len(S)):
        track.setObsAnalyticalFeature("speed", i, track["speed"][len(S) - width])


def computeAvgSpeed(track, id_ini=0, id_fin=None):
    """
    Computes averaged speed (m/s) between two points
    TODO : à adapter
    """
    if id_fin is None:
        id_fin = track.size() - 1
    d = track.getCurvAbsBetweenTwoPoints(id_ini, id_fin)
    t = track[id_fin].timestamp - track[id_ini].timestamp
    return d / t


def computeAvgAscSpeed(track, id_ini=0, id_fin=None):
    """
    Computes average ascending speed (m/s)
    TODO : à adapter
    """
    if id_fin is None:
        id_fin = track.size() - 1
    dp = track.computeAscDeniv(id_ini, id_fin)
    t = track[id_fin].timestamp - track[id_ini].timestamp
    return dp / t


def computeAbsCurv(track):
    """Compute and return curvilinear abscissa for each points"""

    if not track.hasAnalyticalFeature(BIAF_DS):
        track.addAnalyticalFeature(ds, BIAF_DS)
    if not track.hasAnalyticalFeature(BIAF_ABS_CURV):
        track.operate(Operator.Operator.INTEGRATOR, BIAF_DS, BIAF_ABS_CURV)
    track.removeAnalyticalFeature(BIAF_DS)

    return track.getAnalyticalFeature(BIAF_ABS_CURV)


def computeCurvAbsBetweenTwoPoints(track, id_ini=0, id_fin=None):
    """Computes and return the curvilinear abscissa between two points
    TODO : adapter avec le filtre"""
    if id_fin is None:
        id_fin = track.size() - 1
    s = 0
    for i in range(id_ini, id_fin):
        s = s + track[i].position.distance2DTo(track[i + 1].position)
    return s


def computeNetDeniv(track, id_ini=0, id_fin=None):
    """Computes net denivellation (in meters)"""
    if id_fin is None:
        id_fin = track.size() - 1
    return track[id_fin].position.getZ() - track[id_ini].position.getZ()


def computeAscDeniv(track, id_ini=0, id_fin=None):
    """Computes positive denivellation (in meters)"""
    if id_fin is None:
        id_fin = track.size() - 1

    dp = 0

    for i in range(id_ini, id_fin):
        Z1 = track[i].position.getZ()
        Z2 = track[i + 1].position.getZ()
        if Z2 > Z1:
            dp += Z2 - Z1

    return dp


def computeDescDeniv(track, id_ini=0, id_fin=None):
    """Computes negative denivellation (in meters)"""
    if id_fin is None:
        id_fin = track.size() - 1

    dn = 0

    for i in range(id_ini, id_fin):
        Z1 = track[i].position.getZ()
        Z2 = track[i + 1].position.getZ()
        if Z2 < Z1:
            dn += Z2 - Z1

    return dn

def computeRadialSignature(track, factor=1):
    track = track.copy(); track.loop()
    R = track.getEnclosedPolygon().signature()
    track.createAnalyticalFeature("s", R[0])
    track.createAnalyticalFeature("r", R[1])
    return track


def isInflection(track, i):
    '''
    AF algorithm to compute if the observation is an inflection point.

    Parameters
    ----------
    track : Track
    i : integer
        the th point.

    Returns
    -------
    int
        ième point de la trace.

    '''
    
    if i == 0 or i == 1:
        return 0
    if i == track.size() -1 or i == track.size() - 2:
        return 0
    
    x1 = track.getObs(i-1).position.getX()
    y1 = track.getObs(i-1).position.getY()
    x2 = track.getObs(i).position.getX()
    y2 = track.getObs(i).position.getY()
    x3 = track.getObs(i+1).position.getX()
    y3 = track.getObs(i+1).position.getY()
    x4 = track.getObs(i+2).position.getX()
    y4 = track.getObs(i+2).position.getY()
  
    d1 = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
    d2 = (x3 - x2) * (y4 - y2) - (y3 - y2) * (x4 - x2)
    
    if (d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0):
        return 1
    
    return 0


def sommet(track, i):
    
    import tracklib.algo.Analytics as Algo
    seuil = 150
    
    # on cherche imin
    imin = 1
    j = i-1
    while j > 0:
        if track.getObsAnalyticalFeature('pointinflexion', j) == 1:
            imin = j
            break
        j -= 1
    # on cherche imax
    imax = track.size()-2
    j = i+1
    while j < track.size()-1:
        if track.getObsAnalyticalFeature('pointinflexion', j) == 1:
            imax = j
            break
        j += 1
    
    # on cherche la plus petite courbure dans ]imin, imax[
    K = 400
    iK = -1
    for j in range(imin, imax):
        kj = Algo.anglegeom(track, j)
        #print (kj)
        if kj < K:
            K = kj
            iK = j
            
    if iK == i:
        if K < seuil:
            return 1

    return 0