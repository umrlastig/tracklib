# -*- coding: utf-8 -*-

import os.path
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.io.RasterReader import RasterReader


class TestRasterReader(TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")

    def test_read_ign_mnt(self):
        # =============================================================
        csvpath = os.path.join(self.resource_path, 'data/asc/RGEALTI_0930_6415_LAMB93_IGN69.asc')
        raster = RasterReader.readFromAscFile(csvpath)
        grid = raster.getRasterBand(1)
        
        self.assertEqual(1000, grid.nrow)
        self.assertEqual(1000, grid.ncol)
        self.assertEqual(5.0, grid.XPixelSize)
        self.assertEqual(5.0, grid.YPixelSize)
        self.assertEqual(929997.5, grid.xmin)
        self.assertEqual(6410002.5, grid.ymin)
        self.assertEqual(934997.5, grid.xmax)
        self.assertEqual(6415002.5, grid.ymax)
        

    def test_read_test_mnt(self):
        # =============================================================
        csvpath = os.path.join(self.resource_path, 'data/asc/test.asc')
        raster = RasterReader.readFromAscFile(csvpath)
        grid = raster.getRasterBand(1)
        
        self.assertEqual(2000, grid.nrow)
        self.assertEqual(2000, grid.ncol)
        self.assertEqual(5.0, grid.XPixelSize)
        self.assertEqual(5.0, grid.YPixelSize)
        self.assertEqual(939997.5, grid.xmin)
        self.assertEqual(6430002.5, grid.ymin)
        self.assertEqual(949997.5, grid.xmax)
        self.assertEqual(6440002.5, grid.ymax)
        
        self.assertEqual(902, grid.grid[884][600])
        self.assertEqual(1317, grid.grid[365][836])
        self.assertEqual(1678, grid.grid[935][1102])
        
    #def test_read_alti(self):
    #    NetworkReader.getAltitude('aa')


if __name__ == '__main__':
    #unittest.main()
    suite = TestSuite()
    suite.addTest(TestRasterReader("test_read_ign_mnt"))
    suite.addTest(TestRasterReader("test_read_test_mnt"))
    runner = TextTestRunner()
    runner.run(suite)

