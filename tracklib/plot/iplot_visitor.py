# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Marie-Dominique Van Damme
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

from abc import ABC, abstractmethod
from tracklib.util.exceptions import *
#from typing import Iterable, Literal


class IPlotVisitor(ABC):
    """
    Interface to plot Track, TrackCollection, Netork, SpatialIndex, etc
    with different library: Maptplotlib or Qgis.
    
    Uses the decorator design pattern.
    """
    
    @abstractmethod
    def plotTrackAsMarkers(
        self, track, size=8, frg="k", bkg="w", sym_frg="+", sym_bkg="o", type=None, 
        append=True
    ):
        """
        Plot a track as markers.
        """
        pass
    
    @abstractmethod
    def plotTrackEllipses(self, track, sym="r-", factor=3, af=None, append=True):
        """
        """
        pass
    
    @abstractmethod
    def plotTrack(self, track, sym="k-", type="LINE", af_name="", cmap=-1, append=True, 
             size=5, style=None, color=None, w=6.4, h=4.8, title="", xlabel=None, ylabel=None, 
             xlim=None, ylim=None):
        """
        Method to plot a track (short cut from Plot)
        Append:
            - True : append to the current plot
            - False: create a new plot
            - Ax   : append to the fiven ax object
        ----------------------------------------------------
        Output:
            Ax object (may be input into append parameter)
    
        af_name: test si isAFTransition
        """
        pass
    
    @abstractmethod
    def plotAnalyticalFeature(self, track, af_name, template="BOXPLOT", append=False):
        """
        Plot AF values by abcisse curvilign.
        """
        pass
    
    @abstractmethod
    def plotFirstObs(self, track, ptcolor="r", pttext="S", dx=0, dy=0, markersize=4, 
                     append=False):
        """TODO"""
        pass
    
    @abstractmethod
    def plotLastObs(self, track, ptcolor="r", pttext="E", dx=0, dy=0, markersize=4, 
                     append=False):
        """TODO"""
        pass
    
    @abstractmethod
    def plotTrackProfil(
        self, track, template="SPATIAL_SPEED_PROFIL", afs=[], 
                   linestyle = '-', linewidth=1, color='g', append=False):
        """
        Plot a profil track.
        """
        pass
    
    
    
