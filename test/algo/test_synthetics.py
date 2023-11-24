# -*- coding: utf-8 -*-


import math
import matplotlib.pyplot as plt
from tracklib import generate, ObsTime, ENUCoords, TrackCollection, Track
from unittest import TestCase, TestSuite, TextTestRunner


class TestSynthetics(TestCase):
    '''
    '''
    
    def test_generate_random(self):
        t = generate(verbose=False)
        
        self.assertEqual(t.size(), 100)
        
        dt = t.getLastObs().timestamp - t.getFirstObs().timestamp
        self.assertGreaterEqual(dt, 3550)
        self.assertLessEqual(dt, 3650)
        
        for i in range(t.size()):
            p = t.getObs(i).position
            self.assertGreaterEqual(p.getX(), -150)
            self.assertLessEqual(p.getX(), 250)
            self.assertGreaterEqual(p.getY(), -150)
            self.assertLessEqual(p.getY(), 250)
            
    def test_generate_x(self):
        t = generate(0.5, verbose=False)
        
        self.assertEqual(t.size(), 100)
        
        dt = t.getLastObs().timestamp - t.getFirstObs().timestamp
        self.assertGreaterEqual(dt, 3550)
        self.assertLessEqual(dt, 3650)
        
        for i in range(t.size()):
            p = t.getObs(i).position
            self.assertGreaterEqual(p.getX(), -250)
            self.assertLessEqual(p.getX(), 250)
            self.assertGreaterEqual(p.getY(), -250)
            self.assertLessEqual(p.getY(), 250)
        
    def test_generate_cercle_N(self):
        Nb = 100
        ts = generate(0.5, N=Nb, verbose=False)
        
        self.assertIsInstance(ts, TrackCollection)
        self.assertEqual(ts.size(), Nb)
        
        for i in range(ts.size()):
            t = ts[i]
            self.assertIsInstance(t, Track)
            self.assertEqual(t.size(), 100)
            
            dt = t.getLastObs().timestamp - t.getFirstObs().timestamp
            self.assertGreaterEqual(dt, 3550)
            self.assertLessEqual(dt, 3650)
            
            for j in range(t.size()):
                p = t.getObs(j).position
                self.assertGreaterEqual(p.getX(), -250)
                self.assertLessEqual(p.getX(), 250)
                self.assertGreaterEqual(p.getY(), -250)
                self.assertLessEqual(p.getY(), 250)
    
    def x_t(self, t):
        return math.cos(2*math.pi*t)
    def y_t(self, t):
        return math.sin(2*math.pi*t)
    def z_t(self, t):
        return 5*t
    
    def test_generate_cercle_2d(self):
        t = generate(self.x_t, self.y_t)
        
        self.assertIsInstance(t, Track)
        self.assertEqual(t.size(), 100)
        
        dt = t.getLastObs().timestamp - t.getFirstObs().timestamp
        self.assertGreaterEqual(dt, 3550)
        self.assertLessEqual(dt, 3650)
            
        for i in range(t.size()):
            p = t.getObs(i).position
            self.assertGreaterEqual(p.getX(), -1)
            self.assertLessEqual(p.getX(), 1)
            self.assertGreaterEqual(p.getY(), -1)
            self.assertLessEqual(p.getY(), 1)
    
    
    def test_generate_cercle_3d(self):
        t = generate(self.x_t, self.y_t, self.z_t, verbose=False)
        
        self.assertIsInstance(t, Track)
        self.assertEqual(t.size(), 100)
        
        dt = t.getLastObs().timestamp - t.getFirstObs().timestamp
        self.assertGreaterEqual(dt, 3550)
        self.assertLessEqual(dt, 3650)
        
        self.assertEqual(t.getFirstObs().position, ENUCoords(1.0, 0.0, 0.0))
        self.assertEqual(t.getLastObs().position, ENUCoords(1.0, -0.0, 5.0))
        
        self.assertEqual(t.getObs(10).position.getX(), self.x_t(10/99))
        self.assertEqual(t.getObs(10).position.getY(), self.y_t(10/99))
        self.assertEqual(t.getObs(10).position.getZ(), self.z_t(10/99))
        
        self.assertEqual(t.getObs(60).position.getX(), self.x_t(60/99))
        self.assertEqual(t.getObs(60).position.getY(), self.y_t(60/99))
        self.assertEqual(t.getObs(60).position.getZ(), self.z_t(60/99))
        
        #ax = plt.figure().add_subplot(projection='3d')
        #t.plot(append=ax)
        #plt.show()
    
    
    def test_generate_cercle_dt(self):
        t = generate(self.x_t, self.y_t, dt=5, verbose=False)
        
        self.assertIsInstance(t, Track)
        self.assertGreaterEqual(t.size(), 700)
        self.assertLessEqual(t.size(), 750)
        
        dt = t.getLastObs().timestamp - t.getFirstObs().timestamp
        self.assertGreaterEqual(dt, 3550)
        self.assertLessEqual(dt, 3650)
        
        for i in range(t.size()):
            p = t.getObs(i).position
            self.assertGreaterEqual(p.getX(), -1)
            self.assertLessEqual(p.getX(), 1)
            self.assertGreaterEqual(p.getY(), -1)
            self.assertLessEqual(p.getY(), 1)
        
    
    def test_generate_cercle_date(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        dateini = ObsTime.readTimestamp("2018-01-31 11:17:00")
        datefin = ObsTime.readTimestamp("2018-01-31 11:18:40")
        
        t = generate(self.x_t, self.y_t, date_ini=dateini, date_fin=datefin, verbose = False)
        
        self.assertEqual(t.size(), 100)
        
        self.assertEqual(str(t.getFirstObs().timestamp)[0:19], "31/01/2018 11:17:01")
        self.assertEqual(str(t.getObs(10).timestamp)[0:19], "31/01/2018 11:17:11")
        self.assertEqual(str(t.getObs(60).timestamp)[0:19], "31/01/2018 11:18:01")
        self.assertEqual(str(t.getLastObs().timestamp)[0:19], "31/01/2018 11:18:40")
        
        self.assertEqual(t.getFirstObs().position, ENUCoords(1.0, 0.0))
        self.assertEqual(t.getLastObs().position, ENUCoords(1.0, -0.0))
        self.assertEqual(t.getObs(10).position.getX(), self.x_t(10/99))
        self.assertEqual(t.getObs(60).position.getX(), self.x_t(60/99))
        self.assertEqual(t.getObs(10).position.getY(), self.y_t(10/99))
        self.assertEqual(t.getObs(60).position.getY(), self.y_t(60/99))
        
        
    def test_generate_cercle_tot(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        dateini = ObsTime.readTimestamp("2018-01-31 11:17:00")
        datefin = ObsTime.readTimestamp("2018-01-31 11:18:40")
        
        t = generate(self.x_t, self.y_t, self.z_t, dt=5, date_ini=dateini, date_fin=datefin, 
                      verbose = False)
        
        self.assertIsInstance(t, Track)
        self.assertEqual(t.size(), 20)
        
        self.assertEqual(t.getFirstObs().position, ENUCoords(1.0, 0.0, 0.0))
        self.assertEqual(t.getLastObs().position, ENUCoords(1.0, -0.0, 5.0))
        
        self.assertEqual(t.getObs(10).position.getX(), self.x_t(10/19))
        self.assertEqual(t.getObs(10).position.getY(), self.y_t(10/19))
        self.assertEqual(t.getObs(10).position.getZ(), self.z_t(10/19))
        
        self.assertEqual(t.getObs(18).position.getX(), self.x_t(18/19))
        self.assertEqual(t.getObs(18).position.getY(), self.y_t(18/19))
        self.assertEqual(t.getObs(18).position.getZ(), self.z_t(18/19))
    
        
        
if __name__ == '__main__':
    
    suite = TestSuite()
    
    suite.addTest(TestSynthetics("test_generate_random"))
    suite.addTest(TestSynthetics("test_generate_x"))
    suite.addTest(TestSynthetics("test_generate_cercle_N"))
    suite.addTest(TestSynthetics("test_generate_cercle_2d"))
    suite.addTest(TestSynthetics("test_generate_cercle_3d"))
    suite.addTest(TestSynthetics("test_generate_cercle_dt"))
    suite.addTest(TestSynthetics("test_generate_cercle_date"))
    suite.addTest(TestSynthetics("test_generate_cercle_tot"))
    
    runner = TextTestRunner()
    runner.run(suite)
    
    