# -*- coding: utf-8 -*-

import filecmp
import os.path
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.io.NetworkReader import NetworkReader
from tracklib.io.NetworkWriter import NetworkWriter

class TestNetworkwriter(TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        
        
    def test_write_csv_network(self):
        path1 = os.path.join(self.resource_path, 'data/network/network_22245.csv')
        path2 = os.path.join(self.resource_path, 'data/test/network_22245_copie.csv')
        
        network = NetworkReader.readFromFile(path1, formatfile = 'IGN')
        NetworkWriter.writeToCsv(network, path2)
        
        filecmp.cmp(path1, path2)
        
        
#    def test_write_kml_network(self):
#        path1 = os.path.join(self.resource_path, 'data/network/network_22245.csv')
#        path2 = os.path.join(self.resource_path, 'data/network/network_22245_noeud.kml')
#        
#        network = NetworkReader.readFromFile(path1, formatfile = 'IGN')
#        
#        NetworkWriter.writeToKml(network, path2,)
    
    
if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestNetworkwriter("test_write_csv_network"))
    #suite.addTest(TestNetworkwriter("test_write_kml_network"))
    runner = TextTestRunner()
    runner.run(suite)

