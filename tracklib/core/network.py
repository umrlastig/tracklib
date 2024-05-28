# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Yann Méneroux
    Marie-Dominique Van Damme
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



This module contains the class to manage Network

"""

# For type annotation
from __future__ import annotations
from typing import Literal, Union, Dict, Tuple
#from tracklib.util.exceptions import *

import random
#from typing import Union
import progressbar
import numpy as np
import matplotlib.pyplot as plt

import tracklib as tracklib
from tracklib.core import (ECEFCoords, ENUCoords, GeoCoords,
                      Obs,
                      priority_dict,
                      TrackCollection,
                      Bbox)
from tracklib.algo import simplify
from tracklib.core import Track


class Node:
    """Node / vertice of a network"""

    def __init__(self, id: int, coord: Union[ECEFCoords, ENUCoords, GeoCoords]):
        """:class:`Node` constructor

        :param id: unique id of Node
        :param coord: A coordinate object
        """
        self.id = id
        self.coord = coord

    def __str__(self) -> str:
        """Node to string"""
        return "Node object: " + str(self.id)

    def __lt__(self, other: Node) -> bool:
        """Check if a node is bigger than the current node

        :param other: Node to test
        :return: Result of the test
        """
        if isinstance(other, Node):
            return self.id < other.id
        return False

    def __eq__(self, other: Node) -> bool:
        """Check if a node is equal with the current node

        :param other: Node to test
        :return: Result of the test
        """
        if isinstance(other, Node):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        """Return the hash of current node"""
        return hash(self.id)

    def distanceTo(self, node: Node) -> float:
        """Distance to an other node

        :param node: Node to compute the distance
        :return: 3d distance
        """
        return self.coord.distanceTo(node.coord)

    def distance2DTo(self, node: Node) -> float:
        """2d distance to an other node

        :param node: Node to compute the distance
        :return: 2d distance
        """
        return self.coord.distance2DTo(node.coord)

    def plot(self, sym="r+"):
        """Plot the node"""
        plt.plot(self.coord.getX(), self.coord.getY(), sym)


class Edge:
    """Class to define an edge / arc"""

    DOUBLE_SENS = 0
    SENS_DIRECT = 1
    SENS_INVERSE = -1

    def __init__(self, id: int, track: Track):
        """:class:`Edge` constructor

        :param id: unique id of Edge
        :param track: A track
        """
        self.id = id
        self.geom = track

        self.source = None
        self.target = None
        self.orientation = 0
        self.weight = 0

    def plot(self, sym: str = "k-"):
        """Plot the edge

        :param sym: TODO
        """
        self.geom.plot(sym)

    def __str__(self) -> str:
        """Print the edge"""
        return "Edge #" + str(self.id)


class Network:
    """Define a network"""

    # Routing modes
    ROUTING_ALGO_DIJKSTRA = 0
    ROUTING_ALGO_ASTAR = 1

    # Analytical features
    AF_LINK = "#link"
    AF_WEIGHT = "#weight"

    def __init__(self):
        """:class:`Network` constructor"""

        self.NODES = dict()
        self.EDGES = dict()
        self.__idx_nodes = []
        self.__idx_edges = []

        self.NEXT_EDGES = dict()
        self.PREV_EDGES = dict()
        self.NBGR_EDGES = dict()

        self.NEXT_NODES = dict()
        self.PREV_NODES = dict()
        self.NBGR_NODES = dict()

        self.DISTANCES = None
        self.routing_mode = Network.ROUTING_ALGO_DIJKSTRA

        self.astar_wgt = 1

        self.spatial_index = None

    def addNode(self, node: Node):
        """Add a :class:`Node` to the current :class:`Network`

        :param Node: Node to add
        """
        if node.id not in self.NODES:
            self.NODES[node.id] = node
            self.__idx_nodes.append(node.id)
            self.NEXT_EDGES[node.id] = []
            self.PREV_EDGES[node.id] = []
            self.NBGR_EDGES[node.id] = []
            self.NEXT_NODES[node.id] = []
            self.PREV_NODES[node.id] = []
            self.NBGR_NODES[node.id] = []

    def addEdge(self, edge: Edge, source: Node, target: Node):
        """Add a :class:`Edge` to the current :class:`Network`

        :param edge: Edge to add
        :param source: Source Node
        :param target: Target Node
        """
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
        if not self.spatial_index is None:
            self.spatial_index.addFeature(edge.geom, self.getNumberOfEdges() - 1)

    def __iter__(self):
        """Define an iterator on Network"""
        yield from [l[1] for l in list(self.EDGES.items())]

    def size(self) -> int:
        """Return the number of edges

        :return: Number of edges
        """
        return len(self.EDGES)

    def setRoutingMethod(self, method: int):
        """Define the routing algorithm

        :param method: Algorithm of routing. Two values are possible :

            1. ROUTING_ALGO_DIJKSTRA [default].
            2. ROUTING_ALGO_ASTAR.

        **NB:** A* is an efficient approximate version of Dijkstra. It returns
        exact solution under theoretical assumptions on the metrics used to set
        weights on graph edges.
        """
        self.routing_mode = method

    def setAStarWeight(self, weight: float):
        """Define the A* weight"""
        self.astar_wgt = weight

    # ------------------------------------------------------------
    # Topometric methods
    # ------------------------------------------------------------
    def toGeoCoords(self, base: Union[ECEFCoords, ENUCoords]):
        """Convert network to :class:`core.Coords.GeoCoords`

        :param base: Base coordinate for conversion
        """
        for id in self.__idx_nodes:
            self.NODES[id].coord = self.NODES[id].coord.toGeoCoords(base)
        for id in self.__idx_edges:
            self.EDGES[id].geom.toGeoCoords(base)

    def toENUCoords(self, base: Union[GeoCoords, ECEFCoords]):
        """Convert network to :class:`core.Coords.ENUCoords`

        :param base: Base coordinate for conversion
        """
        for id in self.__idx_nodes:
            self.NODES[id].coord = self.NODES[id].coord.toENUCoords(base)
        for id in self.__idx_edges:
            self.EDGES[id].geom.toENUCoords(base)

    def getSRID(self) -> int:
        """Return the SRID of network

        :return: SRID of current network
        """
        return self.EDGES[self.__idx_edges[0]].geom.getSRID()

    def totalLength(self) -> int:
        """Count the edges of current network

        :return: Number of edges
        """
        count = 0
        for id in self.__idx_edges:
            count += self.EDGES[id].geom.length()
        return count

    def simplify(self, tolerance, mode: int = 1):
        """Simplification of current network

        :param tolerance: TODO
        :param mode: Mode of simplification. The possibles values are:

            1. DOUGLAS_PEUCKER
            2. VISVALINGAM
            3. MINIMIZE_LARGEST_DEVIATION
            4. MINIMIZE_ELONGATION_RATIO
            5. PRECLUDE_LARGE_DEVIATION
            6. FREE
            7. FREE_MAXIMIZE

            See :func:`algo.Simplification.simplify` documentation for more infos

        """
        for id in self.__idx_edges:
            self.EDGES[id].geom = simplify(
                self.EDGES[id].geom, tolerance, mode
            )

    # ------------------------------------------------------------
    # Spatial index creation, export and import functions
    # ------------------------------------------------------------
    def createSpatialIndex (
        self, resolution=None, margin: float = 0.05, verbose: bool = True
    ):
        """Create a spatial index

        :param resolution: TODO
        :param margin: TODO
        :param verbose: Verbose creation
        """
        self.spatial_index = tracklib.SpatialIndex(self, resolution, margin, verbose)

    def exportSpatialIndex(self, filename: str):
        """Export the spatial index to a file

        :param filename: File to export
        """
        self.spatial_index.save(filename)

    def importSpatialIndex(self, filename: str):
        """Import a spatial index from a file

        :parma filename: File to import
        """
        self.spatial_index = tracklib.SpatialIndex.load(filename)

    # ------------------------------------------------------------
    # Topologic methods
    # ------------------------------------------------------------
    def getNextNodes(self, node_id: int):
        """Give the XXX of a node

        :param node_id: id of a node
        """
        return self.NEXT_NODES[node_id]

    def getNextEdges(self, node_id: int):
        """Give the XXX of a node

        :param node_id: id of a node
        """
        return self.NEXT_EDGES[node_id]

    def getPrevNodes(self, node_id: int):
        """Give the XXX of a node

        :param node_id: id of a node
        """
        return self.PREV_NODES[node_id]

    def getPrevEdges(self, node_id: int):
        """Give the XXX of a node

        :param node_id: id of a node
        """
        return self.PREV_EDGES[node_id]

    def getAdjacentNodes(self, node_id: int):
        """Give the XXX of a node

        :param node_id: id of a node
        """
        return self.NBGR_NODES[node_id]

    def getIncidentEdges(self, node_id: int):
        """Give the XXX of a node

        :param node_id: id of a node
        """
        return self.NBGR_EDGES[node_id]

    def degree(self, node_id: int) -> int:
        """Compute the degree of a node

        :param node_id: id of a node
        :return: in degree
        """
        return self.getAdjacentNodes(node_id).size()

    def degreeIn(self, node_id: int) -> int:
        """Compute the in degree of a node

        :param node_id: id of a node
        :return: in degree
        """
        return self.getPrevNodes(node_id).size()

    def degreeOut(self, node_id: int) -> int:
        """Compute the out degree of a node

        :param node_id: id of a node
        :return: out degree
        """
        return self.getNextNodes(node_id).size()

    # ------------------------------------------------------------
    # Acces to data
    # ------------------------------------------------------------
    def __getitem__(self, n: int) -> Edge:
        """Return an edge item from its id

        :param n: Edge id
        :return: An edge
        """
        return self.EDGES[self.__idx_edges[n]]

    def __setitem__(self, n: int, edge: Edge):
        """Set an Edge for a give id value

        :param id: The id
        :param edge: The edge to set
        """
        self.EDGES[self.__idx_edges[id]] = edge

    def getIndexNodes(self) -> list[int]:
        """Return the list of seted nodes

        :return: A list of nodes id
        """
        return self.__idx_nodes

    def getNumberOfNodes(self) -> int:
        """Number of nodes in the network

        :return: Number of nodes
        """
        return len(self.NODES)

    def getNumberOfEdges(self) -> int:
        """Number of edges in the network

        :return: Number of edges
        """
        return len(self.EDGES)

    def getNumberOfVertices(self) -> int:
        """Number of vertices in the network

        :return: Number of vertices
        """
        count = 0
        for id in self.__idx_edges:
            count += self.EDGES[id].geom.size()
        return count

    def getNodeId(self, n: int) -> int:
        """The return the id of the n-est Node

        :param n: Position of the node
        :return: Id of the node
        """
        return self.__idx_nodes[n]

    def getEdgeId(self, n: int) -> int:
        """The return the id of the n-est Edge

        :param n: Position of the Edge
        :return: Id of the Edge
        """
        return self.__idx_edges[n]

    def getNodesId(self) -> list[int]:
        """Return a list of all nodes Id

        :return: A list of id
        """
        return [l[0] for l in list(self.NODES.items())]

    def getEdgesId(self) -> list[int]:
        """Return a list of all edges Id

        :return: A list of id
        """
        return [l[0] for l in list(self.EDGES.items())]

    def getRandomNode(self) -> Node:
        """Return a random node of network

        :return: A node randomly choosed
        """
        return self.getNode(
            self.getNodesId()[random.randint(0, self.getNumberOfNodes() - 1)]
        )

    def hasNode(self, id: int) -> bool:
        """Check if a node with a given id exist

        :param id: node id to test
        """
        return id in self.NODES

    def hasEdge(self, id: int) -> bool:
        """Check if a node with a given id exist

        :param id: edge id to test
        """
        return id in self.EDGES

    def getNode(self, id: int) -> Node:
        """Return the node with a give id

        :param id: node id to get
        """
        return self.NODES[id]

    def getEdge(self, id: int) -> Edge:
        """Return the edge with a give id

        :param id: edge id to get
        """
        return self.EDGES[id]

    def getAllEdgeGeoms(self) -> TrackCollection:
        """Return a TrackCollection of all edges

        :return: All edges of :class:`Network`
        """
        tracks = TrackCollection()
        for id in self.__idx_edges:
            tracks.addTrack(self.EDGES[id].geom)
        return tracks

    def bbox(self) -> Bbox:
        """Return the :class:`Bbox` of network"""
        return self.getAllEdgeGeoms().bbox()

    # ------------------------------------------------------------
    # Graphics
    # ------------------------------------------------------------

    def plot(self, edges:str="k-", nodes:str="", 
             direct:str="k--", indirect:str="k--", size:float=0.5, append=False):
        """
        Plot network

        :param edges: TODO
        :param nodes: TODO
        :param direct: TODO
        :param indirect: TODO
        :param size: TODO
        :param append: TODO
        """
        
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(10, 3))
        else:
            ax1 = plt


        x1b = []
        y1b = []
        x1i = []
        y1i = []
        x1d = []
        y1d = []
        x2b = []
        y2b = []
        x2i = []
        y2i = []
        x2d = []
        y2d = []
        exb = []
        eyb = []
        exi = []
        eyi = []
        exd = []
        eyd = []
        nx = []
        ny = []
        
        L = list(self.EDGES.items())
        for i in range(len(L)):
            edge = L[i][1]
            for j in range(edge.geom.size() - 1):
                if edge.orientation == tracklib.Edge.DOUBLE_SENS:
                    x1b.append(edge.geom.getX()[j])
                    x2b.append(edge.geom.getX()[j + 1])
                    y1b.append(edge.geom.getY()[j])
                    y2b.append(edge.geom.getY()[j + 1])
                else:
                    if edge.orientation == tracklib.Edge.SENS_DIRECT:
                        x1d.append(edge.geom.getX()[j])
                        x2d.append(edge.geom.getX()[j + 1])
                        y1d.append(edge.geom.getY()[j])
                        y2d.append(edge.geom.getY()[j + 1])
                    else:
                        x1i.append(edge.geom.getX()[j])
                        x2i.append(edge.geom.getX()[j + 1])
                        y1i.append(edge.geom.getY()[j])
                        y2i.append(edge.geom.getY()[j + 1])
            nx.append(edge.geom.getX()[0])
            nx.append(edge.geom.getX()[-1])
            ny.append(edge.geom.getY()[0])
            ny.append(edge.geom.getY()[-1])
        
        for s, t, u, v in zip(x1b, y1b, x2b, y2b):
            exb.append(s)
            exb.append(u)
            exb.append(None)
            eyb.append(t)
            eyb.append(v)
            eyb.append(None)
        for s, t, u, v in zip(x1d, y1d, x2d, y2d):
            exd.append(s)
            exd.append(u)
            exd.append(None)
            eyd.append(t)
            eyd.append(v)
            eyd.append(None)

        for s, t, u, v in zip(x1i, y1i, x2i, y2i):
            exi.append(s)
            exi.append(u)
            exi.append(None)
            eyi.append(t)
            eyi.append(v)
            eyi.append(None)

        if len(edges) > 0:
            ax1.plot(exb, eyb, edges, linewidth=size, label="double sens")
        if len(direct) > 0:
            ax1.plot(exd, eyd, direct, linewidth=size, label="direct")
        if len(indirect) > 0:
            ax1.plot(exi, eyi, indirect, linewidth=size, label="indirect")
        if len(nodes) > 0:
            ax1.plot(nx, ny, nodes, markersize=4 * size)

    # ------------------------------------------------------------
    # Routing methods
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # Routing algorithms to compute shortest_path(s). Routine is
    # stopped when either target node is reached or distance to
    # source node is greater than 'cut' value. The result of
    # run_dijstra may be used as shortest distance between pair of
    # node, or as shortest distances between 1 node and all other
    # nodes of the graph model. Source and target must be provided
    # as nodes or node ids. As a default strategy, all computations
    # are done with the popular and efficient Dijkstra's algorithm
    # If needed, settings enable to use A* heuristics optimization
    # ------------------------------------------------------------
    # Available functions:
    #  - run_routing_forward: executes forward pass of dijkstra
    #  - run_routing_backward: backtracking recursive search for
    #    the shortest path joining source and target nodes.
    #  - sub_network: extracts sub-network from forward search
    #  - shortest_distance: finds shortest distance between source
    #    node and either a target node or a list of target nodes.
    #  - all_shortest_distances: computes all shortest distances
    #    between pairs of nodes in an efficient way.
    #  - shortest_path: compute shortest path between 2 nodes.
    #  - prepare: computes all distances between pairs of nodes
    #  - save_prep: saves the result computed by 'prepare'
    #  - load_prep: imports the result saved by 'save_prep'
    #  - prepared_shortest_distance: reads shortest distance from
    #    a precomputed dictionnary structure. May be called only
    #    after prepare or load_prep functions.
    # ------------------------------------------------------------
    # Most of the above search functions may be interrupted before
    # end by specifying a target node and/or a cut distance.
    # Output results may be compiled in an output dictionnary.
    # ------------------------------------------------------------
    # Important: to compute the shortest distances between all
    # pairs of nodes, 'all_shortest_distances' function is more
    # efficient than successive calls of shortest_distance(n1, n2)
    # for all pairs of nodes n1 and n2, since the former sums up
    # to an n x O(n.log(n)) = O(n^2.log(n)) time complexity for
    # a typical planar road network, versus n^2 x O(n.log(n)) =
    # O(n^3.log(n)) for the latter. For a general network (not
    # necessarily planar), 'all_shortest_distances' function takes
    # O(n^3.log(n)) against O(n^4.log(n)) for 'shortest_distance'.
    # As a consequence, in every situation, all_shortest_distances
    # is n times faster than a (bad) strategy based on successive
    # calls of pairwise shortest_distance function.
    # ------------------------------------------------------------
    def __correctInputNode(self, node):
        """TODO"""
        if isinstance(node, Node):
            return node.id
        return node

    def sub_network(self, source: Union[int, Node, Union[GeoCoords, ENUCoords, ECEFCoords]], cut: float, mode: Literal["TOPOLOGIC", "GEOMETRIC"] = "TOPOLOGIC", verbose: bool = True) -> Network:
        """Extracts sub-network from routing forward search

        An edge is added to the output network if bot its ends have been visited during
        the search process (TOPOGRAPHIC mode) or if one of its ends are located in a
        circle centered on source with radius = cut


        :param source: a source node (id or node object) or a coord
        :param cut: a maximal distance for search
        :param mode: "TOPOLOGIC" (default) or "GEOMETRIC"
        :param verbose: Verbose creation

        :result: a network containing only visited nodes reachable
            from source with a cost lower than cut distance.

        """
        if mode == "TOPOLOGIC":
            self.run_routing_forward(source, cut=cut)
            return self.__sub_network_routing(verbose)
        if mode == "GEOMETRIC":
            return self.__sub_network_geometric(source, cut, verbose)
        print("Error: unknown network extraction mode: ", mode)
        exit(1)

    def __sub_network_routing(self, verbose: bool) -> Network:
        """Sub network generation

        :param verbose: Verbose creation
        :return: A sub part of the current network
        """
        if verbose:
            print("Sub network extraction...")
        sub_net = Network()
        to_run = self.getEdgesId()
        if verbose:
            to_run = progressbar.progressbar(to_run)
        for eid in to_run:
            e = self.EDGES[eid]
            if (not e.source.visite) or (not e.target.visite):
                continue
            sub_net.addEdge(e, e.source, e.target)
        return sub_net

    def __sub_network_geometric(self, source: Union[Node, str], cut: float, verbose: bool) -> Network:
        """Sub network generation, based on geometry

        :param source: Source for the sub-network
        :param cut: TODO
        :param verbose: Verbose generation
        :return: A sub part of the current network
        """
        if verbose:
            print("Sub network extraction...")
        if isinstance(source, Node) or isinstance(source, str):
            source = self.__correctInputNode(source).coord
        sub_net = Network()
        if self.spatial_index is None:
            to_run = self.getEdgesId()
        else:
            unit = self.spatial_index.groundDistanceToUnits(cut)
            to_run = [e[1] for e in self.spatial_index.neighborhood(source, unit=unit)]
        if verbose:
            to_run = progressbar.progressbar(to_run)
        for eid in to_run:
            e = self.EDGES[eid]
            if (
                min(
                    source.distance2DTo(e.source.coord),
                    source.distance2DTo(e.target.coord),
                )
                > cut
            ):
                continue
            sub_net.addEdge(e, e.source, e.target)
        return sub_net

    def __resetFlags(self):
        """Internal function to call before dijkstra forward step"""
        for elem in self.NODES.items():
            elem[1].poids = -1
            elem[1].visite = False
            elem[1].antecedent = ""
            elem[1].antecedent_edge = ""

    def run_routing_forward(self, source: Union[Node, int], target: Union[Node, int] = None, cut: float = 1e300, output_dict: dict = None):
        """Executes forward pass of routing algorithm to find shortest distance between
        source node and all other nodes in graph.

        Execution may be stopped prematurely by specifying target node and/or cut
        distance. For each nodes reached (with a distance d < cut) during the search
        process, an entry {key=(source, n), value=d} is added to an output dictionnary
        (if specified as input)

        :param source: a source node
        :param target: a target node
        :param cut: a maximal distance for search
        :param output_dict: output structure for retrieved distance
        """

        # Input format
        source = self.__correctInputNode(source)
        target = self.__correctInputNode(target)

        heuristic = 0

        # Node initialization
        self.__resetFlags()
        self.NODES[source].poids = 0

        pere = self.NODES[source]

        # Priority heap initialization
        fil = priority_dict({self.NODES[source]: self.NODES[source].poids})

        # Routing
        while len(fil) != 0:

            pere = fil.pop_smallest()

            # Stop conditions
            if (pere.poids > cut) or (pere.id == target):
                break

            if not output_dict is None:
                output_dict[(source, pere.id)] = pere.poids

            pere.visite = True
            nextEdges = self.getNextEdges(pere.id)

            # Loop on connected edges
            for edge_id in nextEdges:
                e = self.EDGES[edge_id]
                fils = e.target
                if fils == pere:
                    fils = e.source
                if fils.visite:
                    continue
                if (fils.poids == -1) or (pere.poids + e.weight < fils.poids):
                    if (self.routing_mode == 1) and not (target is None):
                        heuristic = self.astar_wgt * fils.distanceTo(self.NODES[target])
                    fils.poids = pere.poids + e.weight + heuristic
                    fils.antecedent = pere
                    fils.antecedent_edge = e.id
                    fil.__setitem__(fils, fils.poids)

    def shortest_distance( self, source: Union[int, Node], target: Union[int, Node] = None, cut: float = 1e300, output_dict: dict = None) -> Union[float, list[float]]:
        """Finds shortest distance between source node and either a target node or a
        list of target nodes.

        In every case, time complexity is :math:`O((n+m) \cdot \log(n))` with :math:`n`
        the number of node and :math:`m` the number of edges. That amounts roughly to
        :math:`O(n \cdot \log(n))` for a typical planar road network, and to
        :math:`O(n^2 \cdot \log(n))` for a general network

        :param source: A source node (id or node object)
        :param target: A target node (id or node object, optional)
        :param cut: A maximal distance for search (optional)
        :param output_dict: output structure for retrieved distance

        :return: The distance between source and target nodes If target node is not
            specified, returns a list of distances between source node and all other nodes
            in the network (non-reachable nodes are associated to 1e300 distance).
        """
        # Input format
        source = self.__correctInputNode(source)
        target = self.__correctInputNode(target)
        self.run_routing_forward(source, target, cut=cut, output_dict=output_dict)
        if not target is None:
            return self.NODES[target].poids
        else:
            return [(n[1].poids < 0) * 1e300 + n[1].poids for n in self.NODES.items()]

    def all_shortest_distances(self, cut: float = 1e300,
                               output_dict: dict = None, verbose=False) -> Dict[Tuple[int, int], float]:
        """Computes all shortest distances between pairs of nodes

        The results are saved in a dictionnary `{key=(source, n), value=d}`.

        If output dictionnary structure is provided as input, it is directly incremented
        during the process, otherwise, it is created before begining to search for
        shortest distances.

        Time complexity is :math:`O(n \cdot (n+m) \cdot \log(n))` with :math:`n` the
        number of nodes and :math:`n`  the number of edges. That amounts roughly to
        :math:`O(n^2.log(n))` for a typical planar road  network, and to
        :math:`O(n^3.log(n))` for a general network.

        :param cut: a maximal distance for search (optional)
        :param output_dict: output structure for retrieved distances

        :return: The distances between all pairs of nodes. Nodes separated by a
            distance > `cut` are not registered in the output dictionnary. If
            dictionnary is provided as input it is incremented during the process, hence
            it is possble tocall 'all_shortest_distances' successively with the same
            output dictionnary structure.
        """
        if verbose:
            print("Map-matching preparation...")

        if output_dict is None:
            output_dict = dict()

        to_run = self.getNodesId()
        if verbose:
            to_run = progressbar.progressbar(to_run)

        #print("Computing all pairs shortest distances...")
        for id_source in to_run:
        #for id_source in progressbar.progressbar(self.getNodesId()):
            self.run_routing_forward(id_source, cut=cut, output_dict=output_dict)
        return output_dict

    def run_routing_backward(self, target: Union[int, Node]) -> Union[Track, None]:
        """Computes shortest path between the source node used in forward step
        :func:`run_routing_forward` and any target node.

        If target node has not been reached during forward search, a None object is
        returned by the function.

        :param target: A target node
        :return: A track between the source node specified in
            :func:`run_routing_forward` and a target node. The track contains topologic
            and non-topologic vertices. If the node target has not been reached during
            forward step, None object is output
        """
        target = self.__correctInputNode(target)
        node = self.NODES[target]
        track = Track()
        track.addObs(Obs(node.coord))
        if node.antecedent == "":
            return None
        while (node.poids != 0) and (node.antecedent != ""):
            e = self.EDGES[node.antecedent_edge]
            edge_geom = e.geom.copy()
            if e.source != node:
                edge_geom = edge_geom.reverse()
            track = track + (edge_geom > 1)
            node = node.antecedent
        return track

    def shortest_path( self, source: Union[int, Node], target: Union[int, Node], cut: float = 1e300, output_dict: dict = None) -> Union[Track, None]:
        """Computes shortest path between source and target nodes

        :param source: A source node
        :param target: a target node
        :param cut: a maximal distance for search
        :param output_dict: output structure for retrieved distances

        :return: A track between source and target node. If target is not reachable
            during forward step, None object is output
        """
        self.run_routing_forward(source, target, cut=cut, output_dict=output_dict)
        return self.run_routing_backward(target)

    def distanceBtwPts( self, edge1: int, abs_curv_1: float, edge2: int, abs_curv_2: float) -> float:
        """Distance between 2 points

        Each points being described by:

            - Edge id number
            - Curvilinear abscissa on edge geometry from source

        :param edge1: edge 1 id number
        :param abs_curv_1: curvilinear abscissa on edge 1 geometry from source
        :param edge2: edge 2 id number
        :param abs_curv_2: curvilinear abscissa on edge 2 geometry from source

        :return: Distance between points
        """

        e1 = self.EDGES[self.getEdgeId(edge1)]
        e2 = self.EDGES[self.getEdgeId(edge2)]

        if e1 == e2:
            return abs(abs_curv_1 - abs_curv_2)

        d1s = abs_curv_1
        ds2 = abs_curv_2
        d1t = e1.geom.length() - abs_curv_1
        dt2 = e2.geom.length() - abs_curv_2

        dss = self.prepared_shortest_distance(e1.source.id, e2.source.id)
        dtt = self.prepared_shortest_distance(e1.target.id, e2.target.id)
        dst = self.prepared_shortest_distance(e1.source.id, e2.target.id)
        dts = self.prepared_shortest_distance(e1.target.id, e2.source.id)

        d1 = d1s + dss + ds2
        d2 = d1t + dtt + dt2
        d3 = d1s + dst + dt2
        d4 = d1t + dts + ds2

        return min(min(d1, d2), min(d3, d4))

    def prepare(self, cut: Union[float, None] = 1e300, verbose=False):
        """Precomputes shortest distances between all pairs of nodes and saves the
        result in :attr:`DISTANCES` attribute.

        :param cut: A maximal distance for search
        """
        if self.DISTANCES is None:
            self.DISTANCES = dict()
        self.all_shortest_distances(cut=cut, output_dict=self.DISTANCES, verbose=verbose)

    def has_prepared_shortest_distance(self, source: Union[int, Node], target: Union[int, Node]) -> bool:
        """Tests if a shortest distance has been precomputed

        :param source: A source node
        :param target: A target node
        :return: True if a shortest distance between `source` and `target` has already
            been computed.
        """
        if self.DISTANCES is None:
            print(
                "Error: prepare function must be called before attempting to use preparation"
            )
        if isinstance(source, Node):
            source = source.id
        if isinstance(target, Node):
            target = target.id
        key = (source, target)
        return key in self.DISTANCES

    def prepared_shortest_distance(self, source: Union[int, Node], target: Union[int, Node]) -> float:
        """Finds shortest distance from the precomputation. May be called only after
        :func:`prepare` or :func:`load_prep.`

        :param source: A source node
        :param target: A target node
        :return: Shortest distance between source and targer. Returns 1e300 if shortest
            distance has not been precomputed.

        """
        if self.DISTANCES is None:
            print(
                "Error: prepare function must be called before attempting to use preparation"
            )
        if isinstance(source, Node):
            source = source.id
        if isinstance(target, Node):
            target = target.id
        key = (source, target)
        if key in self.DISTANCES:
            return self.DISTANCES[key]
        else:
            return 1e300

    def save_prep(self, filename: str):
        """Saves DISTANCES attribute in a npy file for further use

        :param filename: Path to save precomputed structure
        """
        if self.DISTANCES is None:
            print(
                "Error: prepare function must be called before attempting to save preparation"
            )
            exit(1)
        np.save(filename, self.DISTANCES)

    def load_prep(self, filename: str):
        """Imports DISTANCES attribute from an npy file

        :param filename: Path where precomputed structure is saved
        """
        if len(filename) < 4:
            filename = filename + ".npy"
        if filename[-4:] != ".npy":
            filename = filename + ".npy"
        self.DISTANCES = read_dictionary = np.load(filename, allow_pickle="TRUE").item()
