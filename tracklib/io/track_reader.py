# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Yann Méneroux
    marie-Dominique Van Damme
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

# For type annotation
from __future__ import annotations   
from typing import Union, Literal
from tracklib.util.exceptions import *

import csv
import io
import json
import os
from xml.dom import minidom

from . import TrackFormat
from tracklib.core import (ObsTime, ENUCoords, ECEFCoords, GeoCoords, Obs, 
                           islist, isfloat, makeCoords,TrackCollection)
from tracklib.core import Track



class TrackReader:
    """
    This class offer a static method to load track or track collection
    from GPX, CSV or WKT files. 
    Geometry can be structured in coordinates or in a wkt.
    """


    def readFromFile(path, track_format:Union[str, TrackFormat]="DEFAULT", verbose=False):
        '''
        Read track(s) from file(s) with geometry structured in coordinates or wkt.
        
        The method assumes a single track in file.
        
        If only path is provided as input parameters: file format is infered 
        from extension according to file track_file_format
        
        If only path and a string s parameters are provied, the name of file format 
        is set equal to s.


        Parameters
        ----------
        path : file or directory
            DESCRIPTION.
        track_format : str or dict
            name of format which describes metadata of the file
        verbose : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        TrackCollection
            collection of tracks contains in file(s).

        '''

        if not (os.path.isfile(path) or os.path.isdir(path)):
            raise WrongArgumentError("First parameter (path) doesn't refers to a file or a dir.")

        if not isinstance(track_format, str) and not isinstance(track_format, TrackFormat):
            raise WrongArgumentError("The second parameter is not an instantiation of a str or a TrackFormat: "
                                     + str(type(track_format)))

        if isinstance(track_format, TrackFormat):
            fmt = track_format
        else:
            # dict or str for name in ressource files
            fmt = TrackFormat(track_format)

        if fmt.ext is None:
            raise WrongArgumentError("Track format need have the EXT initialised (CSV, GPX, WKT)")
        if fmt.ext not in ['CSV', 'GPX', 'WKT'] and isinstance(track_format, TrackFormat):
            raise WrongArgumentError("Tracklib only read CSV, GPX and WKT files.")

        # num_lines = sum(1 for line in open(path))

        fmt.controlFormat()

        if verbose:
            print("Loading track(s) ...")

        if os.path.isdir(path):
            TRACES = TrackCollection()
            LISTFILE = os.listdir(path)
            for f in LISTFILE:
                # if path[len(path)-1:] == '/':
                #                     collection = TrackReader.readFromGpxFast(path + f)
                #                 else:
                #                     collection = TrackReader.readFromGpxFast(path + '/' + f)
                p = path + "/" + f

                trace = TrackReader.readFromFile(p, track_format, verbose)
                if trace is None:
                    continue

                if not fmt.selector is None:
                    if not fmt.selector.contains(trace):
                        continue

                if isinstance(trace, TrackCollection):
                    for i in range(trace.size()):
                        TRACES.addTrack(trace[i])
                else:
                    TRACES.addTrack(trace)

            return TRACES

        elif not os.path.isfile(path):
            return None

        if verbose:
             print("Loading file " + path)
             print("Extension: " + fmt.ext)

        # On redirige suivant l'extension: CSV, GPX or WKT
        if fmt.ext == "CSV":
            return TrackReader.__readFromCsv(path, fmt, verbose)
        elif fmt.ext == "GPX":
            return TrackReader.__readFromGpx(path, fmt, verbose)
        elif fmt.ext == "WKT":
            return TrackReader.__readFromWkt(path, fmt, verbose)
        else:
            return TrackReader.__readFromCsv(path, fmt, verbose)



    @staticmethod
    def __readFromCsv(path: str, fmt:TrackFormat, verbose) -> Union(Track, TrackCollection):
        """
        Read track(s) from CSV file(s) with geometry structured in coordinates.

            path : file or directory
                DESCRIPTION.
            track_format : str or dict
                name of format which describes metadata of the file
            verbose : TYPE, optional
                DESCRIPTION. The default is False.
            :return: a Track contains in csv files.
        """

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
            for i in range(fmt.header):
                line = fp.readline()
                if line[0] == fmt.cmt:
                    line = line[1:]
                name_non_special = line.split(fmt.separator)

            line = fp.readline().strip()

            # Obs per line
            while line:

                if line.strip()[0] == fmt.cmt:
                    name_non_special = line[1:].split(fmt.separator)
                    line = fp.readline().strip()
                    continue

                fields = line.strip().split(fmt.separator)
                fields = [s for s in fields if s]
                if (verbose):
                    print(fields)
                    
                if fmt.id_T != -1:
                    if isinstance(fmt.time_ini, int):
                        try:
                            T = fields[fmt.id_T].strip().replace('"', '')
                            time = ObsTime.readTimestamp(T)
                        except ValueError:
                            time = ObsTime()
                            if verbose:
                                print (fields[fmt.id_T].strip().replace('"', ''))
                    else:
                        time = fmt.time_ini.addSec((float)(fields[fmt.id_T])*fmt.time_unit)
                else:
                    time = ObsTime()
                
                # Blank fields
                if (fields[fmt.id_E].strip() == '' or fields[fmt.id_E].strip() == 'NA'):
                    fields[fmt.id_E] = fmt.no_data_value
                if (fields[fmt.id_N].strip() == '' or fields[fmt.id_N].strip() == 'NA'):
                    fields[fmt.id_N] = fmt.no_data_value
                if (fmt.id_U >= 0 and fields[fmt.id_U].strip() == ''):
                    fields[fmt.id_U] = fmt.no_data_value

                try:
                    E = (float)(fields[fmt.id_E])
                    N = (float)(fields[fmt.id_N])
                except:
                    raise WrongArgumentError("Parameter E or N is not an instantiation of a float (" + path + ")")

                if (int(E) != fmt.no_data_value) and (int(N) != fmt.no_data_value):
    
                    if fmt.id_U >= 0:
                        U = (float)(fields[fmt.id_U])
                    else:
                        U = 0

                    if not fmt.srid.upper() in [
                        "ENUCOORDS", "ENU", "GEOCOORDS", "GEO", "ECEFCOORDS", "ECEF",
                    ]:
                        raise WrongArgumentError("Error: unknown coordinate type [" + str(srid) + "]")
                    if fmt.srid.upper() in ["ENUCOORDS", "ENU"]:
                        point = Obs(ENUCoords(E, N, U), time)
                    if fmt.srid.upper() in ["GEOCOORDS", "GEO"]:
                        point = Obs(GeoCoords(E, N, U), time)
                    if fmt.srid.upper() in ["ECEFCOORDS", "ECEF"]:
                        point = Obs(ECEFCoords(E, N, U), time)
    
                    track.addObs(point)
                        
                else:
                    no_data = fmt.no_data_value
                    track.addObs(Obs(makeCoords(no_data, no_data, no_data, fmt.srid.upper()), time))

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
                for i in range(fmt.header):
                    fp.readline()

                line = fp.readline()

                counter = 0
                while line:
                    if line.strip()[0] == fmt.cmt:
                        line = fp.readline().strip()
                        continue

                    fields = line.split(fmt.separator)
                    fields = [s for s in fields if s]
                    if (verbose):
                        print(fields)
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

        if not fmt.selector is None:
            if not fmt.selector.contains(track):
                return None

        track.no_data_value = fmt.no_data_value

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
    def __readFromWkt(path:str, fmt:TrackFormat, verbose=False) -> TrackCollection:
        """
        Read track(s) (one per line) from a CSV file, with geometry provided in wkt.

        Parameters
        -----------

        :param str path of wkt file
        :param track_format : str or dict
               name of format which describes metadata of the file
        :param verbose : TYPE, optional
               The default is False.
       
        :return: collection of tracks contains in wkt files.
        """

        TRACES = TrackCollection()

        with open(path, newline="") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=fmt.separator, doublequote=fmt.doublequote)

            # Header
            for i in range(fmt.header):
                next(spamreader)

            for fields in spamreader:
                if len(fields) <= 0:
                    continue

                track = Track()
                if fmt.id_user >= 0:
                    track.uid = fields[fmt.id_user]
                if fmt.id_track >= 0:
                    track.tid = fields[fmt.id_track]

                wkt = fields[fmt.id_wkt]
                if wkt[0:4] == "POLY":
                    wkt = fields[fmt.id_wkt].split("((")[1].split("))")[0]
                    wkt = wkt.split(",")
                elif wkt[0:4] == "LINE":
                    wkt = fields[fmt.id_wkt].split("(")[1].split(")")[0]
                    wkt = wkt.split(",")
                elif wkt[0:7] == "MULTIPO":
                    wkt = fields[fmt.id_wkt].split("((")[1].split("))")[0]
                    wkt = wkt.split(",")
                    if wkt[0] == "(":
                        wkt = wkt[1:]
                    wkt = wkt.split("),(")[0]  # Multipolygon not handled yet
                else:
                    raise WrongArgumentError("This type of wkt is not yet implemented.")

                for s in wkt:
                    sl = s.strip().split(" ")
                    x = float(sl[0])
                    y = float(sl[1])
                    if len(sl) == 3:
                        z = float(sl[2])
                    else:
                        z = 0.0
                        
                    point = Obs(makeCoords(x, y, z, fmt.srid.upper()), ObsTime())
                    track.addObs(point)

                if not fmt.selector is None:
                    if not fmt.selector.contains(track):
                        continue

                TRACES.addTrack(track)
                if verbose:
                    print(len(TRACES), " wkt tracks loaded")

        return TRACES


    # =========================================================================
    #   GPX
    #
    @staticmethod
    def __readFromGpx(path:str, fmt:TrackFormat, verbose) -> TrackCollection:
        fichier = open(path, 'r')
        LINES = fichier.readlines()
        tracks = TrackCollection()
        new_track = False

        if fmt.type == 'trk':
            for line in LINES:
                if ('<'+fmt.type+'>' in line):
                    new_track = True
                    new_point = False
                    tracks.addTrack(Track())
                if ('</'+fmt.type+'>' in line):
                    new_track = False
                if new_track:
                    if ('<'+fmt.type+'pt ' in line):
                        new_point = True
                        splits = line.split("\"")
                        pos = makeCoords(float(splits[3]), float(splits[1]), 0, fmt.srid)
                    if ('</'+fmt.type+'pt>' in line):
                        new_point = False
                        tracks[-1].addObs(Obs(pos, tps))
                    if new_point:
                        if '<ele>' in line:
                            pos.hgt = float(line.split('>')[1].split('<')[0])
                        if '<time>' in line:
                            tps = ObsTime(line.split('>')[1].split('<')[0])

        if fmt.type == 'rte':
            tracks.addTrack(Track())
            for line in LINES:
                if ('<'+fmt.type+'pt' in line):
                    splits = line.split("\"")
                    pos = makeCoords(float(splits[3]), float(splits[1]), 0, fmt.srid)
                    tracks[-1].addObs(Obs(pos))

        fichier.close()
        return tracks


#     @staticmethod
#     def readFromGpx(path:str, 
#                     srid:Literal["GEO", "ENU"] ="GEO", 
#                     type: Literal["trk", "rte"]="trk",
#                     read_all=False, verbose=False) -> TrackCollection:
#         """
#         Reads (multiple) tracks or routes from gpx file(s).
        
#         Parameters
#         -----------
        
#         :param str path: file or directory
#         :param str srid: coordinate system of points ("ENU", "Geo" or "ECEF") 
#         :param str type: may be “trk” to load track points or 
#                          “rte” to load vertex from the route
#         :param bool read_all: if flag read_all is True, read AF in the tag extension 
                   
#         :return: collection of tracks contains in Gpx files.
#         """
             
#         if os.path.isdir(path):
#             TRACES = TrackCollection()
#             LISTFILE = os.listdir(path)
#             for f in LISTFILE:
#                 if verbose:
#                     print(f)
#                 if path[len(path)-1:] == '/':
#                     collection = TrackReader.readFromGpx(path + f)
#                 else:
#                     collection = TrackReader.readFromGpx(path + '/' + f)
#                 for i in range(collection.size()):
#                     TRACES.addTrack(collection[i])
#             return TRACES
        
#         elif os.path.isfile(path) or isinstance(io.StringIO(path), io.IOBase):
#             #format_old = ObsTime.getReadFormat()
#             #ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
            
#             collection = TrackCollection()
    
#             doc = minidom.parse(path)
#             trks = doc.getElementsByTagName(type)

#             for trk in trks:
#                 if os.path.basename(path).split(".")[0] != None:
#                     trace = Track(track_id=os.path.basename(path).split(".")[0])
#                 else:
#                     trace = Track()
                
#                 extensions = dict()
#                 trkpts = trk.getElementsByTagName(type + "pt")
#                 for trkpt in trkpts:
#                     lon = float(trkpt.attributes["lon"].value)
#                     lat = float(trkpt.attributes["lat"].value)
    
#                     hgt = -1 # TODO: utils.NAN
#                     eles = trkpt.getElementsByTagName("ele")
#                     if eles.length > 0:
#                         hgt = float(eles[0].firstChild.data)
    
#                     time = ""
#                     times = trkpt.getElementsByTagName("time")
#                     if times.length > 0:
#                         time = ObsTime(times[0].firstChild.data)
#                     else:
#                         time = ObsTime()
    
#                     point = Obs(makeCoords(lon, lat, hgt, srid), time)
#                     trace.addObs(point)
                    
#                     if read_all:
#                         tagextentions = trkpt.getElementsByTagName("extensions")
#                         for tagextention in tagextentions:
#                             for ext in tagextention.childNodes:
#                                 if ext.nodeType == minidom.Node.ELEMENT_NODE: 
#                                     if ext.tagName not in extensions:
#                                         extensions[ext.tagName] = []
#                                     val = ext.firstChild.nodeValue
#                                     if isfloat(val):
#                                         extensions[ext.tagName].append(float(val))
#                                     elif islist(val):
#                                         extensions[ext.tagName].append(json.loads(val))
#                                     else:
#                                         extensions[ext.tagName].append(val)
                    
#                     # ..
#                     # 
    
#                 if read_all:
#                     for key in extensions.keys():
#                         trace.createAnalyticalFeature(key)
#                         for i in range(trace.size()):
#                             trace.setObsAnalyticalFeature(key, i, extensions[key][i])
                        
#                 collection.addTrack(trace)

#             # pourquoi ?
#             # --> pour remettre le format comme il etait avant la lecture :)   
#             #ObsTime.setReadFormat(format_old)
    
#             #collection = TrackCollection([trace])
#             return collection
        
#         else:
#             print ('path is not a file, not a dir')
#             return None


    @staticmethod
    def readFromWkt(path:str, id_geom, id_user=-1, id_track=-1,
                        separator=";", h=0, srid="ENUCoords",
                        bboxFilter=None, 
                        doublequote:bool=False,
                        verbose=False):
        track_format = TrackFormat({'ext': 'WKT',
                                    'id_wkt': id_geom,
                                    'id_user': id_user,
                                    'id_track': id_track,
                                    'separator': separator,
                                    'header': h,
                                    'srid': srid,
                                    'doublequote': doublequote})
        return TrackReader.readFromFile(path, track_format, verbose)

    @staticmethod
    def readFromGpx(path:str,
            srid: Literal["GEO", "ENU"] ="GEO", 
            type: Literal["trk", "rte"]="trk",
            read_all=False, verbose=False) -> TrackCollection:
        track_format = TrackFormat({'ext': 'GPX',
                                    'type': type,
                                    'srid': srid,
                                    'read_all': read_all})
        return TrackReader.readFromFile(path, track_format, verbose)

    @staticmethod
    def readFromCsv (path: str,
                     id_E:int=-1, id_N:int=-1, id_U:int=-1, id_T:int=-1,
                     separator:str=",", DateIni=-1,  timeUnit=1,   h=0,
                     com="#", no_data_value=-999999, srid="ENUCoords",
                     read_all=False, selector=None, verbose=False):
        track_format = TrackFormat({'ext': 'CSV',
                                    'id_E': id_E,
                                    'id_N': id_N,
                                    'id_U': id_U,
                                    'id_T': id_T,
                                    'separator': separator,
                                    'time_ini': DateIni,
                                    'time_unit': timeUnit,
                                    'header': h,
                                    'com': com,
                                    'no_data_value': no_data_value,
                                    'srid': srid,
                                    'read_all': read_all,
                                    'selector': selector})
        return TrackReader.readFromFile(path, track_format, verbose)



