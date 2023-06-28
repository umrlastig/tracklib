# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os.path
from unittest import TestCase, TestSuite, TextTestRunner

#from tracklib.core.Network import Node
from tracklib.core.Bbox import Bbox
from tracklib.core import ObsCoords as Coords
from tracklib.io.NetworkReader import NetworkReader
#from tracklib.io.TrackReader import TrackReader


class TestNetworkReader(TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        self.nomproxy = None #'ENSG'
        
    def test_read_network_error_path(self):
        path = os.path.join(self.resource_path, 'network/network_22245.csv')
        network = NetworkReader.readFromFile(path, formatfile = 'IGN')
        self.assertIsNone(network)
        
    def test_read_network(self):
        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        network = NetworkReader.readFromFile(path, formatfile = 'IGN')
        self.assertEqual(8086, len(network.EDGES), 'Edges number')
        self.assertEqual(5820, len(network.NODES), 'Nodes number')
        network.plot('k-', '', 'g-', 'r-', 0.5, plt)
        plt.legend()
        
        
    def test_read_wfs(self):
        '''
        path = os.path.join(self.resource_path, 'data/gpx/utgtrack-22245_light.gpx')
        tracks = TrackReader.readFromGpx(path)
        trace = tracks.getTrack(0)
        trace.summary()
        
        emprise = trace.bbox()
        proj = "EPSG:4326"
        tolerance=0.0001
        network = NetworkReader.requestFromIgnGeoportail(emprise, proj, margin=0.020, 
                                   tolerance=tolerance, spatialIndex=True)
        if network != None:
            print ('nb edges=', len(network.EDGES))
        else:
            print ('???')
        '''
        
        xmin = 6.74168
        xmax = 6.82568
        ymin = 45.3485
        ymax = 45.4029
        emprise = Bbox(Coords.GeoCoords(xmin, ymin), Coords.GeoCoords(xmax, ymax))

        proj = "EPSG:4326"

        tolerance=0.0001

        # nomproxy='ENSG'
        network = NetworkReader.requestFromIgnGeoportail(emprise, proj, margin=0.020, 
                                   tolerance=tolerance, spatialIndex=True, nomproxy=self.nomproxy)


        network.plot('k-', '', 'g-', 'r-', 0.5, plt)
        #self.assertEqual(235, len(network.EDGES))
        #self.assertEqual(185, len(network.NODES))

        
    #     self.assertEqual(33, len(network.EDGES))
    #     self.assertEqual(32, len(network.NODES))
        
    #     network.plot('k-', '', 'g-', 'r-', 0.5, plt)
    #     # plt.legend()
        
    #     # TRONROUT0000000006441107
    #     # TRONROUT0000000006441115
    #     # TRONROUT0000000006441117
    #     # TRONROUT0000000006441131
    #     # TRONROUT0000000006441146
    #     edge1 = network.getEdge('troncon_de_route.TRONROUT0000000006441146')
    #     plt.plot(edge1.geom.getX(), edge1.geom.getY(), 'g')
        
    #     node1 = network.getNode('8')
    #     plt.scatter(node1.coord.lon, node1.coord.lat, color="blue")
    #     self.assertIsInstance(node1, Node)
    #     self.assertEqual(3, len(network.PREV_EDGES[node1.id]))
    #     self.assertEqual(3, len(network.NEXT_EDGES[node1.id]))
        
    #     node2 = network.getNode('14')
    #     plt.scatter(node2.coord.lon, node2.coord.lat, color="red")
    #     self.assertIsInstance(node2, Node)
    #     self.assertEqual(3, len(network.PREV_EDGES[node2.id]))
    #     self.assertEqual(3, len(network.NEXT_EDGES[node2.id]))
        

    


if __name__ == '__main__':
    suite = TestSuite()
    #suite.addTest(TestNetworkReader("test_read_network_error_path"))
    #suite.addTest(TestNetworkReader("test_read_network"))
    suite.addTest(TestNetworkReader("test_read_wfs"))
    runner = TextTestRunner()
    runner.run(suite)