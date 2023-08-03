#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os.path
import unittest
from tracklib import (Obs, ObsTime, ENUCoords, 
                      Track, 
                      Network, Node, Edge, 
                      SpatialIndex,
                      computeAbsCurv,
                      mapOnRaster, mapOnNetwork, mapOn,
                      TrackReader, RasterReader)


class TestAlgoMappingMethods(unittest.TestCase):
    
    def getDataset1(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        trace = Track([], 1)

        c1 = ENUCoords(2, 1, 0)
        p1 = Obs(c1, ObsTime.readTimestamp("2018-01-01 10:00:01"))
        trace.addObs(p1)
        
        c2 = ENUCoords(5, 2, 0)
        p2 = Obs(c2, ObsTime.readTimestamp("2018-01-01 10:00:02"))
        trace.addObs(p2)
        
        c3 = ENUCoords(7, 1.5, 0)
        p3 = Obs(c3, ObsTime.readTimestamp("2018-01-01 10:00:03"))
        trace.addObs(p3)
        
        c4 = ENUCoords(11, 1, 0)
        p4 = Obs(c4, ObsTime.readTimestamp("2018-01-01 10:00:04"))
        trace.addObs(p4)
            
        c5 = ENUCoords(13, 3, 0)
        p5 = Obs(c5, ObsTime.readTimestamp("2018-01-01 10:00:04"))
        trace.addObs(p5)
        
        c6 = ENUCoords(15, 2, 0)
        p6 = Obs(c6, ObsTime.readTimestamp("2018-01-01 10:00:04"))
        trace.addObs(p6)
        
        c7 = ENUCoords(18, 1, 0)
        p7 = Obs(c7, ObsTime.readTimestamp("2018-01-01 10:00:04"))
        trace.addObs(p7)
        
        c8 = ENUCoords(22, 1, 0)
        p8 = Obs(c8, ObsTime.readTimestamp("2018-01-01 10:00:04"))
        trace.addObs(p8)
        
        c9 = ENUCoords(27, -0.5, 0)
        p9 = Obs(c9, ObsTime.readTimestamp("2018-01-01 10:00:04"))
        trace.addObs(p9)
        
        #print (len(trace))
        return trace
    
    
    def getDataset2(self):
        network = Network()
        
        # Segment 1
        s1 = Track([], 1)
        c1 = ENUCoords(0, 0, 0)
        p1 = Obs(c1, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s1.addObs(p1)
        c2 = ENUCoords(10, 0, 0)
        p2 = Obs(c2, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s1.addObs(p2)
        computeAbsCurv(s1)
        edge = Edge(1, s1)
        edge.orientation = Edge.DOUBLE_SENS
        edge.weight = s1.length()
        
        noeudIni = Node(1, s1.getFirstObs().position)
        noeudFin = Node(2, s1.getLastObs().position)
        
        network.addEdge(edge, noeudIni, noeudFin)
            
        # Segment 2
        s2 = Track([], 2)
        c1 = ENUCoords(10, 0, 0)
        p1 = Obs(c1, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s2.addObs(p1)
        c2 = ENUCoords(10, 5, 0)
        p2 = Obs(c2, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s2.addObs(p2)
        computeAbsCurv(s2)
        edge = Edge(2, s2)
        edge.orientation = Edge.DOUBLE_SENS
        edge.weight = s2.length()
        
        noeudIni = Node(2, s2.getFirstObs().position)
        noeudFin = Node(4, s2.getLastObs().position)
        
        network.addEdge(edge, noeudIni, noeudFin)
        
        # Segment 3
        s3 = Track([], 2)
        c1 = ENUCoords(10, 5, 0)
        p1 = Obs(c1, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s3.addObs(p1)
        c2 = ENUCoords(20, 5, 0)
        p2 = Obs(c2, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s3.addObs(p2)
        computeAbsCurv(s3)
        edge = Edge(3, s3)
        edge.orientation = Edge.DOUBLE_SENS
        edge.weight = s3.length()
        
        noeudIni = Node(4, s3.getFirstObs().position)
        noeudFin = Node(5, s3.getLastObs().position)
            
        network.addEdge(edge, noeudIni, noeudFin)
        
        # Segment 4
        s4 = Track([], 2)
        c1 = ENUCoords(10, 0, 0)
        p1 = Obs(c1, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s4.addObs(p1)
        c2 = ENUCoords(20, 0, 0)
        p2 = Obs(c2, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s4.addObs(p2)
        computeAbsCurv(s4)
        edge = Edge(4, s4)
        edge.orientation = Edge.DOUBLE_SENS
        edge.weight = s4.length()
            
        noeudIni = Node(2, s4.getFirstObs().position)
        noeudFin = Node(3, s4.getLastObs().position)
        
        network.addEdge(edge, noeudIni, noeudFin)
        
        # Segment 5
        s5 = Track([], 2)
        c1 = ENUCoords(20, 5, 0)
        p1 = Obs(c1, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s5.addObs(p1)
        c2 = ENUCoords(20, 0, 0)
        p2 = Obs(c2, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s5.addObs(p2)
        computeAbsCurv(s5)
        edge = Edge(5, s5)
        edge.orientation = Edge.DOUBLE_SENS
        edge.weight = s5.length()
        
        noeudIni = Node(5, s5.getFirstObs().position)
        noeudFin = Node(3, s5.getLastObs().position)
        
        network.addEdge(edge, noeudIni, noeudFin)
            
        # Segment 6
        s6 = Track([], 2)
        c1 = ENUCoords(20, 0, 0)
        p1 = Obs(c1, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s6.addObs(p1)
        c2 = ENUCoords(30, 0, 0)
        p2 = Obs(c2, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s6.addObs(p2)
        computeAbsCurv(s6)
        edge = Edge(6, s6)
        edge.orientation = Edge.DOUBLE_SENS
        edge.weight = s6.length()
            
        noeudIni = Node(3, s6.getFirstObs().position)
        noeudFin = Node(6, s6.getLastObs().position)
            
        network.addEdge(edge, noeudIni, noeudFin)
        
        return network
    
        
    def testMapOnRaster(self):
        resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        
        mntpath = os.path.join(resource_path, 'data/asc/test.asc')
        self.raster = RasterReader.readFromAscFile(mntpath)
        self.band = self.raster.getRasterBand(0)

        ObsTime.setReadFormat("4Y/2M/2D 2h:2m:2s")
        tracepath = os.path.join(resource_path, 'data/asc/8961191_v3.csv')
        self.trace = TrackReader.readFromCsv(tracepath, 
                                        id_E=0, id_N=1, id_U=3, id_T=4, 
                                        separator=",", h=1)
        #self.trace.plot()
        
        self.assertEqual(self.band.grid[1151][465], 2007.0, 'ele MNT VT')
        self.assertEqual(self.trace.size(), 363, 'track size')
        
        mapOnRaster(self.trace, self.raster)
        
        for j in range(self.trace.size()):
            pos = self.trace.getObs(j).position
            if pos.getX() == 942323.41762134002055973:
                self.assertEqual(1191.0, self.trace.getObsAnalyticalFeature('grid', j), 
                                 'ele MNT AF:')
                self.assertEqual(2002.007, pos.getZ(), 'ele Z:')
        

    def testMapOnNetwork(self):
        trace = self.getDataset1()
        network = self.getDataset2()
        
        # =====================================================================
        #   Indexation spatiale
        si = SpatialIndex(network, resolution=[5,1], margin=0.15)
        network.spatial_index = si

        # =====================================================================
        # Plot
        trace.plotAsMarkers(append=True)
        network.plot('k-', '', 'g-', 'r-', 0.5, plt)
        si.plot(base=False, append=True)

        plt.xlim([-5, 35])
        plt.ylim([-1, 7])

        # =====================================================================
        # 
        network.prepare()
        
        # =====================================================================
        #
        mapOnNetwork(trace, network, search_radius=5.5, debug=False)
        
        plt.show()
        
        
    def testMapOn(self):
        resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        path_cam = os.path.join(resource_path, 'data/hybridation_gnss_camera.dat')
        path_gps = os.path.join(resource_path, 'data/hybridation_gnss_camera.pos')
        
        ObsTime.setReadFormat("2D/2M/4Y-2h:2m:2s.3z")
        
        
        track_cam = TrackReader.readFromCsv(path_cam, 1, 2, 3, 0, " ", srid="ENUCoords")
        track_gps = TrackReader.readFromCsv(path_gps, 1, 2, 3, 0, " ", srid="ENUCoords")
        
        track_cam.incrementTime(0, 18-3600)
        
        ini_time = ObsTime("06/06/2021-16:02:00.000")
        fin_time = ObsTime("06/06/2021-16:12:12.000")
        
        
        track_cam = track_cam.extractSpanTime(ini_time, fin_time)
        track_gps = track_gps.extractSpanTime(ini_time, fin_time)
        track_gps = track_gps // track_cam
        
        track_cam.rotate(0.2);
        mapOn(track_cam, track_gps)
        
        track_cam.plot('r-')
        track_gps.plot('b+')
        plt.show()


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoMappingMethods("testMapOnRaster"))
    suite.addTest(TestAlgoMappingMethods("testMapOnNetwork"))
    suite.addTest(TestAlgoMappingMethods("testMapOn"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
