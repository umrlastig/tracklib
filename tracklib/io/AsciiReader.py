# -*- coding: utf-8 -*-

"""
"""
from tracklib.core import (Bbox, Grid, Raster)
from tracklib.core.Coords import (ENUCoords)


class AsciiReader:
    
    CLES = ['ncols', 'nrows', 'xllcorner', 'yllcorner', 'cellsize', 'NODATA_value']
    
    @staticmethod
    def readFromAscFile(path, srid="ENUCoords", name=''):
        '''

        Parameters
        ----------
        path : str
            chemin du fichier contenent.
        srid : TYPE, optional
            DESCRIPTION. The default is "ENUCoords".

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        
        with open (path, 'r') as fichier:
            lines = fichier.readlines()
            fichier.close()
            
        # Build an empty grid
        xllcorner = 0
        yllcorner = 0
        cellsize = 0
        nrows = 0
        ncols = 0
        
        cptrowheader = 0
        novalue = Grid.NO_DATA_VALUE
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
                if cle == 'NODATA_value':
                    novalue = float(val)
            else:
                break
                    
        ll = ENUCoords(xllcorner, yllcorner, 0)
        ur = ENUCoords(xllcorner + cellsize * ncols, yllcorner + cellsize * nrows, 0)
        bbox = Bbox.Bbox(ll, ur)
            
        resolution = (cellsize, cellsize)
        marge = 0
            
        grid = Grid.Grid(bbox, resolution=resolution, margin=marge, 
                         novalue=novalue, name=Grid.DEFAULT_NAME + '1')
           
        # Read the values
        i = 0
        for line in lines[cptrowheader:]:
            lineValues = line.split(" ")
            j = 0
            for val in lineValues:
                if val.strip() == '':
                    continue
                
                grid.grid[j][i] = float(val)
                j += 1
                
            i += 1

        # Return raster with one grid            
        return Raster.Raster(grid)
        
    