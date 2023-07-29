# -*- coding: utf-8 -*-

import os.path

import filecmp
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib import (Track, ENUCoords, Obs,
                      TrackCollection, ObsTime,
                      TrackWriter, TrackReader,
                      speed, computeAbsCurv)



class TestTrackWriter(TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        self.trace1 = Track(track_id = '11')
        p1 = Obs(ENUCoords(0, 0), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        self.trace1.addObs(p1)
        p2 = Obs(ENUCoords(0, 1), ObsTime.readTimestamp('2020-01-01 10:00:01'))
        self.trace1.addObs(p2)
        p3 = Obs(ENUCoords(1, 1), ObsTime.readTimestamp('2020-01-01 10:00:02'))
        self.trace1.addObs(p3)
        p4 = Obs(ENUCoords(1, 2), ObsTime.readTimestamp('2020-01-01 10:00:03'))
        self.trace1.addObs(p4)
        p5 = Obs(ENUCoords(2, 2), ObsTime.readTimestamp('2020-01-01 10:00:04'))
        self.trace1.addObs(p5)
        
        self.trace2 = Track()
        self.trace2.tid = '12'
        pm3 = Obs(ENUCoords(-2, -1), ObsTime.readTimestamp('2020-01-01 09:59:44'))
        self.trace2.addObs(pm3)
        pm2 = Obs(ENUCoords(-1, -1), ObsTime.readTimestamp('2020-01-01 09:59:48'))
        self.trace2.addObs(pm2)
        pm1 = Obs(ENUCoords(-1, 0), ObsTime.readTimestamp('2020-01-01 09:59:55'))
        self.trace2.addObs(pm1)
        p1 = Obs(ENUCoords(0, 0), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        self.trace2.addObs(p1)
        p2 = Obs(ENUCoords(0, 2), ObsTime.readTimestamp('2020-01-01 10:00:01'))
        self.trace2.addObs(p2)
        p3 = Obs(ENUCoords(1, 2), ObsTime.readTimestamp('2020-01-01 10:00:02'))
        self.trace2.addObs(p3)
        p4 = Obs(ENUCoords(1, 5), ObsTime.readTimestamp('2020-01-01 10:00:03'))
        self.trace2.addObs(p4)
        p5 = Obs(ENUCoords(2, 5), ObsTime.readTimestamp('2020-01-01 10:00:04'))
        self.trace2.addObs(p5)
        p6 = Obs(ENUCoords(2, 9), ObsTime.readTimestamp('2020-01-01 10:00:06'))
        self.trace2.addObs(p6)
        p7 = Obs(ENUCoords(3, 9), ObsTime.readTimestamp('2020-01-01 10:00:08'))
        self.trace2.addObs(p7)
        p8 = Obs(ENUCoords(3, 14), ObsTime.readTimestamp('2020-01-01 10:00:10'))
        self.trace2.addObs(p8)
        p9 = Obs(ENUCoords(4, 14), ObsTime.readTimestamp('2020-01-01 10:00:12'))
        self.trace2.addObs(p9)
        p10 = Obs(ENUCoords(4, 20), ObsTime.readTimestamp('2020-01-01 10:00:15'))
        self.trace2.addObs(p10)
        
        self.trace1.addAnalyticalFeature(speed)
        self.trace2.addAnalyticalFeature(speed)
        
        self.collection = TrackCollection()
        self.collection.addTrack(self.trace1)
        self.collection.addTrack(self.trace2)

    
    def test_write_csv_minim(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        ObsTime.setPrintFormat("2D/2M/4Y 2h:2m:2s")
        track = Track()
        p1 = Obs(ENUCoords(0, 0), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        track.addObs(p1)
        p2 = Obs(ENUCoords(0, 1), ObsTime.readTimestamp('2020-01-01 10:00:01'))
        track.addObs(p2)
        
        csvpath = os.path.join(self.resource_path, 'data/test/test_write_csv_minim.wkt')
        TrackWriter.writeToFile(track, csvpath, id_E=0,id_N=1,id_U=2,id_T=3,h=1, separator=";")
        
        vtpath = os.path.join(self.resource_path, 'data/test/gt/test_write_csv_minim.csv')
        
        filecmp.cmp(csvpath, vtpath)
        
    def test_write_csv_2AF(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        track = Track()
        p1 = Obs(ENUCoords(0, 0), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        track.addObs(p1)
        p2 = Obs(ENUCoords(0, 1), ObsTime.readTimestamp('2020-01-01 10:00:01'))
        track.addObs(p2)
        p3 = Obs(ENUCoords(1, 1), ObsTime.readTimestamp('2020-01-01 10:00:02'))
        track.addObs(p3)
        p4 = Obs(ENUCoords(1, 2), ObsTime.readTimestamp('2020-01-01 10:00:03'))
        track.addObs(p4)
        p5 = Obs(ENUCoords(2, 2), ObsTime.readTimestamp('2020-01-01 10:00:04'))
        track.addObs(p5)
       
        track.addAnalyticalFeature(speed)
        computeAbsCurv(track)
       
        csvpath = os.path.join(self.resource_path, 'data/test/test_write_csv_2AF.wkt')
        af_names = ['speed', 'abs_curv']
        TrackWriter.writeToFile(track, csvpath, id_E=0, id_N=1, id_U=2, id_T=3, h=1, 
                               separator=";", af_names=af_names)
        
        
        vtpath = os.path.join(self.resource_path, 'data/test/gt/test_write_csv_2AF.csv')
        
        filecmp.cmp(csvpath, vtpath)
       
        
    def test_write_csv_2AF_desordre(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        track = Track()
        p1 = Obs(ENUCoords(0, 0), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        track.addObs(p1)
        p2 = Obs(ENUCoords(0, 1), ObsTime.readTimestamp('2020-01-01 10:00:01'))
        track.addObs(p2)
        p3 = Obs(ENUCoords(1, 1), ObsTime.readTimestamp('2020-01-01 10:00:02'))
        track.addObs(p3)
        p4 = Obs(ENUCoords(1, 2), ObsTime.readTimestamp('2020-01-01 10:00:03'))
        track.addObs(p4)
        p5 = Obs(ENUCoords(2, 2), ObsTime.readTimestamp('2020-01-01 10:00:04'))
        track.addObs(p5)
       
        track.addAnalyticalFeature(speed)
        computeAbsCurv(track)
       
        csvpath = os.path.join(self.resource_path, 'data/test/test_write_csv_2AF_desordre.wkt')
        af_names = ['speed', 'abs_curv']
        TrackWriter.writeToFile(track, csvpath, id_E=3, id_N=2, id_U=0, id_T=1, h=1, 
                               separator=";", af_names=af_names)
        
        vtpath = os.path.join(self.resource_path, 'data/test/gt/test_write_csv_2AF_desordre.csv')
        
        filecmp.cmp(csvpath, vtpath)
        
       
        
    def test_write_csv_path(self):
        
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        track = Track()
        p1 = Obs(ENUCoords(0, 0), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        track.addObs(p1)
        p2 = Obs(ENUCoords(0, 1), ObsTime.readTimestamp('2020-01-01 10:00:01'))
        track.addObs(p2)
        p3 = Obs(ENUCoords(1, 1), ObsTime.readTimestamp('2020-01-01 10:00:02'))
        track.addObs(p3)
        p4 = Obs(ENUCoords(1, 2), ObsTime.readTimestamp('2020-01-01 10:00:03'))
        track.addObs(p4)
        p5 = Obs(ENUCoords(2, 2), ObsTime.readTimestamp('2020-01-01 10:00:04'))
        track.addObs(p5)
        
        csvpath = os.path.join(self.resource_path, 'data/test/test_write_csv_path.wkt')
        TrackWriter.writeToFile(track, csvpath)
         
        vtpath = os.path.join(self.resource_path, 'data/test/gt/test_write_csv_path.csv')
        
        filecmp.cmp(csvpath, vtpath)
         
        

    def testWriteOneTrackToOneGpx0AF(self):
        #gpxpath = os.path.join(self.resource_path, 'data/test/gpx1.csv')
        #TrackWriter.writeToGpx(track, path=gpxpath, af=False, oneFile=True)
        
        gpxpath = os.path.join(self.resource_path, 'data/test/gpx1.gpx')
        TrackWriter.writeToGpx(self.trace1, path=gpxpath, af=False, oneFile=True)
        
    def testWriteOneTrackToOneGpx1AF(self):
        gpxpath = os.path.join(self.resource_path, 'data/test/gpx2.gpx')
        TrackWriter.writeToGpx(self.trace1, path=gpxpath, af=True, oneFile=True)
        
    def testWriteOneTrackToOneGpx2AF(self):
        computeAbsCurv(self.trace1)
        gpxpath = os.path.join(self.resource_path, 'data/test/gpx3.gpx')
        TrackWriter.writeToGpx(self.trace1, path=gpxpath, af=True, oneFile=True)

    def testWriteTwoTrackToOneGpx0AF(self):
        computeAbsCurv(self.trace1)
        computeAbsCurv(self.trace2)
        
        gpxpath = os.path.join(self.resource_path, 'data/test/gpx5.gpx')
        TrackWriter.writeToGpx(self.collection, path=gpxpath, af=False, oneFile=True)
        
    def testWriteTwoTrackToOneGpx1AF(self):
        gpxpath = os.path.join(self.resource_path, 'data/test/gpx6.gpx')
        TrackWriter.writeToGpx(self.collection, path=gpxpath, af=True, oneFile=True)
        
    def testWriteTwoTrackToOneGpx2AF(self):
        computeAbsCurv(self.trace1)
        computeAbsCurv(self.trace2)
        
        gpxpath = os.path.join(self.resource_path, 'data/test/gpx7.gpx')
        TrackWriter.writeToGpx(self.collection, path=gpxpath, af=True, oneFile=True)
        
    def testWriteTwoTrackToManyGpx0AF(self):
        computeAbsCurv(self.trace1)
        computeAbsCurv(self.trace2)
        
        gpxpath = os.path.join(self.resource_path, 'data/test/gpx1')
        TrackWriter.writeToGpx(self.collection, path=gpxpath, af=False, oneFile=False)
        
    def testWriteTwoTrackToManyGpx1AF(self):
        gpxpath = os.path.join(self.resource_path, 'data/test/gpx2')
        TrackWriter.writeToGpx(self.collection, path=gpxpath, af=True, oneFile=False)
        
    def testWriteTwoTrackToManyGpx2AF(self):
        computeAbsCurv(self.trace1)
        computeAbsCurv(self.trace2)
        
        gpxpath = os.path.join(self.resource_path, 'data/test/gpx3/')
        TrackWriter.writeToGpx(self.collection, path=gpxpath, af=True, oneFile=False)
        
        gpxpath = os.path.join(self.resource_path, 'data/test/gpx3/11.gpx')
        tracks = TrackReader.readFromGpx(gpxpath, srid='ENU', type="trk", read_all=True)
        trace = tracks[0]
        self.assertEqual(5, trace.size())
        self.assertIsInstance(trace, Track)
        self.assertEqual(0, int(trace.getObs(0).position.E))
        self.assertTrue(trace.hasAnalyticalFeature('speed'))
        self.assertEqual(trace.getObsAnalyticalFeature('speed', 0), 1.0)
        
        
    def testWriteKml(self):
        resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        gpxpath = os.path.join(resource_path, 'data/gpx/activity_5807084803.gpx')
        tracks = TrackReader.readFromGpx(gpxpath)
        trace = tracks.getTrack(0)
       
        trace.addAnalyticalFeature(speed)
        #print (trace.getAnalyticalFeature('speed'))
        
        kmlpath = os.path.join(self.resource_path, 'data/test/couplage.kml')
        TrackWriter.writeToKml(trace, path=kmlpath, type="LINE", af='speed')
        
        
    def testExportGeoJson(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        track = Track()
        p1 = Obs(ENUCoords(0, 0), ObsTime.readTimestamp('2020-01-01 10:00:00'))
        track.addObs(p1)
        p2 = Obs(ENUCoords(0, 1), ObsTime.readTimestamp('2020-01-01 10:00:01'))
        track.addObs(p2)
        
        # ---------------------------------------------------------------------
        txtjson = TrackWriter.exportToGeojson(track, type='POINT')
        # print (txtjson)
        
        txttocompare = '{ '
        txttocompare += '  "type": "FeatureCollection",  '
        txttocompare += '  "features": [ '
        txttocompare += '  { '
        txttocompare += '      "type": "Feature", '
        txttocompare += '      "geometry": { '
        txttocompare += '          "type": "Point",         "coordinates": [ 0.00000,  0.00000] '
        txttocompare += '      },     "properties": {         "prop0": "value0"     } },{ '
        txttocompare += '      "type": "Feature", '
        txttocompare += '      "geometry": { '
        txttocompare += '          "type": "Point",         "coordinates": [ 0.00000,  1.00000]  '
        txttocompare += '      },     "properties": {         "prop0": "value0"     } }    ]} '
    
        import json
        out = json.loads(txttocompare)
        self.assertEqual(out, txtjson)
        
        
        # ---------------------------------------------------------------------
        txtjson = TrackWriter.exportToGeojson(track, type='LINE')
        
        txttocompare = '{     "type": "FeatureCollection", '
        txttocompare += ' "features": [ {     "type": "Feature",  '
        txttocompare += ' "geometry": {         "type": "LineString", '
        txttocompare += ' "coordinates": [[0, 0],[0, 1]]     } }    ]} '
        
        import json
        out = json.loads(txttocompare)
        self.assertEqual(out, txtjson)


if __name__ == '__main__':
    
    suite = TestSuite()
    '''
    suite.addTest(TestTrackWriter("test_write_csv_path"))
    suite.addTest(TestTrackWriter("test_write_csv_minim"))
    suite.addTest(TestTrackWriter("test_write_csv_2AF"))
    suite.addTest(TestTrackWriter("test_write_csv_2AF_desordre"))
    
    # 1 track - 1 gpx
    suite.addTest(TestTrackWriter("testWriteOneTrackToOneGpx0AF"))
    suite.addTest(TestTrackWriter("testWriteOneTrackToOneGpx1AF"))
    suite.addTest(TestTrackWriter("testWriteOneTrackToOneGpx2AF"))
    
    # 2 tracks - gpx
    suite.addTest(TestTrackWriter("testWriteTwoTrackToOneGpx0AF"))
    suite.addTest(TestTrackWriter("testWriteTwoTrackToOneGpx1AF"))
    suite.addTest(TestTrackWriter("testWriteTwoTrackToOneGpx2AF"))
    '''
    #tracks - many gpx
    #suite.addTest(TestTrackWriter("testWriteTwoTrackToManyGpx0AF"))
    #suite.addTest(TestTrackWriter("testWriteTwoTrackToManyGpx1AF"))
    suite.addTest(TestTrackWriter("testWriteTwoTrackToManyGpx2AF"))
    
    #suite.addTest(TestTrackWriter("testWriteKml"))
    #suite.addTest(TestTrackWriter("testExportGeoJson"))
    
    runner = TextTestRunner()
    runner.run(suite)


