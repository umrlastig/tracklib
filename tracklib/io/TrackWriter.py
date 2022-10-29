# -*- coding: utf-8 -*-

# For type annotation
from __future__ import annotations   
from typing import Literal, Union   

import os
import progressbar
import sys 

from tracklib.core.GPSTime import GPSTime
from tracklib.io.TrackFormat import TrackFormat
from tracklib.core.Network import Network
from tracklib.core.Track import Track
from tracklib.core.Track import TrackCollection
import tracklib.core.Utils as utils
import tracklib.core.Operator as Operator


class TrackWriter:
    """
    Write track to CSV, GPX or KML file(s).
    - writeToFile
    - writeToFiles
    - writeToKml
    - __writeCollectionToKml
    - writeToGpx
    - writeToOneGpx
    """

    def __takeFirst(elem):
        return elem[0]

    def __printInOrder(E, N, U, T, headerAF, O, sep):
        D = [E, N, U, T]
        output = ""
        output += str(D[O[0][1]]).strip() + sep
        output += str(D[O[1][1]]).strip() + sep
        output += str(D[O[2][1]]).strip() + sep
        output += str(D[O[3][1]]).strip()
        output += headerAF
        return output


    @staticmethod
    def writeToFile (track, path, id_E=-1, id_N=-1, id_U=-1, id_T=-1, 
                     separator=",", h=0, af_names=[]):
        """
        The method assumes a single track in file. <br/>
        
        If only path is provided as input parameters: file format is infered 
        from extension according to file track_file_format.<br/>
        
        If only path and a string s parameters are provied, 
        the name of file format is set equal to s.<br/>
        
        :param track: track
        :param path: path to write information of the track
        :param id_E: index (starts from 0) of column containing coordinate X (for ECEF), longitude (GEO) or E (ENU)
        :param id_N: index (starts from 0) of column containing coordinate Y (for ECEF), latitude (GEO) or N (ENU)
        :param id_U: index (starts from 0) of column containing Z (for ECEF), height or altitude (GEO/ENU)
        :param id_T: index (starts from 0) of column containing timestamp (in seconds or in time_fmt format)
        :param separator: separating characters (can be multiple characters). Can be c (comma), b (blankspace), s (semi-column)
        :param h: display heading (1) or not (0)
        :param af_names:
        """

        # -------------------------------------------------------
        # Infering file format from extension or name
        # -------------------------------------------------------
        if id_N == -1:
            if id_E == -1:
                fmt = TrackFormat(path, -1)  # Read by extension
            else:
                fmt = TrackFormat(id_E, 0)  # Read by name
        else:
            fmt = TrackFormat("", -1)  # Read from input parameters
            fmt.id_E = id_E
            fmt.id_N = id_N
            fmt.id_U = id_U
            fmt.id_T = id_T
            fmt.separator = separator
            fmt.h = h

        # -------------------------------------------------------
        # Data order
        # -------------------------------------------------------
        O = [(fmt.id_E, 0), (fmt.id_N, 1), (fmt.id_U, 2), (fmt.id_T, 3)]
        headerAF = ""
        if len(af_names) > 0:
            for idx, af_name in enumerate(af_names):
                O.append((4 + idx, 4 + idx))
                headerAF += fmt.separator + af_name
        O.sort(key=TrackWriter.__takeFirst)

        # -------------------------------------------------------
        # Writing data
        # -------------------------------------------------------
        f = open(path, "w")

        # Header
        if fmt.h > 0:
            f.write(fmt.com + "srid: " + track.getSRID() + "\n")
            if isinstance(fmt.DateIni, GPSTime):
                f.write(fmt.com + "Reference epoch: " + fmt.DateIni + "\n")
            
            if track.getSRID().upper() == "ENU":
                f.write(
                    fmt.com
                    + TrackWriter.__printInOrder(
                        "E", "N", "U", "time", headerAF, O, fmt.separator)
                    + "\n"
                )
            if track.getSRID().upper() == "GEO":
                f.write(
                    fmt.com
                    + TrackWriter.__printInOrder(
                        "lon", "lat", "h", "time", headerAF, O, fmt.separator)
                    + "\n"
                )
            if track.getSRID().upper() == "ECEF":
                f.write(
                    fmt.com
                    + TrackWriter.__printInOrder("X", "Y", "Z", "time", 
                                                headerAF, O, fmt.separator)
                    + "\n"
                )

        # Data
        if track.getSRID().upper() == "ENU":
            float_fmt = "{:10.3f}"
        if track.getSRID().upper() == "GEO":
            float_fmt = "{:20.10f}"
        if track.getSRID().upper() == "ECEF":
            float_fmt = "{:10.3f}"
        
        for i in range(track.size()):
            x = float_fmt.format(track.getObs(i).position.getX())
            y = float_fmt.format(track.getObs(i).position.getY())
            z = float_fmt.format(track.getObs(i).position.getZ())
            t = track.getObs(i).timestamp
            if isinstance(fmt.DateIni, GPSTime):
                t = t.toAbsTime() - fmt.DateIni.toAbsTime()
            
            afs = ""
            if len(af_names) > 0:
                for af_name in af_names:
                    afs += fmt.separator + str(track.getObsAnalyticalFeature(af_name, i))
                    
            f.write(TrackWriter.__printInOrder(x, y, z, t,
                                              afs, O, fmt.separator) + "\n")

        f.close()

    
    @staticmethod
    def writeToFiles(trackCollection, pathDir, ext, id_E=-1, id_N=-1, id_U=-1, 
                     id_T=-1, separator=",", h=0):
        """TODO"""

        root = "track_output"

        for i in range(trackCollection.size()):
            track = trackCollection.getTrack(i)
            path = pathDir + "/" + root + "{:04d}" + "." + ext
        if id_N == -1:
            if id_E == -1:
                TrackWriter.writeToFile(track, path)  # Read by extension
            else:
                TrackWriter.writeToFile(track, path, id_E)  # Read by name
        else:
            TrackWriter.writeToFile(
                track, path, id_E, id_N, id_U, id_T, separator, h
            )  # Read from input parameters


    # =========================================================================
    #   KML
    #
    @staticmethod
    def writeToKml(track, path, 
                   type: Literal["LINE", "POINT"] = "LINE", 
                   af=None, 
                   c1=[0, 0, 1, 1], c2=[1, 0, 0, 1], name=False):   
        """
        Write GPS track in KML file(s).
        
        Transforms track/track collection into KML string

        :param path: file to write kml (kml returned in standard output if empty)
        :param type: "POINT" or "LINE"
        :param name: True -> label with point number (in GPS sequence)   
            Str  -> label with AF name (no name if AF value is empty or ".")
        :param af: AF used for coloring in POINT mode
        :param c1: color for min value (default blue) in POINT mode or color in "LINE" mode
        :param c2: color for max value (default red) in POINT mode
        """

        # Track collection case
        if isinstance(track, TrackCollection):
            return TrackWriter.__writeCollectionToKml(track, path, c1)

        # Network case
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

    def __writeCollectionToKml(tracks, path, c1=[1, 1, 1, 1]):
        """TODO"""

        clampToGround = True
        f = open(path, "w")

        default_color = c1

        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://earth.google.com/kml/2.1">\n')
        f.write("  <Document>\n")

        print("KML writing...")
        for j in progressbar.progressbar(range(tracks.size())):

            track = tracks[j]

            f.write("    <Placemark>\n")
            f.write("      <name>" + str(track.tid) + "</name>\n")
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

        f.close()
        print("KML written in file [" + path + "]")
        
        
    # =========================================================================
    #   GPX
    #
    def __getGpxHeader():
        txt = '<?xml version="1.0" encoding="UTF-8"?>\n'
        txt += '<gpx>\n'
        txt += '<metadata>\n'
        txt += "<author>File generated by Tracklib: "
        txt += "https://github.com/umrlastig/tracklib</author>\n"
        txt += "<time>" + str(GPSTime.now()) + "</time>"
        txt += '</metadata>\n'
        return txt
    
    gpxfile_extension = ["gpx"]
    
    @staticmethod
    def writeToGpx(tracks:Union[Track,TrackCollection], path:str, 
                   af:bool=False, oneFile:bool=True):
        """
        Transforms track into Gpx string
        
        Todo: type: Literal["trk", "rte"]="trk"
        
        Parameters
        -----------
        
        tracks Track or TrackCollection
               track or collection to write in GPX
        
        path str
            file or directory to write
            (gpx returned in standard output if empty)
            
        af
            AF exported in gpx file
            
        oneFile bool
            one file per track (default case) or one file for all tracks
            
        """
        
        if isinstance(tracks, Track):
            collection = TrackCollection()
            collection.addTrack(tracks)
            tracks = collection
        
        if not oneFile:
            if not os.path.isdir(path):
                print ("Error: path need to be a directory")
                exit()
            if path != '' and path[len(path) - 1:] != '/':
                path += '/'
        else:
            tabpath = path.split(".")
            if not path.split(".")[len(tabpath) - 1]  in TrackWriter.gpxfile_extension:
                print ("Error: path variable need to contain a file path")
                sys.exit()
            f = open(path, "w")

        # Time output management
        fmt_save = GPSTime.getPrintFormat()
        GPSTime.setPrintFormat("4Y-2M-2DT2h:2m:2s")
        
        if oneFile:
            f.write(TrackWriter.__getGpxHeader())
            
        for i in range(len(tracks)):
            track = tracks.getTrack(i)
            
            if not oneFile:
                filename = str(track.tid) + ".gpx"
                f = open(path + filename, "w")
                f.write(TrackWriter.__getGpxHeader())
            
            f.write("    <trk>\n")
            f.write("        <trkseg>\n")
            for i in range(len(track)):
                x = "{:3.8f}".format(track[i].position.getX())
                y = "{:3.8f}".format(track[i].position.getY())
                z = "{:3.8f}".format(track[i].position.getZ())
                f.write('            <trkpt lat="' + y + '" lon="' + x + '">\n')
                f.write("                <ele>" + z + "</ele>\n")
                f.write("                <time>"
                    + str(track[i].timestamp)
                    + track[i].timestamp.printZone()
                    + "</time>\n"
                )
                if af:
                    f.write("                <extensions>\n")
                    for af_name in track.getListAnalyticalFeatures():
                        f.write("                    <" + af_name + ">")
                        f.write(str(track.getObsAnalyticalFeature(af_name, i)))
                        f.write("</" + af_name + ">\n")
                    f.write("                </extensions>\n")
                f.write("            </trkpt>\n")
            f.write("        </trkseg>\n")
            f.write("    </trk>\n")
            
            if not oneFile:
                f.write("</gpx>\n")
                f.close()
        # end boucle for     

        if oneFile:
            f.write("</gpx>\n")
            f.close()
        
        # re-initialize time format
        GPSTime.setPrintFormat(fmt_save)


