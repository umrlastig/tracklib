# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
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

        b1 = grid1.bbox()
        self.assertEqual(b1.getLowerLeft().getX(), -1)
        self.assertEqual(b1.getLowerLeft().getY(), -1)
        self.assertEqual(b1.getUpperRight().getX(), 11)
        self.assertEqual(b1.getUpperRight().getY(), 11)

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

        b2 = grid2.bbox()
        self.assertEqual(b2.getLowerLeft().getX(), -0.5)
        self.assertEqual(b2.getLowerLeft().getY(), -0.5)
        self.assertEqual(b2.getUpperRight().getX(), 10.5)
        self.assertEqual(b2.getUpperRight().getY(), 10.5)

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

        raster.addAFMap('grille1', [[1,2,1,2,1,2,1,2,1,2], [3,4,3,4,3,4,3,4,3,4],
                                  [1,2,3,4,5,6,7,8,9,0], [7,8,7,8,7,8,7,8,7,8]])

        with self.assertRaises(WrongArgumentError):
            raster.addAFMap('grille1', [[1,1,1,1,1,1,1], [1,1,1,1,1,1,1]])


        raster.addAFMap('grille2', [[1,1,1,1,1,1,1,1,1,1],
                                  [1,1,1,1,1,1,1,1,1,1],
                                  [1,1,1,1,1,1,1,1,1,1],
                                  [1,1,1,1,1,1,1,1,1,1]])

        self.assertEqual(raster.countAFMap(), 3)
        self.assertListEqual(raster.getNamesOfAFMap(), ["grille0", "grille1", "grille2"])


    def test_plot_afmap(self):
        ll = ENUCoords(0, 0)
        ur = ENUCoords(5, 2)
        emprise = Bbox(ll, ur)
        raster = Raster(bbox=emprise, resolution=(1,1), margin=0.5)

        raster.addAFMap('grille1', [[1,1,1,1,1,1,1,1,1,1], [3,3,3,3,3,3,3,3,3,3],
                                  [5,5,5,5,5,5,5,5,5,5], [7,7,7,7,7,7,7,7,7,7]])

        raster.getAFMap('grille1').plotAsGraphic()
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

        self.assertEqual(grid1.bbox().getLowerLeft().getX(), -2)
        self.assertEqual(grid1.bbox().getLowerLeft().getY(), -1)
        self.assertEqual(grid1.bbox().getUpperRight().getX(), 12)
        self.assertEqual(grid1.bbox().getUpperRight().getY(), 6)

        self.assertIsNone(grid1.getCell(ENUCoords(-2.5, 7)))
        self.assertIsNone(grid1.getCell(ENUCoords(0, 7)))
        self.assertIsNone(grid1.getCell(ENUCoords(-2, -2)))


    def test_raster_upsampling(self):
        """
        Ajouter tests:
            - no data value
            - taille des grilles, plus petit plus grand

        """
        ll = ENUCoords(0, 0)
        ur = ENUCoords(10, 10)
        emprise = Bbox(ll, ur)
        '''
        g = AFMap(bb=emprise, resolution=(4, 4),
                        margin=0, novalue=-1, name='g')

        self.assertEqual(g.ncol, 2)
        self.assertEqual(g.XPixelSize, 5)
        self.assertEqual(g.nrow, 2)
        self.assertEqual(g.YPixelSize, 5)
        self.assertEqual(g.bbox().ll.getX(), 0)
        self.assertEqual(g.bbox().ll.getY(), 0)
        self.assertEqual(g.bbox().ur.getX(), 10)
        self.assertEqual(g.bbox().ur.getY(), 10)
        plt.show()

        values = [[1,2], [3,4]]
        g.grid = values
        # g.plotAsGraphic()

        g1 = g.upSampling(resolution=(1,1),
                          interpolation=MODE_NEAREST_NEIGHBOR,
                          name='g1')
        self.assertEqual(g1.getName(), 'g1')
        for i in range(5):
            for j in range(5):
                self.assertEqual(g1.grid[i][j], 1)
        for i in range(5, 10):
            for j in range(5):
                self.assertEqual(g1.grid[i][j], 3)
        for i in range(5):
            for j in range(5, 10):
                self.assertEqual(g1.grid[i][j], 2)
        for i in range(5, 10):
            for j in range(5, 10):
                self.assertEqual(g1.grid[i][j], 4)
        # g1.plotAsGraphic()
        # plt.show()

        g2 = g.upSampling(resolution=(1,1),
                          interpolation=MODE_BED_OF_NAILS_TECHNIQUE,
                          name='g2')
        self.assertEqual(g2.getName(), 'g2')
        for i in range(10):
            for j in range(10):
                if i == 0 and j == 0:
                    self.assertEqual(g2.grid[i][j], 1)
                elif i == 0 and j == 5:
                    self.assertEqual(g2.grid[i][j], 2)
                elif i == 5 and j == 0:
                    self.assertEqual(g2.grid[i][j], 3)
                elif i == 5 and j == 5:
                    self.assertEqual(g2.grid[i][j], 4)
                else:
                    self.assertEqual(g2.grid[i][j], 0)
        # g2.plotAsGraphic()
        '''


if __name__ == '__main__':
    suite = TestSuite()

    suite.addTest(TestRaster("test_create_raster"))
    suite.addTest(TestRaster("test_add_afmap"))
    suite.addTest(TestRaster("test_plot_afmap"))
    suite.addTest(TestRaster("test_raster_band_is_in"))
    suite.addTest(TestRaster("test_raster_band_gell_cell"))
    #suite.addTest(TestRaster("test_raster_upsampling"))

    runner = TextTestRunner()
    runner.run(suite)
    
    