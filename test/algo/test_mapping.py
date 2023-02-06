#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os.path
import unittest

from tracklib.io.TrackReader import TrackReader
from tracklib.io.RasterReader import RasterReader
import tracklib.algo.Mapping as mapping

from tracklib.core import (ObsTime)
from tracklib.core.SpatialIndex import SpatialIndex

from .data import Data as Data


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
        
        trace = Data.getDataset1()
        network = Data.getDataset2()
        
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
        mapping.mapOnNetwork(trace, network, search_radius=5.5, debug=False)
        
        plt.show()
        
        
    def testMapOn(self):
        
        resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        path_cam = os.path.join(resource_path, 'data/hybridation_gnss_camera.dat')
        path_gps = os.path.join(resource_path, 'data/hybridation_gnss_camera.pos')
        
        ObsTime.ObsTime.setReadFormat("2D/2M/4Y-2h:2m:2s.3z")
        
        
        track_cam = TrackReader.readFromCsv(path_cam, 1, 2, 3, 0, " ", srid="ENUCoords")
        track_gps = TrackReader.readFromCsv(path_gps, 1, 2, 3, 0, " ", srid="ENUCoords")
        
        track_cam.incrementTime(0, 18-3600)
        
        ini_time = ObsTime.ObsTime("06/06/2021-16:02:00.000")
        fin_time = ObsTime.ObsTime("06/06/2021-16:12:12.000")
        
        
        track_cam = track_cam.extractSpanTime(ini_time, fin_time)
        track_gps = track_gps.extractSpanTime(ini_time, fin_time)
        track_gps = track_gps // track_cam
        
        track_cam.rotate(0.2);
        mapping.mapOn(track_cam, track_gps)
        
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
