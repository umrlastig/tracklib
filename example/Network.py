import os
import sys
import math
import random
import numpy as np
import matplotlib.pyplot as plt

from tracklib.core.Operator import Operator
from tracklib.io.FileReader import FileReader
from tracklib.io.FileWriter import FileWriter
from tracklib.core.GPSTime import GPSTime
from tracklib.core.Track import Track
from tracklib.core.Coords import ECEFCoords
from tracklib.core.Coords import GeoCoords
from tracklib.core.Coords import ENUCoords

from tracklib.algo.Selection import TrackConstraint
import tracklib.algo.Stochastics as Stochastics
import tracklib.algo.Synthetics as Synthetics
import tracklib.algo.Geometrics as Geometrics
import tracklib.algo.Comparison as Comparison
import tracklib.algo.Cinematics as Cinematics
import tracklib.algo.Dynamics as Dynamics
import tracklib.algo.Interpolation as Interpolation
import tracklib.algo.Simplification as Simplification
import tracklib.algo.Segmentation as Segmentation
import tracklib.algo.Mapping as Mapping
import tracklib.algo.Filtering as Filtering
from tracklib.algo.Dynamics import Kalman

from tracklib.io.KmlWriter import KmlWriter
from tracklib.core.Coords import ENUCoords

from tracklib.io.GpxWriter import GpxWriter
from tracklib.io.GpxReader import GpxReader
from tracklib.core.TrackCollection import TrackCollection
from tracklib.core.Kernel import DiracKernel
from tracklib.core.Kernel import GaussianKernel
from tracklib.core.Kernel import ExponentialKernel
from tracklib.core.Kernel import ExperimentalKernel

from tracklib.core.Obs import Obs
import tracklib.core.Plot as Plot
from tracklib.core.Network import Node
from tracklib.core.Network import Edge
from tracklib.core.Network import Network
from tracklib.io.NetworkReader import NetworkReader

# -----------------------------------------------------------------------
# Example 0: basic usage of network object. Needs 'Ecrin' dataset
# -----------------------------------------------------------------------
# Load network data, display basic information about network, selects 
# random nodes and computes shortest distance and shortest path between 
# them, plot network and results.
# -----------------------------------------------------------------------
def example0():

    Stochastics.seed(8)
	
    # Reading network from text data file
    network = NetworkReader.readFromFile('tracklib/data/network/network_ecrin_extrait.csv', 'TEST2')

    # Basic info display
    print('------------------------------')
    print('Number of nodes =', network.getNumberOfNodes())
    print('Number of edges =', network.getNumberOfEdges())
    print('Number of vertices =', network.getNumberOfVertices())
    print('------------------------------')
    print('SRID = ', network.getSRID())
    print('Total length =', '{:4.1f}'.format(network.totalLength()*1e-3) +" km")
    print('------------------------------\n')	


    # Basic routing operations
    print('--------------------------------------------------------')
    node1 = network.getRandomNode()
    node2 = network.getRandomNode()
    print(node1, "->", node2)
    dist = network.shortest_distance(node1, node2)
    track = network.shortest_path(node1, node2)
    print('Shortest distance between nodes: ' + str(dist))
    print('Shortest path length between nodes: ' + str(track.length()))
    print('--------------------------------------------------------')


    # Plot operations
    network.plot()
    track.plot('r-')
    node1.plot('bs')
    node2.plot('bs')
    plt.show()


    





# -----------------------------------------------------------------------
# Example 1: advanced usage of network object. Needs 'Ecrin' dataset
# -----------------------------------------------------------------------
# Get all shortest paths from one node to all other nodes
# -----------------------------------------------------------------------
def example1():

    Stochastics.seed(8)
	
    # Reading network from text data file
    network = NetworkReader.readFromFile('tracklib/data/network/network_ecrin_extrait.csv', 'TEST2')

    node = network.getRandomNode()

    # Distance bfrom 1 node in 10 km around
    network.shortest_distance(node, cut=1e4)
    net = network.sub_network()   # Get searched area
	
	# Douglas-Peucker
    network.simplify(5)
	
    # Plot operations
    network.plot()
    net.plot('r-')
    node.plot('bs')
    plt.show()
	
# -----------------------------------------------------------------------
# Example 1: advanced usage of network object. Needs 'Ecrin' dataset
# -----------------------------------------------------------------------
# Precompute results, save them for further usage
# -----------------------------------------------------------------------
def example2():

    Stochastics.seed(8)
	
    # Reading network from text data file
    network = NetworkReader.readFromFile('tracklib/data/network/network_ecrin_extrait.csv', 'TEST2')
    
	# Get distance between two nodes
    node1 = network.getRandomNode()
    node2 = network.getRandomNode()
    node3 = network.getRandomNode()
    d12 = network.shortest_distance(node1, node2)
    d23 = network.shortest_distance(node2, node3)
    print("Shortest distance [1-2] = ", d12)
    print("Shortest distance [2-3] = ", d23)
	
    # Precompute distances
    network.prepare(cut=1e4)    
	
    # Saving precomputation
    network.save_prep('precomputation')
	
    # Loading precomputation
    network.load_prep('precomputation')
	
    # Using precomputation
    d12 = network.prepared_shortest_distance(node1, node2)	
    d23 = network.prepared_shortest_distance(node2, node3)
    print("Precomputed shortest distance [1-2] = ", d12)
    print("Precomputed shortest distance [2-3] = ", d23)
	
# -----------------------------------------------------------------------
# Example 3: advanced usage of network object. Needs 'Ecrin' dataset
# -----------------------------------------------------------------------
# Convert SRID and export data in kml
# -----------------------------------------------------------------------
def example3():

    Stochastics.seed(1)
	
    # Reading network from text data file
    network = NetworkReader.readFromFile('tracklib/data/network/network_ecrin_extrait.csv', 'TEST2')
    
    # Cartographic Conversion
    network.toGeoCoords(2154)	
	
	# Get distance between pairs of nodes
    tracks = TrackCollection()
    for i in range(10):
        node1 = network.getRandomNode()
        node2 = network.getRandomNode()
        track = network.shortest_path(node1, node2)
        if not track is None:
            tracks.addTrack(track)
            print(node1, node2, track.size(), track.length())

    # Export
    KmlWriter.writeToKml(network, path='network.kml', c1=[1,1,1,1])   # white network
    KmlWriter.writeToKml(tracks,  path='tracks.kml',  c1=[1,0,0,1])   # red paths