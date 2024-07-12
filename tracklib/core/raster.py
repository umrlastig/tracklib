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



This module contains the class to manipulate rasters.
A raster is defined as a collection of RasterBand.

"""

# For type annotation
from __future__ import annotations   
from typing import Union
#from tracklib.util.exceptions import *

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

import numpy as np

from tracklib.core import listify
from tracklib.core import ECEFCoords, ENUCoords, GeoCoords, getOffsetColorMap
from tracklib.core import Bbox
from tracklib.util import CoordTypeError, SizeError

NO_DATA_VALUE = -9999
DEFAULT_BAND_NAME = 'grid'

# -----------------------------------------------------------------------------
# Specific parameters for interpolation methods for upsampling
# -----------------------------------------------------------------------------
# List of available interpolate methods for upsampling grid
MODE_NEAREST_NEIGHBOR       = 101   #
MODE_BED_OF_NAILS_TECHNIQUE = 102
MODE_MAX_UNPOOLING          = 103



class RasterBand:
    
    def __init__(self, bb: Bbox, resolution=None, margin:float=0.05,
                 novalue:float=NO_DATA_VALUE,
                 name=DEFAULT_BAND_NAME, verbose:bool=False):
        """
        Grid constructor.
        
        :param bbox: Bouding box
        :param resolution: Grid resolution
        :param margin: relative float. Default value is +5%
        :param novalue: value that is regarded as "missing" or "not applicable";
        :param verbose: Verbose creation
        """
        
        bb = bb.copy()
        bb.addMargin(margin)
        self.__bbox = bb
        (self.xmin, self.xmax, self.ymin, self.ymax) = bb.asTuple()
        
        ax, ay = bb.getDimensions()
        if resolution is None:
            am = max(ax, ay)
            r = am / 100
            resolution = (int(ax / r), int(ay / r))
        else:
            r = resolution
            resolution = (int(ax / r[0]), int(ay / r[1]))
        if verbose:
            print (resolution)
    
        # Nombre de dalles par cote
        self.ncol = resolution[0]
        self.nrow = resolution[1]
        if verbose:
            print (self.nrow, self.ncol)
    
        # Tableau de collections de features appartenant a chaque dalle.
        # Un feature peut appartenir a plusieurs dalles.
        self.grid = []
        for i in range(self.nrow):
            self.grid.append([])
            for j in range(self.ncol):
                self.grid[i].append(NO_DATA_VALUE)
    
        self.XPixelSize = ax / self.ncol
        self.YPixelSize = ay / self.nrow
        if verbose:
            print (self.XPixelSize, self.YPixelSize)
        
        self.__noDataValue = novalue
        self.__name = name
        
    def bbox(self):
        return self.__bbox
        
# TODO : impact dans le dictionnaire du raster à gérer
#    def setName(self, name):
#        self.__name = name

    def getName(self):
        return self.__name
    
    def setNoDataValue(self, noDataValue):
        # On récupere l'ancienne valeur
        oldvalue = self.__noDataValue
        self.__noDataValue = noDataValue
        
        for i in range(self.nrow):
            for j in range(self.ncol):
                if self.grid[i][j] == oldvalue:
                    self.grid[i][j] = self.__noDataValue
        
        
    def getNoDataValue(self):
        return self.__noDataValue
        
    
    def isIn(self, coord: Union[ENUCoords]):
        '''
        Return true if coord is in spatial grid, false else.
    
        Parameters
        ----------
        coord : Union[ENUCoords]
            coordinate of the position to test the contain.
    
        Returns
        -------
        bool
            true if contains, false else.
    
        '''
        if coord.E < self.xmin or coord.E > self.xmax:
            return False
        if coord.N < self.ymin or coord.N > self.ymax:
            return False
        
        return True
    
    
    def __str__(self):
        output  = "-------------------------------------\n"
        output += "Grid '" + self.__name + "':\n"
        output += "-------------------------------------\n"
        output += "       nrows = " + str(self.nrow) + "\n"
        output += "       ncols = " + str(self.ncol) + "\n"
        output += "       XPixelSize = " + str(self.XPixelSize) + "\n"
        output += "       YPixelSize = " + str(self.YPixelSize) + "\n"
        output += "   Bounding box: \n"
        output += "       Lower left corner : " + str(self.xmin) + "," + str(self.ymin) + "\n"
        output += "       Upper right corner: " + str(self.xmax) + "," + str(self.ymax) + "\n"
        output += "-------------------------------------\n"
        
        return output
    
    def summary(self):
        print (self.__str__())

    def asNumpy(self) -> np.ndarray:
        '''
        Returns the grid converted in numpy array
        '''
        return np.array(self.grid, dtype=np.float32)

    def bandStatistics(self):
        stats = np.array(self.grid)
        if self.getNoDataValue() != None:
            stats[stats == self.getNoDataValue()] = None
        
        print("-------------------------------------")
        print("Grid '" + self.__name + "':")
        print("-------------------------------------")
        print("    Minimum value: ", np.nanmin(stats))
        print("    Maximum value: ", np.nanmax(stats))
        print("    Mean value:    ", np.nanmean(stats))
        print("    Median value:  ", np.nanmedian(stats))
        print("-------------------------------------\n")
        
        if self.getNoDataValue() != None:
            stats[stats == None] = self.getNoDataValue()

    
    def getCell(self, coord: Union[ENUCoords, ECEFCoords, GeoCoords]) -> Union[tuple[float, float], None]:   
        """Normalized coordinates of coord
    
        (x,) -> (i,j) with:   
    
            - i = (x-xmin)/(xmax-xmin)*nb_cols
            - j = (y-ymin)/(ymax-ymin)*nb_rows
    
        :param coord: Coordinates
        :return: Cell for give coordinates (or None if out of grid)
        """
    
        if (coord.getX() < self.xmin) or (coord.getX() > self.xmax):
            overflow = "{:5.5f}".format(
                max(self.xmin - coord.getX(), coord.getX() - self.xmax)
            )
            print("Warning: x overflow " + str(coord) + "  OVERFLOW = " + str(overflow))
            return None
        
        if (coord.getY() < self.ymin) or (coord.getY() > self.ymax):
            overflow = "{:5.5f}".format(
                max(self.ymin - coord.getY(), coord.getY() - self.ymax)
            )
            print("Warning: y overflow " + str(coord) + "  OVERFLOW = " + str(overflow))
            return None
    
        idx = (float(coord.getX()) - self.xmin) / self.XPixelSize
        idy = (self.nrow-1) - (float(coord.getY()) - self.ymin) / self.YPixelSize
    
        return (idx, idy)
    
    
    def plotAsGraphic(self, backgroundcolor="lightcyan", bordercolor="lightgray"):   
        """ Plot as vector grid. """
        fig = plt.figure()
        ax = fig.add_subplot(
            111, xlim=(self.xmin, self.xmax), ylim=(self.ymin, self.ymax)
        )
    
        for i in range(1, self.ncol):
            xi = i * self.XPixelSize + self.xmin
            ax.plot([xi, xi], [self.ymin, self.ymax], "-", color=bordercolor)
        for j in range(1, self.nrow):
            yj = j * self.YPixelSize + self.ymin
            ax.plot([self.xmin, self.xmax], [yj, yj], "-", color=bordercolor)
    
        for i in range(self.nrow):
            y1 = self.ymin + (self.nrow - 1 - i) * self.YPixelSize
            y2 = self.ymin + (self.nrow - i) * self.YPixelSize
            for j in range(self.ncol):
                x1 = self.xmin + j * self.XPixelSize
                x2 = x1 + self.XPixelSize
                if self.grid[i][j] != NO_DATA_VALUE:
                    #print (self.xmin, x1, y1, x2, y2)
                    polygon = plt.Polygon(
                        [[x1, y1], [x2, y1], [x2, y2], [x1, y2], [x1, y1]]
                    )
                    ax.add_patch(polygon)
                    polygon.set_facecolor(backgroundcolor)
                    
                    text_kwargs = dict(ha='center', va='center', fontsize=12, color='C1')
                    val = str(round(self.grid[i][j], 2))
                    xm = (x2 - x1) / 2
                    ym = (y2 - y1) / 2
                    plt.text(x1 + xm, y1 + ym, val, **text_kwargs)
        plt.title(self.getName())


    def plotAsImage(self, append=False, 
                    color1 = (0, 0, 0), color2 = (255, 255, 255),
                    novaluecolor='white'):
        """ Plot raster band as an image. """
      
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
                fig = ax1.get_figure()
            else:
                fig, ax1 = plt.subplots(figsize=(10, 3))
        else:
            ax1 = append
            fig = ax1.get_figure()
        
        tab = np.array(self.grid, dtype=np.float32)
        if self.getNoDataValue() != None:
            tab[tab == self.getNoDataValue()] = np.nan

        cmap = getOffsetColorMap(color1, color2, 0)
        cmap.set_bad(color=novaluecolor)

        im = ax1.imshow(tab, cmap=cmap)
        ax1.set_title(self.getName())
        
        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right', size='5%', pad=0.1)
        if fig != None:
            fig.colorbar(im, cax=cax, orientation='vertical', fraction=0.046)


    def upSampling(self, resolution, interpolation=MODE_NEAREST_NEIGHBOR,
                       name='Upsampling') -> RasterBand:
        '''
        Interpolation Methods for Upsampling:
            - Nearest Neighbor: this method involves duplicating the existing 
                                pixels to create new ones.
            - Max Unpooling:
        '''

        if not isinstance(self.__bbox.ur, ENUCoords):
            raise CoordTypeError('Only ENU coordinates system implemented')

        if self.XPixelSize != self.YPixelSize:
            raise SizeError('cells must be square.')

        new_grid = RasterBand(self.__bbox,
                            resolution=(resolution[0], resolution[1]),
                            margin=0,
                            novalue=self.__noDataValue,
                            name='Upsampling', verbose=False)

        # Il faut aussi une résoltion proportionnelle entre les deux rasters
        N = int (self.XPixelSize / new_grid.XPixelSize)
        if int(N - (self.XPixelSize / new_grid.XPixelSize)) != 0.0:
            raise SizeError('Two grids resolution not proportional')
        print ('N =', N)

        if interpolation == MODE_NEAREST_NEIGHBOR:
            for i in range(self.nrow):
                for j in range(self.ncol):
                    v = self.grid[i][j]
                    for k in range(0, N):
                        for l in range(0, N):
                            new_grid.grid[i*N + k][j*N + l] = v
            return new_grid

        # MODE_MAX_UNPOOLING
        # MODE_BED_OF_NAILS_TECHNIQUE

        return None


class Raster:
    
    def __init__(self, grids:Union[RasterBand, list]):
        """
        On crée un raster avec une ou plusieurs grilles géographiques 
        déjà chargées avec des données.
        
        Parameters
        ----------
        grids : list or RasterBand
           A list of RasterBand or one RasterBand.
           
        """
        if isinstance(grids, RasterBand):
            grids = listify(grids)
        
        self.__idxBands = []
        self.__bands = {}
        for idx, itergrid in enumerate(grids):
            self.__bands[itergrid.getName()] = itergrid
            self.__idxBands.append(itergrid.getName())

    def bandCount(self):
        """Return the number of bands in this raster"""
        return len(self.__bands)

    def getNamesOfRasterBand(self):
        """Return all names of raster bands in a list."""
        return list(self.__bands.keys())
    
    def getRasterBand(self, identifier: Union[int, str]) -> RasterBand:
        """Return the raster band according to index or name"""
        if isinstance(identifier, int):
            name = self.__idxBands[identifier]
            return self.__bands[name]
        return self.__bands[identifier]

#    def summary(self):
#        pass
    
#    def bandStatistics(self, name: Union[int, str]):
#        pass
    
    def plot(self, identifier:Union[int, str], append=False):
        """For now, juste one band of raster, that's why the name is needeed."""
        if isinstance(identifier, int):
            name = self.__idxBands[identifier]
            self.__bands[name].plotAsImage(append)
        else:
            self.__bands[identifier].plotAsImage(append)
            


            
