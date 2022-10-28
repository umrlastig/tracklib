# -*- coding: utf-8 -*-

import math
import unittest
import matplotlib.pyplot as plt

from tracklib.core.GPSTime import GPSTime
from tracklib.core.Coords import ENUCoords
from tracklib.core.Obs import Obs
from tracklib.core.Track import Track

import tracklib.algo.Geometrics as Geometrics



class TestAlgoGeometricsMethods(unittest.TestCase):
    
    __epsilon = 0.001
    
    def setUp (self):
        
        #----------------------------------------------------------------------
        #   4 sommets sur axes du cercle trigonométrique
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        self.trace1 = Track()
        c1 = ENUCoords(1,  0, 0)
        p1 = Obs(c1, GPSTime.readTimestamp("2018-01-01 10:00:00"))
        self.trace1.addObs(p1)
        c2 = ENUCoords(0, 1, 0)
        p2 = Obs(c2, GPSTime.readTimestamp("2018-01-01 10:00:12"))
        self.trace1.addObs(p2)
        c3 = ENUCoords(-1, 0, 0)
        p3 = Obs(c3, GPSTime.readTimestamp("2018-01-01 10:00:40"))
        self.trace1.addObs(p3)
        c4 = ENUCoords(0, -1, 0)
        p4 = Obs(c4, GPSTime.readTimestamp("2018-01-01 10:01:50"))
        self.trace1.addObs(p4)
        self.trace1.addObs(p1)
        
        # ---------------------------------------------------------------------
        # Un escalier
        self.trace2 = Track()
        pm3 = Obs(ENUCoords(-2, -1), GPSTime.readTimestamp('2020-01-01 09:59:44'))
        self.trace2.addObs(pm3)
        pm2 = Obs(ENUCoords(-1, -1), GPSTime.readTimestamp('2020-01-01 09:59:48'))
        self.trace2.addObs(pm2)
        pm1 = Obs(ENUCoords(-1, 0), GPSTime.readTimestamp('2020-01-01 09:59:55'))
        self.trace2.addObs(pm1)
        p1 = Obs(ENUCoords(0, 0), GPSTime.readTimestamp('2020-01-01 10:00:00'))
        self.trace2.addObs(p1)
        p2 = Obs(ENUCoords(0, 2), GPSTime.readTimestamp('2020-01-01 10:00:01'))
        self.trace2.addObs(p2)
        p3 = Obs(ENUCoords(1, 2), GPSTime.readTimestamp('2020-01-01 10:00:02'))
        self.trace2.addObs(p3)
        p4 = Obs(ENUCoords(1, 5), GPSTime.readTimestamp('2020-01-01 10:00:03'))
        self.trace2.addObs(p4)
        p5 = Obs(ENUCoords(2, 5), GPSTime.readTimestamp('2020-01-01 10:00:04'))
        self.trace2.addObs(p5)
        p6 = Obs(ENUCoords(2, 9), GPSTime.readTimestamp('2020-01-01 10:00:06'))
        self.trace2.addObs(p6)
        p7 = Obs(ENUCoords(3, 9), GPSTime.readTimestamp('2020-01-01 10:00:08'))
        self.trace2.addObs(p7)
        p8 = Obs(ENUCoords(3, 14), GPSTime.readTimestamp('2020-01-01 10:00:10'))
        self.trace2.addObs(p8)
        p9 = Obs(ENUCoords(4, 14), GPSTime.readTimestamp('2020-01-01 10:00:12'))
        self.trace2.addObs(p9)
        p10 = Obs(ENUCoords(4, 20), GPSTime.readTimestamp('2020-01-01 10:00:15'))
        self.trace2.addObs(p10)
        
        # ---------------------------------------------------------------------
        #
        self.trace3 = Track()
        p1 = Obs(ENUCoords(0, 0), GPSTime.readTimestamp('2020-01-01 10:00:00'))
        self.trace3.addObs(p1)
        p2 = Obs(ENUCoords(1.5, 0.5), GPSTime.readTimestamp('2020-01-01 10:00:00'))
        self.trace3.addObs(p2)
        p3 = Obs(ENUCoords(2, 2), GPSTime.readTimestamp('2020-01-01 10:00:00'))
        self.trace3.addObs(p3)
        p4 = Obs(ENUCoords(3.75, 0.6), GPSTime.readTimestamp('2020-01-01 10:00:00'))
        self.trace3.addObs(p4)
        p5 = Obs(ENUCoords(5, 0.5), GPSTime.readTimestamp('2020-01-01 10:00:00'))
        self.trace3.addObs(p5)
        p6 = Obs(ENUCoords(3.55, -0.5), GPSTime.readTimestamp('2020-01-01 10:00:00'))
        self.trace3.addObs(p6)
        p7 = Obs(ENUCoords(1.8, -1.2), GPSTime.readTimestamp('2020-01-01 10:00:00'))
        self.trace3.addObs(p7)
        p8 = Obs(ENUCoords(1, -3), GPSTime.readTimestamp('2020-01-01 10:00:00'))
        self.trace3.addObs(p8)
        
    
    def testCircle(self):
        
        circle = Geometrics.Circle(ENUCoords(3.55, 2.2), 3)
        circle.plot()
        self.trace3.plot()
        
        t = circle.select(self.trace3)
        self.assertEqual(t.size(), 5)
        
        circle.translate(5, 2)
        circle.plot()
        
        circlebis = Geometrics.Circle(ENUCoords(3.55, 2.2), 8)
        circlebis.plot('b:', append=True)
        
        circlebis = Geometrics.Circle(ENUCoords(3.55, 2.2), 7)
        circlebis.plot('b:', append=False)
        
        circleter = Geometrics.Circle(ENUCoords(3.55, 2.2), 3)
        circleter.translate(2, 3)
        circleter.plot('g--', append=plt)
        
        circle3 = circlebis.copy()
        self.assertEqual(circle3.radius, circlebis.radius)
        self.assertEqual(circle3.center.E, circlebis.center.E)
        self.assertEqual(circle3.center.N, circlebis.center.N)
        self.assertEqual(circle3.center.U, circlebis.center.U)
        
        plt.show()


    def testRectangle (self):
        
        ll = ENUCoords(0, 0)
        ur = ENUCoords(10, 20)
        bbox = Geometrics.Rectangle(ll, ur)
        bbox.plot()
        self.trace3.plot()
        plt.plot([0], [0], 'ro', markersize=10)
        
        t = bbox.select(self.trace3)
        self.assertEqual(t.size(), 4)
        
        r = bbox.copy()
        self.assertIsInstance(r, Geometrics.Rectangle)
        self.assertEqual(r.pmin.E, bbox.pmin.E)
        self.assertEqual(r.pmin.N, bbox.pmin.N)
        self.assertEqual(r.pmax.E, bbox.pmax.E)
        self.assertEqual(r.pmax.N, bbox.pmax.N)
        
        r.translate(10, 20)
        self.assertIsInstance(r, Geometrics.Rectangle)
        self.assertEqual(r.pmin.E, 10)
        self.assertEqual(r.pmin.N, 20)
        self.assertEqual(r.pmax.E, 20)
        self.assertEqual(r.pmax.N, 40)
        
        r.rotate(math.pi/2)
        self.assertIsInstance(r, Geometrics.Rectangle)
        self.assertEqual(round(r.pmin.E), float(-20))
        self.assertEqual(round(r.pmin.N), float(10))
        self.assertEqual(round(r.pmax.E), float(-40))
        self.assertEqual(round(r.pmax.N), float(20))
        r.plot('g--')
        
        r.scale(1.5)
        self.assertIsInstance(r, Geometrics.Rectangle)
        self.assertEqual(round(r.pmin.E), float(-30))
        self.assertEqual(round(r.pmin.N), float(15))
        self.assertEqual(round(r.pmax.E), float(-60))
        self.assertEqual(round(r.pmax.N), float(30))
        r.plot('b:')
        
        self.assertEqual(0, bbox.pmin.E)
        self.assertEqual(0, bbox.pmin.N)
        self.assertEqual(10, bbox.pmax.E)
        self.assertEqual(20, bbox.pmax.N)
        
        plt.xlim([-75, 15])
        plt.ylim([-5, 35])
        plt.show()
        
        
    def testPolygon(self):
        
        poly = Geometrics.Polygon([0, 10, 10, 0, -10, -10], [0, 10, 30, 40, 30, 10])
        poly.plot()
        
        self.trace2.plot()
        
        P2 = poly.copy()
        self.assertIsInstance(P2, Geometrics.Polygon)
        self.assertEqual(P2.X, poly.X)
        self.assertEqual(P2.Y, poly.Y)
        
        t = P2.select(self.trace2)
        self.assertEqual(t.size(), 11)
        
        P2.translate(10, 5)
        P2.plot('g--')
        self.assertIsInstance(P2, Geometrics.Polygon)
        self.assertEqual(P2.X, [10, 20, 20, 10, 0, 0, 10])
        self.assertEqual(P2.Y, [5, 15, 35, 45, 35, 15, 5])
        
        P2.rotate(math.pi)
        P2.plot('b:')
        self.assertIsInstance(P2, Geometrics.Polygon)
        self.assertEqual(int(P2.X[0]), -10)
        self.assertEqual(int(P2.X[1]), -20)
        self.assertEqual(int(P2.X[2]), -20)
        self.assertEqual(int(P2.X[3]), -10)
        self.assertEqual(int(P2.X[4]), 0)
        self.assertEqual(int(P2.X[5]), 0)
        self.assertEqual(int(P2.X[6]), -10)
        self.assertEqual(int(P2.Y[0]), -4)
        self.assertEqual(int(P2.Y[1]), -14)
        self.assertEqual(int(P2.Y[2]), -35)
        self.assertEqual(int(P2.Y[3]), -45)
        self.assertEqual(int(P2.Y[4]), -35)
        self.assertEqual(int(P2.Y[5]), -15)
        self.assertEqual(int(P2.Y[6]), -4)
        
        P2.scale(0.2)
        P2.plot('b:')
        self.assertIsInstance(P2, Geometrics.Polygon)
        
        s = P2.area()
        self.assertEqual(s, 24.0)
        
        centre = P2.centroid()
        self.assertEqual(int(centre[0]), -2)
        self.assertEqual(int(centre[1]), -5)
        
        plt.xlim([-30, 25])
        plt.ylim([-50, 55])
        plt.show()
        
        self.assertTrue(P2.isStarShaped())
        
        t = P2.starShapedRatio()
        
        [S, R] = P2.signature()
        plt.plot(S, R)


    def testCircleTrigo(self):
        
        self.trace1.plot()
        
        C1 = Geometrics.minCircle(self.trace1)
        C1.plot()
        self.assertLessEqual(abs(1 - C1.radius), self.__epsilon, "Rayon du cercle")
        self.assertIsInstance(C1.center, ENUCoords)
        self.assertLessEqual(abs(0 - C1.center.getX()), self.__epsilon, "coord x du centre cercle")
        self.assertLessEqual(abs(0 - C1.center.getY()), self.__epsilon, "coord y du centre cercle")

        C2 = Geometrics.fitCircle(self.trace1)
        C2.plot()
        self.assertLessEqual(abs(1 - C2.radius), self.__epsilon, "Rayon du cercle")
        self.assertIsInstance(C2.center, ENUCoords)
        self.assertLessEqual(abs(0 - C2.center.getX()), self.__epsilon, "coord x du centre cercle")
        self.assertLessEqual(abs(0 - C2.center.getY()), self.__epsilon, "coord y du centre cercle")

        plt.show()
        

    def testCircles(self):
        
        self.trace2.plot()
        #plt.plot(track.getX(), track.getY(), 'b+')
        
        circle1 = Geometrics.fitCircle(self.trace2)
        self.assertIsInstance(circle1, Geometrics.Circle)
        self.assertLessEqual(abs(28.363 - circle1.radius), self.__epsilon, "Rayon du cercle")
        self.assertIsInstance(circle1.center, ENUCoords)
        self.assertLessEqual(abs(-25.09 - circle1.center.getX()), self.__epsilon, "coord x du centre cercle")
        self.assertLessEqual(abs(14.79 - circle1.center.getY()), self.__epsilon, "coord y du centre cercle")
        circle1.plot()
        
        circle2 = Geometrics.minCircle(self.trace2)
        self.assertIsInstance(circle2, Geometrics.Circle)
        circle2.plot()
        
        circle3 = Geometrics.minCircleMatrix(self.trace2)
        self.assertEqual(circle3.size, 169)
        # ??
        
        plt.show()


    def testDiameter(self):
        
        D = Geometrics.diameter(self.trace1)
        A = self.trace1.getObs(D[1])
        B = self.trace1.getObs(D[2])
        self.assertEqual(D[0], 2)
        self.assertEqual(A.distanceTo(B), D[0])
        self.assertEqual(A.position.getX(), 1)
        self.assertEqual(A.position.getY(), 0)
        self.assertEqual(B.position.getX(), -1)
        self.assertEqual(B.position.getY(), 0)
        
        D = Geometrics.diameter(self.trace2)
        A = self.trace2.getObs(D[1])
        B = self.trace2.getObs(D[2])
        self.assertIsInstance(A, Obs)
        self.assertIsInstance(B, Obs)
        self.assertEqual(A.distanceTo(B), D[0])
        
    
    def testConvexHull(self):
        
        self.trace3.plot()
        T = Geometrics.convexHull(self.trace3)
        Geometrics.plotPolygon(T)
        plt.show()
        self.assertEqual(len(T), 2*5)
        self.assertEqual(T[0], 0)
        self.assertEqual(T[1], 0)
        self.assertEqual(T[4], 5)
        self.assertEqual(T[5], 0.5)
        self.assertEqual(T[6], 1)
        self.assertEqual(T[7], -3)

        self.trace2.plot()
        T = Geometrics.convexHull(self.trace2)
        Geometrics.plotPolygon(T)
        plt.show()
        
        
    def testminimumBoundingRectangle(self):
        
        self.trace3.plot()
        R = Geometrics.minimumBoundingRectangle(self.trace3)
        T = []
        for coord in R[0]:
            T.append(coord[0])
            T.append(coord[1])
        Geometrics.plotPolygon(T)
        
        self.assertEqual(R[1], 16.5)
        self.assertLessEqual(abs(3.104 - R[2]), self.__epsilon, "l")
        self.assertLessEqual(abs(5.315 - R[3]), self.__epsilon, "L")
        
        
    # def testMinCircle(self):
        
    #     trace = Track()
    #     D = Geometrics.minCircle(trace)




if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoGeometricsMethods("testCircle"))
    suite.addTest(TestAlgoGeometricsMethods("testRectangle"))
    suite.addTest(TestAlgoGeometricsMethods("testPolygon"))
    suite.addTest(TestAlgoGeometricsMethods("testCircleTrigo"))
    suite.addTest(TestAlgoGeometricsMethods("testCircles"))
    suite.addTest(TestAlgoGeometricsMethods("testDiameter"))
    suite.addTest(TestAlgoGeometricsMethods("testConvexHull"))
    suite.addTest(TestAlgoGeometricsMethods("testminimumBoundingRectangle"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
