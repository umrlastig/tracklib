"""
Write Grid to Ascii Raster file (\\*.asc).


The header data includes the following keywords and values:

    - ncols : number of columns in the data set.
    - nrows : number of rows in the data set.
    - xllcenter or xllcorner – x-coordinate of the center or lower-left corner of 
      he lower-left cell.
    - yllcenter or yllcorner – y-coordinate of the center or lower-left corner of 
      the lower-left cell.
    - cellsize – cell size for the data set.
    - nodata_value – value in the file assigned to cells whose value is unknown. 
      This keyword and value is optional. The nodata_value defaults to -9999.

"""

import math
from tracklib.core.Raster import NO_DATA_VALUE

class RasterWriter:
    
    @staticmethod
    def writeToFile(path, grid, name, no_data_values = None):
        """Write to Ascii File

        :param path: File path
        :param grid: TODO
        :param af: TODO
        :param aggregate: TODO
        """
        filepath = path + name 
        #filepath += "_" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") 
        filepath += ".asc"

        ascContent = 'ncols\t\t' + str(grid.ncol) + '\n'
        ascContent = ascContent + 'nrows\t\t' + str(grid.nrow) + '\n'
        ascContent = ascContent + 'xllcorner\t' + str(grid.xmin) + '\n'
        ascContent = ascContent + 'yllcorner\t' + str(grid.ymin) + '\n'
        ascContent = ascContent + 'cellsize\t' + str(math.floor(grid.XPixelSize)) + '\n'
        ascContent = ascContent + 'NODATA_value\t' + str(NO_DATA_VALUE) + '\n'
        
        if no_data_values != None:
            grid.grid[grid.grid == grid.NO_DATA_VALUE] = no_data_values

        for i in range(grid.nrow):
            for j in range(grid.ncol):
                if j > 0:
                    ascContent = ascContent + '\t'
                val = grid.grid[i][j]
                ascContent = ascContent + str(val)
            ascContent = ascContent + '\n'

        try:
            f = open(filepath, "w")
            f.write(ascContent)
            f.close()
        except:
            raise Warning("Error when trying to write in raster file")



