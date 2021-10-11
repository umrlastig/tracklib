"""
This module contaions the class to manage Network
"""

import random
import progressbar
import numpy as np
import matplotlib.pyplot as plt

import tracklib.algo.Simplification as Simplification

from tracklib.core.Obs import Obs
from tracklib.core.Track import Track
from tracklib.core.Utils import priority_dict
from tracklib.core.TrackCollection import TrackCollection


class Node:
    def __init__(self, id, coord):
        self.id = id
        self.coord = coord

    def __str__(self):
        return "Node object: " + str(self.id)

    def __lt__(self, other):
        if isinstance(other, Node):
            return self.id < other.id
        return False

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def distanceTo(self, node):
        return self.coord.distanceTo(node.coord)

    def distance2DTo(self, node):
        return self.coord.distance2DTo(node.coord)

    def plot(self, sym="r+"):
        plt.plot(self.coord.getX(), self.coord.getY(), sym)


class Edge:

    DOUBLE_SENS = 0
    SENS_DIRECT = 1
    SENS_INVERSE = -1

    def __init__(self, id, track):
        self.id = id
        self.geom = track

        self.source = None
        self.target = None
        self.orientation = 0
        self.weight = 0

    def plot(self, sym="k-"):
        self.geom.plot(sym)

    def __str__(self):
        return "Edge #" + str(self.id)


class Network:

    # Routing modes
    ROUTING_ALGO_DIJKSTRA = 0
    ROUTING_ALGO_ASTAR = 1

    # Analytical features
    AF_LINK = "#link"
    AF_WEIGHT = "#weight"

    def __init__(self):
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
        if not self.spatial_index is None:
            self.spatial_index.addFeature(edge.geom, self.getNumberOfEdges() - 1)

    def __iter__(self):
        yield from [l[1] for l in list(self.EDGES.items())]

    def size(self):
        return len(self.EDGES)

    def getIndexNodes(self):
        return self.__idx_nodes

    def setRoutingMethod(self, method: int):
        """Define the routing algorithm

        :param method: Algorithm of routing. Two values are possible :

            - ROUTING_ALGO_DIJKSTRA (*mode=0*) [default]
            - ROUTING_ALGO_ASTAR (*mode=1*). 
            **NB:** A* is an efficient approximate version of Dijkstra. It returns 
            exact solution under theoretical assumptions on the metrics used to set 
            weights on graph edges.

        """
        self.routing_mode = method

    def setAStarWeight(self, weight):
        self.astar_wgt = weight

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

    def getSRID(self):
        return self.EDGES[self.__idx_edges[0]].geom.getSRID()

    def totalLength(self):
        count = 0
        for id in self.__idx_edges:
            count += self.EDGES[id].geom.length()
        return count

    def simplify(self, tolerance, mode=1):
        for id in self.__idx_edges:
            self.EDGES[id].geom = Simplification.simplify(
                self.EDGES[id].geom, tolerance, mode
            )

    # ------------------------------------------------------------
    # Spatial index creation, export and import functions
    # ------------------------------------------------------------

    def createSpatialIndex(self, resolution=None, margin=0.05, verbose=True):
        from tracklib.core.SpatialIndex import SpatialIndex

        self.spatial_index = SpatialIndex(self, resolution, margin, verbose)

    def exportSpatialIndex(self, filename):
        from tracklib.core.SpatialIndex import SpatialIndex

        self.spatial_index.save(filename)

    def importSpatialIndex(self, filename):
        from tracklib.core.SpatialIndex import SpatialIndex

        self.spatial_index = SpatialIndex.load(filename)

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

    def getNumberOfVertices(self):
        count = 0
        for id in self.__idx_edges:
            count += self.EDGES[id].geom.size()
        return count

    def getNodeId(self, n):
        return self.__idx_nodes[n]

    def getEdgeId(self, n):
        return self.__idx_edges[n]

    def getNodesId(self):
        return [l[0] for l in list(self.NODES.items())]

    def getEdgesId(self):
        return [l[0] for l in list(self.EDGES.items())]

    def getRandomNode(self):
        return self.getNode(
            self.getNodesId()[random.randint(0, self.getNumberOfNodes() - 1)]
        )

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

    def bbox(self):
        return self.getAllEdgeGeoms().bbox()

    # ------------------------------------------------------------
    # Graphics
    # ------------------------------------------------------------
    def plot(
        self, edges="k-", nodes="", direct="k--", indirect="k--", size=0.5, append=plt
    ):

        """

        Parameters
        ----------
        edges : TYPE, optional
            DESCRIPTION. The default is 'k-'.
        nodes : TYPE, optional
            DESCRIPTION. The default is ''.
        direct : TYPE, optional
            DESCRIPTION. The default is 'k--'.
        indirect : TYPE, optional
            DESCRIPTION. The default is 'k--'.
        size : TYPE, optional
            DESCRIPTION. The default is 0.5.
        append : TYPE, optional
            DESCRIPTION. The default is plt.

        Returns
        -------
        None.

        """

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
                if edge.orientation == Edge.DOUBLE_SENS:
                    x1b.append(edge.geom.getX()[j])
                    x2b.append(edge.geom.getX()[j + 1])
                    y1b.append(edge.geom.getY()[j])
                    y2b.append(edge.geom.getY()[j + 1])
                else:
                    if edge.orientation == Edge.SENS_DIRECT:
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
            append.plot(exb, eyb, edges, linewidth=size, label="double sens")
        if len(direct) > 0:
            append.plot(exd, eyd, direct, linewidth=size, label="direct")
        if len(indirect) > 0:
            append.plot(exi, eyi, indirect, linewidth=size, label="indirect")
        if len(nodes) > 0:
            append.plot(nx, ny, nodes, markersize=4 * size)

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
        if isinstance(node, Node):
            return node.id
        return node

    # ------------------------------------------------------------
    # sub_network: extracts sub-network from routing forward
    # search. An edge is added to the output network if both
    # its ends have been visited during the search process
    # (TOPOGRAPHIC mode) or if one of its ends are located in
    # a circle centered on source with radius = cut
    # ------------------------------------------------------------
    # Inputs:
    #  - source:    a source node (id or node object) or a coord
    #  - cut   :    a maximal distance for search
    #  - mode  :    "TOPOLOGIC" (default) or "GEOMETRIC"
    # ------------------------------------------------------------
    # Output: a network containing only visited nodes reachable
    # from source with a cost lower than cut distance.
    # ------------------------------------------------------------
    def sub_network(self, source, cut, mode="TOPOLOGIC", verbose=True):
        if mode == "TOPOLOGIC":
            self.run_routing_forward(source, cut=cut)
            return self.__sub_network_routing(verbose)
        if mode == "GEOMETRIC":
            return self.__sub_network_geometric(source, cut, verbose)
        print("Error: unknown network extraction mode: ", mode)
        exit(1)

    def __sub_network_routing(self, verbose):
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

    def __sub_network_geometric(self, source, cut, verbose):
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

    # ------------------------------------------------------------
    # Internal function to call before dijkstra forward step
    # ------------------------------------------------------------
    def __resetFlags(self):
        for elem in self.NODES.items():
            elem[1].poids = -1
            elem[1].visite = False
            elem[1].antecedent = ""
            elem[1].antecedent_edge = ""

    # ------------------------------------------------------------
    # Executes forward pass of routing algorithm to find
    # shortest distance between source node and all other nodes in
    # graph. Execution may be stopped prematurely by specifying
    # target node and/or cut distance. For each nodes reached
    # (with a distance d < cut) during the search process, an
    # entry {key=(source, n), value=d} is added to an output
    # dictionnary (if specified as input)
    # ------------------------------------------------------------
    # Inputs:
    #  - source      : a source node (id or node object)
    #  - target      : a target node (id or node object, optional)
    #  - cut         : a maximal distance for search (optional)
    #  - output_dict : output structure for retrieved distances
    # ------------------------------------------------------------
    # Output: none (flags modified in node objects)
    # ------------------------------------------------------------
    def run_routing_forward(self, source, target=None, cut=1e300, output_dict=None):

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

    # ------------------------------------------------------------
    # Shortest_distance: finds shortest distance between source
    # node and either a target node or a list of target nodes.
    # In every case, time complexity is O((n+m).log(n)) with
    # n the number of node and m the number of edges. That
    # amounts roughly to O(n.log(n)) for a typical planar road
    # network, and to O(n^2.log(n)) for a general network.
    # ------------------------------------------------------------
    # Inputs:
    #  - source      : a source node (id or node object)
    #  - target      : a target node (id or node object, optional)
    #  - cut         : a maximal distance for search (optional)
    #  - output_dict : output structure for retrieved distances
    # ------------------------------------------------------------
    # Output: the (float) distance between source and target nodes
    # If target node is not specified, returns a list of distances
    # between source node and all other nodes in the network (non-
    # reachable nodes are associated to 1e300 distance).
    # ------------------------------------------------------------
    def shortest_distance(self, source, target=None, cut=1e300, output_dict=None):
        # Input format
        source = self.__correctInputNode(source)
        target = self.__correctInputNode(target)
        self.run_routing_forward(source, target, cut=cut, output_dict=output_dict)
        if not target is None:
            return self.NODES[target].poids
        else:
            return [(n[1].poids < 0) * 1e300 + n[1].poids for n in self.NODES.items()]

    # ------------------------------------------------------------
    # Computes all shortest distances between pairs of nodes and
    # saves results in a dictionnary {key=(source, n), value=d}.
    # If output dictionnary structure is provided as input, it is
    # directly incremented during the process, otherwise, it is
    # created before begining to search for shortest distances.
    # Time complexity is O(n.(n+m).log(n)) with n the number of
    # nodes and m the number of edges. That amounts roughly to
    # O(n^2.log(n)) for a typical planar road network, and to
    # O(n^3.log(n)) for a general network.
    # ------------------------------------------------------------
    # Inputs:
    #  - cut         : a maximal distance for search (optional)
    #  - output_dict : output structure for retrieved distances
    # ------------------------------------------------------------
    # Output: the (float) distances between all pairs of nodes.
    # Nodes separated by a distance > cut are not registered in
    # the output dictionnary. If dictionnary is provided as input
    # it is incremented during the process, hence it is possble to
    # call 'all_shortest_distances' successively with the same
    # output dictionnary structure.
    # ------------------------------------------------------------
    def all_shortest_distances(self, cut=1e300, output_dict=None):
        print("Computing all pairs shortest distances...")
        if output_dict is None:
            output_dict = dict()
        for id_source in progressbar.progressbar(self.getNodesId()):
            self.run_routing_forward(id_source, cut=cut, output_dict=output_dict)
        return output_dict

    # ------------------------------------------------------------
    # Computes shortest path between the source node used in
    # forward step 'run_routing_forward' and any target node. If
    # target node has not been reached during forward search, a
    # None object is returned by the function.
    # ------------------------------------------------------------
    # Inputs:
    #  - target      : a target node (id or node object)
    # ------------------------------------------------------------
    # Output: a track between the source node specified in
    # 'run_routing_forward" and a target node. The track contains
    # topologic and non-topologic vertices. If the node target has
    # not been reached during forward step, None object is output
    # ------------------------------------------------------------
    def run_routing_backward(self, target):
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

    # ------------------------------------------------------------
    # Computes shortest path between source and target nodes
    # ------------------------------------------------------------
    # Inputs:
    #  - source      : a source node (id or node object)
    #  - target      : a target node (id or node object, optional)
    #  - cut         : a maximal distance for search (optional)
    #  - output_dict : output structure for retrieved distances
    # ------------------------------------------------------------
    # Output: a track between source and target node. If target is
    # not reachable during forward step, None object is output
    # ------------------------------------------------------------
    def shortest_path(self, source, target, cut=1e300, output_dict=None):
        self.run_routing_forward(source, target, cut=cut, output_dict=output_dict)
        return self.run_routing_backward(target)

    # ------------------------------------------------------------
    # Distance between 2 points, each points being described by:
    #    - edge id number
    #    - curvilinear abscissa on edge geometry from source
    # ------------------------------------------------------------
    def distanceBtwPts(self, edge1, abs_curv_1, edge2, abs_curv_2):

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

    # ------------------------------------------------------------
    # Precomputes shortest distances between all pairs of nodes
    # and saves the result in DISTANCES attribute.
    # ------------------------------------------------------------
    # Inputs:
    #  - cut         : a maximal distance for search (optional)
    # ------------------------------------------------------------
    # Output: none, DISTANCES attribute is built or updated
    # ------------------------------------------------------------
    def prepare(self, cut=1e300):
        if self.DISTANCES is None:
            self.DISTANCES = dict()
        self.all_shortest_distances(cut=cut, output_dict=self.DISTANCES)

    # ------------------------------------------------------------
    # Tests if a shortest distance has been precomputed
    # ------------------------------------------------------------
    # Inputs:
    #  - source      : a source node (id or node object)
    #  - target      : a target node (id or node object, optional)
    # ------------------------------------------------------------
    # Output: true if a shortest distance between source and
    # target has already been computed.
    # ------------------------------------------------------------
    def has_prepared_shortest_distance(self, source, target):
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

    # ------------------------------------------------------------
    # Finds shortest distance from the precomputation. May be
    # called only after prepare or load_prep.
    # ------------------------------------------------------------
    # Inputs:
    #  - source      : a source node (id or node object)
    #  - target      : a target node (id or node object, optional)
    # ------------------------------------------------------------
    # Output: shortest distance between source and targer. Returns
    # 1e300 if shortest distance has not been precomputed.
    # ------------------------------------------------------------
    def prepared_shortest_distance(self, source, target):
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

    # ------------------------------------------------------------
    # Saves DISTANCES attribute in a npy file for further use
    # ------------------------------------------------------------
    # Inputs:
    #  - filename      : path to save precomputed structure
    # ------------------------------------------------------------
    def save_prep(self, filename):
        if self.DISTANCES is None:
            print(
                "Error: prepare function must be called before attempting to save preparation"
            )
            exit(1)
        np.save(filename, self.DISTANCES)

    # ------------------------------------------------------------
    # Imports DISTANCES attribute from an npy file
    # ------------------------------------------------------------
    # Inputs:
    #  - filename      : path where precomputed structure is saved
    # ------------------------------------------------------------
    def load_prep(self, filename):
        if len(filename) < 4:
            filename = filename + ".npy"
        if filename[:-4] != ".npy":
            filename = filename + ".npy"
        self.DISTANCES = read_dictionary = np.load(filename, allow_pickle="TRUE").item()
