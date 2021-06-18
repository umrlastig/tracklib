# ---------------------------- Mapping ----------------------------------------
# Class to manage mapping of GPS tracks on geographic features
# -----------------------------------------------------------------------------
import math
import progressbar
import numpy as np

import tracklib.core.Track as Track
from tracklib.core.Operator import Operator


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


def mapOn(track, reference, TP1=[], TP2=[], init=[], apply=True, N_ITER_MAX=20, NPTS=30, mode="2D", verbose=True):

    '''Geometric affine transformation to align two tracks with diferent
	coordinate systems. For "2D" mode, coordinates must be ENU or Geo. For 
	"3D" mode, any type of coordinates is valid. In general, it is recommended 
	to avoid usage of non-metric Geo coordinates for mapping operation, since 
	it is relying on an isotropic error model. Inputs:
	   - reference: another track we want to align on or a list of points
	   - TP1         : list of tie points indices (relative to track self)
	   - TP2         : list of tie points indices (relative to track)
       - init        : "initial guess" vector : [scale, tx, ty, rotation angle]
	   - N_ITER_MAX  : maximal number of iterations (in least squares or ICP)
       - apply       : boolean value to specify if estimated transfo must be performed
	   - mode        : could be "2D" (default) or "3D"
       - NPTS        : integer specifying number of points to consider (for ICP only)
    If TP2 is not specified, it is assumed equal to TP1.
	TP1 and TP2 must have same size. Adjustment is performed with least squares.
	The general transformation from point X to point X' is provided below:
	                         X' = kRX + T
	with: k a positive real value, R a 2D or 3D rotation matrix and T a 2D or 
	3D translation vector. Transformation parameters are returned in standard 
	output in the following format: [theta, k, tx, ty] (theta in radians)
	Track argument may also be replaced ny a list of points.
	If TP1 is an empty list or if it is not specified, adjustment is performed 
	with iterative closest point (ICP) algorithm, to solve both the transfo and
	the data association problems in a single framework. This method requires 
	however that the "initial guess" (i.e. scale difference and rotation between 
	both datasets) be not too far from reality, in order to reach a good solution.
	For standard least squares, time complexity of the method is O(n^2) with n 
	the number of points used for data matching. For ICP, data association step 
	is O(n^2) and least squares resolution is O(n^2) hence an overall complexity 
	equal to N_ITER_MAX * O(NPTS^2). In general NPTS = 30 performs fair enough.
	Note that mapOn does not handle negative determinant (symetries not allowed)
	'''   
	
    if (len(TP1) == 0):   # Recursive solution
		
        track_copy = track.copy()
		
        # Initial guess (if provided)
        if (len(init) == 4):
            track_copy.rotate(init[3,0])
            track_copy.scale(init[0,0])
            track_copy.translate(init[1,0],init[2,0])	

        # Match data by rough scale factor
        track_copy.compute_abscurv(); reference.compute_abscurv()
        track_copy.operate(Operator.DIFFERENTIATOR, "abs_curv", "ds")
        reference.operate( Operator.DIFFERENTIATOR, "abs_curv", "ds")
        f = reference.operate(Operator.AVERAGER, "ds")/track_copy.operate(Operator.AVERAGER, "ds")
        track_copy.scale(f)

        # Match data by rough translation
        t = track_copy.getCentroid() - reference.getCentroid();
        track_copy.translate(t.getX(), t.getY())
		
        resolution_steps = range(N_ITER_MAX);
        if verbose:
            resolution_steps = progressbar.progressbar(resolution_steps)

		# Iterative closest point
        for step in resolution_steps:

            # -------------------------------------------------
            # Data association step
            # -------------------------------------------------
            TP1 = []; TP2 = [];
            for i in range(0, len(track_copy), (int)(len(track_copy)/NPTS)):
                dmin =  1e300
                jmin = 0
                for j in range(len(reference)):
                    dist = track_copy[i].position.distance2DTo(reference[j].position)
                    if dist < dmin:
                        dmin = dist
                        jmin = j
                TP1.append(i); TP2.append(jmin)
        
            # -------------------------------------------------
            # Recursive data adjustment step
            # -------------------------------------------------
            mapOn(track_copy, reference, TP1, TP2, N_ITER_MAX=1, verbose=False)
		
        # Data association application
        track.createAnalyticalFeature("pair", -1)
        for k in range(len(TP1)):
            track.setObsAnalyticalFeature("pair", TP1[k], TP2[k])		
		
        # Adjustement application
        return mapOn(track, reference, TP1, TP2, apply=apply, N_ITER_MAX=20, verbose=verbose)
		

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

    if isinstance(reference, Track.Track):
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
	
    if apply:
        track.rotate(X[3,0])
        track.scale(X[0,0])
        track.translate(X[1,0],X[2,0])

    return [X[3,0], X[0,0], X[1,0], X[2,0]]
