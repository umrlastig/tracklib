# ------------------------- Coords -------------------------------
# Classes to manage point coordinates:
#    - GeoCoords: geographic coordinates (lon, lat, alti)
#    - ENUCoords: local projection (Eeast, North, Up)
#    - ECEFCoords: Earth-Centered-Earth-Fixed (X, Y, Z)
# ----------------------------------------------------------------

import math
import copy

Re = 6378137.0;                # Earth equatorial radius 
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
    # Base coordinates need to be provided in ECEF/Geo
    # --------------------------------------------------
    def toENUCoords(self, base):
        # Special SRID projection
        if isinstance(base, int):
            return self.toProjCoords(base)
        base_ecef = base.toECEFCoords()
        point_ecef = self.toECEFCoords()
        return point_ecef.toENUCoords(base_ecef);
        
    # --------------------------------------------------
    # Artificial function to ensure point is GeoCoords
    # --------------------------------------------------
    def toGeoCoords(self):
        return self.copy();
        
    # --------------------------------------------------
    # Distance between two geodetic coordinates
    # --------------------------------------------------
    def distanceTo(self, point):
        return self.toECEFCoords().distanceTo(point.toECEFCoords())
        
    # --------------------------------------------------
    # Distance between two geodetic coordinates
    # --------------------------------------------------
    def distance2DTo(self, point):
        return self.toENUCoords(point).norm2D()
    
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
    # Special function to convert to specific ENU srid
    # Input: a SRID number describing projection coords
    #  (e.g. 2154 for Lambert 93)
    # Output: an ENUCoords object
    # --------------------------------------------------
    def toProjCoords(self, srid_number):
        return _proj(self, srid_number)
            
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
    # Base coordinates need to be provided in ECEF/Geo
    # --------------------------------------------------
    def toECEFCoords(self, base):
        
        base = base.toECEFCoords()
        
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
    # Base coordinates need to be provided in ECEF/Geo 
    # --------------------------------------------------
    def toGeoCoords(self, base):
        # Special SRID projection
        if isinstance(base, int):
            return _unproj(self, base)
        base_ecef = base.toECEFCoords()
        point_ecef = self.toECEFCoords(base_ecef)
        return point_ecef.toGeoCoords();
        
    # --------------------------------------------------
    # Convert local ENU coordinates relative to base1 to
    # local ENU coordinates relative to base2.
    # Base coordinates should be provided in ECEF/Geo
    # --------------------------------------------------
    def toENUCoords(self, base1, base2):
        base_ecef1 = base1.toECEFCoords()
        base_ecef2 = base2.toECEFCoords()
        point_ecef = self.toECEFCoords(base_ecef1)
        return point_ecef.toENUCoords(base_ecef2);
        
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
    # Rotation (2D) of point (theta in radians)
    # --------------------------------------------------
    def rotate(self, theta):
        cr = math.cos(theta)
        sr = math.sin(theta)
        xr = +cr*self.E - sr*self.N
        yr = +sr*self.E + cr*self.N
        self.E = xr
        self.N = yr
    
    # --------------------------------------------------
    # Homotehtic transformation (2D) of point
    # --------------------------------------------------
    def scale(self, h):
        self.E *= h
        self.N *= h
        
    # --------------------------------------------------
    # Translation (3D) of point
    # --------------------------------------------------
    def translate(self, tx, ty, tz=0):
        self.E += tx
        self.N += ty
        self.U += tz
    
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
    # Base coordinates need to be provided in ECEF/Geo
    # --------------------------------------------------    
    def toENUCoords(self, base):
    
        base = base.toECEFCoords()
    
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
    # Artificial function to ensure point is ECEFCoords
    # --------------------------------------------------
    def toECEFCoords(self):
        return self.copy();
    
        
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
    

# --------------------------------------------------
# Static projection methods
# --------------------------------------------------   
def _proj(coords, srid):
    if srid == 2154:
        return _projToLambert93(coords)
    print("Error: SRID code " + str(srid) + " is not implmented in Tracklib")
    exit()
    
def _unproj(coords, srid):
    if srid == 2154:
        return __projFromLambert93(coords)
    if (srid >= 32600) and (srid <= 32799):
        zone = ((srid-32600) % 100)
        north = srid < 32700
        return _projFromUTM(coords, zone, north)
    print("Error: SRID code " + str(srid) + " is not implmented in Tracklib")
    exit()

def __projFromLambert93(coords):

    E = 0.08181919106
    Xp = 700000.000
    Yp = 12655612.050
    n = 0.725607765053267
    C = 11754255.4260960
    lambda0 = 0.0523598775598299
    X = coords.getX()
    Y = coords.getY()
    lon = math.atan(-(X-Xp)/(Y-Yp))/n + lambda0
    latiso = -math.log(math.sqrt((X-Xp)**2 + (Y-Yp)**2)/C)/n
    
    phi = 2*math.atan(math.exp(latiso))-math.pi/2
    for i in range(10):    
        phi  = 2*math.atan(((1+E*math.sin(phi))/(1-E*math.sin(phi)))**(E/2)*math.exp(latiso))
        phi -= math.pi/2
 
    return GeoCoords(lon*180/math.pi, phi*180/math.pi, coords.getZ())

def _projToLambert93(coords):
    
    E = 0.08181919106
    Xp = 700000.000
    Yp = 12655612.050
    n = 0.725607765053267
    C = 11754255.4260960
    lambda0 = 0.0523598775598299
    
    lon = coords.getX()*math.pi/180.0
    phi = coords.getY()*math.pi/180.0

    latiso = ((1-E*math.sin(phi))/(1+E*math.sin(phi)))**(E/2)
    latiso = math.tan(math.pi/4+phi/2)*latiso
    latiso = math.log(latiso)

    X = Xp + C*math.exp(-n*latiso)*math.sin(n*(lon-lambda0))
    Y = Yp - C*math.exp(-n*latiso)*math.cos(n*(lon-lambda0))
    
    return ENUCoords(X,Y,coords.getZ())


# --------------------------------------------------------------------------
# Copyright (C) 2012 Tobias Bieniek <Tobias.Bieniek@gmx.de>
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
#to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
# --------------------------------------------------------------------------
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.
# --------------------------------------------------------------------------
def _projFromUTM(coords, zone, northern=True):

    x = coords.getX() - 500000
    y = coords.getY()

    zone_number_to_central_longitude = (zone - 1) * 6 - 180 + 3

    if not northern:
        y -= 10000000
    
    K0 = 0.9996

    E = 0.00669438; E2 = E*E; E3 = E2*E; E_P2 = E/(1.0-E)

    SQRT_E = math.sqrt(1 - E)
    _E = (1 - SQRT_E) / (1 + SQRT_E)
    _E2 = _E * _E; _E3 = _E2 * _E; _E4 = _E3 * _E; _E5 = _E4 * _E

    M1 = (1-E/4-3*E2/64-5*E3/256); M2 = (3*E/8+3*E2/32+45*E3/1024)
    M3 = (15*E2/256+45*E3/1024); M4 = (35*E3/3072)

    P2 = (3./2*_E-27./32*_E3+269./512*_E5); P3 = (21./16*_E2-55./32*_E4)
    P4 = (151./96*_E3-417./128*_E5); P5 = (1097./512*_E4)
    R = 6378137

    m = y/K0; mu = m/(R*M1)

    p_rad = (mu + P2 * math.sin(2*mu) + P3 * math.sin(4*mu) + P4 * math.sin(6*mu) + P5 * math.sin(8* mu))

    p_sin = math.sin(p_rad); p_sin2 = p_sin*p_sin
    p_cos = math.cos(p_rad)

    p_tan  = p_sin / p_cos; p_tan2 = p_tan*p_tan; p_tan4 = p_tan2*p_tan2

    ep_sin = 1-E*p_sin2; ep_sin_sqrt = math.sqrt(1 - E*p_sin2)

    n = R/ep_sin_sqrt; r = (1-E)/ep_sin
    c = E_P2*p_cos**2; c2 = c*c

    d = x/(n*K0)
    d2 = d*d; d3 = d2 * d; d4 = d3*d; d5 = d4*d; d6 = d5*d

    latitude = (p_rad - (p_tan / r) *
            (d2/2-
             d4/24*(5+3*p_tan2+10*c-4*c2-9*E_P2))+
             d6/720*(61+90*p_tan2+298*c+45*p_tan4-252*E_P2-3*c2))

    longitude = (d-
             d3/6*(1+2*p_tan2+c)+
             d5/120*(5-2*c+28*p_tan2-3*c2+8*E_P2+24*p_tan4))/p_cos

    longitude = longitude + math.radians(zone_number_to_central_longitude)  # !!!! mod angle

    return GeoCoords(longitude*180/math.pi, latitude*180/math.pi, coords.getZ())


