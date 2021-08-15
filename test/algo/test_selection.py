# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner


class TestSelection(TestCase):
    
    def setUp (self):
        pass
    
    def test_selection(self):
        print ('1')
    
    
if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestSelection("test_selection"))
    runner = TextTestRunner()
    runner.run(suite)