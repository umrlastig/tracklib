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
        raster = RasterReader.readFromAscFile(csvpath, name='MNT')

        grid = raster.getAFMap(0)
        self.assertEqual('MNT', grid.getName())

        self.assertEqual(1000, raster.nrow)
        self.assertEqual(1000, raster.ncol)
        self.assertEqual(5.0, raster.resolution[0])
        self.assertEqual(5.0, raster.resolution[1])
        self.assertEqual(929997.5, raster.xmin)
        self.assertEqual(6410002.5, raster.ymin)
        self.assertEqual(934997.5, raster.xmax)
        self.assertEqual(6415002.5, raster.ymax)

    def test_read_asc(self):
        # =============================================================
        csvpath = os.path.join(self.resource_path, 'data/asc/test.asc')
        raster = RasterReader.readFromAscFile(csvpath, name='z')
        grid = raster.getAFMap(0)

        self.assertEqual('z', grid.getName())

        self.assertEqual(2000, raster.nrow)
        self.assertEqual(2000, raster.ncol)
        self.assertEqual(5.0, raster.resolution[0])
        self.assertEqual(5.0, raster.resolution[1])
        self.assertEqual(939997.5, raster.xmin)
        self.assertEqual(6430002.5, raster.ymin)
        self.assertEqual(949997.5, raster.xmax)
        self.assertEqual(6440002.5, raster.ymax)

        self.assertEqual(1418, grid.grid[0][1])
        self.assertEqual(1419, grid.grid[1][0])
        self.assertEqual(902, grid.grid[600][884])
        self.assertEqual(1317, grid.grid[836][365])
        self.assertEqual(1678, grid.grid[1102][935])

        # ---------------------------------------------------------------------
        raster = RasterReader.readFromAscFile(csvpath, name='mnt')
        grid = raster.getAFMap(0)
        
        self.assertEqual('mnt', grid.getName())
        self.assertEqual(2000, raster.nrow)
        self.assertEqual(2000, raster.ncol)
        self.assertEqual(5.0, raster.resolution[0])
        self.assertEqual(5.0, raster.resolution[1])
        self.assertEqual(939997.5, raster.xmin)
        self.assertEqual(6430002.5, raster.ymin)
        self.assertEqual(949997.5, raster.xmax)
        self.assertEqual(6440002.5, raster.ymax)
        
        self.assertEqual(1418, grid.grid[0][1])
        self.assertEqual(1419, grid.grid[1][0])
        self.assertEqual(902, grid.grid[600][884])
        self.assertEqual(1317, grid.grid[836][365])
        self.assertEqual(1678, grid.grid[1102][935])
        

    def test_read_metadata_mnt(self):
         csvpath = os.path.join(self.resource_path, 'data/asc/RGEALTI_0930_6415_LAMB93_IGN69.asc')
         rb = RasterReader.readMetadataFromAscFile(csvpath)
         
         self.assertEqual(rb.nrow, 1000)
         self.assertEqual(rb.ncol, 1000)
         self.assertEqual(rb.resolution[0], 5)
         self.assertEqual(rb.resolution[1], 5)
         self.assertEqual(929997.5, rb.xmin)
         self.assertEqual(6410002.5, rb.ymin)
         self.assertEqual(934997.5, rb.xmax)
         self.assertEqual(6415002.5, rb.ymax)
         


if __name__ == '__main__':
    suite = TestSuite()

    suite.addTest(TestRasterReader("test_read_ign_mnt"))
    suite.addTest(TestRasterReader("test_read_asc"))
    suite.addTest(TestRasterReader("test_read_metadata_mnt"))

    runner = TextTestRunner()
    runner.run(suite)

