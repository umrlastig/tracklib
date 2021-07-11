# -*- coding: utf-8 -*-
'''
Write GPS track in KML file(s).


'''

import os
import progressbar

import tracklib.core.Utils as utils
import tracklib.core.Operator as Operator

from tracklib.core.Track import Track
from tracklib.core.Network import Network
from tracklib.core.Track import TrackCollection


class KmlWriter:
        
        
    @staticmethod
    def writeToKml(track, path="", type="LINE", af=None, c1=[0,0,1,1], c2=[1,0,0,1], name=False):
        '''
        Transforms track/track collection/network into KML string
        path: file to write kml (kml returned in standard output if empty)
        type: "POINT" or "LINE"
        name:   True -> label with point number (in GPS sequence)
                Str  -> label with AF name (no name if AF value is empty or ".")
        af: AF used for coloring in POINT mode
        c1: color for min value (default blue) in POINT mode or color in "LINE" mode
        c2: color for max value (default red) in POINT mode
        '''
		
        # Track collection case
        if isinstance(track, TrackCollection):
            return KmlWriter.__writeCollectionToKml(track, path, c1)

        # Network case
        if isinstance(track, Network):
            return KmlWriter.__writeCollectionToKml(track.getAllEdgeGeoms(), path, c1)
        
        clampToGround = True
        for obs in track:
            if obs.position.getZ() != 0:
                clampToGround = False
                break
        
        if not af is None:
            vmin = track.operate(Operator.Operator.MIN, af)
            vmax = track.operate(Operator.Operator.MAX, af)
            
        default_color = c1

        if type not in ["LINE", "POINT"]:
            print("Error in KmlWriter: type '"+type+"' unknown")
            exit()            
        
        if type == "LINE":
            output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            output += "<kml xmlns=\"http://earth.google.com/kml/2.1\">\n"
            output += "<Document>\n"
            output += "<Placemark>\n"
            output += "<name>Rover Track</name>\n"
            output += "<Style>\n"
            output += "<LineStyle>\n"
            output += "<color>"+utils.rgbToHex(default_color)[2:]+"</color>\n"
            output += "</LineStyle>\n"
            output += "</Style>\n"
            output += "<LineString>\n"
            output += "<coordinates>\n"
            
            for i in range(track.size()):
                output += '{:15.12f}'.format(track.getObs(i).position.getX()) + "," 
                output += '{:15.12f}'.format(track.getObs(i).position.getY())
                if not clampToGround:
                    output += "," + '{:15.12f}'.format(track.getObs(i).position.getZ()) 
                output += "\n"
                
            output += "</coordinates>\n"
            output += "</LineString>\n"
            output += "</Placemark>\n"
            output += "</Document>\n"
            output += "</kml>\n"
            
        if type == "POINT":
            output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            output += "<kml xmlns=\"http://earth.google.com/kml/2.1\">\n"
            output += "<Document>\n"
        
            for i in range(track.size()):
                output += "<Placemark>"
                if name:
                    if isinstance(name, str):
                        naf = str(track.getObsAnalyticalFeature(name, i)).strip()
                        if not (naf in ["", "."]):
                            output += "<name>"+naf+"</name>"
                    else:
                        output += "<name>"+str(i)+"</name>"
                output += "<Style>"
                output += "<IconStyle>"
                if not af is None:
                    v = track.getObsAnalyticalFeature(af, i)
                    default_color = utils.interpColors(v, vmin, vmax, c1, c2)
                output += "<color>" + utils.rgbToHex(default_color)[2:] + "</color>"
                output += "<scale>0.3</scale>"
                output += "<Icon><href>http://maps.google.com/mapfiles/kml/pal2/icon18.png</href></Icon>"
                output += "</IconStyle>"
                output += "</Style>"
                output += "<Point>"
                output += "<coordinates>"
                output += '{:15.12f}'.format(track.getObs(i).position.getX()) + "," 
                output += '{:15.12f}'.format(track.getObs(i).position.getY()) + ","
                output += '{:15.12f}'.format(track.getObs(i).position.getZ())
                output += "</coordinates>"
                output += "</Point>"
                output += "</Placemark>\n"
                
            output += "</Document>\n"
            output += "</kml>\n"
                        
        if path:
            f = open(path, "w")
            f.write(output)
            f.close()
            return "KML written in file [" + path + "]" 
            
        return output
      
      
    def __writeCollectionToKml(tracks, path="", c1=[1,1,1,1]):
        
        clampToGround = True

        default_color = c1
        
        output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        output += "<kml xmlns=\"http://earth.google.com/kml/2.1\">\n"
        output += "<Document>\n"
		
        print("KML writing...")
        for j in progressbar.progressbar(range(tracks.size())):

            track = tracks[j]			

            output += "<Placemark>\n"
            output += "<name>"+str(track.tid)+"</name>\n"
            output += "<Style>\n"
            output += "<LineStyle>\n"
            output += "<color>"+utils.rgbToHex(default_color)[2:]+"</color>\n"
            output += "</LineStyle>\n"
            output += "</Style>\n"

            output += "<LineString>\n"
            output += "<coordinates>\n"
            
            for i in range(track.size()):
                output += '{:15.12f}'.format(track.getObs(i).position.getX()) + "," 
                output += '{:15.12f}'.format(track.getObs(i).position.getY())
                if not clampToGround:
                    output += "," + '{:15.12f}'.format(track.getObs(i).position.getZ()) 
                output += "\n"
                
            output += "</coordinates>\n"
            output += "</LineString>\n"

            output += "</Placemark>\n"

        output += "</Document>\n"
        output += "</kml>\n"
        
        if path:
            f = open(path, "w")
            f.write(output)
            f.close()
            return "KML written in file [" + path + "]" 
            
        return output
                   