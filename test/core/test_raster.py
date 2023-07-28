# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner

from tracklib import (ENUCoords)
from tracklib.core import (RasterBand, Bbox)


class TestRaster(TestCase):
    
    def setCreateRasterBand (self):
        
        ll = ENUCoords(0, 0)
        ur = ENUCoords(10, 10)
        emprise = Bbox.Bbox(ll, ur)
        
        grid1 = RasterBand.RasterBand(bb=emprise, resolution=(1,1), margin=0.1, novalue=-1, name='grille1')
        grid2 = RasterBand.RasterBand(bb=emprise, resolution=(1,1), margin=0.1, novalue=-1)
        
        self.assertEqual(grid1.getName(), 'grille1')
        self.assertEqual(grid2.getName(), 'grid')
        
        grid1.summary()
        grid1.plotAsGraphic()
        


if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestRaster("setCreateRasterBand"))
    runner = TextTestRunner()
    runner.run(suite)
    
    