# -*- coding: utf-8 -*-

import math
import matplotlib.pyplot as plt
import sys

from tracklib.core.Coords import GeoCoords, ENUCoords, ECEFCoords
#from Coords import GeoCoords, ENUCoords, ECEFCoords
from tracklib.core.Network import Edge
from tracklib.core.Track import Track

import tracklib.algo.Geometrics as Geometrics


class SpatialIndex:
    
    def __init__(self, collection, resolution=(100, 100)):
        '''
        Parameters
        ----------
        features : bbox() + iterable
                   
        
            TrackCollection : on construit une grille 
                dont l’emprise est calculée sur la fonction getBBox 
                de TrackCollection et dans un deuxième temps on appelle 
                addSegment([c1,c2], [i,j]) pour chaque segment [c1,c2] 
                (localisé entre les points GPS i et i+1) de chaque trace j, 
                de la collection. 
            Network : on construit une grille (de taille 100 x 100) par défaut, 
                  dont l’emprise est calculée sur celle du réseau, et on appelle 
                  addSegment ([c1,c2], [i,j]) pour chaque segment [c1,c2] 
                  (localisé entre les points GPS i et i+1) de chaque tronçon j, 
                  du réseau.
        

        resolution : tuple (xsize, ysize)
            DESCRIPTION. The default is (100, 100).

        Returns
        -------
        None.

        '''
        
        self.collection = collection
        
        # Nombre de dalle par cote
        self.resolution = resolution
        self.csize = self.resolution[0]
        self.lsize = self.resolution[1]
        # print ('nb cellule', self.xsize * self.ysize)
        
        # Tableau de collections de features appartenant a chaque dalle. 
        # Un feature peut appartenir a plusieurs dalles.
        self.grid = []
        for i in range(self.csize + 1):
            self.grid.append([])
            for j in range(self.lsize + 1):
                self.grid[i].append([])
        
        (self.xmin, self.xmax, self.ymin, self.ymax) = collection.bbox()
        
        self.dX = (self.xmax - self.xmin) / self.csize
        self.dY = (self.ymax - self.ymin) / self.lsize
        #print (self.dX, self.dY)
        
        # Calcul de la grille
        for num in range(collection.size()):
            feature = collection[num]
            # On récupere la trace
            if isinstance(feature, Track):
                self.__addIntersectCells(feature, num)
            # On récupère l'arc du reseau qui est une trace
            elif isinstance(feature, Edge):
                self.__addIntersectCells(feature.track, num)
                


    def __addIntersectCells(self, track, num):
        '''
        '''
        coord1 = None
        for i in range(track.size()):
            obs = track.getObs(i)
            coord2 = obs.position
            if coord1 != None:
                p1 = self.__getCell(coord1)
                p2 = self.__getCell(coord2)
                self.__addSegment(p1, p2, (i-1,num))
            coord1 = coord2

    
    
    def __addSegment(self, coord1, coord2, data):
        '''
        data de type: int, liste, tuple, dictionnaire
        ajoute les données data dans toutes les cellules de la grille 
               traversée par le segment [coord1, coord2] avec
               coord1 : indices de la grille
        '''
        #
        CELLS = self.__cellsCrossSegment(coord1, coord2)
        #print (CELLS)
        
        for cell in CELLS:
            i = cell[0]
            j = cell[1]
            if i > self.csize:
                print ('error, depassement en x')
                exit()
            if j > self.lsize:
                print ('error, depassement en y')
                exit()
                
            if data not in self.grid[i][j]:
                self.grid[i][j].append(data)
                
    
    def __addPoint (self, coord, data):
        pass
    
    
    def __getCell(self, coord):
        '''
            Fonction qui retourne les identifiants de la cellule en indices (i,j)
            de Coord  
        '''
        # (idx, idy) = self.__getCoordGrille(coord)
        X = float(coord.getX()) - self.xmin
        idx = X / self.dX
        
        Y = float(coord.getY()) - self.ymin
        idy = Y / self.dY
        
        if math.floor(idx) < 0 or math.floor(idx) > (self.csize + 1):
            sys.exit ('error, depassement en x')
        if idy < 0 or idy > (self.lsize + 1):
            sys.exit ('error, depassement en y')
        
        #return (math.floor(idx), math.floor(idy))
        return (idx, idy)
    
    
    def plot(self):
        
        fig = plt.figure()
        ax = fig.add_subplot(111, xlim=(0, self.csize), ylim=(0, self.lsize))
        
        for i in range(1,self.csize):
            ax.plot([i,i], [0, self.csize], '-',color='lightgray')
        for j in range(1,self.lsize):
            ax.plot([0, self.lsize], [j,j], '-',color='lightgray')
        
        for j in range(self.collection.size()):
            features = self.collection[j]
            X = features.getX()
            Y = features.getY()
            X1 = []
            Y1 = []
            for i in range(len(X)):
                X1.append((X[i] - self.xmin ) / self.dX)
                Y1.append((Y[i] - self.ymin ) / self.dY)
            #print (Y1)
            ax.plot(X1, Y1, '-', color='forestgreen')
        #ax.plot([x1,x2], [y1,y2], '-')
        
        for i in range(self.csize):
            for j in range(self.lsize):
                # cellule (i,j)

                if len(self.grid[i][j]) > 0:
                    polygon = plt.Polygon(
                        [[i, j], [i+1, j], [i+1, j+1], [i, j+1], [i, j]])
                    ax.add_patch(polygon)
                    polygon.set_facecolor('lightcyan')


    def request(self, obj, j = -1): 
        '''
        retourne toutes les données (sous forme de liste simple) 
        référencées dans ...
        '''
        # print (type(obj))
        if isinstance(obj, int):
            ''' dans la cellule (i,j)  '''
            i = obj
            return self.grid[i][j]
           
        if isinstance(obj, GeoCoords) or isinstance(obj, ENUCoords) or isinstance(obj, ECEFCoords):
            ''' dans la cellule contenant le point coord '''
            coord = obj
            c = self.__getCell(coord)
            return self.request(math.floor(c[0]), math.floor(c[1]))
        
        if isinstance(obj, list):
            ''' dans les cellules traversées par le segment défini
            par des coordonnées géographiques '''
            [coord1, coord2] = obj
            p1 = self.__getCell(coord1)
            p2 = self.__getCell(coord2)
            
            # Les cellules traversées par le segment
            CELLS = self.__cellsCrossSegment(p1, p2)
            TAB = []
            for cell in CELLS:
                self.__addCellValuesInTAB(TAB, cell)
            return TAB
            
        if isinstance(obj, Track):
            ''' dans les cellules traversée par la track '''
            track = obj
            
            # récupération des cellules de la track
            TAB = []
            pos1 = None
            for i in range(track.size()):
                obs = track.getObs(i)
                pos2 = obs.position
                if pos1 != None:
                    coord1 = self.__getCell(pos1)
                    coord2 = self.__getCell(pos2)
                    
                    CELLS = self.__cellsCrossSegment(coord1, coord2)
                    for cell in CELLS:
                        self.__addCellValuesInTAB(TAB, cell)
                pos1 = pos2
                
            return TAB
        
        
    def neighborhood(self, obj, j = -1, unit=0):
        '''
        retourne toutes les données (sous forme de liste simple) référencées 
        dans la cellule (i,j). 
        
        Si unit=-1, calcule la valeur minimale à donner à unit, 
        pour que la liste ne soit pas vide*.  
        '''
        
        if isinstance(obj, int):
        
            i = obj

            if unit > -1:
                NC = self.__neighbouringcells(i, j, unit)
                TAB = []
                for cell in NC:
                    self.__addCellValuesInTAB(TAB, cell)
                #print (TAB)
                return TAB
            
            # Si unit = -1, tant liste ne soit pas vide
            # plus une marge de une unité
            u = 0
            while (u <= max(self.csize, self.lsize)):
                NC = self.__neighbouringcells(i, j, u)
                TAB = []
                for cell in NC:
                    self.__addCellValuesInTAB(TAB, cell)
                
                if len(TAB) <= 0:
                    u += 1
                    continue
                
                # Plus une marge de sécurité
                NC = self.__neighbouringcells(i, j, u+1)
                for cell in NC:
                    self.__addCellValuesInTAB(TAB, cell)
                #print (TAB)                
                return TAB
        
        
        if isinstance(obj, GeoCoords) or isinstance(obj, ENUCoords) or isinstance(obj, ECEFCoords):
            coord = obj
            x = coord.getX()
            y = coord.getY()
            c = self.__getCell(ENUCoords(x, y))
            # print (c)
            return self.neighborhood(math.floor(c[0]), math.floor(c[1]), unit)
           
        
        if isinstance(obj, list):
            ''' cellules voisines traversées par le segment coord '''
            [coord1, coord2] = obj
            p1 = self.__getCell(coord1)
            p2 = self.__getCell(coord2)
            
            if unit > -1:
                # Tableau à retourner
                TAB = []
            
                # Les cellules traversées par le segment
                CELLS = self.__cellsCrossSegment(p1, p2)
                for cell in CELLS:
                    NC = self.__neighbouringcells(cell[0], cell[1], unit)
                    #print ('    ', cell, NC)
                    for cellu in NC:
                        self.__addCellValuesInTAB(TAB, cellu)
                
                return TAB
            
            
            u = 0
            while (u <= max(self.csize, self.lsize)):
                TAB = []
                CELLS = self.__cellsCrossSegment(p1, p2)
                for cell in CELLS:
                    NC = self.__neighbouringcells(cell[0], cell[1], u)
                    #print (cell, NC)
                    for cellu in NC:
                        self.__addCellValuesInTAB(TAB, cellu)
                
                #print (TAB)
                if len(TAB) <= 0:
                    u += 1
                    continue
                
                # Plus une marge de sécurité
                CELLS = self.__cellsCrossSegment(p1, p2)
                for cell in CELLS:
                    NC = self.__neighbouringcells(cell[0], cell[1], u+1)
                    #print (cell, NC)
                    for cellu in NC:
                        self.__addCellValuesInTAB(TAB, cellu)
                #print (TAB)                
                return TAB
            

        if isinstance(obj, Track):
            ''' cellules voisines traversées par Track '''
            
            track = obj
            
            TAB2 = []
            pos1 = None
            for i in range(track.size()):
                obs = track.getObs(i)
                pos2 = obs.position
                
                if pos1 != None:
                    CELLS = self.neighborhood([pos1, pos2], None, unit)
                    #print (CELLS, unit)
                    for cell in CELLS:
                        if cell not in TAB2:
                            TAB2.append(cell)
                pos1 = pos2
                
            return TAB2
            

        
    
    def __neighbouringcells(self, i, j, u=1):
        '''
        Parameters
        ----------
        i : int
            indice de la cellule (i,j).
        j : int
            indice de la cellule (i,j).
        u : TYPE, optional
            DESCRIPTION. The default is 1.

        Returns
        -------
        NC : integer
            neighbouring cells of (i,j) with u unit

        '''
        
        NC = []
        
        #  i = +-u et j = +- 0-->u
        for t in range(-u, u+1):
            candidat1 = (i + u, j + t)
            if (i+u) < self.csize and (i+u) >= 0 and (j+t) < self.lsize and (j+t) >= 0:
                if candidat1 not in NC:
                    NC.append(candidat1)
            candidat2 = (i - u, j + t)
            if (i-u) < self.csize and (i-u) >= 0 and (j+t) < self.lsize and (j+t) >= 0:
                if candidat2 not in NC:
                    NC.append(candidat2)
        
        #  i = +- 0-->u-1 et j = +-u
        for s in range(-u+1, u):
            candidat1 = (i + s, j + u)
            if (i+s) < self.csize and (i+s) >= 0 and (j+u) < self.lsize and (j+u) >= 0:
                if candidat1 not in NC:
                    NC.append(candidat1)
            candidat2 = (i + s, j - u)
            if (i+s) < self.csize and (i+s) >= 0 and (j-u) < self.lsize and (j-u) >= 0:
                if candidat2 not in NC:
                    NC.append(candidat2)
            
        # return neighbouring cells
        # print (NC)
        return NC
        
        
    
    def __addCellValuesInTAB(self, TAB, cell):
        '''
           Add all values of the cell in TAB array.
           Check: 
               if cell is empty 
               if the values of cell are not already in TAB
        '''
        
        values = self.request(cell[0], cell[1])
        if len (values) > 0:
            for d in values:
                if d not in TAB:
                    TAB.append(d)
        

        
    def __cellsCrossSegment(self, coord1, coord2):
        '''
            liste des cellules passent par le segment défini 
            par [coord1, coord2] en pixel
        '''
        CELLS = []
        segment2 = [coord1[0], coord1[1], coord2[0], coord2[1]]
        
        xmin = min (math.floor(coord1[0]), math.floor(coord2[0]))
        xmax = max (math.floor(coord1[0]), math.floor(coord2[0]))
        
        ymin = min (math.floor(coord1[1]), math.floor(coord2[1]))
        ymax = max (math.floor(coord1[1]), math.floor(coord2[1]))
        
        for i in range( xmin,  xmax+1):
            for j in range(ymin, ymax+1):
                
                segment1 = [i, j, i+1, j]
                if Geometrics.isSegmentIntersects(segment1, segment2):
                    CELLS.append((i,j))
                    
                segment1 = [i, j, i, j+1]
                if Geometrics.isSegmentIntersects(segment1, segment2):
                     if (i,j) not in CELLS:
                         CELLS.append((i,j))
                    
                segment1 = [i,j+1,i+1,j+1]
                if Geometrics.isSegmentIntersects(segment1, segment2):
                     if (i,j) not in CELLS:
                         CELLS.append((i,j))
                    
                segment1 = [i+1,j,i+1,j+1]
                if Geometrics.isSegmentIntersects(segment1, segment2):
                    if (i,j) not in CELLS:
                        CELLS.append((i,j))
                
        return CELLS   