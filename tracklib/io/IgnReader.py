# -*- coding: utf-8 -*-

import json
import requests
from xml.dom import minidom

from tracklib.core.Network import Network, Edge, Node
from tracklib.core.Track import Track
import tracklib.util.Wkt as wkt

class IgnReader:
    
    NB_PER_PAGE = 1000;
    
    URL_SERVER = "https://wxs.ign.fr/choisirgeoportail/geoportail/wfs?"
    URL_SERVER += "service=WFS&version=2.0.0&request=GetFeature&"
    URL_SERVER += "typeName=BDTOPO_V3:troncon_de_route&"
    #URL_SERVER += "srsName=EPSG:2154&"
    URL_SERVER += "outputFormat=json&"
    #URL_SERVER += "BBOX=44.538617443499014,5.808794912294471,45.05505710140573,6.644301708889899"
    #URL_SERVER += "&count=3&startIndex=0"
    
    #self.id = id
    #self.coords = coords
    #self.nature = nature
    #self.sens = sens
    #self.fictif = fictif
    #self.pos = pos

    # ===========================
    # tolerance
    # ===========================
    @staticmethod
    def getNetwork(bbox, proj, tolerance = 0.1):
        '''
            TODO : posSol
        '''
        
        network = Network()
        
        cptNode = 1
        base = None
        
        nbRoute = IgnReader.__getNbRouteEmprise(bbox)
        nbiter = int(nbRoute / IgnReader.NB_PER_PAGE) + 1
        
        offset = 0
        for j in range(nbiter):
            URL_FEAT = IgnReader.URL_SERVER
            URL_FEAT += "BBOX=" + str(bbox[1]) + "," + str(bbox[0])  
            URL_FEAT += "," + str(bbox[3]) + "," + str(bbox[2])
            URL_FEAT += "&count=" + str(IgnReader.NB_PER_PAGE) 
            URL_FEAT += "&startIndex=" + str(offset)
            URL_FEAT += "&RESULTTYPE=results"
            # print (URL_FEAT)

            response = requests.get(URL_FEAT)
            data = json.loads(response.text)
            features = data['features']
            for feature in features:
                
                idd = feature['id']
                # nature = feature['properties']['nature']
                fictif = feature['properties']['fictif']
                if fictif == 'True':
                    continue
                
                # TODO
                #pos = feature['properties']['position_par_rapport_au_sol']
                
                TAB_OBS = []
                coords = feature['geometry']['coordinates']
                if (feature['geometry']['type'] == 'LineString'):
                    #print (str(len(coords)))
                    #geom = coords
                    TAB_OBS = wkt.tabCoordsLineStringToObs(coords, 'GEOCOORDS')
                
                if len(TAB_OBS) < 2:
                    continue
                
                track = Track(TAB_OBS)
                if base == None:
                    track.toENUCoords()
                    base = track.base
                else:
                    track.toENUCoords(base)
                
                
                edge = Edge(idd, track)
                
                # Orientation
                sens = feature['properties']['sens_de_circulation']
                orientation = 0
                if sens == 'Double sens' or sens == 'Sans objet':
                    orientation = 0
                elif sens == 'Direct' or sens == 'Sens direct':
                    orientation = 1
                elif sens == 'Indirect' or sens == 'Sens inverse':
                    orientation = -1
                #edge.setOrientation(orientation)
                # edge.orientation = orientation
                edge.orientation = 0
                
                # Poids
                poids = track.length()
                #edge.setPoids(poids)
                edge.poids= poids
                
                # Source node 
                p1 = track.getFirstObs().position
                noeudIni = Node(str(cptNode), p1)
                candidates = selectNodes(network, Node('0', p1), tolerance)
                if len(candidates) > 0:
                    for cand in candidates:
                        #edge.setNoeudIni(cand)
                        noeudIni = cand
                else:
                    #edge.setNoeudIni(noeudIni)
                    network.addNode(noeudIni)  
                    cptNode += 1
                
                # Target node 
                p2 = track.getLastObs().position
                noeudFin = Node(str(cptNode), p2)
                candidates = selectNodes(network, Node('0', p2), tolerance)
                if len(candidates) > 0:
                    for cand in candidates:
                        #edge.setNoeudFin(cand)
                        noeudFin = cand
                else:
                    #edge.setNoeudFin(noeudFin)
                    network.addNode(noeudFin)
                    cptNode += 1
                
                # Add edge
                #network.addEdge(edge)
                network.addEdge(edge, noeudIni, noeudFin)
                
            offset = offset + IgnReader.NB_PER_PAGE
        
        return network

    
    
    
    
    
    # --------------------------------------------------------------------------
    # Function to count road network features in bbox
    # --------------------------------------------------------------------------
    # Input : 
    #   - v: a float value
    # --------------------------------------------------------------------------
    # Output : number 
    # --------------------------------------------------------------------------
    @staticmethod
    def __getNbRouteEmprise(bbox):
        
        nb = 0
        
        URL_HITS = IgnReader.URL_SERVER 
        URL_HITS += "BBOX=" + str(bbox[1]) + "," + str(bbox[0])  
        URL_HITS += "," + str(bbox[3]) + "," + str(bbox[2])
        URL_HITS += "&resulttype=hits"
        
        res = requests.get(URL_HITS)
        # x = requests.get(url, proxies = { "https" : "https://1.1.0.1:80"})
        dom = minidom.parseString(res.text)
        result = dom.getElementsByTagName('wfs:FeatureCollection')
        
        nb = int(result[0].attributes['numberMatched'].value)
        
        return nb
        


def selectNodes(network, node, distance):
        '''
        Selection des autres noeuds dans le cercle dont node.coord est le centre, 
        de rayon distance
        Parameters
        ----------
        node : Node
            le centre du cercle de recherche.
        tolerance : double
            le rayon du cercle de recherche.
        Returns
        -------
        NODES : tableau de NODES
            liste des noeuds dans le cercle
        '''
        NODES = []
        
        for key in network.NODES:
            n = network.NODES[key]
            if n.coord.distance2DTo(node.coord) <= distance:
                NODES.append(n)
        
        return NODES