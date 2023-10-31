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
"""

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
from tracklib.core import NO_DATA_VALUE

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



