# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner
import matplotlib.pyplot as plt
import os.path


from tracklib import (Obs, ObsTime, ENUCoords, TrackCollection,
                      speed,
                      RasterBand, NO_DATA_VALUE,
                      Track, TrackReader,
                      co_avg, co_max, co_count,
                      co_min, # co_dominant, co_median,
                      summarize, AFMap, RasterWriter)


class TestSummarising(TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        
    
    def test_summarize_af(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        TRACES = []
        
        # ---------------------------------------------------------------------
        trace1 = Track([], 1)
        c1 = ENUCoords(10, 10, 0)
        p1 = Obs(c1, ObsTime.readTimestamp("2018-01-01 10:00:00"))
        trace1.addObs(p1)
        
        c2 = ENUCoords(10, 110, 0)
        p2 = Obs(c2, ObsTime.readTimestamp("2018-01-01 10:00:12"))
        trace1.addObs(p2)
        
        c3 = ENUCoords(270, 110, 0)
        p3 = Obs(c3, ObsTime.readTimestamp("2018-01-01 10:00:40"))
        trace1.addObs(p3)
        
        c4 = ENUCoords(370, 190, 0)
        p4 = Obs(c4, ObsTime.readTimestamp("2018-01-01 10:01:50"))
        trace1.addObs(p4)
        
        TRACES.append(trace1)
        
        # ---------------------------------------------------------------------
        trace2 = Track([], 2)
        c7 = ENUCoords(25, 10, 0)
        p7 = Obs(c7, ObsTime.readTimestamp("2018-01-01 10:00:15"))
        trace2.addObs(p7)
        
        c6 = ENUCoords(280, 90, 0)
        p6 = Obs(c6, ObsTime.readTimestamp("2018-01-01 10:00:45"))
        trace2.addObs(p6)
        
        c5 = ENUCoords(330, 20, 0)
        p5 = Obs(c5, ObsTime.readTimestamp("2018-01-01 10:01:55"))
        trace2.addObs(p5)
        
        TRACES.append(trace2)
        
        collection = TrackCollection(TRACES)
        collection.plot('k-')
        plt.show()

        # ---------------------------------------------------------------------

        name = AFMap.getMeasureName('speed', co_max)
        self.assertEqual(name, 'speed#co_max')

        name = AFMap.getMeasureName(speed, co_avg)
        self.assertEqual(name, 'speed#co_avg')

        name = AFMap.getMeasureName('uid', co_count)
        self.assertEqual(name, 'uid#co_count')


        # ---------------------------------------------------------------------

        collection.addAnalyticalFeature(speed)
        
        af_algos = ['speed', 'speed', 'uid']
        cell_operators = [co_avg, co_max, co_count] #, utils.sum]

        #  Construction du raster
        marge = 0.0
        raster = summarize(collection, af_algos, cell_operators,
                               (60, 60), marge)
#        raster.plot('uid#co_count')

        grille = raster.getRasterBand(AFMap.getMeasureName(speed, co_avg))
        self.assertIsInstance(grille, RasterBand)
        
        self.assertEqual(grille.getNoDataValue(), NO_DATA_VALUE)
        
        grille.plotAsGraphic()
        plt.show()
        
#        grille.plotAsImage()
#        plt.show()


        # ---------------------------------------------------------------------

        # raster = summarize(collection,
        #                    af_algos, cell_operators, (60, 60), marge)
        grille = raster.getRasterBand(
            AFMap.getMeasureName(speed, co_avg))
        '''
        grille.setNoDataValue(0)
        self.assertEqual(grille.getNoDataValue(), 0)
        grille.plotAsImage()
        plt.show()

        # ---------------------------------------------------------------------
        # On teste la construction de la grille
        '''
        self.assertEqual(grille.xmin, 10.0 - marge*(370-10))
        self.assertEqual(grille.xmax, 370.0 + marge*(370-10))
        self.assertEqual(grille.ymin, 10.0 - marge*(190-10))
        self.assertEqual(grille.ymax, 190.0 + marge*(190-10))
        
        self.assertEqual(grille.ncol, int (((370-10) + marge*(370-10)) / 60))
        self.assertEqual(grille.nrow, int (((190-10) + marge*(190-10)) / 60))
    
        self.assertEqual(grille.XPixelSize, ((370-10) + 2*marge*(370-10)) / grille.ncol)
        self.assertEqual(grille.YPixelSize, ((190-10) + 2*marge*(190-10)) / grille.nrow)
        

        # ---------------------------------------------------------------------
        # On teste les valeurs de la grille

        speedTrace1 = collection.getTrack(0).getAnalyticalFeature('speed')
        speedTrace2 = collection.getTrack(1).getAnalyticalFeature('speed')


        self.assertEqual(grille.grid[2][0], (speedTrace1[0] + speedTrace2[0]) / 2)
        self.assertEqual(grille.grid[1][0], speedTrace1[1])
        self.assertEqual(grille.grid[0][0], grille.getNoDataValue())
        
        self.assertEqual(grille.grid[2][1], grille.getNoDataValue())
        self.assertEqual(grille.grid[1][1], grille.getNoDataValue())
        self.assertEqual(grille.grid[0][1], grille.getNoDataValue())
        
        self.assertEqual(grille.grid[2][2], grille.getNoDataValue())
        self.assertEqual(grille.grid[1][2], grille.getNoDataValue())
        self.assertEqual(grille.grid[0][2], grille.getNoDataValue())
        
        self.assertEqual(grille.grid[2][3], grille.getNoDataValue())
        self.assertEqual(grille.grid[1][3], grille.getNoDataValue())
        self.assertEqual(grille.grid[0][3], grille.getNoDataValue())
        
        self.assertEqual(grille.grid[2][4], grille.getNoDataValue())
        self.assertEqual(grille.grid[1][4], (speedTrace1[2] + speedTrace2[1]) / 2)
        self.assertEqual(grille.grid[0][4], grille.getNoDataValue())
        
        self.assertEqual(grille.grid[0][5], speedTrace1[3])
        self.assertEqual(grille.grid[1][5], grille.getNoDataValue())
        self.assertEqual(grille.grid[2][5], speedTrace2[2])
    
        raster.plot(AFMap.getMeasureName(speed, co_avg))
        plt.show()
        
        raster.plot(0)
        plt.show()
        
        
        name2 = AFMap.getMeasureName(speed, co_max)
        self.assertEqual(name2, 'speed#co_max')
        grille2 = raster.getRasterBand(name2)
        grille2.plotAsGraphic()
        plt.show()
        
        grille.bandStatistics()
        grille2.bandStatistics()
        

        # ---------------------------------------------------------------------
        af_algos = ['uid']
        cell_operators = [co_count]

        #  Construction du raster
        marge = 0.0
        resolution = (60, 60)

        bbox = collection.bbox()
        attendanceMap = AFMap(bbox, af_algos, cell_operators,
                               resolution, marge)

        self.assertEqual(attendanceMap.getRaster().bandCount(), 1)
        self.assertEqual(attendanceMap.getRaster().getNamesOfRasterBand()[0], 'uid#co_count')


        # band = raster.getRasterBand(0)
        # print (band.bbox())
        # band = raster.getRasterBand('uid#co_count')
        # print (band.bbox(), band.getName())

        for trace in collection:
            attendanceMap.addTrackToMap(trace)


        attendanceMap.computeAggregates()

        raster = attendanceMap.getRaster()


        grille3 = raster.getRasterBand(AFMap.getMeasureName('uid', co_count))

        self.assertEqual(grille3.grid[2][0], 2)
        self.assertEqual(grille3.grid[1][0], 1)
        self.assertEqual(grille3.grid[0][0], 0)

        self.assertEqual(grille3.grid[0][4], 0)
        self.assertEqual(grille3.grid[1][4], 2)
        self.assertEqual(grille3.grid[2][4], 0)

        self.assertEqual(grille3.grid[2][5], 1)
        self.assertEqual(grille3.grid[1][5], 0)
        self.assertEqual(grille3.grid[0][5], 1)


        raster.plot('uid#co_count')
        plt.show()

        #RasterWriter.writeToFile('/home/md_vandamme/',
        #        raster, raster.getRasterBand('uid#co_count'), 'testraster')




    #, utils.stop_point]


    def test_quickstart(self):

        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        gpxpath = os.path.join(self.resource_path, 'data/gpx/activity_5807084803.gpx')
        tracks = TrackReader.readFromGpx(gpxpath)
        trace = tracks.getTrack(0)
        # Transformation GEO coordinates to ENU
        trace.toENUCoords()
        # Display
        trace.plot()
        plt.show()

        # speed
        trace.estimate_speed()
        
        collection = TrackCollection([trace])

        af_algos = [speed, speed, speed]
        cell_operators = [co_avg, co_min, co_max]
        marge = 0.000005
        raster = summarize(collection, af_algos, cell_operators, (5, 5), margin=marge)
        raster.getRasterBand(0).noDataValue = 0

        raster.getRasterBand(0).plotAsGraphic()
        raster.getRasterBand(0).summary()
        raster.plot(0)
        
        raster.plot(AFMap.getMeasureName(speed, co_avg))
        raster.plot(AFMap.getMeasureName(speed, co_min))
        raster.plot(AFMap.getMeasureName(speed, co_max))
        plt.show()




if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestSummarising("test_summarize_af"))
    suite.addTest(TestSummarising("test_quickstart"))
    runner = TextTestRunner()
    runner.run(suite)
    
    