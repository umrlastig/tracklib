#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('../tracklib/'))


class TestNanMethods(unittest.TestCase):

    def test_nan_segmentation(self):
        a = 3
        b = 3
        self.assertTrue(a==b)




if __name__ == '__main__':
    #unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestNanMethods("test_nan_segmentation"))
    runner = unittest.TextTestRunner()
    runner.run(suite)

