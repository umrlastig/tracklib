# --------------------------- Filtering ---------------------------------------
# Class to manage filtering of GPS tracks
# -----------------------------------------------------------------------------

import numpy as np

import tracklib.algo.Dynamics as Dynamics

FILTER_LOW_PASS = 0
FILTER_HIGH_PASS = 1

FILTER_TEMPORAL = 0
FILTER_SPATIAL = 1

FILTER_X = ["x"]
FILTER_Y = ["y"]
FILTER_Z = ["z"]
FILTER_XY = ["x","y"]
FILTER_XZ = ["x","z"]
FILTER_YZ = ["y","z"]
FILTER_XYZ = ["x","y","z"]

KALMAN_FORWARD = 0
KALMAN_BACKWARD = 1
KALMAN_COMBINED = 2

# -----------------------------------------
# Global variables for Markov filtering
# -----------------------------------------
sig = 0
res = 0
# -----------------------------------------

# --------------------------------------------------------------------------
# TO DO: Gaussian process filtering
# --------------------------------------------------------------------------
def gaussianProcess(track):
    return None
	
# --------------------------------------------------------------------------
# TO DO: Wavelet filtering (Donoho and Johnstone)
# --------------------------------------------------------------------------
def waveletTransform(track):
    return None
def waveletFiltering(track):
    return None
	
# --------------------------------------------------------------------------
# TO DO: Karhunen-Loeve filtering
# --------------------------------------------------------------------------
def KLBasis(TrackCollection):
    return None
def KLTransform(track):
    return None	
def KLFiltering(track):
    return None	
	
# --------------------------------------------------------------------------
# Filtering with Unscented Kalman filter based on speed regularization
# Inputs:
#    - track: a track to filter
#    - sigma: Positional standard deviation (in ground units)
#    - speed: standard deviation of speed
#    - speed_af: AF field containing speeds (optional)
#    - mode : forward, backward or combined
# Important: tracks are assumed to be sampled at constant time frequency
# --------------------------------------------------------------------------
def __kalman(track, sigma, speed_std, speed_af=None, verbose=True):

    track = track.copy()
    dt = abs(track.frequency())

    # -----------------------------------------------------
	# Mode speed recorded in AF field
	# -----------------------------------------------------
    if not (speed_af is None):

        F = lambda x: Dynamics.DYN_MAT_2D_CST_SPEED(dt) @ x      
        H = lambda x: np.array([[x[0,0]], [x[1,0]], [(x[2,0]**2 + x[3,0]**2)**0.5]])           
        
        Q = np.eye(4,4); Q[2,2] = 0; Q[3,3] = 0
        R = sigma**2*np.eye(3,3); R[2,2] = speed_std**2;
        X0 = np.array([[track[0].position.getX()],[track[0].position.getY()],[0],[0]])
        P0 = sigma**2*np.eye(4,4)                                           
        
        UKF = Dynamics.Kalman(spreading=1)
        UKF.setTransition(F, Q)                        
        UKF.setObservation(H, R)                        
        UKF.setInitState(X0, P0)  

        UKF.estimate(track, ["x", "y", speed_af], verbose=verbose) 
		
	# -----------------------------------------------------
	# Mode prior information on speed based on std value
	# -----------------------------------------------------
    else:

        F = lambda x: x                                 # Transition model
        H = lambda x: np.array([[x[0,0]],[x[1,0]]])     # Observation model
        
        Q = (dt*speed_std)**2*np.eye(2,2)               # Transition covariance
        R = sigma**2*np.eye(2,2)                        # Observation covariance
        
        p0 = track[0].position                          # First position
        X0 = np.array([[p0.getX()],[p0.getY()]])        # Initial state
        P0 = sigma**2*np.eye(2,2)                       # Initial covariance
        
        UKF = Dynamics.Kalman(spreading=1)
        UKF.setTransition(F, Q)                         # Dynamic model
        UKF.setObservation(H, R)                        # Observation model
        UKF.setInitState(X0, P0)                        # Initialization
        
        UKF.estimate(track, ["x", "y"], verbose=verbose)              
    
    for i in range(len(track)):
        track[i].position.setX(track.getObsAnalyticalFeature("kf_0", i))
        track[i].position.setY(track.getObsAnalyticalFeature("kf_1", i))
  
    return track	

def Kalman(track, sigma, speed_std, speed_af=None, mode=KALMAN_FORWARD, verbose=True):
    if mode == KALMAN_FORWARD:
       return __kalman(track, sigma, speed_std, speed_af, verbose)
    if mode == KALMAN_BACKWARD:  
       return __kalman(track.reverse(), sigma, speed_std, speed_af, verbose).reverse()
    if mode == KALMAN_COMBINED:
        track_fwd = Kalman(track, sigma, speed_std, speed_af, mode=KALMAN_FORWARD,  verbose=verbose)
        track_bwd = Kalman(track, sigma, speed_std, speed_af, mode=KALMAN_BACKWARD, verbose=verbose)
        for k in range(len(track_fwd)):
            x_fusion = 0.5*track_fwd[k].position.getX() + 0.5*track_bwd[k].position.getX()
            y_fusion = 0.5*track_fwd[k].position.getY() + 0.5*track_bwd[k].position.getY()
            track_fwd[k].position.setX(x_fusion)
            track_fwd[k].position.setY(y_fusion)
        return track_fwd
	
# --------------------------------------------------------------------------
# Filtering with Markov process based on speed regularization
# Inputs:
#    - track: a track to filter
#    - sigma: Positional standard deviation (in ground units)
#    - speed: a function describing the speed distribution. It is a 3-valued 
#      function, where f(v,k,t) describes the (possibly non-normalized) 
#      probability value that track t is moving with speed v at epoch k. It 
#      may be (if necessary) computed with track analytical features or 
#      global external data such as DTM slope.
#    - resolution: search grid resolution (in ground units). Note that the 
#      number N of states varies as the inverse of O(r^2), with r being the 
#      search grid resolution, while the time complexity of the overall 
#      algorithm is O(n^2). Therefore, the time required to compute a 
#      solution is proportional to the 4th power of (1/r). A resolution 
#      twice thinner implies 16 times longer computation. As thumb rule, the 
#      resoluton should be chosen around sigma/3, where sigma is the 
#      positional standrad deviation (in ground units). So, for a typical 
#      (standard positioning) GPS receiver with 3 m error, a search grid 
#      resolution of 1 m provides a thin modelization.    
# --------------------------------------------------------------------------
def __Markov_S(track, i):
    etats = []
    N = int(2*sig/res)+1
    for kx in range(-N,N+1):
        for ky in range(-N,N+1):
            p = track[i].position.copy()
            p.translate(res*kx, res*ky)
            etats.append(p)
    return etats 
	
def __Markov_Plog(pi, y, k, track):
    return -(pi.distance2DTo(y)/20)**2
	
def MarkovRegularization(track, sigma, speed, resolution):
    global res, sig
    sig = sigma
    res = resolution
    model = Dynamics.HMM()
    model.setStates(__Markov_S)
    model.setTransitionModel(speed)
    model.setObservationModel(__Markov_Plog)
    model.setLog(True)
    model.estimate(track, obs=["x","y","z"], mode=Dynamics.MODE_OBS_AND_STATES_AS_3D_POSITIONS)

# --------------------------------------------------------------------------
# Generic method to filter a track with Fast Fourier Transforms
# Mode :
#     - FILTER_TEMPORAL (0)
#     - FILTER_SPATIAL (1)
# Type : 
#     - FILTER_LOW_PASS (0) or "low" for low-pass filter 
#     - FILTER_HIGH_PASS (1) or "high" for high pass filter
# Cut-off frequency fc :
#     - All frequencies above (resp. below) fc are filtered for low-pass 
# Dimension dim : FILTER_X, FILTER_Y, FILTER_Z, FILTER_XY, FILTER_YZ, 
# FILTER_XY or FILTER XYZ depending in the number of dimensions to filter
# (resp.) high-pass filter. May also be a list of analytical features names
# Spectral filtering is applied to a regularly sampled track. If track 
# is temporally (resp. spatially) sampled, cut off frequencies are 
# given in Hz or points/sec (resp. points/m or points/ground units).
# Note that pass-band and cut-band filters may be obtained by calling filter 
# function twice sequentially with FILTER_LOW_PASS and FILTER_HIGH_PASS.
# --------------------------------------------------------------------------
def filter(track, fc, mode = FILTER_TEMPORAL, type = FILTER_LOW_PASS, dim=FILTER_XYZ):

	output = track.copy()
	fs = output.frequency(mode)
		
	for af in dim:
	
		F = np.fft.fft(track.getAnalyticalFeature(af))

		N = int(F.shape[0]/2)
		Nc = int(N*fc)
		
		if (type == FILTER_LOW_PASS):
			F[Nc:F.shape[0]-Nc] = 0;
		else:
			F[1:Nc] = 0; F[F.shape[0]-Nc:F.shape[0]] = 0;
			
		f = np.real(np.fft.ifft(F))

		for i in range(len(output)):
			output.setObsAnalyticalFeature(af, i, f[i])
			
	return output