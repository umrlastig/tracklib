# -*- coding: utf-8 -*-

import os.path
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.core.Track import Track
from tracklib.core.Network import Node
from tracklib.io.NetworkReader import NetworkReader
from tracklib.io.IgnReader import IgnReader


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
        
        proj = "EPSG:2154"
    
        network = IgnReader.getNetwork((xmin, ymin, xmax, ymax), proj)
        self.assertEqual(107, len(network.EDGES))
        self.assertEqual(78, len(network.NODES))
        
        node1 = network.getNode('5')
        node2 = network.getNode('7')
        print ('\n', node1.coord)
        print (node2.coord, '\n')
        network.plot('k-', 'ob')
        
        trace = network.shortest_path(node1, node2)
        print (trace)
        #self.assertLessEqual((523.2339 - trace.length()), self.__epsilon, "len pcc")
        # #self.assertEqual(40, trace.size())
        # self.assertLessEqual((65.58062 - trace.getObsAnalyticalFeature(Network.AF_WEIGHT, 0)), self.__epsilon, "len pcc")
        # #network.plot(trace, node1, node2)
        # #print (trace.summary())
        # # Distance du ppc
        # self.assertLessEqual((523.77046 - network.shortest_path_distance(node1, node2)), self.__epsilon, "len pcc")

        # #        
        # trace = network.shortest_path(node1, node2, 250)
        # self.assertLessEqual((0 - trace.length()), self.__epsilon, "len pcc")
        # self.assertEqual(0, trace.size())
        
        # #
        # self.assertIsNone(network.shortest_path_distance(node1, node2, 250))
        
        # #
        # trace = network.shortest_path(node1, node2)
        # self.assertLessEqual((523.23394 - trace.length()), self.__epsilon, "len pcc")
        # DIST = network.shortest_path_distances(node1)
        # self.assertEqual (65, len(DIST), 'matrix')

        
        # #
        # node3 = network.getNode('75')
        # trace = network.shortest_path(node3, node2)
        # DIST = network.shortest_path_distances(node3)
        # self.assertEqual (62, len(DIST), 'matrix')
        
        
        # #
        # network.shortest_path(node1, node2)
        # DIST = network.shortest_path_distances(node1, 250)
        # self.assertEqual (17, len(DIST), 'matrix')
        
        # # 
        # network.shortest_path(node1, node2, 250)
        # DIST = network.shortest_path_distances(node1)
        # self.assertEqual (17, len(DIST), 'matrix')
        
        
        # #
        # MATRIX = network.shortest_path_all_distances(node1)
        # self.assertEqual (68, len(MATRIX), 'matrix')
        
        # MATRIX = network.shortest_path_all_distances(node1, 250)
        # self.assertEqual (17, len(MATRIX), 'matrix')
        
    
    def test_dijkstra_bdtopo(self):
        
        chemin = os.path.join(self.resource_path, 'data/network/network_ecrin_extrait.csv')
        network = NetworkReader.readFromFile(chemin, 'TEST2')
        
        self.assertEqual(890, len(network.EDGES))
        self.assertEqual(738, len(network.NODES))
        
        node1 = network.getNode('69715')
        node2 = network.getNode('94047')
        
        trace = network.shortest_path(node1, node2)
        self.assertEqual(trace.size(), 1122)   # 38
        
    
    def test_dijkstra(self):
        
        chemin = os.path.join(self.resource_path, 'data/network/network_test.csv')
        network = NetworkReader.readFromFile(chemin, 'TEST_UNITAIRE')
        
        self.assertEqual(8, len(network.EDGES))
        self.assertEqual(6, len(network.NODES))
        
        node0 = network.getNode('0')
        self.assertIsInstance(node0, Node)
        self.assertEqual(0, len(network.PREV_EDGES[node0.id]))
        self.assertEqual(3, len(network.NEXT_EDGES[node0.id]))
        
        node3 = network.getNode('3')
        self.assertIsInstance(node3, Node)
        self.assertEqual(3, len(network.PREV_EDGES[node3.id]))
        self.assertEqual(0, len(network.NEXT_EDGES[node3.id]))
        
        node5 = network.getNode('5')
        self.assertIsInstance(node5, Node)
        self.assertEqual(1, len(network.PREV_EDGES[node5.id]))
        self.assertEqual(2, len(network.NEXT_EDGES[node5.id]))
        
        trace = network.shortest_path(node0, node3)
        self.assertIsInstance(trace, Track)
        self.assertEqual(trace.size(), 3)  # 4
        
        #DISTS = trace.getAnalyticalFeature(Network.AF_WEIGHT)
        #self.assertEqual(DISTS[0], 0)
        #self.assertEqual(DISTS[1], 6.0)
        #self.assertEqual(DISTS[2], 17.0)
        #self.assertEqual(DISTS[3], 20.0)

        
    def test_igast(self):
        
        chemin = os.path.join(self.resource_path, 'data/network/network_igast.csv')
        network = NetworkReader.readFromFile(chemin, 'TEST_UNITAIRE')
        
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
        
#        DISTS = trace.getAnalyticalFeature(Network.AF_WEIGHT)
        #self.assertEqual(DISTS[6], 442.0)  # 978
        #self.assertEqual(DISTS[5], 800)
        #self.assertEqual(DISTS[4], 668)
        #self.assertEqual(DISTS[3], 545)
        #self.assertEqual(DISTS[2], 442)
        #self.assertEqual(DISTS[1], 185)
        #self.assertEqual(DISTS[0], 370)


        

if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestDijkstra("test_dijkstra"))
    suite.addTest(TestDijkstra("test_igast"))
    suite.addTest(TestDijkstra("test_dijkstra_bdtopo"))
    suite.addTest(TestDijkstra("test_bdtopo"))
    runner = TextTestRunner()
    runner.run(suite)
    
