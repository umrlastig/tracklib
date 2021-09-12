# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os.path
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.algo.Selection import Constraint
import tracklib.algo.Geometrics as Geometrics
from tracklib.core.GPSTime import GPSTime
from tracklib.io.FileReader import FileReader



class TestSelection(TestCase):
    
    def setUp (self):
        
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
    
    
    def test_selection(self):
        
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        chemin = os.path.join(self.resource_path, './data/trace1.dat')
        track = FileReader.readFromFile(chemin, 2, 3, -1, 4, separator=",")
        
        circle = Geometrics.Circle(track.getLastObs().position, 10)
        print (circle.center.getX(), circle.center.getY(), circle.radius)
        circle.plot()

        #plt.plot(track.getX(), track.getY(), 'b+')
        plt.show()
        
        c1 = Constraint(circle, track)
        t = c1.contains(track)
        #print (t)
        #tr = c1.select(track)
        #print (type(t))
        print (track.size(), track.length())
    
    
    
        
    
if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestSelection("test_selection"))
    runner = TextTestRunner()
    runner.run(suite)