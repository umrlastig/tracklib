# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
from unittest import TestCase, TestSuite, TextTestRunner
from tracklib import (ENUCoords, Bbox, Raster,
                      CountDistinctBand, GridBand, AFMap, Band, Grid2D,
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


        grille1 = raster.addAFMap('grille1')
        grille1.addValues()

        self.assertEqual(raster.countAFMap(), 1)
        self.assertEqual(raster.getNamesOfAFMap(), ['grille1'])
        self.assertEqual(raster.getAFMap(0).af_name, 'grille1')
        self.assertEqual(raster.getAFMap('grille1').af_name, 'grille1')
        self.assertIsInstance(raster.getAFMap(0), AFMap)
        self.assertIsInstance(raster.getAFMap(0)[0], Band)
        self.assertEqual(raster.getAFMap(0)[0].getName(), 'values')
        self.assertEqual(raster.getAFMap(0)['values'].getName(), 'values')
        self.assertIsInstance(raster.getAFMap(0)[0].getGrid(), Grid2D)
        self.assertEqual(len(raster.getAFMap(0)[0].getGrid().values), raster.nrow)
        self.assertEqual(len(raster.getAFMap(0)[0].getGrid().values[0]), raster.ncol)


        with self.assertRaises(WrongArgumentError):
            afmap = raster.addAFMap('grille1')
            gridvalues = afmap.addValues([1,2,3,4,5,6,7])

        with self.assertRaises(WrongArgumentError):
            afmap = raster.addAFMap('grille1')
            gridvalues = afmap.addValues()
            gridvalues.setGrid([1,2,3,4,5,6,7])

        with self.assertRaises(WrongArgumentError):
            afmap = raster.addAFMap('')
            gridvalues = afmap.addValues([[1,2,3,4,5,6,7], [1,2,3,4,5,6,7]])

        with self.assertRaises(WrongArgumentError):
            afmap = raster.addAFMap('grille1')
            gridvalues = afmap.addValues(np.array([[1,1,1,1,1,1,1], [1,1,1,1,1,1,1]]))


        # OK
        grille2 = raster.addAFMap('grille2')
        grille2.addValues(np.array([[1,2,1,2,1,2,1,2,1,2], [3,4,3,4,3,4,3,4,3,4],
                                      [1,2,3,4,5,6,7,8,9,0], [7,8,7,8,7,8,7,8,7,8]]))

        self.assertEqual(raster.countAFMap(), 2)
        self.assertEqual(raster.getNamesOfAFMap(), ['grille1', 'grille2'])
        self.assertEqual(raster.getAFMap(1).af_name, 'grille2')
        self.assertEqual(raster.getAFMap('grille2').af_name, 'grille2')
        self.assertIsInstance(raster.getAFMap(1), AFMap)
        self.assertIsInstance(raster.getAFMap(1)[0], Band)
        self.assertEqual(raster.getAFMap(1)[0].getName(), 'values')
        self.assertEqual(raster.getAFMap(1)['values'].getName(), 'values')
        self.assertIsInstance(raster.getAFMap(1)[0].getGrid(), Grid2D)


        grille3 = raster.addAFMap('grille3')
        grille3.addValues(np.array([[1,1,1,1,1,1,1,1,1,1],
                                  [1,1,1,1,1,1,1,1,1,1],
                                  [1,1,1,1,1,1,1,1,1,1],
                                  [1,1,1,1,1,1,1,1,1,1]]))
        self.assertEqual(raster.countAFMap(), 3)
        self.assertListEqual(raster.getNamesOfAFMap(), ["grille1", "grille2", "grille3"])



    def test_plot_afmap(self):
        ll = ENUCoords(0, 0)
        ur = ENUCoords(5, 2)
        emprise = Bbox(ll, ur)
        raster = Raster(bbox=emprise, resolution=(1,1), margin=0.5)

        grille1 = raster.addAFMap('grille1')
        grille1.addValues(np.array([[1,1,1,1,1,1,1,1,1,1], [3,3,3,3,3,3,3,3,3,3],
                                  [5,5,5,5,5,5,5,5,5,5], [7,7,7,7,7,7,7,7,7,7]]))

        raster.getAFMap('grille1').plotAsVectorGraphic()
        raster.getAFMap('grille1').plot()




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

        # print (grid1)

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


    def test_filter(self):

        ll = ENUCoords(0, 0)
        ur = ENUCoords(7, 7)
        emprise = Bbox(ll, ur)
        raster = Raster(bbox=emprise, resolution=(1,1), margin=0)
        
        grille1 = raster.addAFMap('grille1')
        grid = np.array([[0,0,0,0,0,0,0],
                         [1,1,1,0,1,1,1],
                         [1,1,1,0,1,0,0],
                         [0,0,1,1,1,0,0],
                         [1,1,1,0,1,0,0],
                         [1,1,1,0,1,1,1],
                         [0,0,0,0,0,0,0]])
        grille1.addValues(grid)

        raster.getAFMap('grille1').plot(cmap='viridis')

        mask = np.array([
                [0,1,0],
                [1,1,1],
                [0,1,0]])

        # Dilatation
        raster.getAFMap('grille1').filter(mask=mask, aggregation=np.max)

        # Erosion
        raster.getAFMap('grille1')[0].getGrid().filter(np.array([[1]]), lambda x : 1-x)     # Dual de la carte
        raster.getAFMap('grille1')[0].getGrid().filter(mask, np.max)                        # Dilatation
        raster.getAFMap('grille1')[0].getGrid().filter(np.array([[1]]), lambda x : 1-x)     # Dual de la carte

        raster.getAFMap('grille1').plot(cmap='viridis')


if __name__ == '__main__':
    suite = TestSuite()

    suite.addTest(TestRaster("test_create_raster"))
    suite.addTest(TestRaster("test_add_afmap"))
    suite.addTest(TestRaster("test_plot_afmap"))
    suite.addTest(TestRaster("test_raster_band_is_in"))
    suite.addTest(TestRaster("test_raster_band_gell_cell"))
    suite.addTest(TestRaster("test_filter"))

    runner = TextTestRunner()
    runner.run(suite)
    
    