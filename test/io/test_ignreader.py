# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os.path
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.core.Network import Node, Edge
from tracklib.io.IgnReader import IgnReader


class TestNetworkReader(TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        self.nomproxy = 'ENSG'
        

    def test_read_default(self):

        xmin = 1.88728
        xmax = 1.89542
        ymin = 47.85971
        ymax = 47.86179
        
        network = IgnReader.getNetwork((xmin, xmax, ymin, ymax), None, 0.0, 0.1, 
                                       False, nomproxy = self.nomproxy)
        self.assertEqual(40, len(network.EDGES))
        self.assertEqual(119, len(network.NODES))
        
        network.plot('k-', '', 'g-', 'r-', 0.5, plt)
        plt.legend()
        
        node1 = network.getNode('8')
        plt.scatter(node1.coord.lon, node1.coord.lat, color="blue")
        self.assertIsInstance(node1, Node)
        self.assertEqual(0, len(network.PREV_EDGES[node1.id]))
        self.assertEqual(0, len(network.NEXT_EDGES[node1.id]))
        
        #node2 = network.getNode('15')
        #plt.scatter(node2.coord.lon, node2.coord.lat, color="red")
        #self.assertIsInstance(node2, Node)
        #self.assertEqual(2, len(network.PREV_EDGES[node2.id]))
        #self.assertEqual(2, len(network.NEXT_EDGES[node2.id]))


if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestNetworkReader("test_read_default"))
    runner = TextTestRunner()
    runner.run(suite)