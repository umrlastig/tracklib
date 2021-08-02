# -*- coding: utf-8 -*-

import math
import json
import progressbar
import requests
from xml.dom import minidom

from tracklib.core.Obs import Obs
from tracklib.core.Track import Track
from tracklib.core.Coords import GeoCoords
from tracklib.core.SpatialIndex import SpatialIndex
from tracklib.core.Network import Network, Edge, Node
from tracklib.core.TrackCollection import TrackCollection

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
    def getNetwork(bbox, proj=None, margin=0.0, tolerance=0.1, spatialIndex=True):
        '''

        Parameters
        ----------
        bbox : 4-tuples , mandatory
            DESCRIPTION. The bounding box of the selected area. 
            The bounding box must be expressed in WGS84
        proj : projection of results, optional.
            For example: 'EPSG:2154' or 'EPSG:4326'
            
        -------
            TODO : posSol
        '''
		
        # Adding margin
        xmin, xmax, ymin, ymax = bbox
        dx = (xmax-xmin)/2
        dy = (ymax-ymin)/2
        bbox = (xmin-margin*dx, xmax+margin*dx, ymin-margin*dy, ymax+margin*dy)
        
        network = Network()
        if spatialIndex:
            network.spatial_index = SpatialIndex(bbox, resolution=(dx/1e3, dy/1e3), margin=0.4)
            network.spatial_index.collection = network

        cptNode = 0
		
        if proj == None:
            proj = 'EPSG:4326'
        
        nbRoute = IgnReader.__getNbRouteEmprise(bbox)
        nbiter = int(nbRoute / IgnReader.NB_PER_PAGE) + 1
        
        offset = 0
        for j in range(nbiter):
            print("PAGE "+str(j+1)+"/"+str(nbiter))
            URL_FEAT = IgnReader.URL_SERVER
            URL_FEAT += "BBOX=" + str(bbox[2]) + "," + str(bbox[0])  
            URL_FEAT += "," + str(bbox[3]) + "," + str(bbox[1])
            URL_FEAT += "&count=" + str(IgnReader.NB_PER_PAGE) 
            URL_FEAT += "&startIndex=" + str(offset)
            URL_FEAT += "&RESULTTYPE=results"
            URL_FEAT += "&srsname="+proj

            #print (URL_FEAT)

            response = requests.get(URL_FEAT)
            data = json.loads(response.text)
            features = data['features']

            for feature in progressbar.progressbar(features):
                
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
                    #print (coords)
                    
                    typeCoord = 'GEOCOORDS'
                    if proj == 'EPSG:2154':
                        typeCoord = 'ENUCoords'
                    TAB_OBS = wkt.tabCoordsLineStringToObs(coords, typeCoord)
                    
                
                if len(TAB_OBS) < 2:
                    continue
                
                track = Track(TAB_OBS)                
                edge = Edge(idd, track)
                
                # Orientation
                sens = feature['properties']['sens_de_circulation']
                edge.orientation = Edge.DOUBLE_SENS
                if sens == None or sens == '':
                    edge.orientation = Edge.DOUBLE_SENS
                elif sens == 'Double sens' or sens == 'Sans objet':
                    edge.orientation = Edge.DOUBLE_SENS
                elif sens == 'Direct' or sens == 'Sens direct':
                    edge.orientation = Edge.SENS_DIRECT
                elif sens == 'Indirect' or sens == 'Sens inverse':
                    edge.orientation = Edge.SENS_INVERSE
                else:
                    print (sens)
            
                edge.weight = track.length()
                
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
        URL_HITS += "BBOX=" + str(bbox[2]) + "," + str(bbox[0])  
        URL_HITS += "," + str(bbox[3]) + "," + str(bbox[1])
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
        
        if network.spatial_index is None:
            for key in network.getIndexNodes():
                n = network.NODES[key]
                if n.coord.distance2DTo(node.coord) <= distance:
                    NODES.append(n)
        else:
            vicinity_edges = network.spatial_index.neighborhood(node.coord, unit=1)
            for e in vicinity_edges:
                source = network.EDGES[network.getEdgeId(e)].source
                target = network.EDGES[network.getEdgeId(e)].target
                if source.coord.distance2DTo(node.coord) <= distance:
                    NODES.append(source)
                if target.coord.distance2DTo(node.coord) <= distance:
                    NODES.append(target)

        return NODES