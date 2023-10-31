# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Yann Méneroux
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



This module contains the class to manage observation in a GPS track
Points are referenced in geodetic coordinates

"""

# For type annotation
from __future__ import annotations

import sys
import copy

from . import ECEFCoords, ENUCoords, ObsTime


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
