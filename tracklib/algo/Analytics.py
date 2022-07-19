"""ds, speed, abs_curv
Algorithms to detect stop
"""

import math
import tracklib.core.Utils as utils


# Liste des AF algo intégrés à disposition
BIAF_DS = "ds"
BIAF_SPEED = "speed"
BIAF_HEADING = "heading"
BIAF_ABS_CURV = "abs_curv"
BUILT_IN_AF = [BIAF_DS, BIAF_SPEED, BIAF_ABS_CURV, BIAF_HEADING]

# __all__ = ["BIAF_DS", "BIAF_SPEED", "BIAF_HEADING", "BIAF_ABS_CURV", "BUILT_IN_AF"]


def addListToAF(track, af_name, array):
    """TODO"""
    if af_name == None:
        return
    for i in range(track.size()):
        track.setObsAnalyticalFeature(af_name, i, array[i])


def ds(track, i):
    """TODO"""
    if i == 0:
        return 0
    return track.getObs(i).distance2DTo(track.getObs(i - 1))


def abs_curv(track, i):
    """TODO"""
    S = [0]
    for i in range(1, track.size()):
        ds = track.getObs(i - 1).position.distance2DTo(track.getObs(i).position)
        S.append(S[i - 1] + ds)
    return S


def heading(track, i):
    """TODO"""
    if i == len(track):
        return heading(track, i - 1)
    return track.getObs(i).position.azimuthTo(track.getObs(i - 1).position)


def speed(track, i):
    """
    Méthode calculant le paramètre 'speed' pour chaque point de la trace
    """

    # On attribut au point d'indice [0] la vitesse du point d'indice [1]
    if i == 0:
        ds0 = track.getObs(1).position.distance2DTo(track.getObs(0).position)
        dt0 = track.getObs(1).timestamp - track.getObs(0).timestamp
        if dt0 == 0:
            return utils.NAN
        else:
            return ds0 / dt0

    # On attribut au point d'indice [N-1] la vitesse du point d'indice [N-2]
    N = track.size()
    if i == N - 1:
        dsN = track.getObs(N - 1).position.distance2DTo(track.getObs(N - 2).position)
        dtN = track.getObs(N - 1).timestamp - track.getObs(N - 2).timestamp
        if dtN == 0:
            return utils.NAN
        else:
            return dsN / dtN

    # Pour les autres points :
    ds = track.getObs(i + 1).position.distance2DTo(track.getObs(i - 1).position)
    dt = track.getObs(i + 1).timestamp - track.getObs(i - 1).timestamp

    # La vitesse est obtenue en divisant la distance entre deux points successifs
    # par le temps les séparant
    if dt == 0:
        return utils.NAN
    else:
        return ds / dt


def acceleration(track, i):
    """
    Acceleration instantannée de la trace
    """

    if i == 0:
        return utils.NAN

    N = track.size()
    if i == N - 1:
        d = speed(track, i) - speed(track, i - 1)
        dt = track.getObs(i).timestamp - track.getObs(i - 1).timestamp

        if dt == 0:
            return utils.NAN
        return d / dt

    d = speed(track, i + 1) - speed(track, i - 1)
    dt = track.getObs(i + 1).timestamp - track.getObs(i - 1).timestamp

    if dt == 0:
        return utils.NAN

    return d / dt


# =============================================================================
#    Des AF algo sur les angles
# =============================================================================


def anglegeom(track, i) -> float:
    """
    Mesure l'angle  géométrique (non orienté) intérieur abc.

    :return: Angle abc (degrees)
    """

    if i == 0:
        return utils.NAN

    N = track.size()
    if i == N - 1:
        return utils.NAN

    x1 = track.getObs(i-1).position.getX()
    x2 = track.getObs(i).position.getX()
    x3 = track.getObs(i+1).position.getX()
    y1 = track.getObs(i-1).position.getY()
    y2 = track.getObs(i).position.getY()
    y3 = track.getObs(i+1).position.getY()

    num = (x1 - x2) * (x3 - x2) + (y1 - y2) * (y3 - y2)
    den = math.sqrt((x1-x2)**2 + (y1-y2)**2) * math.sqrt((x3-x2)**2 + (y3-y2)**2)
    r = num / den
    if r > 1:
        r = 1
    if r < -1:
        r = -1
    # print (num, den)
    angle = math.degrees(math.acos(r))
    return angle


def calculAngleOriente(track, i):
    """Mesure l'angle orienté dans le sens trigonométrique abc."""

    if i == 0:
        return utils.NAN

    N = track.size()
    if i == N - 1:
        return utils.NAN


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

    if i == 0:
        return utils.NAN

    N = track.size()
    if i == N - 1:
        return utils.NAN

    dx = float(track.getObs(i).position.getX()) - float(
        track.getObs(i - 1).position.getX()
    )
    dy = float(track.getObs(i).position.getY()) - float(
        track.getObs(i - 1).position.getY()
    )
    orientation = math.atan2(dy, dx)
    #print (orientation)
    angle = math.degrees(orientation)
    if angle < 0:
        angle += 360
    #print (angle)

    # On convertit la valeur calculée en orientation relative
    cap = utils.NAN

    for direction in orientation_dictionnary:
        if (
            angle >= orientation_dictionnary[direction][0]
            and angle < orientation_dictionnary[direction][1]
        ):
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


# =============================================================================
# =============================================================================
def stop_point_with_acceleration_criteria(track, i):
    """This algorithm detect stop point.
    A point is a stop when:
        - speed is null
        - acceleration is negative
    """
    if i == 0:
        return 0

    stop_point = 0
    v = speed(track, i)
    acc = acceleration(track, i)
    
    # Si un point d'indice [i] affiche une vitesse nulle suivant une deccelération,
    #    on cherche le prochain point d'accélération
    if abs(v) < 0.001 and acc < 0:
        # Initialisation d'un compteur sur i
        j = i
        # Tant qu'aucun des points suivants n'accélère, on ne marque pas le point d'arrêt
        while j <= track.size() - 2 and acceleration(track, j) <= 0:
            j += 1
            # Si on trouve un point d'accélération, on donne la valeur 1
            #     au paramètre du point d'indice [i]
            if acceleration(track, j) > 0:
                stop_point = 1

    return stop_point


VAL_AF_TIME_WINDOW_STOP = 1
VAL_AF_TIME_WINDOW_MOVE = 0
VAL_AF_TIME_WINDOW_NONE = -1


def stop_point_with_time_window_criteria(trace, i):
    """This algorithm of stop detection is based on geographical moving distance in time windows.

    The AF has value:

        - stop (*1*)
        - not stop (*0*)
        - not yet examined (*-1*)

    """

    name_af = "stop_point_with_time_window_criteria"

    N = trace.size()

    val = trace.getObsAnalyticalFeature(name_af, i)
    if val > -1:
        return val

    if i == N - 1:
        return trace.getObsAnalyticalFeature(name_af, N - 2)

    T = 40  # fenetre de 45s
    D = 30  # 30 metres

    S = trace.getAnalyticalFeature("abs_curv")

    j = i + 1
    ispause = False

    tj = trace.getObs(j).timestamp
    ti = trace.getObs(i).timestamp

    # On cherche la fin de la fenetre
    while (tj - ti) <= T:
        j = j + 1
        if j == N - 1:
            break
        tj = trace.getObs(j).timestamp

    #print(S[j] - S[i])

    # On agrandit la fenetre
    while (tj - ti) >= T and (S[j] - S[i]) <= D:
        ispause = True
        # print ('pause ' + str(i) + ',' + str(j))
        j = j + 1
        if j == N - 1:
            break
        tj = trace.getObs(j).timestamp

    retour = VAL_AF_TIME_WINDOW_MOVE
    if ispause:
        # PAUSES.append([i, j-1])
        #print ('pause de ' + str(i) + ',' + str(j-1))
        retour = VAL_AF_TIME_WINDOW_STOP
        for k in range(i, j - 1):
            trace.setObsAnalyticalFeature(name_af, k, VAL_AF_TIME_WINDOW_STOP)

    else:
        trace.setObsAnalyticalFeature(name_af, i, VAL_AF_TIME_WINDOW_MOVE)

    return retour
