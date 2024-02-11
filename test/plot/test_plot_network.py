# -*- coding: utf-8 -*-

import os.path
from unittest import TestCase, TestSuite, TextTestRunner
from tracklib import (NetworkReader)



class TestPlotNetwork(TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        chemin = os.path.join(self.resource_path, 'data/network/network_ecrin_extrait.csv')
        self.network = NetworkReader.readFromFile(chemin, 'TEST2', False)
        
    def test_plot_minimal(self):
        self.network.plot()
    
    def test_plot_edge_node(self):
        self.network.plot(edges='b-', nodes='ro')
        
    def test_plot_direct(self):
        self.network.plot(edges='b-', direct='r-')


if __name__ == '__main__':
    
    suite = TestSuite()

    suite.addTest(TestPlotNetwork("test_plot_minimal"))
    suite.addTest(TestPlotNetwork("test_plot_edge_node"))
    suite.addTest(TestPlotNetwork("test_plot_direct"))
    
    runner = TextTestRunner()
    runner.run(suite)


