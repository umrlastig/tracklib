#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -------------------------- Grid -------------------------------
#   Matrice à 2 dimensions
#     Opérations avec ....
#
# ----------------------------------------------------------------
from datetime import datetime
import math
import matplotlib.pyplot as plt
import numpy as np
from skimage import io
#from PIL import Image



import tracklib.core.core_utils as utils


class Grid:
    """ 
        Une grille est définie par son coin inférieur droit, 
        sa taille et la taille des cellules.
        Elle contient des SummarizeTable (tableau des valeurs et )
     """
    
    NO_DATA_VALUE = 0  #-99999.00
    
    
    def __init__(self, XOrigin, YOrigin, XSize, YSize, XPixelSize, YPixelSize = None):
        '''
        Grid constructor. 
        The origin is the lower-left corner of the grid.
        
        :param XOrigin: the first coordinate of the origin
        :param YOrigin: the second coordinate of the origin
        :param XSize: raster width
        :param YSize: raster height
        :param XPixelSize: 
        
        :type XOrigin: double
        :type YOrigin: double
        '''
        
        self.XOrigin = XOrigin 
        self.YOrigin = YOrigin
        self.XSize = XSize
        self.YSize = YSize
        self.XPixelSize = XPixelSize
        if YPixelSize == None:
            self.YPixelSize = XPixelSize
        else:
            self.YPixelSize = YPixelSize
        
        # 
        self.ncol = int(self.XSize / self.XPixelSize) + 1
        self.nrow = int(self.YSize / self.YPixelSize) + 1
        
        # les aggrégats
        self.__summarizeFieldDico = {}
        
        # Pour stocker les valeurs des AF
        self.tabval = [[[] for j in range(self.ncol)] for i in range(self.nrow)]
        
        # On initialise plus tard les agrégats    
        self.sum = np.empty((0, 0, 0))
        
        self.color1 = (0,0,0)
        self.color2 = (255,255,255)
        
        
    def setColor(self, c1, c2):
        self.color1 = c1
        self.color2 = c2
    
    
    def addAnalyticalFunctionForSummarize(self, collection, af_algos, aggregates):
       
        if len(af_algos) == 0:
            print("Error: af_algos is empty")
            return 0
        
        if len(af_algos) != len(aggregates):
            print("Error: af_names and aggregates must have the same number elements")
            return 0
        
        for idx, af_algo in enumerate(af_algos):
            aggregate = aggregates[idx]
            name = af_algo.__name__ + '#' + aggregate.__name__

            if name not in self.__summarizeFieldDico:
                idAF = len(self.__summarizeFieldDico)
                self.__summarizeFieldDico[name] = idAF
                
            if idx > 50:
                break
        
        n = len(self.__summarizeFieldDico)
        
        # Les valeurs agrégées
        self.sum = np.zeros((self.nrow, self.ncol, n), dtype='float')    
        
        self.tabval = [[[[] for k in range(n)] for j in range(self.ncol)] for i in range(self.nrow)]
        
        
        for idx, af_algo in enumerate(af_algos):
            aggregate = aggregates[idx]
            name = af_algo.__name__ + '#' + aggregate.__name__
            k = self.__summarizeFieldDico[name]
                
            # On saupoudre l'AF dans les cellules
            self.__addAFValueInCell(collection, af_algo, k)
                    
            # On summarize
            self.__summarize(af_algo, aggregate)
            
            if idx > 50:
                break
                    
            
    def __addAFValueInCell(self, collection, af_algo, k):
        ''' 
        On dispatch les valeurs de l'AF dans les cellules.
        Avant on vérifie si l'AF existe, sinon on la calcule
        '''
        
        # On calcule l'AF si ce n'est pas fait
        collection.addAnalyticalFeature(af_algo)
        
        for trace in collection.getTracks():
            
            # On eparpille dans les cellules
            for i in range(trace.size()):
                obs = trace.getObs(i)
                
                # On cherche la cellule de la grille ou est le point
                X = float(obs.position.getX()) - self.XOrigin
                column = math.floor(X / self.XPixelSize)
                
                Y = float(obs.position.getY()) - self.YOrigin
                line = math.floor(Y / self.YPixelSize)
                
                if (column >= 0 and column < self.ncol and line >= 0 and line < self.nrow):
                    val = trace.getObsAnalyticalFeature(af_algo.__name__, i)
                    self.tabval[line][column][k].append(val)
#                else:
#                    print ("Warning: position outer of zone. " \
#                       + "Row: [0, " + str(line) + ', ' + str(self.nrow) + '], ' \
#                       + "Column: [0, " + str(column) + ', ' + str(self.ncol) + ']' + str(obs.position))
#    
    def __summarize(self, af_algo, aggregate):
        '''
        Le tableau est inversé en i: le zero est en haut à gauche.
        '''
        name = af_algo.__name__ + '#' + aggregate.__name__
        k = self.__summarizeFieldDico[name]
        
        for i in range(self.nrow):
            for j in range(self.ncol):
                tarray = self.tabval[i][j][k]
                sumval = aggregate(tarray)
                if ((self.nrow-1 - i) == 1270 and j == 1188):
                    print (tarray, sumval)
                if ((self.nrow-1 - i) == 1270 and j == 1234):
                    print (tarray, sumval)
                
                self.sum[self.nrow-1 - i][j][k] = sumval
                
    
    
    def plot (self, af_algo, aggregate, valmax = None, startpixel = 0):
        
        name = af_algo.__name__ + '#' + aggregate.__name__
        k = self.__summarizeFieldDico[name]
        
        sumPlot = np.zeros((self.nrow, self.ncol, len(self.__summarizeFieldDico)), dtype='uint8')    
        for i in range(self.nrow):
            for j in range(self.ncol):
                val = self.sum[i][j][k]
                if utils.isnan(val):
                    val = 0
                elif valmax != None and val > valmax:
                    val = startpixel
                else:
                    if valmax != None:
                        val = int(startpixel + (255 - startpixel) * (valmax - val) / valmax)
                        #print (i,j,val)

                    
                sumPlot[i][j][k] = val
        
        # plt.figure(figsize = (25, 8))
        #my_dpi = 96
        #fig = plt.figure(figsize=(1629/my_dpi, 1309/my_dpi), dpi=my_dpi)
        
        cmap = utils.getOffsetColorMap(self.color1, self.color2, startpixel / 255)
        plt.imshow(sumPlot[:,:,k], cmap=cmap)
        plt.title(name)
        plt.colorbar()
        plt.show()
        
        #fig.savefig('/home/marie-dominique/DEV/WORKSPACE/python/tracklib/mitaka/4mmpx_output/descriptors/image1.png', dpi=my_dpi)
        io.imsave('/home/marie-dominique/DEV/WORKSPACE/python/tracklib/mitaka/4mmpx_output/test/image1.png', sumPlot)
        
        
#    def boxplot(self, af_algo, aggregate):
#        name = af_algo.__name__ + '#' + aggregate.__name__
#        k = self.__summarizeFieldDico[name]
#        
#        sumPlot = np.zeros((self.nrow, self.ncol, len(self.__summarizeFieldDico)), dtype='float')    
#        for i in range(self.nrow):
#            for j in range(self.ncol):
#                val = self.sum[i][j][k]
#                if utils.isnan(val):
#                    val = 0
#                sumPlot[i][j][k] = val
#        
#        sumPlot = self.__getSumArray(af_algo, aggregate)
#        
#        plt.boxplot(sumPlot[:,:,k], vert=False)
        

#    def exportToAsc(self, path, af, aggregate):
#        
#        name = af.__name__ + '#' + aggregate.__name__
#        filepath = path + name + "_" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".asc"
#
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
    
    


        
        
#    def plotImage3AF(self, afs_algo, aggs):
#        w, h = self.ncol, self.nrow
#        t = (h, w, 3)
#        A = np.zeros(t, dtype=np.uint8)
#        
#        maxs = []
#        #maxs.append(utils.co_max()
#        #        self.track.operate(Operator.Operator.MAX, afs_algo[0]))
#        
#        for i in range(h):
#            for j in range(w):
#                rgb = [100, 155, 3]
#                for k in range(len(afs_algo)):
#                    af_algo = afs_algo[k]
#                    aggregate = aggs[k]
#                    
#                    name = af_algo.__name__ + '#' + aggregate.__name__
#                    ind = self.__summarizeFieldDico[name]
#                    
#                    val = self.sum[i][j][ind]
#                    if utils.isnan(val):
#                        val = 0
#                 
#                A[i,j] = rgb
#        
#        #i = Image.fromarray(A, "RGB")
#        # im = Image.new(mode = "RGB", size = (200, 200) )
#        im = Image.fromarray(A)
#        im.show()
        
        
        
        