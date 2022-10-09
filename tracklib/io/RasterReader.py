
# For type annotation
from __future__ import annotations   
from typing import Union

from tracklib.core import (Bbox, Coords, RasterBand, Raster)
from tracklib.core.Coords import (ENUCoords)


class RasterReader:
    '''
    This class offer static methods to load raster data:
    - read raster from ascii files, 
    - get DTM data from IGN web services.    
    '''
    
    @staticmethod
    def readFromAscFile(path: str, 
                        srid: Union[Coords.ENUCoords, Coords.ENUCoords, Coords.GeoCoords] =  ENUCoords,  
                        name: str ='')-> Raster:
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
           grid = raster.getRasterBand(1)
           self.assertEqual(1000, grid.nrow)


        Parameters
        -----------
        path : str
            chemin du fichier.
        srid : str
            nom de la classe représentant le type des coordonnées. The default is "ENUCoords".
        name: str
            nom de la band du raster, par exemple 'speed#avg'

        Returns
        --------
        Raster
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
        novalue = RasterBand.NO_DATA_VALUE
        for line in lines:
            cle = line.split(" ")[0].strip()
            if cle in  ['ncols', 'nrows', 'xllcorner', 'yllcorner', 'cellsize', 'NODATA_value']:
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
            
        grid = RasterBand.RasterBand(bbox, resolution=resolution, margin=marge, 
                         novalue=novalue, name=RasterBand.DEFAULT_NAME + '1')
           
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


#    @staticmethod
#    def getAltitude(bbox, proj=None, nomproxy=None):
#        URL_ELEVATION = ''
#        # https://wxs.ign.fr/altimetrie/geoportail/r/wms?LAYERS=ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES&EXCEPTIONS=text/xml&FORMAT=image%2Fgeotiff&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&STYLES=&CRS=EPSG:2154&BBOX=660034.3692562445,6859000.245020923,660169.3953205446,6859140.163403969&WIDTH=2048&HEIGHT=2048
     
    