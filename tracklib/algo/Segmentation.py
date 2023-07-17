"""Class to manage segmentation of GPS tracks"""

import sys
import math
import progressbar
import numpy as np

from tracklib.core.Obs import Obs
from tracklib.core.ObsCoords import ENUCoords
from tracklib.algo.Geometrics import Circle, minCircle

import tracklib.core.Utils as utils
from tracklib.algo.Interpolation import ALGO_LINEAR, MODE_SPATIAL
import tracklib.core.Operator as Operator
#from tracklib.algo.Analytics import speed, acceleration

# --------------------------------------------------------------------------
# Circular import (not satisfying solution)
# --------------------------------------------------------------------------
from tracklib.core.Track import Track
from tracklib.core.TrackCollection import TrackCollection


MODE_COMPARAISON_AND = 1
MODE_COMPARAISON_OR = 2

MODE_STOPS_LOCAL = 0
MODE_STOPS_GLOBAL = 1
MODE_STOPS_RTK = 2
MODE_STOPS_ACC = 3

MODE_SPLIT_RETURN_EXHAUSTIVE = 0
MODE_SPLIT_RETURN_FAST = 1

MODE_SEGMENTATION_MINIMIZE = 0
MODE_SEGMENTATION_MAXIMIZE = 1


# =============================================================================
# =============================================================================
#    Segmentation and Split track
# =============================================================================
# =============================================================================

def segmentation(track, afs_input, af_output, 
                 thresholds_max, mode_comparaison=MODE_COMPARAISON_AND):
    """
    Method to divide a track into multiple according to analytical feaures value.
    Creates an AF with 0 if change of division, 1 otherwise
    """

    # Gestion cas un seul AF
    if not isinstance(afs_input, list):
        afs_input = [afs_input]
    if not isinstance(thresholds_max, list):
        thresholds_max = [thresholds_max]

    track.createAnalyticalFeature(af_output)

    for i in range(track.size()):

        # On cumule les comparaisons pour chaque af_input
        if mode_comparaison == MODE_COMPARAISON_AND:
            comp = True
        else:
            comp = False

        for index, af_input in enumerate(afs_input):
            current_value = track.getObsAnalyticalFeature(af_input, i)

            # on compare uniquement si on peut
            if not utils.isnan(current_value):

                seuil_max = sys.float_info.max
                if thresholds_max != None and len(thresholds_max) >= index:
                    seuil_max = thresholds_max[index]

                if mode_comparaison == MODE_COMPARAISON_AND:
                    comp = comp and (current_value <= seuil_max)
                else:
                    comp = comp or (current_value <= seuil_max)

        #  On clot l'intervalle, on le marque a 1
        if not comp:
            track.setObsAnalyticalFeature(af_output, i, 1)
        else:
            track.setObsAnalyticalFeature(af_output, i, 0)


def split(track, source, limit=0) -> TrackCollection:
    """
    Splits track according to :
        - af name (considered as a marker) if `source` is a string
        - list of index if `source` is a list
        
    if limit > 0, only track which have more or equal than limit points are keeped.

    :return: No track if no segmentation, otherwise a TrackCollection object
    """

    NEW_TRACES = TrackCollection()

    # --------------------------------------------
    # Split from analytical feature name
    # --------------------------------------------
    if isinstance(source, str):
        count = 0  # Initialisation du compteur des étapes
        begin = 0  # indice du premier point de l'étape
        for i in range(track.size()):
            # Nouvelle trajectoire
            if track.getObsAnalyticalFeature(source, i) == 1:  

                # L'identifiant de la trace subdivisée est obtenue par concaténation
                # de l'identifiant de la trace initiale et du compteur
                # Important pour les pauses
                new_id = str(track.uid) + "." + str(count) + "." + str(begin) + "." + str(i)

                # La liste de points correspondant à l'intervalle de subdivision est créée
                newtrack = track.extract(begin, i)
                begin = i + 1
                newtrack.setUid(new_id)

                if (limit > 0 and newtrack.length() < limit):
                    continue
        
                NEW_TRACES.addTrack(newtrack)
                count += 1

        # Si tous les points sont dans la même classe, la liste d'étapes reste vide
        # sinon, on clôt la derniere étape et on l'ajoute à la liste
        if begin != 0:
            # Formalisme Important pour les pauses
            new_id = str(track.uid) + "." + str(count)+ "." + str(begin) + "." + str(track.size()-1)
            newtrack = track.extract(begin, track.size() - 1)
            
            if limit == 0 or (limit > 0 and newtrack.length() >= limit):
                newtrack.setUid(new_id)
                NEW_TRACES.addTrack(newtrack)

    # --------------------------------------------
    # Split from list of indices
    # --------------------------------------------
    if isinstance(source, list):
        for i in range(len(source) - 1):
            newtrack = track.extract(source[i], source[i + 1])
            if (limit > 0 and newtrack.length() < limit):
                continue
            NEW_TRACES.addTrack(newtrack)

    # RETURN collection
    return NEW_TRACES


def splitAR(track, pt1, pt2=None, radius=10, nb_min_pts=10, verbose=True):
    '''
    # -------------------------------------------------------------------------
    #  Method to split a track between two mark points
    # -------------------------------------------------------------------------
    Inputs:
        - track      : a track to segment
        - pt1        : first point 'departure'
        - pt2        : second point 'return'
                       If pt2 is not provided, it is set automatically equal to pt1
        - radius     : threshold distance (in ground units) around pt1 and pt2
        - nb_min_pts : minima number of points to form a track
    Output:
       - a track collection containing segmented tracks
    # -------------------------------------------------------------------------
    '''

    if pt2 is None:
        pt2 = pt1

    tracks = TrackCollection()
    
    subtrack = Track()
    k = -1
    while k < len(track) - 1:
        k = k + 1
        if (
            min(
                track[k].position.distance2DTo(pt1), track[k].position.distance2DTo(pt2)
            )
            < radius
        ):
            if len(subtrack) > nb_min_pts:
                tracks.addTrack(subtrack)
                if verbose:
                    print(
                        "Add sub-track: ",
                        subtrack[0].timestamp,
                        subtrack[-1].timestamp,
                        "[" + str(len(tracks)) + "]",
                    )
                subtrack = Track()
            subtrack.addObs(track[k].copy())
    
    if len(subtrack) > nb_min_pts:
        tracks.addTrack(subtrack)
        if verbose:
            print(
                "Add sub-track: ",
                subtrack[0].timestamp,
                subtrack[-1].timestamp,
                "[" + str(len(tracks)) + "]",
            )
    
    return tracks


def splitReturnTrip(track, mode):
    if mode == MODE_SPLIT_RETURN_EXHAUSTIVE:
        return splitReturnTripExhaustive(track)
    if mode == MODE_SPLIT_RETURN_FAST:
        return splitReturnTripFast(track)


def splitReturnTripExhaustive(track):
    """Split track when there is a return trip to keep only the first part"""

    min_val = 1e300
    argmin = 0

    AVG = Operator.Operator.AVERAGER
    for return_point in progressbar.progressbar(range(1, track.size() - 1)):

        T1 = track.extract(0, return_point)
        T2 = track.extract(return_point, track.size() - 1)

        avg = (T1 - T2).operate(AVG, "diff") + (T2 - T1).operate(AVG, "diff")

        if avg < min_val:
            min_val = avg
            argmin = return_point

    first_part = track.extract(0, argmin - 1)
    second_part = track.extract(argmin, track.size() - 1)

    TRACKS = TrackCollection()
    TRACKS.addTrack(first_part)
    TRACKS.addTrack(second_part)

    return TRACKS


def splitReturnTripFast(track, side_effect=0.1, sampling=1):
    """Split track when there is a return trip to keep only the first part.
    Second version with Fast Fourier Transform"""

    track = track.copy()
    track.toENUCoords(track.getFirstObs().position)
    track_test = track.copy()
    track_test.resample(
        (track_test.length() / track_test.size()) / sampling, ALGO_LINEAR, MODE_SPATIAL
    )

    H = np.fft.fft(track_test.getY())
    G = np.fft.fft(track_test.getY()[::-1])
    temp = np.flip(np.abs(np.fft.ifft(H * np.conj(G))))

    id = np.argmax(
        temp[int(side_effect * len(temp)) : int((1 - side_effect) * len(temp))]
    )
    pt = track_test[id].position

    dmin = 1e300
    argmin = 0
    for i in range(track.size()):
        d = track[i].position.distance2DTo(pt)
        if d < dmin:
            dmin = d
            argmin = i

    first_part = track.extract(0, argmin - 1)
    second_part = track.extract(argmin, track.size() - 1)

    TRACKS = TrackCollection()
    TRACKS.addTrack(first_part)
    TRACKS.addTrack(second_part)

    return TRACKS


# =============================================================================
# =============================================================================
#    Find Stop
# =============================================================================
# =============================================================================

def findStops(track: Track, spatial, temporal, mode, verbose=True) -> Track:
    '''
    Function to find stop positions from a track

    Parameters
    ----------
    track : Track

    spatial : float

    temporal : float

    mode : MODE_STOPS_LOCAL, MODE_STOPS_GLOBAL, MODE_STOPS_RTK, MODE_STOPS_ACC

    verbose : bool, optional
        The default is True.

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''
    if mode == MODE_STOPS_LOCAL:
        return findStopsLocal(track, spatial, temporal)
    if mode == MODE_STOPS_GLOBAL:
        return findStopsGlobal(track, spatial, temporal, verbose)
    if mode == MODE_STOPS_RTK:
        return findStopsGlobalForRTK(track, spatial, temporal, verbose)
    if mode == MODE_STOPS_ACC:
        pass


def findStopsLocal(track, speed=1, duration=10):
    '''
    # -------------------------------------------------------------------------
    Function to find stop positions from a track
    
    Inputs:
        - duration: minimal stop duration (in seconds)
        - speed: maximal speed during stop (in ground units / sec)
    Output: a track with centroids (and first time of stop sequence)
    
    For classical standard GPS track set 1 m/s for 10 sec)
    # -------------------------------------------------------------------------
    '''

    track = track.copy()
    stops = Track()
    
    segmentation(track, "speed", "#mark", speed)
    track.operate(Operator.Operator.DIFFERENTIATOR, "#mark")
    track.operate(Operator.Operator.RECTIFIER, "#mark")
    track.operate(Operator.Operator.SHIFT_LEFT, "#mark")
    #print (track.getAnalyticalFeature('#mark'))
                  
    segmentedTracks = split(track, "#mark")
    #print (len(segmentedTracks))

    TMP_RADIUS = []
    TMP_MEAN_X = []
    TMP_MEAN_Y = []
    TMP_MEAN_Z = []
    TMP_IDSTART = []
    TMP_IDEND = []
    TMP_STD_X = []
    TMP_STD_Y = []
    TMP_STD_Z = []
    TMP_DURATION = []
    TMP_NBPOINTS = []

    for i in range(1, len(segmentedTracks), 2):
        trackWS = segmentedTracks[i]
        if trackWS.duration() < duration:
            continue
        # print (trackWS)
        center = trackWS.getCentroid().copy()
        stops.addObs(Obs(center, trackWS.getFirstObs().timestamp.copy()))
            
        TMP_RADIUS.append(center)
        TMP_MEAN_X.append(trackWS.operate(Operator.Operator.AVERAGER, "x"))
        TMP_MEAN_Y.append(trackWS.operate(Operator.Operator.AVERAGER, "y"))
        TMP_MEAN_Z.append(trackWS.operate(Operator.Operator.AVERAGER, "z"))
        TMP_STD_X.append(trackWS.operate(Operator.Operator.STDDEV, "x"))
        TMP_STD_Y.append(trackWS.operate(Operator.Operator.STDDEV, "y"))
        TMP_STD_Z.append(trackWS.operate(Operator.Operator.STDDEV, "z"))
        
        tab = trackWS.uid.split('.')
        TMP_IDSTART.append(tab[2])
        TMP_IDEND.append(tab[3])
        TMP_NBPOINTS.append(trackWS.size())
        TMP_DURATION.append(trackWS.duration())

    if stops.size() == 0:
        return stops

    stops.createAnalyticalFeature("radius", TMP_RADIUS)
    stops.createAnalyticalFeature("mean_x", TMP_MEAN_X)
    stops.createAnalyticalFeature("mean_y", TMP_MEAN_Y)
    stops.createAnalyticalFeature("mean_z", TMP_MEAN_Z)
    stops.createAnalyticalFeature("id_ini", TMP_IDSTART)
    stops.createAnalyticalFeature("id_end", TMP_IDEND)
    stops.createAnalyticalFeature("sigma_x", TMP_STD_X)
    stops.createAnalyticalFeature("sigma_y", TMP_STD_Y)
    stops.createAnalyticalFeature("sigma_z", TMP_STD_Z)
    stops.createAnalyticalFeature("duration", TMP_DURATION)
    stops.createAnalyticalFeature("nb_points", TMP_NBPOINTS)

    stops.operate(Operator.Operator.QUAD_ADDER, "sigma_x", "sigma_y", "rmse")

    return stops



def stop_point_with_acceleration_criteria(track, diameter=20, duration=60):
    """
    This algorithm detect stop point.
    A point is a stop when speed is null and acceleration is negative.
    """
    
    '''
    if i == 0:
        return 0

    stop_point = 0
    v = speed(track, i)
    acc = acceleration(track, i)

    # Si un point d'indice [i] affiche une vitesse nulle suivant une deccelération,
    #    on cherche le prochain point d'accélération
    if abs(v) < 3 and acc < 0:
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
    '''

# ----------------------------------------------------------------
# Fonctions utilitaires
# ----------------------------------------------------------------
def backtracking(B, i, j):
    if (B[i, j] < 0) or (abs(i - j) <= 1):
        return [i]
    else:
        id = (int)(B[i, j])
        return backtracking(B, i, id) + backtracking(B, id, j)


def backward(B):
    n = B.shape[0]
    return backtracking(B, 0, n - 1) + [n - 1]


def plotStops(stops, x="x", y="y", r="radius", rf=1, sym="r-"):
    for i in range(len(stops)):
        Circle(ENUCoords(stops[x][i], stops[y][i]), rf * stops[r][i]).plot(sym)


'''
def removeStops(track, stops=None):
    if stops is None:
        stops = extractStopsBis(track)
    output = track.extract(0, stops["id_ini"][0])
    for i in range(len(stops) - 1):
        output = output + track.extract(stops["id_end"][i], stops["id_ini"][i + 1])
    output = output + track.extract(stops["id_end"][-1], track.size() - 1)
    return output
'''

def findStopsGlobal(track, diameter=20, duration=60, downsampling=1, verbose=True):
    '''
    Find stop points in a track based on two parameters:
    Maximal size of a stop (as the diameter of enclosing circle,
    in ground units) and minimal time duration (in seconds).
    Use downsampling parameter > 1 to speed up the process

    Parameters
    ----------
    track : Track
        track to detect stop points
    diameter : float, optional
        Maximal size of a stop (as the diameter of enclosing circle,
        in ground units). The default is 20.
    duration : float, optional
        minimal time duration (in seconds). The default is 60.
    downsampling : float, optional
        to speed up the process, value need to be > 1. The default is 1.
    verbose : boolean, optional
        verbose or not. The default is True.

    Returns
    -------
    stops : Track
        stops points constitute a new Track.
    '''


    # If down-sampling is required
    if downsampling > 1:
        track = track.copy()
        track **= track.size() / downsampling

    # ---------------------------------------------------------------------------
    # Computes cost matrix as :
    #    Cij = 0 if size of enclosing circle of pi, pi+1, ... pj-1 is > diameter
    #    Cij = 0 if time duration between pi and pj-1 is < duration
    #    Cij = (j-i)**2 = square of the number of points of segment otherwise
    # ---------------------------------------------------------------------------
    C = np.zeros((track.size(), track.size()))
    RANGE = range(track.size() - 2)
    if verbose:
        print("Minimal enclosing circles computation:")
        RANGE = progressbar.progressbar(RANGE)
    for i in RANGE:
        for j in range(i + 1, track.size() - 1):
            if track[i].distance2DTo(track[j - 1]) > diameter:
                C[i, j] = 0
                break
            if track[j - 1].timestamp - track[i].timestamp <= duration:
                C[i, j] = 0
                continue
            
            cercle = minCircle(track.extract(i, j - 1))
            if cercle != None:
                C[i, j] = 2 * cercle.radius
                C[i, j] = (C[i, j] < diameter) * (j - i) ** 2
            else:
                # TODO : à valider
                C[i, j] = 0
                continue
    C = C + np.transpose(C)

    # ---------------------------------------------------------------------------
    # Computes optimal partition with dynamic programing
    # ---------------------------------------------------------------------------
    segmentation = optimalPartition(C, MODE_SEGMENTATION_MAXIMIZE, verbose)
    #print ('seg', segmentation)

    stops = Track()
    TMP_RADIUS = []
    TMP_MEAN_X = []
    TMP_MEAN_Y = []
    TMP_MEAN_Z = []
    TMP_IDSTART = []
    TMP_IDEND = []
    TMP_STD_X = []
    TMP_STD_Y = []
    TMP_STD_Z = []
    TMP_DURATION = []
    TMP_NBPOINTS = []

    for i in range(len(segmentation) - 1):
        portion = track.extract(segmentation[i], segmentation[i + 1] - 1)
        C = minCircle(portion)
        if C != None:
            if (C.radius > diameter / 2) or (portion.duration() < duration):
                continue
            
            stops.addObs(Obs(C.center, portion.getFirstObs().timestamp))
            TMP_RADIUS.append(C.radius)
            TMP_MEAN_X.append(portion.operate(Operator.Operator.AVERAGER, "x"))
            TMP_MEAN_Y.append(portion.operate(Operator.Operator.AVERAGER, "y"))
            TMP_MEAN_Z.append(portion.operate(Operator.Operator.AVERAGER, "z"))
            TMP_STD_X.append(portion.operate(Operator.Operator.STDDEV, "x"))
            TMP_STD_Y.append(portion.operate(Operator.Operator.STDDEV, "y"))
            TMP_STD_Z.append(portion.operate(Operator.Operator.STDDEV, "z"))
            TMP_IDSTART.append(segmentation[i] * downsampling)
            TMP_IDEND.append((segmentation[i + 1] - 1) * downsampling)
            TMP_NBPOINTS.append(segmentation[i + 1] - segmentation[i])
            TMP_DURATION.append(portion.duration())

    if stops.size() == 0:
        return stops

    stops.createAnalyticalFeature("radius", TMP_RADIUS)
    stops.createAnalyticalFeature("mean_x", TMP_MEAN_X)
    stops.createAnalyticalFeature("mean_y", TMP_MEAN_Y)
    stops.createAnalyticalFeature("mean_z", TMP_MEAN_Z)
    stops.createAnalyticalFeature("id_ini", TMP_IDSTART)
    stops.createAnalyticalFeature("id_end", TMP_IDEND)
    stops.createAnalyticalFeature("sigma_x", TMP_STD_X)
    stops.createAnalyticalFeature("sigma_y", TMP_STD_Y)
    stops.createAnalyticalFeature("sigma_z", TMP_STD_Z)
    stops.createAnalyticalFeature("duration", TMP_DURATION)
    stops.createAnalyticalFeature("nb_points", TMP_NBPOINTS)

    stops.operate(Operator.Operator.QUAD_ADDER, "sigma_x", "sigma_y", "rmse")
    stops.base = track.base

    return stops


def findStopsGlobalForRTK(
    track, std_max=2e-2, duration=5, downsampling=1, verbose=True
):
    """Find stop points in a track based on maximal size of a stop and minimal
    time duration

    Two parameters:

        - Maximal size of a stop (as the standard deviation per axis, in ground units)
        - Minimal time duration (in seconds)

    Use downsampling parameter > 1 to speed up the process.

    Default is set for precise RTK GNSS survey (2 cm for 5 sec)
    """

    # If down-sampling is required
    if downsampling > 1:
        track = track.copy()
        track **= track.size() / downsampling

    # ---------------------------------------------------------------------------
    # Computes cost matrix as :
    #    Cij = 0 if sqrt(0.33*(std_x^2 + std_y^2 + std_Z^2)) > std_max
    #    Cij = 0 if time duration between pi and p-1 is < duration
    #    Cij = (j-i)**2 = square of the number of points of segment otherwise
    # ---------------------------------------------------------------------------
    C = np.zeros((track.size(), track.size()))
    RANGE = range(track.size() - 2)
    if verbose:
        print("Minimal enclosing circles computation:")
        RANGE = progressbar.progressbar(RANGE)
    for i in RANGE:
        for j in range(i + 1, track.size() - 1):
            if track[i].distanceTo(track[j - 1]) > 3 * std_max:
                C[i, j] = 0
                break
            if track[j - 1].timestamp - track[i].timestamp <= duration:
                C[i, j] = 0
                continue
            portion = track.extract(i, j - 1)
            varx = portion.operate(Operator.Operator.VARIANCE, "x")
            vary = portion.operate(Operator.Operator.VARIANCE, "y")
            varz = portion.operate(Operator.Operator.VARIANCE, "z")
            C[i, j] = math.sqrt(varx + vary + varz)
            C[i, j] = (C[i, j] < std_max) * (j - i) ** 2
    C = C + np.transpose(C)

    # ---------------------------------------------------------------------------
    # Computes optimal partition with dynamic programing
    # ---------------------------------------------------------------------------
    segmentation = optimalPartition(C, MODE_SEGMENTATION_MAXIMIZE, verbose)

    stops = Track()

    TMP_RADIUS = []
    TMP_MEAN_X = []
    TMP_MEAN_Y = []
    TMP_MEAN_Z = []
    TMP_IDSTART = []
    TMP_IDEND = []
    TMP_STD_X = []
    TMP_STD_Y = []
    TMP_STD_Z = []
    TMP_DURATION = []
    TMP_NBPOINTS = []

    for i in range(len(segmentation) - 1):
        portion = track.extract(segmentation[i], segmentation[i + 1] - 1)

        radius = C[segmentation[i], segmentation[i + 1]]
        if radius == 0:
            continue

        xm = portion.operate(Operator.Operator.AVERAGER, "x")
        ym = portion.operate(Operator.Operator.AVERAGER, "y")
        zm = portion.operate(Operator.Operator.AVERAGER, "z")

        xv = portion.operate(Operator.Operator.VARIANCE, "x")
        yv = portion.operate(Operator.Operator.VARIANCE, "y")
        zv = portion.operate(Operator.Operator.VARIANCE, "z")

        pt = portion[0].position.copy()
        pt.setX(xm)
        pt.setY(ym)
        pt.setZ(zm)
        stops.addObs(Obs(pt, portion[0].timestamp))

        TMP_RADIUS.append(math.sqrt(xv + yv + zv))
        TMP_MEAN_X.append(xm)
        TMP_MEAN_Y.append(ym)
        TMP_MEAN_Z.append(zm)
        TMP_STD_X.append(xv ** 0.5)
        TMP_STD_Y.append(yv ** 0.5)
        TMP_STD_Z.append(zv ** 0.5)
        TMP_IDSTART.append(segmentation[i] * downsampling)
        TMP_IDEND.append((segmentation[i + 1] - 1) * downsampling)
        TMP_NBPOINTS.append(segmentation[i + 1] - segmentation[i])
        TMP_DURATION.append(portion.duration())

    if stops.size() == 0:
        return stops

    stops.createAnalyticalFeature("radius", TMP_RADIUS)
    stops.createAnalyticalFeature("mean_x", TMP_MEAN_X)
    stops.createAnalyticalFeature("mean_y", TMP_MEAN_Y)
    stops.createAnalyticalFeature("mean_z", TMP_MEAN_Z)
    stops.createAnalyticalFeature("id_ini", TMP_IDSTART)
    stops.createAnalyticalFeature("id_end", TMP_IDEND)
    stops.createAnalyticalFeature("sigma_x", TMP_STD_X)
    stops.createAnalyticalFeature("sigma_y", TMP_STD_Y)
    stops.createAnalyticalFeature("sigma_z", TMP_STD_Z)
    stops.createAnalyticalFeature("duration", TMP_DURATION)
    stops.createAnalyticalFeature("nb_points", TMP_NBPOINTS)

    stops.operate(Operator.Operator.QUAD_ADDER, "sigma_x", "sigma_y", "rmse")
    stops.base = track.base

    return stops


def optimalPartition(cost_matrix, mode=MODE_SEGMENTATION_MINIMIZE, verbose=True):
    '''
    # -------------------------------------------------------------------------
      Generic method to segment a track (with it cost matrix) 
      with dynamic programming
    # -------------------------------------------------------------------------
    Inputs:
        - cost: a three or four-valued function taking as input a track, two
                integers i < j and an optional global parameter, and returning
                the cost of a segment from i to j (both included) in track
                Note that cost function may as well be considered as a reward
                function, simply by setting mode to MODE_SEGMENTATION_MAXIMIZE
        - mode: a parameter inidcating wether cost function must be minnimized
               (MODE_SEGMENTATION_MINIMIZE) or maximized (MODE_SEGMENTATION_MAXIMIZE)
        - verbose: parameter to enable progress bar and console displays
    Output:
        - A optimal segmentation, represented as a list of indices in track
    # -------------------------------------------------------------------------
    '''

    N = cost_matrix.shape[0] - 1
    D = np.zeros((N, N))
    M = np.zeros((N, N))

    for i in range(N):
        for j in range(i, N):
            D[i, j] = cost_matrix[i, j]
            M[i, j] = -1

    # ---------------------------------------------------------------------------
    # Computes optimal partition with dynamic programing
    # ---------------------------------------------------------------------------
    RANGE = range(2, N)
    if verbose:
        print("Optimal split search:")
        RANGE = progressbar.progressbar(RANGE)
    for diag in RANGE:
        for i in range(0, N - diag):
            j = i + diag
            for k in range(i + 1, j):
                val = D[i, k] + D[k, j]
                if val < D[i, j] and MODE_SEGMENTATION_MINIMIZE:
                    D[i, j] = val
                    M[i, j] = k
                if val > D[i, j] and MODE_SEGMENTATION_MAXIMIZE:
                    D[i, j] = val
                    M[i, j] = k

    # ---------------------------------------------------------------------------
    # Backward phase to form optimal split
    # ---------------------------------------------------------------------------
    return backward(M)


def optimalSegmentation(
    track, cost, glob_param=None, mode=MODE_SEGMENTATION_MINIMIZE, verbose=True
):

    # ---------------------------------------------------------------------------
    # Computes cost matrix as :
    #    Cij = width of MBR of point set pi, pi+1, ... pj-1
    # ---------------------------------------------------------------------------
    C = np.zeros((track.size(), track.size()))

    RANGE = range(track.size() - 2)
    if verbose:
        print("Cost matrix computation:")
        RANGE = progressbar.progressbar(RANGE)
    for i in RANGE:
        for j in range(i, track.size() - 1):
            if glob_param is None:
                C[i, j] = cost(track, i, j - 1)
            else:
                C[i, j] = cost(track, i, j - 1, glob_param)

    C = C + np.transpose(C)

    return optimalPartition(C, mode, verbose)


# =============================================================================
# =============================================================================
#    ST-DBSCAN
# =============================================================================
# =============================================================================
    
def stdbscan(track, af_name, eps1, eps2, minPts, deltaT, debug = False):
    '''
    
    References
    ----------
    Birant, D., & Kut, A. (2007). ST-DBSCAN: An algorithm for clustering
    spatial–temporal data. Data & Knowledge Engineering, 60(1), 208-221.


    Parameters
    -----------
    track : Track
        track to detect stop points.
    eps1 : float
        maximum geographical coordinate (spatial) distance value.
    eps2 : float
        maximum non-spatial distance value.
    minPts : int
        minimum number of points within eps1 and eps2 distance.
    deltaT : float
        threshold value to be included in a cluster.

    Returns
    -------
    Cluster in AF

    '''
    
    stack = []
    cluster_label = 0
    
    track.createAnalyticalFeature('stdbscan', 0)
    track.createAnalyticalFeature('noise', 0)
    
    for i, obs in enumerate(track):
        nocluster = track.getObsAnalyticalFeature('stdbscan', i)
        if nocluster == 0:
            neighbors_index = retrieveNeighbors(track, af_name, i, eps1, eps2)
            if len(neighbors_index) < minPts:
                track.setObsAnalyticalFeature('noise', i, 1)
            else:
                cluster_label += 1
                if debug:
                    print ('New cluster ', str(cluster_label), ', i= ', i)
                    
                for k in neighbors_index:
                    track.setObsAnalyticalFeature('stdbscan', k, cluster_label)
                    stack.append(k)
                    
                while len(stack) > 0:
                     io = stack[0]
                     stack.remove(io)
                     neighbors_index2 = retrieveNeighbors(track, af_name, io, eps1, eps2)
                     if len(neighbors_index2) >= minPts:
                         for k in neighbors_index2:
                             nonoise =  track.getObsAnalyticalFeature('noise', k)
                             nocluster = track.getObsAnalyticalFeature('stdbscan', k)
                             # avg
                             avgCluster = computeAvgCluster(track, af_name, cluster_label)
                             diff = abs(avgCluster - track.getObsAnalyticalFeature(af_name, k))
                             if (nonoise > 0 or nocluster == 0) and diff < deltaT:
                                 track.setObsAnalyticalFeature('stdbscan', k, cluster_label)
                                 track.setObsAnalyticalFeature('noise', k, 0)
                                 stack.append(k)
                    
def computeAvgCluster(track, af_name, cluster_label):
    '''
    AF average values of the cluster_label cluster.
    '''
    avgCluster = 0
    nbObsCluster = 0
    for o in range(track.size()):
        valueAF = track.getObsAnalyticalFeature(af_name, o)
        nocluster = track.getObsAnalyticalFeature('stdbscan', o)
        if nocluster == cluster_label:
            nbObsCluster += 1
            avgCluster += valueAF
    avgCluster = avgCluster / nbObsCluster
    return avgCluster
    

def retrieveNeighbors(track, af_name, j, eps1, eps2):
    '''
    objects that have a distance less than Eps1 and Eps2 parameters to the selected object.
    Equals to the intersection of Retrieve_Neighbours(object, Eps1) and Retrieve_Neighbours(object, Eps2)

    Eps1 is the distance parameter for spatial attributes (latitude and longitude). 
    Eps2 is the distance parameter for non-spatial attributes (af values)

    return list of index
    '''
    neighbors_index = []
    for i in range (track.size()):
        if i == j:
            continue
        valj = track.getObsAnalyticalFeature(af_name, j)
        vali = track.getObsAnalyticalFeature(af_name, i)
        daf = abs(valj - vali)
        
        dd = track.getObs(j).distanceTo(track.getObs(i))
        #dt = abs(track.getObs(j).timestamp.toAbsTime() - track.getObs(i).timestamp.toAbsTime())
        
        if dd <= eps1 and daf <= eps2:
            neighbors_index.append(i)
        
    return neighbors_index


#def standardizing(neigh_ipm, ipm_cluster):
#    return (neigh_ipm - ipm_cluster.mean()) / ipm_cluster.std(ddof=0)




   
    
                           

