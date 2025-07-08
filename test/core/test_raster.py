# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
from unittest import TestCase, TestSuite, TextTestRunner
from tracklib import (ENUCoords, Bbox, Raster,
                      NO_DATA_VALUE, WrongArgumentError)


class TestRaster(TestCase):

    def test_create_raster(self):

        ll = ENUCoords(0, 0)
        ur = ENUCoords(10, 10)
        emprise = Bbox(ll, ur)

        # ---------------------------------------------------------------------
        grid1 = Raster(bbox=emprise, resolution=(1,1), margin=0.1, novalue=-1)

        self.assertEqual(grid1.xmin, -1)
        self.assertEqual(grid1.ymin, -1)
        self.assertEqual(grid1.xmax, 11)
        self.assertEqual(grid1.ymax, 11)

        self.assertEqual(grid1.resolution[0], 1)
        self.assertEqual(grid1.resolution[1], 1)

        self.assertEqual(grid1.ncol, 12)
        self.assertEqual(grid1.nrow, 12)

        self.assertEqual(grid1.getNoDataValue(), -1)
        self.assertEqual(grid1.countAFMap(), 0)
        self.assertEqual(grid1.getNamesOfAFMap(), [])

        print (grid1)

        # ---------------------------------------------------------------------
        grid2 = Raster(bbox=emprise, resolution=(1,1))

        self.assertEqual(grid2.xmin, -0.5)
        self.assertEqual(grid2.ymin, -0.5)
        self.assertEqual(grid2.xmax, 10.5)
        self.assertEqual(grid2.ymax, 10.5)

        self.assertEqual(grid2.resolution[0], 1)
        self.assertEqual(grid2.resolution[1], 1)

        self.assertEqual(grid2.ncol, 11)
        self.assertEqual(grid2.nrow, 11)

        self.assertEqual(grid2.getNoDataValue(), NO_DATA_VALUE)
        self.assertEqual(grid2.countAFMap(), 0)
        self.assertEqual(grid2.getNamesOfAFMap(), [])

        grid2.summary()


    def test_add_afmap(self):

        ll = ENUCoords(0, 0)
        ur = ENUCoords(5, 2)
        emprise = Bbox(ll, ur)
        raster = Raster(bbox=emprise, resolution=(1,1), margin=0.5)
        print (raster)

        raster.addAFMap('grille0', None)
        self.assertEqual(len(raster.getAFMap('grille0').grid), raster.nrow)
        self.assertEqual(len(raster.getAFMap('grille0').grid[0]), raster.ncol)

        with self.assertRaises(WrongArgumentError):
            raster.addAFMap('grille1', [1,2,3,4,5,6,7])

        with self.assertRaises(WrongArgumentError):
            raster.addAFMap('', [[1,2,3,4,5,6,7], [1,2,3,4,5,6,7]])

        raster.addAFMap('grille1', np.array([[1,2,1,2,1,2,1,2,1,2], [3,4,3,4,3,4,3,4,3,4],
                                  [1,2,3,4,5,6,7,8,9,0], [7,8,7,8,7,8,7,8,7,8]]))

        with self.assertRaises(WrongArgumentError):
            raster.addAFMap('grille1', np.array([[1,1,1,1,1,1,1], [1,1,1,1,1,1,1]]))


        raster.addAFMap('grille2', np.array([[1,1,1,1,1,1,1,1,1,1],
                                  [1,1,1,1,1,1,1,1,1,1],
                                  [1,1,1,1,1,1,1,1,1,1],
                                  [1,1,1,1,1,1,1,1,1,1]]))

        self.assertEqual(raster.countAFMap(), 3)
        self.assertListEqual(raster.getNamesOfAFMap(), ["grille0", "grille1", "grille2"])


    def test_plot_afmap(self):
        ll = ENUCoords(0, 0)
        ur = ENUCoords(5, 2)
        emprise = Bbox(ll, ur)
        raster = Raster(bbox=emprise, resolution=(1,1), margin=0.5)

        raster.addAFMap('grille1', np.array([[1,1,1,1,1,1,1,1,1,1], [3,3,3,3,3,3,3,3,3,3],
                                  [5,5,5,5,5,5,5,5,5,5], [7,7,7,7,7,7,7,7,7,7]]))

        raster.getAFMap('grille1').plotAsVectorGraphic()
        raster.getAFMap('grille1').plotAsImage()


    def test_raster_band_is_in(self):
        ll = ENUCoords(0, 0)
        ur = ENUCoords(10, 10)
        emprise = Bbox(ll, ur)

        grid1 = Raster(bbox=emprise, resolution=(1,1), margin=0.1, novalue=-1)

        self.assertTrue(grid1.isIn(ENUCoords(0, 0)))
        self.assertTrue(grid1.isIn(ENUCoords(-1, -1)))
        self.assertTrue(grid1.isIn(ENUCoords(-1, 11)))
        self.assertTrue(grid1.isIn(ENUCoords(5, 11)))
        self.assertTrue(grid1.isIn(ENUCoords(11, 11)))
        
        self.assertFalse(grid1.isIn(ENUCoords(-1.1, -1.1)))
        self.assertFalse(grid1.isIn(ENUCoords(-1.1, 5)))
        self.assertFalse(grid1.isIn(ENUCoords(-1.1, 11)))
        self.assertFalse(grid1.isIn(ENUCoords(-1.1, 12)))
        self.assertFalse(grid1.isIn(ENUCoords(-1, 12)))
        self.assertFalse(grid1.isIn(ENUCoords(5, 12)))
        self.assertFalse(grid1.isIn(ENUCoords(11, 12)))
        self.assertFalse(grid1.isIn(ENUCoords(12, 12)))
        self.assertFalse(grid1.isIn(ENUCoords(12, 5)))
        self.assertFalse(grid1.isIn(ENUCoords(12, -1)))
        self.assertFalse(grid1.isIn(ENUCoords(12, 0)))
        self.assertFalse(grid1.isIn(ENUCoords(12, -1.5)))
        self.assertFalse(grid1.isIn(ENUCoords(5, -1.5)))



    def test_raster_band_gell_cell(self):
        ll = ENUCoords(0, 0)
        ur = ENUCoords(10, 5)
        emprise = Bbox(ll, ur)

        grid1 = Raster(bbox=emprise, resolution=(2,3), margin=0.2, novalue=-1)

        print (grid1)

        self.assertEqual(grid1.ncol, 7)
        self.assertEqual(grid1.resolution[0], 2)
        self.assertEqual(grid1.nrow, 3)
        self.assertEqual(grid1.resolution[1], 3)

        self.assertEqual(grid1.xmin, -2)
        self.assertEqual(grid1.ymin, -1)
        self.assertEqual(grid1.xmax, 12)
        self.assertEqual(grid1.ymax, 8)

        self.assertIsNone(grid1.getCell(ENUCoords(-2.5, 7)))
        self.assertIsNone(grid1.getCell(ENUCoords(0, 8.1)))
        self.assertIsNone(grid1.getCell(ENUCoords(-2, -2)))




if __name__ == '__main__':
    suite = TestSuite()

    suite.addTest(TestRaster("test_create_raster"))
    suite.addTest(TestRaster("test_add_afmap"))
    suite.addTest(TestRaster("test_plot_afmap"))
    suite.addTest(TestRaster("test_raster_band_is_in"))
    suite.addTest(TestRaster("test_raster_band_gell_cell"))

    runner = TextTestRunner()
    runner.run(suite)
    
    