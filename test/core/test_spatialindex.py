# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner

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
    
    
    def test_index_trackcollection(self):
       
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        collection = FileReader.readFromFiles("../data/CSV_L93_VERCORS/", 3, 4, 5, 6)
        
        collection.addAnalyticalFeature(Analytics.speed)
        
        #print (collection.size())
        #print (collection.bbox())
        #collection.plot()
    
        index = SpatialIndex(collection)
        index.plot()
        plt.show()
        
    
    def test_index_network(self):
        
         xmin = 2.34850
         xmax = 2.35463
         ymin = 48.83896
         ymax = 48.84299
         network = IgnReader.getNetwork((xmin, ymin, xmax, ymax), "EPSG:2154")
        
         # print (network.bbox())
         # network.plot()
        
         index = SpatialIndex(network)
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
        
        
    
if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestSpatialIndex("testCreateIndex"))
    suite.addTest(TestSpatialIndex("test_index_trackcollection"))
    suite.addTest(TestSpatialIndex("test_index_network"))
    runner = TextTestRunner()
    runner.run(suite)