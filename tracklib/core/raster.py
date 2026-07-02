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
from matplotlib.axes import Axes

import sys
import math
import numpy as np
from collections import defaultdict
from collections import Counter

from abc import ABCMeta, abstractmethod

from tracklib.core import listify
from tracklib.core import ECEFCoords, ENUCoords, GeoCoords, getOffsetColorMap
from tracklib.core import Bbox
# from tracklib.core import isnan
#   co_count, co_sum, co_min, co_max, co_avg,
#   co_dominant, co_median, co_count_distinct
from tracklib.util import AnalyticalFeatureError, CoordTypeError, SizeError, WrongArgumentError


# co_sum
# co_min              : OK
# co_max              : OK
# co_count            : OK
# co_count_distinct   : OK
# co_avg              : OK
# co_dominant
# co_median


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
        self.bbox = bb
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


    def getNoDataValue(self):
        return self.__noDataValue
    def setNoDataValue(self, novalue):
        self.__noDataValue = novalue

    def getResolution(self):
        return self.resolution

    def countAFMap(self):
        """Return the number of bands in this raster"""
        return len(self.__afmaps)

    def getNamesOfAFMap(self):
        """Return all names of raster bands in a list."""
        return list(self.__afmaps.keys())


    def getAFMap(self, identifier: Union[int,str]) -> AFMap:
        """Return the AFMap according to name"""
        if isinstance(identifier, str):
            return self.__afmaps[identifier]
        if isinstance(identifier, int):
            name = list(self.__afmaps.keys())[identifier]
            return self.__afmaps[name]
        raise KeyError(identifier)


    def addAFMap(self, af_name:str):
        # Est-ce qu'elle existe ?
        if af_name in list(self.__afmaps.keys()):
            afmap = self.__afmaps[af_name]
        else:
            afmap = AFMap(self, af_name)
            self.__afmaps[af_name] = afmap
        return afmap


    def getCell(self, coord: Union[ENUCoords, ECEFCoords, GeoCoords])-> Union[tuple[int, int], None]:
        """
        Normalized coordinates of coord
    
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

        return (column, line)


    def accumulate(self, collection):
        '''
        Parameters
        ----------
        collection : TrackCollection
            tracks collection.

        Returns
        -------
        None.
        '''
    
        # On vérifie que les AF sont calculés
        for trace in collection.getTracks():
            for afname in self.getNamesOfAFMap():
                if not trace.hasAnalyticalFeature(afname) and afname != 'uid':
                    raise AnalyticalFeatureError("Error: track does not contain analytical feature '" + afname + "'")

        for track in collection.getTracks():
            # On éparpille dans les cellules
            for i in range(track.size()):
                obs = track.getObs(i)
                (column, line) = self.getCell(obs.position)
                for afname in self.getNamesOfAFMap():
                    '''
                    if afname != "uid":
                        val = track.getObsAnalyticalFeature(afname, i)
                    else:
                        val = track.uid
                    '''

                    for bandname in self.__afmaps[afname].bands:
                        band = self.__afmaps[afname].bands[bandname]
                        band.accumulate((line, column), i, track, afname)

                    #for aggregator in aggregators:
                    # aggregator.update(cell, value)
                    #self.collectionValuesGrid[afname][(line, column)].append(val)


    def compute(self):
        for afname in self.getNamesOfAFMap():
            for bandname in self.__afmaps[afname].bands:
                band = self.__afmaps[afname].bands[bandname]
                band.finalize()


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


    def writeToAscFile(self, band, pathG1):
        from tracklib.io import RasterWriter
        RasterWriter.writeMapToAscFile(pathG1, self, band)


class AFMap:
    '''
    Par exemple : AFMap(speed)
                    ├── mean
                    ├── max
                    ├── std
                    └── median

                AFMap(altitude)
                ├── mean
                ├── max

    Represents all band for few named matrix of values.
        Attributes: 
            - name : the name of AF
            - raster which defines spatial information
            - mean, max, std, median
    '''

    def __init__(self, raster, af_name):

        if not isinstance(raster, Raster):
            raise WrongArgumentError("First parameter need to be a Raster.")

        # Nom n'est pas déjà pris
        if af_name is None or af_name.strip() == '':
            raise WrongArgumentError("Parameter (af_name) is empty.")
        if af_name in raster.getNamesOfAFMap():
            raise WrongArgumentError("Parameter (af_name) is already taken.")

        self.raster = raster
        self.af_name = af_name
        self.bands = {}

    def getName(self):
        return self.af_name

    def bandCount(self):
        return len(self.bands)

    def getNamesOfBand(self):
        """Return all names of raster bands in a list."""
        return list(self.bands.keys())


    def addCountDistinct(self):
        band = CountDistinctBand()
        self.addNewBand(band)
        return band

    def addValues(self, narray = None):
        band = GridBand()
        self.addNewBand(band)
        if not narray is None:
            band.setGrid(narray)
        return band

    def addCount(self):
        band = CountBand()
        self.addNewBand(band)
        return band

    def addMean(self):
        band = MeanBand()
        self.addNewBand(band)
        return band

    def addMax(self):
        band = MaxBand()
        self.addNewBand(band)
        return band

    def addMin(self):
        band = MinBand()
        self.addNewBand(band)
        return band

    def addDominant(self):
        band = DominantBand()
        self.addNewBand(band)
        return band

    def addMedian(self):
        band = MedianBand()
        self.addNewBand(band)
        return band

    def addNewBand(self, band):
        band.initialize((self.raster.nrow, self.raster.ncol), self.raster.getNoDataValue())
        self.bands[band.getName()] = band


    def __getitem__(self, k):
        if isinstance(k, str):
            if k not in self.getNamesOfBand():
                raise WrongArgumentError("Index '{af_name}' does not exist.")
            return self.bands[k]
        if isinstance(k, int):
            name = list(self.bands.keys())[k]
            return self.bands[name]
        raise KeyError(k)


    def plot(self, band="values", **kwargs):
        self[band].plot(**kwargs)

    def histogram(self, band="values", **kwargs):
        if band not in self.getNamesOfBand():
            raise WrongArgumentError("Index '{band}' does not exist.")

        self[band].histogram(**kwargs)

    def plotAsVectorGraphic(self, band="values", **kwargs):
        self[band]._plotAsVectorGraphic(self.raster, **kwargs)


    def filter(self, band="values",
               mask = np.array([[0,1,0],[1,1,1],[0,1,0]]), aggregation=np.max):

        if band not in self.getNamesOfBand():
            raise WrongArgumentError("Index '{band}' does not exist.")

        self[band].getGrid().filter(mask, aggregation)


class Grid2D:

    def __init__(self, nrow, ncol, dtype=float):
        self.values = np.zeros((nrow, ncol), dtype=dtype)

    def plot(self, append=False, cmap='turbo', vmin=None, title=''):
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
                fig = ax1.get_figure()
            else:
                fig, ax1 = plt.subplots(figsize=(8, 8))
                ax1.set_aspect('equal')
        elif isinstance(append, Axes):
            ax1 = append
            fig = ax1.get_figure()
        else:
            fig, ax1 = plt.subplots(figsize=(8, 8))

        color1 = (0, 0, 0)
        color2 = (255, 255, 255)

        if cmap is None:
            cmap = getOffsetColorMap(color1, color2, 0)
            cmap.set_bad(color='white')

        if vmin is not None:
            im = ax1.imshow(self.values, cmap=cmap, vmin=vmin)
        else:
            im = ax1.imshow(self.values, cmap=cmap)

        ax1.set_title(title)

        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right', size='5%', pad=0.1)
        if fig != None:
            fig.colorbar(im, cax=cax, orientation='vertical', fraction=0.046)

    def histogram(self):

        stats = np.array(self.values, dtype=np.float32)

        print("-------------------------------------")
        print("Grid :")
        print("-------------------------------------")
        print("    Minimum value: ", np.nanmin(stats))
        print("    Maximum value: ", np.nanmax(stats))
        print("    Mean value:    ", np.nanmean(stats))
        print("    Median value:  ", np.nanmedian(stats))
        print("-------------------------------------\n")
        
    def interpolate(self):
        pass


    def filter(self, mask, aggregation):
        if (mask.shape[0] != mask.shape[1]):
            print("Error: mask must be a square matrix"); sys.exit()
        if (mask.shape[0]%2 == 0):
            print("Error: mask must be odd-size matrix"); sys.exit()
        if (np.any(mask.T - mask) != 0):
            print("Error: mask must be a symmetric matrix"); sys.exit()

        output = self.values*0; mask_temp = mask*0
        s = int((mask.shape[0]-1)/2)
        for i in range(s, output.shape[0]-s):
            for j in range(s, output.shape[1]-s):
                value = aggregation(
                    self.values[(i-s):(i+s+1), (j-s):(j+s+1)] * mask
                )
                
                if isinstance(value, np.ndarray):
                    if value.size != 1:
                        raise ValueError(
                            "Aggregation function must return a scalar."
                        )
                    value = value.item()
    
                output[i, j] = value

                # output[i,j] = aggregation(self.values[(i-s):(i+s+1), (j-s):(j+s+1)]*mask)
        self.values = output

    def _plotAsVectorGraphic(self, raster,
                            backgroundcolor="lightsteelblue", bordercolor="lightgray",
                            append=False):
        """ 
        Plot as vector grid. 
        """
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
                fig = ax1.get_figure()
            else:
                # figsize=(8, 8)
                fig, ax1 = plt.subplots()
                # ax1.set_aspect('equal')
        elif isinstance(append, Axes):
            ax1 = append
            fig = ax1.get_figure()
        else:
            fig, ax1 = plt.subplots(figsize=(8, 8))

        for i in range(0, raster.ncol+1):
            xi = raster.xmin + i * raster.resolution[0]
            y1 = raster.ymin
            y2 = raster.ymin + raster.nrow * raster.resolution[1]
            ax1.plot([xi, xi], [y1, y2], "-", color=bordercolor)

        for j in range(0, raster.nrow+1):
            yj = j * raster.resolution[1] + raster.ymin
            x1 = raster.xmin
            x2 = raster.xmin + raster.ncol * raster.resolution[0]
            ax1.plot([x1, x2], [yj, yj], "-", color=bordercolor)

        for j in range(raster.nrow):
            ysize = raster.resolution[1]
            y1 = raster.ymin + (raster.nrow - 1 - j) * ysize
            y2 = raster.ymin + (raster.nrow - j) * ysize

            for i in range(raster.ncol):
                xsize = raster.resolution[0]
                x1 = raster.xmin + i * xsize
                x2 = x1 + raster.resolution[0]

                if self.values[j][i] != raster.getNoDataValue():
                    polygon = plt.Polygon(
                        [[x1, y1], [x2, y1], [x2, y2], [x1, y2], [x1, y1]]
                    )
                    ax1.add_patch(polygon)
                    polygon.set_facecolor(backgroundcolor)
                    
                    text_kwargs = dict(ha='center', va='center', fontsize=12, color='r')
                    val = str(round(self.values[j][i], 2))
                    xm = (x2 - x1) / 2
                    ym = (y2 - y1) / 2
                    plt.text(x1 + xm, y1 + ym, val, **text_kwargs)


class Band(metaclass=ABCMeta):

    def __init__(self):
        self.name = "None"

    def getName(self):
        return self.name

    def getGrid(self):
        return self._grid2d

    @abstractmethod
    def initialize(self, shape, noDataValue):
        pass

    @abstractmethod
    def accumulate(self, cell, iobs, track, afname):
        """Accumulate one observation."""
        pass

    def finalize(self):
        """Finalize the computation."""
        pass

    def plot(self, *args, **kwargs):
        self._grid2d.plot(*args, **kwargs)
        plt.title(self.getName())

    def _plotAsVectorGraphic(self, raster, *args, **kwargs):
        self._grid2d._plotAsVectorGraphic(raster, *args, **kwargs)
        plt.title(self.getName())

    def histogram(self, *args, **kwargs):
        return self._grid2d.histogram(*args, **kwargs)

    def setGrid(self, grid):
        # Il faut que la taille de la grille correspondent au raster
        if not isinstance(grid, np.ndarray):
            raise WrongArgumentError("grid must be a ndarray")

        dim1 = grid.shape
        dim2 = self._grid2d.values.shape
        if dim1[0] != dim2[0] or dim1[1] != dim2[1]:
            raise WrongArgumentError("Size of grid must be " + str(dim2[0])
                                     + "x" + str(dim2[1]) + ":"
                                     + str(dim1[0]) + "x" + str(dim1[1]))

        #self._grid2d.values = grid
        self._grid2d.values[:, :] = grid

class CountDistinctBand(Band):

    def __init__(self):
        self.name = "count_distinct"

    def initialize(self, shape, noDataValue):
        """
        Initialize the band.

        Parameters
        ----------
        shape : tuple
            Raster shape (nrow, ncol).
        """
        self.shape = shape
        self.nodata = noDataValue
        self._cells = defaultdict(set)
        self._grid2d = Grid2D(shape[0], shape[1], np.uint32)
        self._grid2d.values = np.full(shape, float(noDataValue))


    def accumulate(self, cell, iobs, track, afname):
        """
        Register one observation.

        Parameters
        ----------
        cell : tuple
            Raster cell (row, column).
        obs : Obs
            Current observation (unused here).
        track : Track
            Current track.
        """
        if afname == 'uid':
            value = track.uid
        else:
            value = track.getObsAnalyticalFeature(afname, iobs)

        if value == self.nodata:
            return

        self._cells[cell].add(value)

    def finalize(self):
        """
        Compute the final raster.
        """
        # print (self._cells[0,0])
        for cell, ids in self._cells.items():
            self._grid2d.values[cell[0]][cell[1]] = len(ids)

        # Free memory
        del  self._cells


class CountBand(Band):

    def __init__(self):
        self.name = "count"

    def initialize(self, shape, noDataValue):
        """
        Initialize the band.

        Parameters
        ----------
        shape : tuple
            Raster shape (nrow, ncol).
        """
        self.nodata = noDataValue
        self.shape = shape
        self._grid2d = Grid2D(shape[0], shape[1], np.uint32)


    def accumulate(self, cell, iobs, track, afname):
        """
        Register one observation.

        Parameters
        ----------
        cell : tuple
            Raster cell (row, column).
        obs : Obs
            Current observation (unused here).
        track : Track
            Current track.
        """
        if afname == 'uid':
            value = track.uid
        else:
            value = track.getObsAnalyticalFeature(afname, iobs)

        if value == self.nodata:
            return

        self._grid2d.values[cell] += 1

    def finalize(self):
        """
        Compute the final raster.
        """
        pass


class MeanBand(Band):

    def __init__(self):
        self.name = "mean"
        self._grid2d = None
        self.sum = None
        self.count = None

    def initialize(self, shape, noDataValue):
        self.nodata = noDataValue
        self._grid2d = Grid2D(shape[0], shape[1], np.float32)
        self._grid2d.values = np.full(shape, float(noDataValue))

        self.sum = np.zeros(shape, dtype=np.float32)
        self.count = np.zeros(shape, dtype=np.uint32)

    def accumulate(self, cell, iobs, track, afname):
        if afname == 'uid':
            value = track.uid
        else:
            value = track.getObsAnalyticalFeature(afname, iobs)

        if value == self.nodata:
            return

        self.sum[cell] += value
        self.count[cell] += 1

    def finalize(self):

        #self._grid2d.values = self.sum / self.count

        np.divide(
            self.sum,
            self.count,
            out=self._grid2d.values,
            where=self.count != 0
        )

        # Free memory
        del  self.sum
        del  self.count


class SumBand(Band):

    def __init__(self):
        self.name = "sum"
        self._grid2d = None

    def initialize(self, shape, noDataValue):
        self.nodata = noDataValue
        self._grid2d = Grid2D(shape[0], shape[1], np.float32)

    def accumulate(self, cell, iobs, track, afname):
        if afname == 'uid':
            value = track.uid
        else:
            value = track.getObsAnalyticalFeature(afname, iobs)

        if value == self.nodata:
            return

        self._grid2d.values[cell] += value

    def finalize(self):
        pass


class MaxBand(Band):

    def __init__(self):
        self.name = "max"
        self._grid2d = None

    def initialize(self, shape, noDataValue):
        self.nodata = noDataValue
        self._grid2d = Grid2D(shape[0], shape[1], np.float32)

    def accumulate(self, cell, iobs, track, afname):
        if afname == 'uid':
            value = track.uid
        else:
            value = track.getObsAnalyticalFeature(afname, iobs)

        if value == self.nodata:
            return

        if value > self._grid2d.values[cell]:
            self._grid2d.values[cell] = value

    def finalize(self):
        pass


class MinBand(Band):

    def __init__(self):
        self.name = "min"
        self._grid2d = None

    def initialize(self, shape, noDataValue):
        self.nodata = noDataValue
        self._grid2d = Grid2D(shape[0], shape[1], np.float32)

    def accumulate(self, cell, iobs, track, afname):
        if afname == 'uid':
            value = track.uid
        else:
            value = track.getObsAnalyticalFeature(afname, iobs)

        if value == self.nodata:
            return

        if value < self._grid2d.values[cell]:
            self._grid2d.values[cell] = value

    def finalize(self):
        pass


class GridBand(Band):

    def __init__(self):
        self.name = "values"
        self._grid2d = None

    def initialize(self, shape, noDataValue):
        self.nodata = noDataValue
        self._grid2d = Grid2D(shape[0], shape[1], np.uint32)

    def accumulate(self, cell, iobs, track, afname):
        raise NotImplementedError()

    def finalize(self):
        pass


class DominantBand(Band):

    def __init__(self):
        self.name = "dominant"
        self._grid2d = None
        self._counts = None

    def initialize(self, shape, noDataValue):
        self.nodata = noDataValue
        self._grid2d = Grid2D(shape[0], shape[1], np.float32)
        self._grid2d.values = np.full(shape, float(noDataValue))

        # One dictionary of occurrences per cell
        self._counts = np.empty(shape, dtype=object)
        for cell in np.ndindex(shape):
            self._counts[cell] = Counter()


    def accumulate(self, cell, iobs, track, afname):
        if afname == 'uid':
            value = track.uid
        else:
            value = track.getObsAnalyticalFeature(afname, iobs)

        if value == self.nodata:
            return

        self._counts[cell][value] += 1

    def finalize(self):
        # print (self._counts[2,1])
        for cell in np.ndindex(self._counts.shape):
            counter = self._counts[cell]
            if len(counter) == 0:
                continue

            # Most frequent value
            dominant = self._counts[cell].most_common(1)[0][0]

            self._grid2d.values[cell] = dominant

        # Free memory
        del  self._counts


class MedianBand(Band):
    """Band computing the median value in each cell."""

    def __init__(self):
        self.name = "median"
        self._values = None
        self._grid2d = None

    def initialize(self, shape, noDataValue):
        self.nodata = noDataValue
        self._grid2d = Grid2D(shape[0], shape[1], np.float32)
        self._grid2d.values = np.full(shape, float(noDataValue))

        # One list of values per cell
        self._values = np.empty(shape, dtype=object)

        for cell in np.ndindex(shape):
            self._values[cell] = []

    def accumulate(self, cell, iobs, track, afname):
        if afname == 'uid':
            value = track.uid
        else:
            value = track.getObsAnalyticalFeature(afname, iobs)

        if value == self.nodata:
            return

        self._values[cell].append(value)

    def finalize(self):

        for cell in np.ndindex(self._values.shape):

            values = self._values[cell]

            if len(values) == 0:
                continue

            self._grid2d.values[cell] = np.median(values)

        # Free memory
        del  self._values
