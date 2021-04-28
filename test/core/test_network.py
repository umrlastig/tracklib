# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.io.NetworkReader import NetworkReader
from tracklib.core.Network import Node, Edge


class TestDijkstra(TestCase):
    
    #chemin = '../../data/network_ecrin.wkt'
    #network = NetworkReader.readFromFile(chemin, 'TEST1')

    #chemin = '../../data/network_ecrin_extrait.csv'
    #network = NetworkReader.readFromFile(chemin, 'TEST2')
    
    def test_dijkstra(self):
        
        chemin = 'data/network_test.csv'
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
        
        PPC = node0.plusCourtChemin(node5)
        for i in range(len(PPC)):
            elt = PPC[i]
            if isinstance(elt, Node):
                print ('noeud' + elt.id + ',' + str(elt.distance))
            if isinstance(elt, Edge):
                print ('arc' + elt.id)
        
        #print (len(PPC))
        

if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestDijkstra("test_dijkstra"))
    runner = TextTestRunner()
    runner.run(suite)