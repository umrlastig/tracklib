# -*- coding: utf-8 -*-

import csv

#from tracklib.core.Coords import ENUCoords, ECEFCoords, GeoCoords
from tracklib.core.Network import Network, Node, Edge
from tracklib.core.Track import Track
from tracklib.io.NetworkFormat import NetworkFormat
import tracklib.util.Wkt as wkt

class NetworkReader:
    
    @staticmethod
    def readFromFile(path, formatfile = 'DEFAULT'):
        '''
        TODO : posSol
        '''
        
        fmt = NetworkFormat(formatfile)  # Read from input parameters
        
        network = Network()
        
        with open(path, encoding='utf-8') as csvfile:
            
            spamreader = csv.reader(csvfile, delimiter=fmt.separator, doublequote= True, )
        
            
            # Header
            cpt = 0
            for row in spamreader:
                cpt += 1
                if cpt >= fmt.h:
                    break
    
                
            for row in spamreader:
                
                edge_id = str(row[fmt.pos_edge_id])
                geom = str(row[fmt.pos_wkt])
                TAB_OBS = wkt.wktLineStringToObs(geom, fmt.srid.upper())
                
                # Au moins 2 points
                if len(TAB_OBS) < 2:
                    continue
                
                track = Track(TAB_OBS)

                # Transformation GEO coordinates to ENU
                if (fmt.srid.upper() in ["GEOCOORDS", "GEO", "ECEFCOORDS", "ECEF"]):
                    track.toENUCoords()
                
                edge = Edge(edge_id, track)
                
                # Orientation
                orientation = int(row[fmt.pos_sens])
                if (orientation not in [Edge.DOUBLE_SENS, Edge.SENS_DIRECT, Edge.SENS_INVERSE]):
                    orientation = Edge.DOUBLE_SENS
                edge.setOrientation(orientation)
                
                # Poids
                if fmt.pos_poids == -1:
                    poids = track.length()
                else:
                    poids = float(row[fmt.pos_poids])
                edge.setPoids(poids)
                
                # source node 
                source = str(row[fmt.pos_source])
                noeudIni = Node(source, track.getFirstObs())
                if noeudIni not in network.NODES:
                    edge.setNoeudIni(noeudIni)
                    network.addNode(noeudIni)
                else:
                    n = network.getNode(source)
                    edge.setNoeudIni(n)
                
                # target node 
                target = str(row[fmt.pos_target])
                noeudFin = Node(target, track.getLastObs())
                if noeudFin not in network.NODES:
                    edge.setNoeudFin(noeudFin)
                    network.addNode(noeudFin)
                else:
                    n = network.getNode(target)
                    edge.setNoeudFin(n)
                
                # Add edge
                network.addEdge(edge)
                
                #if len(network.EDGES) > 10:
                #    break
        
        csvfile.close()        
                
        # Return network loaded
        return network
        
    