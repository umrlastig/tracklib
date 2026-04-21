# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Yann Méneroux
Creation date: 1th november 2020

tracklib library provides a variety of tools, operators and 
functions to manipulate GPS trajectories. It is a open source contribution 
of the LASTIG laboratory at the Institut National de l'Information 
Géographique et Forestière (the French National Mapping Agency).
See: https://tracklib.readthedocs.io
 
This software is governed by the CeCILL-C license under French law and
abiding by the rules of distribution of free software. You can  use, 
modify and/ or redistribute the software under the terms of the CeCILL-C
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info". 

As a counterpart to the access to the source code and rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability. 

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or 
data to be ensured and,  more generally, to use and operate it in the 
same conditions as regards security. 

The fact that you are presently reading this means that you have had
knowledge of the CeCILL-C license and that you accept its terms.



Classes to create topology.

"""

import math
import cmath
from rtree import index

#dps = 1.0       # Simplification threshold (m)
#ter = 10        # Terminal edge removing (m)
#tbp = 1e-3      # Tolerance between points (m)  -- 1e-6
#tsl = 30        # Length of "trisquels" (m)

LOOPS = []

class Topology:

    @staticmethod
    def create_topology(input_file, srid, output_file, tbp=1e-6, verbose=False):
        '''
          Create base topology network

        @param tbp 
        '''

        network = Network(tbp)

        f = open(input_file, "r")
        # Reading data
        lines = f.readlines()
        for i in range(0, len(lines)):
            wkt = lines[i]
            wkt = wkt.upper()

            if "MULTILINESTRING" in wkt:
                wkt = wkt.split("((")[1]
                wktlines = wkt.split(")")
                for line in wktlines:
                    geom = []
                    coords = line.replace(',(', '').strip()
                    if coords == '':
                        continue
                    for coord in coords.split(","):
                        sl = coord.strip().split(" ")
                        x = float(sl[0])
                        y = float(sl[1])
                        geom.append((float(x), float(y)))
                    network.addEdge(geom)

            elif "LINESTRING" in wkt:
                wkt = wkt.split("(")[1].split(")")[0]
                if wkt.strip() == '':
                    continue
                geom = []
                for coord in wkt.split(","):
                    sl = coord.strip().split(" ")
                    x = float(sl[0])
                    y = float(sl[1])
                    geom.append((float(x), float(y)))
                network.addEdge(geom)


        NODES = network.getListOfNodes()
        TOREM = []
        for i, node in enumerate(NODES):
            deg = network.getDegree(i)
            if deg == 2:
                TOREM.append(i)
        for idx in TOREM:
            network.removeDeg2Node(idx)

        network.writeAsWkt(output_file)




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
    def __init__(self, tbp):
        self.idx = index.Index()
        self.vertices = {}
        self.edges = {}
        self.node_counter = 0
        self.edge_counter = 0
        self.adjacency = {}
        self.tbp = tbp

    def __str__(self):
        return "Network with [" + str(self.getNumberOfNodes()) + "] nodes and [" + str(self.getNumberOfEgdes()) + "] edges"

    def addNode(self, x, y):
        L = list(self.idx.intersection((x-self.tbp, y-self.tbp, x+self.tbp, y+self.tbp)))
        if len(L) == 0:
            self.idx.insert(self.node_counter, (x-self.tbp, y-self.tbp, x+self.tbp, y+self.tbp))
            self.vertices[self.node_counter] = (x, y)
            self.adjacency[self.node_counter] = []
            self.node_counter += 1
    def queryNodeIndex(self, x, y):
        L = list(self.idx.intersection((x-self.tbp, y-self.tbp, x+self.tbp, y+self.tbp)))
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
        self.addNode(geom[0][0], geom[0][1])
        idx1 = self.queryNodeIndex(geom[0][0], geom[0][1])

        self.addNode(geom[-1][0], geom[-1][1])
        idx2 = self.queryNodeIndex(geom[-1][0], geom[-1][1])

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
        #print("Network written in ["+path+"]")
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
        return (abs(p1[0]-p2[0]) + abs(p1[1]-p2[1]) < self.tbp)
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

    
