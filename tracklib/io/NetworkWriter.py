# -*- coding: utf-8 -*-

# For type annotation
from __future__ import annotations   
from typing import Literal   

from tracklib.core.Network import Network

class NetworkWriter:
    """
    Write Network to CSV or KML files.
    
    """

    @staticmethod
    def writeToCsv(network, path="", separator=",", h=1):
        """TODO"""

        if h == 1:
            output = "link_id" + separator
            output += "source" + separator
            output += "target" + separator
            output += "direction" + separator
            output += "wkt\n"
        else:
            output = ""

        for idedge in network.EDGES:
            edge = network.EDGES[idedge]
            output += edge.id + separator
            output += edge.source.id + separator
            output += edge.target.id + separator
            output += str(edge.orientation) + separator
            output += '"' + edge.geom.toWKT() + '"'
            output += "\n"

        if path:
            f = open(path, "w")
            f.write(output)
            f.close()

        return output
    
    
    @staticmethod
    def writeToKml(track, path, type: Literal["LINE", "POINT"] = "LINE", 
                   af=None, c1=[0, 0, 1, 1], c2=[1, 0, 0, 1], name=False):   
        """Transforms track/track collection/network into KML string

        :param path: file to write kml (kml returned in standard output if empty)
        :param type: "POINT" or "LINE"
        :param name: True -> label with point number (in GPS sequence)   
            Str  -> label with AF name (no name if AF value is empty or ".")
        :param af: AF used for coloring in POINT mode
        :param c1: color for min value (default blue) in POINT mode or color in "LINE" mode
        :param c2: color for max value (default red) in POINT mode
        """
        
        if isinstance(track, Network):
            return TrackWriter.__writeCollectionToKml(track.getAllEdgeGeoms(), path, c1)

        f = open(path, "w")

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
            print("Error in KmlWriter: type '" + type + "' unknown")
            exit()

        if type == "LINE":
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<kml xmlns="http://earth.google.com/kml/2.1">\n')
            f.write("  <Document>\n")
            f.write("    <Placemark>\n")
            f.write("      <name>Rover Track</name>\n")
            f.write("      <Style>\n")
            f.write("        <LineStyle>\n")
            f.write(
                "          <color>" + utils.rgbToHex(default_color)[2:] + "</color>\n"
            )
            f.write("        </LineStyle>\n")
            f.write("      </Style>\n")
            f.write("      <LineString>\n")
            f.write("        <coordinates>\n")

            for i in range(track.size()):
                f.write("          ")
                f.write("{:15.12f}".format(track.getObs(i).position.getX()) + ",")
                f.write("{:15.12f}".format(track.getObs(i).position.getY()))
                if not clampToGround:
                    f.write("," + "{:15.12f}".format(track.getObs(i).position.getZ()))
                f.write("\n")

            f.write("        </coordinates>\n")
            f.write("      </LineString>\n")
            f.write("    </Placemark>\n")
            f.write("  </Document>\n")
            f.write("</kml>\n")

        if type == "POINT":
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<kml xmlns="http://earth.google.com/kml/2.1">\n')
            f.write("  <Document>\n")

            for i in range(track.size()):
                f.write("    <Placemark>")
                if name:
                    if isinstance(name, str):
                        naf = str(track.getObsAnalyticalFeature(name, i)).strip()
                        if not (naf in ["", "."]):
                            f.write("      <name>" + naf + "</name>")
                    else:
                        f.write("      <name>" + str(i) + "</name>")
                f.write("      <Style>")
                f.write("        <IconStyle>")
                if not af is None:
                    v = track.getObsAnalyticalFeature(af, i)
                    default_color = utils.interpColors(v, vmin, vmax, c1, c2)
                f.write(
                    "          <color>" + utils.rgbToHex(default_color)[2:] + "</color>"
                )
                f.write("          <scale>0.3</scale>")
                f.write(
                    "          <Icon><href>http://maps.google.com/mapfiles/kml/pal2/icon18.png</href></Icon>"
                )
                f.write("        </IconStyle>")
                f.write("      </Style>")
                f.write("      <Point>")
                f.write("        <coordinates>")
                f.write("          ")
                f.write("{:15.12f}".format(track.getObs(i).position.getX()) + ",")
                f.write("{:15.12f}".format(track.getObs(i).position.getY()) + ",")
                f.write("{:15.12f}".format(track.getObs(i).position.getZ()))
                f.write("        </coordinates>")
                f.write("      </Point>")
                f.write("    </Placemark>\n")

            f.write("  </Document>\n")
            f.write("</kml>\n")

        f.close()
        print("KML written in file [" + path + "]")
