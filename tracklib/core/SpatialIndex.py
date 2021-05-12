# -*- coding: utf-8 -*-

import math
import matplotlib.pyplot as plt

from tracklib.core.Coords import GeoCoords, ENUCoords, ECEFCoords
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
        self.xsize = self.resolution[0] + 0
        self.ysize = self.resolution[1] + 0
        #print ('nb cellule', self.xsize * self.ysize)
        
        # Tableau de collections de features appartenant a chaque dalle. 
        # Un feature peut appartenir a plusieurs dalles.
        self.grid = []
        for i in range(self.xsize+1):
            self.grid.append([])
            for j in range(self.ysize+1):
                self.grid[i].append([])
        
        (self.xmin, self.xmax, self.ymin, self.ymax) = collection.bbox()
        
        self.dX = (self.xmax - self.xmin) / self.xsize
        self.dY = (self.ymax - self.ymin) / self.ysize
        #print (self.dX, self.dY)
        
        # Calcul de la grille
        for num in range(collection.size()):
            features = collection[num]
            # On récupere la trace
            if isinstance(features, Track):
                self.__addIntersectCells(features, num)
            elif isinstance(features, Edge):
                self.__addIntersectCells(features.track, num)
                


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
                #print (p1, p2)
                self.__addSegment(p1, p2, (i-1,num))
            coord1 = coord2

    
    
    def __addSegment(self, coord1, coord2, data):
        '''
        data de type: int, liste, tuple, dictionnaire
        ajoute les données data dans toutes les cellules de la grille 
               traversée par le segment [coord1, coord2] avec
               coord1 : indices de la grille
        '''
        
        segment2 = [coord1[0], coord1[1], coord2[0], coord2[1]]
        
        xmin = min (math.floor(coord1[0]), math.floor(coord2[0]))
        xmax = max (math.floor(coord1[0]), math.floor(coord2[0]))
        
        ymin = min (math.floor(coord1[1]), math.floor(coord2[1]))
        ymax = max (math.floor(coord1[1]), math.floor(coord2[1]))
        
        # On boucle sur les cellules 
        for i in range( xmin,  xmax+1):
             #print (i)
             for j in range(ymin, ymax+1):
                
                 # On boucle sur les 4 bordures        
                 segment1 = [i+0.0, j, i+1, j]
                 if Geometrics.isSegmentIntersects(segment1, segment2):
                     if data not in self.grid[i][j]:
                         self.grid[i][j].append(data)
                    
                 segment1 = [i,j,i,j+1]
                 if Geometrics.isSegmentIntersects(segment1, segment2):
                     if data not in self.grid[i][j]:
                         self.grid[i][j].append(data)
                    
                 segment1 = [i,j+1,i+1,j+1]
                 if Geometrics.isSegmentIntersects(segment1, segment2):
                     if data not in self.grid[i][j]:
                         self.grid[i][j].append(data)
                    
                 segment1 = [i+1,j,i+1,j+1]
                 if Geometrics.isSegmentIntersects(segment1, segment2):
                     if data not in self.grid[i][j]:
                         self.grid[i][j].append(data)
        
       
    
    def __getCoordGrille(self, coord):
        '''
            Fonction qui convertit des coordonnées Coords en indices (i,j), 
        '''
        X = float(coord.getX()) - self.xmin
        idx = X / self.dX
        
        Y = float(coord.getY()) - self.ymin
        idy = Y / self.dY
        
        return (idx, idy)
    
    
    def __getCell(self, coord):
        '''
            Fonction qui convertit des coordonnées Coords en indices (i,j), 
        '''
        (idx, idy) = self.__getCoordGrille(coord)
        return (math.floor(idx), math.floor(idy))
    
    
    
    def __addPoint (self, coord, data):
        
        pass
    
    
    
    def plot(self):
        
        fig = plt.figure()
        ax = fig.add_subplot(111, xlim=(0, self.xsize), ylim=(0, self.ysize))
        
        for i in range(1,self.xsize):
            ax.plot([i,i], [0,self.xsize], '-',color='lightgray')
        for j in range(1,self.ysize):
            ax.plot([0,self.ysize], [j,j], '-',color='lightgray')
        
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
        
        for i in range(self.xsize):
            for j in range(self.ysize):
                # cellule (i,j)

                if len(self.grid[i][j]) > 0:
                    polygon = plt.Polygon(
                        [[i, j], [i+1, j], [i+1, j+1], [i, j+1], [i, j]])
                    ax.add_patch(polygon)
                    polygon.set_facecolor('lightcyan')

                
    def request(self, obj, j = -1) : 
        '''
        retourne toutes les données (sous forme de liste simple) 
        référencées dans ...
        '''
        
        if isinstance(obj, int):
            ''' dans la cellule (i,j)  '''
            i = obj
            return self.grid[i][j]
           
        if isinstance(obj, GeoCoords) or isinstance(obj, ENUCoords) or isinstance(obj, ECEFCoords):
            ''' dans la cellule contenant le point coord '''
            
            coord = obj
            x = coord.getX()
            y = coord.getY()
            c = self.__getCell(ENUCoords(x, y))
            return self.grid[c[0]][c[1]]
        
        elif isinstance(obj, list):
            ''' dans les cellules traversée par le segment coord '''
            [coord1, coord2] = obj
            segment2 = [coord1[0], coord1[1], coord2[0], coord2[1]]
            
            # Les cellules traversées par le segment
            
            xmin = min (math.floor(coord1[0]), math.floor(coord2[0]))
            xmax = max (math.floor(coord1[0]), math.floor(coord2[0]))
        
            ymin = min (math.floor(coord1[1]), math.floor(coord2[1]))
            ymax = max (math.floor(coord1[1]), math.floor(coord2[1]))
        
            TAB = []
            # On boucle sur les cellules 
            for i in range( xmin,  xmax+1):
                #print (i)
                for j in range(ymin, ymax+1):
                    
                    val = self.grid[i][j]
                    
                    # On boucle sur les 4 bordures         
                    segment1 = [i+0.0, j, i+1, j]
                    if Geometrics.isSegmentIntersects(segment1, segment2):
                        for d in val:
                            if d not in TAB:
                                TAB.append(d)
                    
                    segment1 = [i,j,i,j+1]
                    if Geometrics.isSegmentIntersects(segment1, segment2):
                        for d in val:
                            if d not in TAB:
                                TAB.append(d)
                    
                    segment1 = [i,j+1,i+1,j+1]
                    if Geometrics.isSegmentIntersects(segment1, segment2):
                        for d in val:
                            if d not in TAB:
                                TAB.append(d)
                    
                    segment1 = [i+1,j,i+1,j+1]
                    if Geometrics.isSegmentIntersects(segment1, segment2):
                        for d in val:
                            if d not in TAB:
                                TAB.append(d)
                    
            return TAB
        
        elif isinstance(obj, Track):
            ''' dans les cellules traversée par la track '''
            
            # récupération des cellules de la track
            track = obj
            
            TAB = []
            
            pos1 = None
            for i in range(track.size()):
                obs = track.getObs(i)
                pos2 = obs.position
                if pos1 != None:
                    coord1 = self.__getCell(pos1)
                    coord2 = self.__getCell(pos2)
                    #print (p1, p2)
                    #self.__addSegment(p1, p2, (i-1,num))
                    
                    segment2 = [coord1[0], coord1[1], coord2[0], coord2[1]]
        
                    xmin = min (math.floor(coord1[0]), math.floor(coord2[0]))
                    xmax = max (math.floor(coord1[0]), math.floor(coord2[0]))
        
                    ymin = min (math.floor(coord1[1]), math.floor(coord2[1]))
                    ymax = max (math.floor(coord1[1]), math.floor(coord2[1]))
                    
                    
                    # On boucle sur les cellules 
                    for i in range( xmin,  xmax+1):
                        #print (i)
                        for j in range(ymin, ymax+1):
                            
                            val = self.grid[i][j]
                            
                            segment1 = [i+0.0, j, i+1, j]
                            if Geometrics.isSegmentIntersects(segment1, segment2):
                                for d in val:
                                    if d not in TAB:
                                        TAB.append(d)
                                        
                            segment1 = [i,j,i,j+1]
                            if Geometrics.isSegmentIntersects(segment1, segment2):
                                for d in val:
                                    if d not in TAB:
                                        TAB.append(d)
                                        
                            segment1 = [i,j+1,i+1,j+1]
                            if Geometrics.isSegmentIntersects(segment1, segment2):
                                for d in val:
                                    if d not in TAB:
                                        TAB.append(d)
                            
                            segment1 = [i+1,j,i+1,j+1]
                            if Geometrics.isSegmentIntersects(segment1, segment2):
                                for d in val:
                                    if d not in TAB:
                                        TAB.append(d)
                    
                    
                pos1 = pos2
                
            return TAB