# --------------------------- Analytics ---------------------------------------
# Class to manage general operations on a track
# -----------------------------------------------------------------------------
import sys
import math
import numpy as np
import random
import progressbar
import matplotlib.pyplot as plt

from tracklib.core.Obs import Obs
from tracklib.core.Coords import ENUCoords
from tracklib.core.GPSTime import GPSTime

import tracklib.core.core_utils as utils
import tracklib.core.Track as core_Track
import tracklib.core.Operator as Operator
import tracklib.core.TrackCollection as TrackCollection

import tracklib.algo.Interpolation as interp




def __right(a,b,c):
    return ((a == c) or (b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]) < 0)
            

def convexHull(track):
	'''
	Finds the convex hull of a track, returned as 
	a list of x an y coordinates : [x1, y1, x2, y2,...]
	Computation is performed with Jarvis march algorithm
	with O(n^2) time complexity. It may be needed to resample
	track if computation is too long.'''
	
	T = []
	for i in range(len(track)):
		T.append([track[i].position.getX(), track[i].position.getY()])
		
	X = [p[0] for p in T]
	H = [X.index(min(X))]

	while((len(H) < 3) or (H[-1] != H[0])):
		H.append(0)
		for i in range(len(T)):
			if not (__right(T[H[-2]], T[H[-1]], T[i])):
				H[-1] = i
   
	return (H)


def diameter(track):
	'''
	Finds longest distance between points on track 
	The two selected points are returned in a vector
	along with the minimal distance : [min_dist, p1, p2].
	Exhaustive search in O(n^2) time complexity'''
	
	dmax = 0
	idmax = [0,0]
	
	for i in range(len(track)):
		for j in range(len(track)):
			d = track.getObs(i).distance2DTo(track.getObs(j))
			if d > dmax:
				dmax = d
				idmax = [i,j]
	return [dmax, idmax[0], idmax[1]]
	
	
def __circle(p1, p2=None, p3=None):
	''' Finds circle through 1, 2 or 3 points
	Returns [C, R]'''
	if not isinstance(p1, ENUCoords):
		print("Error: ENU coordinates are required for min circle computation")
		exit()
	if p2 is None:
		return [p1, 0.0]
	if p3 is None:
		centre = p1+p2
		centre.scale(0.5)
		return [centre, p1.distance2DTo(p2)/2]
		
	if (p1.distance2DTo(p2) == 0):
		p2.setX(p2.getX()+random.random()*1e-10)
		p2.setY(p2.getY()+random.random()*1e-10)
			
	if (p1.distance2DTo(p3) == 0):
		p3.setX(p3.getX()+random.random()*1e-10)
		p3.setY(p3.getY()+random.random()*1e-10)
		
	if (p2.distance2DTo(p3) == 0):
		p3.setX(p3.getX()+random.random()*1e-10)
		p3.setY(p3.getY()+random.random()*1e-10)
	
	C12 = __circle(p1, p2)
	C23 = __circle(p2, p3)
	C13 = __circle(p1, p3)
	CANDIDATS = []
	
	if (C12[0].distance2DTo(p3) < C12[1]):
		CANDIDATS.append(C12)
	if (C23[0].distance2DTo(p1) < C23[1]):
		CANDIDATS.append(C23)
	if (C13[0].distance2DTo(p2) < C13[1]):
		CANDIDATS.append(C13)

	if len(CANDIDATS) > 0:
		min = CANDIDATS[0][1]
		argmin = 0
		for i in range(len(CANDIDATS)):
			if CANDIDATS[i][1] < min:
				min = CANDIDATS[i][1]
				argmin = i
		return CANDIDATS[argmin]
		

	x = np.complex(p1.getX(), p1.getY())
	y = np.complex(p2.getX(), p2.getY())
	z = np.complex(p3.getX(), p3.getY())

	w = z-x; w /= y-x; c = (x-y)*(w-abs(w)**2)/2j/np.imag(w)-x
	centre = p1.copy(); 
	centre.setX(-np.real(c)); 
	centre.setY(-np.imag(c));	
	return [centre, np.abs(c+x)]
	
def __welzl(P, R):
	'''Finds minimal bounding circle with Welzl's algorithm'''
	
	P = P.copy()
	R = R.copy()
	
	if ((len(P) == 0) or (len(R) == 3)):
		if len(R) == 0:
			return [ENUCoords(0,0,0), 0]
		if len(R) == 1:
			return __circle(R[0])
		if len(R) == 2:
			return __circle(R[0], R[1])
		return __circle(R[0], R[1], R[2])
	id = random.randint(0,len(P)-1)
	
	p = P[id]
	P2 = []
	for i in range(len(P)):
		if i == id:
			continue
		P2.append(P[i])
	P = P2
	D = __welzl(P, R)
	if (p.distance2DTo(D[0]) < D[1]):
		return D
	else:
		R.append(p)
		return __welzl(P, R)
	
	
	
def plotCircle(S, color=[1,0,0,1]):
	'''Function to plot a circle from a vector:
	S = [Coords, radius], where Coords is ECEF, ECEF or GEO
	Needs to call plt.show() after this function'''	
	X = [0]*100
	Y = [0]*100
	for t in range(len(X)-1):
		X[t] = S[1]*math.cos(2*math.pi*t/len(X)) + S[0].getX()
		Y[t] = S[1]*math.sin(2*math.pi*t/len(Y)) + S[0].getY()
	X[len(X)-1] = X[0]
	Y[len(Y)-1] = Y[0]
	plt.plot(X, Y, '-', color=color)
	

def minCircle(track):
	'''
	Finds minimal bounding circle with Welzl's recursive 
	algorithm in O(n) complexity. Output is given as a list 
	[p, R], where p is a Coords object defining circle center
	and R is its radius. Due to recursion limits, only tracks 
	with fewer than 800 points can be processed'''	
	if not track.getSRID() == "ENU":
		print("Error: ENU coordinates are required for min circle computation")
		exit()
	if track.size() > 0.5*sys.getrecursionlimit():
		message  = "Error: too many points in track to compute minimal enclosing circle. "
		message += "Downsample track, or use \"sys.setrecursionlimit("
		message += str(int((2*track.size())/1000)*1000 + 1000)+") or higher\""
		print(message)
		exit()
	
	centre = track.getFirstObs().position.copy()
	
	P = [obs.position for obs in track]
	R = []
		
	return __welzl(P,R)
	
def minCircleMatrix(track):
	'''Computes matrix of all min circles in a track.
		M[i,j] gives the radius of the min circle enclosing 
		points in track from obs i to obs j (included)'''
	
	M = np.zeros((track.size(), track.size()))
	for i in range(track.size()):
		print(i, "/", track.size())
		for j in range(i, track.size()-1):
			M[i,j] = minCircle(track.extract(i,j))[1]
	M = M + np.transpose(M)
	return M
	
	
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

def plotStops(stops):
	for i in range(len(stops)):
		plotCircle([stops[i].position, stops["radius"][i]])
	
def removeStops(track, stops=None):	
	if stops is None:
		stops = extractStopsBis(track)
	output = track.extract(0, stops["id_ini"][0])
	for i in range(len(stops)-1):
		output = output + track.extract(stops["id_end"][i], stops["id_ini"][i+1])
	output = output + track.extract(stops["id_end"][-1], track.size()-1)
	return output
	
def extractStopsBis(track, diameter=2e-2, duration=10, downsampling=1):
	'''Extract stop points in a track based on two parameters:
		Maximal size of a stop (as the diameter of enclosing circle, 
		in ground units) and minimal time duration (in seconds)
		Use downsampling parameter > 1 to speed up the process'''
		
	# If down-sampling is required
	if (downsampling > 1):
		track = track.copy()
		track **= track.size()/downsampling
	
	# ---------------------------------------------------------------------------
	# Computes cost matrix as :
	#    Cij = 0 if size of enclosing circle of pi, pi+1, ... pj is > diameter
	#    Cij = 0 if time duration between pi and pj is < duration
	#    Cij = (j-i+1)**2 = square of the number of points of segment otherwise
	# ---------------------------------------------------------------------------
	C = np.zeros((track.size(), track.size()))
	print("Minimal enclosing circles computation:")
	for i in progressbar.progressbar(range(track.size()-2)):
		for j in range(i+1, track.size()-1):
			if (track[i].distance2DTo(track[j-1]) > diameter):
				C[i,j] = 0
				break
			if (track[j-1].timestamp - track[i].timestamp <= duration):
				C[i,j] = 0
				continue
			C[i,j] = 2*minCircle(track.extract(i,j-1))[1]
			C[i,j] = (C[i,j] < diameter)*(j-i)**2
	C = C + np.transpose(C)
	
	# ---------------------------------------------------------------------------
	# Computes optimal partition with dynamic programing
	# ---------------------------------------------------------------------------
	D = np.zeros((track.size()-1, track.size()-1))
	M = np.zeros((track.size()-1, track.size()-1))
	N = D.shape[0]
	
	for i in range(N):
		for j in range(i,N):
			D[i,j] = C[i,j]
			M[i,j] = -1
	
	print("Optimal split search:")
	for diag in progressbar.progressbar(range(2,N)):
		for i in range(0,N-diag):
			j=i+diag
			for k in range(i+1,j):
				val = D[i,k] + D[k,j]
				if val > D[i,j]:
					D[i,j] =  val
					M[i,j] = k
					
	# ---------------------------------------------------------------------------
	# Backward phase to form optimal split
	# ---------------------------------------------------------------------------
	segmentation = backward(M)
	
	stops = core_Track.Track()
	
	TMP_RADIUS = []
	TMP_MEAN_X = []
	TMP_MEAN_Y = []
	TMP_IDSTART = []
	TMP_IDEND = []
	TMP_STD_X = []
	TMP_STD_Y = []
	TMP_DURATION = []
	TMP_NBPOINTS = []
	
	for i in range(len(segmentation)-1):
		portion = track.extract(segmentation[i], segmentation[i+1]-1)
		C = minCircle(portion)
		if ((C[1] > diameter/2) or (portion.duration() < duration)):
			continue
		stops.addObs(Obs(C[0], portion.getFirstObs().timestamp))
		TMP_RADIUS.append(C[1])
		TMP_MEAN_X.append(portion.operate(Operator.Operator.AVERAGER, 'x'))
		TMP_MEAN_Y.append(portion.operate(Operator.Operator.AVERAGER, 'y'))
		TMP_STD_X.append(portion.operate(Operator.Operator.STDDEV, 'x'))
		TMP_STD_Y.append(portion.operate(Operator.Operator.STDDEV, 'y'))
		TMP_IDSTART.append(segmentation[i]*downsampling)
		TMP_IDEND.append((segmentation[i+1]-1)*downsampling)
		TMP_NBPOINTS.append(segmentation[i+1]-segmentation[i])
		TMP_DURATION.append(portion.duration())

	
	if stops.size() == 0:
		return stops
		
	stops.createAnalyticalFeature("radius")
	stops.createAnalyticalFeature("mean_x")
	stops.createAnalyticalFeature("mean_y")
	stops.createAnalyticalFeature("id_ini")
	stops.createAnalyticalFeature("id_end")
	stops.createAnalyticalFeature("sigma_x")
	stops.createAnalyticalFeature("sigma_y")
	stops.createAnalyticalFeature("duration")
	stops.createAnalyticalFeature("nb_points")
	
	for i in range(len(TMP_RADIUS)):
		stops.setObsAnalyticalFeature("radius", i, TMP_RADIUS[i])
		stops.setObsAnalyticalFeature("mean_x", i, TMP_MEAN_X[i])
		stops.setObsAnalyticalFeature("mean_y", i, TMP_MEAN_Y[i])
		stops.setObsAnalyticalFeature("id_ini", i, TMP_IDSTART[i])
		stops.setObsAnalyticalFeature("id_end", i, TMP_IDEND[i])
		stops.setObsAnalyticalFeature("sigma_x", i, TMP_STD_X[i])
		stops.setObsAnalyticalFeature("sigma_y", i, TMP_STD_Y[i])
		stops.setObsAnalyticalFeature("duration", i, TMP_DURATION[i])
		stops.setObsAnalyticalFeature("nb_points", i, TMP_NBPOINTS[i])
		
	stops.operate(Operator.Operator.QUAD_ADDER, "sigma_x", "sigma_y", "rmse")
				
	return stops
		
		
def splitAR1(track):
	'''Separation trace Aller/retour'''
	
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

	TRACKS = TrackCollection.TrackCollection()
	TRACKS.addTrack(first_part)
	TRACKS.addTrack(second_part)

	return (TRACKS)
	
def splitAR2(track, side_effect=0.1, sampling=1):
	'''Separation trace Aller/retour
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

	TRACKS = TrackCollection.TrackCollection()
	TRACKS.addTrack(first_part)
	TRACKS.addTrack(second_part)
	
	return TRACKS