# --------------------------- Comparison --------------------------------------
# Class to manage comparisons of GPS tracks
# -----------------------------------------------------------------------------

import sys
import progressbar
import numpy as np
import matplotlib.pyplot as plt

import tracklib.algo.Interpolation as Interpolation

# ------------------------------------------------------------
# Difference profile plot
# ------------------------------------------------------------	
def plotDifferenceProfile(profile, track2, af_name="pair"):
    for i in range(profile.size()):
        x1 = profile.getObs(i).position.getX()
        y1 = profile.getObs(i).position.getY()
        x2 = track2.getObs(profile.getObsAnalyticalFeature(af_name, i)).position.getX()
        y2 = track2.getObs(profile.getObsAnalyticalFeature(af_name, i)).position.getY()
        plt.plot([x1,x2],[y1,y2],'g--',linewidth=0.5)

# ------------------------------------------------------------
# Profile of difference between two traces : t2 - t1
# Two possible modes: 
# - NN (Nearest Neighbour): O(n^2) time and O(n) space
# - DTW (Dynamic Time Warping): O(n^3) time and O(n^2) space
# Output is a track objet, with an analytical feature diff
# containing shortest distance of each point of track t1, to 
# the points of track t2. We may get profile as a list with 
# output.getAbsCurv() and output.getAnalyticalFeature("diff")
# The selected candidate in registerd in AF "pair"
# Set "ends" parameter to True to force end points to meet
# p is Minkowski's exponent for distance computation. Default 
# value is 1 for summation of distances, 2 for least squares 
# solution and 10 for an approximation of Frechet solution. 
# ------------------------------------------------------------		
def differenceProfile(track1, track2, mode="NN", ends=False, p=1):

    output = track1.copy()
    output.createAnalyticalFeature("diff");
    output.createAnalyticalFeature("pair");
 
    # --------------------------------------------------------
    # Nearest Neighbor (NN) algorithm
    # --------------------------------------------------------
    if mode == "NN":
        for i in range(output.size()):
            val_min = sys.float_info.max
            id_min = 0
            for j in range(track2.size()):
                distance = output.getObs(i).distance2DTo(track2.getObs(j))
                if distance < val_min:
                    val_min = distance
                    id_min = j
            output.setObsAnalyticalFeature("diff", i, val_min)
            output.setObsAnalyticalFeature("pair", i, id_min)

    # --------------------------------------------------------
    # Dynamic time warping (DTW) algorithm
    # --------------------------------------------------------
    if mode == "DTW":
	
        p = max(min(p,15),1e-2)
        
        track1 = track1.copy()
        track2 = track2.copy()
		
        # Forming distance matrix
        D = np.zeros((track1.size(), track2.size()))
        for i in range(track1.size()):
            for j in range(track2.size()):
                D[i,j] = track1.getObs(i).distance2DTo(track2.getObs(j))**p
        
        # Optimal path with dynamic programming
        T = np.zeros((track1.size(), track2.size()))
        M = np.zeros((track1.size(), track2.size()))
        T[0,0] = D[0,0]
        M[0,0] = -1
		
		# Forward step
        for i in progressbar.progressbar(range(1,T.shape[0])):
            T[i,0] = T[i-1,0] + D[i,0]
            M[i,0] = 0
            for j in range(1, T.shape[1]):
                K = D[i,0:(j+1)]
                for k in range(j-1,-1,-1):
                    K[k] = K[k] + K[k+1]
                V = T[i-1,0:(j+1)] + K
                M[i,j] = np.argmin(V) 
                T[i,j] = V[int(M[i,j])]
                
        
        # Backward step
        S = [0]*(track1.size())
        if ends:
            S[track1.size()-1] = int(M[track1.size()-1,track2.size()-1]) 
        else:
            S[track1.size()-1] = np.argmin(T[track1.size()-1,:])
        for i in range(track1.size()-2, -1, -1):
            S[i] = int(M[i+1,S[i+1]])
			
        #print((T[track1.size()-1, S[track1.size()-1]] / track1.size())**(1.0/p))
		
        #plt.plot(S, 'r-')			
        #plt.imshow(M)

        for i in range(track1.size()):
            x1 = track1.getObs(i).position.getX()
            y1 = track1.getObs(i).position.getY()
            x2 = track2.getObs(S[i]).position.getX()
            y2 = track2.getObs(S[i]).position.getY()
            d = track1.getObs(i).distance2DTo(track2.getObs(S[i]))
            output.setObsAnalyticalFeature("diff", i, d)
            output.setObsAnalyticalFeature("pair", i, S[i])

    output.compute_abscurv()
    return output

def synchronize(self, track):
        
    '''Resampling of 2 tracks with linear interpolation
    on a common base of timestamps
    track: track to synchronize with'''
    
    Interpolation.synchronize(self, track)

def compare(track1, track2):

    '''Comparison of 2 tracks. Tracks are interpolated
    linearly on a common base of timestamps
    track: track to compare with'''
    
    trackA = track1.copy()
    trackB = track2.copy()
    
    track2.synchronize(track3)
    
    rmse = 0
    for i in range(trackA.size()):
        rmse += trackA.getObs(i).distanceTo(trackB.getObs(i))**2
    
    return math.sqrt(rmse/trackA.size())