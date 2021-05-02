# -*- coding: utf-8 -*-

#
from tracklib.core.Coords import ENUCoords, ECEFCoords, GeoCoords
from tracklib.core.GPSTime import GPSTime
from tracklib.core.Obs import Obs


def wktLineStringToObs(wkt, srid):
    '''
    Une polyligne de n points est modélisée par une Track (timestamp = 1970/01/01 00 :00 :00)
        Cas LINESTRING()
    '''
    
    # Creation d'une liste vide
    TAB_OBS = list()
    
    # Separation de la chaine
    coords_string = wkt.split("(")
    coords_string = coords_string[1]
    coords_string = coords_string.split(")")[0]

    coords = coords_string.split(",")
    
    for i in range(0, len(coords)):
        sl = coords[i].strip().split(" ")
        x = float(sl[0])
        y = float(sl[1])
        if (len(sl) == 3):
            z = float(sl[2])
        else:
            z = 0.0

        if not srid.upper() in ["ENUCOORDS", "ENU", "GEOCOORDS", "GEO", "ECEFCOORDS", "ECEF"]:
            print("Error: unknown coordinate type ["+str(srid)+"]")
            exit()
                    
        if (srid.upper() in ["ENUCOORDS", "ENU"]):
            point = ENUCoords(x,y,z)
        if (srid.upper() in ["GEOCOORDS", "GEO"]):
            point = GeoCoords(x,y,z)
        if (srid.upper() in ["ECEFCOORDS", "ECEF"]):
            point = ECEFCoords(x,y,z)  

        TAB_OBS.append(Obs(point, GPSTime()))                  

    return TAB_OBS



def tabCoordsLineStringToObs(coords, srid):
    
    # Creation d'une liste vide
    TAB_OBS = list()
    
    for i in range(0, len(coords)):
        sl = coords[i]
        x = float(sl[0])
        y = float(sl[1])
        if (len(sl) == 3):
            z = float(sl[2])
        else:
            z = 0.0

        if not srid.upper() in ["ENUCOORDS", "ENU", "GEOCOORDS", "GEO", "ECEFCOORDS", "ECEF"]:
            print("Error: unknown coordinate type ["+str(srid)+"]")
            exit()
                    
        if (srid.upper() in ["ENUCOORDS", "ENU"]):
            point = ENUCoords(x,y,z)
        if (srid.upper() in ["GEOCOORDS", "GEO"]):
            point = GeoCoords(x,y,z)
        if (srid.upper() in ["ECEFCOORDS", "ECEF"]):
            point = ECEFCoords(x,y,z)  

        TAB_OBS.append(Obs(point, GPSTime()))                  

    return TAB_OBS
