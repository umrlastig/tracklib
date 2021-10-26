# -*- coding: utf-8 -*-

import unittest

from algo.test_segmentation import TestAlgoSegmentationMethods
from algo.test_geometrics import TestAlgoGeometricsMethods
from algo.test_selection import TestSelection
from core.test_grille import TestGrille


if __name__ == '__main__':
    
    # =========================================================================
    suite = unittest.TestSuite()
    
    # =========================================================================
    #  ANALYTICS
    
    # =========================================================================
    #  GEOMETRICS
    suite.addTest(TestAlgoGeometricsMethods("testCircleTrigo"))
    suite.addTest(TestAlgoGeometricsMethods("testCircles"))
    suite.addTest(TestAlgoGeometricsMethods("testDiameter"))
    suite.addTest(TestAlgoGeometricsMethods("testConvexHull"))
    suite.addTest(TestAlgoGeometricsMethods("testminimumBoundingRectangle"))
    
    # =========================================================================
    #  SEGMENTATION
    suite.addTest(TestAlgoSegmentationMethods("testFindStopsLocal"))
    
    # =========================================================================
    #  SELECTION
    suite.addTest(TestSelection("test_selection_one_timestamp_constraint"))
    suite.addTest(TestSelection("test_selection_one_shape_constraint"))
    suite.addTest(TestSelection("test_selection_one_shape_time_constraint"))
    suite.addTest(TestSelection("test_selection_track_constraint"))
    suite.addTest(TestSelection("test_selection_combinaison_constraint"))
    
    # =========================================================================
    #  SIMPLIFICATION
    
    
    # =========================================================================
    #  SUMMARIZE
    suite.addTest(TestGrille("test_summarize_af"))
    
    
    # =========================================================================
    # =========================================================================
    runner = unittest.TextTestRunner()
    runner.run(suite)
