# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.io.NetworkReader import NetworkReader
from tracklib.core.Network import Node


class TestDijkstra(TestCase):
    
    def test_dijkstra(self):
        chemin = '../data/network_test.csv'
        network = NetworkReader.readFromFile(chemin, 'TEST_UNITAIRE')
        
        #self.assertEqual(sumPlot[0][7][0], 1)
        self.assertEqual(8, len(network.EDGES))
        self.assertEqual(6, len(network.NODES))

        node0 = network.getNode('0')
        self.assertIsInstance(node0, Node)
        self.assertEqual(0, len(node0.getArcEntrants()))
        self.assertEqual(3, len(node0.getArcSortants()))
        
        node3 = network.getNode('3')
        self.assertIsInstance(node3, Node)
        self.assertEqual(3, len(node3.getArcEntrants()))
        self.assertEqual(0, len(node3.getArcSortants()))
        
        node5 = network.getNode('5')
        self.assertIsInstance(node5, Node)
        self.assertEqual(1, len(node5.getArcEntrants()))
        self.assertEqual(2, len(node5.getArcSortants()))
        
        node0.plusCourtChemin(node5)
        

if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestDijkstra("test_dijkstra"))
    runner = TextTestRunner()
    runner.run(suite)