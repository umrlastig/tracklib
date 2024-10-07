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
A raster is defined as a collection of AFMap.

"""

# For type annotation
from __future__ import annotations   
from typing import Union

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import math
import numpy as np

from tracklib.core import listify
from tracklib.core import ECEFCoords, ENUCoords, GeoCoords, getOffsetColorMap
from tracklib.core import Bbox
from tracklib.core import (isnan,
                           co_count, co_sum, co_min, co_max, co_avg,
                           co_dominant, co_median, co_count_distinct)
from tracklib.util import AnalyticalFeatureError, CoordTypeError, SizeError, WrongArgumentError


NO_DATA_VALUE = -99999.0


class Raster:
    
    def __init__(self, bbox: Bbox,
                 resolution:tuple[float, float]=(100, 100),
                 margin:float=0.05,
                 novalue:float=NO_DATA_VALUE):
        """
        
        Parameters
        ----------
        :param bbox: Bouding box
        :param resolution: Grid resolution
        :param margin: relative float. Default value is +5%
        :param novalue: value that is regarded as "missing" or "not applicable";
           
        """

        bb = bbox.copy()
        bb.addMargin(margin)
        self.__bbox = bb
        (self.xmin, self.xmax, self.ymin, self.ymax) = bb.asTuple()
        
        self.resolution = resolution
        ax, ay = bb.getDimensions()

        # Nombre de dalles par cote
        self.ncol = math.ceil(ax / resolution[0])
        self.nrow = math.ceil(ay / resolution[1])

        #self.xsize = ax / resolution[0]
        #self.ysize = ay / resolution[1]
        #print (self.xsize, self.ysize)

        self.__noDataValue = novalue

        self.__afmaps = {}

    def bbox(self):
        return self.__bbox

    def countAFMap(self):
        """Return the number of bands in this raster"""
        return len(self.__afmaps)

    def getNamesOfAFMap(self):
        """Return all names of raster bands in a list."""
        return list(self.__afmaps.keys())
    
    def getAFMap(self, identifier: Union[int, str]) -> AFMap:
        """Return the raster band according to index or name"""
        if isinstance(identifier, int):
            name = list(self.__afmaps.keys())[identifier]
            return self.__afmaps[name]
        return self.__afmaps[identifier]

    def getNoDataValue(self):
        return self.__noDataValue
    def setNoDataValue(self, novalue):
        self.__noDataValue = novalue

    def __str__(self):
        output  = "-------------------------------------\n"
        output += "Raster:\n"
        output += "-------------------------------------\n"
        output += "       nrows = " + str(self.nrow) + "\n"
        output += "       ncols = " + str(self.ncol) + "\n"
        output += "       XPixelSize = " + str(self.resolution[0]) + "\n"
        output += "       YPixelSize = " + str(self.resolution[1]) + "\n"
        output += "   Bounding box: \n"
        output += "       Lower left corner : " + str(self.xmin) + ", " + str(self.ymin) + "\n"
        output += "       Upper right corner: " + str(self.xmax) + ", " + str(self.ymax) + "\n"
        output += "-------------------------------------\n"
        
        return output
    
    def summary(self):
        print (self.__str__())

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

    def getCell(self, coord: Union[ENUCoords, ECEFCoords, GeoCoords])-> Union[tuple[int, int], None]:
        """Normalized coordinates of coord
    
        (x,y) -> (i,j) with:   
    
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
    
        idx = (float(coord.getX()) - self.xmin) / self.resolution[0]
        idy = (self.nrow-1) - (float(coord.getY()) - self.ymin) / self.resolution[1]

        #idx = (float(coord.getX()) - self.xmin) / self.xsize
        #idy = (float(coord.getY()) - self.ymin) / self.ysize

        # Cas des bordures
        if idx == self.ncol:
            column = math.floor(idx) - 1
        else:
            column = math.floor(idx)

        if idy.is_integer() and int(idy) > -1:
            line = int(idy)
        elif idy.is_integer() and int(idy) == -1:
            line = int(idy) + 1
        else:
            line = math.floor(idy) + 1 # il faut arrondir par le dessus!

        #line = math.floor(idy)
        #column = math.floor(idx)
        return (column, line)


    def plot(self, identifier:Union[int, str], append=False):
        """For now, juste one band of raster, that's why the name is needeed."""
        if isinstance(identifier, int):
            name = list(self.__afmaps.keys())[identifier]
            self.__afmaps[name].plotAsImage(append)
        else:
            self.__afmaps[identifier].plotAsImage(append)
            

    def addAFMap(self, name, grid=None):
        if grid is None:
            grid = []
            for i in range(self.nrow):
                grid.append([])
                for j in range(self.ncol):
                    grid[i].append([])

        afmap = AFMap(self, name, grid)
        self.__afmaps[name] = afmap


    def addCollectionToRaster(self, collection):
        '''
        L'enjeu ici est de stocker qu'une fois chaque AF. Il faut donc que les maps
        soient déjà créées.

        Parameters
        ----------
        collection : TrackCollection
            tracks collection.

        Returns
        -------
        None.

        '''

        AFs = set()
        for mapname in self.getNamesOfAFMap():
            if '#' in mapname:
                AFs.add(mapname.split('#')[0])
            else:
                AFs.add(mapname)

        # On initialise le dictionnaire qui va contenir toutes les valeurs
        self.collectionValuesGrid = {}
        for afname in AFs:
            self.collectionValuesGrid[afname] = []
            for i in range(self.nrow):
                self.collectionValuesGrid[afname].append([])
                for j in range(self.ncol):
                    self.collectionValuesGrid[afname][i].append([])
                    self.collectionValuesGrid[afname][i][j] = []

        # On vérifie que les AF sont calculés
        for trace in collection.getTracks():
            for afname in AFs:
                if not trace.hasAnalyticalFeature(afname) and afname != 'uid':
                    raise AnalyticalFeatureError("Error: track does not contain analytical feature '" + afname + "'")

        for trace in collection.getTracks():
            for afname in AFs:
                # On éparpille dans les cellules
                for i in range(trace.size()):
                    obs = trace.getObs(i)
                    (column, line) = self.getCell(obs.position)
                    #print (column, line, obs.position)

#                    if (0 <= column and column <= self.ncol
#                        and 0 <= line and line <= self.nrow):

                    if afname != "uid":
                        val = trace.getObsAnalyticalFeature(afname, i)
                    else:
                        val = trace.uid

                    self.collectionValuesGrid[afname][line][column].append(val)



    def computeAggregates(self):
        for i in range(self.countAFMap()):
            afmap = self.getAFMap(i)
            names = afmap.getName().split('#')
            afname = names[0]
            aggregate = names[1]

            # On calcule les agregats
            for i in range(self.nrow):
                for j in range(self.ncol):
                    tarray = self.collectionValuesGrid[afname][i][j]
                    sumval = eval(aggregate + '(tarray)')
                    if isnan(sumval):
                        afmap.grid[i][j] = NO_DATA_VALUE
                    else:
                        afmap.grid[i][j] = sumval




class AFMap:
    '''
    Represents a matrix of values: name (AF name) + array 2x2
    '''

    def __init__(self, raster, af_name, grid):

        if not isinstance(raster, Raster):
            raise WrongArgumentError("First parameter need to be a Raster.")

        # Nom n'est pas déjà pris
        if af_name is None or af_name.strip() == '':
            raise WrongArgumentError("Parameter (af_name) is empty.")
        if af_name in raster.getNamesOfAFMap():
            raise WrongArgumentError("Parameter (af_name) is already taken.")

        # Il faut que la taille de la grille correspondent au raster
        if not isinstance(grid, list) or not isinstance(grid[0], list):
            raise WrongArgumentError("grid must be a 2x2 list")
        if len(grid) != raster.nrow or len(grid[0]) != raster.ncol:
            raise WrongArgumentError("Size of grid must be " + str(raster.nrow)
                                     + "x" + str(raster.ncol) + ":"
                                     + str(len(grid)) + "x" + str(len(grid[0])))

        self.raster = raster
        self.af_name = af_name
        self.grid = grid
    

    def getName(self):
        return self.af_name

    @staticmethod
    def getMeasureName(af_algo:Union[int, str], aggregate=None):
        """
        Return the identifier of the measure defined by: af + aggregate operator
        """
        if af_algo != "uid":
            if isinstance(af_algo, str):
                cle = af_algo + "#" + aggregate.__name__
            else:
                cle = af_algo.__name__ + "#" + aggregate.__name__
        else:
            cle = "uid" + "#" + aggregate.__name__
                
        return cle


    def plotAsGraphic(self, backgroundcolor="lightcyan", bordercolor="lightgray"):   
        """ 
        Plot as vector grid. 
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
    
        for i in range(0, self.raster.ncol):
            xi = i * self.raster.resolution[0] + self.raster.xmin
            ax.plot([xi, xi], [self.raster.ymin, self.raster.ymax], "-", color=bordercolor)

        for j in range(0, self.raster.nrow):
            yj = j * self.raster.resolution[1] + self.raster.ymin
            ax.plot([self.raster.xmin, self.raster.xmax], [yj, yj], "-", color=bordercolor)


        for j in range(self.raster.nrow):
            ysize = self.raster.resolution[1]
            y1 = self.raster.ymin + (self.raster.nrow - 1 - j) * ysize
            y2 = self.raster.ymin + (self.raster.nrow - j) * ysize

            for i in range(self.raster.ncol):
                xsize = self.raster.resolution[0]
                x1 = self.raster.xmin + i * xsize
                x2 = x1 + self.raster.resolution[0]

                if self.grid[j][i] != NO_DATA_VALUE:
                    pass
                    '''
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
                    '''
        plt.title(self.getName())


    def plotAsImage(self, append=False,
                    color1 = (0, 0, 0), color2 = (255, 255, 255),
                    novaluecolor='white', cmap=None):
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
        if self.raster.getNoDataValue() != None:
            tab[tab == self.raster.getNoDataValue()] = np.nan

        if cmap is None:
            cmap = getOffsetColorMap(color1, color2, 0)
            cmap.set_bad(color=novaluecolor)


        im = ax1.imshow(tab, cmap=cmap)
        ax1.set_title(self.getName())
        
        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right', size='5%', pad=0.1)
        if fig != None:
            fig.colorbar(im, cax=cax, orientation='vertical', fraction=0.046)


    def bandStatistics(self):
        stats = np.array(self.grid, dtype=np.float32)
        if self.raster.getNoDataValue() != None:
            stats[stats == self.raster.getNoDataValue()] = np.nan

        print("-------------------------------------")
        print("Grid '" + self.af_name + "':")
        print("-------------------------------------")
        print("    Minimum value: ", np.nanmin(stats))
        print("    Maximum value: ", np.nanmax(stats))
        print("    Mean value:    ", np.nanmean(stats))
        print("    Median value:  ", np.nanmedian(stats))
        print("-------------------------------------\n")
        
        if self.raster.getNoDataValue() != None:
            stats[stats == None] = self.raster.getNoDataValue()




    # def upSampling(self, resolution, name='Upsampling') -> AFMap:
    #     '''
    #     Interpolation Methods for Upsampling:
    #         - Nearest Neighbor: this method involves duplicating the existing 
    #                             pixels to create new ones.
    #     '''

    #     if not isinstance(self.__bbox.ur, ENUCoords):
    #         raise CoordTypeError('Only ENU coordinates system implemented')

    #     if self.XPixelSize != self.YPixelSize:
    #         raise SizeError('cells must be square.')


    #     newafmap = AFMap(self.__bbox,
    #                         resolution=(resolution[0], resolution[1]),
    #                         margin=0,
    #                         novalue=self.__noDataValue,
    #                         name=name, verbose=False)

    #     '''
    #     # Il faut aussi une résoltion proportionnelle entre les deux rasters
    #     N = int (self.XPixelSize / new_grid.XPixelSize)
    #     if int(N - (self.XPixelSize / new_grid.XPixelSize)) != 0.0:
    #         raise SizeError('Two grids resolution not proportional')
    #     # print ('N =', N)

    #     if interpolation == MODE_NEAREST_NEIGHBOR:
    #         for i in range(self.nrow):
    #             for j in range(self.ncol):
    #                 v = self.grid[i][j]
    #                 for k in range(0, N):
    #                     for l in range(0, N):
    #                         new_grid.grid[i*N + k][j*N + l] = v
    #         return new_grid

    #     '''
    #     return None


    # def asNumpy(self) -> np.ndarray:
    #     '''
    #     Returns the grid converted in numpy array
    #     '''
    #     return np.array(self.grid, dtype=np.float32)




