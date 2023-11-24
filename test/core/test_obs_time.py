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
        
    def test_compare(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s.2z")
        
        date1 = '2018-06-15 13:21:46.00'
        t1 = ObsTime.readTimestamp(date1)
        
        date2 = '2018-06-15 13:21:46.00'
        t2 = ObsTime.readTimestamp(date2)
        
        date3 = '2018-06-15 13:21:46.057'
        t3 = ObsTime.readTimestamp(date3)
        
        date4 = '2018-06-15 14:21:46.057'
        t4 = ObsTime.readTimestamp(date4)
        
        date7 = '2018-06-16 13:21:46.057'
        t7 = ObsTime.readTimestamp(date7)
        
        date5 = '2018-07-15 13:21:46.057'
        t5 = ObsTime.readTimestamp(date5)
        
        date6 = '2012-06-15 13:21:46.057'
        t6 = ObsTime.readTimestamp(date6)
        
        self.assertTrue(t1 == t2)
        self.assertTrue(t3 == t3)
        self.assertFalse(t1 == t3)
        
        self.assertFalse(t3 == t4)
        self.assertFalse(t3 == t5)
        self.assertFalse(t3 == t6)
        self.assertFalse(t3 == t7)
        
        self.assertTrue(not t1 == t3)
        self.assertTrue(not t3 == t4)
        self.assertTrue(not t3 == t5)
        self.assertTrue(not t3 == t6)
        self.assertTrue(not t3 == t7)
        
        self.assertFalse(t3 == None)
        
        # ---------------------------------
        self.assertTrue(t4 > t3)
        self.assertTrue(t5 > t3)
        self.assertTrue(t3 > t6)
        self.assertTrue(t7 > t3)
        
        # ---------------------------------
        self.assertTrue(t3 < t4)
        self.assertTrue(t3 < t5)
        self.assertTrue(t6 < t3)
        self.assertTrue(t3 < t7)
        
        
    def test_add(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s.2z")
        
        date1 = '2018-06-15 13:21:46.00'
        t1 = ObsTime.readTimestamp(date1)
        t3 = t1.addMin(5)
        
        date2 = '2018-06-15 13:26:46.00'
        t2 = ObsTime.readTimestamp(date2)
        
        self.assertTrue(t3 == t2)
        
        t4 = t1.addDay(4)
        date5 = '2018-06-19 13:21:46.00'
        t5 = ObsTime.readTimestamp(date5)
        
        self.assertTrue(t4 == t5)
        
        
if __name__ == '__main__':
    
    suite = unittest.TestSuite()
    
    suite.addTest(TestObsTime("test_read_with_format"))
    suite.addTest(TestObsTime("test_readunixtime"))
    suite.addTest(TestObsTime("test_compare"))
    suite.addTest(TestObsTime("test_add"))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)
    
    
    