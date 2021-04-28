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
        
        
    def test_igast(self):
        
        chemin = 'data/network_igast.csv'
        network = NetworkReader.readFromFile(chemin, 'TEST_UNITAIRE')
        
        self.assertEqual(34, len(network.EDGES))
        self.assertEqual(21, len(network.NODES))
        
        node1 = network.getNode("Bayonne")
        self.assertIsInstance(node1, Node)
        self.assertEqual(1, len(node1.getArcEntrants()))
        self.assertEqual(1, len(node1.getArcSortants()))
        
        node2 = network.getNode('Troyes')
        
        self.assertEqual(978.0, network.shortest_path_distance(node1, node2))
        
        PPC = network.shortest_path(node1, node2)
        self.assertEqual(13, len(PPC))
        
        self.assertIsInstance(PPC[0], Node)
        self.assertIsInstance(PPC[1], Edge)
        self.assertIsInstance(PPC[2], Node)
        
        self.assertEqual(PPC[0].id, 'Troyes')
        self.assertEqual(PPC[2].id, 'Paris')
        self.assertEqual(PPC[4].id, 'Orléans')
        self.assertEqual(PPC[6].id, 'Tours')
        self.assertEqual(PPC[8].id, 'Poitiers')
        self.assertEqual(PPC[10].id, 'Bordeaux')
        self.assertEqual(PPC[12].id, 'Bayonne')
        
        self.assertEqual(PPC[0].distance, 978)
        self.assertEqual(PPC[2].distance, 800)
        self.assertEqual(PPC[4].distance, 668)
        self.assertEqual(PPC[6].distance, 545)
        self.assertEqual(PPC[8].distance, 442)
        self.assertEqual(PPC[10].distance, 185)
        #self.assertEqual(PPC[12].distance, 0)
        
        self.assertEqual(PPC[1].id, '29')
        self.assertEqual(PPC[3].id, '24')
        self.assertEqual(PPC[5].id, '17')
        self.assertEqual(PPC[7].id, '13')
        self.assertEqual(PPC[9].id, '8')
        self.assertEqual(PPC[11].id, '1')
        

if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestDijkstra("test_dijkstra"))
    suite.addTest(TestDijkstra("test_igast"))
    runner = TextTestRunner()
    runner.run(suite)
    