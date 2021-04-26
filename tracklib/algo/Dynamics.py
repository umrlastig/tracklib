# --------------------------- Cinematics --------------------------------------
# Class to manage cinematic computations on GPS tracks
# -----------------------------------------------------------------------------

import sys
import math
import progressbar
import numpy as np
import matplotlib.pyplot as plt

from tracklib.core.Obs import Obs
from tracklib.core.Coords import ENUCoords
from tracklib.core.TrackCollection import TrackCollection
from tracklib.core.Kernel import GaussianKernel

import tracklib.core.Utils as utils
import tracklib.algo.Analytics as Analytics
import tracklib.algo.Geometrics as Geometrics
import tracklib.algo.Interpolation as Interpolation
import tracklib.core.Operator as Operator
import tracklib.core.Kernel as Kernel

MODE_OBS_AS_SCALAR = 0
MODE_OBS_AS_2D_POSITION = 1
MODE_OBS_AS_3D_POSITION = 2

# -------------------------------------------------------
# Hidden Markov Model is designed to estimate discrete 
# sequential variables on tracks, given a probabilistic 
# transition model Q and observation model P on S :
#    - S is a two-valued function, where S(t, k) 
#      provides a list of all the possible states of 
#      track t at epoch k.
#    - Q is a four-valued function, giving the (possibly 
#    non-normalized) probability function Q(s1,s2,k,t) 
#    to observe a transition from state s1 to state s2, at
#    in track t at epoch k. 
#    - P is a four-valued function, giving the (possibly 
#    non-normalized) probability P(s,y,k,t) = P(y|si), 
#    the probability to observe y when (actual) state is 
#    s in track t at epoch k.
# Note that s1 and s2 arguments in transition Q must belong 
# to the sets S(t,k) and S(t,k+1), respectively.
# Observation y may be  any value (continuous or discrete,
# even string or boolean). It may also be a list of values 
# for multi-dimensional hidden markov model. 
# If the underlying Markov model is stationnary, then 
# Q, P and S do not depend on k. In this case, track t 
# and epoch k are no longer mandatory in S, Q and P 
# functions. They can be 0-valued (constant output), 
# 2-valued and 2-valued (respectively), if the boolean 
# member value "stationarity" is set to True.
# log: set to True if Q and P are already log values
# -------------------------------------------------------
class HMM:

    def __init__(self, S=None, Q=None, P=None, log=False, stationarity=False):
        self.S = S
        self.P = P
        self.Q = Q
        self.log = log
        self.stationarity = stationarity

    def setLog(self, log):
        self.log = log

    def setStationarity(self, stat):
        self.stationarity = stat

    def setStates(self, S):
        self.S = S

    def setObservationModel(self, P):
        self.P = P

    def setTransitionModel(self, Q):
        self.Q = Q   

    def Qlog(self, s1, s2, k, track):
        q = self.Q(s1, s2, k, track)
        if not (self.log):
            q = math.log(q + 1e-300)
        return q

    def Plog(self, s, y, k, track):
        p = self.P(s, y, k, track)
        if not (self.log):
            p = math.log(p + 1e-300)
        return p 	

    # ------------------------------------------------------------
    # Internal function to get all observations at epoch k in a 
    # track, from a list of analytical feature names (obs) and a
    # mode if retrieved values must be converted to positions
    # ------------------------------------------------------------
    def __getObs(self, track, obs, k, mode):
    
        y = track.getObsAnalyticalFeatures(obs,k)
        
        if mode == MODE_OBS_AS_2D_POSITION:    
            if len(y) < 2:
                print("Error: wrong number of observations in HMM to form 2D position")
                exit()
            ytemp = [utils.makeCoords(y[0], y[1], 0.0, track.getSRID())]
            for remain in range(2,len(y)):
                ytemp.append(y[remain])
            y = ytemp
        if mode == MODE_OBS_AS_3D_POSITION:     
            if len(y) < 3:
                print("Error: wrong number of observations in HMM to form 3D position")
                exit()
            ytemp = [utils.makeCoords(y[0], y[1], y[2], track.getSRID())] 
            for remain in range(3,len(y)):
                ytemp.append(y[remain])
            y = ytemp

        return utils.unlistify(y)

    # ------------------------------------------------------------
    # Main function of HMM object, to estimate (decode) the 
    # maximum a posteriori sequence of states given observations
    # Inputs:
    #   - track: the track on which estimation is performed
    #   - obs: the name of an analytical feature (may also a list 
    #     of analytical feature names for multi-dimensional HMM)
    #     All the analytical features listed must be in the track
    #   - mode: to specify how observations are used
    #        - MODE_OBS_AS_SCALAR: list of values (default)
    #        - MODE_OBS_AS_2D_POSITION: the first two fields 
    #          of  obs are used to make a Coords object. 
    #          Z component is set to 0 as default.
    #        - MODE_OBS_AS_3D_POSITION: the first three fields
    #          of obs are used to make a Coords object
    #     For MODE_OBS_AS_2D_POSITION and MODE_OBS_AS_3D_POSITION
    #     modes, coordinates SRID is the same as track SRID.
    # ------------------------------------------------------------
    def estimate(self, track, obs, log=False, mode=MODE_OBS_AS_SCALAR, verbose=True):
        
	    # -----------------------------------------------
        # Preprocessing
        # -----------------------------------------------	
        print("Compilation of states on track")
        N = len(track); STATES = []
        for k in range(N):
            STATES.append(self.S(track, k))
			
        TAB_MRK = []; TAB_VAL = []; 
        print("Cost and marker matrix initialization")
        for k in range(N):
            TAB_MRK.append([0]*len(STATES[k]))
            TAB_VAL.append([0]*len(STATES[k]))
            
        print("Compilation of observations on track")
        OBS = []
        for k in range(N):
            OBS.append(self.__getObs(track, obs, k, mode))
   
        for l in range(len(TAB_MRK[0])):
            TAB_MRK[0][l] = -1
            TAB_VAL[0][l] =  -self.Plog(STATES[0][l],OBS[0],0,track)
	
	    # -----------------------------------------------
        # Forward step
        # -----------------------------------------------		
        print("Optimal sequence computation")
        for k in range(1, N):
            print("Epoch", str(k+1)+"/"+str((len(TAB_MRK))), " ("+str(len(TAB_MRK[k]))+" states)")
            y  = OBS[k]
            for l in progressbar.progressbar(range(len(TAB_MRK[k]))):
                best_val = 1e300
                best_ant = 0
                s2 = STATES[k][l]
                for m in range(len(TAB_MRK[k-1])):
                    s1 = STATES[k-1][m]
                    val  = -self.Qlog(s1,s2,k-1,track) + TAB_VAL[k-1][m]
                    if val < best_val:
                        best_val = val
                        best_ant = m
                TAB_MRK[k][l] = best_ant
                TAB_VAL[k][l] = best_val - self.Plog(s2,y,k,track)			
        
		# -----------------------------------------------
        # Backward step	
		# -----------------------------------------------
        track.createAnalyticalFeature("hmm_output")
        idk = np.argmin(TAB_VAL[-1])
        for k in range(N-1,-1,-1):
            track.setObsAnalyticalFeature("hmm_output", k, STATES[k][idk])
            track[k].position = STATES[k][idk]
            idk = TAB_MRK[k][idk]
 
        return track["hmm_output"]