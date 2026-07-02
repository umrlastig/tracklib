# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TextTestRunner
import matplotlib.pyplot as plt
import os.path

import numpy as np

from tracklib import (Obs, ObsTime, ENUCoords, TrackCollection,
                      speed,NO_DATA_VALUE, orientation,
                      Track, TrackReader, Raster,
                      MinBand, MaxBand, MeanBand,
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
        collection.plot('k-')
        collection.plot('ko')
        plt.show()

        collection.addAnalyticalFeature(speed)


        # ---------------------------------------------------------------------

        marge = 0.0
        res = (60, 60)
        raster = Raster(bbox=collection.bbox(), resolution=res, margin=marge,
                        align=BBOX_ALIGN_CENTER,
                        novalue=0)

        self.assertEqual(raster.getNoDataValue(), 0)
        self.assertEqual(raster.xmin, 10.0 - marge*(370-10))
        self.assertEqual(raster.xmax, 370.0 + marge*(370-10))
        self.assertEqual(raster.ymin, 10.0 - marge*(190-10))
        self.assertEqual(raster.ymax, 190.0 + marge*(190-10))
        
        self.assertEqual(raster.ncol, int (((370-10) + marge*(370-10)) / 60))
        self.assertEqual(raster.nrow, int (((190-10) + marge*(190-10)) / 60))
    
        self.assertEqual(raster.resolution[0], ((370-10) + 2*marge*(370-10)) / raster.ncol)
        self.assertEqual(raster.resolution[1], ((190-10) + 2*marge*(190-10)) / raster.nrow)


        # ---------------------------------------------------------------------

        uidMap = raster.addAFMap("uid")
        uidMap.addCountDistinct()
        uidMap.addCount()
        speedMap = raster.addAFMap("speed")
        speedMap.addMean()
        speedMap.addMax()
        speedMap.addMin()

        self.assertEqual(raster.countAFMap(), 2)
        self.assertEqual(raster.getNamesOfAFMap(), ['uid', 'speed'])

        self.assertEqual(raster.getAFMap('uid').bandCount(), 2)
        self.assertEqual(raster.getAFMap('speed').bandCount(), 3)

        self.assertEqual(raster.getAFMap('uid')[0].getName(), 'count_distinct')
        self.assertEqual(raster.getAFMap('uid')[1].getName(), 'count')

        self.assertEqual(raster.getAFMap('speed')[0].getName(), 'mean')
        self.assertEqual(raster.getAFMap('speed')[1].getName(), 'max')
        self.assertEqual(raster.getAFMap('speed')[2].getName(), 'min')

        self.assertIsInstance(uidMap, AFMap)
        self.assertIsInstance(speedMap, AFMap)
        self.assertIsInstance(raster.getAFMap('speed')[0], MeanBand)
        self.assertIsInstance(raster.getAFMap('speed')[1], MaxBand)
        self.assertIsInstance(raster.getAFMap('speed')[2], MinBand)


        # ---------------------------------------------------------------------

        summarize(collection, raster)

        #  On teste les plots

        uidMap.plot('count')
        uidMap.plotAsVectorGraphic('count')
        uidMap.plotAsVectorGraphic('count_distinct')

        #
        uidMap.histogram('count')


        # ---------------------------------------------------------------------
        # On teste les valeurs de la grille: map 2

        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[2][0], 2)
        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[1][0], 1)
        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[0][0], 0)

        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[2][1], 0)
        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[1][1], 0)
        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[0][1], 0)

        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[2][2], 0)
        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[1][2], 1)
        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[0][2], 0)

        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[2][3], 1)
        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[1][3], 0)
        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[0][3], 0)

        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[2][4], 0)
        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[1][4], 2)
        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[0][4], 1)

        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[2][5], 1)
        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[1][5], 0)
        self.assertEqual(raster.getAFMap('uid')[0].getGrid().values[0][5], 1)


        # ---------------------------------------------------------------------
        # On teste les valeurs de la grille: map 1

        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[2][0], 3)
        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[1][0], 1)
        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[0][0], 0)

        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[2][1], 0)
        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[1][1], 0)
        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[0][1], 0)

        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[2][2], 0)
        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[1][2], 1)
        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[0][2], 0)

        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[2][3], 1)
        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[1][3], 0)
        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[0][3], 0)

        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[2][4], 0)
        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[1][4], 2)
        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[0][4], 1)

        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[2][5], 1)
        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[1][5], 0)
        self.assertEqual(raster.getAFMap('uid')[1].getGrid().values[0][5], 1)


        # ---------------------------------------------------------------------
        # On teste les valeurs de la grille: map 3

        # raster.setNoDataValue(0)

        speedTrace1 = collection.getTrack(0).getAnalyticalFeature('speed')
        speedTrace2 = collection.getTrack(1).getAnalyticalFeature('speed')

        self.assertTrue(abs(raster.getAFMap('speed')[0].getGrid().values[2][0] -
                         ((speedTrace1[0] + speedTrace1[1] + speedTrace2[0]) / 3) < 0.001))

        self.assertTrue(abs(raster.getAFMap('speed')[0].getGrid().values[1][0] - speedTrace1[2]) < 0.001)
        self.assertEqual(raster.getAFMap('speed')[0].getGrid().values[0][0], raster.getNoDataValue())

        self.assertEqual(raster.getAFMap('speed')[0].getGrid().values[2][1], raster.getNoDataValue())
        self.assertEqual(raster.getAFMap('speed')[0].getGrid().values[1][1], raster.getNoDataValue())
        self.assertEqual(raster.getAFMap('speed')[0].getGrid().values[0][1], raster.getNoDataValue())
        
        self.assertEqual(raster.getAFMap('speed')[0].getGrid().values[2][2], raster.getNoDataValue())
        self.assertTrue(abs(raster.getAFMap('speed')[0].getGrid().values[1][2] - speedTrace1[3]) < 0.001)
        self.assertEqual(raster.getAFMap('speed')[0].getGrid().values[0][2], raster.getNoDataValue())
        
        self.assertTrue(abs(raster.getAFMap('speed')[0].getGrid().values[2][3] - speedTrace1[4]) < 0.001)
        self.assertEqual(raster.getAFMap('speed')[0].getGrid().values[1][3], raster.getNoDataValue())
        self.assertEqual(raster.getAFMap('speed')[0].getGrid().values[0][3], raster.getNoDataValue())
        
        self.assertEqual(raster.getAFMap('speed')[0].getGrid().values[2][4], raster.getNoDataValue())
        self.assertTrue(abs(raster.getAFMap('speed')[0].getGrid().values[1][4] - (speedTrace1[5] + speedTrace2[1]) / 2) < 0.001)
        self.assertTrue(abs(raster.getAFMap('speed')[0].getGrid().values[0][4] - speedTrace1[6]) < 0.001)
        
        self.assertTrue(abs(raster.getAFMap('speed')[0].getGrid().values[0][5] - speedTrace1[7]) < 0.001)
        self.assertEqual(raster.getAFMap('speed')[0].getGrid().values[1][5], raster.getNoDataValue())
        self.assertTrue(abs(raster.getAFMap('speed')[0].getGrid().values[2][5] - speedTrace2[2]) < 0.001)

        speedMap.plot('mean')
        plt.show()
        
        



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

        marge = 0.1
        res = (60, 60)

        raster = Raster(bbox=collection.bbox(), resolution=res, margin=marge,
                        align=BBOX_ALIGN_LL)

        uidMap = raster.addAFMap("uid")
        uidMap.addCountDistinct()


        #  Construction du raster
        summarize(collection, raster)


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

        afmap = raster.getAFMap('uid')
        self.assertIsInstance(afmap, AFMap)

        afmap.plotAsVectorGraphic('count_distinct')



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

        # ---------------------------------------------------------------------

        SIZE = 15
        marge = 0
        resolution = (SIZE, SIZE)
        bbox = tracks.bbox()

        raster = Raster(bbox=tracks.bbox(), resolution=resolution, margin=marge,
                        align=BBOX_ALIGN_LL, novalue=0)

        uidMap = raster.addAFMap("uid")
        uidMap.addCountDistinct()

        summarize(tracks, raster)

        raster.getAFMap('uid').plotAsVectorGraphic('count_distinct')

        self.assertEqual(round(raster.xmin, 1), -5.2)
        self.assertEqual(round(raster.xmax, 1), 54.8)
        self.assertEqual(round(raster.ymin, 1), -22.4)
        self.assertEqual(round(raster.ymax, 1), 52.6)
        
        self.assertEqual(raster.ncol, 4)
        self.assertEqual(raster.nrow, 5)
    
        self.assertEqual(raster.resolution[0], 15)
        self.assertEqual(raster.resolution[1], 15)

        grid = raster.getAFMap('uid')['count_distinct'].getGrid().values

        self.assertEqual(grid[0][0], 3)
        self.assertEqual(grid[1][0], 3)
        self.assertEqual(grid[2][0], 3)
        self.assertEqual(grid[3][0], 3)
        self.assertEqual(grid[4][0], 1)

        self.assertEqual(grid[0][1], 3)
        self.assertEqual(grid[1][1], 3)
        self.assertEqual(grid[2][1], 3)
        self.assertEqual(grid[3][1], 1)
        self.assertEqual(grid[4][1], 0)

        self.assertEqual(grid[0][2], 0)
        self.assertEqual(grid[1][2], 0)
        self.assertEqual(grid[2][2], 2)
        self.assertEqual(grid[3][2], 3)
        self.assertEqual(grid[4][2], 3)

        self.assertEqual(grid[0][3], 0)
        self.assertEqual(grid[1][3], 0)
        self.assertEqual(grid[2][3], 0)
        self.assertEqual(grid[3][3], 3)
        self.assertEqual(grid[4][3], 1)


        # ---------------------------------------------------------------------

        raster = Raster(bbox=tracks.bbox(), resolution=resolution, margin=marge,
                        align=BBOX_ALIGN_CENTER, novalue=NO_DATA_VALUE)

        uidMap = raster.addAFMap("uid")
        uidMap.addCountDistinct()

        summarize(tracks, raster)

        raster.getAFMap('uid').plotAsVectorGraphic('count_distinct')
        grid = raster.getAFMap('uid')['count_distinct'].getGrid().values


        self.assertEqual(round(raster.xmin, 1), -8.5)
        self.assertEqual(round(raster.xmax, 1), 51.5)
        self.assertEqual(round(raster.ymin, 1), -26.4)
        self.assertEqual(round(raster.ymax, 1), 48.6)
        
        self.assertEqual(raster.ncol, 4)
        self.assertEqual(raster.nrow, 5)
    
        self.assertEqual(raster.resolution[0], 15)
        self.assertEqual(raster.resolution[1], 15)

        self.assertEqual(grid[0][0], 3)
        self.assertEqual(grid[1][0], 3)
        self.assertEqual(grid[2][0], 3)
        self.assertEqual(grid[3][0], 3)
        self.assertEqual(grid[4][0], NO_DATA_VALUE)

        self.assertEqual(grid[0][1], 3)
        self.assertEqual(grid[1][1], 3)
        self.assertEqual(grid[2][1], 1)
        self.assertEqual(grid[3][1], NO_DATA_VALUE)
        self.assertEqual(grid[4][1], NO_DATA_VALUE)

        self.assertEqual(grid[0][2], NO_DATA_VALUE)
        self.assertEqual(grid[1][2], NO_DATA_VALUE)
        self.assertEqual(grid[2][2], 3)
        self.assertEqual(grid[3][2], 3)
        self.assertEqual(grid[4][2], 3)

        self.assertEqual(grid[0][3], NO_DATA_VALUE)
        self.assertEqual(grid[1][3], NO_DATA_VALUE)
        self.assertEqual(grid[2][3], 3)
        self.assertEqual(grid[3][3], 3)
        self.assertEqual(grid[4][3], 3)


        # ---------------------------------------------------------------------

        raster = Raster(bbox=tracks.bbox(), resolution=resolution, margin=marge,
                        align=BBOX_ALIGN_UR)

        uidMap = raster.addAFMap("uid")
        uidMap.addCountDistinct()

        summarize(tracks, raster)

        raster.getAFMap('uid').plotAsVectorGraphic('count_distinct')
        grid = raster.getAFMap('uid')['count_distinct'].getGrid().values


        self.assertEqual(round(raster.xmin, 1), -11.8)
        self.assertEqual(round(raster.xmax, 1), 48.2)
        self.assertEqual(round(raster.ymin, 1), -30.3)
        self.assertEqual(round(raster.ymax, 1), 44.7)
        
        self.assertEqual(raster.ncol, 4)
        self.assertEqual(raster.nrow, 5)
    
        self.assertEqual(raster.resolution[0], 15)
        self.assertEqual(raster.resolution[1], 15)

        self.assertEqual(grid[0][0], 3)
        self.assertEqual(grid[1][0], 3)
        self.assertEqual(grid[2][0], 3)
        self.assertEqual(grid[3][0], 3)
        self.assertEqual(grid[4][0], NO_DATA_VALUE)

        self.assertEqual(grid[0][1], 3)
        self.assertEqual(grid[1][1], 2)
        self.assertEqual(grid[2][1], 1)
        self.assertEqual(grid[3][1], NO_DATA_VALUE)
        self.assertEqual(grid[4][1], NO_DATA_VALUE)

        self.assertEqual(grid[0][2], 1)
        self.assertEqual(grid[1][2], 3)
        self.assertEqual(grid[2][2], 3)
        self.assertEqual(grid[3][2], 3)
        self.assertEqual(grid[4][2], 3)

        self.assertEqual(grid[0][3], NO_DATA_VALUE)
        self.assertEqual(grid[1][3], NO_DATA_VALUE)
        self.assertEqual(grid[2][3], 3)
        self.assertEqual(grid[3][3], 3)
        self.assertEqual(grid[4][3], 3)


    def test_dominant_band(self):
        '''
        Valeur dominante
        '''


        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        TRACES = []
        
        # ---------------------------------------------------------------------
        trace1 = Track([], 1)

        trace1.addObs(Obs(ENUCoords(0, 0), ObsTime()))
        trace1.addObs(Obs(ENUCoords(1, 1),  ObsTime()))
        trace1.addObs(Obs(ENUCoords(1, 0),  ObsTime()))
        trace1.addObs(Obs(ENUCoords(3, 0),  ObsTime()))
        trace1.addObs(Obs(ENUCoords(3, 3),  ObsTime()))
        trace1.addObs(Obs(ENUCoords(1, 3),  ObsTime()))
        trace1.addObs(Obs(ENUCoords(2, 2),  ObsTime()))
        trace1.addObs(Obs(ENUCoords(2, 1),  ObsTime()))

        trace1.addAnalyticalFeature(orientation)
        print(trace1.getAnalyticalFeature('orientation'))
        TRACES.append(trace1)



        # ---------------------------------------------------------------------
        trace2 = Track([], 2)

        trace2.addObs(Obs(ENUCoords(0, 0.5), ObsTime()))
        trace2.addObs(Obs(ENUCoords(1, 1.5), ObsTime()))
        trace2.addObs(Obs(ENUCoords(1, 0.5), ObsTime()))
        trace2.addObs(Obs(ENUCoords(3, 0.5), ObsTime()))
        trace2.addObs(Obs(ENUCoords(3, 3.5), ObsTime()))
        trace2.addObs(Obs(ENUCoords(1, 3.5),  ObsTime()))
        trace2.addObs(Obs(ENUCoords(2, 2.5),  ObsTime()))
        trace2.addObs(Obs(ENUCoords(2, 1.5),  ObsTime()))

        trace2.addAnalyticalFeature(orientation)
        print(trace2.getAnalyticalFeature('orientation'))
        TRACES.append(trace2)


        # ---------------------------------------------------------------------
        trace3 = Track([], 3)

        trace3.addObs(Obs(ENUCoords(0, 1), ObsTime()))
        trace3.addObs(Obs(ENUCoords(1, 2), ObsTime()))
        trace3.addObs(Obs(ENUCoords(1, 1), ObsTime()))
        trace3.addObs(Obs(ENUCoords(3, 1), ObsTime()))
        trace3.addObs(Obs(ENUCoords(3, 4), ObsTime()))
        trace3.addObs(Obs(ENUCoords(1, 4),  ObsTime()))
        trace3.addObs(Obs(ENUCoords(2, 3),  ObsTime()))
        trace3.addObs(Obs(ENUCoords(2, 2),  ObsTime()))

        trace3.addAnalyticalFeature(orientation)
        print(trace3.getAnalyticalFeature('orientation'))
        TRACES.append(trace3)


        # ---------------------------------------------------------------------
        collection = TrackCollection(TRACES)
        collection.plot()
        collection.plot('ko')
        plt.xlim([-1,5])
        plt.ylim([-1,5])
        plt.plot([0.0,3.0], [-0.5,-0.5], color='gray', linewidth=1, linestyle='dashdot')
        plt.plot([0.0,3.0], [1.5,1.5], color='gray', linewidth=1, linestyle='dashdot')
        plt.plot([0.0,3.0], [3.0,3.0], color='gray', linewidth=1, linestyle='dashdot')
        plt.plot([0.0,3.0], [4.5,4.5], color='gray', linewidth=1, linestyle='dashdot')
        plt.plot([0.0, 0.0], [-0.5,4.5], color='gray', linewidth=1, linestyle='dashdot')
        plt.plot([1.5, 1.5], [-0.5,4.5], color='gray', linewidth=1, linestyle='dashdot')
        plt.plot([3.0, 3.0], [-0.5,4.5], color='gray', linewidth=1, linestyle='dashdot')
        plt.title('collection de traces')
        plt.show()


        # ---------------------------------------------------------------------
        marge = 0.0
        res = (1.5, 1.5)
        raster = Raster(bbox=collection.bbox(), resolution=res, margin=marge,
                        align=BBOX_ALIGN_CENTER,
                        novalue=0)
        # print (raster.bbox)

        orientationMap = raster.addAFMap("orientation")
        orientationMap.addCountDistinct()
        orientationMap.addDominant()

        summarize(collection, raster)

        raster.getAFMap('orientation').plotAsVectorGraphic('count_distinct')
        plt.xlim([-1,5])
        plt.ylim([-1,5])
        plt.show()

        raster.getAFMap('orientation').plotAsVectorGraphic('dominant')
        plt.xlim([-1,5])
        plt.ylim([-1,5])
        plt.show()

        grid1 = raster.getAFMap('orientation')['count_distinct'].getGrid().values
        grid2 = raster.getAFMap('orientation')['dominant'].getGrid().values


        self.assertEqual(int(grid1[2][0]), 2)
        self.assertEqual(int(grid1[2][1]), 2)
        self.assertEqual(int(grid1[1][1]), 2)

        self.assertEqual(grid2[2][1], 1.0)
        self.assertEqual(grid2[1][1], 8.0)
        self.assertEqual(grid2[0][1], 3.0)


    def test_median_band(self):
        '''
        Valeur médiane
        '''


        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        TRACES = []
        
        # ---------------------------------------------------------------------
        trace1 = Track([], 1)

        trace1.addObs(Obs(ENUCoords(0, 0), ObsTime()))
        trace1.addObs(Obs(ENUCoords(1, 1),  ObsTime()))
        trace1.addObs(Obs(ENUCoords(1, 0),  ObsTime()))
        trace1.addObs(Obs(ENUCoords(3, 0),  ObsTime()))
        trace1.addObs(Obs(ENUCoords(3, 3),  ObsTime()))
        trace1.addObs(Obs(ENUCoords(1, 3),  ObsTime()))
        trace1.addObs(Obs(ENUCoords(2, 2),  ObsTime()))
        trace1.addObs(Obs(ENUCoords(2, 1),  ObsTime()))

        trace1.addAnalyticalFeature(orientation)
        print(trace1.getAnalyticalFeature('orientation'))
        TRACES.append(trace1)



        # ---------------------------------------------------------------------
        trace2 = Track([], 2)

        trace2.addObs(Obs(ENUCoords(0, 0.5), ObsTime()))
        trace2.addObs(Obs(ENUCoords(1, 1.5), ObsTime()))
        trace2.addObs(Obs(ENUCoords(1, 0.5), ObsTime()))
        trace2.addObs(Obs(ENUCoords(3, 0.5), ObsTime()))
        trace2.addObs(Obs(ENUCoords(3, 3.5), ObsTime()))
        trace2.addObs(Obs(ENUCoords(1, 3.5),  ObsTime()))
        trace2.addObs(Obs(ENUCoords(2, 2.5),  ObsTime()))
        trace2.addObs(Obs(ENUCoords(2, 1.5),  ObsTime()))

        trace2.addAnalyticalFeature(orientation)
        print(trace2.getAnalyticalFeature('orientation'))
        TRACES.append(trace2)


        # ---------------------------------------------------------------------
        trace3 = Track([], 3)

        trace3.addObs(Obs(ENUCoords(0, 1), ObsTime()))
        trace3.addObs(Obs(ENUCoords(1, 2), ObsTime()))
        trace3.addObs(Obs(ENUCoords(1, 1), ObsTime()))
        trace3.addObs(Obs(ENUCoords(3, 1), ObsTime()))
        trace3.addObs(Obs(ENUCoords(3, 4), ObsTime()))
        trace3.addObs(Obs(ENUCoords(1, 4),  ObsTime()))
        trace3.addObs(Obs(ENUCoords(2, 3),  ObsTime()))
        trace3.addObs(Obs(ENUCoords(2, 2),  ObsTime()))

        trace3.addAnalyticalFeature(orientation)
        print(trace3.getAnalyticalFeature('orientation'))
        TRACES.append(trace3)


        # ---------------------------------------------------------------------
        collection = TrackCollection(TRACES)
        collection.plot()
        collection.plot('ko')
        plt.xlim([-1,5])
        plt.ylim([-1,5])
        plt.plot([0.0,3.0], [-0.5,-0.5], color='gray', linewidth=1, linestyle='dashdot')
        plt.plot([0.0,3.0], [1.5,1.5], color='gray', linewidth=1, linestyle='dashdot')
        plt.plot([0.0,3.0], [3.0,3.0], color='gray', linewidth=1, linestyle='dashdot')
        plt.plot([0.0,3.0], [4.5,4.5], color='gray', linewidth=1, linestyle='dashdot')
        plt.plot([0.0, 0.0], [-0.5,4.5], color='gray', linewidth=1, linestyle='dashdot')
        plt.plot([1.5, 1.5], [-0.5,4.5], color='gray', linewidth=1, linestyle='dashdot')
        plt.plot([3.0, 3.0], [-0.5,4.5], color='gray', linewidth=1, linestyle='dashdot')
        plt.title('collection de traces')
        plt.show()


        # ---------------------------------------------------------------------
        marge = 0.0
        res = (1.5, 1.5)
        raster = Raster(bbox=collection.bbox(), resolution=res, margin=marge,
                        align=BBOX_ALIGN_CENTER,
                        novalue=0)
        # print (raster.bbox)

        orientationMap = raster.addAFMap("orientation")
        orientationMap.addCountDistinct()
        orientationMap.addDominant()
        orientationMap.addMedian()

        summarize(collection, raster)

        raster.getAFMap('orientation').plotAsVectorGraphic('count_distinct')
        plt.xlim([-1,5])
        plt.ylim([-1,5])
        plt.show()

        raster.getAFMap('orientation').plotAsVectorGraphic('dominant')
        plt.xlim([-1,5])
        plt.ylim([-1,5])
        plt.show()

        raster.getAFMap('orientation').plotAsVectorGraphic('median')
        plt.xlim([-1,5])
        plt.ylim([-1,5])
        plt.show()

        grid1 = raster.getAFMap('orientation')['count_distinct'].getGrid().values
        grid2 = raster.getAFMap('orientation')['dominant'].getGrid().values
        grid3 = raster.getAFMap('orientation')['median'].getGrid().values

        self.assertEqual(int(grid1[2][0]), 2)
        self.assertEqual(int(grid1[2][1]), 2)
        self.assertEqual(int(grid1[1][1]), 2)

        self.assertEqual(grid2[2][1], 1.0)
        self.assertEqual(grid2[1][1], 8.0)
        self.assertEqual(grid2[0][1], 3.0)

        self.assertEqual(grid3[0][1], 3.0)
        self.assertEqual(grid3[1][1], 7.5)
        self.assertEqual(grid3[2][0], 2.0)


if __name__ == '__main__':
    suite = TestSuite()

    suite.addTest(TestSummarising("test_summarize_af"))
    suite.addTest(TestSummarising("test_summarize_af_grid_grande"))
    suite.addTest(TestSummarising("test_synthetic_dataset"))
    suite.addTest(TestSummarising("test_dominant_band"))
    suite.addTest(TestSummarising("test_median_band"))

    runner = TextTestRunner()
    runner.run(suite)
    
    