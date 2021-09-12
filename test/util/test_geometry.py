# -*- coding: utf-8 -*-

import unittest

import tracklib.util.Geometry as Geometry


class TestGeometry(unittest.TestCase):
    
    __epsilon = 0.001
    
    def testIntersectionCelluleSegment(self):
        
        x1 = 1.2
        y1 = 1.3
        x2 = 4.8
        y2 = 2.4

        segment2 = [x1,y1,x2,y2]
        
        # --------------------------------------------------------------
        # Intersect
        segment1 = [2, 1, 2, 2]
        self.assertTrue(Geometry.isSegmentIntersects(segment1, segment2))
        
        segment1 = [3, 1, 3, 2]
        self.assertTrue(Geometry.isSegmentIntersects(segment1, segment2))
        
        segment1 = [3, 2, 4, 2]
        self.assertTrue(Geometry.isSegmentIntersects(segment1, segment2))
        
        segment1 = [4, 2, 4, 3]
        self.assertTrue(Geometry.isSegmentIntersects(segment1, segment2))
        
        
        # --------------------------------------------------------------
        # Non intersect
        segment1 = [1, 1, 1, 2]
        self.assertFalse(Geometry.isSegmentIntersects(segment1, segment2))
        segment1 = [1, 1, 2, 1]
        self.assertFalse(Geometry.isSegmentIntersects(segment1, segment2))
        segment1 = [1, 2, 2, 2]
        self.assertFalse(Geometry.isSegmentIntersects(segment1, segment2))
        
        segment1 = [2, 1, 3, 1]
        self.assertFalse(Geometry.isSegmentIntersects(segment1, segment2))
        segment1 = [2, 2, 3, 2]
        self.assertFalse(Geometry.isSegmentIntersects(segment1, segment2))
        
        segment1 = [3, 2, 3, 3]
        self.assertFalse(Geometry.isSegmentIntersects(segment1, segment2))
        segment1 = [3, 3, 4, 3]
        self.assertFalse(Geometry.isSegmentIntersects(segment1, segment2))
        
        segment1 = [4, 2, 5, 2]
        self.assertFalse(Geometry.isSegmentIntersects(segment1, segment2))
        segment1 = [5, 2, 5, 3]
        self.assertFalse(Geometry.isSegmentIntersects(segment1, segment2))
        segment1 = [4, 3, 5, 3]
        self.assertFalse(Geometry.isSegmentIntersects(segment1, segment2))
        
        segment1 = [2, 2, 2, 3]
        self.assertFalse(Geometry.isSegmentIntersects(segment1, segment2))
        segment1 = [2, 3, 3, 3]
        self.assertFalse(Geometry.isSegmentIntersects(segment1, segment2))
        
        segment1 = [4, 1, 4, 2]
        self.assertFalse(Geometry.isSegmentIntersects(segment1, segment2))
        
        
    def testAzimuth(self):
        
        A = [-2, -1]
        B = [-1, 0]
        self.assertLessEqual(abs(45 - Geometry.azimut(A[0], A[1], B[0], B[1])), self.__epsilon, "Azimuth")
        C = [0, 1]
        self.assertLessEqual(abs(45 - Geometry.azimut(A[0], A[1], C[0], C[1])), self.__epsilon, "Azimuth")
        D = [1, 2]
        self.assertLessEqual(abs(45 - Geometry.azimut(A[0], A[1], D[0], D[1])), self.__epsilon, "Azimuth")
        
        
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestGeometry("testIntersectionCelluleSegment"))
    suite.addTest(TestGeometry("testAzimuth"))
    runner = unittest.TextTestRunner()
    runner.run(suite)