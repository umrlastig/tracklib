# -*- coding: utf-8 -*-

import os.path
import unittest
#import matplotlib.pyplot as plt

from tracklib.core.GPSTime import GPSTime
from tracklib.io.TrackReader import TrackReader
#from tracklib.io.FileReader import FileReader
#from tracklib.core.Plot import Plot

from tracklib.algo.Segmentation import findStopsGlobal#, findStopsLocal

class TestAlgoSegmentationMethods(unittest.TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")


    def testStopsAFaire(self):
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        #chemin = os.path.join(self.resource_path, './data/trace1.dat')
        #trace = FileReader.readFromCsvFiles(chemin, 2, 3, -1, 4, separator=",")
        

    def testFindStopsLocal(self):
        resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        gpxpath = os.path.join(resource_path, 'data/gpx/vincennes.gpx')
        GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        tracks = TrackReader.readFromGpx(gpxpath, srid='ENU')
        trace = tracks.getTrack(0)
        #trace = trace.extract(1150, 2500)
        print (trace.size())

        
        #trace.summary()

        #plot = Plot(trace)
        #plot.plotProfil('SPATIAL_SPEED_PROFIL')
        
        #trace.plot()
        
        stops = findStopsGlobal(trace, downsampling=5)
        print (type(stops), len(stops))
        
        
        #COLS = utils.getColorMap((220, 220, 220), (255, 0, 0))
        #trace.plot(type='POINT', af_name='virage', append = False, cmap = COLS)
    
        #plt.plot(stops.getX(), stops.getY(), 'ro')
    
    
        #self.assertLessEqual(3, 5)
        
    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestAlgoSegmentationMethods("testFindStopsLocal"))
    runner = unittest.TextTestRunner()
    runner.run(suite)