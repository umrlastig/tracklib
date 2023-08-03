# -*- coding: utf-8 -*-

import os.path
from unittest import TestCase, TestSuite, TextTestRunner
from tracklib import RasterReader


class TestRasterReader(TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")

    def test_read_ign_mnt(self):
        # =============================================================
        csvpath = os.path.join(self.resource_path, 'data/asc/RGEALTI_0930_6415_LAMB93_IGN69.asc')
        raster = RasterReader.readFromAscFile(csvpath)
        grid = raster.getRasterBand(0)
        
        self.assertEqual('grid', grid.getName())
        self.assertEqual(1000, grid.nrow)
        self.assertEqual(1000, grid.ncol)
        self.assertEqual(5.0, grid.XPixelSize)
        self.assertEqual(5.0, grid.YPixelSize)
        self.assertEqual(929997.5, grid.xmin)
        self.assertEqual(6410002.5, grid.ymin)
        self.assertEqual(934997.5, grid.xmax)
        self.assertEqual(6415002.5, grid.ymax)
        

    def test_read_asc(self):
        # =============================================================
        csvpath = os.path.join(self.resource_path, 'data/asc/test.asc')
        raster = RasterReader.readFromAscFile(csvpath)
        grid = raster.getRasterBand(0)
        
        self.assertEqual('grid', grid.getName())
        self.assertEqual(2000, grid.nrow)
        self.assertEqual(2000, grid.ncol)
        self.assertEqual(5.0, grid.XPixelSize)
        self.assertEqual(5.0, grid.YPixelSize)
        self.assertEqual(939997.5, grid.xmin)
        self.assertEqual(6430002.5, grid.ymin)
        self.assertEqual(949997.5, grid.xmax)
        self.assertEqual(6440002.5, grid.ymax)

        self.assertEqual(1418, grid.grid[0][1])
        self.assertEqual(1419, grid.grid[1][0])
        self.assertEqual(902, grid.grid[600][884])
        self.assertEqual(1317, grid.grid[836][365])
        self.assertEqual(1678, grid.grid[1102][935])
        
        # ---------------------------------------------------------------------
        raster = RasterReader.readFromAscFile(csvpath, name='mnt')
        grid = raster.getRasterBand(0)
        
        self.assertEqual('mnt', grid.getName())
        self.assertEqual(2000, grid.nrow)
        self.assertEqual(2000, grid.ncol)
        self.assertEqual(5.0, grid.XPixelSize)
        self.assertEqual(5.0, grid.YPixelSize)
        self.assertEqual(939997.5, grid.xmin)
        self.assertEqual(6430002.5, grid.ymin)
        self.assertEqual(949997.5, grid.xmax)
        self.assertEqual(6440002.5, grid.ymax)
        
        self.assertEqual(1418, grid.grid[0][1])
        self.assertEqual(1419, grid.grid[1][0])
        self.assertEqual(902, grid.grid[600][884])
        self.assertEqual(1317, grid.grid[836][365])
        self.assertEqual(1678, grid.grid[1102][935])
        
        
    #def test_read_alti(self):
    #    NetworkReader.getAltitude('aa')
    
    
    def test_read_metadata_mnt(self):
         csvpath = os.path.join(self.resource_path, 'data/asc/RGEALTI_0930_6415_LAMB93_IGN69.asc')
         rb = RasterReader.readMetadataFromAscFile(csvpath, 'MNT')
         
         self.assertEqual(rb.getName(), 'MNT')
         self.assertEqual(rb.nrow, 1000)
         self.assertEqual(rb.ncol, 1000)
         self.assertEqual(rb.XPixelSize, 5)
         self.assertEqual(rb.YPixelSize, 5)
         self.assertEqual(929997.5, rb.xmin)
         self.assertEqual(6410002.5, rb.ymin)
         self.assertEqual(934997.5, rb.xmax)
         self.assertEqual(6415002.5, rb.ymax)
         


if __name__ == '__main__':
    #unittest.main()
    suite = TestSuite()
    suite.addTest(TestRasterReader("test_read_ign_mnt"))
    suite.addTest(TestRasterReader("test_read_asc"))
    suite.addTest(TestRasterReader("test_read_metadata_mnt"))
    runner = TextTestRunner()
    runner.run(suite)

