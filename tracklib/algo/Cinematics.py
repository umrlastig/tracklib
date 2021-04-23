# --------------------------- Cinematics --------------------------------------
# Class to manage cinematic computations on GPS tracks
# -----------------------------------------------------------------------------

import sys
import progressbar
import numpy as np


from tracklib.core.Obs import Obs
from tracklib.core.TrackCollection import TrackCollection
from tracklib.core.Kernel import GaussianKernel

import tracklib.core.Utils as utils
import tracklib.algo.Analytics as Analytics
import tracklib.algo.Geometrics as Geometrics
import tracklib.algo.Interpolation as Interpolation
import tracklib.core.Operator as Operator
import tracklib.core.Kernel as Kernel


    
def estimate_speed(track):
    '''
    Compute and return speed for each point
    Difference finie arriere-avant
    '''
    if track.hasAnalyticalFeature(Analytics.BIAF_SPEED):
        return track.getAnalyticalFeature(Analytics.BIAF_SPEED)
    else:
        return track.addAnalyticalFeature(Analytics.speed)
		

# --------------------------------------------------
# Difference finie centree lissee
# --------------------------------------------------
def smoothed_speed_calculation(track, width):

    S = track.compute_abscurv()
    track.estimate_speed()
	
    if track.size() < width:
        print ('warning:not enough point in track for this width')
        return None

    for i in range(width, len(S)-width):
        ds = S[i+width] - S[i-width]
        dt = track[i+width].timestamp - track[i-width].timestamp
        
        if dt != 0: 
            track.setObsAnalyticalFeature("speed", i, ds/dt)

    for i in range(width):
        track.setObsAnalyticalFeature("speed", i, track["speed"][width])
    for i in range(len(S)-width, len(S)): 
        track.setObsAnalyticalFeature("speed", i, track["speed"][len(S) - width])	
		

def computeAvgSpeed(track, id_ini=0, id_fin=None):
    '''
    Computes averaged speed (m/s) between two points
    TODO : à adapter
    '''
    if id_fin is None:
        id_fin = track.size()-1
    d = track.getCurvAbsBetweenTwoPoints(id_ini, id_fin)
    t = track[id_fin].timestamp-track[id_ini].timestamp
    return d/t

def computeAvgAscSpeed(track, id_ini=0, id_fin=None):
    '''
    Computes average ascending speed (m/s)
    TODO : à adapter
    '''
    if id_fin is None:
        id_fin = track.size()-1
    dp =  track.computeAscDeniv(id_ini, id_fin)
    t = track[id_fin].timestamp - track[id_ini].timestamp
    return dp/t
	
def computeAbsCurv(track):
    '''Compute and return curvilinear abscissa for each points'''
    
    if not track.hasAnalyticalFeature(Analytics.BIAF_DS):
        track.addAnalyticalFeature(Analytics.ds, Analytics.BIAF_DS)
    if not track.hasAnalyticalFeature(Analytics.BIAF_ABS_CURV):
        track.operate(Operator.Operator.INTEGRATOR, Analytics.BIAF_DS, Analytics.BIAF_ABS_CURV)
    track.removeAnalyticalFeature(Analytics.BIAF_DS)
   
    return track.getAnalyticalFeature(Analytics.BIAF_ABS_CURV)
	
    
def computeCurvAbsBetweenTwoPoints(track, id_ini=0, id_fin=None):
    '''Computes and return the curvilinear abscissa between two points
    TODO : adapter avec le filtre''' 
    if id_fin is None:
        id_fin = track.size()-1
    s = 0
    for i in range(id_ini, id_fin):
        s = s + track[i].position.distance2DTo(track[i+1].position)
    return s
	
def computeNetDeniv(track, id_ini=0, id_fin=None):
    '''Computes net denivellation (in meters)'''
    if id_fin is None:
        id_fin = track.size()-1
    return track[id_fin].position.getZ() - track[id_ini].position.getZ()
	
	
def computeAscDeniv(track, id_ini=0, id_fin=None):
        '''Computes positive denivellation (in meters)'''  		
        if id_fin is None:
            id_fin = track.size()-1
        
        dp = 0
        
        for i in range(id_ini, id_fin):
            Z1 = track[i].position.getZ()
            Z2 = track[i+1].position.getZ()
            if (Z2 > Z1):
                dp += Z2-Z1
    
        return dp 
    
 
def computeDescDeniv(track, id_ini=0, id_fin=None):
    '''Computes negative denivellation (in meters)'''
    if id_fin is None:
        id_fin = track.size()-1 
		
    dn = 0
    
    for i in range(id_ini, id_fin):
        Z1 = track[i].position.getZ()
        Z2 = track[i+1].position.getZ()
        if (Z2 < Z1):
            dn += Z2-Z1

    return dn