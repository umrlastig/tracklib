# -*- coding: utf-8 -*-

from tracklib.core.GPSTime import GPSTime
from tracklib.io.FileFormat import FileFormat


class FileWriter:
    """Write GPS track to CSV file(s)."""

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
        headerAF = ""
        if len(af_names) > 0:
            for idx, af_name in enumerate(af_names):
                O.append((4 + idx, 4 + idx))
                headerAF += fmt.separator + af_name
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
                    + FileWriter.__printInOrder(
                        "E", "N", "U", "time", headerAF, O, fmt.separator)
                    + "\n"
                )
            if track.getSRID().upper() == "GEO":
                f.write(
                    fmt.com
                    + FileWriter.__printInOrder(
                        "lon", "lat", "h", "time", headerAF, O, fmt.separator)
                    + "\n"
                )
            if track.getSRID().upper() == "ECEF":
                f.write(
                    fmt.com
                    + FileWriter.__printInOrder("X", "Y", "Z", "time", 
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
                    
            f.write(FileWriter.__printInOrder(x, y, z, t,
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
                FileWriter.writeToFile(track, path)  # Read by extension
            else:
                FileWriter.writeToFile(track, path, id_E)  # Read by name
        else:
            FileWriter.writeToFile(
                track, path, id_E, id_N, id_U, id_T, separator, h
            )  # Read from input parameters
