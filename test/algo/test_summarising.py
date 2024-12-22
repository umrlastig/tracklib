# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner
import matplotlib.pyplot as plt
import os.path

from tracklib import (Obs, ObsTime, ENUCoords, TrackCollection,
                      speed,NO_DATA_VALUE,
                      Track, TrackReader,
                      co_avg, co_max, co_count, co_min, co_count_distinct,
                      summarize, AFMap, seed, generate, noise, MODE_DIRECTION_ORTHO,
                      SincKernel, DiracKernel,
                      BBOX_ALIGN_LL, BBOX_ALIGN_CENTER, BBOX_ALIGN_UR)


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
        #collection.plot('k-')
        #plt.show()

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
        res = (60, 60)
        raster = summarize(collection, af_algos, cell_operators, res, marge)
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

        #map1.plotAsVectorGraphic()
        #plt.show()

        map2.plotAsVectorGraphic()
        plt.show()

        #raster.plot(0)
        #plt.show()

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
        '''
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
        '''


    def test_summarize_af_grid_grande(self):
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
        trace2.addObs(Obs(ENUCoords(25, 10, 0), ObsTime.readTimestamp("2018-01-01 10:00:15")))
        trace2.addObs(Obs(ENUCoords(280, 90, 0), ObsTime.readTimestamp("2018-01-01 10:00:45")))
        trace2.addObs(Obs(ENUCoords(330, 20, 0), ObsTime.readTimestamp("2018-01-01 10:01:55")))
        TRACES.append(trace2)
        
        collection = TrackCollection(TRACES)

        # ---------------------------------------------------------------------
        af_algos = ['uid']
        cell_operators = [co_count_distinct]

        #  Construction du raster
        marge = 0.1
        res = (60, 60)
        noovalue = -1
        raster = summarize(collection, af_algos, cell_operators, res, marge)

        self.assertEqual(raster.getNoDataValue(), NO_DATA_VALUE)
        print (raster)

        self.assertEqual(raster.xmin, -26)
        self.assertEqual(raster.xmax, 454)
        self.assertEqual(raster.ymin, -8)
        self.assertEqual(raster.ymax, 232)
        
        self.assertEqual(raster.ncol, 8)
        self.assertEqual(raster.nrow, 4)
    
        self.assertEqual(raster.resolution[0], 60)
        self.assertEqual(raster.resolution[1], 60)

        # ---------------------------------------------------------------------
        #   On teste les maps

        map1 = raster.getAFMap(AFMap.getMeasureName('uid', co_count_distinct))
        self.assertIsInstance(map1, AFMap)

        map1.plotAsVectorGraphic()
        plt.show()




    def test_synthetic_dataset(self):

        seed(123)

        base_lacets = generate(0.4, dt=10)
        chemin = noise(base_lacets, 20, SincKernel(20), direction=MODE_DIRECTION_ORTHO)[::3]
        chemin = chemin[80:250]
        chemin.scale(3)

        N = 3
        tracks = TrackCollection([chemin]*N)
        tracks.noise(2, DiracKernel())
        cpt = 1
        for track in tracks:
            track.uid = str(cpt)
            cpt += 1
        
        af_algos = ['uid']
        cell_operators = [co_count_distinct]

        SIZE = 15
        marge = 0
        resolution = (SIZE, SIZE)
        bbox = tracks.bbox()

        # ---------------------------------------------------------------------
        raster = summarize(tracks, af_algos, cell_operators,
                               resolution, marge, align=BBOX_ALIGN_LL)
        map1 = raster.getAFMap('uid#co_count_distinct')
        map1.plotAsVectorGraphic()
        # print (raster)

        self.assertEqual(round(raster.xmin, 1), -5.2)
        self.assertEqual(round(raster.xmax, 1), 54.8)
        self.assertEqual(round(raster.ymin, 1), -22.4)
        self.assertEqual(round(raster.ymax, 1), 52.6)
        
        self.assertEqual(raster.ncol, 4)
        self.assertEqual(raster.nrow, 5)
    
        self.assertEqual(raster.resolution[0], 15)
        self.assertEqual(raster.resolution[1], 15)

        self.assertEqual(map1.grid[0][0], 3)
        self.assertEqual(map1.grid[1][0], 3)
        self.assertEqual(map1.grid[2][0], 3)
        self.assertEqual(map1.grid[3][0], 3)
        self.assertEqual(map1.grid[4][0], 1)

        self.assertEqual(map1.grid[0][1], 3)
        self.assertEqual(map1.grid[1][1], 3)
        self.assertEqual(map1.grid[2][1], 3)
        self.assertEqual(map1.grid[3][1], 1)
        self.assertEqual(map1.grid[4][1], 0)

        self.assertEqual(map1.grid[0][2], 0)
        self.assertEqual(map1.grid[1][2], 0)
        self.assertEqual(map1.grid[2][2], 2)
        self.assertEqual(map1.grid[3][2], 3)
        self.assertEqual(map1.grid[4][2], 3)

        self.assertEqual(map1.grid[0][3], 0)
        self.assertEqual(map1.grid[1][3], 0)
        self.assertEqual(map1.grid[2][3], 0)
        self.assertEqual(map1.grid[3][3], 3)
        self.assertEqual(map1.grid[4][3], 1)

        # ---------------------------------------------------------------------
        raster = summarize(tracks, af_algos, cell_operators,
                               resolution, marge, align=BBOX_ALIGN_CENTER)
        map1 = raster.getAFMap('uid#co_count_distinct')
        map1.plotAsVectorGraphic()
        #print (raster)

        self.assertEqual(round(raster.xmin, 1), -8.5)
        self.assertEqual(round(raster.xmax, 1), 51.5)
        self.assertEqual(round(raster.ymin, 1), -26.4)
        self.assertEqual(round(raster.ymax, 1), 48.6)
        
        self.assertEqual(raster.ncol, 4)
        self.assertEqual(raster.nrow, 5)
    
        self.assertEqual(raster.resolution[0], 15)
        self.assertEqual(raster.resolution[1], 15)

        self.assertEqual(map1.grid[0][0], 3)
        self.assertEqual(map1.grid[1][0], 3)
        self.assertEqual(map1.grid[2][0], 3)
        self.assertEqual(map1.grid[3][0], 3)
        self.assertEqual(map1.grid[4][0], 0)

        self.assertEqual(map1.grid[0][1], 3)
        self.assertEqual(map1.grid[1][1], 3)
        self.assertEqual(map1.grid[2][1], 1)
        self.assertEqual(map1.grid[3][1], 0)
        self.assertEqual(map1.grid[4][1], 0)

        self.assertEqual(map1.grid[0][2], 0)
        self.assertEqual(map1.grid[1][2], 0)
        self.assertEqual(map1.grid[2][2], 3)
        self.assertEqual(map1.grid[3][2], 3)
        self.assertEqual(map1.grid[4][2], 3)

        self.assertEqual(map1.grid[0][3], 0)
        self.assertEqual(map1.grid[1][3], 0)
        self.assertEqual(map1.grid[2][3], 3)
        self.assertEqual(map1.grid[3][3], 3)
        self.assertEqual(map1.grid[4][3], 3)


        # ---------------------------------------------------------------------
        raster = summarize(tracks, af_algos, cell_operators,
                               resolution, marge, align=BBOX_ALIGN_UR)
        map1 = raster.getAFMap('uid#co_count_distinct')
        map1.plotAsVectorGraphic()
        #print (raster)

        self.assertEqual(round(raster.xmin, 1), -11.8)
        self.assertEqual(round(raster.xmax, 1), 48.2)
        self.assertEqual(round(raster.ymin, 1), -30.3)
        self.assertEqual(round(raster.ymax, 1), 44.7)
        
        self.assertEqual(raster.ncol, 4)
        self.assertEqual(raster.nrow, 5)
    
        self.assertEqual(raster.resolution[0], 15)
        self.assertEqual(raster.resolution[1], 15)

        self.assertEqual(map1.grid[0][0], 3)
        self.assertEqual(map1.grid[1][0], 3)
        self.assertEqual(map1.grid[2][0], 3)
        self.assertEqual(map1.grid[3][0], 3)
        self.assertEqual(map1.grid[4][0], 0)

        self.assertEqual(map1.grid[0][1], 3)
        self.assertEqual(map1.grid[1][1], 2)
        self.assertEqual(map1.grid[2][1], 1)
        self.assertEqual(map1.grid[3][1], 0)
        self.assertEqual(map1.grid[4][1], 0)

        self.assertEqual(map1.grid[0][2], 1)
        self.assertEqual(map1.grid[1][2], 3)
        self.assertEqual(map1.grid[2][2], 3)
        self.assertEqual(map1.grid[3][2], 3)
        self.assertEqual(map1.grid[4][2], 3)

        self.assertEqual(map1.grid[0][3], 0)
        self.assertEqual(map1.grid[1][3], 0)
        self.assertEqual(map1.grid[2][3], 3)
        self.assertEqual(map1.grid[3][3], 3)
        self.assertEqual(map1.grid[4][3], 3)


if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestSummarising("test_summarize_af"))
    suite.addTest(TestSummarising("test_summarize_af_grid_grande"))
    suite.addTest(TestSummarising("test_synthetic_dataset"))
    runner = TextTestRunner()
    runner.run(suite)
    
    