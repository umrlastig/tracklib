# -*- coding: utf-8 -*-

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

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoGeometricsMethods("testCircleTrigo"))
    suite.addTest(TestAlgoGeometricsMethods("testCircles"))
    suite.addTest(TestAlgoGeometricsMethods("testDiameter"))
    suite.addTest(TestAlgoGeometricsMethods("testConvexHull"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
