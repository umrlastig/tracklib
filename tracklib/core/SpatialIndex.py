# -*- coding: utf-8 -*-
import sys
import math
import pickle
import progressbar
import matplotlib.pyplot as plt

from tracklib.core.Track import Track
from tracklib.core.Network import Edge
from tracklib.core.Coords import GeoCoords, ENUCoords, ECEFCoords

import tracklib.algo.Geometrics as Geometrics


class SpatialIndex:
    
    def __init__(self, collection, resolution=None, margin=0.05, verbose=True):
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
        bb = collection.bbox()
        (self.xmin, self.xmax, self.ymin, self.ymax) = SpatialIndex._addMargin(bb, margin)
        ax = self.xmax-self.xmin
        ay = self.ymax-self.ymin

        if resolution is None:
            am = max(ax, ay)
            r = am/100; resolution = (int(ax/r), int(ay/r))
        else:
            r = resolution; resolution = (int(ax/r), int(ay/r))
   
        self.collection = collection

		# Keeps track of registered features
        self.inventaire = set()

        # Nombre de dalle par cote
        self.resolution = resolution
        self.csize = self.resolution[0]
        self.lsize = self.resolution[1]
        # print ('nb cellule', self.xsize * self.ysize)
        
        # Tableau de collections de features appartenant a chaque dalle. 
        # Un feature peut appartenir a plusieurs dalles.
        self.grid = []
        for i in range(self.csize):
            self.grid.append([])
            for j in range(self.lsize):
                self.grid[i].append([])
        
        self.dX = ax / self.csize
        self.dY = ay / self.lsize
        
        # Calcul de la grille
        boucle = range(collection.size())
        if verbose:
            print("Building ["+str(self.csize)+" x "+str(self.lsize)+"] spatial index...")
            boucle = progressbar.progressbar(boucle)
        for num in boucle:
            feature = collection[num]
            # On récupere la trace
            if isinstance(feature, Track):
                self.__addIntersectCells(feature, num)
            # On récupère l'arc du reseau qui est une trace
            elif isinstance(feature, Edge):
                self.__addIntersectCells(feature.geom, num)

    def _addMargin(bbox, margin):
        (xmin, xmax, ymin, ymax) = bbox
        ax = xmax-xmin
        ay = ymax-ymin
        xmin -= margin*ax
        xmax += margin*ax
        ymin -= margin*ay
        ymax += margin*ay
        return (xmin, xmax, ymin, ymax)

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
        CELLS = self.__cellsCrossSegment(coord1, coord2)
        #print (CELLS, coord1, coord2)

        
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
                if (i,j,data) not in self.inventaire:
                    self.grid[i][j].append(data)
                    self.inventaire.add((i,j,data))
                
    
    def __addPoint (self, coord, data):
        pass
    
    
    # ------------------------------------------------------------
    # Normalized coordinates of coord: (x,) -> (i,j) with:
	#   i = (x-xmin)/(xmax-xmin)*nb_cols
	#   j = (y-ymin)/(ymax-ymin)*nb_rows
    # ------------------------------------------------------------
    def __getCell(self, coord):
	
        if (coord.getX() < self.xmin) or (coord.getX() > self.xmax):
            sys.exit ('Error: x overflow')
        if (coord.getY() < self.ymin) or (coord.getY() > self.ymax):
            sys.exit ('Error: y overflow')

        idx = (float(coord.getX()) - self.xmin) / self.dX
        idy = (float(coord.getY()) - self.ymin) / self.dY
                
        return (idx, idy)
    
    
    # ------------------------------------------------------------
    # Plot spatial index and collection structure together in the 
	# same reference frame (geographic reference frame)
	#   - base: plot support network or track collection if True
    # ------------------------------------------------------------
    def plot(self, base=True):

        fig = plt.figure()
        ax = fig.add_subplot(111, xlim=(self.xmin, self.xmax), ylim=(self.ymin, self.ymax))
        
        for i in range(1,self.csize):
            xi = i*self.dX + self.xmin
            ax.plot([xi,xi], [self.ymin, self.ymax], '-',color='lightgray')
        for j in range(1,self.lsize):
            yj = j*self.dY + self.ymin
            ax.plot([self.xmin, self.xmax], [yj,yj], '-',color='lightgray')
        
        if base:
            self.collection.plot(append=ax)        

        for i in range(self.csize):
            xi1 = i*self.dX + self.xmin; xi2 = xi1 + self.dX
            for j in range(self.lsize):
                yj1 = j*self.dY + self.ymin; yj2 = yj1 + self.dY
                if len(self.grid[i][j]) > 0:
                    polygon = plt.Polygon(
                        [[xi1, yj1], [xi2, yj1], [xi2, yj2], [xi1, yj2], [xi1, yj1]])
                    ax.add_patch(polygon)
                    polygon.set_facecolor('lightcyan')
					
    # ------------------------------------------------------------
    # Plot a specific cell (i,j)
    # ------------------------------------------------------------
    def highlight(self, i, j, sym='r-', size=0.5):
        x0 = self.xmin+i*self.dX; x1 = x0+self.dX
        y0 = self.ymin+j*self.dY; y1 = y0+self.dY
        X = [x0, x1, x1, x0, x0]
        Y = [y0, y0, y1, y1, y0] 
        plt.plot(X, Y, sym, linewidth=size)		

    # ------------------------------------------------------------
    # Request function to get data registered in spatial index
    # Inputs:
	# 	- request(i,j) returns data registered in cell (i,j) 
	#   	- i: row index i of spatial index grid
	#		- j: col index j of spatial index grid
	#   - request(coord) returns data registered in the cell 
	#     containing GeoCoords or ENUCoors object coord
	#   - request(list) returns data registered in all cells 
	#     crossed by a segment list=[coord1, coord2].
	#	- request(track) returns data registered in all cells 
	#     crossed by a track.
    # ------------------------------------------------------------
    def request(self, obj, j=None): 
        '''
        retourne toutes les données (sous forme de liste simple) 
        référencées dans ...
        '''
        # print (type(obj))
        if isinstance(obj, int):
            ''' dans la cellule (i,j)  '''
            i = obj
            return self.grid[i][j]
           
        if isinstance(obj, GeoCoords) or isinstance(obj, ENUCoords):
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
        
    # ------------------------------------------------------------
	# Neighborhood function to get all data registered in spatial 
	# index and located in the vicinity of a given location.
	# ------------------------------------------------------------
	# - neighborhood(i,j,unit) returns all data (as a plain list) 
	#   registered in a cell located at less than 'unit' distance 
	#   from (i,j) cell. 
	# - neighborhood(coord, unit) returns data (as a plain list) 
	#   registered in a cells located at less than 'unit' distance 
	#   from cell containing coord. 
	# - neighborhood([c1, c2], unit) returns data (as a plain 
	#   list) registered in a cells located at less than 'unit' 
	#   distance from cells containing segment [c1, c2]
	# - neighborhood(track, unit) returns data (as a plain list) 
	#   registered in a cells located at less than 'unit' distance 
	#   from cells containing track
	# ------------------------------------------------------------
	# As default value, unit=0, meaning that only data located in 
	# (i,j) cell are selected. If unit=-1, the minimal value is 
	# selected in order to get at least 1 data in function output. 
	# ------------------------------------------------------------
	# The number of cells inspected is given by:
	#    - (1+2*unit)^2 if unit >= 0
	#    - (1+2*(unit'+1))^2 if unit < 0, with unit' is the min 
	#      value of unit such that output is not empty
	# ------------------------------------------------------------

    def neighborhood(self, obj, j=None, unit=0):
        '''
        retourne toutes les données (sous forme de liste simple) référencées 
        dans la cellule (i,j). 
        
        Si unit=-1, calcule la valeur minimale à donner à unit, 
        pour que la liste ne soit pas vide*.  
        '''
        
	    # --------------------------------------------------------	
        # neighborhood(i,j,unit)
	    # --------------------------------------------------------	
        if isinstance(obj, int):
        
            i = obj

            if unit != -1:
                TAB = set()
                NC = self.__neighboringcells(i, j, unit, False)
                for cell in NC:
                    TAB.update(self.request(cell[0], cell[1]))
                return list(TAB)
				
            # -----------------------------------------
            # Case: unit < 0 -> search for unit value
			# -----------------------------------------
            u = 0; TAB = set(); found = False
            while (u <= max(self.csize, self.lsize)):
                NC = self.__neighboringcells(i, j, u, True)
                for cell in NC:
                    TAB.update(self.request(cell[0], cell[1]))
                if found:
                    break
					
                found = (len(TAB) > 0); u += 1
                 
            return list(TAB)
        
        # --------------------------------------------------------	
        # neighborhood(coord, unit)
	    # --------------------------------------------------------	
        if isinstance(obj, GeoCoords) or isinstance(obj, ENUCoords):
            coord = obj
            x = coord.getX()
            y = coord.getY()
            c = self.__getCell(ENUCoords(x, y))
            return self.neighborhood(math.floor(c[0]), math.floor(c[1]), unit)
           
        
		# --------------------------------------------------------	
        # neighborhood([c1, c2], unit)
	    # --------------------------------------------------------	
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
                    NC = self.__neighboringcells(cell[0], cell[1], unit)
                    #print ('    ', cell, NC)
                    for cellu in NC:
                        self.__addCellValuesInTAB(TAB, cellu)
                
                return TAB
            
            
            u = 0
            while (u <= max(self.csize, self.lsize)):
                TAB = []
                CELLS = self.__cellsCrossSegment(p1, p2)
                for cell in CELLS:
                    NC = self.__neighboringcells(cell[0], cell[1], u)
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
                    NC = self.__neighboringcells(cell[0], cell[1], u+1)
                    #print (cell, NC)
                    for cellu in NC:
                        self.__addCellValuesInTAB(TAB, cellu)
                #print (TAB)                
                return TAB
            
		# --------------------------------------------------------	
        # neighborhood(track, unit)
	    # --------------------------------------------------------	
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
    # ------------------------------------------------------------
	# Function to convert ground distance (metric system is 
	# assumed to be orthonormal) into unit number
	# ------------------------------------------------------------        
    def groundDistanceToUnits(self, distance):
        return math.floor(distance/max(self.dX, self.dY)+1)
        
    # ------------------------------------------------------------
	# Returns all cells (i',j') in a vicinity unit of (i,j) 
	# ------------------------------------------------------------
	# - incremental = True: gets all cells where distance is to 
	#   central cell is exactly u units (Manhattan L1 discretized 
	#   distance). Used for incremental search of neighbors.
	# - incremental = False: gets all cells where distance is less 
	#   or equal than u units (Manhattan L1 discretized distance)
	# ------------------------------------------------------------
    def __neighboringcells(self, i, j, u=0, incremental=False):   
        NC = []
        imin = max(i-u, 0); imax = min(i+u+1, self.csize) 
        jmin = max(j-u, 0); jmax = min(j+u+1, self.lsize)
        for ii in range(imin, imax):
            for jj in range(jmin, jmax):	
                if incremental:
                    if (ii != imin) and (ii != imax-1):
                        if (jj != jmin) and (jj != jmax-1):
                            continue
                NC.append((ii,jj))	
        return NC				
    
	# ------------------------------------------------------------
	# Add data registered in cell within TAB structure 
	# ------------------------------------------------------------
    def __addCellValuesInTAB(self, TAB, cell):     
        values = self.request(cell[0], cell[1])
        for d in values:
            if d not in TAB:
                TAB.append(d)
        
	# ------------------------------------------------------------
	# List of cells crossing segment [coord1, coord2] (in px)
	# ------------------------------------------------------------        
    def __cellsCrossSegment(self, coord1, coord2):

        CELLS = []
        segment2 = [coord1[0], coord1[1], coord2[0], coord2[1]]
        
        xmin = min (math.floor(coord1[0]), math.floor(coord2[0]))
        xmax = max (math.floor(coord1[0]), math.floor(coord2[0]))
        
        ymin = min (math.floor(coord1[1]), math.floor(coord2[1]))
        ymax = max (math.floor(coord1[1]), math.floor(coord2[1]))
        
        for i in range( xmin,  xmax+1):
            for j in range(ymin, ymax+1):
                
                # complètement inclus
                if i < coord1[0] and coord1[0] < i+1 and i < coord2[0] and coord2[0] < i+1 and j < coord1[1] and coord1[1] < j+1 and j < coord2[1] and coord2[1] < j+1:
                    if (i,j) not in CELLS:
                        CELLS.append((i,j))
                    continue
                
                # traverse
                segment1 = [i, j, i+1, j]
                if Geometrics.isSegmentIntersects(segment1, segment2):
                    if (i,j) not in CELLS:
                        CELLS.append((i,j))
                    continue
                    
                segment1 = [i, j, i, j+1]
                if Geometrics.isSegmentIntersects(segment1, segment2):
                    if (i,j) not in CELLS:
                        CELLS.append((i,j))
                    continue
                    
                segment1 = [i,j+1,i+1,j+1]
                if Geometrics.isSegmentIntersects(segment1, segment2):
                    if (i,j) not in CELLS:
                        CELLS.append((i,j))
                    continue
                    
                segment1 = [i+1,j,i+1,j+1]
                if Geometrics.isSegmentIntersects(segment1, segment2):
                    if (i,j) not in CELLS:
                        CELLS.append((i,j))
                    continue
                
        return CELLS


    def save(self, filename):
        outfile = open(filename,'wb')
        pickle.dump(self, outfile)
        outfile.close()
    def load(filename):
        infile = open(filename,'rb')
        index = pickle.load(infile)
        infile.close()
        return index