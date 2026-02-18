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
import sys
import math
import numpy as np
from collections import defaultdict

from tracklib.core import listify
from tracklib.core import ECEFCoords, ENUCoords, GeoCoords, getOffsetColorMap
from tracklib.core import Bbox
from tracklib.core import (isnan,
                           co_count, co_sum, co_min, co_max, co_avg,
                           co_dominant, co_median, co_count_distinct)
from tracklib.util import AnalyticalFeatureError, CoordTypeError, SizeError, WrongArgumentError



# -----------------------------------------------------------------------------
#  Value that is regarded as "missing" or "not applicable"
# -----------------------------------------------------------------------------
NO_DATA_VALUE = -99999.0


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
BBOX_ALIGN_CENTER = 1
BBOX_ALIGN_LL= 2
BBOX_ALIGN_UR= 3


class Raster:
    
    def __init__(self, bbox: Bbox,
                 resolution:tuple[float, float]=(100, 100),
                 margin:float=0.05,
                 align=BBOX_ALIGN_LL,
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
        ax, ay = bb.getDimensions()

        self.resolution = resolution

        self.ncol = math.ceil(ax / resolution[0])
        self.nrow = math.ceil(ay / resolution[1])

        if align == BBOX_ALIGN_LL:
            (self.xmin, self.xmax, self.ymin, self.ymax) = bb.asTuple()
            self.xmax = self.xmin + float(self.resolution[0]) * self.ncol
            self.ymax = self.ymin + float(self.resolution[1]) * self.nrow
        elif align == BBOX_ALIGN_CENTER:
            diffx = (float(self.resolution[0]) * self.ncol - ax) / 2
            self.xmin = bb.getXmin() - diffx
            self.xmax = bb.getXmax() + diffx
            diffy = (float(self.resolution[1]) * self.nrow - ay) / 2
            self.ymin = bb.getYmin() - diffy
            self.ymax = bb.getYmax() + diffy
        elif align == BBOX_ALIGN_UR:
            (self.xmin, self.xmax, self.ymin, self.ymax) = bb.asTuple()
            self.xmin = self.xmax - float(self.resolution[0]) * self.ncol
            self.ymin = self.ymax - float(self.resolution[1]) * self.nrow
        else:
            raise WrongArgumentError("e value of the ‘align’ parameter is not recognizd.")

        self.__noDataValue = novalue

        self.__afmaps = {}


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
        output += "Raster:                              \n"
        output += "-------------------------------------\n"
        output += "       nrows = " + str(self.nrow) + "\n"
        output += "       ncols = " + str(self.ncol) + "\n"
        output += "       XPixelSize = " + str(self.resolution[0]) + "\n"
        output += "       YPixelSize = " + str(self.resolution[1]) + "\n"
        w = float(self.resolution[0]) * self.ncol
        h = float(self.resolution[1]) * self.nrow
        output += "       Extent: width = " + str(w) + ", height = " + str(h) + "\n"
        output += "   Bounding box: \n"
        output += "       Lower left corner : " + str(self.xmin) + ", " + str(self.ymin) + "\n"
        output += "       Upper right corner: " + str(self.xmax) + ", " + str(self.ymax) + "\n"
        output += "-------------------------------------\n"
        
        return output

    def getResolution(self):
        return self.resolution
    
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
        '''
        grid peut-être vide (si on summarize) ou non (via reader)
        '''
        if grid is None:
            grid = np.full([self.nrow, self.ncol],
                           self.getNoDataValue(),
                           dtype=np.float32)
        afmap = AFMap(self, name, grid)
        self.__afmaps[name] = afmap


    def addCollectionToRaster(self, collection):
        '''
        L'enjeu ici est de stocker qu'une fois chaque AF. 
        Il faut donc que les maps soient déjà créées.

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

        # On vérifie que les AF sont calculés
        for trace in collection.getTracks():
            for afname in AFs:
                if not trace.hasAnalyticalFeature(afname) and afname != 'uid':
                    raise AnalyticalFeatureError("Error: track does not contain analytical feature '" + afname + "'")


        # On initialise le dictionnaire qui va contenir toutes les valeurs
        self.collectionValuesGrid = {}
        for afname in AFs:
            self.collectionValuesGrid[afname] = defaultdict(list)

        for trace in collection.getTracks():
            # On éparpille dans les cellules
            for i in range(trace.size()):
                obs = trace.getObs(i)
                (column, line) = self.getCell(obs.position)
                for afname in AFs:
                    if afname != "uid":
                        val = trace.getObsAnalyticalFeature(afname, i)
                    else:
                        val = trace.uid
                    self.collectionValuesGrid[afname][(line, column)].append(val)


    def computeAggregates(self):
        for k in range(self.countAFMap()):
            afmap = self.getAFMap(k)
            names = afmap.getName().split('#')
            afname = names[0]
            aggregate = names[1]

            for (i, j), tarray in self.collectionValuesGrid[afname].items():
                sumval = eval(aggregate + '(tarray)')
                if not isnan(sumval):
                    afmap.grid[i][j] = sumval


class AFMap:
    '''
    Represents a named matrix of values.
        Attributes: 
            - name (AF name) follows template: algo_name + '#' + aggregate operator name
            - 2D array
            - raster which defines spatial information
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
        if not isinstance(grid, np.ndarray):
            raise WrongArgumentError("grid must be a ndarray")
        dim = grid.shape
        if dim[0] != raster.nrow or dim[1] != raster.ncol:
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


    def plotAsVectorGraphic(self, backgroundcolor="lightsteelblue", bordercolor="lightgray"):
        """ 
        Plot as vector grid. 
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)

        for i in range(0, self.raster.ncol+1):
            xi = self.raster.xmin + i * self.raster.resolution[0]
            y1 = self.raster.ymin
            y2 = self.raster.ymin + self.raster.nrow * self.raster.resolution[1]
            ax.plot([xi, xi], [y1, y2], "-", color=bordercolor)

        for j in range(0, self.raster.nrow+1):
            yj = j * self.raster.resolution[1] + self.raster.ymin
            x1 = self.raster.xmin
            x2 = self.raster.xmin + self.raster.ncol * self.raster.resolution[0]
            ax.plot([x1, x2], [yj, yj], "-", color=bordercolor)

        for j in range(self.raster.nrow):
            ysize = self.raster.resolution[1]
            y1 = self.raster.ymin + (self.raster.nrow - 1 - j) * ysize
            y2 = self.raster.ymin + (self.raster.nrow - j) * ysize

            for i in range(self.raster.ncol):
                xsize = self.raster.resolution[0]
                x1 = self.raster.xmin + i * xsize
                x2 = x1 + self.raster.resolution[0]

                if self.grid[j][i] != self.raster.getNoDataValue():
                    polygon = plt.Polygon(
                        [[x1, y1], [x2, y1], [x2, y2], [x1, y2], [x1, y1]]
                    )
                    ax.add_patch(polygon)
                    polygon.set_facecolor(backgroundcolor)
                    
                    text_kwargs = dict(ha='center', va='center', fontsize=12, color='r')
                    val = str(round(self.grid[j][i], 2))
                    xm = (x2 - x1) / 2
                    ym = (y2 - y1) / 2
                    plt.text(x1 + xm, y1 + ym, val, **text_kwargs)

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

        matrice = np.full((self.raster.nrow, self.raster.ncol),
                          self.raster.getNoDataValue(), dtype=np.float32)
        for i in range(self.raster.nrow):
            for j in range(self.raster.ncol):
                val = float(self.grid[i][j])
                if val != self.raster.getNoDataValue():
                    matrice[i][j] = val
        if self.raster.getNoDataValue() != None:
            matrice[matrice == self.raster.getNoDataValue()] = np.nan

        if cmap is None:
            cmap = getOffsetColorMap(color1, color2, 0)
            cmap.set_bad(color=novaluecolor)

        im = ax1.imshow(matrice, cmap=cmap)
        ax1.set_title(self.getName())

        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right', size='5%', pad=0.1)
        if fig != None:
            fig.colorbar(im, cax=cax, orientation='vertical', fraction=0.046)

    # ------------------------------------------------------------------
    # Filter operation on an AFMap
    # ------------------------------------------------------------------
    # Inputs (outputs void):
    #     - mask        :      a (2n+1) x (2n+1) float number matrix 
    #     - aggregation :      a python function [mask -> float number]
    # ------------------------------------------------------------------
    def filter(self, mask, aggregation):
        if (mask.shape[0] != mask.shape[1]):
            print("Error: mask must be a square matrix"); sys.exit()
        if (mask.shape[0]%2 == 0):
            print("Error: mask must be odd-size matrix"); sys.exit()
        if (np.any(mask.T - mask) != 0):
            print("Error: mask must be a symmetric matrix"); sys.exit()
        output = self.grid*0; mask_temp = mask*0
        s = int((mask.shape[0]-1)/2)
        for i in range(s, output.shape[0]-s):
            for j in range(s, output.shape[1]-s):
                output[i,j] = aggregation(self.grid[(i-s):(i+s+1), (j-s):(j+s+1)]*mask)
        self.grid = output

    def statistics(self):
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





