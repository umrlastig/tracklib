# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
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
             label=None, size=5, w=6.4, h=4.8, title="", xlabel=None, ylabel=None, 
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
        self, track, template="SPATIAL_SPEED_PROFIL", afs=[], append=False,
                   linestyle = '-', linewidth=1):
        """
        Plot a profil track.
        """
        pass
    
    @abstractmethod
    def plotMMLink(self, track):
        """
        Plot the map matched track on network links.
        """
        pass
        
    
    @abstractmethod
    def plotSpatialIndex(self, si, base=True, append=True):
        """
        Plot a spatial index.
        """
        pass
    
    @abstractmethod
    def highlightCellInSpatialIndex(self, si, i, j, sym="r-", size=0.5):
        """
        Plot a specific cell (i,j)
        """
        pass
    
    
    @abstractmethod
    def plotNetwork(self, network, edges:str="k-", nodes:str="",
        direct:str="k--", indirect:str="k--", size:float=0.5, append=None):
        """
        Plot a network.
        """
        pass
    
