# -*- coding: utf-8 -*-

import unittest

import math
import matplotlib.pyplot as plt

from tracklib.core.Coords import ENUCoords
from tracklib.core.Bbox import Bbox
import tracklib.algo.Geometrics as Geometrics


class TestBbox(unittest.TestCase):

    def testPlotBbox(self):
        
        Xmin = 370250
        Xmax = 371250
        Ymin = 3949050
        Ymax = 3950050

        ll = ENUCoords(Xmin, Ymin)
        ur = ENUCoords(Xmax, Ymax)
        emprise = Bbox(ll, ur)
        emprise.plot()
        
        print (emprise)
        self.assertEqual(emprise.getLowerLeft().E, Xmin)
        self.assertEqual(emprise.getLowerLeft().N, Ymin)
        self.assertEqual(emprise.getUpperRight().E, Xmax)
        self.assertEqual(emprise.getUpperRight().N, Ymax)
        
        self.assertTrue(emprise.contains(ENUCoords(370800, 3949550)))
        self.assertFalse(emprise.contains(ENUCoords(3.45, 48.77)))
        self.assertFalse(emprise.contains(ENUCoords(3.45, 0.0)))
        self.assertFalse(emprise.contains(ENUCoords(0.0, 0.0)))
        
        poly = Geometrics.Polygon([Xmin, Xmax, Xmax, Xmin, Xmin], [Ymin, Ymin, Ymax, Ymax, Ymin])
        self.assertEqual(emprise.geom().X, poly.X)
        self.assertEqual(emprise.geom().Y, poly.Y)
        
        bbox2 = emprise.copy()
        bbox2.translate(10, 20)
        self.assertIsInstance(bbox2, Bbox)
        self.assertEqual(bbox2.ll.E, Xmin + 10)
        self.assertEqual(bbox2.ll.N, Ymin + 20)
        self.assertEqual(bbox2.ur.E, Xmax + 10)
        self.assertEqual(bbox2.ur.N, Ymax + 20)
        
        bbox2.rotate(math.pi/2)
        self.assertIsInstance(bbox2, Bbox)
        self.assertEqual(round(bbox2.ll.E), float(-3949070))
        self.assertEqual(round(bbox2.ll.N), float(370260))
        self.assertEqual(round(bbox2.ur.E), float(-3950070))
        self.assertEqual(round(bbox2.ur.N), float(371260))
        #bbox2.plot('g--')
        
        bbox2.scale(1.5)
        self.assertIsInstance(bbox2, Bbox)
        self.assertEqual(round(bbox2.ll.E), float(-5923605))
        self.assertEqual(round(bbox2.ll.N), float(555390))
        self.assertEqual(round(bbox2.ur.E), float(-5925105))
        self.assertEqual(round(bbox2.ur.N), float(556890))
        #bbox2.plot('b:')
        
        plt.show()
        
        
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestBbox("testPlotBbox"))
    runner = unittest.TextTestRunner()
    runner.run(suite)