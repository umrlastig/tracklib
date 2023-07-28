"""
This module contains the class to manipulate rasters.
Class for defining a collection of RasterBand.
"""

# For type annotation
from __future__ import annotations   
from typing import Union

from tracklib import listify
import tracklib.core.RasterBand as grid


class Raster:
    
    def __init__(self, grids: Union[grid.RasterBand, list], verbose=True):
        """
        On crée un raster avec une ou plusieurs grilles géographiques 
        déjà chargées avec les données.
        
        Parameters
        ----------
        grids : list 
           A list of RasterBand or one RasterBand.
           
        """
        
        grids = listify(grids)
        
        self.__idxBands = []
        self.__bands = {}
        for idx, itergrid in enumerate(grids):
            self.__bands[itergrid.getName()] = itergrid
            self.__idxBands.append(itergrid.getName())


    def bandCount(self):
        """
        TODO
        """
        return len(self.__bands)

    def getNamesOfRasterBand(self):
        """
        Return all the names of raster bands in a list.
        """
        return list(self.__bands.keys())
    
    
    def getRasterBand(self, identifier: Union[int, str]) -> grid.RasterBand:
        """
        Return the raster band by the index
        """
        if isinstance(identifier, int):
            name = self.__idxBands[identifier]
            return self.__bands[name]
        
        return self.__bands[identifier]

    
#    def summary(self):
#        pass
    
    #def bandStatistics(self, name: Union[int, str]):
        #    pass

    
    def plot(self, identifier: Union[int, str], append=False, 
             color1=(0, 0, 0), color2=(255, 255, 255)):
        """
        At the moment, juste one band of raster, that's why the name is needeed.
        """
        
        if isinstance(identifier, int):
            name = self.__idxBands[identifier]
            self.__bands[name].plotAsImage(append)
        else:
            self.__bands[identifier].plotAsImage(append)
            


            
