# -*- coding: utf-8 -*-

import unittest
import matplotlib.pyplot as plt
from tracklib import (Obs, ObsTime, ENUCoords, 
                      Track, TrackReader,
#                      TimeConstraint,
                      isSegmentIntersects,
                      azimut,
                      proj_segment,
                      proj_polyligne,
                      dist_point_droite,
                      intersection,
                      detect_side)


class TestGeometry(unittest.TestCase):
    
    __epsilon = 0.001
    
    def testIntersectionCelluleSegment(self):
        
        x1 = 1.2
        y1 = 1.3
        x2 = 4.8
        y2 = 2.4

        segment2 = [x1,y1,x2,y2]
        
        # --------------------------------------------------------------
        # Intersect
        segment1 = [2, 1, 2, 2]
        self.assertTrue(isSegmentIntersects(segment1, segment2))
        
        segment1 = [3, 1, 3, 2]
        self.assertTrue(isSegmentIntersects(segment1, segment2))
        
        segment1 = [3, 2, 4, 2]
        self.assertTrue(isSegmentIntersects(segment1, segment2))
        
        segment1 = [4, 2, 4, 3]
        self.assertTrue(isSegmentIntersects(segment1, segment2))
        
        
        # --------------------------------------------------------------
        # Non intersect
        segment1 = [1, 1, 1, 2]
        self.assertFalse(isSegmentIntersects(segment1, segment2))
        segment1 = [1, 1, 2, 1]
        self.assertFalse(isSegmentIntersects(segment1, segment2))
        segment1 = [1, 2, 2, 2]
        self.assertFalse(isSegmentIntersects(segment1, segment2))
        
        segment1 = [2, 1, 3, 1]
        self.assertFalse(isSegmentIntersects(segment1, segment2))
        segment1 = [2, 2, 3, 2]
        self.assertFalse(isSegmentIntersects(segment1, segment2))
        
        segment1 = [3, 2, 3, 3]
        self.assertFalse(isSegmentIntersects(segment1, segment2))
        segment1 = [3, 3, 4, 3]
        self.assertFalse(isSegmentIntersects(segment1, segment2))
        
        segment1 = [4, 2, 5, 2]
        self.assertFalse(isSegmentIntersects(segment1, segment2))
        segment1 = [5, 2, 5, 3]
        self.assertFalse(isSegmentIntersects(segment1, segment2))
        segment1 = [4, 3, 5, 3]
        self.assertFalse(isSegmentIntersects(segment1, segment2))
        
        segment1 = [2, 2, 2, 3]
        self.assertFalse(isSegmentIntersects(segment1, segment2))
        segment1 = [2, 3, 3, 3]
        self.assertFalse(isSegmentIntersects(segment1, segment2))
        
        segment1 = [4, 1, 4, 2]
        self.assertFalse(isSegmentIntersects(segment1, segment2))
        
        
    def testAzimuth(self):
        
        A = [-2, -1]
        B = [-1, 0]
        self.assertLessEqual(abs(45 - azimut(A[0], A[1], B[0], B[1])), self.__epsilon, "Azimuth")
        C = [0, 1]
        self.assertLessEqual(abs(45 - azimut(A[0], A[1], C[0], C[1])), self.__epsilon, "Azimuth")
        D = [1, 2]
        self.assertLessEqual(abs(45 - azimut(A[0], A[1], D[0], D[1])), self.__epsilon, "Azimuth")
        
        
    def testProjSegment(self):
        
        segment = [0,0,10,0]
        distmin, xp, yp = proj_segment(segment, 5, 5)
        self.assertEqual(distmin, 5.0)
        self.assertEqual(xp, 5)
        self.assertEqual(yp, 0)
        
        segment = [0,0,10,0]
        distmin, xp, yp = proj_segment(segment, 15, 5)
        self.assertLessEqual(abs(distmin-7.07106), 0.001)
        self.assertEqual(xp, 10)
        self.assertEqual(yp, 0)
        
        
        segment = [10,0,10,5]
        distmin, xp, yp = proj_segment(segment, 5, 2)
        self.assertLessEqual(abs(distmin-5.3851), 0.001)
        self.assertEqual(xp, 10)
        self.assertEqual(yp, 0)
        
    
    def testProjPolyligne(self):
         
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        trace1 = Track([], 1)

        c1 = ENUCoords(0, 0, 0)
        p1 = Obs(c1, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        trace1.addObs(p1)
        
        c2 = ENUCoords(10, 0, 0)
        p2 = Obs(c2, ObsTime.readTimestamp("2018-01-01 10:00:12"))
        trace1.addObs(p2)
        
        c3 = ENUCoords(20, 0, 0)
        p3 = Obs(c3, ObsTime.readTimestamp("2018-01-01 10:00:12"))
        trace1.addObs(p3)
        
        distmin, xproj, yproj, iproj = proj_polyligne(trace1.getX(), trace1.getY(), 
                                    p1.position.getX(), p1.position.getY())
        
        self.assertEqual(distmin, 0)
        self.assertEqual(xproj, 0)
        self.assertEqual(yproj, 0)
        self.assertEqual(iproj, 0)
        
        p  = ENUCoords(16, 5, 0)
        distmin, xproj, yproj, iproj = proj_polyligne(trace1.getX(), trace1.getY(), 
                                    p.getX(), p.getY())
        
        
        self.assertEqual(distmin, 5.0)
        self.assertEqual(xproj, 16)
        self.assertEqual(yproj, 0)
        self.assertEqual(iproj, 1)
        
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # 3eme CAS
        trace1 = Track([], 1)

        c1 = ENUCoords(0, 0, 0)
        p1 = Obs(c1, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        trace1.addObs(p1)
        
        c2 = ENUCoords(10, 0, 0)
        p2 = Obs(c2, ObsTime.readTimestamp("2018-01-01 10:00:12"))
        trace1.addObs(p2)
        
        c3 = ENUCoords(10, 10, 0)
        p3 = Obs(c3, ObsTime.readTimestamp("2018-01-01 10:00:12"))
        trace1.addObs(p3)
        
        c4 = ENUCoords(20, 10, 0)
        p4 = Obs(c4, ObsTime.readTimestamp("2018-01-01 10:00:12"))
        trace1.addObs(p4)
        
        p  = ENUCoords(18, 8, 0)
        distmin, xproj, yproj, iproj = proj_polyligne(trace1.getX(), trace1.getY(), 
                                    p.getX(), p.getY())
        #trace1.plot('r-')
        #plt.plot(18, 8, 'bo')
        #plt.xlim([-5,25])
        
        self.assertEqual(distmin, 2)
        self.assertEqual(xproj, 18)
        self.assertEqual(yproj, 10)
        self.assertEqual(iproj, 2)
        

    def testDistPointDroite(self):
        param = [4, 0, 1]
        d = dist_point_droite(param, 0, 0)
        self.assertEqual(d, 0.25)
        
        
    def testIntersection(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        trace1 = Track([], 1)
        p1 = Obs(ENUCoords(0, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:00"))
        trace1.addObs(p1)
        p2 = Obs(ENUCoords(10, 0, 0), ObsTime.readTimestamp("2018-01-01 10:30:00"))
        trace1.addObs(p2)
        p3 = Obs(ENUCoords(30, 0, 0), ObsTime.readTimestamp("2018-01-01 11:30:00"))
        trace1.addObs(p3)
        
        trace2 = Track([], 1)
        p1 = Obs(ENUCoords(5, 5, 0), ObsTime.readTimestamp("2018-01-01 10:40:00"))
        trace2.addObs(p1)
        p2 = Obs(ENUCoords(5, -5, 0), ObsTime.readTimestamp("2018-01-01 11:00:00"))
        trace2.addObs(p2)
        p3 = Obs(ENUCoords(15, -5, 0), ObsTime.readTimestamp("2018-01-01 11:10:00"))
        trace2.addObs(p3)
        p4 = Obs(ENUCoords(15, 5, 0), ObsTime.readTimestamp("2018-01-01 11:20:00"))
        trace2.addObs(p4)
        
        T = intersection(trace1 ,trace2, -1)
        self.assertEqual(T.size(), 2)
        self.assertEqual(T[0].position.getX(), 5.0)
        self.assertEqual(T[0].position.getY(), 0.0)
        self.assertEqual(T[1].position.getX(), 15.0)
        self.assertEqual(T[1].position.getY(), 0.0)
        self.assertEqual(str(T[0].timestamp), '01/01/2018 10:00:00')
        self.assertEqual(str(T[1].timestamp), '01/01/2018 10:30:00')
        
        T = intersection(trace1 ,trace2, 1000)
        self.assertEqual(T.size(), 0)
        
        T = intersection(trace1 ,trace2, 2000)
        self.assertEqual(T.size(), 1)
        self.assertEqual(T[0].position.getX(), 15.0)
        self.assertEqual(T[0].position.getY(), 0.0)
        self.assertEqual(str(T[0].timestamp), '01/01/2018 10:30:00')
        
        T = intersection(trace1 ,trace2, 3000)
        self.assertEqual(T.size(), 2)
        self.assertEqual(T[0].position.getX(), 5.0)
        self.assertEqual(T[0].position.getY(), 0.0)
        self.assertEqual(str(T[0].timestamp), '01/01/2018 10:00:00')
        self.assertEqual(T[1].position.getX(), 15.0)
        self.assertEqual(T[1].position.getY(), 0.0)
        self.assertEqual(str(T[1].timestamp), '01/01/2018 10:30:00')

    def testSide(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")

        # Droite
        trace1 = Track([], 1)
        p1 = Obs(ENUCoords(0, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:00"))
        trace1.addObs(p1)
        p2 = Obs(ENUCoords(10, 0, 0), ObsTime.readTimestamp("2018-01-01 10:00:12"))
        trace1.addObs(p2)
        p3 = Obs(ENUCoords(10, 10, 0), ObsTime.readTimestamp("2018-01-01 10:00:13"))
        trace1.addObs(p3)
        p4 = Obs(ENUCoords(20, 10, 0), ObsTime.readTimestamp("2018-01-01 10:00:14"))
        trace1.addObs(p4)

        s = detect_side(trace1, 18, 8)
        self.assertEqual(s, -1)

        # Gauche
        trace2 = trace1.reverse()
        s = detect_side(trace2, 18, 8)
        self.assertEqual(s, 1)

        # Line
        s = detect_side(trace1, 22, 10)
        self.assertEqual(s, 0)

        s = detect_side(trace1, 15, 5)
        self.assertEqual(s, -1)

        # Cas réél - Gauche
        x = 904436.02026022097561508
        y = 6435693.33668548986315727
        trace3 = TrackReader.parseWkt("LineString (904449.30000000004656613 6435691.5, 904445.59999999997671694 6435692, 904442.19999999995343387 6435692.70000000018626451, 904438.90000000002328306 6435692.40000000037252903, 904438.40000000002328306 6435692.5, 904438.40000000002328306 6435692.5, 904437.19999999995343387 6435696, 904435.59999999997671694 6435699.70000000018626451, 904434.69999999995343387 6435704, 904434 6435708.40000000037252903, 904433.5 6435712.70000000018626451, 904433.09999999997671694 6435716.79999999981373549, 904432.5 6435720.79999999981373549, 904432.09999999997671694 6435722.29999999981373549, 904432.09999999997671694 6435722.29999999981373549, 904431.30000000004656613 6435724.90000000037252903, 904428.59999999997671694 6435728.20000000018626451, 904425.40000000002328306 6435730.5, 904422.09999999997671694 6435733, 904418.80000000004656613 6435735.40000000037252903)")
        s = detect_side(trace3, x, y)
        self.assertEqual(s, 1)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestGeometry("testIntersectionCelluleSegment"))
    suite.addTest(TestGeometry("testAzimuth"))
    suite.addTest(TestGeometry("testProjPolyligne"))
    suite.addTest(TestGeometry("testProjSegment"))
    suite.addTest(TestGeometry("testDistPointDroite"))
    suite.addTest(TestGeometry("testIntersection"))
    suite.addTest(TestGeometry("testSide"))
    runner = unittest.TextTestRunner()
    runner.run(suite)