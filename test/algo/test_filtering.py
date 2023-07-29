# -*- coding: utf-8 -*-

import os.path

from unittest import TestCase, TestSuite, TextTestRunner

from tracklib import (ObsTime)
from tracklib.io import TrackReader
from tracklib import DiracKernel, GaussianKernel, TriangularKernel, ExponentialKernel
import tracklib.algo.Filtering as flt


class TestFiltering(TestCase):
    
    __epsilon = 1
    
    def setUp(self):
        
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        self.csvpath = os.path.join(self.resource_path, 'data/trace0.gps')
        
        ObsTime.setPrintFormat("2D/2M/4Y 2h:2m:2s.3z")
        self.track = TrackReader.readFromCsv(self.csvpath) % 10
        self.track.plot('kx')
        
    def view(self, track, sym):
        track.plot(sym)
    
    
    # =========================================================================
    # --------------------------------------------------------------------
    # Lissage
    # --------------------------------------------------------------------

    def test22(self, sym = 'r-'):
        '''
        Filtrage par noyau fenetre glissante de taille 5
        '''
        self.track = flt.filter_seq(self.track, kernel=5, dim=flt.FILTER_XY)
        self.view(self.track, sym)	


    def test23(self, sym = 'r-'):
        '''
        Filtrage par noyau 'user-defined'
        '''
        self.track = flt.filter_seq(self.track, kernel=[1,2,32,2,1], dim=["x","y"])
        self.view(self.track, sym)	
	

    def test24(self, sym = 'r-'):
        '''
        Filtrage par noyau 'user-defined' pour faire un filtre 'avance'
        '''
        self.track = flt.filter_seq(self.track, kernel=[0,0,1], dim=["y"])
        self.view(self.track, sym)	
	

    def test25(self, sym = 'r-'):
        '''
        Filtrage par noyau 'user-defined' pour faire un filtre 'retard'
        '''
        self.track = flt.filter_seq(self.track, kernel=[1,0,0], dim=["y"])
        self.view(self.track, sym)	

        
    def test26(self, sym = 'r-'):
        '''
        Filtrage par noyau gaussien
        '''
        self.track = self.track.copy()
        self.track *= 10
        self.track = flt.filter_seq(self.track, kernel=GaussianKernel(20), dim=flt.FILTER_XY)
        self.view(self.track, sym)	


    def test27(self, sym = 'r-'):
        '''
        Filtrage par noyau exponentiel
        '''
        self.track = self.track.copy()
        self.track *= 10
        self.track = flt.filter_seq(self.track, kernel=ExponentialKernel(20), dim=flt.FILTER_XY)
        self.view(self.track, sym)	


    def test28(self, sym = 'r-'):
        '''
        Filtrage par noyau triangulaire
        '''
        self.track = self.track.copy()
        self.track *= 10
        self.track = flt.filter_seq(self.track, kernel=TriangularKernel(20), dim=flt.FILTER_XY)
        self.view(self.track, sym)	

    
    def test29(self, sym = 'r-'):
        '''
        Filtrage par noyau de Dirac (sans effet)
        '''
        self.track = self.track.copy()
        self.track *= 10
        self.track = flt.filter_seq(self.track, kernel=DiracKernel(), dim=flt.FILTER_XY)
        self.view(self.track, sym)	
     
     
    def test30(self, sym = 'r-'):
        '''
        Filtrage passe-bas par transformation de Fourier (frequence temporelle)
        '''
        self.track = flt.filter_freq(self.track, 1, mode=flt.FILTER_TEMPORAL, 
                                      type=flt.FILTER_LOW_PASS, dim=flt.FILTER_XY)
        self.view(self.track, sym)	
     
     
    def test31(self, sym = 'r-'):
        '''
        Filtrage passe-bas par transformation de Fourier (frequence spatiale)
        '''
        self.track *= 10
        self.track = flt.filter_freq(self.track, 0.03, 
                                      mode=flt.FILTER_SPATIAL, 
                                      type=flt.FILTER_LOW_PASS, 
                                      dim=flt.FILTER_XY)
        self.view(self.track, sym)	


    def test32(self, sym = 'r-'):
        '''
        Filtrage de Kalman (50 cm sur le GPS / 2 m.s-1 sur la vitesse)
        '''
        self.track = flt.Kalman(self.track, 0.5, 2)
        self.view(self.track, sym)	
        
        
if __name__ == '__main__':
    suite = TestSuite()
    
    suite.addTest(TestFiltering("test22"))
    suite.addTest(TestFiltering("test23"))
    suite.addTest(TestFiltering("test24"))
    suite.addTest(TestFiltering("test25"))
    suite.addTest(TestFiltering("test26"))
    suite.addTest(TestFiltering("test27"))
    suite.addTest(TestFiltering("test28"))
    suite.addTest(TestFiltering("test29"))
    suite.addTest(TestFiltering("test30"))
    suite.addTest(TestFiltering("test31"))
    suite.addTest(TestFiltering("test32"))
    
    runner = TextTestRunner()
    runner.run(suite)