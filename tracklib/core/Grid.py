#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -------------------------- Grid -------------------------------
#   Matrice à 2 dimensions
#     Opérations avec ....
#
# ----------------------------------------------------------------
import matplotlib.pyplot as plt

from tracklib.core.Bbox import Bbox


class Grid:
    """ 
        Pour IndexSpatial et Summarizng
        
        grid[icol][jrow] = list or dict
    """
    
    def __init__(self, collection, resolution=None, margin=0.05, verbose=True):
        '''
        Grid constructor. 
        
        Margin : relative float. Default value is +5%
        
        '''
        # Bbox only or collection
        if isinstance(collection, Bbox):
            bb = collection
        else:
            bb = collection.bbox()
            
        bb = bb.copy()
        bb.addMargin(margin)
        (self.xmin, self.xmax, self.ymin, self.ymax) = bb.asTuple()

        ax, ay = bb.getDimensions()
        
        if resolution is None:
            am = max(ax, ay)
            r = am/100
            resolution = (int(ax/r), int(ay/r))
        else:
            r = resolution
            resolution = (int(ax/r[0]), int(ay/r[1]))

        self.collection = collection
        
        # Nombre de dalles par cote
        self.ncol = resolution[0]
        self.nrow = resolution[1]
        
        # Tableau de collections de features appartenant a chaque dalle. 
        # Un feature peut appartenir a plusieurs dalles.
        self.grid = []
        for i in range(self.ncol):
            self.grid.append([])
            for j in range(self.nrow):
                self.grid[i].append([])
                
        self.XPixelSize = ax / self.ncol
        self.YPixelSize = ay / self.nrow
        
        
        
    # ------------------------------------------------------------
    # Normalized coordinates of coord: (x,) -> (i,j) with:
    #   i = (x-xmin)/(xmax-xmin)*nb_cols
    #   j = (y-ymin)/(ymax-ymin)*nb_rows
    # Returns None if out of grid
    # ------------------------------------------------------------
    def getCell(self, coord):
        
        if (coord.getX() < self.xmin) or (coord.getX() > self.xmax):
            overflow = '{:5.5f}'.format(max(self.xmin-coord.getX(), coord.getX()-self.xmax))
            print('Warning: x overflow '+str(coord)+"  OVERFLOW = "+str(overflow))
            return None
        if (coord.getY() < self.ymin) or (coord.getY() > self.ymax):
            overflow = '{:5.5f}'.format(max(self.ymin-coord.getY(), coord.getY()-self.ymax))
            print('Warning: y overflow '+str(coord)+"  OVERFLOW = "+str(overflow))
            return None

        idx = (float(coord.getX()) - self.xmin) / self.XPixelSize
        idy = (float(coord.getY()) - self.ymin) / self.YPixelSize
                
        return (idx, idy)

        
    def plot(self, base=True, af_algo = None, aggregate = None):

        fig = plt.figure()
        ax = fig.add_subplot(111, xlim=(self.xmin, self.xmax), ylim=(self.ymin, self.ymax))
        
        for i in range(1,self.ncol):
            xi = i*self.XPixelSize + self.xmin
            ax.plot([xi,xi], [self.ymin, self.ymax], '-',color='lightgray')
        for j in range(1,self.nrow):
            yj = j*self.YPixelSize + self.ymin
            ax.plot([self.xmin, self.xmax], [yj,yj], '-',color='lightgray')
        
        if base:
            self.collection.plot(append=ax)

        for i in range(self.ncol):
            xi1 = i*self.XPixelSize + self.xmin; xi2 = xi1 + self.XPixelSize
            for j in range(self.nrow):
                yj1 = j*self.YPixelSize + self.ymin; yj2 = yj1 + self.YPixelSize
                if len(self.grid[i][j]) > 0:
                    print (self.grid[i][j])
                    polygon = plt.Polygon(
                         [[xi1, yj1], [xi2, yj1], [xi2, yj2], [xi1, yj2], [xi1, yj1]])
                    ax.add_patch(polygon)
                    polygon.set_facecolor('lightcyan')


