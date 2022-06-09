# -*- coding: utf-8 -*-

"""
"""


from tracklib.core import (Bbox, Grid)
from tracklib.core.Coords import (ENUCoords)


class AsciiReader:
    
    @staticmethod
    def readFromFile(path, srid="ENUCoords"):
        
        with open (path, 'r') as fichier:
            ncols = int(fichier.readline()[5:].rstrip())
            nrows = int(fichier.readline()[5:].rstrip())
            xllcorner = float(fichier.readline()[9:].rstrip())
            yllcorner = float(fichier.readline()[9:].rstrip())
            cellsize = float(fichier.readline()[8:].rstrip())

            ll = ENUCoords(xllcorner, yllcorner, 0)
            ur = ENUCoords(xllcorner + cellsize * ncols, yllcorner + cellsize * nrows, 0)
            bbox = Bbox.Bbox(ll, ur)
            
            resolution = (cellsize, cellsize)
            marge = 0
            
            grid = Grid.Grid(bbox, resolution=resolution, margin=marge)
        
            return grid