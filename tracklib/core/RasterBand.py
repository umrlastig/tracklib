# -*- coding: utf-8 -*-

# For type annotation
from __future__ import annotations   
from typing import Union

import matplotlib.pyplot as plt

from tracklib.core.Bbox import Bbox
from tracklib.core.ObsCoords import ECEFCoords, ENUCoords, GeoCoords

NO_DATA_VALUE = -9999
DEFAULT_NAME = 'grid'


class RasterBand:
    """
    Class for defining a spatial grid: structure de données un peu plus évoluée
          qu'un tableau 2x2.
    Mainly used by :class:`core.SpatialIndex.SpatialIndex` and `algo.Summarizing.summarize`
    
    
    Parameters
    ----------
    nrow : int
       Numbers of rows.
    ncol : int
       Numbers of cols.
    
    
    """
    
    def __init__(
        self,
        bb: Bbox,
        resolution=None,
        margin: float = 0.05,
        novalue: float = NO_DATA_VALUE,
        name = DEFAULT_NAME,
        verbose: bool = True,
    ):
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
        (self.xmin, self.xmax, self.ymin, self.ymax) = bb.asTuple()
        #print (self.xmin, self.xmax)
        ax, ay = bb.getDimensions()
        #print (ax, ay)
    
        if resolution is None:
            am = max(ax, ay)
            r = am / 100
            resolution = (int(ax / r), int(ay / r))
        else:
            r = resolution
            #print (ax, r[0])
            resolution = (int(ax / r[0]), int(ay / r[1]))
        #print (resolution)
    
        # Nombre de dalles par cote
        self.ncol = resolution[0]
        self.nrow = resolution[1]
        #print (self.nrow, self.ncol)
    
        # Tableau de collections de features appartenant a chaque dalle.
        # Un feature peut appartenir a plusieurs dalles.
        self.grid = []
        for i in range(self.nrow):
            self.grid.append([])
            for j in range(self.ncol):
                self.grid[i].append(NO_DATA_VALUE)
    
        self.XPixelSize = ax / self.ncol
        self.YPixelSize = ay / self.nrow
        #print (self.XPixelSize, self.YPixelSize)
        
        self.noDataValue = novalue
        self.name = name
        
        
    def getName(self):
        return self.name
        
    
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
        if coord.E < self.xmin and coord.E > self.xmax:
            return False
        if coord.N < self.ymin and coord.N > self.ymax:
            return False
        
        return True
    
    
    def __str__(self):
        output  = "-------------------------------------\n"
        output += "Grid '" + self.name + "':\n"
        output += "       nrows = " + str(self.nrow) + "\n"
        output += "       ncols = " + str(self.ncol) + "\n"
        output += "       XPixelSize = " + str(self.XPixelSize) + "\n"
        output += "       YPixelSize = " + str(self.YPixelSize) + "\n"
        output += " Bounding box: \n"
        output += "       Lower left corner : " + str(self.xmin) + "," + str(self.ymin) + "\n"
        output += "       Upper right corner: " + str(self.xmax) + "," + str(self.ymax) + "\n"
        output += "-------------------------------------\n"
        
        return output
    
    
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
    
    
    def plot(self, base: bool = True):   
        """Plot grid
        
        :param base: TODO
        """
    
        fig = plt.figure()
        ax = fig.add_subplot(
            111, xlim=(self.xmin, self.xmax), ylim=(self.ymin, self.ymax)
        )
    
        for i in range(1, self.ncol):
            xi = i * self.XPixelSize + self.xmin
            ax.plot([xi, xi], [self.ymin, self.ymax], "-", color="lightgray")
        for j in range(1, self.nrow):
            yj = j * self.YPixelSize + self.ymin
            ax.plot([self.xmin, self.xmax], [yj, yj], "-", color="lightgray")
    
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
                    polygon.set_facecolor("lightcyan")
    
