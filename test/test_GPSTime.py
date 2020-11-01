#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

import unittest

from tracklib.core.GPSTime import GPSTime


class TestGPSTime(unittest.TestCase):

    def test_format_time(self):
        
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        madate = '2018-01-31 13:21:46'
        t = GPSTime.readTimestamp(madate)
        self.assertEqual("31/01/2018 13:21:46", str(t))
        
        GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2s1Z")
        madate = '2018-01-31T11:17:46Z'
        t = GPSTime.readTimestamp(madate)
        self.assertEqual("31/01/2018 11:17:46", str(t))
        
        print (GPSTime.readUnixTime(1550941038.0))
        
        
if __name__ == '__main__':
    #unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestGPSTime("test_format_time"))
    runner = unittest.TextTestRunner()
    runner.run(suite)