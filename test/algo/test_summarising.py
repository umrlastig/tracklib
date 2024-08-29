# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner
import matplotlib.pyplot as plt
import os.path

from tracklib import (Obs, ObsTime, ENUCoords, TrackCollection,
                      speed,NO_DATA_VALUE,
                      Track, TrackReader,
                      co_avg, co_max, co_count, co_min, co_count_distinct,
                      summarize, AFMap)


class TestSummarising(TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")

    def test_summarize_af(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        TRACES = []
        
        # ---------------------------------------------------------------------
        trace1 = Track([], 1)

        trace1.addObs(Obs(ENUCoords(10, 10, 0), ObsTime.readTimestamp("2018-01-01 10:00:00")))
        trace1.addObs(Obs(ENUCoords(10, 30, 0), ObsTime.readTimestamp("2018-01-01 10:00:04")))
        trace1.addObs(Obs(ENUCoords(10, 110, 0), ObsTime.readTimestamp("2018-01-01 10:00:12")))
        trace1.addObs(Obs(ENUCoords(130, 110), ObsTime.readTimestamp("2018-01-01 10:00:30")))
        trace1.addObs(Obs(ENUCoords(190, 10), ObsTime.readTimestamp("2018-01-01 10:00:35")))
        trace1.addObs(Obs(ENUCoords(270, 110), ObsTime.readTimestamp("2018-01-01 10:00:40")))
        trace1.addObs(Obs(ENUCoords(300, 190), ObsTime.readTimestamp("2018-01-01 10:01:00")))
        trace1.addObs(Obs(ENUCoords(370, 190, 0), ObsTime.readTimestamp("2018-01-01 10:01:50")))
        
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
        
        af_algos = ['speed', 'speed', 'uid', 'uid']
        cell_operators = [co_avg, co_max, co_count, co_count_distinct]

        #  Construction du raster
        marge = 0.0
        raster = summarize(collection, af_algos, cell_operators,
                               (60, 60), marge)
        # print (raster.collectionValuesGrid)

        self.assertEqual(raster.getNoDataValue(), NO_DATA_VALUE)

        self.assertEqual(raster.xmin, 10.0 - marge*(370-10))
        self.assertEqual(raster.xmax, 370.0 + marge*(370-10))
        self.assertEqual(raster.ymin, 10.0 - marge*(190-10))
        self.assertEqual(raster.ymax, 190.0 + marge*(190-10))
        
        self.assertEqual(raster.ncol, int (((370-10) + marge*(370-10)) / 60))
        self.assertEqual(raster.nrow, int (((190-10) + marge*(190-10)) / 60))
    
        self.assertEqual(raster.resolution[0], ((370-10) + 2*marge*(370-10)) / raster.ncol)
        self.assertEqual(raster.resolution[1], ((190-10) + 2*marge*(190-10)) / raster.nrow)

        # ---------------------------------------------------------------------
        #   On teste les maps

        map1 = raster.getAFMap(AFMap.getMeasureName('uid', co_count))
        self.assertIsInstance(map1, AFMap)

        map2 = raster.getAFMap(AFMap.getMeasureName('uid', co_count_distinct))
        self.assertIsInstance(map2, AFMap)

        map3 = raster.getAFMap(AFMap.getMeasureName(speed, co_avg))
        self.assertIsInstance(map3, AFMap)

        map4 = raster.getAFMap(AFMap.getMeasureName(speed, co_max))
        self.assertIsInstance(map4, AFMap)


        # ---------------------------------------------------------------------
        #  On teste les plots

        map1.plotAsGraphic()
        plt.show()

        map2.plotAsGraphic()
        plt.show()

        raster.plot(0)
        plt.show()

        # ---------------------------------------------------------------------
        # On teste les valeurs de la grille: map 2

        self.assertEqual(map2.grid[2][0], 2)
        self.assertEqual(map2.grid[1][0], 1)
        self.assertEqual(map2.grid[0][0], 0)

        self.assertEqual(map2.grid[2][1], 0)
        self.assertEqual(map2.grid[1][1], 0)
        self.assertEqual(map2.grid[0][1], 0)

        self.assertEqual(map2.grid[2][2], 0)
        self.assertEqual(map2.grid[1][2], 1)
        self.assertEqual(map2.grid[0][2], 0)

        self.assertEqual(map2.grid[2][3], 1)
        self.assertEqual(map2.grid[1][3], 0)
        self.assertEqual(map2.grid[0][3], 0)

        self.assertEqual(map2.grid[2][4], 0)
        self.assertEqual(map2.grid[1][4], 2)
        self.assertEqual(map2.grid[0][4], 1)

        self.assertEqual(map2.grid[2][5], 1)
        self.assertEqual(map2.grid[1][5], 0)
        self.assertEqual(map2.grid[0][5], 1)

        # ---------------------------------------------------------------------
        # On teste les valeurs de la grille: map 1

        self.assertEqual(map1.grid[2][0], 3)
        self.assertEqual(map1.grid[1][0], 1)
        self.assertEqual(map1.grid[0][0], 0)

        self.assertEqual(map1.grid[2][1], 0)
        self.assertEqual(map1.grid[1][1], 0)
        self.assertEqual(map1.grid[0][1], 0)

        self.assertEqual(map1.grid[2][2], 0)
        self.assertEqual(map1.grid[1][2], 1)
        self.assertEqual(map1.grid[0][2], 0)

        self.assertEqual(map1.grid[2][3], 1)
        self.assertEqual(map1.grid[1][3], 0)
        self.assertEqual(map1.grid[0][3], 0)

        self.assertEqual(map1.grid[2][4], 0)
        self.assertEqual(map1.grid[1][4], 2)
        self.assertEqual(map1.grid[0][4], 1)

        self.assertEqual(map1.grid[2][5], 1)
        self.assertEqual(map1.grid[1][5], 0)
        self.assertEqual(map1.grid[0][5], 1)

        # ---------------------------------------------------------------------
        # On teste les valeurs de la grille: map 3

        speedTrace1 = collection.getTrack(0).getAnalyticalFeature('speed')
        speedTrace2 = collection.getTrack(1).getAnalyticalFeature('speed')

        self.assertEqual(map3.grid[2][0], (speedTrace1[0] + speedTrace1[1] + speedTrace2[0]) / 3)
        self.assertEqual(map3.grid[1][0], speedTrace1[2])
        self.assertEqual(map3.grid[0][0], raster.getNoDataValue())
        
        self.assertEqual(map3.grid[2][1], raster.getNoDataValue())
        self.assertEqual(map3.grid[1][1], raster.getNoDataValue())
        self.assertEqual(map3.grid[0][1], raster.getNoDataValue())
        
        self.assertEqual(map3.grid[2][2], raster.getNoDataValue())
        self.assertEqual(map3.grid[1][2], speedTrace1[3])
        self.assertEqual(map3.grid[0][2], raster.getNoDataValue())
        
        self.assertEqual(map3.grid[2][3], speedTrace1[4])
        self.assertEqual(map3.grid[1][3], raster.getNoDataValue())
        self.assertEqual(map3.grid[0][3], raster.getNoDataValue())
        
        self.assertEqual(map3.grid[2][4], raster.getNoDataValue())
        self.assertEqual(map3.grid[1][4], (speedTrace1[5] + speedTrace2[1]) / 2)
        self.assertEqual(map3.grid[0][4], speedTrace1[6])
        
        self.assertEqual(map3.grid[0][5], speedTrace1[7])
        self.assertEqual(map3.grid[1][5], raster.getNoDataValue())
        self.assertEqual(map3.grid[2][5], speedTrace2[2])
    
        raster.plot(AFMap.getMeasureName(speed, co_avg))
        plt.show()
        
        # ---------------------------------------------------------------------
        #
        
        name2 = AFMap.getMeasureName(speed, co_max)
        self.assertEqual(name2, 'speed#co_max')

        map2.bandStatistics()
        map4.bandStatistics()
        


    def test_quickstart(self):

        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        '''
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
        raster.getAFMap(0).noDataValue = 0

        raster.getAFMap(0).plotAsGraphic()
        raster.getAFMap(0).summary()
        raster.plot(0)
        
        raster.plot(AFMap.getMeasureName(speed, co_avg))
        raster.plot(AFMap.getMeasureName(speed, co_min))
        raster.plot(AFMap.getMeasureName(speed, co_max))
        plt.show()
        '''



if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestSummarising("test_summarize_af"))
    suite.addTest(TestSummarising("test_quickstart"))
    runner = TextTestRunner()
    runner.run(suite)
    
    