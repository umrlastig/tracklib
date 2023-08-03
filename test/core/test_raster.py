# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner
from tracklib import (ENUCoords, Bbox, RasterBand, Raster)

class TestRaster(TestCase):
    
    def test_create_raster_band(self):
        ll = ENUCoords(0, 0)
        ur = ENUCoords(10, 10)
        emprise = Bbox(ll, ur)
        
        grid1 = RasterBand(bb=emprise, resolution=(1,1), margin=0.1, novalue=-1, name='grille1')
        grid2 = RasterBand(bb=emprise, resolution=(1,1), margin=0.2, novalue=-1, name='grille2')
        
        self.assertEqual(grid1.getName(), 'grille1')
        self.assertEqual(grid2.getName(), 'grille2')
        
        grid1.summary()
        grid1.plotAsGraphic()
        
        raster = Raster([grid1, grid2])
        self.assertEqual(raster.bandCount(), 2)
        self.assertListEqual(raster.getNamesOfRasterBand(), ["grille1", "grille2"])
        
        raster.plot(1)
        raster.plot('grille2')
        
        b1 = raster.getRasterBand(0).bbox()
        self.assertEqual(b1.getLowerLeft().getX(), -1)
        self.assertEqual(b1.getLowerLeft().getY(), -1)
        self.assertEqual(b1.getUpperRight().getX(), 11)
        self.assertEqual(b1.getUpperRight().getY(), 11)
        
        b2 = raster.getRasterBand(1).bbox()
        self.assertEqual(b2.getLowerLeft().getX(), -2)
        self.assertEqual(b2.getLowerLeft().getY(), -2)
        self.assertEqual(b2.getUpperRight().getX(), 12)
        self.assertEqual(b2.getUpperRight().getY(), 12)
        

    def test_raster_band_is_in(self):
        ll = ENUCoords(0, 0)
        ur = ENUCoords(10, 10)
        emprise = Bbox(ll, ur)
        
        grid1 = RasterBand(bb=emprise, resolution=(1,1), margin=0.1, novalue=-1, name='grille1')
        
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
        
        grid1 = RasterBand(bb=emprise, resolution=(2,3), margin=0.2, novalue=-1, name='grille1')
        
        self.assertEqual(grid1.ncol, 7)
        self.assertEqual(grid1.XPixelSize, 2)
        self.assertEqual(grid1.nrow, 2)
        self.assertEqual(grid1.YPixelSize, 3.5)
        
        self.assertEqual(grid1.bbox().getLowerLeft().getX(), -2)
        self.assertEqual(grid1.bbox().getLowerLeft().getY(), -1)
        self.assertEqual(grid1.bbox().getUpperRight().getX(), 12)
        self.assertEqual(grid1.bbox().getUpperRight().getY(), 6)
        
        self.assertIsNone(grid1.getCell(ENUCoords(-2.5, 7)))
        self.assertIsNone(grid1.getCell(ENUCoords(0, 7)))
        

if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestRaster("test_create_raster_band"))
    suite.addTest(TestRaster("test_raster_band_is_in"))
    suite.addTest(TestRaster("test_raster_band_gell_cell"))
    runner = TextTestRunner()
    runner.run(suite)
    
    