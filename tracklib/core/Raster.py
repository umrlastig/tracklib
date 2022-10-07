"""
This module contains the class to manipulate rasters
"""

# For type annotation
from __future__ import annotations   
from typing import Union

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np

#from skimage import io

import tracklib.core.Utils as utils
import tracklib.core.RasterBand as grid

NO_DATA_VALUE = -9999

class Raster:
    '''
    Class for defining a spatial grid: structure de données un peu plus évoluée
          qu'un tableau 2x2. 
          
    Mainly used by :function:`algo.Mapping.mapOnRaster` and `algo.Summarizing.summarize`.
          
    Parameters
    ----------
    nrow : int
       Numbers of rows.
    ncol : int
       Numbers of cols.
    '''
    
    def __init__(self, grids: Union[grid.RasterBand, list], verbose=True):
        """
        On crée un raster avec une ou plusieurs grilles géographiques 
        déjà chargées avec les données.
        """
        
        grids = utils.listify(grids)
        
        self.bands = {}
        for itergrid in grids:
            self.bands[itergrid.name] = itergrid

        self.color1 = (0, 0, 0)
        self.color2 = (255, 255, 255)

    def getNamesOfRasterBand(self):
        for name in self.bands:
            print (name)

    def setColor(self, c1, c2):
        """TODO"""
        self.color1 = c1
        self.color2 = c2
        
        
    def getCle(self, af_algo: Union[int, str], aggregate = None):
        """TODO"""
        
        if af_algo != "uid":
            if isinstance(af_algo, str):
                cle = af_algo + "#" + aggregate.__name__
            else:
                cle = af_algo.__name__ + "#" + aggregate.__name__
        else:
            cle = "uid" + "#" + aggregate.__name__
            
        return cle
    
    def getRasterBand(self, af_algo: Union[int, str], aggregate = None):
        """TODO"""
        
        if isinstance(af_algo, int):
            return self.bands[grid.DEFAULT_NAME + str(af_algo)]
        
        cle = self.getCle(af_algo, aggregate)
        return self.bands[cle]

    
    def plot(self, af_algo, aggregate, no_data_values = None, 
             axe = None, figure = None):
        """TODO"""
        
        tab = np.array(self.getRasterBand(af_algo, aggregate).grid)
        
        if no_data_values != None:
            tab[tab == grid.NO_DATA_VALUE] = no_data_values

        cmap = utils.getOffsetColorMap(self.color1, self.color2, 0)
        
        if axe == None:
            im = plt.imshow(tab, cmap=cmap)
            plt.title(self.getCle(af_algo, aggregate))
            plt.colorbar(im,fraction=0.046, pad=0.04)
            plt.show()
        else:
            im = axe.imshow(tab, cmap=cmap)
            axe.set_title(self.getCle(af_algo, aggregate))
            
            divider = make_axes_locatable(axe)
            cax = divider.append_axes('right', size='5%', pad=0.1)
            if figure != None:
                figure.colorbar(im, cax=cax, orientation='vertical', fraction=0.046)
            # axe.grid(True)
            

    def saveGrid(self, path, af_algo, aggregate, no_data_values = None, dpi = 300):

        tab = np.array(self.getRasterBand(af_algo, aggregate).grid)
        
        if no_data_values != None:
            tab[tab == grid.NO_DATA_VALUE] = no_data_values

        cmap = utils.getOffsetColorMap(self.color1, self.color2, 0)
        
        fig = plt.figure()
        im = plt.imshow(tab, cmap=cmap)
        plt.title(self.getCle(af_algo, aggregate))
        plt.colorbar(im,fraction=0.046, pad=0.04)
        plt.savefig(path, dpi=dpi)
        plt.close(fig)
        
        
            
