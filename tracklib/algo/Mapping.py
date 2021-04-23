# ---------------------------- Mapping ----------------------------------------
# Class to manage mapping of GPS tracks on geographic features
# -----------------------------------------------------------------------------

import sys
import numpy as np

import tracklib.core.Track as Track
import tracklib.core.Utils as utils
import tracklib.core.Operator as Operator


# --------------------------------------------------------------------------
# TO DO: map-matching on a network
# --------------------------------------------------------------------------
def mapOnNetwork(trackCollecion, network):
    return None

# --------------------------------------------------------------------------
# TO DO: map-matching on raster
# --------------------------------------------------------------------------
def mapOnRaster(track, grid):
    return None


def mapOn(track, reference, TP1, TP2=[], init=[], N_ITER_MAX=20, mode="2D", verbose=True):

    '''Geometric affine transformation to align two tracks with diferent
	coordinate systems. For "2D" mode, coordinates must be ENU or Geo. For 
	"3D" mode, any type of coordinates is valid. In general, it is recommended 
	to avoid usage of non-metric Geo coordinates for mapping operation, since 
	it is relying on an isotropic error model. Inputs:
	   - reference: another track we want to align on or a list of points
	   - TP1: list of tie points indices (relative to track self)
	   - TP2: list of tie points indices (relative to track)
	   - mode: could be "2D" (default) or "3D"
    if TP2 is not specified, it is assumed equal to TP1.
	TP1 and TP2 must have same size. Adjustment is performed with least squares.
	The general transformation from point X to point X' is provided below:
	                         X' = kRX + T
	with: k a positive real value, R a 2D or 3D rotation matrix and T a 2D or 
	3D translation vector. Transformation parameters are returned in standard 
	output in the following format: [theta, k, tx, ty] (theta in radians)
	Track argument may also be replaced ny a list of points.
	Note that mapOn does not handle negative determinant (symetries not allowed)
	'''   

    if (mode == "3D"):
        print("Mode 3D is not implemented yet")
        exit()	

    if (len(init) == 0):
        init = [0,1,0,0]		
	
    if (len(TP2) == 0):
        TP2 = TP1
    if not (len(TP1) == len(TP2)):
        print("Error: tie points lists must have same size")
        exit()
		
    P1 = [track.getObs(i).position.copy() for i in TP1]
	
    if isinstance(reference, Track):
        P2 = [reference.getObs(i).position.copy() for i in TP2]
    else:
        P2 = reference
	
    n = len(P1)

    if verbose:
        print("-----------------------------------------------------------------")
        print("NUMBER OF TIE POINTS: " + str(len(TP1)))
        print("-----------------------------------------------------------------")			
        N = int(math.log(track.size())/math.log(10))+1
        for i in range(len(TP1)):
            message = "POINT " + ('{:0'+str(N)+'d}').format(TP1[i]) + "   "  
            message += str(track.getObs(TP1[i]).timestamp) + "   ERROR = "
            message += str('{:10.2f}'.format(P1[i].distance2DTo(P2[i]))) + " m"
            print(message)
        print("-----------------------------------------------------------------")
		
    J = np.zeros((2*n, 4))
    B = np.zeros((2*n, 1))
    X = np.matrix([init[1],init[0],init[2],init[3]]).transpose()
	
	# Iterations
    for iter in range(N_ITER_MAX):
    
        # Current parameters
        k  = X[0,0]        
        tx = X[1,0]
        ty = X[2,0]
        a  = X[3,0]; ca = math.cos(a); sa = math.sin(a)			
        
        for i in range(0,2*n,2):
            x1 = P1[int(i/2)].getX(); y1 = P1[int(i/2)].getY()
            x2 = P2[int(i/2)].getX(); y2 = P2[int(i/2)].getY()
            x2_th = k*(ca*x1-sa*y1)+tx
            y2_th = k*(sa*x1+ca*y1)+ty		
            J[i,0]   = ca*x1-sa*y1;  J[i,1]   = 1;  J[i,2]   = 0;   J[i,3]   = -k*(sa*x1+ca*y1);   B[i]   = x2-x2_th
            J[i+1,0] = sa*x1+ca*y1;  J[i+1,1] = 0;  J[i+1,2] = 1;   J[i+1,3] = +k*(ca*x1-sa*y1);   B[i+1] = y2-y2_th
        	
        dX = np.linalg.solve(J.transpose()@J, J.transpose()@B)
        X = X+dX
		
        cv_param = max(max(max(dX[0,0]*1e4, dX[1,0]*1e4), dX[2,0]*1e4),  dX[3,0]*1e4)
        if (cv_param < 1):
            break               
        
        if verbose:
            N = int(math.log(N_ITER_MAX-1)/math.log(10)) + 1
            message = "ITERATION " + ('{:0'+str(N)+'d}').format(iter) + "  "
            message += "RMSE = " + '{:10.5f}'.format(math.sqrt(B.transpose()@B/(2*n))) + " m    "
            message += "MAX = " + '{:10.5f}'.format(np.max(B)) + " m    "
            print(message)
			
    if verbose:
        print("-----------------------------------------------------------------")
        print("CONVERGENCE REACHED AFTER " + str(iter) + " ITERATIONS")
        glob_res = 0.0
        for l in range(0,2*n,2):
            res = math.sqrt(B[l]**2+B[l+1]**2)
            glob_res += res
            message = "RESIDUAL (2D) POINT " + str(int(l/2)) + ":  "
            message += '{:4.3f}'.format(res) + " m"
            print(message)
        print("GLOBAL 2D RESIDUAL ON TIE POINTS: " + '{:5.3f}'.format(glob_res/n) + " m")
        print("-----------------------------------------------------------------")
        message = "Theta = " + '{:3.2f}'.format(X[3,0]) + " rad   k = " + '{:5.3f}'.format(X[0,0])
        message += "  Tx = " + '{:8.3f}'.format(X[1,0]) + " m  Ty = " + '{:8.3f}'.format(X[2,0]) + " m"
        print(message)
        print("-----------------------------------------------------------------")
	
    track.rotate(X[3,0])
    track.scale(X[0,0])
    track.translate(X[1,0],X[2,0])

    return [X[3,0], X[0,0], X[1,0], X[2,0]]
