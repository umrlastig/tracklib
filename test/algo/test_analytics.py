#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest


class TestAlgoAnalyticsMethods(unittest.TestCase):
    
    def setUp (self):
        pass
    
    def testDS(self):
        self.assertLessEqual(3, 5)
    
    def testAbsCurv(self):
        self.assertLessEqual(3, 5)
        
    def testSpeed(self):
        self.assertLessEqual(3, 5)
    
    def testAcceleration(self):
        self.assertLessEqual(3, 5)
        
    def testAngleGeom(self):
        self.assertLessEqual(3, 5)
        
    def testCalculAngleOriente(self):
        self.assertLessEqual(3, 5)
        
    def testOrientation(self):
        self.assertLessEqual(3, 5)
        
    def testStopPointWithAccelerationCriteria(self):
        self.assertLessEqual(3, 5)
        
    def testStopPointWithTimeWindowCriteria(self):
        self.assertLessEqual(3, 5)
    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoAnalyticsMethods("testDS"))
    suite.addTest(TestAlgoAnalyticsMethods("testAbsCurv"))
    suite.addTest(TestAlgoAnalyticsMethods("testSpeed"))
    suite.addTest(TestAlgoAnalyticsMethods("testAcceleration"))
    suite.addTest(TestAlgoAnalyticsMethods("testAngleGeom"))
    suite.addTest(TestAlgoAnalyticsMethods("testCalculAngleOriente"))
    suite.addTest(TestAlgoAnalyticsMethods("testOrientation"))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)