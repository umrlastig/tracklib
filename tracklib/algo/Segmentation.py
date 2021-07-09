# -------------------------- Segmentation -------------------------------------
# Class to manage segmentation of GPS tracks
# -----------------------------------------------------------------------------

import sys
import math
import progressbar
import numpy as np

from tracklib.core.Obs import Obs
from tracklib.core.Coords import ENUCoords
from tracklib.algo.Geometrics import Circle

import tracklib.core.Utils as utils
import tracklib.algo.Geometrics as Geometrics
import tracklib.algo.Interpolation as interp
import tracklib.core.Operator as Operator

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

MODE_SPLIT_RETURN_EXHAUSTIVE = 0
MODE_SPLIT_RETURN_FAST = 1

MODE_SEGMENTATION_MINIMIZE = 0
MODE_SEGMENTATION_MAXIMIZE = 1

# -------------------------------------------------------------------------
# Segmentation and Split track
# -------------------------------------------------------------------------
    
def segmentation(track, afs_input, af_output, thresholds_max, mode_comparaison = MODE_COMPARAISON_AND):
    ''' Method to divide a track into multiple according to analytical feaures value
    Creates an AF with 0 if change of division, 1 otherwise'''
    
    # Gestion cas un seul AF        
    if not isinstance(afs_input, list):
        afs_input = [afs_input]        
    if not isinstance(thresholds_max, list):
        thresholds_max = [thresholds_max]    
    
    track.createAnalyticalFeature(af_output)
    
    for i in range(track.size()):
        
        # On cumule les comparaisons pour chaque af_input
        comp = (1 == 1)
            
        for index, af_input in enumerate(afs_input):
            current_value = track.getObsAnalyticalFeature(af_input, i)
            
            # on compare uniquement si on peut
            if not utils.isnan(current_value):
            
                seuil_max =  sys.float_info.max
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
            


def split(track, source):
    '''Splits track according to:
	   - af name (considered as a marker) if source is a string 
       - list of index if source is a list
	Returns no trrack if no segmentation, otherwise a TrackCollection object
    '''
    
    NEW_TRACES = TrackCollection()
    
	# --------------------------------------------
	# Split from analytical feature name
	# --------------------------------------------
    if isinstance(source, str):
	
        count = 0  # Initialisation du compteur des étapes
        begin = 0  # indice du premier point de l'étape
    
        for i in range(track.size()):
        
            if track.getObsAnalyticalFeature(source, i) == 1:  # Nouvelle trajectoire
                
                # L'identifiant de la trace subdivisée est obtenue par concaténation 
                # de l'identifiant de la trace initiale et du compteur
                new_id = str(track.uid) + '.' + str(count)
            
                # La liste de points correspondant à l'intervalle de subdivision est créée
                new_traj = track.extract(begin, i)
                new_traj.setUid(new_id)
            
                NEW_TRACES.addTrack(new_traj)
                count += 1
                begin = i+1
            
        # Si tous les points sont dans la même classe, la liste d'étapes reste vide
        # sinon, on clôt la derniere étape et on l'ajoute à la liste
        if begin != 0:
            new_id = str(track.uid) + '.' + str(count)
            new_traj = track.extract(begin, track.size() - 1)
            new_traj.setUid(new_id)
            NEW_TRACES.addTrack(new_traj)
    
	# --------------------------------------------
	# Split from list of indices
	# --------------------------------------------
    if isinstance(source, list):
        for i in range(len(source)-1):
           NEW_TRACES.addTrack(track.extract(source[i], source[i+1]))

    return NEW_TRACES
    
    
# -------------------------------------------------------------------
# Function to find stop positions from a track
# -------------------------------------------------------------------
def findStops(track, spatial, temporal, mode, verbose=True):  
    if mode == MODE_STOPS_LOCAL:
        return findStopsLocal(track, spatial, temporal)
    if mode == MODE_STOPS_GLOBAL:
        return findStopsGlobal(track, spatial, temporal, verbose)
    if mode == MODE_STOPS_RTK:
        return findStopsGlobalForRTK(track, spatial, temporal, verbose)
    
# -------------------------------------------------------------------
# Function to find stop positions from a track
# Inputs:
#     - duration: minimal stop duration (in seconds)
#     - speed: maximal speed during stop (in ground units / sec)
# Output: a track with centroids (and first time of stop sequence)
# For classical standard GPS track set 1 m/s for 10 sec)'''
# -------------------------------------------------------------------
def findStopsLocal(track, speed=1, duration=10):        
    
    track = track.copy()
    stops = Track()
   
    track.segmentation("speed", "#mark", speed)
    track.operate(Operator.Operator.DIFFERENTIATOR, "#mark")
    track.operate(Operator.Operator.RECTIFIER, "#mark")

    TRACES = split(track, "#mark")            

    TMP_MEAN_X = []
    TMP_MEAN_Y = []
    TMP_MEAN_Z = []    
    TMP_STD_X = []
    TMP_STD_Y = []
    TMP_STD_Z = []
    TMP_DURATION = []
    TMP_NBPOINTS = []	
    
    for i in range(0,len(TRACES),2):
        if (TRACES[i].duration() < duration):
            continue
        stops.addObs(Obs(TRACES[i].getCentroid().copy(), TRACES[i].getFirstObs().timestamp.copy()))
        TMP_SIGMA_X.append(TRACES[i].operate(Operator.Operator.AVERAGER, 'x'))
        TMP_SIGMA_Y.append(TRACES[i].operate(Operator.Operator.AVERAGER, 'y'))
        TMP_SIGMA_Z.append(TRACES[i].operate(Operator.Operator.AVERAGER, 'z'))
        TMP_SIGMA_X.append(TRACES[i].operate(Operator.Operator.STDDEV, 'x'))
        TMP_SIGMA_Y.append(TRACES[i].operate(Operator.Operator.STDDEV, 'y'))
        TMP_SIGMA_Z.append(TRACES[i].operate(Operator.Operator.STDDEV, 'z'))
        TMP_NBPOINTS.append(TRACES[i].size())
        TMP_DURATION.append(TRACES[i].duration())
    
	
    if stops.size() == 0:
        return stops
        
    stops.createAnalyticalFeature("radius", TMP_RADIUS)
    stops.createAnalyticalFeature("mean_x", TMP_MEAN_X)
    stops.createAnalyticalFeature("mean_y", TMP_MEAN_Y)
    stops.createAnalyticalFeature("mean_z", TMP_MEAN_Z)
    stops.createAnalyticalFeature("sigma_x", TMP_STD_X)
    stops.createAnalyticalFeature("sigma_y", TMP_STD_Y)
    stops.createAnalyticalFeature("sigma_z", TMP_STD_Z)
    stops.createAnalyticalFeature("duration", TMP_DURATION)
    stops.createAnalyticalFeature("nb_points", TMP_NBPOINTS)
	
    stops.operate(Operator.Operator.QUAD_ADDER, "sigma_x", "sigma_y", "rmse")
	
    return stops
    
    
# ----------------------------------------------------------------
# Fonctions utilitaires
# ----------------------------------------------------------------
def backtracking(B, i, j):
    if (B[i,j] < 0) or (abs(i-j) <= 1):
        return [i]
    else:
        id = (int)(B[i,j])
        return backtracking(B, i, id) + backtracking(B, id, j)

def backward(B):
    n = B.shape[0]
    return backtracking(B, 0, n-1) + [n-1]

def plotStops(stops, x="x", y="y", r="radius", rf=1, sym='r-'):
    for i in range(len(stops)):
        Circle(ENUCoords(stops[x][i], stops[y][i]), rf*stops[r][i]).plot(sym)
    
def removeStops(track, stops=None):    
    if stops is None:
        stops = extractStopsBis(track)
    output = track.extract(0, stops["id_ini"][0])
    for i in range(len(stops)-1):
        output = output + track.extract(stops["id_end"][i], stops["id_ini"][i+1])
    output = output + track.extract(stops["id_end"][-1], track.size()-1)
    return output
    
		
def findStopsGlobal(track, diameter=20, duration=60, downsampling=1, verbose=True):
    '''Find stop points in a track based on two parameters:
        Maximal size of a stop (as the diameter of enclosing circle, 
        in ground units) and minimal time duration (in seconds)
        Use downsampling parameter > 1 to speed up the process'''
        
    # If down-sampling is required
    if (downsampling > 1):
        track = track.copy()
        track **= track.size()/downsampling
    
    # ---------------------------------------------------------------------------
    # Computes cost matrix as :
    #    Cij = 0 if size of enclosing circle of pi, pi+1, ... pj-1 is > diameter
    #    Cij = 0 if time duration between pi and p-1 is < duration
    #    Cij = (j-i)**2 = square of the number of points of segment otherwise
    # ---------------------------------------------------------------------------
    C = np.zeros((track.size(), track.size()))
    RANGE = range(track.size()-2)
    if verbose:
        print("Minimal enclosing circles computation:")
        RANGE = progressbar.progressbar(RANGE)
    for i in RANGE:
        for j in range(i+1, track.size()-1):
            if (track[i].distance2DTo(track[j-1]) > diameter):
                C[i,j] = 0
                break
            if (track[j-1].timestamp - track[i].timestamp <= duration):
                C[i,j] = 0
                continue
            C[i,j] = 2*Geometrics.minCircle(track.extract(i,j-1))[1]
            C[i,j] = (C[i,j] < diameter)*(j-i)**2
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
    
    for i in range(len(segmentation)-1):
        portion = track.extract(segmentation[i], segmentation[i+1]-1)
        C = Geometrics.minCircle(portion)
        if ((C[1] > diameter/2) or (portion.duration() < duration)):
            continue
        stops.addObs(Obs(C[0], portion.getFirstObs().timestamp))
        TMP_RADIUS.append(C[1])
        TMP_MEAN_X.append(portion.operate(Operator.Operator.AVERAGER, 'x'))
        TMP_MEAN_Y.append(portion.operate(Operator.Operator.AVERAGER, 'y'))
        TMP_MEAN_Z.append(portion.operate(Operator.Operator.AVERAGER, 'z'))
        TMP_STD_X.append(portion.operate(Operator.Operator.STDDEV, 'x'))
        TMP_STD_Y.append(portion.operate(Operator.Operator.STDDEV, 'y'))
        TMP_STD_Z.append(portion.operate(Operator.Operator.STDDEV, 'z'))
        TMP_IDSTART.append(segmentation[i]*downsampling)
        TMP_IDEND.append((segmentation[i+1]-1)*downsampling)
        TMP_NBPOINTS.append(segmentation[i+1]-segmentation[i])
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
	
def findStopsGlobalForRTK(track, std_max=2e-2, duration=5, downsampling=1, verbose=True):
    '''Find stop points in a track based on two parameters:
        Maximal size of a stop (as the standard deviation per axis, 
        in ground units) and minimal time duration (in seconds)
        Use downsampling parameter > 1 to speed up the process
		Default is set for precise RTK GNSS survey (2 cm for 5 sec)'''
        
    # If down-sampling is required
    if (downsampling > 1):
        track = track.copy()
        track **= track.size()/downsampling
    
    # ---------------------------------------------------------------------------
    # Computes cost matrix as :
    #    Cij = 0 if sqrt(0.33*(std_x^2 + std_y^2 + std_Z^2)) > std_max 
    #    Cij = 0 if time duration between pi and p-1 is < duration
    #    Cij = (j-i)**2 = square of the number of points of segment otherwise
    # ---------------------------------------------------------------------------
    C = np.zeros((track.size(), track.size()))
    RANGE = range(track.size()-2)
    if verbose:
        print("Minimal enclosing circles computation:")
        RANGE = progressbar.progressbar(RANGE)
    for i in RANGE:
        for j in range(i+1, track.size()-1):
            if (track[i].distanceTo(track[j-1]) > 3*std_max):
                C[i,j] = 0
                break
            if (track[j-1].timestamp - track[i].timestamp <= duration):
                C[i,j] = 0
                continue
            portion = track.extract(i,j-1)
            varx = portion.operate(Operator.Operator.VARIANCE, "x")
            vary = portion.operate(Operator.Operator.VARIANCE, "y")
            varz = portion.operate(Operator.Operator.VARIANCE, "z")
            C[i,j] = math.sqrt(varx + vary + varz)
            C[i,j] = (C[i,j] < std_max)*(j-i)**2
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
    
    for i in range(len(segmentation)-1):
        portion = track.extract(segmentation[i], segmentation[i+1]-1)

        radius = C[segmentation[i],segmentation[i+1]]
        if  radius == 0:
            continue

        xm = portion.operate(Operator.Operator.AVERAGER, 'x')
        ym = portion.operate(Operator.Operator.AVERAGER, 'y')
        zm = portion.operate(Operator.Operator.AVERAGER, 'z')
		
        xv = portion.operate(Operator.Operator.VARIANCE, 'x')
        yv = portion.operate(Operator.Operator.VARIANCE, 'y')
        zv = portion.operate(Operator.Operator.VARIANCE, 'z')
 		
        pt = portion[0].position.copy(); pt.setX(xm); pt.setY(ym); pt.setZ(zm)
        stops.addObs(Obs(pt, portion[0].timestamp))

        TMP_RADIUS.append(math.sqrt(xv+yv+zv))
        TMP_MEAN_X.append(xm)
        TMP_MEAN_Y.append(ym)
        TMP_MEAN_Z.append(zm)
        TMP_STD_X.append(xv**0.5)
        TMP_STD_Y.append(yv**0.5)
        TMP_STD_Z.append(zv**0.5)
        TMP_IDSTART.append(segmentation[i]*downsampling)
        TMP_IDEND.append((segmentation[i+1]-1)*downsampling)
        TMP_NBPOINTS.append(segmentation[i+1]-segmentation[i])
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

def splitReturnTrip(track, mode):
    if mode == MODE_SPLIT_RETURN_EXHAUSTIVE:
        return splitReturnTripExhaustive(track)
    if mode == MODE_SPLIT_RETURN_FAST:
        return splitReturnTripFast(track)        
        
def splitReturnTripExhaustive(track):
    '''Split track when there is a return trip to keep only the first part'''
    
    min_val = 1e300
    argmin = 0
    
    AVG = Operator.Operator.AVERAGER
    for return_point in progressbar.progressbar(range(1, track.size()-1)):

        T1 = track.extract(0, return_point)
        T2 = track.extract(return_point, track.size()-1)
        
        avg = (T1-T2).operate(AVG, "diff") + (T2-T1).operate(AVG, "diff")
    
        if avg < min_val:
            min_val = avg
            argmin = return_point
    
    first_part =  track.extract(0, argmin-1)
    second_part = track.extract(argmin, track.size()-1)

    TRACKS = TrackCollection()
    TRACKS.addTrack(first_part)
    TRACKS.addTrack(second_part)

    return (TRACKS)
    
def splitReturnTripFast(track, side_effect=0.1, sampling=1):
    '''Split track when there is a return trip to keep only the first part.
    Second version with Fast Fourier Transform'''
    
    track = track.copy()
    track.toENUCoords(track.getFirstObs().position)
    track_test = track.copy()
    track_test.resample((track_test.length()/track_test.size())/sampling, interp.ALGO_LINEAR, interp.MODE_SPATIAL) 

    H = np.fft.fft(track_test.getY())
    G = np.fft.fft(track_test.getY()[::-1])
    temp = np.flip(np.abs(np.fft.ifft(H*np.conj(G))))
    
    id = np.argmax(temp[int(side_effect*len(temp)):int((1-side_effect)*len(temp))])
    pt = track_test[id].position

    dmin = 1e300
    argmin = 0
    for i in range(track.size()):
        d = track[i].position.distance2DTo(pt)
        if d < dmin:
            dmin = d
            argmin = i
    
    first_part =  track.extract(0, argmin-1)
    second_part = track.extract(argmin, track.size()-1)

    TRACKS = TrackCollection()
    TRACKS.addTrack(first_part)
    TRACKS.addTrack(second_part)
    
    return TRACKS
	
	
# -------------------------------------------------------------------------
#  Generic method to segment a track with dynamic programming
# -------------------------------------------------------------------------
# Inputs: 
#    - track: A track to segment (potentially with analytical features)
#    - cost: a three or four-valued function taking as input a track, two 
#      integers i < j and an optional global parameter, and returning 
#      the cost of a segment from i to j (both included) in track
#      Note that cost function may as well be considered as a reward 
#      function, simply by setting mode to MODE_SEGMENTATION_MAXIMIZE
#    - mode: a parameter inidcating wether cost function must be minnimized
#      (MODE_SEGMENTATION_MINIMIZE) or maximized (MODE_SEGMENTATION_MAXIMIZE)
#    - verbose: parameter to enable progress bar and console displays
# Output: 
#    - A optimal segmentation, represented as a list of indices in track
# -------------------------------------------------------------------------
def optimalPartition(cost_matrix, mode=MODE_SEGMENTATION_MINIMIZE, verbose=True):

    N = cost_matrix.shape[0]-1
    D = np.zeros((N,N))
    M = np.zeros((N,N))
    
    for i in range(N):
        for j in range(i,N):
            D[i,j] = cost_matrix[i,j]
            M[i,j] = -1
    	
	# ---------------------------------------------------------------------------
    # Computes optimal partition with dynamic programing
    # ---------------------------------------------------------------------------    
    RANGE = range(2,N)
    if verbose:
        print("Optimal split search:")
        RANGE = progressbar.progressbar(RANGE)
    for diag in RANGE:
        for i in range(0,N-diag):
            j=i+diag
            for k in range(i+1,j):
                val = D[i,k] + D[k,j]
                if val < D[i,j] and MODE_SEGMENTATION_MINIMIZE:
                    D[i,j] = val
                    M[i,j] = k
                if val > D[i,j] and MODE_SEGMENTATION_MAXIMIZE:
                    D[i,j] = val
                    M[i,j] = k  					

	# ---------------------------------------------------------------------------
    # Backward phase to form optimal split
    # ---------------------------------------------------------------------------
    return backward(M)

def optimalSegmentation(track, cost, glob_param=None, mode=MODE_SEGMENTATION_MINIMIZE, verbose=True):
	
	# ---------------------------------------------------------------------------
    # Computes cost matrix as :
    #    Cij = width of MBR of point set pi, pi+1, ... pj-1
    # ---------------------------------------------------------------------------
    C = np.zeros((track.size(), track.size()))

    RANGE = range(track.size()-2)
    if verbose:
        print("Cost matrix computation:")
        RANGE = progressbar.progressbar(RANGE)
    for i in RANGE:
        for j in range(i, track.size()-1): 
            if glob_param is None:
                C[i,j] = cost(track, i, j-1)
            else:
                C[i,j] = cost(track, i, j-1, glob_param)
				
    C = C + np.transpose(C)

    return optimalPartition(C, mode, verbose)

                    


