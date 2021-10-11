"""
This module contains the class to manipulate rasters
"""

import math
import matplotlib.pyplot as plt
import numpy as np

from skimage import io

import tracklib.core.Utils as utils

class Raster:
    
    NO_DATA_VALUE = -99999.00
    
    def __init__(self, grid, af_algos, aggregates, verbose = True):
        '''
        Example :
            af_algos = [algo.speed, algo.speed]
            cell_operators = [celloperator.co_avg, celloperator.co_max]
        '''

        if not isinstance(af_algos, list):
            af_algos = [af_algos]
        if not isinstance(aggregates, list):
            aggregates = [aggregates]
    
        if len(af_algos) == 0:
            print("Error: af_algos is empty")
            return 0
            
        if len(af_algos) != len(aggregates):
            print("Error: af_names and aggregates must have the same number elements")
            return 0
        
        self.color1 = (0,0,0)
        self.color2 = (255,255,255)
            
        # ---------------------------------------------------------------------
        # Tableau des noms
        self.af_names = [] # Utile pour stocker une seule fois l'af
        self.summarizeFields = {}  # cle nom_algo#nom_agg
            
        for idx, af_algo in enumerate(af_algos):
                
            aggregate = aggregates[idx]
                
            if isinstance(af_algo, str):
                name = af_algo
            else:
                name = af_algo.__name__
                    
            cle = name + '#' + aggregate.__name__
                
            if name not in self.af_names:
                self.af_names.append(name)
            if cle not in self.summarizeFields.keys():
                self.summarizeFields[cle] = aggregate
            
        # ---------------------------------------------------------------------        
        #  On construit des cellules vides
       
        for i in range(grid.ncol):
            for j in range(grid.nrow):
                grid.grid[i][j] = {}
                for name in self.af_names:
                    grid.grid[i][j][name] = []
        
        self.bands = {}
        for cle in self.summarizeFields:
            self.bands[cle] = []
            for i in range(grid.nrow):
                self.bands[cle].append([])
                for j in range(grid.ncol):
                    self.bands[cle][i].append(Raster.NO_DATA_VALUE)
        
        # ---------------------------------------------------------------------
        #  On ajoute les valeurs des af dans les cellules
        for af_algo in af_algos:
            ''' 
            On dispatch les valeurs de l'AF dans les cellules.
            Avant on vérifie si l'AF existe, sinon on la calcule.
            '''
            if not isinstance(af_algo, str):
                af_name = af_algo.__name__
            else:
                af_name = af_algo

            for trace in grid.collection.getTracks():
                
                if not isinstance(af_algo, str):
                    # On calcule l'AF si ce n'est pas fait
                    trace.addAnalyticalFeature(af_algo)
                
                # On eparpille dans les cellules
                for i in range(trace.size()):
                    obs = trace.getObs(i)
                    
                    (idx, idy) = grid.getCell(obs.position)
                    column = math.floor(idx)
                    line = math.floor(idy)
                    # print (column, line)
    
                    if (0 <= column and column < grid.ncol and 0 <= line and line < grid.nrow):
    
                        if not isinstance(af_algo, str):
                            val = trace.getObsAnalyticalFeature(af_name, i)
                        elif af_algo != "uid":
                            val = trace.getObsAnalyticalFeature(af_algo, i)
                        else:
                            val = trace.uid
                            # val = int(startpixel + (255 - startpixel) * (valmax - val) / valmax)
                        
                        grid.grid[column][line][af_name].append(val)

        # On calcule les agregats            
        for cle in self.summarizeFields.keys():
            for i in range(grid.nrow):
                for j in range(grid.ncol):
                    ii = grid.nrow-1-i
                    tabnames = cle.split('#')
                    tarray = grid.grid[j][i][tabnames[0]]
                    sumval = aggregate(tarray)
                    if utils.isnan(sumval):
                        self.bands[cle][ii][j] = 0
                    # elif valmax != None and val > valmax:
                    else:
                        self.bands[cle][ii][j] = sumval
                        
    
    def setColor(self, c1, c2):
        self.color1 = c1
        self.color2 = c2
        
        
    def getRasterBand(self, af_algo, aggregate):
        if af_algo != 'uid':
            cle = af_algo.__name__ + '#' + aggregate.__name__
        else:
            cle = 'uid' + '#' + aggregate.__name__
        return self.bands[cle]

    
    def plot(self, af_algo, aggregate, valmax = None, startpixel = 0):
        if af_algo != 'uid':
            cle = af_algo.__name__ + '#' + aggregate.__name__
        else:
            cle = 'uid' + '#' + aggregate.__name__
            
        tab = np.array(self.bands[cle])
            
        cmap = utils.getOffsetColorMap(self.color1, self.color2, 0)
        plt.imshow(tab, cmap=cmap)
        plt.title(cle)
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
        
        
