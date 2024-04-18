#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import unittest

import tracklib as tkl


class TestKernel(unittest.TestCase):
    
    __epsilon = 0.001
    
    def setUp (self):
        pass
        
		
    def test_sinc_kernel(self):
        k = tkl.SincKernel(7)
        k.plot()
        
        s = str(k)
        self.assertEqual(s, "Sinc kernel (width=7.0)")
        
        a = k.evaluate(0)
        self.assertLessEqual(abs(a - 0.4547), self.__epsilon, "k(0)")
        a = k.evaluate(5)
        self.assertLessEqual(abs(a - 0.0482), self.__epsilon, "k(5)")
        
        print (a)
        scale = 0.1 * 5
        b = scale * math.sin((a + 1e-300) / scale) / (a + 1e-300) / (math.pi * scale)
        print (b)


if __name__ == '__main__':
    
    suite = unittest.TestSuite()
    
    suite.addTest(TestKernel("test_sinc_kernel"))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)