# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner
import os.path

import matplotlib.pyplot as plt

from tracklib.core.GPSTime import GPSTime
from tracklib.core.Coords import ENUCoords
from tracklib.core.Obs import Obs
from tracklib.core.Track import Track
from tracklib.core.TrackCollection import TrackCollection
from tracklib.core.SpatialIndex import SpatialIndex

from tracklib.io.FileReader import FileReader
from tracklib.io.IgnReader import IgnReader

from tracklib.algo import (Analytics)


class TestSpatialIndex(TestCase):
    
    __epsilon = 0.001
    
    resource_path = os.path.join(os.path.split(__file__)[0], "..")
    
    
    def test_index_trackcollection(self):
       
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        chemindata = os.path.join(TestSpatialIndex.resource_path, "data/CSV_L93_VERCORS/")
        collection = FileReader.readFromFiles(chemindata, 3, 4, 5, 6)
        
        collection.addAnalyticalFeature(Analytics.speed)
        
        #print (collection.size())
        #print (collection.bbox())
        #collection.plot()
    
        index = SpatialIndex(collection, (30,30))
        index.plot()
        plt.show()
        
    
    def test_index_network(self):
        
         xmin = 2.34850
         xmax = 2.35463
         ymin = 48.83896
         ymax = 48.84299
         network = IgnReader.getNetwork((xmin, ymin, xmax, ymax), "EPSG:2154")
         
         #NetworkReader.writeFromFile("ici.csv", network)
        
         # print (network.bbox())
         # network.plot()
        
         index = SpatialIndex(network, (20, 20))
         index.plot()
        
        
    def testCreateIndex(self):
        
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        track = Track()
        p1 = Obs(ENUCoords(550, 320), GPSTime.readTimestamp('2020-01-01 10:00:00'))
        track.addObs(p1)
        p2 = Obs(ENUCoords(610, 325), GPSTime.readTimestamp('2020-01-01 10:08:00'))
        track.addObs(p2)
        p3 = Obs(ENUCoords(610, 330), GPSTime.readTimestamp('2020-01-01 10:17:00'))
        track.addObs(p3)
        p4 = Obs(ENUCoords(650, 330), GPSTime.readTimestamp('2020-01-01 10:21:00'))
        track.addObs(p4)
        p5 = Obs(ENUCoords(675, 340), GPSTime.readTimestamp('2020-01-01 10:25:00'))
        track.addObs(p5)
        #track.plot()
        #track.plotAsMarkers()
        
        TRACES = []
        TRACES.append(track)
        collection = TrackCollection(TRACES)
        
        index = SpatialIndex(collection, (5, 5))
        index.plot()
        
        
        self.assertEqual(index.request(0, 0), [(0,0)])
        self.assertEqual(index.request(1, 0), [(0,0)])
        self.assertEqual(index.request(0, 1), [])
        self.assertEqual(index.request(1, 1), [(0,0)])
        self.assertEqual(index.request(2, 0), [(0,0)])
        self.assertEqual(index.request(2, 1), [(0,0),(1,0)])
        self.assertEqual(index.request(2, 2), [(1,0), (2,0)])
        self.assertEqual(index.request(3, 2), [(2,0)])
        self.assertEqual(index.request(4, 2), [(2,0),(3,0)])
        self.assertEqual(index.request(4, 4), [(3,0)])
        
        self.assertEqual(index.request(ENUCoords(550, 320)), [(0,0)])
        self.assertEqual(index.request(ENUCoords(610, 325)), [(0,0), (1,0)])
        self.assertEqual(index.request(ENUCoords(610, 330)), [(1,0), (2,0)])
        self.assertEqual(index.request(ENUCoords(650, 330)), [(2,0), (3,0)])
        self.assertEqual(index.request(ENUCoords(675, 340)), [(3,0)])
        
        
        self.assertEqual(index.request([(2.1, 0.5), (1.1, 1.1)]), [(0,0)])
        self.assertEqual(index.request([(2.5, 2.5), (2.1, 1.1)]), [(0,0),(1,0),(2,0)])
        
        
        self.assertEqual(index.request(track), [(0,0),(1,0),(2,0),(3,0)])
        
    
    
    def testIndexPoint(self):
        ''' TODO '''
        pass
        
        
    
if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestSpatialIndex("testCreateIndex"))
    suite.addTest(TestSpatialIndex("test_index_trackcollection"))
    suite.addTest(TestSpatialIndex("test_index_network"))
    suite.addTest(TestSpatialIndex("testIndexPoint"))
    runner = TextTestRunner()
    runner.run(suite)
    