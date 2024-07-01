
import sys
import math
import cmath
from rtree import index


# -------------------------------------------------------
# PARAMETERS
# -------------------------------------------------------
dps = 1.0       # Simplification threshold (m)
ter = 10        # Terminal edge removing (m)
tbp = 1e-6      # Tolerance between points (m)
tsl = 30        # Length of "trisquels" (m)
# -------------------------------------------------------


input_file = sys.argv[1]
output_file = sys.argv[2]

f = open(input_file, "r")

# Reading data
lines = f.readlines()

splits = []
ids = []
for i in range(1, len(lines)):
	entry = lines[i].split("MULTILINESTRING")[1].split(")")[0]
	splits.append(entry)
	ids.append(lines[i].split("\"")[2].split(",")[1])
	



# -----------------------------------------------------------
# Special edge object
# -----------------------------------------------------------   
class Edge:
    def __init__(self, ini, end, geom):
        self.ini = ini
        self.end = end
        self.geom = geom
    def length(self):
        L = 0
        for i in range(1, len(self.geom)):
            x1 = self.geom[i-1][0]; y1 = self.geom[i-1][1]
            x2 = self.geom[i][0]; y2 = self.geom[i][1]
            L += math.sqrt((x2-x1)**2+(y2-y1)**2)
        return L
class Network:
    def __init__(self):
        self.idx = index.Index()
        self.vertices = {}
        self.edges = {}
        self.node_counter = 0
        self.edge_counter = 0
        self.adjacency = {}
    def __str__(self):
        return "Network with [" + str(self.getNumberOfNodes()) + "] nodes and [" + str(self.getNumberOfEgdes()) + "] edges"
    def addNode(self, x, y):
        L = list(self.idx.intersection((x-tbp, y-tbp, x+tbp, y+tbp)))
        if len(L) == 0:
            self.idx.insert(self.node_counter, (x-tbp, y-tbp, x+tbp, y+tbp))
            self.vertices[self.node_counter] = (x, y)
            self.adjacency[self.node_counter] = []
            self.node_counter += 1
    def queryNodeIndex(self, x, y):
        L = list(self.idx.intersection((x-tbp, y-tbp, x+tbp, y+tbp)))
        if len(L) == 0:
            return -1
        return L[0]
    def getListOfNodes(self):
        return self.vertices.keys()
    def getListOfEdges(self):
        return self.edges.keys()
    def getNodeGeom(self, i):
        return self.vertices[i]
    def getEdgeGeom(self, i):
        return self.edges[i]
    def addEdge(self, geom):
        self.addNode(geom[ 0][0], geom[ 0][1]); idx1 = self.queryNodeIndex(geom[ 0][0], geom[ 0][1])
        self.addNode(geom[-1][0], geom[-1][1]); idx2 = self.queryNodeIndex(geom[-1][0], geom[-1][1])
        self.edges[self.edge_counter] = Edge(idx1, idx2, geom)
        self.adjacency[idx1].append(self.edge_counter)
        self.adjacency[idx2].append(self.edge_counter)
        self.edge_counter += 1
    def getNumberOfEgdes(self):
        return len(self.edges)
    def getNumberOfNodes(self):
        return len(self.vertices)
    def writeAsWkt(self, path):
        out = open(path, "w")
        out.write("id,i1,i2,wkt\n")
        for i in range(self.edge_counter):
            if not i in self.edges:
                continue
            idx1 = self.edges[i].ini
            idx2 = self.edges[i].end
            line  = str(i)+","+str(idx1)+","+str(idx2)+",\"LINESTRING("
            for j in range(len(self.edges[i].geom)):
                line += str(self.edges[i].geom[j][0])+" "+str(self.edges[i].geom[j][1])
                if j < len(self.edges[i].geom)-1:
                    line += ","
            line += ")\""
            out.write(line+"\n")
        out.close()
        print("Network written in ["+path+"]")
    def removeNode(self, i):
        node_geom = self.getNodeGeom(i)
        self.idx.delete(i, [node_geom[0], node_geom[1], node_geom[0], node_geom[1]])
        del self.adjacency[i]
        del self.vertices[i]
        return node_geom
    def removeEdge(self, i):
        edge = self.edges[i]
        self.adjacency[edge.ini].remove(i)
        self.adjacency[edge.end].remove(i)
        del self.edges[i]
    def __samePt(self, p1, p2):
        return (abs(p1[0]-p2[0]) + abs(p1[1]-p2[1]) < tbp)
    def __mergeEdgesGeom(self, geom1, geom2):
        for i in range(len(geom2)):
            geom1.append(geom2[i])
        return geom1
    def __fusionEdgesGeom(self, geom1, geom2):
        if (self.__samePt(geom1[-1], geom2[0])):  
            #print("AB+BC")
            geom2 = geom2[1:]
            return self.__mergeEdgesGeom(geom1, geom2)
        if (self.__samePt(geom1[-1], geom2[-1])):    
            #print("AB+CB")
            geom2.reverse()
            geom2 = geom2[1:]
            return self.__mergeEdgesGeom(geom1, geom2)
        if (self.__samePt(geom1[0], geom2[0])):     
            #print("BA+BC")
            geom1.reverse()
            geom2 = geom2[1:]
            return self.__mergeEdgesGeom(geom1, geom2)
        if (self.__samePt(geom1[0], geom2[-1])):
            #print("BA+CB")
            geom1.reverse()
            geom2.reverse()
            geom2 = geom2[1:]
            return self.__mergeEdgesGeom(geom1, geom2)
    def getDegree(self, i):
        return len(self.adjacency[i])
    def removeDeg2Node(self, i):
        deg = self.getDegree(i)
        if  deg != 2:
            print("Error: node ["+str(i)+"] is of degree "+str(deg))
            return -1
        edges = self.adjacency[i]; e1 = edges[0]; e2 = edges[1]
        # Control loop
        if ((self.edges[e1].ini == self.edges[e2].ini) and (self.edges[e1].end == self.edges[e2].end)):
            LOOPS.append(e1)
            return -1
        if ((self.edges[e1].ini == self.edges[e2].end) and (self.edges[e1].end == self.edges[e2].ini)):
            LOOPS.append(e2)
            return -1
        geom1 = self.getEdgeGeom(edges[0]).geom
        geom2 = self.getEdgeGeom(edges[1]).geom
        fusion = self.__fusionEdgesGeom(geom1, geom2)
        self.removeEdge(e1)
        self.removeEdge(e2)
        node_geom = self.removeNode(i)
        self.addEdge(fusion)

    
network = Network()    
    
LOOPS = []    
    
    
 
    
# -----------------------------------------------------------
# Create base topology network
# -----------------------------------------------------------
N = len(splits)
for i in range(N):
    print("["+str(i)+"/"+str(N)+"] -> "+str(network.getNumberOfNodes()))
    s = splits[i].replace('(', '').replace(')', '').replace(',',' ').strip()
    values = s.split(' ')
    X = values[0::2]
    Y = values[1::2]
    geom = []
    for j in range(len(X)):
        geom.append((float(X[j]), float(Y[j])))
    network.addEdge(geom)
    
    

print(network)

network.writeAsWkt(output_file)    

