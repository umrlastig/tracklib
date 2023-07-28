"""
Class to manage cinematic computations on GPS tracks
"""


from . import (anglegeom,
               BIAF_SPEED, speed,
               BIAF_HEADING, heading,
               BIAF_DS, ds,
               BIAF_ABS_CURV)
from tracklib.core import Operator
from tracklib.util import angleBetweenThreePoints


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
    
    computeAbsCurv(track)
    S = track.getAbsCurv()
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


def computeAvgSpeed(track, id_ini=0, id_fin=None):
    """
    Computes averaged speed (m/s) between two points
    TODO : à adapter
    """
    if id_fin is None:
        id_fin = track.size() - 1
    # extract ?
    d = computeCurvAbsBetweenTwoPoints(track, id_ini, id_fin)
    t = track[id_fin].timestamp - track[id_ini].timestamp
    return d / t


def computeAvgAscSpeed(track, id_ini=0, id_fin=None):
    """
    Computes average ascending speed (m/s)
    TODO : à adapter
    """
    if id_fin is None:
        id_fin = track.size() - 1
    dp = computeAscDeniv(track, id_ini, id_fin)
    t = track[id_fin].timestamp - track[id_ini].timestamp
    return dp / t


def computeAbsCurv(track):
    """Compute and return curvilinear abscissa for each points"""

    if not track.hasAnalyticalFeature(BIAF_DS):
        track.addAnalyticalFeature(ds, BIAF_DS)
    if not track.hasAnalyticalFeature(BIAF_ABS_CURV):
        track.operate(Operator.INTEGRATOR, BIAF_DS, BIAF_ABS_CURV)
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


# =============================================================================
#  

def inflection(track):
    """
    Among the characteristic points, inflection points are those the curvature 
    changes sign. In tracklib, this characteristic is modeled as an AF algorithm to detect 
    if the observation obs(i) is an inflection point or not.
    
    Le principe de détection est fondé sur l'étude de la variation 
    des produits vectoriels le long de la ligne. Les points d'inflexion sont 
    détectés aux changements de signe de ces produits. Pour éviter les micros 
    inflexion, on considère aussi qu'on a au moins 2 produits consécutifs 
    de même signe de part et d’autre.

    Normalement, le point d'inflexion est le milieu de [oi, oi+1]. 
    TODO : Pour ne pas avoir à ajouter de points, on prend oi, à changer.
    
    
    Parameters
    -----------
    
    :param track: a track to compute inflection point
    :param i: the th point
    :type track: Track
    :type i: int
    :returns: 1 if obs(i) is a inflection point, 0 else.
    :rtype: int
    
    """
    
    track.createAnalyticalFeature('inflection', 0)
    
    for i in range(track.size()):
    
        if i == 0 or i == 1 or i == 2:
            continue
    
        if i == track.size()-1 or i == track.size()-2 or i == track.size()-3:
            continue
    
        x0 = track.getObs(i-2).position.getX()
        y0 = track.getObs(i-2).position.getY()
        x1 = track.getObs(i-1).position.getX()
        y1 = track.getObs(i-1).position.getY()
        x2 = track.getObs(i).position.getX()
        y2 = track.getObs(i).position.getY()
        
        x3 = track.getObs(i+1).position.getX()
        y3 = track.getObs(i+1).position.getY()
        x4 = track.getObs(i+2).position.getX()
        y4 = track.getObs(i+2).position.getY()
        x5 = track.getObs(i+3).position.getX()
        y5 = track.getObs(i+3).position.getY()
      
        d1 = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
        d2 = (x3 - x2) * (y4 - y2) - (y3 - y2) * (x4 - x2)
        
        # Signe différent => 1
        isPICandidat = 0
        
        if d1 > 0 and d2 == 0:
            isPICandidat = 1
        if d1 < 0 and d2 == 0:
            isPICandidat = 1
        if d2 > 0 and d1 == 0:
            isPICandidat = 1
        if d2 < 0 and d1 == 0:
            isPICandidat = 1
        
        if isPICandidat == 0:
            isPICandidat = (d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)
    
        # On regarde un coup de plus avant, il faut le même signe que d1
        if isPICandidat == 1:
            d11 = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
            
            if (d1 > 0 and d11 > 0) or (d1 < 0 and d11 < 0):
                d22 = (x4 - x3) * (y5 - y3) - (y4 - y3) * (x5 - x3)
                # print (i, d11, d22)
                if (d2 > 0 and d22 > 0) or (d2 < 0 and d22 < 0):
                    #print (i)
                    track.setObsAnalyticalFeature('inflection', i, 1)
    


def setVertexAF(track):
    '''
    Vertices are characteristic points of a track corresponding to 
    the maxima of curvature between two inflexion points.
    
    "sommet" dans la thèse de Plazannet
    
    This function is an AF algorithm to detect if the observation obs(i) 
    is a vertex point of the track or not.
    
    Parameters
    -----------
    
    :param track: a track to compute inflection point
    :param i: the th point
    :type track: Track
    :type i: int
    :returns: 1 if obs(i) is a vertex point, 0 else.
    :rtype: int
    '''

    track.createAnalyticalFeature('vertex', 0)
    
    if not track.hasAnalyticalFeature('inflection'):
        inflection(track)
    
    for i in range(track.size()):
        
        # on cherche imin, l'indice du point d'inflexion le plus proche 
        # en amont de la trace
        imin = 0
        j = i-1
        while j >= 0:
            if track.getObsAnalyticalFeature('inflection', j) == 1:
                imin = j
                break
            j -= 1
        
        # on cherche imax, l'indice du point d'inflexion le plus proche 
        # en aval de la trace
        imax = track.size() -1
        j = i+1
        while j <= track.size() - 1:
            if track.getObsAnalyticalFeature('inflection', j) == 1:
                imax = j
                break
            j += 1
        
        #print (i, imin, imax)
        #if imin == 0:
        #    continue
        #if imax == track.size() - 1:
        #    continue
        #print (i, imin, imax)
    
        # on cherche la plus petite courbure dans ]imin, imax[
        K = 400
        iK = -1
        for j in range(imin, imax+1):
            kj = anglegeom(track, j)
            if kj < K:
                K = kj
                iK = j
    
        #print ('   ', i, iK)
        track.setObsAnalyticalFeature('vertex', iK, 1)


from numpy import pi
def setBendAsAF(track, angle_min = pi/2):
    '''
    Attribution des points de la trace qui composent 
    le virage défini par le sommet et les points d'inflexion les plus proches 
    de chaque côté.
    
    Un bon virage est un virage dont l'angle avec le sommet et ses 
    points d'inflexion est inférieur à angle_min.
    
    AF = 'bend' and value is 1 if obs(i) is in a bend, 0 else.


    Parameters
    ----------
    T : Track
        La trace dont on veut extraire les points autour du sommet.
    angle_min : float
        angle min in radians.

    '''
    
    track.createAnalyticalFeature('bend', 0)
    if not track.hasAnalyticalFeature('inflection'):
        inflection(track)
    if not track.hasAnalyticalFeature('vertex'):
        setVertexAF(track)
    
    for i in range(track.size()):
        # On ne traite que les virages à partir des sommets
        afsommet = track.getObsAnalyticalFeature('vertex', i)
        if afsommet == 1:
            # on cherche le pt inflexion avant
            deb = 0
            for j in range(i, -1, -1):
                ptinflexion = track.getObsAnalyticalFeature('inflection', j)
                if ptinflexion == 1:
                    deb = j
                    break
            # On cherche le pt inflexion apres
            fin = track.size()-1
            for j in range(i, track.size()):
                ptinflexion = track.getObsAnalyticalFeature('inflection', j)
                if ptinflexion == 1:
                    fin = j
                    break
            #print (i, deb, fin)
                
            angle_virage = angleBetweenThreePoints(track.getObs(deb), track.getObs(i), 
                                                   track.getObs(fin))
            # print (angle_virage*180/pi, angle_min*180/pi)
            if angle_virage < angle_min:
                # print (deb, fin, angle_virage, garde)
                # Le virage est un bon virage, on prend tous les points
                for j in range(deb, fin):
                    track.setObsAnalyticalFeature('bend', j, 1)
                if fin < track.size():
                    track.setObsAnalyticalFeature('bend', fin, 1)
            


def setSwitchbacksAsAF(track, nb_virage_min = 3, dist_max = 150):
    '''
    Fusion des virages (consécutifs ou pas) si leur nombre est supérieur à 
    nb_virage_min et si la distance maximale entre deux sommets est inférieure 
    à dist_max.
    Attention: c'est une structure de fonction particulière qui créée un AF, 
    elle ne s'appelle pas avec la méthode addAnalyticalFeature.
    
    TODO: a revoir
    
    Parameters
    -----------
    track : Track
    nb_virage_min : nombre
    dist_max : distance

    '''
    #    
    track.createAnalyticalFeature('switchbacks', 0)
    
    if not track.hasAnalyticalFeature('inflection'):
        inflection(track)
    if not track.hasAnalyticalFeature('vertex'):
        setVertexAF(track)
    if not track.hasAnalyticalFeature('bend'):
        setBendAsAF(track)
        
    SERIE = False
    deb = 0
    fin = 0
    
    # Nombre de virage de la série
    nbvirage = 0 
    
    # Calcul de la distance entre 2 sommets
    dist = 0
    
    for i in range(track.size()):
        afsommet = track["vertex", i]
        afvirage = track["bend", i]
        
        if afvirage == 1 and not SERIE:
            #print ("on démarre à : ", i)
            SERIE = True
            deb = i
            dist = 0
        elif SERIE and afvirage == 1:
            dist += track.getObs(i).distanceTo(track.getObs(i-1))
            #print (dist)
        elif SERIE and afvirage != 1:
            # Est-ce qu'on a fini la série ?
            fini = True
            # Sauf si le point suivant 
            for j in range(i+1, track.size()):
                afprochainvirage = track.getObsAnalyticalFeature('bend', j)
                if afprochainvirage == 1:
                    dhorsvirage = track.getObs(j).distanceTo(track.getObs(i))
                    if dhorsvirage < dist_max:
                        fini = False
                    break
                
            if fini:
                # print ('fin, ', deb, fin, nbvirage)
                # On a fini la série, on passe les AF de la série à 1
                fin = i - 1
                if nbvirage >= nb_virage_min:
                    for k in range(deb, fin):
                        track.setObsAnalyticalFeature('switchbacks', k, 1)
                SERIE = False
                deb = 0
                fin = 0
                nbvirage = 0
                dist = 0

        if afsommet == 1 and afvirage == 1:
            if nbvirage == 0:
                dist = 0
                nbvirage = 1
            elif dist > dist_max:
                # On stoppe la série
                SERIE = False
                deb = 0
                fin = 0
                nbvirage = 0
                dist = 0
                # print ('stop', i)
            else:
                nbvirage += 1
                dist = 0

# 




