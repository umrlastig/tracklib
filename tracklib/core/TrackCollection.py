"""This module contain a class to manage the collections of tracks"""

from typing import Literal   
import matplotlib.pyplot as plt

from tracklib import removeNan, listify, compLike


class TrackCollection:
    """TODO"""

    def __init__(self, TRACES=[]):
        """
        TRACES: list of Track
        """
        self.__TRACES = TRACES.copy()
        self.spatial_index = None

    def addTrack(self, track):
        """TODO"""
        self.__TRACES.append(track)

    def size(self):
        """TODO"""
        return len(self.__TRACES)

    def length(self):
        """TODO"""
        length = 0
        for track in self:
            length += track.length()
        return length

    def duration(self):
        """TODO"""
        duration = 0
        for track in self:
            duration += track.duration()
        return duration

    def getTracks(self):
        """TODO"""
        return self.__TRACES

    def getTrack(self, i):
        """TODO"""
        return self.__TRACES[i]

    def copy(self):
        """TODO"""
        TRACKS = TrackCollection()
        for i in range(self.size()):
            TRACKS.addTrack(self.getTrack(i).copy())
        return TRACKS

    def setTimeZone(self, zone):
        """TODO"""
        for i in range(len(self)):
            self[i].setTimeZone(zone)

    def convertToTimeZone(self, zone):
        """TODO"""
        for i in range(len(self)):
            self[i].convertToZone(zone)

    # Average frequency	of tracks
    def frequency(self, mode="temporal"):
        """TODO"""
        m = 0
        for track in self:
            m += track.frequency(mode)
        return m / self.size()

    def __iter__(self):
        """TODO"""
        yield from self.__TRACES

    # =========================================================================
    # Spatial index creation, export and import functions
    # =========================================================================

    def createSpatialIndex(self, resolution=None, verbose=True):
        """TODO"""
        from tracklib.core.SpatialIndex import SpatialIndex

        self.spatial_index = SpatialIndex(self, resolution, verbose)

    def exportSpatialIndex(self, filename):
        """TODO"""
        # from tracklib.core.SpatialIndex import SpatialIndex
        self.spatial_index.save(filename)

    def importSpatialIndex(self, filename):
        """TODO"""
        from tracklib.core.SpatialIndex import SpatialIndex

        self.spatial_index = SpatialIndex.load(filename)

    # =========================================================================
    # Track collection coordinate transformation
    # =========================================================================

    def toECEFCoords(self, base=None):
        """TODO"""
        if self.__TRACES[0].getSRID() == "Geo":
            for track in self.__TRACES:
                track.toECEFCoords()
            return
        if self.__TRACES[0].getSRID() == "ENU":
            if base == None:
                print(
                    "Error: base coordinates should be specified for conversion ENU -> ECEF"
                )
                exit()
            for track in self.__TRACES:
                track.toECEFCoords(base)
            return

    def toENUCoords(self, base=None):
        """TODO"""
        if self.__TRACES[0].getSRID() in ["Geo", "ECEF"]:
            if base == None:
                base = self.__TRACES[0].getFirstObs().position
                message = "Warning: no reference point (base) provided for local projection to ENU coordinates. "
                message += "Arbitrarily used: " + str(base)
                print(message)
            for track in self.__TRACES:
                track.toENUCoords(base)
            return
        if self.__TRACES[0].getSRID() == "ENU":
            if base == None:
                print(
                    "Error: new base coordinates should be specified for conversion ENU -> ENU"
                )
                exit()
            for track in self.__TRACES:
                if track.base == None:
                    print(
                        "Error: former base coordinates should be specified for conversion ENU -> ENU"
                    )
                    exit()
                track.toENUCoords(track.base, base)
            track.base = base.toGeoCoords()
            return base

    def toGeoCoords(self, base=None):
        """TODO"""
        if self.__TRACES[0].getSRID() == "ECEF":
            for track in self.__TRACES:
                track.toGeoCoords()
        if self.__TRACES[0].getSRID() == "ENU":
            if base == None:
                print(
                    "Error: base coordinates should be specified for conversion ENU -> Geo"
                )
                exit()
            for track in self.__TRACES:
                track.toGeoCoords(base)

    # Function to convert track to ENUCoords if it is in GeoCoords. Returns None
    # if no transformation operated, and returns used reference point otherwise
    def toENUCoordsIfNeeded(self):
        """TODO"""
        base = None
        if self.getTrack(0).getSRID() in ["GEO", "Geo"]:
            base = self.getTrack(0).getObs(0).position.copy()
            self.toENUCoords(base)
        return base

    # =========================================================================
    #  Thin plates smoothing
    # =========================================================================
    def smooth(self, constraint=1e3):
        """TODO"""
        for track in self:
            track.smooth(constraint)

    def summary(self):
        """
        Print summary (complete wkt below)
        """
        output = "-------------------------------------\n"
        output += "Number of GPS track: " + str(len(self.__TRACES)) + "\n"
        output += "-------------------------------------\n"
        SIZES = []
        for trace in self.__TRACES:
            SIZES.append(trace.size())
        output += "  Nb of pt(s):   " + str(SIZES) + "\n"
        # output += "  Nb of pt(s):   " + str(len(self.__POINTS)) + "\n"
        print(output)

    def addAnalyticalFeature(self, algorithm, name=None):
        """TODO"""
        for trace in self.__TRACES:
            trace.addAnalyticalFeature(algorithm, name)
            
            
    def getAnalyticalFeature(self, af_name, withNan=True):
        valuesAF = []
        for track in self:
            values = track.getAnalyticalFeature(af_name)
            if not withNan:
                values = removeNan(values)
            valuesAF = valuesAF + values
        return valuesAF
            
    def operate(self, operator, arg1=None, arg2=None, arg3=None):
        """TODO"""
        for trace in self.__TRACES:
            trace.operate(operator, arg1, arg2, arg3)

    def plot(self, symbols=None, markersize=[4], margin=0.05, append=False):
        """TODO"""
        if symbols is None:
            symbols = ["r-", "g-", "b-", "c-", "m-", "y-", "k-"]
        if len(self) == 0:
            return
        symbols = listify(symbols)
        markersize = listify(markersize)
        if not append:
            (xmin, xmax, ymin, ymax) = self.bbox().asTuple()
            dx = margin * (xmax - xmin)
            dy = margin * (ymax - ymin)
            plt.xlim([xmin - dx, xmax + dx])
            plt.ylim([ymin - dy, ymax + dy])
        Ns = len(symbols)
        Ms = len(markersize)
        for i in range(len(self.__TRACES)):
            trace = self.__TRACES[i]
            X = trace.getX()
            Y = trace.getY()
            plt.plot(X, Y, symbols[i % Ns], markersize=markersize[i % Ms])

    def filterOnBBox(self, bbox):
        """TODO"""
        xmin, xmax, ymin, ymax = bbox.asTuple()
        for i in range(len(self) - 1, -1, -1):
            track = self[i]
            for j in range(len(track)):
                inside = True
                inside = inside & (track[j].position.getX() > xmin)
                inside = inside & (track[j].position.getY() > ymin)
                inside = inside & (track[j].position.getX() < xmax)
                inside = inside & (track[j].position.getY() < ymax)
                if not inside:
                    self.removeTrack(track)
                    break

    def bbox(self):
        """TODO"""
        bbox = self.getTrack(0).bbox()
        for i in range(1, len(self)):
            bbox = bbox + self.getTrack(i).bbox()
        return bbox

    def resample(self, delta, algo: Literal[1,2,3,4]=1, mode:Literal[1,2]=1):   
        """Resampling tracks with linear interpolation


        :param delta: interpolation interval (time in sec if temporal mode is selected,
                     space in meters if spatial).

        :param mode: Mode of interpolation.
            Available modes are:

            - MODE_SPATIAL (*mode=1*)
            - MODE_TEMPORAL (*mode=2*)

        :params algorithm: of interpolation.
            Available algorithm are :

            - ALGO_LINEAR (*algo=1*)
            - ALGO_THIN_SPLINES (*algo=2*)
            - ALGO_B_SPLINES (*algo=3*)
            - ALGO_GAUSSIAN_PROCESS (*algo=4*)

        **NB**: In temporal mode, argument may be:

            - an integer or float: interval in seconds
            - a list of timestamps where interpolation should be computed
            - a reference track

        """
        for track in self:
            track.resample(delta, algo, mode)

    def __collectionnify(tracks):
        """TODO"""
        if isinstance(tracks, list):
            return TrackCollection(tracks)
        else:
            return tracks

    # =========================================================================
    # Tracks simplification (returns a new track)
    # Tolerance is in the unit of track observation coordinates
    #   MODE_SIMPLIFY_DOUGLAS_PEUCKER (1)
    #   MODE_SIMPLIFY_VISVALINGAM (2)
    # =========================================================================
    def simplify(self, tolerance, mode=1):
        """TODO"""
        output = self.copy()
        for i in range(len(output)):
            output[i] = output[i].simplify(tolerance, mode)

    # ------------------------------------------------------------
    # [+] Concatenation of two track collections
    # ------------------------------------------------------------
    def __add__(self, collection):
        """TODO"""
        return TrackCollection(self.__TRACES + collection.__TRACES)

    # ------------------------------------------------------------
    # [/] Even split track collection (returns n+1 collections)
    # ------------------------------------------------------------
    def __truediv__(self, number):
        """TODO"""
        N = (int)(self.size() / number)
        # R = self.size()-N*number
        SPLITS = []
        for i in range(number + 1):
            id_ini = i * N
            id_fin = min((i + 1) * N, self.size()) + 1
            SPLITS.append(TrackCollection(self[id_ini:id_fin].copy()))
        return SPLITS

    # ------------------------------------------------------------
    # [>] Removes first n points of track
    # ------------------------------------------------------------
    def __gt__(self, nb_points):
        """TODO"""
        output = self.copy()
        for i in range(self.size()):
            output[i] = output[i] > nb_points
        return output

    # ------------------------------------------------------------
    # [<] Removes last n points of track
    # ------------------------------------------------------------
    def __lt__(self, nb_points):
        """TODO"""
        output = self.copy()
        for i in range(self.size()):
            output[i] = output[i] < nb_points
        return output

    # ------------------------------------------------------------
    # [>=] Available operator
    # ------------------------------------------------------------
    def __ge__(self, arg):
        """TODO"""
        return None

    # ------------------------------------------------------------
    # [<=] Available operator
    # ------------------------------------------------------------
    def __le__(self, arg):
        """TODO"""
        return None

    # ------------------------------------------------------------
    # [!=] Available operator
    # ------------------------------------------------------------
    def __neq__(self, arg):
        """TODO"""
        return None

    # ------------------------------------------------------------
    # [Unary -] Available operator
    # ------------------------------------------------------------
    def __neg__(self, arg):
        """TODO"""
        return None

    # ------------------------------------------------------------
    # [**] Resample (spatial) according to a number of points
    # Linear interpolation and temporal resampling
    # ------------------------------------------------------------
    def __pow__(self, nb_points):
        """TODO"""
        output = self.copy()
        for i in range(self.size()):
            output[i] **= nb_points
        return output

    # ------------------------------------------------------------
    # [abs] Available operator
    # ------------------------------------------------------------
    def __abs__(self):
        """TODO"""
        return None

    # ------------------------------------------------------------
    # [len] Number of tracks in track collection
    # ------------------------------------------------------------
    def __len__(self):
        """TODO"""
        return self.size()

    # ------------------------------------------------------------
    # [-] Computes difference profile of 2 tracks
    # ------------------------------------------------------------
    def __sub__(self, arg):
        """TODO"""
        print("Available operator not implemented yet")

    # ------------------------------------------------------------
    # [*] Temporal resampling of tracks
    # ------------------------------------------------------------
    def __mul__(self, number):
        """TODO"""
        output = self.copy()
        for i in range(self.size()):
            output[i] *= number
        return output

    # ------------------------------------------------------------
    # [%] Remove one point out of n (or according to list pattern)
    # ------------------------------------------------------------
    def __mod__(self, sample):
        """TODO"""
        output = self.copy()
        for i in range(self.size()):
            output[i] %= sample
        return output

    # ------------------------------------------------------------
    # [//] Time resample of a tracks according to another track
    # ------------------------------------------------------------
    def __floordiv__(self, track):
        """TODO"""
        output = self.copy()
        for t in output.__TRACES:
            t.resample(track)  # Mode temporal / linear
        return output

    # ------------------------------------------------------------
    # [[n]] Get and set track number n
    # May be tuple with uid, tid
    # ------------------------------------------------------------
    def __getitem__(self, n):
        """TODO"""
        if isinstance(n, tuple):
            tracks = TrackCollection()
            for track in self:
                if (compLike(track.uid, n[0])) and (
                    compLike(track.tid, n[1])
                ):
                    tracks.addTrack(track)
            return tracks
        return TrackCollection.__collectionnify(self.__TRACES[n])

    def __setitem__(self, n, track):
        self.__TRACES[n] = track

    # =========================================================================
    def removeTrack(self, track):
        """TODO"""
        self.__TRACES.remove(track)

    def removeEmptyTrack(self):
        """
        Remove tracks without observation
        """
        for track in self.__TRACES:
            if track.size() <= 0:
                self.removeTrack(track)

    # =========================================================================
    #    SEGMENTATION, EXTRACT, REMOVE

    def segmentation(self, afs_input, af_output, thresholds_max, mode_comparaison=1):
        """TODO"""
        for t in self.__TRACES:
            t.segmentation(afs_input, af_output, thresholds_max, mode_comparaison)

    def split_segmentation(self, af_output):
        """
        Découpe les traces suivant la segmentation définie par le paramètre af_output ET
        Remplace la trace par les traces splittées s'il y a une segmentation.
        """
        NEW_TRACES = []
        for track in self.__TRACES:
            TRACES_SPLIT = track.split_segmentation(af_output)
            # Si le tableau est nulle pas de segmentation, on ne fait rien
            # sinon on supprime la trace et on ajoute les traces splittées
            if len(TRACES_SPLIT) > 0:
                for split in TRACES_SPLIT:
                    # print (split.size())
                    NEW_TRACES.append(split)
            else:
                NEW_TRACES.append(track)

        self.__TRACES = NEW_TRACES
