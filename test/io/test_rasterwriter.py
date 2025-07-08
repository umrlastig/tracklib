# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import os

import filecmp
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib import (ObsTime, Track, ENUCoords, Obs, TrackCollection, Bbox,
                      AFMap, co_count, summarize,
                      RasterWriter, WrongArgumentError, Raster)


class TestRasterWriter(TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "..")

        # ---------------------------------------------------------------------
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")

        trace1 = Track([], 1)
        c1 = ENUCoords(0, 10, 0)
        p1 = Obs(c1, ObsTime())
        trace1.addObs(p1)
        
        c2 = ENUCoords(0, 110, 0)
        p2 = Obs(c2, ObsTime())
        trace1.addObs(p2)
        
        c3 = ENUCoords(50, 110, 0)
        p3 = Obs(c3, ObsTime())
        trace1.addObs(p3)
        
        c4 = ENUCoords(50, 10, 0)
        p4 = Obs(c4, ObsTime())
        trace1.addObs(p4)
        
        self.collection = TrackCollection([trace1])

    def test_write_asc_file(self):

        # ---------------------------------------------------------------------
        # Test exception if the first parameter is not a filepath
        self.assertRaises(WrongArgumentError, RasterWriter.writeMapToAscFile, "", None)

        ascfile = os.path.join(self.resource_path, 'data/io/raster/test_write_asc_file.asc')

        # Test exception if the second parameter is not a RasterBand
        self.assertRaises(WrongArgumentError, RasterWriter.writeMapToAscFile, ascfile, None)

        ll = ENUCoords(0, 0)
        ur = ENUCoords(10, 10)
        emprise = Bbox(ll, ur)
        grid1 = Raster(bbox=emprise, resolution=(1,1), margin=0.1, novalue=-1)
        self.assertRaises(WrongArgumentError, RasterWriter.writeMapToAscFile, ascfile, grid1)

        # ---------------------------------------------------------------------
        # Test asc contents
        ll = ENUCoords(0, 0)
        ur = ENUCoords(5, 2)
        emprise = Bbox(ll, ur)
        raster = Raster(bbox=emprise, resolution=(1,1), margin=0.5)

        raster.addAFMap('grille1', np.array([[1,2,1,2,1,2,1,2,1,2], [3,4,3,4,3,4,3,4,3,4],
                                  [1,2,3,4,5,6,7,8,9,0], [7,8,7,8,7,8,7,8,7,8]]))

        raster.getAFMap(0).plotAsImage()
        plt.show()

        RasterWriter.writeMapToAscFile(ascfile, raster.getAFMap(0))

        vtpath = os.path.join(self.resource_path, 'data/io/raster/test1.asc')
        self.assertTrue(filecmp.cmp(ascfile, vtpath))



if __name__ == '__main__':
    
    suite = TestSuite()

    suite.addTest(TestRasterWriter("test_write_asc_file"))

    runner = TextTestRunner()
    runner.run(suite)
