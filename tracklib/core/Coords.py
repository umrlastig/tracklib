# ------------------------- Coords -------------------------------
# Classes to manage point coordinates:
#    - GeoCoords: geographic coordinates (lon, lat, alti)
#    - ENUCoords: local projection (Eeast, North, Up)
#    - ECEFCoords: Earth-Centered-Earth-Fixed (X, Y, Z)
# ----------------------------------------------------------------

import math
import copy

Re = 6378137.0;				   # Earth equatorial radius 
Fe = 1.0/298.257223563;        # Earth eccentricity

class GeoCoords:

	# --------------------------------------------------
	# Longitude and latitude in decimal degrees.
	# Height in meters above geoid or ellipsoïd
	# --------------------------------------------------
	def __init__(self, lon, lat, hgt=0):
		self.lon = lon
		self.lat = lat
		self.hgt = hgt
		
		
	def __str__(self):
		output  = "[lon="+'{:12.9f}'.format(self.lon)+", "
		output +=  "lat="+'{:11.9f}'.format(self.lat)+", "
		output +=  "hgt="+'{:7.3f}'.format(self.hgt)+"]"
		return output
	
	def copy(self):
		return copy.deepcopy(self)
		
	# --------------------------------------------------
	# Convert geodetic coordinates to absolute ECEF
	# --------------------------------------------------
	def toECEFCoords(self):
	
		xyz = ECEFCoords(0.0, 0.0, 0.0)

		e = math.sqrt(Fe*(2-Fe));

		lon = self.lon * math.pi/180.0
		lat = self.lat * math.pi/180.0;
		hgt = self.hgt
		
		n = Re/math.sqrt(1-(e*math.sin(lat))**2);

		xyz.X = (n+hgt)*math.cos(lat)*math.cos(lon);
		xyz.Y = (n+hgt)*math.cos(lat)*math.sin(lon);
		xyz.Z = ((1-e*e)*n+hgt)*math.sin(lat);

		return xyz
	
	# --------------------------------------------------
	# Convert geodetic coordinates to local ENU coords
	# Base coordinates need to be provided in geo coords
	# --------------------------------------------------
	def toENUCoords(self, base):
		base_ecef = base.toECEFCoords()
		point_ecef = self.toECEFCoords()
		return point_ecef.toENUCoords(base_ecef);
		
	# --------------------------------------------------
	# Distance between two geodetic coordinates
	# --------------------------------------------------
	def distanceTo(self, point):
		return self.toECEFCoords().distanceTo(point.toECEFCoords())
	
	# --------------------------------------------------
	# Elevation (in rad) between two geodetic coordinates
	# --------------------------------------------------
	def elevationTo(self, point):
		objectif = point.toENUCoords(self)
		return math.atan2(objectif.U, objectif.norm2D())
		
	# --------------------------------------------------
	# Azimut (in rad) between two geodetic coordinates
	# --------------------------------------------------
	def azimuthTo(self, point):
		objectif = point.toENUCoords(self)
		return math.atan2(objectif.E, objectif.N)
			
	# --------------------------------------------------
	# Coords Alias X, Y, Z
	# --------------------------------------------------
	def getX(self):
		return self.lon
	def getY(self):
		return self.lat
	def getZ(self):
		return self.hgt
	def setX(self, X):
		self.lon = X
	def setY(self, Y):
		self.lat = Y
	def setZ(self, Z):
		self.hgt = Z	
	
	
class ENUCoords:

	# --------------------------------------------------
	# East, North and Up in meters
	# --------------------------------------------------
	def __init__(self, E, N, U=0):
		self.E = E
		self.N = N
		self.U = U
		
	def __str__(self):
		output  = "[E="+'{:12.3f}'.format(self.E)+", "
		output +=  "N="+'{:12.3f}'.format(self.N)+", "
		output +=  "U="+'{:12.3f}'.format(self.U)+"]"
		return output
	
	def copy(self):
		return copy.deepcopy(self)
		
	# --------------------------------------------------
	# Convert local planimetric to absolute geocentric
	# Base coordinates need to be provided in ECEF
	# --------------------------------------------------
	def toECEFCoords(self, base):
		
		xyz = ECEFCoords(0.0, 0.0, 0.0);
		
		e = self.E;
		n = self.N;
		u = self.U;

		base_geo = base.toGeoCoords();

		blon = base_geo.lon * math.pi/180.0;
		blat = base_geo.lat * math.pi/180.0;

		slon = math.sin(blon);
		slat = math.sin(blat);
		clon = math.cos(blon);
		clat = math.cos(blat);

		xyz.X = -e*slon       - n*clon*slat  +  u*clon*clat    +  base.X;
		xyz.Y =  e*clon       - n*slon*slat  +  u*slon*clat    +  base.Y;
		xyz.Z =                 n*clat       +  u*slat         +  base.Z;

		return xyz;
	
	# --------------------------------------------------
	# Convert local ENU coordinates to  geo coords
	# Base coordinates need to be provided in geo coords
	# --------------------------------------------------
	def toGeoCoords(self, base):
		base_ecef = base.toECEFCoords()
		point_ecef = self.toECEFCoords(base_ecef)
		return point_ecef.toGeoCoords();
		
	# --------------------------------------------------
	# Planimetric euclidian norm of point
	# --------------------------------------------------
	def norm2D(self):
		return math.sqrt(self.E**2 + self.N**2)

	# --------------------------------------------------
	# R^3 space euclidian norm of point
	# --------------------------------------------------
	def norm(self):
		return math.sqrt(self.E**2 + self.N**2 + self.U**2)
		
	# --------------------------------------------------
	# Dot product between two vectors
	# --------------------------------------------------
	def dot(self, point):
		return self.E*point.E + self.N*point.N + self.U*point.U
		
	# --------------------------------------------------
	# Elevation (in rad) between two ENU coordinates
	# --------------------------------------------------
	def elevationTo(self, point):
		visee = point - self
		return math.atan2(visee.U, visee.norm2D())
		
	# --------------------------------------------------
	# Azimut (in rad) between two ENU coordinates
	# --------------------------------------------------
	def azimuthTo(self, point):
		visee = point - self
		return math.atan2(visee.E, visee.N)
		
	# --------------------------------------------------
	# Vector difference between two ENU coordinates
	# --------------------------------------------------
	def __sub__(self, p): 
		return ENUCoords(p.E-self.E, p.N-self.N, p.U-self.U)
		
	# --------------------------------------------------
	# Vector difference between two ENU coordinates
	# --------------------------------------------------
	def __add__(self, p): 
		return ENUCoords(p.E+self.E, p.N+self.N, p.U+self.U)
		
	# --------------------------------------------------
	# Distance 2D between two ENU coordinates
	# --------------------------------------------------
	def distance2DTo(self, point):
		return (point-self).norm2D()
		
	# --------------------------------------------------
	# Distance 3D between two ENU coordinates
	# --------------------------------------------------
	def distanceTo(self, point):
		return (point-self).norm()
		
	
	# --------------------------------------------------
	# Coords Alias X, Y, Z
	# --------------------------------------------------
	def getX(self):
		return self.E
	def getY(self):
		return self.N
	def getZ(self):
		return self.U
	def setX(self, X):
		self.E = X
	def setY(self, Y):
		self.N = Y
	def setZ(self, Z):
		self.U = Z
		
		
	
class ECEFCoords:

	# --------------------------------------------------
	# X, Y, Z in meters
	# --------------------------------------------------
	def __init__(self, X, Y, Z):
		self.X = X
		self.Y = Y
		self.Z = Z
		
	def __str__(self):
		output  = "[X="+'{:12.3f}'.format(self.X)+", "
		output +=  "Y="+'{:12.3f}'.format(self.Y)+", "
		output +=  "Z="+'{:12.3f}'.format(self.Z)+"]"
		return output
	
	def copy(self):
		return copy.deepcopy(self)
		
	# --------------------------------------------------
	# Convert absolute geocentric coords to geodetic
	# longitude, latitude and height
	# --------------------------------------------------	
	def toGeoCoords(self):

		geo = GeoCoords(0.0, 0.0, 0.0);

		b = Re*(1-Fe);
		e = math.sqrt(Fe*(2-Fe));

		X = self.X;
		Y = self.Y;
		Z = self.Z;

		h = Re*Re-b*b;
		p = math.sqrt(X*X + Y*Y);
		t = math.atan2(Z*Re, p*b);

		geo.lon = math.atan2(Y,X);
		geo.lat = math.atan2(Z+h/b*pow(math.sin(t),3), p-h/Re*(math.cos(t))**3);
		n = Re/math.sqrt(1-(e*math.sin(geo.lat))**2);
		geo.hgt = (p/math.cos(geo.lat))-n;

		geo.lon *= 180.0/math.pi
		geo.lat *= 180.0/math.pi

		return geo;
	
	
	# --------------------------------------------------
	# Convert local coordinates to absolute geocentric
	# Base coordinates need to be provided in ECEF
	# --------------------------------------------------	
	def toENUCoords(self, base):
	
		enu = ENUCoords(0.0, 0.0, 0.0)

		base_geo = base.toGeoCoords();

		blon = base_geo.lon * math.pi/180.0
		blat = base_geo.lat * math.pi/180.0

		x = self.X - base.X;
		y = self.Y - base.Y;
		z = self.Z - base.Z;

		slon = math.sin(blon);
		slat = math.sin(blat);
		clon = math.cos(blon);
		clat = math.cos(blat);

		enu.E = -x*slon       + y*clon;
		enu.N = -x*clon*slat  - y*slon*slat  +  z*clat;
		enu.U =  x*clon*clat  + y*slon*clat  +  z*slat;

		return enu;	
	
		
	# --------------------------------------------------
	# Elevation (in rad) between two ECEF coordinates
	# --------------------------------------------------
	def elevationTo(self, point):
		objectif = point.toENUCoords(self)
		return math.atan2(objectif.U, objectif.norm2D())
		
	# --------------------------------------------------
	# Azimut (in rad) between two ECEF coordinates
	# --------------------------------------------------
	def azimuthTo(self, point):
		objectif = point.toENUCoords(self)
		return math.atan2(objectif.E, objectif.N)
		
	# --------------------------------------------------
	# Dot product between two vectors
	# --------------------------------------------------
	def dot(self, point):
		return self.X*point.X + self.Y*point.Y + self.Z*point.Z

	# --------------------------------------------------
	# R^3 space euclidian norm of point
	# --------------------------------------------------
	def norm(self):
		return math.sqrt(self.dot(self));

	# --------------------------------------------------
	# Scalar multiplication of a vector
	# --------------------------------------------------
	def scalar(self, factor):
		self.X *= factor
		self.Y *= factor
		self.Z *= factor

	# --------------------------------------------------
	# Vector difference between two ECEF coordinates
	# --------------------------------------------------
	def __sub__(self, p): 
		return ECEFCoords(p.X-self.X, p.Y-self.Y, p.Z-self.Z)
		
	# --------------------------------------------------
	# Vector sum of two ECEF coordinates
	# --------------------------------------------------
	def __add__(self, p): 
		return ECEFCoords(p.X+self.X, p.Y+self.Y, p.Z+self.Z)

	# --------------------------------------------------
	# Distance (in m) between two ECEF coordinates
	# --------------------------------------------------
	def distanceTo(self, point):
		return (point-self).norm()
	
		
	# --------------------------------------------------
	# Coords Alias X, Y, Z
	# --------------------------------------------------
	def getX(self):
		return self.X
	def getY(self):
		return self.Y
	def getZ(self):
		return self.Z
	def setX(self, X):
		self.X = X
	def setY(self, Y):
		self.Y = Y
	def setZ(self, Z):
		self.Z = Z
	
	