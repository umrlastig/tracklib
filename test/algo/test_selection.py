# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os.path
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib import (Obs, ObsTime, ENUCoords, Track,
                      Circle, Rectangle, TrackReader,
                      Selector, GlobalSelector,
                      Constraint, TimeConstraint, TrackConstraint, TollGateConstraint,
                      MODE_INSIDE, MODE_CROSSES, MODE_GETS_IN, MODE_GETS_OUT,
                      MODE_PARALLEL, COMBINATION_OR, COMBINATION_AND)




class TestSelection(TestCase):

    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        
        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        chemin = os.path.join(self.resource_path, './data/gpx/activity_5807084803.gpx')
        tracks = TrackReader.readFromGpx(chemin)
        self.trace = tracks.getTrack(0)

        # Transformation GEO coordinates to ENU
        self.trace.toENUCoordsIfNeeded()
        #self.trace.summary()
        
        #query  = " SELECT * "
        #query += " WHERE timestamp <= 2020-11-11 15:44:15 "
        #query += "   WHERE timestamp >= 2020-11-11 15:42:05 "
        #self.trace = self.trace.query(query)
        #print (self.trace.size())
        
        #self.trace.plot()

    
    # 31/07/2018 11:36:55
    # 31/07/2018 17:57:41
    def test_selection_one_timestamp_constraint(self):

        t1 = TimeConstraint(begin=ObsTime('2020-11-11 15:42:05'))
        c = Constraint(time = t1)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        t2 = TimeConstraint(begin=ObsTime('2020-11-11 15:52:01'))
        c = Constraint(time = t2)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        t2 = TimeConstraint()
        t2.setMinTimestamp(ObsTime('2020-11-11 15:52:01'))
        c = Constraint(time = t2)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        t3 = TimeConstraint(begin=ObsTime('2020-11-11 15:40:00'), end=ObsTime('2020-11-11 15:50:00'))
        c = Constraint(time = t3)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        t3 = TimeConstraint()
        t3.setMinTimestamp(ObsTime('2020-11-11 15:40:00'))
        t3.setMaxTimestamp(ObsTime('2020-11-11 15:50:00'))
        c = Constraint(time = t3)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        t4 = TimeConstraint(begin=ObsTime('2020-11-10 15:40:00'), end=ObsTime('2020-11-11 15:40:00'))
        c = Constraint(time = t4)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        t5 = TimeConstraint(begin=ObsTime('2020-11-11 15:52:01'), end=ObsTime('2020-11-11 15:53:41'))
        c = Constraint(time = t5)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        t6 = TimeConstraint(begin=ObsTime('2020-11-10 15:52:01'), end=ObsTime('2020-11-11 15:38:41'))
        c = Constraint(time = t6)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        t7 = TimeConstraint(begin=ObsTime('2020-11-11 18:01:58'), end=ObsTime('2020-11-11 18:03:41'))
        c = Constraint(time = t7)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        t8 = TimeConstraint(begin=ObsTime('2018-11-11 15:40:04'), end=ObsTime('2018-11-11 15:45:09'))
        c = Constraint(time = t8)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        t9 = TimeConstraint(begin=ObsTime('2021-11-11 14:57:59'), end=ObsTime('2021-11-11 18:12:01'))
        c = Constraint(time = t9)
        s = Selector([c])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        

    def test_selection_one_shape_constraint(self):
        
        center = self.trace.getObs(int(self.trace.size()/2)).position
        radius = 200
        circle1 = Circle(center, radius)
        
        c1 = Constraint(shape = circle1, mode = MODE_CROSSES)
        s = Selector([c1])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        c2 = Constraint(shape = circle1, mode = MODE_INSIDE)
        s = Selector([c2])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        c3 = Constraint(shape = circle1, mode = MODE_GETS_IN)
        s = Selector([c3])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        c4 = Constraint(shape = circle1, mode = MODE_GETS_OUT)
        s = Selector([c4])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        # -------------------------------------------------------
        
        center = self.trace.getObs(int(self.trace.size()/2)).position
        radius = 30
        circle2 = Circle(center, radius)
        #circle2.plot()
        #plt.show()
        
        c1 = Constraint(shape = circle2, mode = MODE_CROSSES)
        s = Selector([c1])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        c2 = Constraint(shape = circle2, mode = MODE_INSIDE)
        s = Selector([c2])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        c3 = Constraint(shape = circle2, mode = MODE_GETS_IN)
        s = Selector([c3])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        c4 = Constraint(shape = circle2, mode = MODE_GETS_OUT)
        s = Selector([c4])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        # -------------------------------------------------------
        center = self.trace.getObs(0).position
        radius = 30
        circle3 = Circle(center, radius)
        #self.trace.plot()
        #circle3.plot()
        #plt.show()
        
        c1 = Constraint(shape = circle3, mode = MODE_CROSSES)
        s = Selector([c1])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        c2 = Constraint(shape = circle3, mode = MODE_INSIDE)
        s = Selector([c2])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        c3 = Constraint(shape = circle3, mode = MODE_GETS_IN)
        s = Selector([c3])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        c4 = Constraint(shape = circle3, mode = MODE_GETS_OUT)
        s = Selector([c4])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        # -------------------------------------------------------
        pt = self.trace.getObs(int(self.trace.size()/2)).position
        center = ENUCoords(pt.getX() + 10000, pt.getY() + 30000)
        radius = 30
        circle4 = Circle(center, radius)
        #circle4.plot()
        #plt.show()
        
        c1 = Constraint(shape = circle4, mode = MODE_CROSSES)
        s = Selector([c1])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        c2 = Constraint(shape = circle4, mode = MODE_INSIDE)
        s = Selector([c2])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        c3 = Constraint(shape = circle4, mode = MODE_GETS_IN)
        s = Selector([c3])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        c4 = Constraint(shape = circle4, mode = MODE_GETS_OUT)
        s = Selector([c4])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        

    def test_selection_one_shape_time_constraint(self):
        
        t1 = TimeConstraint(begin=ObsTime('2020-11-11 14:42:00'))
        t3 = TimeConstraint(begin=ObsTime('2020-11-11 15:42:00'))
        t2 = TimeConstraint(begin=ObsTime('2020-11-11 16:42:00'))
        
        center = self.trace.getObs(int(self.trace.size()/2)).position
        radius = 30
        circle1 = Circle(center, radius)
        #circle1.plot()
        #plt.show()
        
        pt = self.trace.getObs(int(self.trace.size()/2)).position
        center = ENUCoords(pt.getX() + 10000, pt.getY() + 30000)
        radius = 10000
        circle4 = Circle(center, radius)
        
        # =====================================================================
        c1 = Constraint(shape = circle1, time=t1, mode = MODE_CROSSES)
        s = Selector([c1])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        # =====================================================================
        c1 = Constraint(shape = circle1, time=t2, mode = MODE_CROSSES)
        s = Selector([c1])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        # =====================================================================
        c1 = Constraint(shape = circle1, time=t3, mode = MODE_CROSSES)
        s = Selector([c1])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        # =====================================================================
        c1 = Constraint(shape = circle4, time=t1, mode = MODE_CROSSES)
        s = Selector([c1])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        

    def test_selection_track_constraint(self):
        
        trace1 = Track()
        c1 = self.trace.getObs(0).position
        c0 = ENUCoords(c1.getX() + 25, c1.getY())
        c2 = ENUCoords(c1.getX() - 25, c1.getY())
        c3 = ENUCoords(c1.getX() - 110, c1.getY())
        p1 = Obs(c0, ObsTime.readTimestamp("2020-11-11 15:42:00"))
        p2 = Obs(c1, ObsTime.readTimestamp("2020-11-11 15:43:00"))
        p3 = Obs(c2, ObsTime.readTimestamp("2020-11-11 15:44:00"))
        p4 = Obs(c3, ObsTime.readTimestamp("2020-11-11 15:45:00"))
        trace1.addObs(p1)
        trace1.addObs(p2)
        trace1.addObs(p3)
        trace1.addObs(p4)
        #plt.plot(trace1.getX(), trace1.getY(), 'r-')
        #self.trace.plot()
        #plt.show()
        
        c3 = TrackConstraint(trace1, mode=MODE_PARALLEL, length=0)
        #c3.plot()
        #plt.show()
        s = Selector([c3])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        c4 = TrackConstraint(trace1, mode=MODE_CROSSES)
        s = Selector([c4])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        # =====================================================================
        trace1 = Track()
        c0 = ENUCoords(self.trace.getObs(134).position.getX(), self.trace.getObs(134).position.getY())
        c1 = ENUCoords(self.trace.getObs(135).position.getX(), self.trace.getObs(135).position.getY())
        c2 = ENUCoords(self.trace.getObs(136).position.getX(), self.trace.getObs(136).position.getY())
        p1 = Obs(c0, ObsTime.readTimestamp("2020-11-11 15:42:00"))
        p2 = Obs(c1, ObsTime.readTimestamp("2020-11-11 15:43:00"))
        p3 = Obs(c2, ObsTime.readTimestamp("2020-11-11 15:44:00"))
        trace1.addObs(p1)
        trace1.addObs(p2)
        trace1.addObs(p3)
        #self.trace.plot()
        #plt.plot(trace1.getX(), trace1.getY(), 'r-')
        
        c3 = TrackConstraint(trace1, mode=MODE_PARALLEL)
        #c3.plot()
        s = Selector([c3])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        c4 = TrackConstraint(trace1, mode=MODE_CROSSES)
        #c4.plot()
        s = Selector([c4])
        selector = GlobalSelector([s])
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        plt.show()
        

    def test_selection_combinaison_constraint(self):
        
        #self.trace.plot()
        
        t1 = TimeConstraint(begin=ObsTime('2020-11-11 15:40:00'))
        t3 = TimeConstraint(begin=ObsTime('2020-11-10 15:40:00'))
        
        center = self.trace.getObs(int(self.trace.size()/2)).position
        radius = 40
        circle1 = Circle(center, radius)
        #circle1.plot('b-')
        
        pt = self.trace.getObs(int(self.trace.size()/2)).position
        ll = ENUCoords(pt.getX() + 1, pt.getY() + 15)
        ur = ENUCoords(pt.getX() + 10, pt.getY() + 40)
        rect1 = Rectangle(ll, ur)
        #rect1.plot()

        # =====================================================================
        c1 = Constraint(shape = circle1, time=t1, mode = MODE_CROSSES)
        s1 = Selector([c1])
        c2 = Constraint(shape = rect1, time=t3, mode = MODE_CROSSES)
        s2 = Selector([c2])
        
        selector = GlobalSelector([s1,s2])
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        selector = GlobalSelector([s1,s2], combination = COMBINATION_OR)
        isSelection = selector.contains(self.trace)
        self.assertTrue(isSelection)
        
        selector = GlobalSelector([s1,s2], combination = COMBINATION_AND)
        isSelection = selector.contains(self.trace)
        self.assertFalse(isSelection)
        
        
    def test_print(self):
        
        # ---------------------------------------------------------------------
        t1 = TimeConstraint()
        t1.setMinTimestamp(ObsTime('2020-11-11 15:19:00'))
        t1.setMaxTimestamp(ObsTime('2020-11-11 17:55:00'))
        print (t1)
        c = Constraint(time = t1)
        s = Selector([c])
        selector = GlobalSelector([s])
        print (selector)
        
        # ---------------------------------------------------------------------
        center = ENUCoords(0,0)
        circle = Circle(center, 1)
        c1 = Constraint(shape = circle, time=t1, mode = MODE_INSIDE)
        s = Selector([c1])
        self.assertEqual(1, len(s))
        selector = GlobalSelector([s])
        print (selector)
        selector.plot()
        self.assertEqual(1, len(selector))
        
        
        # ---------------------------------------------------------------------
        t1 = TimeConstraint(begin=ObsTime('2018-07-31 14:00:00'))
        t1.setMaxTimestamp(ObsTime('2018-07-31 17:55:00'))
        center = self.trace.getObs(int(self.trace.size()/2)).position
        radius = 91000
        circle1 = Circle(center, radius)
        
        c1 = Constraint(time=t1)
        c1.setShape(circle1)
        print (c1)
        s = Selector([c1])
        selector = GlobalSelector([s])
        self.assertEqual(1, selector.numberOfConstraints())
        selector.plot()

        # ---------------------------------------------------------------------
        trace1 = Track()
        c0 = ENUCoords(self.trace.getObs(49).position.getX(), self.trace.getObs(49).position.getY())
        c1 = ENUCoords(self.trace.getObs(50).position.getX(), self.trace.getObs(50).position.getY())
        c2 = ENUCoords(self.trace.getObs(51).position.getX(), self.trace.getObs(51).position.getY())
        p1 = Obs(c0, ObsTime.readTimestamp("2018-07-31 14:00:00"))
        p2 = Obs(c1, ObsTime.readTimestamp("2018-07-31 14:01:00"))
        p3 = Obs(c2, ObsTime.readTimestamp("2018-07-31 14:02:00"))
        trace1.addObs(p1)
        trace1.addObs(p2)
        trace1.addObs(p3)
        self.trace.plot()
        plt.plot(trace1.getX(), trace1.getY(), 'r-')
        
        c3 = TrackConstraint(trace1, mode=MODE_PARALLEL)
        s = Selector([c3])
        selector = GlobalSelector([s])
        print (selector)
        
        # ---------------------------------------------------------------------
        

    def test_toll_gate(self):
        
        #tg = TollGateConstraint()
        
        pass

    
        
        
if __name__ == '__main__':
    
    suite = TestSuite()
    
    suite.addTest(TestSelection("test_print"))
    suite.addTest(TestSelection("test_selection_one_timestamp_constraint"))
    suite.addTest(TestSelection("test_selection_one_shape_constraint"))
    suite.addTest(TestSelection("test_selection_one_shape_time_constraint"))
    suite.addTest(TestSelection("test_selection_track_constraint"))
    suite.addTest(TestSelection("test_selection_combinaison_constraint"))
    suite.addTest(TestSelection("test_toll_gate"))
    
    runner = TextTestRunner()
    runner.run(suite)
    
    