#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

import unittest
from tracklib import (ObsTime)

class TestObsTime(unittest.TestCase):

    def test_read_with_format(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        madate = '2018-01-31 13:21:46'
        t = ObsTime.readTimestamp(madate)
        self.assertEqual("31/01/2018 13:21:46", str(t)[0:19])
        
        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2s1Z")
        madate = '2018-01-31T11:17:46Z'
        t = ObsTime.readTimestamp(madate)
        self.assertEqual("31/01/2018 11:17:46", str(t)[0:19])
        
        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2s.2zZ")
        madate = '2023-10-15T06:33:22.750000Z'
        t = ObsTime.readTimestamp(madate)
        ObsTime.setPrintFormat("4Y-2M-2D 2h:2m:2s.2z")
        self.assertEqual("2023-10-15 06:33:22", str(t)[0:19])
        self.assertEqual("2023-10-15 06:33:22.75", str(t)[0:22])
        
    def test_readunixtime(self):
        ObsTime.setPrintFormat("2D/2M/4Y 2h:2m:2s.2z")
        
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
    suite.addTest(TestObsTime("test_read_with_format"))
    suite.addTest(TestObsTime("test_readunixtime"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
    
    
    