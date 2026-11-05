# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from unittest import TestCase, TestSuite, TextTestRunner
import os.path

from tracklib import (ENUCoords, ObsTime, Obs, Track,
                      TrackCollection,
                      SpatialIndex, NetworkReader)


class TestSpatialIndex(TestCase):
    
    __epsilon = 0.001
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
    
    
    def test_create_index_collection1(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")

        track = Track()
        p1 = Obs(ENUCoords(0, 0), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        track.addObs(p1)
        p2 = Obs(ENUCoords(2.5, 3), ObsTime.readTimestamp('2020-01-01 10:08:00'))
        track.addObs(p2)
        p3 = Obs(ENUCoords(2.5, 5), ObsTime.readTimestamp('2020-01-01 10:17:00'))
        track.addObs(p3)
        p4 = Obs(ENUCoords(7, 5), ObsTime.readTimestamp('2020-01-01 10:21:00'))
        track.addObs(p4)
        p5 = Obs(ENUCoords(10, 10), ObsTime.readTimestamp('2020-01-01 10:25:00'))
        track.addObs(p5)
        #track.plot()
        track.plotAsMarkers()
                
        TRACES = []
        TRACES.append(track)
        collection = TrackCollection(TRACES)
                
        index = SpatialIndex(collection, (2, 2))
        index.plot()

        # =====================================================================
        # =====================================================================
        self.assertEqual(index.request(0, 0), [0])
        self.assertEqual(index.request(1, 0), [])
        self.assertEqual(index.request(0, 1), [0])
        self.assertEqual(index.request(1, 1), [0])
        self.assertEqual(index.request(2, 0), [])
        self.assertEqual(index.request(2, 1), [])
        self.assertEqual(index.request(1, 2), [0])
        self.assertEqual(index.request(2, 2), [0])
        self.assertEqual(index.request(3, 2), [0])
        self.assertEqual(index.request(3, 3), [0])
        self.assertEqual(index.request(4, 3), [0])
        self.assertEqual(index.request(4, 4), [0])
        
        
        # # =====================================================================
        self.assertEqual(index.request(ENUCoords(0, 0)), [0])
        self.assertEqual(index.request(ENUCoords(2.5, 3)), [0])
        self.assertEqual(index.request(ENUCoords(2.5, 5)), [0])
        self.assertEqual(index.request(ENUCoords(7, 5)), [0])
        self.assertEqual(index.request(ENUCoords(10, 10)), [0])
        self.assertEqual(index.request(ENUCoords(0.5, 2.5)), [0])
        self.assertEqual(index.request(ENUCoords(4.2, 5.8)), [0])

        
        # # =====================================================================
        self.assertEqual(index.request([ENUCoords(2.1, 0.5), ENUCoords(1.1, 1.1)]), [0])
        self.assertEqual(index.request([ENUCoords(2.1, 0.5), ENUCoords(7.1, 3.5)]), [])
        self.assertEqual(index.request([ENUCoords(5.8, 5.8), ENUCoords(2.1, 1.1)]), [0])
        
        
        # # =====================================================================
        # self.assertEqual(index.request(track), [0])
 
        track2 = Track()
        p6 = Obs(ENUCoords(2.2, 0), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        track2.addObs(p6)
        p7 = Obs(ENUCoords(2.2, 3.8), ObsTime.readTimestamp('2020-01-01 10:08:00'))
        track2.addObs(p7)
        p8 = Obs(ENUCoords(6.5, 3.8), ObsTime.readTimestamp('2020-01-01 10:08:00'))
        track2.addObs(p8)
        self.assertEqual(index.request(track2), [0])
        
        
        track3 = Track()
        p9 = Obs(ENUCoords(6.5, 3.8), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        track3.addObs(p9)
        p10 = Obs(ENUCoords(6.5, 7), ObsTime.readTimestamp('2020-01-01 10:08:00'))
        track3.addObs(p10)
        p11 = Obs(ENUCoords(10, 7), ObsTime.readTimestamp('2020-01-01 10:08:00'))
        track3.addObs(p11)
        self.assertEqual(index.request(track3), [0])


        # # =====================================================================
        # # =====================================================================
        self.assertCountEqual(index.neighborhood(0, 4, 0), [])
        self.assertCountEqual(index.neighborhood(0, 4, 1), [])
        self.assertCountEqual(index.neighborhood(0, 4, 2), [0])
        self.assertCountEqual(index.neighborhood(0, 4, 3), [0])
    
        self.assertCountEqual(index.neighborhood(3, 0, 0), [])
        self.assertCountEqual(index.neighborhood(3, 0, 1), [])
        self.assertCountEqual(index.neighborhood(3, 0, 2), [0])
        self.assertCountEqual(index.neighborhood(3, 0, 3), [0])
    
        self.assertCountEqual(index.neighborhood(2, 2, 0), [0])
        self.assertCountEqual(index.neighborhood(2, 2, 1), [0])
        self.assertCountEqual(index.neighborhood(2, 2, 2), [0])
        self.assertCountEqual(index.neighborhood(2, 2, 3), [0])
    
        # # UNIT = -1
        self.assertCountEqual(index.neighborhood(2, 1, -1), [0])
        self.assertCountEqual(index.neighborhood(2, 0, -1), [0])
        self.assertCountEqual(index.neighborhood(0, 1, -1), [0])
        self.assertCountEqual(index.neighborhood(1, 1, -1), [0])
        self.assertCountEqual(index.neighborhood(0, 4, -1), [0])
        self.assertCountEqual(index.neighborhood(3, 4, -1), [0])
        self.assertCountEqual(index.neighborhood(4, 4, -1), [0])
        self.assertCountEqual(index.neighborhood(2, 4, -1), [0])
        
        
        # # =====================================================================
        self.assertCountEqual(index.neighborhood(ENUCoords(0, 0.1)), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(2.5, 3)), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(2.5, 5)), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(7, 5)), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(10, 10)), [0])
        
        self.assertCountEqual(index.neighborhood(ENUCoords(6.5, 3.8), None, 0), [])
        self.assertCountEqual(index.neighborhood(ENUCoords(6.5, 3.8), None, 1), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(6.5, 3.8), None, 2), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(6.5, 3.8), None, 3), [0])

        self.assertCountEqual(index.neighborhood(ENUCoords(2.2, 3.8), None, 0), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(2.2, 3.8), None, 1), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(2.2, 3.8), None, 2), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(2.2, 3.8), None, 3), [0])
        
        self.assertCountEqual(index.neighborhood(ENUCoords(9.9, 7), None, 0), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(9.9, 7), None, 1), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(9.9, 7), None, 2), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(9.9, 7), None, 3), [0])
       
        #  # UNIT = -1
        self.assertCountEqual(index.neighborhood(ENUCoords(0, 0), None, -1), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(2.5, 3), None, -1), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(2.5, 5), None, -1), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(7, 5), None, -1), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(10, 10), None, -1), [0])
        
        self.assertCountEqual(index.neighborhood(ENUCoords(6.5, 3.8), None, -1), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(2.2, 3.8), None, -1), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(9.9, 7), None, -1), [0])
  
    
        # # =====================================================================
        self.assertEqual(index.neighborhood([ENUCoords(2.1, 0.5), ENUCoords(0.1, 2.1)], None, 0), [0])
        self.assertEqual(index.neighborhood([ENUCoords(2.1, 0.5), ENUCoords(0.1, 2.1)], None, 1), [0])
        self.assertEqual(index.neighborhood([ENUCoords(2.1, 0.5), ENUCoords(0.1, 2.1)], None, 2), [0])
        self.assertEqual(index.neighborhood([ENUCoords(2.1, 0.5), ENUCoords(0.1, 2.1)], None, -1), [0])

        self.assertEqual(index.neighborhood([ENUCoords(2.1, 0.5), ENUCoords(7.1, 3.5)]), [])
        self.assertEqual(index.neighborhood([ENUCoords(2.1, 0.5), ENUCoords(7.1, 3.5)], None, 2), [0])
        self.assertEqual(index.neighborhood([ENUCoords(2.1, 0.5), ENUCoords(7.1, 3.5)], None, -1), [0])
        
        self.assertEqual(index.neighborhood([ENUCoords(5.8, 5.8), ENUCoords(2.1, 1.1)]), [0])
        self.assertEqual(index.neighborhood([ENUCoords(5.8, 5.8), ENUCoords(2.1, 1.1)], None, 1), [0])
        self.assertEqual(index.neighborhood([ENUCoords(5.8, 5.8), ENUCoords(2.1, 1.1)], None, 2), [0])
        self.assertEqual(index.neighborhood([ENUCoords(5.8, 5.8), ENUCoords(2.1, 1.1)], None, -1), [0])
        
        
        # # =====================================================================
        self.assertEqual(index.neighborhood(track), [0])
        self.assertEqual(index.neighborhood(track, None, 1), [0])
        self.assertEqual(index.neighborhood(track, None, 3), [0])
        self.assertEqual(index.neighborhood(track, None, -1), [0])
 
        self.assertEqual(index.neighborhood(track2), [0])
        self.assertEqual(index.neighborhood(track2, None, 0), [0])
        self.assertEqual(index.neighborhood(track2, None, 1), [0])
        self.assertEqual(index.neighborhood(track2, None, 3), [0])
        self.assertEqual(index.neighborhood(track2, None, -1), [0])
        
        self.assertEqual(index.neighborhood(track3), [0])
        self.assertEqual(index.neighborhood(track3, None, 0), [0])
        self.assertEqual(index.neighborhood(track3, None, 1), [0])
        self.assertEqual(index.neighborhood(track3, None, 2), [0])
        self.assertEqual(index.neighborhood(track3, None, 3), [0])
        self.assertEqual(index.neighborhood(track3, None, -1), [0])
        
        plt.show()
        
    
    def test_create_index_collection2(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        track = Track()
        p1 = Obs(ENUCoords(0, 0), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        track.addObs(p1)
        p2 = Obs(ENUCoords(3.1, 3), ObsTime.readTimestamp('2020-01-01 10:08:00'))
        track.addObs(p2)
        p3 = Obs(ENUCoords(3.1, 4.5), ObsTime.readTimestamp('2020-01-01 10:17:00'))
        track.addObs(p3)
        
        p4 = Obs(ENUCoords(4.5, 4.5), ObsTime.readTimestamp('2020-01-01 10:21:00'))
        track.addObs(p4)
        p5 = Obs(ENUCoords(6, 5.5), ObsTime.readTimestamp('2020-01-01 10:21:00'))
        track.addObs(p5)
        
        p6 = Obs(ENUCoords(7, 4.5), ObsTime.readTimestamp('2020-01-01 10:21:00'))
        track.addObs(p6)
        p7 = Obs(ENUCoords(11, 5.5), ObsTime.readTimestamp('2020-01-01 10:21:00'))
        track.addObs(p7)
        p8 = Obs(ENUCoords(13, 10), ObsTime.readTimestamp('2020-01-01 10:25:00'))
        track.addObs(p8)
                #track.plot()
                #track.plotAsMarkers()
                
        TRACES = []
        TRACES.append(track)
        collection = TrackCollection(TRACES)
                
        index = SpatialIndex(collection, (2, 2))
        index.plot()
        
        # =====================================================================
        # =====================================================================
        self.assertEqual(index.request(0, 0), [0])
        self.assertEqual(index.request(1, 0), [0])
        self.assertEqual(index.request(0, 1), [])
        self.assertEqual(index.request(1, 1), [0])
        self.assertEqual(index.request(2, 0), [])
        self.assertEqual(index.request(2, 1), [])
        self.assertEqual(index.request(1, 2), [0])
        self.assertEqual(index.request(2, 2), [0])
        self.assertEqual(index.request(3, 2), [0])
        self.assertEqual(index.request(3, 3), [])
        self.assertEqual(index.request(4, 2), [0])
        self.assertEqual(index.request(4, 3), [])
        self.assertEqual(index.request(4, 4), [])
        self.assertEqual(index.request(5, 2), [0])
        self.assertEqual(index.request(5, 3), [0])
        self.assertEqual(index.request(5, 4), [])
        
        plt.show()
        
        
    def test_request_index(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        track = Track()
        p1 = Obs(ENUCoords(550, 320), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        track.addObs(p1)
        p2 = Obs(ENUCoords(610, 325), ObsTime.readTimestamp('2020-01-01 10:08:00'))
        track.addObs(p2)
        p3 = Obs(ENUCoords(610, 330), ObsTime.readTimestamp('2020-01-01 10:17:00'))
        track.addObs(p3)
        p4 = Obs(ENUCoords(650, 330), ObsTime.readTimestamp('2020-01-01 10:21:00'))
        track.addObs(p4)
        p5 = Obs(ENUCoords(675, 340), ObsTime.readTimestamp('2020-01-01 10:25:00'))
        track.addObs(p5)
        track.plot()
        #track.plotAsMarkers()
        
        TRACES = []
        TRACES.append(track)
        collection = TrackCollection(TRACES)
        
        res = (25, 4)
        index = SpatialIndex(collection, res, 0.05, True)
        index.plot()
        
        # =====================================================================
        self.assertEqual(index.request(0, 0), [0])
        self.assertEqual(index.request(1, 0), [0])
        self.assertEqual(index.request(0, 1), [])
        self.assertEqual(index.request(1, 1), [0])
        self.assertEqual(index.request(2, 0), [])
        self.assertEqual(index.request(2, 1), [0])
        self.assertEqual(index.request(2, 2), [0])
        self.assertEqual(index.request(3, 2), [0])
        self.assertEqual(index.request(4, 2), [0])
        self.assertEqual(index.request(4, 3), [0])
        self.assertEqual(index.request(4, 4), [0])
        
        # =====================================================================
        self.assertEqual(index.request(ENUCoords(550, 320)), [0])
        self.assertEqual(index.request(ENUCoords(550, 330)), [])
        self.assertEqual(index.request(ENUCoords(610, 325)), [0])
        self.assertEqual(index.request(ENUCoords(610, 330)), [0])
        self.assertEqual(index.request(ENUCoords(650, 330)), [0])
        self.assertEqual(index.request(ENUCoords(675, 340)), [0])
        self.assertEqual(index.request(ENUCoords(675, 325)), [])
        
        # ======================================================================
        p1 = ENUCoords(550, 320)
        p2 = ENUCoords(580, 320)
        p3 = ENUCoords(580, 330)
        p4 = ENUCoords(580, 340)
        self.assertEqual(index.request([p1, p2]), [0])
        self.assertEqual(index.request([p1, p3]), [0])
        self.assertEqual(index.request([p3, p4]), [])
        
        # ======================================================================
        self.assertEqual(index.request(track), [0])

        # =====================================================================
        track2 = Track()
        p6 = Obs(ENUCoords(580, 320), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        track2.addObs(p6)
        p7 = Obs(ENUCoords(580, 327), ObsTime.readTimestamp('2020-01-01 10:08:00'))
        track2.addObs(p7)
        p8 = Obs(ENUCoords(640, 327), ObsTime.readTimestamp('2020-01-01 10:08:00'))
        track2.addObs(p8)
        
        self.assertEqual(index.request(track2), [0])
        
        # =====================================================================
        track3 = Track()
        p9 = Obs(ENUCoords(640, 327), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        track3.addObs(p9)
        p10 = Obs(ENUCoords(640, 335), ObsTime.readTimestamp('2020-01-01 10:08:00'))
        track3.addObs(p10)
        p11 = Obs(ENUCoords(675, 335), ObsTime.readTimestamp('2020-01-01 10:08:00'))
        track3.addObs(p11)
       
        self.assertEqual(index.request(track3), [0])
        
        plt.show()
        
        
    def test_neighborhood_index(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        track = Track()
        p1 = Obs(ENUCoords(550, 320), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        track.addObs(p1)
        p2 = Obs(ENUCoords(610, 325), ObsTime.readTimestamp('2020-01-01 10:08:00'))
        track.addObs(p2)
        p3 = Obs(ENUCoords(610, 330), ObsTime.readTimestamp('2020-01-01 10:17:00'))
        track.addObs(p3)
        p4 = Obs(ENUCoords(650, 330), ObsTime.readTimestamp('2020-01-01 10:21:00'))
        track.addObs(p4)
        p5 = Obs(ENUCoords(675, 340), ObsTime.readTimestamp('2020-01-01 10:25:00'))
        track.addObs(p5)
        track.plot()
        #track.plotAsMarkers()
        
        TRACES = []
        TRACES.append(track)
        collection = TrackCollection(TRACES)
        
        res = (25, 4)
        index = SpatialIndex(collection, res, 0.05, True)
        index.plot()
        
        # =====================================================================
        self.assertCountEqual(index.neighborhood(0, 4, 0), [])
        self.assertCountEqual(index.neighborhood(0, 4, 1), [])
        self.assertCountEqual(index.neighborhood(0, 4, 2), [0])
        self.assertCountEqual(index.neighborhood(0, 4, 3), [0])
    
        self.assertCountEqual(index.neighborhood(3, 0, 0), [])
        self.assertCountEqual(index.neighborhood(3, 0, 1), [0])
        self.assertCountEqual(index.neighborhood(3, 0, 2), [0])
        self.assertCountEqual(index.neighborhood(3, 0, 3), [0])
    
        self.assertCountEqual(index.neighborhood(2, 2, 0), [0])
        self.assertCountEqual(index.neighborhood(2, 2, 1), [0])
        self.assertCountEqual(index.neighborhood(2, 2, 2), [0])
        self.assertCountEqual(index.neighborhood(2, 2, 3), [0])
    
        # =====================================================================
        # UNIT != -1
        self.assertCountEqual(index.neighborhood(2, 1, 0), [0])
        self.assertCountEqual(index.neighborhood(2, 1, 1), [0])
        self.assertCountEqual(index.neighborhood(2, 1, 2), [0])
        self.assertCountEqual(index.neighborhood(2, 1, 3), [0])
        
        # UNIT = -1
        self.assertCountEqual(index.neighborhood(2, 1, -1), [0])
        self.assertCountEqual(index.neighborhood(2, 0, -1), [0])
        self.assertCountEqual(index.neighborhood(0, 1, -1), [0])
        self.assertCountEqual(index.neighborhood(1, 1, -1), [0])
        self.assertCountEqual(index.neighborhood(0, 4, -1), [0])
        self.assertCountEqual(index.neighborhood(3, 4, -1), [0])
        self.assertCountEqual(index.neighborhood(4, 4, -1), [0])
        self.assertCountEqual(index.neighborhood(2, 4, -1), [0])
        
        # =====================================================================
        # UNIT != -1
        self.assertCountEqual(index.neighborhood(ENUCoords(550, 320)), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(610, 325)), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(610, 330)), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(650, 330)), [0])
        self.assertCountEqual(index.neighborhood(ENUCoords(675, 320)), [])
        
#        self.assertCountEqual(index.neighborhood(ENUCoords(640, 327), None, 0), [])
#        self.assertCountEqual(index.neighborhood(ENUCoords(640, 327), None, 1), [(0,0), (1,0), (2,0), (3,0)])
#        self.assertCountEqual(index.neighborhood(ENUCoords(640, 327), None, 2), [(0,0), (3,0)])
#        self.assertCountEqual(index.neighborhood(ENUCoords(640, 327), None, 3), [(0,0), (3,0)])
        
#        self.assertCountEqual(index.neighborhood(ENUCoords(580, 327), None, 0), [(0,0)])
#        self.assertCountEqual(index.neighborhood(ENUCoords(580, 327), None, 1), [(0,0),(1,0),(2,0)])
#        self.assertCountEqual(index.neighborhood(ENUCoords(580, 327), None, 2), [(2,0)])
#        self.assertCountEqual(index.neighborhood(ENUCoords(580, 327), None, 3), [(2,0), (3,0)])
        
#        self.assertCountEqual(index.neighborhood(ENUCoords(674, 335), None, 0), [(3,0)])
#        self.assertCountEqual(index.neighborhood(ENUCoords(674, 335), None, 1), [(2,0), (3,0)])
#        self.assertCountEqual(index.neighborhood(ENUCoords(674, 335), None, 2), [(0,0), (1,0), (2,0)])
#        self.assertCountEqual(index.neighborhood(ENUCoords(674, 335), None, 3), [(0,0)])
        
        # UNIT = -1
#        self.assertCountEqual(index.neighborhood(ENUCoords(550, 320), None, -1), [(0,0)])
#        self.assertCountEqual(index.neighborhood(ENUCoords(610, 325), None, -1), [(0,0), (1,0), (2,0)])
#        self.assertCountEqual(index.neighborhood(ENUCoords(610, 330), None, -1), [(0,0), (1,0), (2,0)])
#        self.assertCountEqual(index.neighborhood(ENUCoords(650, 330), None, -1), [(2,0), (3,0)])
#        self.assertCountEqual(index.neighborhood(ENUCoords(675, 340), None, -1), [(3,0)])
        
#        self.assertCountEqual(index.neighborhood(ENUCoords(640, 327), None, -1), [(0,0),(1,0),(2,0),(3,0)])
#        self.assertCountEqual(index.neighborhood(ENUCoords(580, 327), None, -1), [(0,0), (1,0), (2,0)])
#        self.assertCountEqual(index.neighborhood(ENUCoords(674, 335), None, -1), [(2,0), (3,0)])
        
        
        # =====================================================================
        # UNIT != -1
        #self.assertEqual(index.neighborhood([(2.1, 0.5), (1.1, 1.1)], None, 0), [(0,0)])
        
        plt.show()
        
        
    def test_index_network(self):
        
        chemin = os.path.join(self.resource_path, 'data/network/network_igast.csv')
        network = NetworkReader.readFromFile(chemin, 'TEST_UNITAIRE', False)

        index = SpatialIndex(network, (2,2))
        index.plot()

        self.assertCountEqual(index.neighborhood(ENUCoords(5, 46), unit=0),
                              [5, 8, 9])
        index.collection[5].geom.plot('b-', append=True)
        index.collection[8].geom.plot('r-', append=True)
        index.collection[9].geom.plot('k-', append=True)
        # print (index.neighborhood(ENUCoords(5, 46), unit=1))
        # print (index.neighborhood(ENUCoords(5, 46), unit=-1))

        plt.xlim([-7, 10])
        plt.ylim([42, 52])
        plt.show()

        self.assertCountEqual(index.neighborhood(ENUCoords(5, 46), unit=0), [5, 8, 9])

        edge5 = network[5]
        network.removeEdge(edge5)
        index.removeFeature(5)

        index.plot()
        plt.xlim([-7, 10])
        plt.ylim([42, 52])
        plt.show()

        self.assertCountEqual(index.neighborhood(ENUCoords(5, 46), unit=0), [8, 9])

        box = index.bbox()
        self.assertTrue(abs(box.ur.N - 50.996) < 0.01)
        self.assertTrue(abs(box.ur.E - 8.364) < 0.01)

        self.assertFalse(index.covers(ENUCoords(-5.1, 48)))
        self.assertFalse(index.covers(ENUCoords(0, 42.5)))
        self.assertFalse(index.covers(ENUCoords(0, 51)))
        self.assertFalse(index.covers(ENUCoords(10, 48)))


    def test_remove_obj(self):
        TRACES = []

        track1 = Track()
        track1.addObs(Obs(ENUCoords(0, 0), ObsTime()))
        track1.addObs(Obs(ENUCoords(2.5, 3), ObsTime()))
        track1.addObs(Obs(ENUCoords(2.5, 5), ObsTime()))
        track1.addObs(Obs(ENUCoords(7, 5), ObsTime()))
        track1.addObs(Obs(ENUCoords(10, 10), ObsTime()))
        track1.plotAsMarkers()
        TRACES.append(track1)

        track2 = Track()
        track2.addObs(Obs(ENUCoords(0, 2.5), ObsTime()))
        track2.addObs(Obs(ENUCoords(3.5, 2.5), ObsTime()))
        track2.addObs(Obs(ENUCoords(3.5, 5.5), ObsTime()))
        track2.addObs(Obs(ENUCoords(6.5, 5.5), ObsTime()))
        track2.addObs(Obs(ENUCoords(6.5, 7), ObsTime()))
        track2.addObs(Obs(ENUCoords(9, 10), ObsTime()))
        track2.plotAsMarkers()
        TRACES.append(track2)

        track3 = Track()
        track3.addObs(Obs(ENUCoords(1, 9), ObsTime()))
        track3.addObs(Obs(ENUCoords(1, 3.5), ObsTime()))
        track3.addObs(Obs(ENUCoords(2, 3.5), ObsTime()))
        track3.addObs(Obs(ENUCoords(2, 5.8), ObsTime()))
        track3.addObs(Obs(ENUCoords(7.8, 5.8), ObsTime()))
        track3.addObs(Obs(ENUCoords(7.8, 9.5), ObsTime()))
        track3.plotAsMarkers()
        TRACES.append(track3)

        collection = TrackCollection(TRACES)
        index = SpatialIndex(collection, (2, 2))
        index.plot()
        index.highlight(2,2)
        plt.show()

        self.assertCountEqual(index.neighborhood(ENUCoords(5, 5), None, 0), [0, 1, 2])
        self.assertCountEqual(index.neighborhood(ENUCoords(5, 5), None, -1), [0, 1, 2])
        self.assertCountEqual(index.neighborhood(ENUCoords(7, 9), None, -1), [0, 1, 2])
        self.assertCountEqual(index.neighborhood(ENUCoords(7, 9), None, 0), [1, 2])
        self.assertCountEqual(index.neighborhood(ENUCoords(1, 10), None, 0), [2])
        self.assertCountEqual(index.neighborhood(ENUCoords(1, 10), None, -1), [2])
        self.assertCountEqual(index.neighborhood(ENUCoords(1, 10), None, 2), [0, 1, 2])

        index.removeFeature(2)
        index.plot()
        plt.show()

        index.removeFeature(0)
        index.plot()
        plt.show()
        # print (index.collection[0])





    
if __name__ == '__main__':
    suite = TestSuite()
    
    suite.addTest(TestSpatialIndex("test_request_index"))
    suite.addTest(TestSpatialIndex("test_neighborhood_index"))
    suite.addTest(TestSpatialIndex("test_create_index_collection1"))
    suite.addTest(TestSpatialIndex("test_create_index_collection2"))
    suite.addTest(TestSpatialIndex("test_remove_obj"))
    suite.addTest(TestSpatialIndex("test_index_network"))
    runner = TextTestRunner()
    runner.run(suite)
    