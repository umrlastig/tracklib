"""Read GPS track from CSV file(s)."""

import csv
import os

from tracklib.core.GPSTime import GPSTime
from tracklib.core.Coords import ENUCoords
from tracklib.core.Coords import GeoCoords
from tracklib.core.Coords import ECEFCoords
from tracklib.core.Obs import Obs
from tracklib.core.Track import Track
from tracklib.core.TrackCollection import TrackCollection
import tracklib.core.Utils as utils
from tracklib.io.FileFormat import FileFormat


class FileReader:
    """TODO"""

    NMEA_GGA = "GGA"
    NMEA_RMC = "RMC"
    NMEA_GPGGA = "GPGGA"
    NMEA_GNGGA = "GNGGA"
    NMEA_GPRMC = "GPRMC"
    NMEA_GNRMC = "GNRMC"

    @staticmethod
    def readFromFile(
        path,
        id_E=-1,
        id_N=-1,
        id_U=-1,
        id_T=-1,
        separator=",",
        DateIni=-1,
        h=0,
        com="#",
        no_data_value=-999999,
        srid="ENUCoords",
        read_all=False,
        verbose=False,
    ):
        """
        The method assumes a single track in file.
        If only path is provided as input parameters: file format is infered from extension according to file track_file_format
        If only path and a string s parameters are provied, the name of file format is set equal to s.
        """

        # -------------------------------------------------------
        # Infering file format from extension or name
        # -------------------------------------------------------
        if id_N == -1:
            if id_E == -1:
                fmt = FileFormat(path, 1)  # Read by extension
            else:
                fmt = FileFormat(id_E, 0)  # Read by name
        else:
            fmt = FileFormat("", -1)  # Read from input parameters
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
        track = Track()

        time_fmt_save = GPSTime.getReadFormat()
        GPSTime.setReadFormat(fmt.time_fmt)

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

            while line:

                if line.strip()[0] == fmt.com:
                    name_non_special = line[1:].split(fmt.separator)
                    line = fp.readline().strip()
                    continue

                fields = line.strip().split(fmt.separator)
                fields = [s for s in fields if s]

                if fmt.id_T != -1:
                    if isinstance(fmt.DateIni, int):
                        time = GPSTime.readTimestamp(fields[fmt.id_T])
                    else:
                        time = fmt.DateIni.addSec((float)(fields[fmt.id_T]))
                else:
                    time = GPSTime()

                E = (float)(fields[fmt.id_E])
                N = (float)(fields[fmt.id_N])

                if (int(E) != fmt.no_data_value) and (int(N) != fmt.no_data_value):

                    if fmt.id_U >= 0:
                        U = (float)(fields[fmt.id_U])
                    else:
                        U = utils.NAN

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

        GPSTime.setReadFormat(time_fmt_save)

        if verbose:
            print(
                "File "
                + path
                + " loaded: \n"
                + (str)(track.size())
                + " point(s) registered"
            )

        return track

    @staticmethod
    def readFromFiles(
        pathdir,
        id_E=-1,
        id_N=-1,
        id_U=-1,
        id_T=-1,
        separator=",",
        DateIni=-1,
        h=0,
        com="#",
        no_data_value=-999999,
        srid="ENUCoords",
        read_all=False,
        verbose=False,
        selector=None,
    ):
        """TODO"""

        TRACES = TrackCollection()
        LISTFILE = os.listdir(pathdir)
        for f in LISTFILE:
            p = pathdir + "/" + f
            if TRACES.size() > 10:
                break
            print(TRACES.size())
            trace = FileReader.readFromFile(
                p,
                id_E,
                id_N,
                id_U,
                id_T,
                separator,
                DateIni,
                h,
                com,
                no_data_value,
                srid,
                read_all,
                verbose=False,
            )
            if not selector is None:
                if not selector.contains(trace):
                    continue
            TRACES.addTrack(trace)
            if verbose:
                print(
                    "File "
                    + p
                    + " loaded: \n"
                    + (str)(trace.size())
                    + " point(s) registered"
                )

        return TRACES

    @staticmethod
    def readFromWKTFile(
        path,
        id_geom,
        id_user=-1,
        id_track=-1,
        separator=";",
        h=0,
        srid="ENUCoords",
        bboxFilter=None,
        doublequote=False,
    ):
        """TODO"""

        if separator == " ":
            print("Error: separator must not be space for reading WKT file")
            exit()

        TRACES = TrackCollection()

        with open(path, newline="") as csvfile:
            spamreader = csv.reader(
                csvfile, delimiter=separator, doublequote=doublequote
            )

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
                    if not srid.upper() in [
                        "ENUCOORDS",
                        "ENU",
                        "GEOCOORDS",
                        "GEO",
                        "ECEFCOORDS",
                        "ECEF",
                    ]:
                        print("Error: unknown coordinate type [" + str(srid) + "]")
                        exit()
                    if srid.upper() in ["ENUCOORDS", "ENU"]:
                        point = ENUCoords(x, y, z)
                    if srid.upper() in ["GEOCOORDS", "GEO"]:
                        point = GeoCoords(x, y, z)
                    if srid.upper() in ["ECEFCOORDS", "ECEF"]:
                        point = ECEFCoords(x, y, z)

                    track.addObs(Obs(point, GPSTime()))

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

        return TRACES

    @staticmethod
    def readFromNMEAFile(path, frame=NMEA_GGA):
        """The method assumes a single track in file."""

        track = Track()

        if frame.upper() == FileReader.NMEA_GGA:
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
                        time = GPSTime(hour=h, min=m, sec=s, ms=ms)
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
