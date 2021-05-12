# --------------------------- Cinematics --------------------------------------
# Class to manage cinematic computations on GPS tracks
# -----------------------------------------------------------------------------

import math
import progressbar
import numpy as np

import tracklib.core.Utils as utils


MODE_OBS_AS_SCALAR = 0
MODE_OBS_AS_2D_POSITIONS = 1
MODE_OBS_AS_3D_POSITIONS = 2
MODE_OBS_AND_STATES_AS_2D_POSITIONS = 3
MODE_OBS_AND_STATES_AS_3D_POSITIONS = 4
MODE_STATES_AS_POSITIONS = 5

MODE_VERBOSE_NONE = 0
MODE_VERBOSE_ALL = 1
MODE_VERBOSE_PROGRESS = 2
MODE_VERBOSE_PROGRESS_BY_EPOCH = 3

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
        
        if mode in [MODE_OBS_AS_2D_POSITIONS, MODE_OBS_AND_STATES_AS_2D_POSITIONS]:    
            if len(y) < 2:
                print("Error: wrong number of observations in HMM to form 2D position")
                exit()
            ytemp = [utils.makeCoords(y[0], y[1], 0.0, track.getSRID())]
            for remain in range(2,len(y)):
                ytemp.append(y[remain])
            y = ytemp
        if mode in [MODE_OBS_AS_3D_POSITIONS, MODE_OBS_AND_STATES_AS_3D_POSITIONS]:     
            if len(y) < 3:
                print("Error: wrong number of observations in HMM to form 3D position")
                exit()
            ytemp = [utils.makeCoords(y[0], y[1], y[2], track.getSRID())] 
            for remain in range(3,len(y)):
                ytemp.append(y[remain])
            y = ytemp

        return utils.unlistify(y)
        
    # Method to deal with computation trace    
    def printTrace(self, message, importance, level):
        if level in importance:
            print(message)
            
    def printSeparator(self, importance, level, type):
        if level in importance:
            if type == 0:
                style = "--------------------------------------"
            if type == 1:
                style = "======================================"
            print(style+style)


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
    #        - MODE_OBS_AS_3D_POSITIONS: the first three fields
    #          of obs are used to make a Coords object
    #     For MODE_OBS_AS_2D_POSITIONS / MODE_OBS_AS_3D_POSITIONS
    #     modes, coordinates SRID is the same as track SRID.
    # ------------------------------------------------------------
    def estimate(self, track, obs, log=False, mode=MODE_OBS_AS_SCALAR, verbose=MODE_VERBOSE_PROGRESS_BY_EPOCH):
        
        # -----------------------------------------------
        # Preprocessing
        # -----------------------------------------------
        self.printTrace("Compilation of states on track", [1,2,3], verbose)
            
        N = len(track); STATES = []
        for k in range(N):
            STATES.append(self.S(track, k))
            
        TAB_MRK = []; TAB_VAL = []; 
        
        self.printTrace("Cost and marker matrix initialization", [1,2,3], verbose)
        
        for k in range(N):
            TAB_MRK.append([0]*len(STATES[k]))
            TAB_VAL.append([0]*len(STATES[k]))
             
        self.printTrace("Compilation of observations on track", [1,2,3], verbose)

        OBS = []
        for k in range(N):
            OBS.append(self.__getObs(track, obs, k, mode))
   
        for l in range(len(TAB_MRK[0])):
            TAB_MRK[0][l] = -1
            TAB_VAL[0][l] =  -self.Plog(STATES[0][l],OBS[0],0,track)
    
        # -----------------------------------------------
        # Forward step
        # -----------------------------------------------    
        self.printTrace("Optimal sequence computation", [1,2,3], verbose)        

        EPOCHS = range(1, N)
        if verbose == MODE_VERBOSE_PROGRESS:
            EPOCHS = progressbar.progressbar(EPOCHS)
        for k in EPOCHS:

            y  = OBS[k]
            STATES_TO_TEST = range(len(TAB_MRK[k]))

            message = "Epoch "+str(k+1)+"/"+str((len(TAB_MRK)))+" ("+str(len(TAB_MRK[k]))+" states)"
            self.printTrace(message, [1,3], verbose)

            if (verbose == MODE_VERBOSE_PROGRESS_BY_EPOCH):
                STATES_TO_TEST = progressbar.progressbar(STATES_TO_TEST)

            for l in STATES_TO_TEST:

                best_val = 1e300
                best_ant = 0
                s2 = STATES[k][l]

                for m in range(len(TAB_MRK[k-1])):

                    s1 = STATES[k-1][m]
                    q = -self.Qlog(s1,s2,k-1,track)
                    val  = q + TAB_VAL[k-1][m]

                    message  = "State "+str(l)+"/"+str(k-1)+" "+str(s1)+" --> " 
                    message += "state "+str(m)+"/"+str(k)  +" "+str(s2) 
                    message += " TRANSITION COST = " + str(q)
                    self.printTrace(message, [1], verbose)

                    if val < best_val:
                        best_val = val
                        best_ant = m

                p = -self.Plog(s2,y,k,track)
                TAB_MRK[k][l] = best_ant
                TAB_VAL[k][l] = best_val + p

                message  = "State "+str(l)+"/"+str(k-1)+" "+str(s1)+" to "
                message += str(y)+"  OBS COST = "+str(p)
                self.printTrace(message, [1], verbose)
                self.printSeparator([1], verbose, 0)

            self.printSeparator([1], verbose, 1)    
        
        # -----------------------------------------------
        # Backward step    
        # -----------------------------------------------
        self.printTrace("Backward reconstruction phase", [1,2,3], verbose) 
        track.createAnalyticalFeature("hmm_inference")
        track.createAnalyticalFeature("hmm_cost")
        idk = np.argmin(TAB_VAL[-1])
        for k in range(N-1,-1,-1):
            self.printTrace("Step "+str(k)+": state "+str(idk)+" (cost: "+str(TAB_VAL[k][idk])+")", [1], verbose)
            track.setObsAnalyticalFeature("hmm_inference", k, STATES[k][idk])
            track.setObsAnalyticalFeature("hmm_cost", k, TAB_VAL[k][idk])
            if mode in [3,4,5]:
                track[k].position = STATES[k][idk]
            idk = TAB_MRK[k][idk]

        self.printSeparator([1], verbose, 1)  