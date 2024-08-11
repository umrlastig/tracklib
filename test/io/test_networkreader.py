# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os.path
from unittest import TestCase, TestSuite, TextTestRunner
from tracklib import (Bbox, NetworkReader, GeoCoords,
                      WrongArgumentError, Network, NetworkFormat,
                      TrackReader, ObsTime)


class TestNetworkReader(TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        self.nomproxy = None #'ENSG'

    def test_read_network_error_param(self):

        # ---------------------------------------------------------------------
        # Test exception if the first parameter is not a filepath

        path = os.path.join(self.resource_path, 'network/network_22245.csv')
        self.assertRaises(WrongArgumentError, NetworkReader.readFromFile, path, None)

        path = os.path.join(self.resource_path, '/home/network/')
        self.assertRaises(WrongArgumentError, NetworkReader.readFromFile, path, None)

        # ---------------------------------------------------------------------
        #
        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        self.assertRaises(WrongArgumentError, NetworkReader.readFromFile, path, None)

        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        self.assertRaises(WrongArgumentError, NetworkReader.readFromFile, path, 3)

        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        self.assertRaises(WrongArgumentError, NetworkReader.readFromFile, path, Network())

        # ---------------------------------------------------------------------
        #
        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        self.assertRaises(WrongArgumentError, NetworkReader.readFromFile, path, NetworkFormat())

        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        self.assertRaises(WrongArgumentError, NetworkReader.readFromFile, path, NetworkFormat({
            "pos_edge_id": 1}))

        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        self.assertRaises(WrongArgumentError, NetworkReader.readFromFile, path, NetworkFormat({
            "pos_edge_id": 1, "pos_source": 2}))

        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        self.assertRaises(WrongArgumentError, NetworkReader.readFromFile, path, NetworkFormat({
            "pos_edge_id": 1, "pos_source": 2, "pos_target": 3}))

        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        self.assertRaises(WrongArgumentError, NetworkReader.readFromFile, path, NetworkFormat({
            "pos_edge_id": 1, "pos_source": 2, "pos_target": 3, "separator": ""}))

        # ---------------------------------------------------------------------
        #
        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        fmt = NetworkFormat()
        fmt.pos_edge_id = 1
        self.assertRaises(WrongArgumentError, NetworkReader.readFromFile, path, fmt)

        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        fmt = NetworkFormat()
        fmt.pos_edge_id = 1
        fmt.pos_source = 3
        self.assertRaises(WrongArgumentError, NetworkReader.readFromFile, path, fmt)

        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        fmt = NetworkFormat()
        fmt.pos_edge_id = 1
        fmt.pos_source = 3
        fmt.pos_target = 5
        self.assertRaises(WrongArgumentError, NetworkReader.readFromFile, path, fmt)

        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        fmt = NetworkFormat()
        fmt.pos_edge_id = 1
        fmt.pos_source = 3
        fmt.pos_target = 5
        fmt.separator = ""
        self.assertRaises(WrongArgumentError, NetworkReader.readFromFile, path, fmt)

        # ---------------------------------------------------------------------
        #
        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        self.assertRaises(WrongArgumentError, NetworkReader.readFromFile, path, NetworkFormat("TSUKUBA"))

        # ---------------------------------------------------------------------
        #
        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        net = NetworkReader.readFromFile(path, "IGN")
        self.assertIsInstance(net, Network)


    def test_format_str(self):

        fmt = NetworkFormat("TSUKUBA")
        t = str(fmt)
        print (t)

        t = fmt.asString()
        print (t)


    def test_read_network(self):

        path = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        network = NetworkReader.readFromFile(path, NetworkFormat("IGN"))

        self.assertEqual(8086, len(network.EDGES), 'Edges number')
        self.assertEqual(5820, len(network.NODES), 'Nodes number')

        network.plot('k-', '', 'g-', 'r-', 0.5, plt)
        plt.legend()


    def test_read_wfs(self):

        xmin = 6.74168
        xmax = 6.82568
        ymin = 45.3485
        ymax = 45.4029
        emprise = Bbox(GeoCoords(xmin, ymin), GeoCoords(xmax, ymax))

        tolerance=0.0001
        network = NetworkReader.requestFromIgnGeoportail(emprise, tolerance=tolerance,
                                        spatialIndex=True, proxy=self.nomproxy)
        
        if network != None:
            print ('nb edges=', len(network.EDGES))
        else:
            print ('???')

        
        network.plot('k-', '', 'g-', 'r-', 0.5, plt)
        plt.legend()

        #self.assertEqual(235, len(network.EDGES))
        #self.assertEqual(185, len(network.NODES))


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

    suite.addTest(TestNetworkReader("test_read_network_error_param"))
    suite.addTest(TestNetworkReader("test_format_str"))
    suite.addTest(TestNetworkReader("test_read_network"))
    suite.addTest(TestNetworkReader("test_read_wfs"))

    runner = TextTestRunner()
    runner.run(suite)


