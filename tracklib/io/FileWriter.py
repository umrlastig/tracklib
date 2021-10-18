"""Write GPS track to CSV file(s)."""

import os

from tracklib.core.GPSTime import GPSTime
from tracklib.core.Coords import ENUCoords
from tracklib.core.Coords import GeoCoords
from tracklib.core.Coords import ECEFCoords
from tracklib.core.Obs import Obs
from tracklib.core.Track import Track
from tracklib.core.Coords import ECEFCoords
from tracklib.core.TrackCollection import TrackCollection

from tracklib.io.FileFormat import FileFormat


class FileWriter:
    def __takeFirst(elem):
        return elem[0]

    def __printInOrder(E, N, U, T, O, sep):
        D = [E, N, U, T]
        output = ""
        output += str(D[O[0][1]]) + sep
        output += str(D[O[1][1]]) + sep
        output += str(D[O[2][1]]) + sep
        output += str(D[O[3][1]])
        return output

    @staticmethod
    def writeToFile(
        track, path, id_E=-1, id_N=-1, id_U=-1, id_T=-1, separator=",", h=0
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
                fmt = FileFormat(path, -1)  # Read by extension
            else:
                fmt = FileFormat(id_E, 0)  # Read by name
        else:
            fmt = FileFormat("", -1)  # Read from input parameters
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
        O.sort(key=FileWriter.__takeFirst)

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
                    + FileWriter.__printInOrder("E", "N", "U", "time", O, fmt.separator)
                    + "\n"
                )
            if track.getSRID().upper() == "GEO":
                f.write(
                    fmt.com
                    + FileWriter.__printInOrder(
                        "lon", "lat", "h", "time", O, fmt.separator
                    )
                    + "\n"
                )
            if track.getSRID().upper() == "ECEF":
                f.write(
                    fmt.com
                    + FileWriter.__printInOrder("X", "Y", "Z", "time", O, fmt.separator)
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
            f.write(FileWriter.__printInOrder(x, y, z, t, O, fmt.separator) + "\n")

        f.close()

    @staticmethod
    def writeToFiles(
        trackCollection,
        pathDir,
        ext,
        id_E=-1,
        id_N=-1,
        id_U=-1,
        id_T=-1,
        separator=",",
        h=0,
    ):

        root = "track_output"

        for i in range(trackCollection.size()):
            track = trackCollection.getTrack(i)
            path = pathDir + "/" + root + "{:04d}" + "." + ext
        if id_N == -1:
            if id_E == -1:
                FileWriter.writeToFile(track, path)  # Read by extension
            else:
                FileWriter.writeToFile(track, path, id_E)  # Read by name
        else:
            FileWriter.writeToFile(
                track, path, id_E, id_N, id_U, id_T, separator, h
            )  # Read from input parameters
