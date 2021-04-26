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
#from skimage import io
#from PIL import Image

import tracklib.core.Utils as utils


class Cell:
    '''
    '''
    
    def __init__(self, line_pos, col_pos, af_names, cles):
        
        self.line_pos = line_pos
        self.col_pos = col_pos
        
        # List of values of each observations for algo_names (speed, stop)
        self.vals = {} 
        for name in af_names:
            self.vals[name] = []
            
        # Dictionary for an af value is the aggregate
        self.af_agg = {} #
        for cle in cles:
            self.af_agg[cle] = Grid.NO_DATA_VALUE
        
        
        
    def compute(self, cle, aggregate):
        
        tabnames = cle.split('#')
        tarray = self.vals[tabnames[0]]
        sumval = aggregate(tarray)
        self.af_agg[cle] = sumval
                
        
        



class Grid:
    """ 
        Une grille est définie par son coin inférieur droit, 
        sa taille et la taille des cellules.
        Elle contient des SummarizeTable (tableau des valeurs et )
     """
    
    NO_DATA_VALUE = 0  #-99999.00
    
    
    def __init__(self, Xmin, Ymin, Xmax, Ymax, XPixelSize, YPixelSize = None):
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
        
        self.XSize = Xmax - Xmin
        self.YSize = Ymax - Ymin
        
        self.XOrigin = Xmin 
        self.YOrigin = Ymin + self.YSize
        
        self.XPixelSize = XPixelSize
        if YPixelSize == None:
            self.YPixelSize = XPixelSize
        else:
            self.YPixelSize = YPixelSize
        
        # 
        self.ncol = math.ceil(self.XSize / self.XPixelSize)
        self.nrow = math.ceil(self.YSize / self.YPixelSize)
        
        self.color1 = (0,0,0)
        self.color2 = (255,255,255)
        
        
    def setColor(self, c1, c2):
        self.color1 = c1
        self.color2 = c2
    
    
    def addAnalyticalFunctionForSummarize(self, collection, af_algos, aggregates):

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
        
        # ---------------------------------------------------------------------
        # Tableau des noms
        self.af_names = [] # Utile pour stocker une seule fois l'af
        self.__summarizeFields = {}  # cle nom_algo#nom_agg
        
        for idx, af_algo in enumerate(af_algos):
            aggregate = aggregates[idx]
            name = af_algo.__name__
            cle = af_algo.__name__ + '#' + aggregate.__name__
            
            if name not in self.af_names:
                self.af_names.append(name)
            if cle not in self.__summarizeFields.keys():
                self.__summarizeFields[cle] = aggregate
        
        # ---------------------------------------------------------------------        
        #  On construit des cellules vides
        self.tabcel = []
        for i in range(self.nrow):
            self.tabcel.append([])
            for j in range(self.ncol):
                self.tabcel[i].append(Cell(i, j, self.af_names, self.__summarizeFields.keys()))
        
        # ---------------------------------------------------------------------
        #  On ajoute les valeurs des af dans les cellules
        for af_algo in af_algos:
            self.__addAFValueInCell(collection, af_algo)

        # On calcule les agregats            
        for cle in self.__summarizeFields.keys():
            self.__summarize(cle, self.__summarizeFields[cle])
              

                    
            
    def __addAFValueInCell(self, collection, af_algo):
        ''' 
        On dispatch les valeurs de l'AF dans les cellules.
        Avant on vérifie si l'AF existe, sinon on la calcule.
        '''
        
        af_name = af_algo.__name__
        
        for trace in collection.getTracks():
            
            # On calcule l'AF si ce n'est pas fait
            trace.addAnalyticalFeature(af_algo)
            
            # On eparpille dans les cellules
            for i in range(trace.size()):
                obs = trace.getObs(i)
                
                # On cherche la cellule de la grille ou est le point
                X = float(obs.position.getX()) - self.XOrigin
                column = math.floor(X / self.XPixelSize)
                
                #Y = float(obs.position.getY()) - self.YOrigin
                Y = self.YOrigin - float(obs.position.getY())
                line = math.floor(Y / self.YPixelSize)

                if (0 <= column and column < self.ncol and 0 <= line and line < self.nrow):

                    val = trace.getObsAnalyticalFeature(af_name, i)
                    self.tabcel[line][column].vals[af_name].append(val)
##                else:
##                    print ("Warning: position outer of zone. " \
##                       + "Row: [0, " + str(line) + ', ' + str(self.nrow) + '], ' \
##                       + "Column: [0, " + str(column) + ', ' + str(self.ncol) + ']' + str(obs.position))
##    
                    
                    
    def __summarize(self, cle, aggregate):
       for i in range(self.nrow):
           for j in range(self.ncol):
                cell = self.tabcel[i][j]
                cell.compute(cle, aggregate)
                
                
    
    def __buildArray__(self, af_algo, aggregate, valmax = None, startpixel = 0):
        
        name = af_algo.__name__ + '#' + aggregate.__name__
        
        sumPlot = np.zeros((self.nrow, self.ncol, len(self.__summarizeFields)), dtype='uint8')    
        for i in range(self.nrow):
            for j in range(self.ncol):
                val = self.tabcel[i][j].af_agg[name]
                if utils.isnan(val):
                    val = 0
                elif valmax != None and val > valmax:
                    val = startpixel
                else:
                    if valmax != None:
                        val = int(startpixel + (255 - startpixel) * (valmax - val) / valmax)

                sumPlot[i][j][0] = val
    
        return sumPlot
    
    
    def plot (self, af_algo, aggregate, valmax = None, startpixel = 0):
        
        name = af_algo.__name__ + '#' + aggregate.__name__
        
        sumPlot = self.__buildArray__(af_algo, aggregate, valmax, startpixel)
        
        cmap = utils.getOffsetColorMap(self.color1, self.color2, startpixel / 255)
        plt.imshow(sumPlot[:,:,0], cmap=cmap)
        plt.title(name)
        plt.colorbar()
        plt.show()
        
        
        
    
    def saveGrid(self, filename, af_algo, aggregate, valmax = None, startpixel = 0):
        
        sumPlot = self.__buildArray__(af_algo, aggregate, valmax, startpixel)
        io.imsave(filename, sumPlot)
        
        
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
        

    def exportToAsc(self, path, af, aggregate):
        
        name = af.__name__ + '#' + aggregate.__name__
        filepath = path + name + "_" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".asc"

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
        
        
        
        