"""
This module contains the class to manipulate rasters
"""

# For type annotation
from __future__ import annotations   
from typing import Union

import matplotlib.pyplot as plt
import numpy as np

#from skimage import io

import tracklib.core.Utils as utils
import tracklib.core.Grid as grid

class Raster:
    '''
    '''
    
    def __init__(self, grids: Union[grid.Grid, list], verbose=True):
        """
        On crée un raster avec une ou plusieurs grilles géographiques 
        déjà chargées avec les données.
        """
        
        grids = utils.listify(grids)
        
        self.bands = {}
        for itergrid in grids:
            self.bands[itergrid.name] = itergrid

        self.color1 = (0, 0, 0)
        self.color2 = (255, 255, 255)


    def setColor(self, c1, c2):
        """TODO"""
        self.color1 = c1
        self.color2 = c2
        
        
    def getCle(self, af_algo: Union[int, str], aggregate = None):
        """TODO"""
        
        if af_algo != "uid":
            if isinstance(af_algo, str):
                cle = af_algo + "#" + aggregate.__name__
            else:
                cle = af_algo.__name__ + "#" + aggregate.__name__
        else:
            cle = "uid" + "#" + aggregate.__name__
            
        return cle


    def getRasterBand(self, af_algo: Union[int, str], aggregate = None):
        """TODO"""
        
        if isinstance(af_algo, int):
            return self.bands[grid.DEFAULT_NAME + str(af_algo)]
        
        cle = self.getCle(af_algo, aggregate)
        return self.bands[cle]

    
    def plot(self, af_algo, aggregate, valmax=None, startpixel=0, no_data_values = None):
        """TODO"""
        
        tab = np.array(self.getRasterBand(af_algo, aggregate).grid)
        
        if no_data_values != None:
            tab[tab == grid.NO_DATA_VALUE] = no_data_values

        cmap = utils.getOffsetColorMap(self.color1, self.color2, 0)
        plt.imshow(tab, cmap=cmap)
        plt.title(self.getCle(af_algo, aggregate))
        plt.colorbar()
        plt.show()


# #    def boxplot(self, af_algo, aggregate):
# #        name = af_algo.__name__ + '#' + aggregate.__name__
# #        k = self.__summarizeFieldDico[name]
# #
# #        sumPlot = np.zeros((self.nrow, self.ncol, len(self.__summarizeFieldDico)), dtype='float')
# #        for i in range(self.nrow):
# #            for j in range(self.ncol):
# #                val = self.sum[i][j][k]
# #                if utils.isnan(val):
# #                    val = 0
# #                sumPlot[i][j][k] = val
# #
# #        sumPlot = self.__getSumArray(af_algo, aggregate)
# #
# #        plt.boxplot(sumPlot[:,:,k], vert=False)


# #    def plotImage3AF(self, afs_algo, aggs):
# #        w, h = self.ncol, self.nrow
# #        t = (h, w, 3)
# #        A = np.zeros(t, dtype=np.uint8)
# #
# #        maxs = []
# #        #maxs.append(utils.co_max()
# #        #        self.track.operate(Operator.Operator.MAX, afs_algo[0]))
# #
# #        for i in range(h):
# #            for j in range(w):
# #                rgb = [100, 155, 3]
# #                for k in range(len(afs_algo)):
# #                    af_algo = afs_algo[k]
# #                    aggregate = aggs[k]
# #
# #                    name = af_algo.__name__ + '#' + aggregate.__name__
# #                    ind = self.__summarizeFieldDico[name]
# #
# #                    val = self.sum[i][j][ind]
# #                    if utils.isnan(val):
# #                        val = 0
# #
# #                A[i,j] = rgb
# #
# #        #i = Image.fromarray(A, "RGB")
# #        # im = Image.new(mode = "RGB", size = (200, 200) )
# #        im = Image.fromarray(A)
# #        im.show()


#      def saveGrid(self, filename, af_algo, aggregate, valmax = None, startpixel = 0):

#         sumPlot = self.buildArray(af_algo, aggregate, valmax, startpixel)
#         io.imsave(filename, sumPlot)
