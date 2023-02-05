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
    