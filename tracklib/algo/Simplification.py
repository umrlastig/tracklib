# ------------------------- Simplification -------------------------------------
# Class to manage simplification of GPS tracks
# -----------------------------------------------------------------------------

import sys
import numpy as np

import tracklib.core.Track as Track
import tracklib.core.Utils as utils
import tracklib.core.Operator as Operator

MODE_SIMPLIFY_DOUGLAS_PEUCKER = 1
MODE_SIMPLIFY_VISVALINGAM = 2

# --------------------------------------------------------------------------
# Generic method to simplify a track
# Tolerance is in the unit of track observation coordinates
# 	MODE_SIMPLIFY_DOUGLAS_PEUCKER (1)
#   MODE_SIMPLIFY_VISVALINGAM (2)
# --------------------------------------------------------------------------
def simplify(track, tolerance, mode = MODE_SIMPLIFY_DOUGLAS_PEUCKER):
		if mode == MODE_SIMPLIFY_DOUGLAS_PEUCKER:
			return douglas_peucker(track, tolerance)
		if mode == MODE_SIMPLIFY_VISVALINGAM:
			return visvalingam(track, tolerance)
		sys.exit("Error: track simplification mode " + (str)(mode) + " not implemented yet")

# --------------------------------------------------------------------------
# Function to simplify a GPS track with Visvalingam algorithm
# --------------------------------------------------------------------------
# Input : 
#   - track ::     GPS track
#   - eps   ::     length threshold epsilon (sqrt of triangle area)
# --------------------------------------------------------------------------
# Output : simplified 
# --------------------------------------------------------------------------
def visvalingam(track, eps):
	eps **= 2
	output = track.copy()
	output.addAnalyticalFeature(utils.aire_visval, "@aire")
	while 1:
		id = output.operate(Operator.Operator.ARGMIN, "@aire")
		if output.getObsAnalyticalFeature("@aire", id) > eps:
			break
		output.removeObs(id)
		if id > 1:
			output.setObsAnalyticalFeature("@aire", id-1, utils.aire_visval(output, id-1))
		if id < output.size()-1:
			output.setObsAnalyticalFeature("@aire", id, utils.aire_visval(output, id))
	output.removeAnalyticalFeature("@aire")
	return output
	

# --------------------------------------------------------------------------
# Function to simplify a GPS track with Douglas-Peucker algorithm
# --------------------------------------------------------------------------
# Input : 
#   - track ::     GPS track
#   - eps   ::     length threshold epsilon
# --------------------------------------------------------------------------
# Output : simplified 
# --------------------------------------------------------------------------
def douglas_peucker(track, eps):

	L = track.getObsList()
	
	n = len(L)
	if (n <= 2):
		return Track.Track(L)
	
	dmax = 0
	imax = 0
	
	for i in range(0,n):
		x0 = L[i].position.getX()
		y0 = L[i].position.getY()
		xa = L[0].position.getX()
		ya = L[0].position.getY()
		xb = L[n-1].position.getX()
		yb = L[n-1].position.getY()
		d = utils.distance_to_segment(x0, y0, xa, ya, xb, yb)
		if (d > dmax):
			dmax = d
			imax = i
		
	if (dmax < eps):
		return Track.Track([L[0], L[n-1]])
	else:
		XY1 = Track.Track(L[0:imax])
		XY2 = Track.Track(L[imax:n])
		return douglas_peucker(XY1, eps) + douglas_peucker(XY2, eps)