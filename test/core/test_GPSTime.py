#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

import unittest

from tracklib.core.ObsTime import ObsTime


class TestGPSTime(unittest.TestCase):

    def test_format_time(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        madate = '2018-01-31 13:21:46'
        t = ObsTime.readTimestamp(madate)
        self.assertEqual("31/01/2018 13:21:46", str(t)[0:19])
        
        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2s1Z")
        madate = '2018-01-31T11:17:46Z'
        t = ObsTime.readTimestamp(madate)
        self.assertEqual("31/01/2018 11:17:46", str(t)[0:19])
        
        # GPSTime.setReadFormat("2s")
        # madate = '1345841684000'
        # t = GPSTime.readTimestamp(madate)
        # print (t)
        
    def test_readunixtime(self):
        
        d = ObsTime.readUnixTime(1550941038.0)
        self.assertIsInstance(d, ObsTime)
        self.assertEqual('23/02/2019 16:57:18', str(d)[0:19])
        self.assertEqual(23, d.day)
        self.assertEqual(2, d.month)
        self.assertEqual(2019, d.year)
        self.assertEqual(16, d.hour)
        self.assertEqual(57, d.min)
        self.assertEqual(18, d.sec)
        
        
        d = ObsTime.readUnixTime(1334665563298 * 1e-3)
        print (d)
        self.assertIsInstance(d, ObsTime)
        self.assertEqual('17/04/2012 12:26:03', str(d)[0:19])
        self.assertEqual(17, d.day)
        self.assertEqual(4, d.month)
        self.assertEqual(2012, d.year)
        self.assertEqual(12, d.hour)
        self.assertEqual(26, d.min)
        self.assertEqual(3, d.sec)
        
        
if __name__ == '__main__':
    #unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestGPSTime("test_format_time"))
    suite.addTest(TestGPSTime("test_readunixtime"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
    
    
    