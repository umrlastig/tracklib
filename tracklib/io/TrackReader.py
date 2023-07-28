# -*- coding: utf-8 -*-

# For type annotation
from __future__ import annotations   
from typing import Union, Literal

import csv
import io
import os
from xml.dom import minidom

from tracklib import (ObsTime, ENUCoords, ECEFCoords, GeoCoords, Obs, 
                      makeCoords, islist, isfloat)
from tracklib.core.Track import Track
from tracklib.core.TrackCollection import TrackCollection
from tracklib.io.TrackFormat import TrackFormat


class TrackReader:
    """
    This class offers static methods to load track or track collection
    from GPX, CSV files. Geometry can be structured in coordinates or in a wkt.
    """

    @staticmethod
    def readFromCsv (path: str,
        id_E:int=-1, id_N:int=-1, id_U:int=-1, id_T:int=-1,
        separator:str=",",
        DateIni=-1,
		timeUnit=1,
        h=0,
        com="#",
        no_data_value=-999999,
        srid="ENUCoords",
        read_all=False,
        selector=None,
        verbose=False,
    ) -> Union(Track, TrackCollection):
        """
        Read track(s) from CSV file(s) with geometry structured in coordinates.
        
        The method assumes a single track in file.
        
        If only path is provided as input parameters: file format is infered 
        from extension according to file track_file_format
        
        If only path and a string s parameters are provied, the name of file format 
        is set equal to s.
        
        Parameters
        -----------
        
        :param str path: file or directory
        :param int id_E: index (starts from 0) of column containing coordinate X (for ECEF), 
                         longitude (GEO) or E (ENU)
                         -1 if file format is used
        :param int id_N: index (starts from 0) of column containing coordinate Y (for ECEF), 
                         latitude (GEO) or N (ENU)
                         -1 if file format is used
        :param int id_U: index (starts from 0) of column containing Z (for ECEF), 
                         height or altitude (GEO/ENU)
                         -1 if file format is used
        :param int id_T: index (starts from 0) of column containing timestamp 
                         (in seconds x timeUnit or in time_fmt format)
                         -1 if file format is used
        :param str separator: separating characters (can be multiple characters). 
                              Can be c (comma), b (blankspace), s (semi-column)
        :param GPSTime DateIni: initial date (in time_fmt format) if timestamps 
                                are provided in seconds (-1 if not used)
        :param float timeUnit: number of seconds per unit of time in id_T column
        :param int h: number of heading line
        :param str com: comment character (lines starting with cmt on the top left 
                        are skipped)
        :param int no_data_value: a special float or integer indicating 
                                  that record is non-valid and should be skipped
        :param str srid: coordinate system of points ("ENU", "Geo" or "ECEF") 
        :param bool read_all: if flag read_all is True, read AF in the tag extension 
        :param Selector selector: to select track with a Selection which combine 
                                  different constraint
                                  
        :return: a track or a collection of tracks contains in wkt files.
        """
        
        if os.path.isdir(path):
            TRACES = TrackCollection()
            
            LISTFILE = os.listdir(path)
            for f in LISTFILE:
                
                p = path + "/" + f
                trace = TrackReader.readFromCsv(
                    p, id_E, id_N, id_U, id_T,
                    separator, DateIni, timeUnit, h, com, no_data_value,
                    srid, read_all, selector, verbose,
                )
                
                if trace is None:
                    continue
                
                if not selector is None:
                    if not selector.contains(trace):
                        continue
                    
                TRACES.addTrack(trace)

            return TRACES
            
        elif not os.path.isfile(path):
            return None
        
        if verbose:
            print("Loading file " + path)

        # -------------------------------------------------------
        # Infering file format from extension or name
        # -------------------------------------------------------
        if id_N == -1:
            if id_E == -1:
                fmt = TrackFormat(path, 1)  # Read by extension
            else:
                fmt = TrackFormat(id_E, 0)  # Read by name
        else:
            fmt = TrackFormat("", -1)  # Read from input parameters
            fmt.id_E = id_E
            fmt.id_N = id_N
            fmt.id_U = id_U
            fmt.id_T = id_T
            fmt.DateIni = DateIni
            fmt.separator = separator
            fmt.h = h
            fmt.com = com
            fmt.no_data_value = no_data_value
            fmt.srid = srid
            fmt.read_all = read_all

        # -------------------------------------------------------
        # Reading data according to file format
        # -------------------------------------------------------
        if os.path.basename(path).split(".")[0] != None:
            track = Track(track_id=os.path.basename(path).split(".")[0])
        else:
            track = Track()

        time_fmt_save = ObsTime.getReadFormat()
        ObsTime.setReadFormat(fmt.time_fmt)

        id_special = [fmt.id_E, fmt.id_N]
        if fmt.id_U >= 0:
            id_special.append(fmt.id_U)
        if fmt.id_T >= 0:
            id_special.append(fmt.id_T)

        with open(path) as fp:

            # Header
            for i in range(fmt.h):
                line = fp.readline()
                if line[0] == fmt.com:
                    line = line[1:]
                name_non_special = line.split(fmt.separator)

            line = fp.readline().strip()

            # Obs per line
            while line:

                if line.strip()[0] == fmt.com:
                    name_non_special = line[1:].split(fmt.separator)
                    line = fp.readline().strip()
                    continue

                fields = line.strip().split(fmt.separator)
                fields = [s for s in fields if s]

                if fmt.id_T != -1:
                    if isinstance(fmt.DateIni, int):
                        time = ObsTime.readTimestamp(fields[fmt.id_T])
                    else:
                        time = fmt.DateIni.addSec((float)(fields[fmt.id_T])*timeUnit)
                else:
                    time = ObsTime()
                    
                # Blank fields
                '''
                if (fields[fmt.id_E].strip() == ''):
                    fields[fmt.id_E] = fmt.no_data_value
                if (fields[fmt.id_N].strip() == ''):
                    fields[fmt.id_N] = fmt.no_data_value
                if (fields[fmt.id_U].strip() == ''):
                    fields[fmt.id_U] = fmt.no_data_value
                '''

                E = (float)(fields[fmt.id_E])
                N = (float)(fields[fmt.id_N])

                if (int(E) != fmt.no_data_value) and (int(N) != fmt.no_data_value):

                    if fmt.id_U >= 0:
                        U = (float)(fields[fmt.id_U])
                    else:
                        U = 0

                    if not fmt.srid.upper() in [
                        "ENUCOORDS",
                        "ENU",
                        "GEOCOORDS",
                        "GEO",
                        "ECEFCOORDS",
                        "ECEF",
                    ]:
                        print("Error: unknown coordinate type [" + str(srid) + "]")
                        exit()
                    if fmt.srid.upper() in ["ENUCOORDS", "ENU"]:
                        point = Obs(ENUCoords(E, N, U), time)
                    if fmt.srid.upper() in ["GEOCOORDS", "GEO"]:
                        point = Obs(GeoCoords(E, N, U), time)
                    if fmt.srid.upper() in ["ECEFCOORDS", "ECEF"]:
                        point = Obs(ECEFCoords(E, N, U), time)

                    track.addObs(point)

                line = fp.readline().strip()

        fp.close()

        # Reading other features
        if fmt.read_all:

            name_non_special = [s.strip() for s in name_non_special if s]

            for i in range(len(fields)):
                if not (i in id_special):
                    track.createAnalyticalFeature(name_non_special[i])

            with open(path) as fp:

                # Header
                for i in range(fmt.h):
                    fp.readline()

                line = fp.readline()

                counter = 0

                while line:

                    if line.strip()[0] == fmt.com:
                        line = fp.readline().strip()
                        continue

                    fields = line.split(fmt.separator)
                    fields = [s for s in fields if s]
                    for i in range(len(fields)):
                        if not (i in id_special):
                            val = fields[i].strip()
                            if not (name_non_special[i][-1] == "&"):
                                try:
                                    val = float(val)
                                except ValueError:
                                    val = str(val).replace('"', "")
                            track.setObsAnalyticalFeature(
                                name_non_special[i], counter, val
                            )

                    line = fp.readline().strip()
                    counter += 1

            fp.close()

        ObsTime.setReadFormat(time_fmt_save)
        
        if track is None:
            return None

        if not selector is None:
            if not selector.contains(track):
                return None

        if verbose:
            print ("  File " + path + " loaded: "
                + (str)(track.size())
                + " point(s) registered")
        
        return track


    NMEA_GGA = "GGA"
    NMEA_RMC = "RMC"
    NMEA_GPGGA = "GPGGA"
    NMEA_GNGGA = "GNGGA"
    NMEA_GPRMC = "GPRMC"
    NMEA_GNRMC = "GNRMC"

    @staticmethod
    def readFromNMEA(path, frame=NMEA_GGA):
        """The method assumes a single track in file."""

        track = Track()

        if frame.upper() == TrackReader.NMEA_GGA:
            pattern = ["$GNGGA"]
            TMP_NB_SATS = []
            TMP_HDOP = []

            with open(path, "rb") as fp:
                line = str(fp.readline())
                while not (line in ["", "b''"]):
                    if pattern[0] in line:
                        frame = line.split(pattern[0])[1]
                        fields = frame.split(",")
                        h = int(fields[1][0:2])
                        m = int(fields[1][2:4])
                        s = int(fields[1][4:6])
                        ms = int(fields[1][7:9])
                        time = ObsTime(hour=h, min=m, sec=s, ms=ms)
                        if fields[4] == "":
                            line = str(fp.readline())
                            continue
                        if fields[2] == "":
                            line = str(fp.readline())
                            continue
                        lon = float(fields[4]) / 100
                        lat = float(fields[2]) / 100
                        lon = int(lon) + (lon - int(lon)) * 100 / 60
                        lat = int(lat) + (lat - int(lat)) * 100 / 60
                        hgt = float(fields[9])
                        if fields[5] == "W":
                            lon = -lon
                        if fields[3] == "S":
                            lat = -lat
                        track.addObs(Obs(GeoCoords(lon, lat, hgt), time))
                        TMP_NB_SATS.append(int(fields[7]))
                        TMP_HDOP.append(float(fields[8]))
                        # print(fields)

                    line = str(fp.readline())

            track.createAnalyticalFeature("nb_sats")
            track.createAnalyticalFeature("hdop")

            for i in range(len(TMP_NB_SATS)):
                track.setObsAnalyticalFeature("nb_sats", i, TMP_NB_SATS[i])
                track.setObsAnalyticalFeature("hdop", i, TMP_HDOP[i])

        return track
    
    
    @staticmethod
    def readFromWkt(path:str, 
                        id_geom, id_user=-1, id_track=-1,
                        separator=";", h=0, srid="ENUCoords",
                        bboxFilter=None, 
                        doublequote:bool=False, 
                        verbose=False) -> TrackCollection:
        """
        Read track(s) (one per line) from a CSV file, with geometry provided in wkt.
        
        Parameters
        -----------
        
        :param str path: csv file
        :param int id_geom: index of the column that contains the geometry
        :param int id_user: index of the column that contains the id of the user of the track
        :param int id_track: index of the column that contains the id of the track
        :param str separator: separating characters (can be multiple characters). 
                              Can be c (comma), b (blankspace), s (semi-column)
        :param int h: number of heading line
        :param str srid: coordinate system of points ("ENU", "Geo" or "ECEF") 
        :param ?? bboxFilter: 
        :param bool doublequote: when True, quotechar is doubled. 
                                 When False, the escapechar is used as a prefix to the quotechar
        
        :return: collection of tracks contains in wkt files.
        """

        if separator == " ":
            print("Error: separator must not be space for reading WKT file")
            exit()

        TRACES = TrackCollection()

        with open(path, newline="") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=separator, doublequote=doublequote)

            # Header
            for i in range(h):
                next(spamreader)

            for fields in spamreader:
                if len(fields) <= 0:
                    continue

                track = Track()
                if id_user >= 0:
                    track.uid = fields[id_user]
                if id_track >= 0:
                    track.tid = fields[id_track]

                wkt = fields[id_geom]
                if wkt[0:4] == "POLY":
                    wkt = fields[id_geom].split("((")[1].split("))")[0]
                    wkt = wkt.split(",")
                elif wkt[0:4] == "LINE":
                    wkt = fields[id_geom].split("(")[1].split(")")[0]
                    wkt = wkt.split(",")
                elif wkt[0:7] == "MULTIPO":
                    wkt = fields[id_geom].split("((")[1].split("))")[0]
                    wkt = wkt.split(",")
                    if wkt[0] == "(":
                        wkt = wkt[1:]
                    wkt = wkt.split("),(")[0]  # Multipolygon not handled yet
                else:
                    print("this type of wkt is not yet implemented")

                for s in wkt:
                    sl = s.split(" ")
                    x = float(sl[0])
                    y = float(sl[1])
                    if len(sl) == 3:
                        z = float(sl[2])
                    else:
                        z = 0.0
                        
                    point = Obs(makeCoords(x, y, z, srid.upper()), ObsTime())   
                    track.addObs(point)
                    

                if not (bboxFilter is None):
                    xmin = bboxFilter[0]
                    ymin = bboxFilter[1]
                    xmax = bboxFilter[2]
                    ymax = bboxFilter[3]
                    for j in range(len(track)):
                        inside = True
                        inside = inside & (track[j].position.getX() > xmin)
                        inside = inside & (track[j].position.getY() > ymin)
                        inside = inside & (track[j].position.getX() < xmax)
                        inside = inside & (track[j].position.getY() < ymax)
                        if not inside:
                            break
                    if not inside:
                        continue

                TRACES.addTrack(track)
                if verbose:
                    print(len(TRACES), " wkt tracks loaded")

        return TRACES
    
    # =========================================================================
    #   GPX
    #
    @staticmethod
    def readFromGpx(path:str, 
                    srid:Literal["GEO", "ENU"] ="GEO", 
                    type: Literal["trk", "rte"]="trk",
                    read_all=False) -> TrackCollection:
        """
        Reads (multiple) tracks or routes from gpx file(s).
        
        Parameters
        -----------
        
        :param str path: file or directory
        :param str srid: coordinate system of points ("ENU", "Geo" or "ECEF") 
        :param str type: may be “trk” to load track points or 
                         “rte” to load vertex from the route
        :param bool read_all: if flag read_all is True, read AF in the tag extension 
                   
        :return: collection of tracks contains in Gpx files.
        """
             
        TRACES = TrackCollection()
        
        if os.path.isdir(path):
            LISTFILE = os.listdir(path)
            for f in LISTFILE:
                if path[len(path)-1:] == '/':
                    collection = TrackReader.readFromGpx(path + f)
                else:
                    collection = TrackReader.readFromGpx(path + '/' + f)
                TRACES.addTrack(collection.getTrack(0))
            return TRACES
        
        elif os.path.isfile(path) or isinstance(io.StringIO(path), io.IOBase):
            format_old = ObsTime.getReadFormat()
            ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
    
            doc = minidom.parse(path)
            trks = doc.getElementsByTagName(type)

            for trk in trks:
                if os.path.basename(path).split(".")[0] != None:
                    trace = Track(track_id=os.path.basename(path).split(".")[0])
                else:
                    trace = Track()
                
                extensions = dict()
                trkpts = trk.getElementsByTagName(type + "pt")
                for trkpt in trkpts:
                    lon = float(trkpt.attributes["lon"].value)
                    lat = float(trkpt.attributes["lat"].value)
    
                    hgt = -1 # TODO: utils.NAN
                    eles = trkpt.getElementsByTagName("ele")
                    if eles.length > 0:
                        hgt = float(eles[0].firstChild.data)
    
                    time = ""
                    times = trkpt.getElementsByTagName("time")
                    if times.length > 0:
                        time = ObsTime(times[0].firstChild.data)
                    else:
                        time = ObsTime()
    
                    point = Obs(makeCoords(lon, lat, hgt, srid), time)
                    trace.addObs(point)
                    
                    if read_all:
                        tagextentions = trkpt.getElementsByTagName("extensions")
                        for tagextention in tagextentions:
                            for ext in tagextention.childNodes:
                                if ext.nodeType == minidom.Node.ELEMENT_NODE: 
                                    if ext.tagName not in extensions:
                                        extensions[ext.tagName] = []
                                    val = ext.firstChild.nodeValue
                                    if isfloat(val):
                                        extensions[ext.tagName].append(float(val))
                                    elif islist(val):
                                        import json
                                        extensions[ext.tagName].append(json.loads(val))
                                    else:
                                        extensions[ext.tagName].append(val)
                    
                    # ..
                    # 
    
                if read_all:
                    for key in extensions.keys():
                        trace.createAnalyticalFeature(key)
                        for i in range(trace.size()):
                            trace.setObsAnalyticalFeature(key, i, extensions[key][i])
                        
                TRACES.addTrack(trace)

            # pourquoi ?
            # --> pour remettre le format comme il etait avant la lecture :)   
            ObsTime.setReadFormat(format_old)
    
            collection = TrackCollection(TRACES)
            return collection
        
        else:
            print ('path is not a file, not a dir')
            return None
    
    
    
        
