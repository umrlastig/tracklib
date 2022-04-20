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
        self.assertEqual("31/01/2018 13:21:46", str(t)[0:19])
        
        GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2s1Z")
        madate = '2018-01-31T11:17:46Z'
        t = GPSTime.readTimestamp(madate)
        self.assertEqual("31/01/2018 11:17:46", str(t)[0:19])
        
        d = GPSTime.readUnixTime(1550941038.0)
        self.assertIsInstance(d, GPSTime)
        self.assertEqual('23/02/2019 16:57:18', str(d)[0:19])
        self.assertEqual(23, d.day)
        self.assertEqual(2, d.month)
        self.assertEqual(2019, d.year)
        self.assertEqual(16, d.hour)
        self.assertEqual(57, d.min)
        self.assertEqual(18, d.sec)
        
        
if __name__ == '__main__':
    #unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestGPSTime("test_format_time"))
    runner = unittest.TextTestRunner()
    runner.run(suite)