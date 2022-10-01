#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

import os.path
from tracklib.core import (GPSTime)
from tracklib.io.FileReader import FileReader
from tracklib.io.RasterReader import RasterReader
import tracklib.algo.Mapping as mapping


class TestAlgoMappingMethods(unittest.TestCase):
    
    def setUp (self):
        resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        mntpath = os.path.join(resource_path, 'data/asc/test.asc')
        self.raster = RasterReader.readFromAscFile(mntpath)
        print (self.raster.getRasterBand(1))
        self.band = self.raster.getRasterBand(1)
        
        GPSTime.GPSTime.setReadFormat("4Y/2M/2D 2h:2m:2s")
        tracepath = os.path.join(resource_path, 'data/asc/8961191_v3.csv')
        self.trace = FileReader.readFromFile(tracepath, 
                                        id_E=0, id_N=1, id_U=3, id_T=4, 
                                        separator=",", h=1)
        
    def testMapOnRaster(self):
        self.assertEqual(self.band.grid[465][1151], 2007.0, 'ele MNT VT')
        self.assertEqual(self.trace.size(), 363, 'track size')
        mapping.mapOnRaster(self.trace, self.raster)
        
        for j in range(self.trace.size()):
            pos = self.trace.getObs(j).position
            if pos.getX() == 942323.41762134002055973:
                self.assertEqual(2007.0, 
                                 self.trace.getObsAnalyticalFeature('grid1', j), 
                                 'ele MNT AF:')
                self.assertEqual(2002.007, pos.getZ(), 'ele Z:')


if __name__ == '__main__':
    suite = unittest.TestSuite()
    
    suite.addTest(TestAlgoMappingMethods("testMapOnRaster"))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)