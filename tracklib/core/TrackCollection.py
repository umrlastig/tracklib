"""This module contain a class to manage the collections of tracks"""

import matplotlib.pyplot as plt

import tracklib.core.Utils as Utils


class TrackCollection:
    def __init__(self, TRACES=[]):
        """
        TRACES: list of Track
        """
        self.__TRACES = TRACES.copy()
        self.spatial_index = None

    def addTrack(self, track):
        self.__TRACES.append(track)

    def size(self):
        return len(self.__TRACES)

    def length(self):
        length = 0
        for track in self:
            length += track.length()
        return length

    def duration(self):
        duration = 0
        for track in self:
            duration += track.duration()
        return duration

    def getTracks(self):
        return self.__TRACES

    def getTrack(self, i):
        return self.__TRACES[i]

    def copy(self):
        TRACKS = TrackCollection()
        for i in range(self.size()):
            TRACKS.addTrack(self.getTrack(i).copy())
        return TRACKS

    def setTimeZone(self, zone):
        for i in range(len(self)):
            self[i].setTimeZone(zone)

    def convertToTimeZone(self, zone):
        for i in range(len(self)):
            self[i].convertToZone(zone)

    # Average frequency	of tracks
    def frequency(self, mode="temporal"):
        m = 0
        for track in self:
            m += track.frequency(mode)
        return m / self.size()

    def __iter__(self):
        yield from self.__TRACES

    # =========================================================================
    # Spatial index creation, export and import functions
    # =========================================================================

    def createSpatialIndex(self, resolution=(100, 100), verbose=True):
        from tracklib.core.SpatialIndex import SpatialIndex

        self.spatial_index = SpatialIndex(self, resolution, verbose)

    def exportSpatialIndex(self, filename):
        # from tracklib.core.SpatialIndex import SpatialIndex
        self.spatial_index.save(filename)

    def importSpatialIndex(self, filename):
        from tracklib.core.SpatialIndex import SpatialIndex

        self.spatial_index = SpatialIndex.load(filename)

    # =========================================================================
    # Track collection coordinate transformation
    # =========================================================================

    def toECEFCoords(self, base=None):
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
        base = None
        if self.getTrack(0).getSRID() in ["GEO", "Geo"]:
            base = self.getTrack(0).getObs(0).position.copy()
            self.toENUCoords(base)
        return base

    # =========================================================================
    #  Thin plates smoothing
    # =========================================================================
    def smooth(self, constraint=1e3):
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
        for trace in self.__TRACES:
            trace.addAnalyticalFeature(algorithm, name)

    def plot(self, symbols=None, markersize=[4], margin=0.05, append=False):
        if symbols is None:
            symbols = ["r-", "g-", "b-", "c-", "m-", "y-", "k-"]
        if len(self) == 0:
            return
        symbols = Utils.listify(symbols)
        markersize = Utils.listify(markersize)
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
        bbox = self.getTrack(0).bbox()
        for i in range(1, len(self)):
            bbox = bbox + self.getTrack(i).bbox()
        return bbox

    def resample(self, delta, algo=1, mode=2):
        """Resampling tracks with linear interpolation


        :parm delta: interpolation interval (time in sec if temporal mode is selected,
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
        output = self.copy()
        for i in range(len(output)):
            output[i] = output[i].simplify(tolerance, mode)

    # ------------------------------------------------------------
    # [+] Concatenation of two track collections
    # ------------------------------------------------------------
    def __add__(self, collection):
        return TrackCollection(self.__TRACES + collection.__TRACES)

    # ------------------------------------------------------------
    # [/] Even split track collection (returns n+1 collections)
    # ------------------------------------------------------------
    def __truediv__(self, number):
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
        output = self.copy()
        for i in range(self.size()):
            output[i] = output[i] > nb_points
        return output

    # ------------------------------------------------------------
    # [<] Removes last n points of track
    # ------------------------------------------------------------
    def __lt__(self, nb_points):
        output = self.copy()
        for i in range(self.size()):
            output[i] = output[i] < nb_points
        return output

    # ------------------------------------------------------------
    # [>=] Available operator
    # ------------------------------------------------------------
    def __ge__(self, arg):
        return None

    # ------------------------------------------------------------
    # [<=] Available operator
    # ------------------------------------------------------------
    def __le__(self, arg):
        return None

    # ------------------------------------------------------------
    # [!=] Available operator
    # ------------------------------------------------------------
    def __neq__(self, arg):
        return None

    # ------------------------------------------------------------
    # [Unary -] Available operator
    # ------------------------------------------------------------
    def __neg__(self, arg):
        return None

    # ------------------------------------------------------------
    # [**] Resample (spatial) according to a number of points
    # Linear interpolation and temporal resampling
    # ------------------------------------------------------------
    def __pow__(self, nb_points):
        output = self.copy()
        for i in range(self.size()):
            output[i] **= nb_points
        return output

    # ------------------------------------------------------------
    # [abs] Available operator
    # ------------------------------------------------------------
    def __abs__(self):
        return None

    # ------------------------------------------------------------
    # [len] Number of tracks in track collection
    # ------------------------------------------------------------
    def __len__(self):
        return self.size()

    # ------------------------------------------------------------
    # [-] Computes difference profile of 2 tracks
    # ------------------------------------------------------------
    def __sub__(self, arg):
        print("Available operator not implemented yet")

    # ------------------------------------------------------------
    # [*] Temporal resampling of tracks
    # ------------------------------------------------------------
    def __mul__(self, number):
        output = self.copy()
        for i in range(self.size()):
            output[i] *= number
        return output

    # ------------------------------------------------------------
    # [%] Remove one point out of n (or according to list pattern)
    # ------------------------------------------------------------
    def __mod__(self, sample):
        output = self.copy()
        for i in range(self.size()):
            output[i] %= sample
        return output

    # ------------------------------------------------------------
    # [//] Time resample of a tracks according to another track
    # ------------------------------------------------------------
    def __floordiv__(self, track):
        output = self.copy()
        for t in output.__TRACES:
            t.resample(track)  # Mode temporal / linear
        return output

    # ------------------------------------------------------------
    # [[n]] Get and set track number n
    # May be tuple with uid, tid
    # ------------------------------------------------------------
    def __getitem__(self, n):
        if isinstance(n, tuple):
            tracks = TrackCollection()
            for track in self:
                if (Utils.compLike(track.uid, n[0])) and (
                    Utils.compLike(track.tid, n[1])
                ):
                    tracks.addTrack(track)
            return tracks
        return TrackCollection.__collectionnify(self.__TRACES[n])

    def __setitem__(self, n, track):
        self.__TRACES[n] = track

    # =========================================================================
    def removeTrack(self, track):
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
