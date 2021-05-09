# --------------------------- Obs --------------------------------
# Class to manage observation in a GPS track
# Points are referenced in geodetic coordinates
# ----------------------------------------------------------------
import sys
import copy

from tracklib.core.Coords import ECEFCoords
from tracklib.core.GPSTime import GPSTime

class Obs:
	
	# --------------------------------------------------
	# Point cooridnates in meters (ENUCoords)
	# Timestamp of aquisition (GPSTime format)
	# + GPS related information (DOP, std, ...)
	# Default timestamp is 1970/01/01 00:00:00
	# --------------------------------------------------
	def __init__(self, position, timestamp=None):
	
		if timestamp is None:
			timestamp = GPSTime()
	
		self.position = position
		self.timestamp = timestamp
		
		self.features = []
		
		self.gdop = 0
		self.pdop = 0
		self.vdop = 0
		self.hdop = 0
		self.tdop = 0
		
		self.nb_sats = 0
		self.mask = 0
		self.code = 0
		
		self.azimut = 0
		self.elevation = 0
		
	def __str__(self):
		return (str)(self.timestamp) + "  " + (str)(self.position)
	
	def copy(self):
		return copy.deepcopy(self)
	
		
	# --------------------------------------------------
	# Geom. methods (should not depend on coords type)
	# --------------------------------------------------
	def __check_call_geom1(fname, obs1, obs2):
		if (isinstance(obs1.position, ECEFCoords) or (isinstance(obs2.position, ECEFCoords))):
			sys.exit("Error: cannot call " + fname + " with ECEF coordinates")
	
	def __check_call_geom2(fname, obs1, obs2):
		c1 = type(obs1.position)
		c2 = type(obs2.position)
		nc1 = (str)(c1)[7:-1]
		nc2 = (str)(c2)[7:-1]
		if (c1 != c2):
			sys.exit("Error: cannot call " + fname + " method with " + nc1 +  " and " + nc2 + " objects")
		
	def distanceTo(self, obs):
		Obs.__check_call_geom2("distanceTo", self, obs)
		return self.position.distanceTo(obs.position)
	
	def distance2DTo(self, obs):
		Obs.__check_call_geom1("distance2DTo", self, obs)
		return self.position.distance2DTo(obs.position)
	
	def azimuthTo(self, obs):
		Obs.__check_call_geom2("azimuthTo", self, obs)
		return self.position.azimuthTo(obs.position)
	
	def elevationTo(self, obs):
		Obs.__check_call_geom2("elevationTo", self, obs)
		return self.position.elevationTo(obs.position)
		
	# ------------------------------------------------------------
    # [[n]] Get and set AF number
    # ------------------------------------------------------------    
	def __getitem__(self, af_index):
		return self.features[af_index]
	def __setitem__(self, af_index, value):
		self.features[af_index] = value	
