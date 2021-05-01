# -------------------------- Network ------------------------------------------
# Class to manage Network
# 
# -----------------------------------------------------------------------------

#from tracklib.core import (Coords)

# =============================================================================
#
#
class Node:
    
    def __init__(self, id, coord):
        
        self.id = id
        self.coord = coord
        
        self.entrants = []
        self.sortants = []
        
        # Pour le ppc:
        self.__noeudPrecedent = None
        self.__distance = -1
        self.__arcPrecedent = None
        
    def getDistance(self):
        return self.__distance
        
    def getArcsEntrants(self):
        return self.entrants
    
    def getArcsSortants(self):
        return self.sortants
    
    def addArcSortant(self, edge):
        self.sortants.append(edge)

    def addArcEntrant(self, edge):
        self.entrants.append(edge)

    def plusCourtChemin(self, arrivee):
        '''
        Plus court chemin de self vers arrivée, en tenant compte du sens de circulation. 
        Le pcc s'appuie sur l'attribut 'poids' des arcs, qui doit être rempli auparavant.
        '''
        PPC = []
        
        if self == arrivee:
            PPC.add(self)
            return PPC
        
        self.__distance = 0
        
        (arcsVoisins, noeudsVoisins, distancesVoisins) = self.__chercheArcsNoeudsVoisins()
    
        noeudsTraites = []
        noeudsATraiter = []
        
        for i in range(len(noeudsVoisins)):
            noeudVoisin = noeudsVoisins[i]
            arcVoisin = arcsVoisins[i]
            dist = float(distancesVoisins[i])
            noeudVoisin.__distance = dist
            noeudVoisin.__arcPrecedent = arcVoisin
            noeudVoisin.__noeudPrecedent = self
      
        noeudsATraiter += noeudsVoisins
        
        # Phase "avant"
        while len(noeudsATraiter) > 0:
            # on choisit le noeud à marquer comme traité parmi les voisins
            plusProche = noeudsATraiter[0]
            for i in range(1, len(noeudsATraiter)):
                if noeudsATraiter[i].__distance < plusProche.__distance:
                    plusProche = noeudsATraiter[i]

            noeudsTraites.append(plusProche)
            noeudsATraiter.remove(plusProche)
            
            # Il s'agit du noeud d'arrivée
            if plusProche == arrivee:
                # Arrivé !!!
                break
        
            (arcsVoisins, noeudsVoisins, distancesVoisins) = plusProche.__chercheArcsNoeudsVoisins()
        
            for i in range(len(noeudsVoisins)):
                noeudVoisin = noeudsVoisins[i]
                arcVoisin = arcsVoisins[i]
                dist = float(distancesVoisins[i])
                
                if noeudVoisin in noeudsTraites:
                    # Noeud est déjà traité
                    continue
                
                if noeudVoisin in noeudsATraiter:
                    # Noeud déjà atteint, on voit si on a trouvé 
                    #       un chemin plus court pour y accèder
                    if noeudVoisin.__distance > (plusProche.__distance + dist):
                        noeudVoisin.__distance = plusProche.__distance + dist
                        noeudVoisin.__arcPrecedent = arcVoisin
                        noeudVoisin.__noeudPrecedent = plusProche
            
                    continue
          
                # Nouveau noeud atteint, on l'initialise
                noeudVoisin.__distance = plusProche.__distance + dist
                noeudVoisin.__arcPrecedent = arcVoisin
                noeudVoisin.__noeudPrecedent = plusProche
                noeudsATraiter.append(noeudVoisin)
        
        
        # Phase "arriere"
        if arrivee not in noeudsTraites:
            # Couldn't reach it
            # sys.exit("Error: Couldn't reach it")
            return None
        
        if arrivee not in PPC:
            PPC.append(arrivee)
            
        arcsFinaux = []
        noeudsFinaux = []
        
        suivant = arrivee
        while (True):
            arcsFinaux.insert(0, suivant.__arcPrecedent)
            #suivant.__arcPrecedent.addGroupe(plusCourtChemin)
            if suivant.__arcPrecedent not in PPC:
                PPC.append(suivant.__arcPrecedent)
            suivant = suivant.__noeudPrecedent
            if suivant == self:
                break
        
            noeudsFinaux.insert(0, suivant)
            #suivant.addGroupe(plusCourtChemin)
            if suivant not in PPC:
                PPC.append(suivant)
                
        noeudsFinaux.insert(0, self)
        # self.addGroupe(plusCourtChemin)
        if self not in PPC:
            PPC.append(self)
        noeudsFinaux.insert(0, arrivee)
        # arrivee.addGroupe(plusCourtChemin)
        

#        plusCourtChemin.setListeArcs(arcsFinaux);
#        plusCourtChemin.setListeNoeuds(noeudsFinaux);
#        plusCourtChemin.setLength(arrivee.__distance);
#        
        return PPC
            
    
    def __chercheArcsNoeudsVoisins(self):
        '''
            Tient compte du sens de la circulation
        '''
        noeudsVoisins = []
        distancesVoisins = []
        arcsVoisins = []
        
        arcsEntrants = self.getArcsEntrants()
        arcsSortants = self.getArcsSortants()
        
        # transformation du sens géométrique au sens de circulation
        for arc in arcsEntrants:
            if arc.getOrientation() == -1 or arc.getOrientation() == 0:
                if arc.getNoeudIni() != None:
                    arcsVoisins.append(arc)
                    noeudsVoisins.append(arc.getNoeudIni())
                    distancesVoisins.append(arc.getPoids())
        for arc in arcsSortants:
            if arc.getOrientation() == 1 or arc.getOrientation() == 0:
                if arc.getNoeudFin() != None:
                    arcsVoisins.append(arc)
                    noeudsVoisins.append(arc.getNoeudFin())
                    distancesVoisins.append(arc.getPoids())
        
        return (arcsVoisins, noeudsVoisins, distancesVoisins)
    
    
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        if self.id == other.id:
            return True
        return False
        
    def __str__(self):
        return self.id
        

# =============================================================================
#
#
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
            self.noeudIni.getArcsSortants().remove(self)
    
        if noeud != None:
            self.noeudIni = noeud
      
        if self not in noeud.getArcsSortants():
            noeud.addArcSortant(self)
        else:
            self.noeudIni = None
    
    def getNoeudFin(self):
        return self.noeudFin
    
    def setNoeudFin(self, noeud):
        #self.noeudFin = noeudFin
        
        if self.noeudFin != None:
            self.getNoeudFin().getArcsEntrants().remove(self)
    
        if noeud != None:
            self.noeudFin = noeud
      
        if self not in noeud.getArcsEntrants():
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

    def __str__(self):
        return self.id


# =============================================================================
#
#
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
    
    
    def shortest_path(self, node1, node2):
        return node1.plusCourtChemin(node2)
    
    
    def shortest_path_distance(self, node1, node2):
        PPC = node1.plusCourtChemin(node2)
        return PPC[0].getDistance()


#if __name__ == '__main__':
#    n1 = Node()
#    n = Network()