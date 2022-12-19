"""
This module contains the class to manage observation in a GPS track
Points are referenced in geodetic coordinates
"""

# For type annotation
from __future__ import annotations

import sys
import copy

from tracklib.core.ObsCoords import ECEFCoords, ENUCoords
from tracklib.core.ObsTime import ObsTime


class Obs:
    """Class to define an observation"""

    def __init__(self, position: ENUCoords, timestamp: ObsTime = None):
        """Constructor of :class:`Obs` class

        :param position: A point coordinate
        :param timestamp: The time stamp of acquisition (Default timestamp is 1970/01/01 00:00:00)
        """

        if timestamp is None:
            timestamp = ObsTime()

        self.position = position
        self.timestamp = timestamp

        self.features = []

        self.gdop = 0
        self.pdop = 0
        self.vdop = 0
        self.hdop = 0
        self.tdop = 0

        self.nb_sats = 0
        self.mask = 0
        self.code = 0

        self.azimut = 0
        self.elevation = 0

    def __str__(self) -> str:
        """String of observation"""
        return (str)(self.timestamp) + "  " + (str)(self.position)

    def copy(self) -> Obs:
        """Copy the current object"""
        return copy.deepcopy(self)

    # --------------------------------------------------
    # Geom. methods (should not depend on coords type)
    # --------------------------------------------------
    def __check_call_geom1(fname, obs1: Obs, obs2: Obs):
        """TODO

        :param fname: TODO
        :param obs1: TODO
        :param obs2: TODO
        """
        if isinstance(obs1.position, ECEFCoords) or (
            isinstance(obs2.position, ECEFCoords)
        ):
            sys.exit("Error: cannot call " + fname + " with ECEF coordinates")

    def __check_call_geom2(fname, obs1: Obs, obs2: Obs):
        """TODO

        :param fname: TODO
        :param obs1: TODO
        :param obs2: TODO
        """
        c1 = type(obs1.position)
        c2 = type(obs2.position)
        nc1 = (str)(c1)[7:-1]
        nc2 = (str)(c2)[7:-1]
        if c1 != c2:
            sys.exit(
                "Error: cannot call "
                + fname
                + " method with "
                + nc1
                + " and "
                + nc2
                + " objects"
            )

    def distanceTo(self, obs: Obs) -> float:
        """Compute the distance between two observations

        :param obs: Observation
        :return: A 3d distance
        """
        Obs.__check_call_geom2("distanceTo", self, obs)
        return self.position.distanceTo(obs.position)

    def distance2DTo(self, obs: Obs) -> float:
        """Compute the 2d distance between two observations

        :param obs: Observation
        :return: A 2d distance
        """
        Obs.__check_call_geom1("distance2DTo", self, obs)
        return self.position.distance2DTo(obs.position)

    def azimuthTo(self, obs: Obs) -> float:
        """Compute the azimuth between two observations

        :param obs: Observation
        :return: An azimuth
        """
        Obs.__check_call_geom2("azimuthTo", self, obs)
        return self.position.azimuthTo(obs.position)

    def elevationTo(self, obs: Obs) -> float:
        """Compute the elevation between two observations

        :param obs: Observation
        :return: An Elevation
        """
        Obs.__check_call_geom2("elevationTo", self, obs)
        return self.position.elevationTo(obs.position)

    def __getitem__(self, af_index: int):
        """Get the n-est feature

        :param af_index: Index of feature
        :return: The feature
        """
        return self.features[af_index]

    def __setitem__(self, af_index: int, value):
        """Set the n-est feature

        :param af_index: Index of feature
        :param value: The value to set
        """
        self.features[af_index] = value
