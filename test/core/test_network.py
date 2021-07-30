# -*- coding: utf-8 -*-

import os.path
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.core.Track import Track
from tracklib.core.Network import Node, Edge
from tracklib.io.NetworkReader import NetworkReader
from tracklib.io.IgnReader import IgnReader

import matplotlib.pyplot as plt

class TestDijkstra(TestCase):
    
    __epsilon = 0.001
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
    
    #chemin = '../../data/network_ecrin.wkt'
    #network = NetworkReader.readFromFile(chemin, 'TEST1')

    def test_bdtopo(self):
        
        xmin = 6.11779213241985538
        xmax = 6.12425230208879839
        ymin = 44.985438233863199
        ymax = 44.99425829041950919
        
        xmin = 2.34850
        xmax = 2.35463
        ymin = 48.83896
        ymax = 48.84299
        
        network = IgnReader.getNetwork((xmin, ymin, xmax, ymax), None)
        self.assertEqual(107, len(network.EDGES))
        self.assertEqual(78, len(network.NODES))
        
        network.plot('k-', '', 'g-', 'r-', 0.5, plt)
        #plt.legend()
        
        node1 = network.getNode('8')
        plt.scatter(node1.coord.E, node1.coord.N, color="blue")
        self.assertIsInstance(node1, Node)
        self.assertEqual(1, len(network.PREV_EDGES[node1.id]))
        self.assertEqual(2, len(network.NEXT_EDGES[node1.id]))
        
        node2 = network.getNode('12')
        plt.scatter(node2.coord.E, node2.coord.N, color="red")
        self.assertEqual(1, len(network.PREV_EDGES[node2.id]))
        self.assertEqual(2, len(network.NEXT_EDGES[node2.id]))
        self.assertIsInstance(node2, Node)
        
        trace = network.shortest_path(node1, node2)
        plt.plot(trace.getX(), trace.getY(), 'b-')

        self.assertLessEqual((73.0961 - trace.length()), self.__epsilon, "len pcc")
        self.assertEqual(3, trace.size())

        #        
        trace = network.shortest_path(node1, node2, 25)
        self.assertIsNone(trace, 'Pas de trace inférieure à 50')
        
        #
        DIST = network.shortest_distance(node1)
        self.assertLessEqual((272.5967 - DIST[13]), self.__epsilon, "len pcc")
        self.assertLessEqual((0.0 - DIST[11]), self.__epsilon, "len pcc")
        self.assertEqual (len(network.NODES), len(DIST), 'matrix')
        
        
        
    
    def test_dijkstra_bdtopo(self):
        
        chemin = os.path.join(self.resource_path, 'data/network/network_ecrin_extrait.csv')
        network = NetworkReader.readFromFile(chemin, 'TEST2', False)
        
        self.assertEqual(890, len(network.EDGES))
        self.assertEqual(738, len(network.NODES))
        
        node1 = network.getNode('69715')
        node2 = network.getNode('94047')
        
        trace = network.shortest_path(node1, node2)
        self.assertEqual(trace.size(), 1122)   # 38
        
    
    def test_dijkstra(self):
        
        chemin = os.path.join(self.resource_path, 'data/network/network_test.csv')
        network = NetworkReader.readFromFile(chemin, 'TEST_UNITAIRE', False)
        network.plot()
        # Il y a des poids !!!
        
        self.assertEqual(8, len(network.EDGES))
        self.assertEqual(6, len(network.NODES))
        
        edge3 = network.getEdge('3')
        self.assertIsInstance(edge3, Edge)
        
        node0 = network.getNode('0')
        self.assertIsInstance(node0, Node)
        self.assertEqual(0, len(network.PREV_EDGES[node0.id]))
        self.assertEqual(3, len(network.NEXT_EDGES[node0.id]))
        
        node3 = network.getNode('3')
        self.assertEqual('3', node3.id)
        self.assertIsInstance(node3, Node)
        self.assertEqual(3, len(network.PREV_EDGES[node3.id]))
        self.assertEqual(0, len(network.NEXT_EDGES[node3.id]))
        
        node5 = network.getNode('5')
        self.assertIsInstance(node5, Node)
        self.assertEqual(1, len(network.PREV_EDGES[node5.id]))
        self.assertEqual(2, len(network.NEXT_EDGES[node5.id]))
        
        trace = network.shortest_path(node0, node3)
        self.assertIsInstance(trace, Track)
        self.assertEqual(trace.size(), 3)
        
        trace = network.shortest_path(node5, node3)
        self.assertIsInstance(trace, Track)
        self.assertEqual(trace.size(), 2)
        
        trace = network.shortest_path(node0, node5)
        self.assertIsInstance(trace, Track)
        self.assertEqual(trace.size(), 4)
        
        node4 = network.getNode('4')
        trace = network.shortest_path(node0, node4)
        self.assertIsInstance(trace, Track)
        self.assertEqual(trace.size(), 3)
        
        
    def test_igast(self):
        
        chemin = os.path.join(self.resource_path, 'data/network/network_igast.csv')
        network = NetworkReader.readFromFile(chemin, 'TEST_UNITAIRE', False)
        network.plot()
        
        self.assertEqual(34, len(network.EDGES))
        self.assertEqual(21, len(network.NODES))
        
        node1 = network.getNode("Bayonne")
        self.assertIsInstance(node1, Node)
        self.assertEqual(2, len(network.NEXT_EDGES[node1.id]))
        self.assertEqual(2, len(network.PREV_EDGES[node1.id]))
        
        node2 = network.getNode('Troyes')
        
        distance = network.shortest_distance(node1, node2)
        self.assertEqual(978.0, distance)
        
        trace = network.shortest_path(node1, node2)
        self.assertEqual(7, trace.size())
        
        #self.assertEqual(PPC[0].id, 'Troyes')
        #self.assertEqual(PPC[2].id, 'Paris')
        #self.assertEqual(PPC[4].id, 'Orléans')
        #self.assertEqual(PPC[6].id, 'Tours')
        #self.assertEqual(PPC[8].id, 'Poitiers')
        #self.assertEqual(PPC[10].id, 'Bordeaux')
        #self.assertEqual(PPC[12].id, 'Bayonne')
        


        

if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestDijkstra("test_dijkstra"))
    suite.addTest(TestDijkstra("test_igast"))
    suite.addTest(TestDijkstra("test_dijkstra_bdtopo"))
    suite.addTest(TestDijkstra("test_bdtopo"))
    runner = TextTestRunner()
    runner.run(suite)
    
