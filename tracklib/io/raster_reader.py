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

    This class offer static methods to load raster data:
    - read raster from ascii files, 
    - get DTM data from IGN web services.    

"""

# For type annotation
from __future__ import annotations   
from tracklib.util.exceptions import *

from tracklib.core import (ENUCoords, Bbox, 
                           Raster, 
                           NO_DATA_VALUE,
                           AFMap)


class RasterReader:

    @staticmethod
    def readFromAscFile(path:str, name:str, separator=" ")-> Raster:
        '''
        Read grid data from an ASCII file. The first six lines of the file indicate the reference of the grid, 
        followed by the values listed in the order they would appear (left to right and top to bottom).
        Where:
            - ncols is the numbers of rows (represented as integers)
            - nrows is the numbers of rows (represented as integers)
            - Lower-left corner refers to a cell corner, and not to a data point
            - xllcorner and yllcorner are the western (left) X coordinate and southern (bottom) Y coordinates, such as easting and northing (represented as real numbers with an optional decimal point)
            - xllcorner and yllcorner are the X and Y coordinates for the lower left corner of the lower left grid cell. Some ESRI raster files use xllcenter and yllcenter instead for the XY reference point, which indicate the X and Y coordinates for the center of the lower left grid cell. These values are represented as real numbers with an optional decimal point
            - cellsize is the length of one side of a square cell (a real number)
            - nodata_value is the value that is regarded as "missing" or "not applicable"; this line is optional, but highly recommended as some programs expect this line to be declared (a real number)

        
        Example
        *********
        
        .. code-block:: python
        
           raster = RasterReader.readFromAscFile('data/asc/RGEALTI_0930_6415_LAMB93_IGN69.asc')
           grid = raster.getAFMap(1)
           self.assertEqual(1000, grid.nrow)


        Parameters
        -----------
        path : str
            chemin du fichier.
        name: str
            nom de l'AF du raster, par exemple 'z, speed, etc.'

        Returns
        --------
        Raster
            DESCRIPTION.

        '''
        
        with open (path, 'r') as fichier:
            lines = fichier.readlines()
            fichier.close()
            
        cptrowheader = 0
        for line in lines:
            cle = line.split(separator)[0].strip()
            if cle.lower() in  ['ncols', 'nrows', 'xllcorner', 'yllcorner', 'cellsize', 'nodata_value']:
                cptrowheader += 1

        raster = RasterReader.readMetadataFromAscFile(path, separator)

        grid = []
        for i in range(raster.nrow):
            grid.append([])
            for j in range(raster.ncol):
                grid[i].append(raster.getNoDataValue())

        # Read the values
        i = 0
        for line in lines[cptrowheader:]:
            lineValues = line.split(separator)
            j = 0
            for val in lineValues:
                if val.strip() == '':
                    continue
                grid[i][j] = float(val)
                j += 1
            i += 1

        # Return raster with one grid
        raster.addAFMap(name, grid)
        return raster
    
    
    @staticmethod
    def readMetadataFromAscFile(path: str, separator=" ")-> Raster:
        '''
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
        novalue = NO_DATA_VALUE
        for line in lines:
            cle = line.split(separator)[0].strip()

            if cle.lower() in  ['ncols', 'nrows', 'xllcorner', 'yllcorner', 'cellsize', 'nodata_value']:
                cptrowheader += 1
                i = 1
                val = line.split(separator)[1].strip()
                while val == '':
                    i += 1
                    val = line.split(separator)[i].strip()

                if cle.lower() == 'ncols':
                    ncols = int(val)
                if cle.lower() == 'nrows':
                    nrows = int(val)
                if cle.lower() == 'xllcorner':
                    xllcorner = float(val)
                if cle.lower() == 'yllcorner':
                    yllcorner = float(val)
                if cle.lower() == 'cellsize':
                    cellsize = int(float(val))
                if cle.lower() == 'NODATA_value':
                    novalue = float(val)

            else:
                break
                    
        ll = ENUCoords(xllcorner, yllcorner, 0)
        ur = ENUCoords(xllcorner + cellsize * ncols, yllcorner + cellsize * nrows, 0)
        bbox = Bbox(ll, ur)
            
        resolution = (cellsize, cellsize)
        marge = 0

        return Raster(bbox, resolution=resolution, margin=marge,
                          novalue=novalue)

    
    

        

      
        
        