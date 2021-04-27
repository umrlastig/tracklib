# -------------------------- Track -------------------------------
# Class to manage GPS tracks
# Points are referenced in geodetic coordinates
# ----------------------------------------------------------------

from tracklib.core import (Coords)

class Node:
    
    def __init__(self, id, coord):
        
        self.id = id
        self.coord = coord
        
        self.entrants = []
        self.sortants = []
        
        # Pour le ppc:
        self.noeudPrecedent = None
        self.distance = -1
        self.arcPrecedent = None
        
        
    def getArcEntrants(self):
        return self.entrants
    
    def getArcSortants(self):
        return self.sortants
    
    def addArcSortant(self, edge):
        self.sortants.append(edge)

    def addArcEntrant(self, edge):
        self.entrants.append(edge)

    def plusCourtChemin(self, arrivee):
        '''
        Plus court chemin de this vers arrivée, en tenant compte du sens de circulation. 
        Le pcc s'appuie sur l'attribut 'poids' des arcs, qui doit être rempli auparavant.
        '''
        PPC = []
        
        if self == arrivee:
            PPC.add(self)
            return PPC
        
        self.distance = 0
        
        self.__chercheArcsNoeudsVoisins()
    
    
    def __chercheArcsNoeudsVoisins(self):
        '''
            
        '''
        noeudsVoisins = []
        distancesVoisins = []
        arcsVoisins = []
        
        arcsEntrants = self.getArcEntrants()
        arcsSortants = self.getArcSortants()
        
        # transformation du sens géométrique au sens de circulation
        for arc in arcsEntrants:
            if arc.getOrientation() == -1 or arc.getOrientation() == 2:
                if arc.getNoeudIni() != None:
                    arcsVoisins.append(arc)
                    noeudsVoisins.append(arc.getNoeudIni())
                    distancesVoisins.append(arc.getPoids())
        for arc in arcsSortants:
            if arc.getOrientation() == 1 or arc.getOrientation() == 2:
                if arc.getNoeudFin() != None:
                    arcsVoisins.append(arc)
                    noeudsVoisins.append(arc.getNoeudFin())
                    distancesVoisins.append(arc.getPoids())
        
    
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        if self.id == other.id:
            return True
        return False
        
        

class Edge:
    
    '''
    Sens de l'attribut du troncon et pas celui de la géométrie
    '''
    DOUBLE_SENS  = 0
    SENS_DIRECT  = 1
    SENS_INVERSE = -1
    
    def __init__(self, id, track):
        
        self.id = id
        self.track = track
        
        self.noeudIni = None
        self.noeudFin = None
        self.orientation = 0
        self.poids = 0
        
    def getNoeudIni(self):
        return self.noeudIni
    
    def setNoeudIni(self, noeud):
        
        if self.noeudIni != None:
            self.noeudIni.getArcSortants().remove(self);
    
        if noeud != None:
            self.noeudIni = noeud
      
        if self not in noeud.getArcSortants():
            noeud.addArcSortant(self)
        else:
            self.noeudIni = None
    
    def getNoeudFin(self):
        return self.noeudFin
    
    def setNoeudFin(self, noeud):
        #self.noeudFin = noeudFin
        
        if self.noeudFin != None:
            self.getNoeudFin().getArcEntrants().remove(self)
    
        if noeud != None:
            self.noeudFin = noeud
      
        if self not in noeud.getArcEntrants():
            noeud.addArcEntrant(self)
        else:
            self.noeudFin = None
    
      
        
    def setOrientation(self, orientation):
        self.orientation = orientation
    def getOrientation(self):
        return self.orientation
        
    def setPoids(self, poids):
        self.poids = poids
    def getPoids(self):
        return self.poids
        
    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        if self.id == other.id:
            return True
        return False


class Network:

    def __init__(self):
        '''
        '''
        self.EDGES = []
        self.NODES = []


    def addEdge(self, edge):
        self.EDGES.append(edge)
        
    def addNode(self, node):
        self.NODES.append(node)

    def getNode(self, id):
        for node in self.NODES:
            if node.id == id:
                return node
        return None


#if __name__ == '__main__':
#    n1 = Node()
#    n = Network()