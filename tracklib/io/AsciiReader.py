# -*- coding: utf-8 -*-

"""
"""
import numpy as np

from tracklib.core import (Bbox, Grid)
from tracklib.core.Coords import (ENUCoords)


class AsciiReader:
    
    CLES = ['ncols', 'nrows', 'xllcorner', 'yllcorner', 'cellsize', 'NODATA_value']
    
    @staticmethod
    def readFromFile(path, srid="ENUCoords"):
        
        with open (path, 'r') as fichier:
            lines = fichier.readlines()
            fichier.close()
            
            cptrowheader = 0
            for line in lines:
                cle = line.split(" ")[0].strip()
                if cle in AsciiReader.CLES:
                    cptrowheader += 1
                    
                    i = 1
                    val = line.split(" ")[1].strip()
                    while val == '':
                        i += 1
                        val = line.split(" ")[i].strip()
                    
                    if cle == 'ncols':
                        ncols = int(val)
                    if cle == 'nrows':
                        nrows = int(val)
                    if cle == 'xllcorner':
                        xllcorner = float(val)
                    if cle == 'yllcorner':
                        yllcorner = float(val)
                    if cle == 'cellsize':
                        cellsize = int(float(val))
                else:
                    break
                    
            ll = ENUCoords(xllcorner, yllcorner, 0)
            ur = ENUCoords(xllcorner + cellsize * ncols, yllcorner + cellsize * nrows, 0)
            bbox = Bbox.Bbox(ll, ur)
            
            resolution = (cellsize, cellsize)
            marge = 0
            
            grid = Grid.Grid(bbox, resolution=resolution, margin=marge)
            
            matrice = np.loadtxt(path, skiprows=cptrowheader, dtype=np.int16)
            grid.grid = matrice.T
        
            return grid
        
    