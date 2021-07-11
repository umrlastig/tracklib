# -------------------------- Network ------------------------------------------
# Class to manage Network
# -----------------------------------------------------------------------------
import random
import progressbar
import numpy as np
import matplotlib.pyplot as plt

import tracklib.algo.Summarize as Sum
import tracklib.algo.Simplification as Simplification

from tracklib.core.Obs import Obs
from tracklib.core.Track import Track
from tracklib.core.GPSTime import GPSTime
from tracklib.core.Operator import Operator
from tracklib.core.Utils import priority_dict
from tracklib.core.TrackCollection import TrackCollection


AF_LINK = "#link"
AF_WEIGHT = "#weight"


class Node:
    
    def __init__(self, id, coord):
        
        self.id = id
        self.coord = coord
		
    def __str__(self):
        return "Node object: " + str(self.id)
  
    def plot(self, sym='r+'):
        plt.plot(self.coord.getX(), self.coord.getY(), sym)
		
class Edge:
    
    DOUBLE_SENS  = 0
    SENS_DIRECT  = 1
    SENS_INVERSE = -1
    
    def __init__(self, id, track):
        
        self.id = id
        self.geom = track
        
        self.source = None
        self.target = None
        self.orientation = 0
        self.weight = 0
		
    def plot(self, sym='k-'):
        self.geom.plot(sym)
        
    def __str__(self):
        return 'Edge #' + str(self.id)		
           
		
class Network:

    def __init__(self):
        
        self.NODES = dict();
        self.EDGES = dict(); 
        self.__idx_nodes = []
        self.__idx_edges = []
		
        self.NEXT_EDGES = dict()
        self.PREV_EDGES = dict()
        self.NBGR_EDGES = dict()

        self.NEXT_NODES = dict()
        self.PREV_NODES = dict()
        self.NBGR_NODES = dict()
		
        self.DISTANCES = None
		
    def addNode(self, node):
        if node.id not in self.NODES:
            self.NODES[node.id] = node
            self.__idx_nodes.append(node.id)
            self.NEXT_EDGES[node.id] = []
            self.PREV_EDGES[node.id] = []
            self.NBGR_EDGES[node.id] = []
            self.NEXT_NODES[node.id] = []
            self.PREV_NODES[node.id] = []
            self.NBGR_NODES[node.id] = []			
			
    def addEdge(self, edge, source, target):
        self.addNode(source)
        self.addNode(target)
        if target.id not in self.NODES:
            self.NODES[target.id] = target 
            self.__idx_nodes.append(target.id)
        edge.source = self.NODES[source.id]
        edge.target = self.NODES[target.id]
        self.EDGES[edge.id] = edge
        self.__idx_edges.append(edge.id)
        if edge.orientation >= 0:
            self.NEXT_EDGES[source.id].append(edge.id)
            self.PREV_EDGES[target.id].append(edge.id)	        
            self.NEXT_NODES[source.id].append(target.id)
            self.PREV_NODES[target.id].append(source.id)
        if edge.orientation <= 0:
            self.NEXT_EDGES[target.id].append(edge.id)
            self.PREV_EDGES[source.id].append(edge.id)	        
            self.NEXT_NODES[target.id].append(source.id)
            self.PREV_NODES[source.id].append(target.id)
        self.NBGR_EDGES[source.id].append(edge.id)
        self.NBGR_EDGES[target.id].append(edge.id)
        self.NBGR_NODES[source.id].append(target.id)
        self.NBGR_NODES[target.id].append(source.id)
		
    def __iter__(self):
        yield from [l[1] for l in list(self.EDGES.items())]
        
    def size(self):
        return len(self.EDGES)
		
    # ------------------------------------------------------------
    # Topometric methods
    # ------------------------------------------------------------ 
    def toGeoCoords(self, base):
        for id in self.__idx_nodes:
            self.NODES[id].coord = self.NODES[id].coord.toGeoCoords(base)
        for id in self.__idx_edges:
            self.EDGES[id].geom.toGeoCoords(base)

    def toENUCoords(self, base):
        for id in self.__idx_nodes:
            self.NODES[id].coord = self.NODES[id].coord.toENUCoords(base)
        for id in self.__idx_edges:
            self.EDGES[id].geom.toENUCoords(base)  

    def simplify(self, tolerance, mode=1):	
        for id in self.__idx_edges:
            self.EDGES[id].geom = Simplification.simplify(self.EDGES[id].geom, tolerance, mode)
			
    # ------------------------------------------------------------
    # Topologic methods
    # ------------------------------------------------------------ 
    def getNextNodes(self, node_id):
        return self.NEXT_NODES[node_id]
    def getNextEdges(self, node_id):
        return self.NEXT_EDGES[node_id]	
		
    def getPrevNodes(self, node_id):
        return self.PREV_NODES[node_id]	
    def getPrevEdges(self, node_id):
        return self.PREV_EDGES[node_id]	
		
    def getAdjacentNodes(self, node_id):
        return self.NBGR_NODES[node_id]	
    def getIncidentEdges(self, node_id):
        return self.NBGR_EDGES[node_id]	
		
    def degree(self, node_id):
        return self.getAdjacentNodes(node_id).size()
    def degreeIn(self, node_id):
        return self.getPrevNodes(node_id).size()
    def degreeOut(self, node_id):
        return self.getNextNodes(node_id).size()

    # ------------------------------------------------------------
    # Acces to data
    # ------------------------------------------------------------    
    def __getitem__(self, n):
        return self.EDGES[self.__idx_edges[n]]
    def __setitem__(self, n, edge):
        self.EDGES[self.__idx_edges[id]] = edge  
        
    def getIndexNodes(self):
        return self.__idx_nodes
        
    def getNumberOfNodes(self):
        return len(self.NODES)
    def getNumberOfEdges(self):
        return len(self.EDGES)
        
    def getNodeId(self, n):
        return self.__idx_nodes[n]
    def getEdgeId(self, n):
        return self.__idx_edges[n]
    def getNodesId(self):
        return [l[0] for l in list(self.NODES.items())]
    def getEdgesId(self):
        return [l[0] for l in list(self.EDGES.items())]
        
    def getRandomNode(self):
        return self.getNode(self.getNodesId()[random.randint(0, self.getNumberOfNodes())])
     
    def hasNode(self, id):
        return id in self.NODES  
    def hasEdge(self, id):
        return id in self.EDGES

    def getNode(self, id):
        return self.NODES[id]
    def getEdge(self, id):
        return self.EDGES[id] 
		
    def getAllEdgeGeoms(self):
        tracks = TrackCollection()
        for id in self.__idx_edges:
            tracks.addTrack(self.EDGES[id].geom)
        return tracks	

    # ------------------------------------------------------------
    # Graphics
    # ------------------------------------------------------------   		
    def plot(self, edges='k-', nodes='', indirect='r-', size=0.5):
    
        x1d = []; y1d = []; x1i = []; y1i = []
        x2d = []; y2d = []; x2i = []; y2i = []
        exd = []; eyd = []; exi = []; eyi = [];
        nx = [];   ny = [];
        
        L = list(self.EDGES.items())
        for i in range(len(L)):
            edge = L[i][1]
            for j in range(edge.geom.size()-1):
                if edge.orientation == Edge.DOUBLE_SENS:
                    x1d.append(edge.geom.getX()[j]); x2d.append(edge.geom.getX()[j+1])
                    y1d.append(edge.geom.getY()[j]); y2d.append(edge.geom.getY()[j+1])
                else:
                    x1i.append(edge.geom.getX()[j]); x2i.append(edge.geom.getX()[j+1])
                    y1i.append(edge.geom.getY()[j]); y2i.append(edge.geom.getY()[j+1])
            nx.append(edge.geom.getX()[0]); nx.append(edge.geom.getX()[-1])   
            ny.append(edge.geom.getY()[0]); ny.append(edge.geom.getY()[-1])

        for s, t, u, v in zip(x1d, y1d, x2d, y2d):
            exd.append(s); exd.append(u); exd.append(None)
            eyd.append(t); eyd.append(v); eyd.append(None)
        for s, t, u, v in zip(x1i, y1i, x2i, y2i):
            exi.append(s); exi.append(u); exi.append(None)
            eyi.append(t); eyi.append(v); eyi.append(None)
            
        if len(edges) > 0: 
            plt.plot(exd, eyd, edges, linewidth=size)
        if len(indirect) > 0: 
            plt.plot(exi, eyi, indirect, linewidth=size)
        if (len(nodes) > 0):
            plt.plot(nx, ny, nodes, markersize=4*size)  
			
    # ------------------------------------------------------------
    # Routing methods
    # ------------------------------------------------------------ 
    
    # ------------------------------------------------------------ 
	# Dijkstra algorithm to compute shortest_path(s). Routine is 
	# stopped when either target node is reached or distance to 
	# source node is greater than 'cut' value. The result of 
	# run_dijstra may be used as shortest distance between pair of 
	# node, or as shortest distances between 1 node and all other 
	# nodes of the graph model. Source and target must be provided
	# as nodes or node ids.
    # ------------------------------------------------------------
    def sub_network(self, source, cut):
        print("Sub network extraction...")
        self.run_dijkstra_forward(source, cut=cut)
        sub_net = Network()
        for eid in progressbar.progressbar(self.getEdgesId()):
            e = self.EDGES[eid]
            if (not e.source.visite) or (not e.target.visite):
                continue
            sub_net.addEdge(e, e.source, e.target)
        return sub_net
		
    def resetFlags(self):
        for elem in self.NODES.items():  	
            elem[1].poids = -1   
            elem[1].visite = False
            elem[1].antecedent = ""
            elem[1].antecedent_edge = ""

    def run_dijkstra_forward(self, source, target=None, cut=1e300, output_dict=None):
	
        # Input format
        if isinstance(source, Node):
            source = source.id
        if isinstance(target, Node):
            target = target.id  			
       
	    # Node initialization
        self.resetFlags()
        self.NODES[source].poids = 0

        pere = self.NODES[source];
		
        # Priority heap initialization	
        fil = priority_dict({self.NODES[source]:self.NODES[source].poids})	

        # Routing   
        while len(fil) != 0:
				
            pere = fil.pop_smallest()

            if (pere.poids > cut) or (pere.id == target):
                break

            if not output_dict is None:
                output_dict[(source, pere)] = pere.poids				

            pere.visite = True
            nextEdges = self.getNextEdges(pere.id)

            for edge_id in nextEdges:
                e = self.EDGES[edge_id]
                fils = e.target
                if fils == pere:
                    fils = e.source
                if fils.visite:
                    continue
                if (fils.poids == -1) or (pere.poids + e.weight < fils.poids):       
                    fils.poids = pere.poids + e.weight
                    fils.antecedent = pere
                    fils.antecedent_edge = e.id
                    fil.__setitem__(fils, fils.poids)

    def shortest_distance(self, source, target=None, cut=1e300):
	    # Input format
        if isinstance(source, Node):
            source = source.id
        if isinstance(target, Node):
            target = target.id  
        self.run_dijkstra_forward(source, target)
        if not target is None:
            return self.NODES[target].poids
        else:
            return [(n[1].poids<0)*1e300 + n[1].poids for n in self.NODES.items()]

    def all_shortest_distances(self, cut=1e300):
        print("Computing all pairs shortest distances...")
        distances = dict()
        for id_source in progressbar.progressbar(self.getNodesId()):
            self.run_dijkstra_forward(id_source, cut=cut, output_dict=distances)
        return distances				   
  
    def run_dijkstra_backward(self, target):
        node = target
        track = Track()
        track.addObs(Obs(node.coord))
        while (node.poids != 0) and (node.antecedent != ""):
            e = self.EDGES[node.antecedent_edge]
            if e.source != node:
                e.geom = e.geom.reverse()
            track = track + e.geom
            node = node.antecedent
            track.addObs(Obs(node.coord))
        return track
			
    def prepare(self, cut=1e300):
        self.DISTANCES = self.all_shortest_distances(cut=cut)
    def save_prep(self, filename):
        if self.DISTANCES is None:
            print("Error: prepare function must be called before attempting to save preparation")
            exit(1)
        np.save(filename, self.DISTANCES) 
    def load_prep(self, filename):
        self.DISTANCES = read_dictionary = np.load(filename, allow_pickle='TRUE').item()
