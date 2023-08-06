#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from tracklib import (ENUCoords, ObsTime, Obs, 
                      makeDistanceMatrix,
                      computeAbsCurv,
                      makeRPN, compLike,
                      Track)


class TestUtils(unittest.TestCase):
    
    def setUp (self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        self.trace1 = Track([], 1)
        
        c1 = ENUCoords(1.0, 5.0, 0)
        p1 = Obs(c1, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace1.addObs(p1)
        
        c2 = ENUCoords(2.0, 5.0, 0)
        p2 = Obs(c2, ObsTime.readTimestamp("2018-01-01 10:00:05"))
        self.trace1.addObs(p2)
        
        c3 = ENUCoords(3.0, 6.0, 0)
        p3 = Obs(c3, ObsTime.readTimestamp("2018-01-01 10:00:10"))
        self.trace1.addObs(p3)
        
        computeAbsCurv(self.trace1)
    
    
    def testMakeDistanceMatrixModeLinear(self):
        mode = 'linear'
        m = makeDistanceMatrix(self.trace1, mode)
        
        self.assertEqual(m[0][0], 0, "matrice des distances: [0,0]")
        self.assertEqual(m[1][1], 0, "matrice des distances: [1,1]")
        self.assertEqual(m[2][2], 0, "matrice des distances: [2,2]")
        
        
        #self.assertEqual(m[0][1], 0, "matrice des distances: [0,1]")
        
        print (m)
        
        
        # makeDistanceMatrixOld


    def test_make_RPN(self):
        
        tab = makeRPN('3 * (10 + 5 )')
        self.assertEqual(len(tab), 5)
        self.assertListEqual(['3', '10', '5', '+', '*'], tab)
        
        tab = makeRPN('a*(b+c/2)')
        self.assertEqual(len(tab), 7)
        self.assertListEqual(['a', 'b', 'c', '2', '/', '+', '*'], tab)
        
        
    def test_comp_like(self):
        a = compLike("abcdefg", "[abcdefg, abcdefgh, abcd]")
        self.assertTrue(a)
        
        a = compLike("3", "['3', '33', '333']")
        self.assertTrue(a)
        
        a = compLike("3", "['4', '44', '4444']")
        self.assertFalse(a)
        
        a = compLike("3", "['1234', '4567', '9090']")
        self.assertTrue(a)
        
        a = compLike("abcdefg", "%")
        self.assertTrue(a)
        
        a = compLike("abcdefg", "%a")
        self.assertTrue(a)
        
        a = compLike("abcdefg", "%c")
        self.assertTrue(a)

        a = compLike("abcdefg", "%bcd")
        self.assertTrue(a)
        
        a = compLike("abcdefg", "%fg")
        self.assertTrue(a)
        
        a = compLike("abcdefg", "%ag")
        self.assertFalse(a)
        
        a = compLike("abcdefg", "%z")
        self.assertFalse(a)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestUtils("testMakeDistanceMatrixModeLinear"))
    suite.addTest(TestUtils("test_make_RPN"))
    suite.addTest(TestUtils("test_comp_like"))
    runner = unittest.TextTestRunner()
    runner.run(suite)



