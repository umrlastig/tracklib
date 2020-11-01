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
		self.assertTrue(1==1)
		
	

	
if __name__ == '__main__':
    #unittest.main()
	suite = unittest.TestSuite()
	suite.addTest(TestNanMethods("test_nan_segmentation"))
	runner = unittest.TextTestRunner()
	runner.run(suite)
	
	