# --------------------------- Analytics ---------------------------------------
# Class to manage general operations on a track
# -----------------------------------------------------------------------------
import sys
import math
import numpy as np
import random
import matplotlib.pyplot as plt

from tracklib.core.Obs import Obs
from tracklib.core.Coords import ENUCoords
from tracklib.core.GPSTime import GPSTime

import tracklib.core.Utils as utils
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
	
	
