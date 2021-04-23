# --------------------------- Filtering ---------------------------------------
# Class to manage filtering of GPS tracks
# -----------------------------------------------------------------------------

import sys
import numpy as np

import tracklib.core.Track as Track
import tracklib.core.Utils as utils
import tracklib.core.Operator as Operator

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
# TO DO: Kalman filtering
# --------------------------------------------------------------------------
def Kalman(track):
    return None

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