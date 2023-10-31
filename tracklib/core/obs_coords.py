"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Yann Méneroux
Creation date: 1th november 2020

tracklib library provides a variety of tools, operators and 
functions to manipulate GPS trajectories. It is a open source contribution 
of the LASTIG laboratory at the Institut National de l'Information 
Géographique et Forestière (the French National Mapping Agency).
See: https://tracklib.readthedocs.io
 
This software is governed by the CeCILL-C license under French law and
abiding by the rules of distribution of free software. You can  use, 
modify and/ or redistribute the software under the terms of the CeCILL-C
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info". 

As a counterpart to the access to the source code and rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability. 

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or 
data to be ensured and,  more generally, to use and operate it in the 
same conditions as regards security. 

The fact that you are presently reading this means that you have had
knowledge of the CeCILL-C license and that you accept its terms.
"""

"""
This Module contains the classes to manage point coordinates:

    - :class:`GeoCoords` : For representation og geographic coordinates (lon, lat, alti)
    - :class:`ENUCoords` : For local projection (East, North, Up)
    - :class:`ECEFCoords` : For Earth-Centered-Earth-Fixed coordinates (X, Y, Z)

"""

# For type annotation
from __future__ import annotations   
from typing import Union

import math
import copy
import matplotlib.pyplot as plt

# The current constants are used in this module : 
Re: float = 6378137.0            #: Earth semi-major axis
Be: float = 6356752.314          #: Earth semi-minor axis
Fe: float = 1.0 / 298.257223563  #: Earth flattening
Ee: float = 0.0818191910428      #: Earth eccentricity

STANDARD_PROJ = 1   # 1: flat, 2: stereographic 

class GeoCoords:
    """Class to represent geographics coordinates"""

    def __init__(self, lon: float, lat: float, hgt: float = 0.0):   
        """Constructor of :class:`GeoCoords` class

        :param lon: longitude in decimal degrees
        :param lat: latitude in decimal degrees
        :param hgt: height in meters above geoid or ellipsoid, defaults to 0
        """
        self.lon = lon
        self.lat = lat
        self.hgt = hgt

    def __str__(self) -> str:   
        """Transform the object in string

        :return: String representation of coordinates
        """
        output = "[lon=" + "{:12.9f}".format(self.lon) + ", "
        output += "lat=" + "{:11.9f}".format(self.lat) + ", "
        output += "hgt=" + "{:7.3f}".format(self.hgt) + "]"
        return output

    def copy(self) -> GeoCoords:   
        """TODO"""
        return copy.deepcopy(self)

    def toECEFCoords(self) -> ECEFCoords:   
        """Convert geodetic coordinates to absolute ECEF

        :return: absolute ECEF coordinates
        """

        xyz = ECEFCoords(0.0, 0.0, 0.0)

        e = math.sqrt(Fe * (2 - Fe))

        lon = self.lon * math.pi / 180.0
        lat = self.lat * math.pi / 180.0
        hgt = self.hgt

        n = Re / math.sqrt(1 - (e * math.sin(lat)) ** 2)

        xyz.X = (n + hgt) * math.cos(lat) * math.cos(lon)
        xyz.Y = (n + hgt) * math.cos(lat) * math.sin(lon)
        xyz.Z = ((1 - e * e) * n + hgt) * math.sin(lat)

        return xyz

    def toENUCoords(self, base: Union[ECEFCoords, GeoCoords]) -> ENUCoords:   
        """Convert geodetic coordinates to local ENU coords

        :param base: Base coordinates for conversion
        :return: Converted coordinates
        """
        # Special SRID projection
        if isinstance(base, int):
            return self.toProjCoords(base)
			
        # ---------------------------------------	
        # Sterographic projection test		
		# ---------------------------------------	
        if (STANDARD_PROJ == 2):
            phi = self.lat*math.pi/180
            psi = math.atan(Be/Re*math.tan(phi))
            w = Be/math.sqrt((Re*math.sin(psi))**2 + (Be*math.cos(psi))**2)
            N = Re/w
            rho = Re*(1-Ee**2)/w**3
            R = math.sqrt(N*rho)

            lon = (self.lon-base.lon)*math.pi/180
            lat = (self.lat-base.lat)*math.pi/180
            x = +R*math.tan(math.pi/4-lat/2)*math.sin(lon)*math.cos(self.lat*math.pi/180)
            y = -R*math.tan(math.pi/4-lat/2)*math.cos(lon)+6380968.157
            output = ENUCoords(x, y, self.hgt)
            return output			
			
        # ---------------------------------------	
        # Standard flat projection	
		# ---------------------------------------	
        else:			
            base_ecef = base.toECEFCoords()
            point_ecef = self.toECEFCoords()
            return point_ecef.toENUCoords(base_ecef)

    def toGeoCoords(self) -> GeoCoords:   
        """Artificial function to ensure point is GeoCoords

        :return: Copy of current object
        """
        return self.copy()

    def distanceTo(self, point: GeoCoords) -> float:   
        """Distance between two geodetic coordinates

        :param point: Geographic coordinate
        :return: Distance
        """
        return self.toECEFCoords().distanceTo(point.toECEFCoords())

    def distance2DTo(self, point: GeoCoords) -> float:   
        """2D Distance between two geodetic coordinates

        :param point: Geographic coordinate
        :return: 2D Distance
        """
        return self.toENUCoords(point).norm2D()

    def elevationTo(self, point: GeoCoords) -> float:   
        """Elevation between two geodetic coordinates

        :param point: Geographic coordinate
        :return: Elevation (in rad)
        """
        objectif = point.toENUCoords(self)
        return math.atan2(objectif.U, objectif.norm2D())

    def azimuthTo(self, point: GeoCoords) -> float:   
        """Azimut between two geodetic coordinates

        :param point: Geographic coordinate
        :return: Azimut (in rad)
        """
        objectif = point.toENUCoords(self)
        return math.atan2(objectif.E, objectif.N)

    def toProjCoords(self, srid_number: int) -> ENUCoords:   
        """Special function to convert to specific ENU srid

        :param srid_number: A SRID number describing projection coords
            (e.g. 2154 for Lambert 93)
        :return: an ENUCoords object
        """
        return _proj(self, srid_number)

    # --------------------------------------------------
    # Coords Alias X, Y, Z
    # --------------------------------------------------
    def getX(self) -> float:   
        """Return the X coordinate"""
        return self.lon

    def getY(self) -> float:   
        """Return the Y coordinate"""
        return self.lat

    def getZ(self) -> float:   
        """Return the Z coordinate"""
        return self.hgt

    def setX(self, X: float):   
        """Set the X coordinate

        :param X: X coordinate
        """
        self.lon = X

    def setY(self, Y: float):   
        """Set the Y coordinate

        :param Y: Y coordinate
        """
        self.lat = Y

    def setZ(self, Z: float):   
        """Set the Z coordinate

        :param Z: Z coordinate
        """
        self.hgt = Z

    def plot(self, sym="ro"):
        """TODO"""
        plt.plot(self.lon, self.lat, sym)


class ENUCoords:
    """Class for representation of local projection (East, North, Up)"""

    def __init__(self, E: float, N: float, U: float = 0):   
        """Constructor of class:`ENUCoords`  class

        :param E: East coordinate (in meters)
        :param N: North coordinate (in meters)
        :param U: Elevation (in meter), defaults to 0
        """
        self.E = E
        self.N = N
        self.U = U

    def __str__(self):
        """Transform the object in string

        :return: String representation of coordinates
        """
        output = "[E=" + "{:12.3f}".format(self.E) + ", "
        output += "N=" + "{:12.3f}".format(self.N) + ", "
        output += "U=" + "{:12.3f}".format(self.U) + "]"
        return output

    def copy(self) -> ENUCoords:   
        """Copy the current object

        :return: A copy of current object
        """
        return copy.deepcopy(self)

    def toECEFCoords(self, base: Union[ECEFCoords, GeoCoords]) -> ECEFCoords:   
        """Convert local planimetric to absolute geocentric

        :param base: Base coordinates
        :return: Transformet coordinates
        """

        base = base.toECEFCoords()

        xyz = ECEFCoords(0.0, 0.0, 0.0)

        e = self.E
        n = self.N
        u = self.U

        base_geo = base.toGeoCoords()

        blon = base_geo.lon * math.pi / 180.0
        blat = base_geo.lat * math.pi / 180.0

        slon = math.sin(blon)
        slat = math.sin(blat)
        clon = math.cos(blon)
        clat = math.cos(blat)

        xyz.X = -e * slon - n * clon * slat + u * clon * clat + base.X
        xyz.Y = e * clon - n * slon * slat + u * slon * clat + base.Y
        xyz.Z = n * clat + u * slat + base.Z

        return xyz

    def toGeoCoords(self, base: Union[ECEFCoords, GeoCoords]) -> GeoCoords:   
        """Convert local ENU coordinates to geo coords

        :param base: Base coordinates
        :return: Transformed coordinates
        """
        # Special SRID projection
        if isinstance(base, int):
            return _unproj(self, base)
        base_ecef = base.toECEFCoords()
        point_ecef = self.toECEFCoords(base_ecef)
        return point_ecef.toGeoCoords()

    def toENUCoords(self, base1: Union[ECEFCoords, GeoCoords], base2: Union[ECEFCoords, GeoCoords]) -> ENUCoords:   
        """Convert local ENU coordinates relative to base1 to
        local ENU coordinates relative to base2.

        :param base1: Base 1 coordinates
        :param base2: Base 2 coordinates
        :return: Transformed coordinates
        """
        base_ecef1 = base1.toECEFCoords()
        base_ecef2 = base2.toECEFCoords()
        point_ecef = self.toECEFCoords(base_ecef1)
        return point_ecef.toENUCoords(base_ecef2)

    def norm2D(self) -> float:   
        """Planimetric euclidian norm of point

        :return: Euclidian norm
        """
        return math.sqrt(self.E ** 2 + self.N ** 2)

    def norm(self) -> float:   
        """R^3 space euclidian norm of point

        :return: R^3 space euclidian norm of point
        """
        return math.sqrt(self.E ** 2 + self.N ** 2 + self.U ** 2)

    def dot(self, point):
        """Dot product between two vectors


        :param point: [description]
        :return: [description]
        """
        return self.E * point.E + self.N * point.N + self.U * point.U

    def elevationTo(self, point: ENUCoords) -> float:   
        """Elevation between two ENU coordinates

        :param point: A ENUCoordinate
        :return: Elevation (in rad)
        """
        visee = point - self
        return math.atan2(visee.U, visee.norm2D())

    def azimuthTo(self, point: ENUCoords) -> float:
        """Azimut between two ENU coordinates

        :param point: A ENUCoordinate
        :return: Azimut (in rad)
        """
        visee = point - self
        return math.atan2(visee.E, visee.N)

    def __sub__(self, p: ENUCoords) -> ENUCoords:   
        """
        Vector difference between two ENU coordinates (AB: B-A).

        :param p: An ENU coordinate
        :return: An ENU coordinate
        """
        # return ENUCoords(p.E - self.E, p.N - self.N, p.U - self.U)
        return ENUCoords(self.E - p.E, self.N - p.N, self.U - p.U)

    def __add__(self, p: ENUCoords) -> ENUCoords:   
        """Vector addition between two ENU coordinates

        :param p: An ENU coordinate
        :return: An ENU coordinate
        """
        return ENUCoords(p.E + self.E, p.N + self.N, p.U + self.U)

    def distance2DTo(self, point: ENUCoords) -> float:   
        """Distance 2D between two ENU coordinates

        :param point: A ENU coordinate
        :return: 2D distance
        """
        return (point - self).norm2D()

    def distanceTo(self, point: ENUCoords) -> float:   
        """Distance 3D between two ENU coordinates

        :param point: A ENU coordinate
        :return: 2D distance
        """
        return (point - self).norm()

    def rotate(self, theta: float):   
        """Rotation (2D) of point

        :param theta: Angle of rotation (in rad)
        """
        cr = math.cos(theta)
        sr = math.sin(theta)
        xr = +cr * self.E - sr * self.N
        yr = +sr * self.E + cr * self.N
        self.E = xr
        self.N = yr

    def scale(self, h: float):   
        """Homotehtic transformation (2D) of point

        :param h: factor
        """
        self.E *= h
        self.N *= h

    def translate(self, tx: float, ty: float, tz: float = 0):   
        """Translation (3D) of point

        :param tx: X translation
        :param ty: Y translation
        :param tz: Z translation, defaults to 0
        """
        self.E += tx
        self.N += ty
        self.U += tz

    # --------------------------------------------------
    # Coords Alias X, Y, Z
    # --------------------------------------------------
    def getX(self) -> float:   
        """Return the X coordinate"""
        return self.E

    def getY(self) -> float:   
        """Return the Y coordinate"""
        return self.N

    def getZ(self) -> float:   
        """Return the Z coordinate"""
        return self.U

    def setX(self, X: float):   
        """Set the X coordinate

        :param X: X coordinate
        """
        self.E = X

    def setY(self, Y: float):   
        """Set the Y coordinate

        :param Y: Y coordinate
        """
        self.N = Y

    def setZ(self, Z: float):   
        """Set the Z coordinate

        :param Z: Z coordinate
        """
        self.U = Z

    def plot(self, sym="ro"):
        """TODO"""
        plt.plot(self.E, self.N, sym)


class ECEFCoords:
    """Class to represent Earth-Centered-Earth-Fixed coordinates"""

    # --------------------------------------------------
    # X, Y, Z in meters
    # --------------------------------------------------
    def __init__(self, X: float, Y: float, Z: float):   
        """Constructor of :class:`ECEFCoords` class

        :param X: X corrdinate (meters)
        :param Y: Y corrdinate (meters)
        :param Z: Z corrdinate (meters)
        """
        self.X = X
        self.Y = Y
        self.Z = Z

    def __str__(self) -> str:   
        """Transform the object in string

        :return: String representation of coordinates
        """
        output = "[X=" + "{:12.3f}".format(self.X) + ", "
        output += "Y=" + "{:12.3f}".format(self.Y) + ", "
        output += "Z=" + "{:12.3f}".format(self.Z) + "]"
        return output

    def copy(self) -> ECEFCoords:   
        """Copy the current object

        :return: A copy of current object
        """
        return copy.deepcopy(self)

    def toGeoCoords(self) -> GeoCoords:   
        """Convert absolute geocentric coords to geodetic longitude, latitude and height

        :return: GeoCoords representation of current coordinates
        """

        geo = GeoCoords(0.0, 0.0, 0.0)

        b = Re * (1 - Fe)
        e = math.sqrt(Fe * (2 - Fe))

        X = self.X
        Y = self.Y
        Z = self.Z

        h = Re * Re - b * b
        p = math.sqrt(X * X + Y * Y)
        t = math.atan2(Z * Re, p * b)

        geo.lon = math.atan2(Y, X)
        geo.lat = math.atan2(
            Z + h / b * pow(math.sin(t), 3), p - h / Re * (math.cos(t)) ** 3
        )
        n = Re / math.sqrt(1 - (e * math.sin(geo.lat)) ** 2)
        geo.hgt = (p / math.cos(geo.lat)) - n

        geo.lon *= 180.0 / math.pi
        geo.lat *= 180.0 / math.pi

        return geo

    def toENUCoords(self, base: Union[ECEFCoords, GeoCoords]) -> ENUCoords:   
        """Convert local coordinates to absolute geocentric

        :param base: Base coordinates
        :return: Transformed coordinates
        """

        base = base.toECEFCoords()

        enu = ENUCoords(0.0, 0.0, 0.0)

        base_geo = base.toGeoCoords()

        blon = base_geo.lon * math.pi / 180.0
        blat = base_geo.lat * math.pi / 180.0

        x = self.X - base.X
        y = self.Y - base.Y
        z = self.Z - base.Z

        slon = math.sin(blon)
        slat = math.sin(blat)
        clon = math.cos(blon)
        clat = math.cos(blat)

        enu.E = -x * slon + y * clon
        enu.N = -x * clon * slat - y * slon * slat + z * clat
        enu.U = x * clon * clat + y * slon * clat + z * slat

        return enu

    def toECEFCoords(self) -> ECEFCoords:   
        """Artificial function to ensure point is ECEFCoords

        :return: ECEFCoords
        """
        return self.copy()

    def elevationTo(self, point: ECEFCoords) -> float:   
        """Elevation between two ECEF coordinates

        :param point: Coordinate 2
        :return: Elevation (rad)
        """
        objectif = point.toENUCoords(self)
        return math.atan2(objectif.U, objectif.norm2D())

    def azimuthTo(self, point: ECEFCoords) -> float:   
        """Azimut between two ECEF coordinates

        :param point: Coordinate 2
        :return: Azimuth (rad)
        """
        objectif = point.toENUCoords(self)
        return math.atan2(objectif.E, objectif.N)

    def dot(self, point):
        """Dot product between two vectors"""
        return self.X * point.X + self.Y * point.Y + self.Z * point.Z

    def norm(self) -> float:   
        """R^3 space euclidian norm of point

        :return: R^3 space euclidian norm
        """
        return math.sqrt(self.dot(self))

    def scalar(self, factor: float):   
        """Scalar multiplication of a vector

        :param factor: Multiplication factor
        """
        self.X *= factor
        self.Y *= factor
        self.Z *= factor

    def __sub__(self, p: ECEFCoords) -> ECEFCoords:   
        """Vector difference between two ECEF coordinates

        :param p: Corrdinate 2
        :return: Result of substration
        """
        return ECEFCoords(p.X - self.X, p.Y - self.Y, p.Z - self.Z)

    def __add__(self, p: ECEFCoords) -> ECEFCoords:   
        """Vector sum between two ECEF coordinates

        :param p: Corrdinate 2
        :return: Result of sum
        """
        return ECEFCoords(p.X + self.X, p.Y + self.Y, p.Z + self.Z)

    def distanceTo(self, point: ECEFCoords) -> float:   
        """Distance between two ECEF coordinates

        :param point: Corrdinate 2
        :return: Distance (meters)
        """
        return (point - self).norm()

    def getX(self) -> float:   
        """Return the X coordinate"""
        return self.X

    def getY(self) -> float:   
        """Return the X coordinate"""
        return self.Y

    def getZ(self) -> float:   
        """Return the X coordinate"""
        return self.Z

    def setX(self, X: float):   
        """Set the X coordinate

        :param X: X coordinate
        """
        self.X = X

    def setY(self, Y: float):   
        """Set the Y coordinate

        :param Y: Y coordinate
        """
        self.Y = Y

    def setZ(self, Z: float):   
        """Set the Z coordinate

        :param Z: Z coordinate
        """
        self.Z = Z


# --------------------------------------------------
#   Utils
# --------------------------------------------------
def makeCoords(x: float, y: float, z: float, srid: str) -> Union[ENUCoords, ECEFCoords, GeoCoords]:   
    """Function to form coords object from (x,y,z) data

    :param x: 1st coordinate (X, lon or E)
    :param y: 2nd coordinate (Y, lat or N)
    :param z: 3rd coordinate (Z, hgt or U)
    :param srid: Id of coord system (ECEF, GEO or ENU)

    :return: Coords object in the proper srid
    """
    if srid.upper() in ["ENUCOORDS", "ENU"]:
        return ENUCoords(x, y, z)
    if srid.upper() in ["GEOCOORDS", "GEO"]:
        return GeoCoords(x, y, z)
    if srid.upper() in ["ECEFCOORDS", "ECEF"]:
        return ECEFCoords(x, y, z)
    
    print("Error: unknown coordinate type [" + str(srid) + "]")
    exit()


# --------------------------------------------------
# Static projection methods
# --------------------------------------------------
def _proj(coords, srid: int):   
    """TODO"""
    if srid == 2154:
        return _projToLambert93(coords)
    print("Error: SRID code " + str(srid) + " is not implmented in Tracklib")
    exit()


def _unproj(coords, srid: int):   
    """TODO"""
    if srid == 2154:
        return __projFromLambert93(coords)
    if (srid >= 32600) and (srid <= 32799):
        zone = (srid - 32600) % 100
        north = srid < 32700
        return _projFromUTM(coords, zone, north)
    print("Error: SRID code " + str(srid) + " is not implmented in Tracklib")
    exit()


def __projFromLambert93(coords) -> GeoCoords:   
    """TODO"""
    E = 0.08181919106  #: TODO
    Xp = 700000.000  #: TODO
    Yp = 12655612.050  #: TODO
    n = 0.725607765053267  #: TODO
    C = 11754255.4260960  #: TODO
    lambda0 = 0.0523598775598299  #: TODO

    X = coords.getX()
    Y = coords.getY()
    lon = math.atan(-(X - Xp) / (Y - Yp)) / n + lambda0
    latiso = -math.log(math.sqrt((X - Xp) ** 2 + (Y - Yp) ** 2) / C) / n

    phi = 2 * math.atan(math.exp(latiso)) - math.pi / 2
    for i in range(10):
        phi = 2 * math.atan(
            ((1 + E * math.sin(phi)) / (1 - E * math.sin(phi))) ** (E / 2)
            * math.exp(latiso)
        )
        phi -= math.pi / 2

    return GeoCoords(lon * 180 / math.pi, phi * 180 / math.pi, coords.getZ())


def _projToLambert93(coords) -> ENUCoords:   
    """TODO"""

    E = 0.08181919106  #: TODO
    Xp = 700000.000  #: TODO
    Yp = 12655612.050  #: TODO
    n = 0.725607765053267  #: TODO
    C = 11754255.4260960  #: TODO
    lambda0 = 0.0523598775598299  #: TODO

    lon = coords.getX() * math.pi / 180.0
    phi = coords.getY() * math.pi / 180.0

    latiso = ((1 - E * math.sin(phi)) / (1 + E * math.sin(phi))) ** (E / 2)
    latiso = math.tan(math.pi / 4 + phi / 2) * latiso
    latiso = math.log(latiso)

    X = Xp + C * math.exp(-n * latiso) * math.sin(n * (lon - lambda0))
    Y = Yp - C * math.exp(-n * latiso) * math.cos(n * (lon - lambda0))

    return ENUCoords(X, Y, coords.getZ())


# --------------------------------------------------------------------------
# Copyright (C) 2012 Tobias Bieniek <Tobias.Bieniek@gmx.de>
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
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
    """TODO"""

    x = coords.getX() - 500000
    y = coords.getY()

    zone_number_to_central_longitude = (zone - 1) * 6 - 180 + 3

    if not northern:
        y -= 10000000

    K0 = 0.9996

    E = 0.00669438
    E2 = E * E
    E3 = E2 * E
    E_P2 = E / (1.0 - E)

    SQRT_E = math.sqrt(1 - E)
    _E = (1 - SQRT_E) / (1 + SQRT_E)
    _E2 = _E * _E
    _E3 = _E2 * _E
    _E4 = _E3 * _E
    _E5 = _E4 * _E

    M1 = 1 - E / 4 - 3 * E2 / 64 - 5 * E3 / 256
    M2 = 3 * E / 8 + 3 * E2 / 32 + 45 * E3 / 1024
    M3 = 15 * E2 / 256 + 45 * E3 / 1024
    M4 = 35 * E3 / 3072

    P2 = 3.0 / 2 * _E - 27.0 / 32 * _E3 + 269.0 / 512 * _E5
    P3 = 21.0 / 16 * _E2 - 55.0 / 32 * _E4
    P4 = 151.0 / 96 * _E3 - 417.0 / 128 * _E5
    P5 = 1097.0 / 512 * _E4
    R = 6378137

    m = y / K0
    mu = m / (R * M1)

    p_rad = (
        mu
        + P2 * math.sin(2 * mu)
        + P3 * math.sin(4 * mu)
        + P4 * math.sin(6 * mu)
        + P5 * math.sin(8 * mu)
    )

    p_sin = math.sin(p_rad)
    p_sin2 = p_sin * p_sin
    p_cos = math.cos(p_rad)

    p_tan = p_sin / p_cos
    p_tan2 = p_tan * p_tan
    p_tan4 = p_tan2 * p_tan2

    ep_sin = 1 - E * p_sin2
    ep_sin_sqrt = math.sqrt(1 - E * p_sin2)

    n = R / ep_sin_sqrt
    r = (1 - E) / ep_sin
    c = E_P2 * p_cos ** 2
    c2 = c * c

    d = x / (n * K0)
    d2 = d * d
    d3 = d2 * d
    d4 = d3 * d
    d5 = d4 * d
    d6 = d5 * d

    latitude = (
        p_rad
        - (p_tan / r)
        * (d2 / 2 - d4 / 24 * (5 + 3 * p_tan2 + 10 * c - 4 * c2 - 9 * E_P2))
        + d6 / 720 * (61 + 90 * p_tan2 + 298 * c + 45 * p_tan4 - 252 * E_P2 - 3 * c2)
    )

    longitude = (
        d
        - d3 / 6 * (1 + 2 * p_tan2 + c)
        + d5 / 120 * (5 - 2 * c + 28 * p_tan2 - 3 * c2 + 8 * E_P2 + 24 * p_tan4)
    ) / p_cos

    longitude = longitude + math.radians(
        zone_number_to_central_longitude
    )  # !!!! mod angle

    return GeoCoords(longitude * 180 / math.pi, latitude * 180 / math.pi, coords.getZ())
