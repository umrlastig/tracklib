#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os.path
import unittest

from tracklib.io.TrackReader import TrackReader
from tracklib.io.RasterReader import RasterReader
import tracklib.algo.Mapping as mapping
import tracklib.algo.Cinematics as Cinematics

from tracklib.core import ObsCoords as Coords
from tracklib.core import (Obs, Track, ObsTime)
from tracklib.core.Network import Network, Node, Edge
from tracklib.core.SpatialIndex import SpatialIndex


class TestAlgoMappingMethods(unittest.TestCase):
    
    #def setUp (self):
        
    def testMapOnRaster(self):
        resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        
        mntpath = os.path.join(resource_path, 'data/asc/test.asc')
        self.raster = RasterReader.readFromAscFile(mntpath)
        print (self.raster.getRasterBand(1))
        self.band = self.raster.getRasterBand(1)
        
        ObsTime.ObsTime.setReadFormat("4Y/2M/2D 2h:2m:2s")
        tracepath = os.path.join(resource_path, 'data/asc/8961191_v3.csv')
        self.trace = TrackReader.readFromCsv(tracepath, 
                                        id_E=0, id_N=1, id_U=3, id_T=4, 
                                        separator=",", h=1)
        #self.trace.plot()
        
        self.assertEqual(self.band.grid[465][1151], 2007.0, 'ele MNT VT')
        self.assertEqual(self.trace.size(), 363, 'track size')
        mapping.mapOnRaster(self.trace, self.raster)
        
        for j in range(self.trace.size()):
            pos = self.trace.getObs(j).position
            if pos.getX() == 942323.41762134002055973:
                self.assertEqual(2006.0, 
                                 self.trace.getObsAnalyticalFeature('grid1', j), 
                                 'ele MNT AF:')
                self.assertEqual(2002.007, pos.getZ(), 'ele Z:')


    def testMapOnNetwork(self):
        
        ObsTime.ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        # =====================================================================
        trace = Track.Track([], 1)

        c1 = Coords.ENUCoords(2, 1, 0)
        p1 = Obs.Obs(c1, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:01"))
        trace.addObs(p1)
        
        c2 = Coords.ENUCoords(5, 2, 0)
        p2 = Obs.Obs(c2, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:02"))
        trace.addObs(p2)
        
        c3 = Coords.ENUCoords(7, 1.5, 0)
        p3 = Obs.Obs(c3, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:03"))
        trace.addObs(p3)
        
        c4 = Coords.ENUCoords(11, 1, 0)
        p4 = Obs.Obs(c4, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:04"))
        trace.addObs(p4)
        
        c5 = Coords.ENUCoords(13, 3, 0)
        p5 = Obs.Obs(c5, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:04"))
        trace.addObs(p5)
        
        c6 = Coords.ENUCoords(15, 2, 0)
        p6 = Obs.Obs(c6, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:04"))
        trace.addObs(p6)
        
        c7 = Coords.ENUCoords(18, 1, 0)
        p7 = Obs.Obs(c7, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:04"))
        trace.addObs(p7)
        
        c8 = Coords.ENUCoords(22, 1, 0)
        p8 = Obs.Obs(c8, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:04"))
        trace.addObs(p8)
        
        c9 = Coords.ENUCoords(27, -0.5, 0)
        p9 = Obs.Obs(c9, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:04"))
        trace.addObs(p9)
        
        #print (len(trace))
        
        # =====================================================================
        network = Network()
        
        #network.addEdge(edge, noeudIni, noeudFin)
        
        # Segment 1
        s1 = Track.Track([], 1)
        c1 = Coords.ENUCoords(0, 0, 0)
        p1 = Obs.Obs(c1, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s1.addObs(p1)
        c2 = Coords.ENUCoords(10, 0, 0)
        p2 = Obs.Obs(c2, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s1.addObs(p2)
        Cinematics.computeAbsCurv(s1)
        edge = Edge(1, s1)
        edge.orientation = Edge.DOUBLE_SENS
        edge.weight = s1.length()
        
        noeudIni = Node(1, s1.getFirstObs().position)
        noeudFin = Node(2, s1.getLastObs().position)
        
        network.addEdge(edge, noeudIni, noeudFin)
        
        # Segment 2
        s2 = Track.Track([], 2)
        c1 = Coords.ENUCoords(10, 0, 0)
        p1 = Obs.Obs(c1, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s2.addObs(p1)
        c2 = Coords.ENUCoords(10, 5, 0)
        p2 = Obs.Obs(c2, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s2.addObs(p2)
        Cinematics.computeAbsCurv(s2)
        edge = Edge(2, s2)
        edge.orientation = Edge.DOUBLE_SENS
        edge.weight = s2.length()
        
        noeudIni = Node(2, s2.getFirstObs().position)
        noeudFin = Node(4, s2.getLastObs().position)
        
        network.addEdge(edge, noeudIni, noeudFin)
        
        # Segment 3
        s3 = Track.Track([], 2)
        c1 = Coords.ENUCoords(10, 5, 0)
        p1 = Obs.Obs(c1, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s3.addObs(p1)
        c2 = Coords.ENUCoords(20, 5, 0)
        p2 = Obs.Obs(c2, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s3.addObs(p2)
        Cinematics.computeAbsCurv(s3)
        edge = Edge(3, s3)
        edge.orientation = Edge.DOUBLE_SENS
        edge.weight = s3.length()
        
        noeudIni = Node(4, s3.getFirstObs().position)
        noeudFin = Node(5, s3.getLastObs().position)
        
        network.addEdge(edge, noeudIni, noeudFin)
        
        # Segment 4
        s4 = Track.Track([], 2)
        c1 = Coords.ENUCoords(10, 0, 0)
        p1 = Obs.Obs(c1, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s4.addObs(p1)
        c2 = Coords.ENUCoords(20, 0, 0)
        p2 = Obs.Obs(c2, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s4.addObs(p2)
        Cinematics.computeAbsCurv(s4)
        edge = Edge(4, s4)
        edge.orientation = Edge.DOUBLE_SENS
        edge.weight = s4.length()
        
        noeudIni = Node(2, s4.getFirstObs().position)
        noeudFin = Node(3, s4.getLastObs().position)
        
        network.addEdge(edge, noeudIni, noeudFin)
        
        # Segment 5
        s5 = Track.Track([], 2)
        c1 = Coords.ENUCoords(20, 5, 0)
        p1 = Obs.Obs(c1, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s5.addObs(p1)
        c2 = Coords.ENUCoords(20, 0, 0)
        p2 = Obs.Obs(c2, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s5.addObs(p2)
        Cinematics.computeAbsCurv(s5)
        edge = Edge(5, s5)
        edge.orientation = Edge.DOUBLE_SENS
        edge.weight = s5.length()
        
        noeudIni = Node(5, s5.getFirstObs().position)
        noeudFin = Node(3, s5.getLastObs().position)
        
        network.addEdge(edge, noeudIni, noeudFin)
        
        # Segment 6
        s6 = Track.Track([], 2)
        c1 = Coords.ENUCoords(20, 0, 0)
        p1 = Obs.Obs(c1, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s6.addObs(p1)
        c2 = Coords.ENUCoords(30, 0, 0)
        p2 = Obs.Obs(c2, ObsTime.ObsTime.readTimestamp("2018-01-01 10:00:00"))
        s6.addObs(p2)
        Cinematics.computeAbsCurv(s6)
        edge = Edge(6, s6)
        edge.orientation = Edge.DOUBLE_SENS
        edge.weight = s6.length()
        
        noeudIni = Node(3, s6.getFirstObs().position)
        noeudFin = Node(6, s6.getLastObs().position)
        
        network.addEdge(edge, noeudIni, noeudFin)
        
        # =====================================================================
        # Plot
        
        
        # =====================================================================

        si = SpatialIndex(network, resolution=[5,1], margin=0.15)
        network.spatial_index = si


        # =====================================================================
        # Plot
        trace.plotAsMarkers(append=True)
        network.plot('k-', '', 'g-', 'r-', 0.5, plt)
        si.plot(base=False, append=True)

        plt.xlim([-5, 35])
        plt.ylim([-1, 7])


        network.prepare()
        
        # =====================================================================
        #
        
        
        mapping.mapOnNetwork(trace, network, search_radius=5.5, debug=False)
        
        plt.show()
        

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoMappingMethods("testMapOnRaster"))
    suite.addTest(TestAlgoMappingMethods("testMapOnNetwork"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
