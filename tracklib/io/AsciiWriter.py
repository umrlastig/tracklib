# -*- coding: utf-8 -*-
"""
Write Grid to Ascii Raster file (*.asc).


The header data includes the following keywords and values:

    - ncols : number of columns in the data set.
    - nrows : number of rows in the data set.
    - xllcenter or xllcorner – x-coordinate of the center or lower-left corner of the lower-left cell.
    - yllcenter or yllcorner – y-coordinate of the center or lower-left corner of the lower-left cell.
    - cellsize – cell size for the data set.
    - nodata_value – value in the file assigned to cells whose value is unknown. This keyword and value is optional. The nodata_value defaults to -9999.

"""

from datetime import datetime


class AsciiWriter:
    @staticmethod
    def writeToFile(path, grid, af, aggregate):
        """Write to Ascii File

        :param path: File path
        :param grid: TODO
        :param af: TODO
        :param aggregate: TODO
        """
        name = af.__name__ + "#" + aggregate.__name__
        filepath = (
            path + name + "_" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".asc"
        )

        #        k = self.__summarizeFieldDico[name]


#
#        ascContent = 'ncols\t\t' + str(self.ncol) + '\n'
#        ascContent = ascContent + 'nrows\t\t' + str(self.nrow) + '\n'
#        ascContent = ascContent + 'xllcorner\t' + str(self.XOrigin) + '\n'
#        ascContent = ascContent + 'yllcorner\t' + str(self.YOrigin) + '\n'
#        ascContent = ascContent + 'cellsize\t' + str(self.XPixelSize) + '\n'
#        ascContent = ascContent + 'NODATA_value\t' + str(Grid.NO_DATA_VALUE) + '\n'
#
#        for i in range(self.nrow):
#            for j in range(self.ncol):
#                if j > 0:
#                    ascContent = ascContent + '\t'
#                val = self.sum[i][j][k]
#                if utils.isnan(val):
#                    val = Grid.NO_DATA_VALUE
#                ascContent = ascContent + str(val)
#            ascContent = ascContent + '\n'
#
#        try:
#            f = open(filepath, "a")
#            f.write(ascContent)
#            f.close()
#        except:
#            raise Warning("impossible d'écrire le fichier asc")


# f = open(path, "w")
# f.write(FileWriter.__printInOrder(x,y,z,t,O,fmt.separator) + "\n")
# f.close()
