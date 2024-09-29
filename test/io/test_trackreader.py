# -*- coding: utf-8 -*-

import os.path
from unittest import TestCase, TestSuite, TextTestRunner
from tracklib import (Track, TrackFormat,
                      Rectangle, ObsTime, TrackCollection, ENUCoords,
                      TrackReader, Constraint,
                      TYPE_CUT_AND_SELECT, MODE_INSIDE,
                      Selector, WrongArgumentError)


class TestTrackReader(TestCase):
    
    __epsilon = 1
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")
        self.nomproxy = None

    def test_track_format_default_parameter(self):
        fmt = TrackFormat()
        #print (fmt)

        self.assertEqual(fmt.name, "UNDEFINED")
        self.assertEqual(fmt.ext, None)
        self.assertEqual(fmt.id_user, -1)
        self.assertEqual(fmt.id_track, -1)
        self.assertEqual(fmt.id_E, -1)
        self.assertEqual(fmt.id_N, -1)
        self.assertEqual(fmt.id_U, -1)
        self.assertEqual(fmt.id_T, -1)
        self.assertEqual(fmt.type, 'trk')
        self.assertEqual(fmt.id_wkt, -1)
        self.assertEqual(fmt.srid, "ENU")
        self.assertEqual(fmt.time_ini, -1)
        self.assertEqual(fmt.time_fmt, ObsTime.getReadFormat())
        self.assertEqual(fmt.separator, ",")
        self.assertEqual(fmt.header, 0)
        self.assertEqual(fmt.cmt, "#")
        self.assertEqual(fmt.no_data_value, -999999)
        self.assertEqual(fmt.doublequote, False)
        self.assertEqual(fmt.encoding, "UTF-8")
        self.assertEqual(fmt.selector, None)
        self.assertEqual(fmt.af_names, [])
        self.assertEqual(fmt.read_all, False)


    def test_read_simple_csv_format(self):
        csvpath = os.path.join(self.resource_path, 'data/csv/22245.csv')

        # Aucun paramètre: il faut un format
        self.assertRaises(WrongArgumentError, TrackReader.readFromFile, csvpath, None)

        # Aucun paramètre: il faut ext
        param = TrackFormat()
        self.assertRaises(WrongArgumentError, TrackReader.readFromFile, csvpath, param)

        # Il faut ext in CSV
        param = TrackFormat({'ext': 'CVS'})
        #TrackReader.readFromFile(csvpath, param)
        self.assertRaises(WrongArgumentError, TrackReader.readFromFile, csvpath, param)

        # Il faut ext in GPX
        param = TrackFormat({'ext': 'GXP'})
        self.assertRaises(WrongArgumentError, TrackReader.readFromFile, csvpath, param)

        # il manque id_e paramètre
        param = TrackFormat({'ext': 'CSV'})
        self.assertRaises(WrongArgumentError, TrackReader.readFromFile, csvpath, param)

        # il manque id_N paramètre
        param = TrackFormat({'ext': 'CSV',
                             'id_E': 0})
        self.assertRaises(WrongArgumentError, TrackReader.readFromFile, csvpath, param)

        param = TrackFormat({'ext': 'CSV',
                             'id_E': 0,
                             'id_N': 1,
                             'id_U': 2,
                             'id_T': 3})
        self.assertRaises(WrongArgumentError, TrackReader.readFromFile, csvpath, param)

        # 2019/07/12 15:42:35
        param = TrackFormat({'ext': 'CSV',
                             'id_E': 0,
                             'id_N': 1,
                             'id_U': 2,
                             'id_T': 3,
                             'header': 1})
        trace = TrackReader.readFromFile(csvpath, param)
        self.assertEqual(trace.size(), 52)


    def test_read_wkt_polygon(self):
        csvpath = os.path.join(self.resource_path, 'data/wkt/bati.wkt')
        param = TrackFormat({'ext': 'WKT',
                             'id_wkt': 0})
        TRACES = TrackReader.readFromFile(csvpath, param)
        self.assertIsInstance(TRACES, TrackCollection)
        self.assertEqual(2312, TRACES.size())
        
        ll = ENUCoords(655791, 6868715)
        ur = ENUCoords(656055, 6868856)
        bbox = Rectangle(ll, ur)
        constraintBBox = Constraint(shape = bbox, mode = MODE_INSIDE, type=TYPE_CUT_AND_SELECT)
        s = Selector([constraintBBox])

        param = TrackFormat({'ext': 'WKT',
                             'id_wkt': 0,
                             'selector': s})
        TRACES = TrackReader.readFromFile(csvpath, param)
        self.assertIsInstance(TRACES, TrackCollection)
        self.assertEqual(125, TRACES.size())

    def test_read_wkt_linestring(self):
        csvpath = os.path.join(self.resource_path, 'data/wkt/iti.wkt')
        param = TrackFormat({'ext': 'WKT',
                             'id_wkt': 0,
                             'id_user': -1,
                             'id_track' : -1,
                             'separator': '#',
                             'header': 1,
                             'srid': 'ENU',
                             'doublequote': True})
        TRACES = TrackReader.readFromFile(csvpath, param)
        self.assertIsInstance(TRACES, TrackCollection)
        self.assertEqual(3, TRACES.size())
        

    def test_read_gpx_enu_trk(self):
        path = os.path.join(self.resource_path, 'data/gpx/vincennes.gpx')
        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        param = TrackFormat({'ext': 'GPX', 'srid': 'ENU', 'type': 'trk'})
        tracks = TrackReader.readFromFile(path, param)
        trace = tracks[0]
        self.assertEqual(5370, trace.size())
        self.assertIsInstance(trace, Track)
        self.assertLessEqual(abs(trace.length() - 10135), 1, "Longueur gpx enu")
        
    def test_read_default_gpx(self):
        path = os.path.join(self.resource_path, 'data/gpx/activity_5807084803.gpx')
        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        param = TrackFormat({'ext': 'GPX'})
        tracks = TrackReader.readFromFile(path, param)
        trace = tracks[0]
        self.assertEqual(190, trace.size())
        self.assertIsInstance(trace, Track)
        self.assertLessEqual(abs(trace.length() - 2412), self.__epsilon, "Longueur gpx geo")
        
        
    def test_read_gpx_geo_trk(self):
        path = os.path.join(self.resource_path, 'data/gpx/activity_5807084803.gpx')
        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        param = TrackFormat({'ext': 'GPX', 'srid': 'GEO', 'type': "trk"})
        tracks = TrackReader.readFromFile(path, param)
        trace = tracks[0]
        self.assertEqual(190, trace.size())
        self.assertIsInstance(trace, Track)
        self.assertLessEqual(abs(trace.length() - 2412), self.__epsilon, "Longueur gpx geo")

    def test_read_gpx_geo_rte(self):
        path = os.path.join(self.resource_path, 'data/gpx/903313.gpx')
        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        param = TrackFormat({'ext': 'GPX', 'srid': 'GEO', 'type': 'rte'})
        tracks = TrackReader.readFromFile(path, param)
        trace = tracks[0]
        self.assertEqual(1275, trace.size())
        self.assertIsInstance(trace, Track)
        self.assertLessEqual(abs(trace.length() - 12848), self.__epsilon, "Longueur gpx geo")
        
    def test_read_gpx_dir(self):
        path = os.path.join(self.resource_path, 'data/gpx/geo')
        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        param = TrackFormat({'ext': 'GPX', 'srid': 'GEO', 'type': 'trk'})
        tracks = TrackReader.readFromFile(path, param)
        self.assertEqual(2, tracks.size())
        self.assertIsInstance(tracks, TrackCollection)
        
        path = os.path.join(self.resource_path, 'data/gpx/geo/')
        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
        tracks = TrackReader.readFromFile(path, param)
        self.assertEqual(2, tracks.size())
        self.assertIsInstance(tracks, TrackCollection)
        
        
    # def testReadGpxWithAF(self):
    #     path = os.path.join(self.resource_path, 'data/test/12.gpx')
    #     ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
    #     tracks = TrackReader.readFromFile(path, srid='ENU', type='trk', read_all=True)
        
    #     self.assertEqual(1, tracks.size())
    #     self.assertIsInstance(tracks, TrackCollection)
    
    #     trace = tracks.getTrack(0)
    #     self.assertEqual(13, trace.size())
        
    #     self.assertEqual(trace.getListAnalyticalFeatures(), ['speed', 'abs_curv'])
    #     self.assertEqual(trace.getObsAnalyticalFeature('speed', 0), 0.25)
    #     v1 = trace.getObsAnalyticalFeature('speed', 1)
    #     self.assertTrue(abs(v1 - 0.1285) < 0.001)
    #     self.assertEqual(trace.getObsAnalyticalFeature('abs_curv', 0), 
    #             [0, 1.0, 2.0, 3.0, 5.0, 6.0, 9.0, 10.0, 14.0, 15.0, 20.0, 21.0, 27.0])
        
        
    def testReadCsvWithAFTrack(self):
        ObsTime.setReadFormat("2D/2M/4Y 2h:2m:2s")
        chemin = os.path.join(self.resource_path, 'data/test/ecrins_interpol4.csv')
        param = TrackFormat({'ext': 'CSV',
                             'id_E': 0,
                             'id_N': 1,
                             'id_U': 2,
                             'id_T': 3,
                             'separator': ";",
                             'read_all': True})
        track = TrackReader.readFromFile(chemin, param)
        
        self.assertIsInstance(track, Track)
        self.assertEqual(1593, track.size())
        self.assertEqual(track.getListAnalyticalFeatures(),
                ['anglegeom', 'angledeg', 'sommet', 'sommet2', 'virage', 'serie'])

    def testReadCsvDir(self):
        ObsTime.setReadFormat("2D/2M/4Y 2h:2m:2s")
        chemin = os.path.join(self.resource_path, 'data/test/csv')
        param = TrackFormat({'ext': 'CSV',
                'id_E': 1,
                 'id_N': 2,
                 'id_U': -1,
                 'id_T': -1,
                 'separator': ","})
        collection = TrackReader.readFromFile(chemin, param)
        
        self.assertIsInstance(collection, TrackCollection)
        self.assertEqual(collection.size(), 2)

    def testReadCsvSelect(self):
        Xmin = 29.72
        Xmax = 29.77
        Ymin = 62.585
        Ymax = 62.615
        ll = ENUCoords(Xmin, Ymin)
        ur = ENUCoords(Xmax, Ymax)
        bbox = Rectangle(ll, ur)
        constraintBBox = Constraint(shape = bbox, mode = MODE_INSIDE, type=TYPE_CUT_AND_SELECT)
        s = Selector([constraintBBox])
        
        chemin = os.path.join(self.resource_path, 'data/mopsi/wgs84')
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        dateInitiale = '1970-01-01 00:00:00'
        param = TrackFormat({'ext': 'CSV',
                             'id_E': 1,
                             'id_N': 0,
                             'id_T': 2,
                             'srid': 'Geo',
                             'time_ini': ObsTime.readTimestamp(dateInitiale),
                             'time_unit': 0.001,
                             'selector': s,
                             'separator': ' '})
        collection = TrackReader.readFromFile(chemin, param, verbose=False)

        self.assertIsInstance(collection, TrackCollection)
        self.assertEqual(collection.size(), 23)
        
    
    def test_read_millisecond(self):
        ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2s.2zZ")
        
        path = os.path.join(os.path.split(__file__)[0], '../data/issue231018.gpx')
        param = TrackFormat({'ext': 'GPX', 'srid': 'ENU', 'type': 'trk', 'read_all': True})
        tracks = TrackReader.readFromFile(path, param)
        track = tracks[0]
        
        ObsTime.setPrintFormat("4Y-2M-2D 2h:2m:2s.2z")
        
        self.assertEqual("2023-10-15 06:33:22", str(track.getObs(0).timestamp)[0:19])
        self.assertEqual("2023-10-15 06:33:22.50", str(track.getObs(0).timestamp)[0:22])
        
        self.assertEqual("2023-10-15 06:33:22", str(track.getObs(1).timestamp)[0:19])
        self.assertEqual("2023-10-15 06:33:22.75", str(track.getObs(1).timestamp)[0:22])
        
        self.assertEqual("2023-10-15 06:33:23", str(track.getObs(2).timestamp)[0:19])
        self.assertEqual("2023-10-15 06:33:23.00", str(track.getObs(2).timestamp)[0:22])
        
        self.assertEqual("2023-10-15 06:33:23", str(track.getObs(3).timestamp)[0:19])
        self.assertEqual("2023-10-15 06:33:23.25", str(track.getObs(3).timestamp)[0:22])
        
        
    def test_read_csv_format_date(self):
        ObsTime.setPrintFormat("4Y-2M-2D 2h:2m:2s.2z")
        csvpath = os.path.join(self.resource_path, 'test/data/csv_format.csv')
        track = TrackReader.readFromFile(csvpath, "CHAMOIS")
        
        self.assertEqual(track.size(), 3)
        
        self.assertEqual("1970-01-01", str(track.getObs(0).timestamp)[0:10])
        
        self.assertEqual("1970-01-01", str(track.getObs(1).timestamp)[0:10])
        self.assertEqual(-999999, track.getObs(1).position.getX())
        self.assertEqual(-999999, track.getObs(1).position.getY())
        
        self.assertEqual("2017-12-06 04:01:00", str(track.getObs(2).timestamp)[0:19])
        self.assertEqual(972940.7050129613, track.getObs(2).position.getX())
        self.assertEqual(6418873.1726411795, track.getObs(2).position.getY())


if __name__ == '__main__':
    #unittest.main()
    suite = TestSuite()

    # TrackFormat: dict
    suite.addTest(TestTrackReader("test_track_format_default_parameter"))

    # TrackFormat : str
    suite.addTest(TestTrackReader("test_read_csv_format_date"))

    # CSV
    suite.addTest(TestTrackReader("test_read_simple_csv_format"))
    suite.addTest(TestTrackReader("testReadCsvWithAFTrack"))
    suite.addTest(TestTrackReader("testReadCsvDir"))
    suite.addTest(TestTrackReader("testReadCsvSelect"))

    # WKT
    suite.addTest(TestTrackReader("test_read_wkt_polygon"))
    suite.addTest(TestTrackReader("test_read_wkt_linestring"))
    
    # GPX
    suite.addTest(TestTrackReader("test_read_default_gpx"))
    suite.addTest(TestTrackReader("test_read_gpx_enu_trk"))
    suite.addTest(TestTrackReader("test_read_gpx_geo_trk"))
    suite.addTest(TestTrackReader("test_read_gpx_geo_rte"))
    suite.addTest(TestTrackReader("test_read_gpx_dir"))
    #suite.addTest(TestTrackReader("testReadGpxWithAF"))
    suite.addTest(TestTrackReader("test_read_millisecond"))

    runner = TextTestRunner()
    runner.run(suite)

