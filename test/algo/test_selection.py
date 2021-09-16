# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os.path
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.algo.Selection import Constraint, TimeConstraint, Selector, GlobalSelector
import tracklib.algo.Geometrics as Geometrics
from tracklib.core.GPSTime import GPSTime
from tracklib.io.FileReader import FileReader

class TestSelection(TestCase):

    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")


    # 31/07/2018 11:36:55
    # 31/07/2018 17:57:41
    def test_selection_one_timestamp_constraint(self):
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        chemin = os.path.join(self.resource_path, './data/trace1.dat')
        trace = FileReader.readFromFile(chemin, 2, 3, -1, 4, separator=",")

        t1 = TimeConstraint(begin=GPSTime('2018-07-31 14:00:00'))
        c = Constraint(time = t1)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(trace)
        self.assertTrue(isSelection)

        t2 = TimeConstraint(begin=GPSTime('2018-07-31 18:00:00'))
        c = Constraint(time = t2)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(trace)
        self.assertFalse(isSelection)
        
        t3 = TimeConstraint(begin=GPSTime('2018-07-31 11:35:00'), end=GPSTime('2018-07-31 17:55:00'))
        c = Constraint(time = t3)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(trace)
        self.assertTrue(isSelection)
        
        t4 = TimeConstraint(begin=GPSTime('2018-07-31 12:13:58'), end=GPSTime('2018-07-31 14:03:41'))
        c = Constraint(time = t4)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(trace)
        self.assertTrue(isSelection)
        
        t5 = TimeConstraint(begin=GPSTime('2018-07-31 18:01:58'), end=GPSTime('2018-07-31 18:03:41'))
        c = Constraint(time = t5)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(trace)
        self.assertFalse(isSelection)
        
        t6 = TimeConstraint(begin=GPSTime('2015-07-31 18:01:58'), end=GPSTime('2018-06-28 14:03:41'))
        c = Constraint(time = t6)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(trace)
        self.assertFalse(isSelection)
        
        t7 = TimeConstraint(begin=GPSTime('2018-07-31 18:01:58'), end=GPSTime('2018-07-31 18:03:41'))
        c = Constraint(time = t7)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(trace)
        self.assertFalse(isSelection)

        t8 = TimeConstraint(begin=GPSTime('2018-07-31 05:03:04'), end=GPSTime('2018-07-31 05:45:09'))
        c = Constraint(time = t8)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(trace)
        self.assertFalse(isSelection)
        
        t9 = TimeConstraint(begin=GPSTime('2018-07-31 17:57:59'), end=GPSTime('2018-07-31 18:12:01'))
        c = Constraint(time = t9)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(trace)
        self.assertFalse(isSelection)


    def test_selection_one_shape_constraint(self):
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        chemin = os.path.join(self.resource_path, './data/trace1.dat')
        trace = FileReader.readFromFile(chemin, 2, 3, -1, 4, separator=",")
        trace.plot()

        circle = Geometrics.Circle(trace.getLastObs().position, 10)
        print (circle.center.getX(), circle.center.getY(), circle.radius)
        circle.plot()

        #plt.plot(track.getX(), track.getY(), 'b+')
        plt.show()
        
        #c1 = Constraint(circle, track)
        #t = c1.contains(track)
        #print (t)
        #tr = c1.select(track)
        #print (type(t))
        #print (track.size(), track.length())
    
    
    
        
    
if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestSelection("test_selection_one_timestamp_constraint"))
    suite.addTest(TestSelection("test_selection_one_shape_constraint"))
    runner = TextTestRunner()
    runner.run(suite)