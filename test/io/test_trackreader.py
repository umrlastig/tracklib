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
        print (fmt)

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

    def test_read_wkt_multilinestring(self):
        wkt = "MULTILINESTRING((996650.11647090199403465 6543000.30213597603142262, 996648.01232606021221727 6542999.45545507315546274), (996655.91265207773540169 6543010.73748384788632393, 996658.86122083698865026 6543014.4771343320608139),(996655.91265207773540169 6543010.73748384788632393, 996655.71583024342544377 6543010.01380750071257353),(996655.71583024342544377 6543010.01380750071257353, 996652.44237655051983893 6543005.95702100824564695),(996652.44237655051983893 6543005.95702100824564695, 996651.91560408123768866 6543003.65730366297066212),(996651.91560408123768866 6543003.65730366297066212, 996650.41783572779968381 6543001.62264404352754354),(996650.41783572779968381 6543001.62264404352754354, 996650.11647090199403465 6543000.30213597603142262),(996650.11647090199403465 6543000.30213597603142262, 996651.0192229722160846 6542998.67892009764909744),(996655.17944290838204324 6542995.91113406512886286, 996651.0192229722160846 6542998.67892009764909744),(996656.94917890150099993 6542996.08491136785596609, 996655.17944290838204324 6542995.91113406512886286),(996656.94917890150099993 6542996.08491136785596609, 996659.90240167547017336 6542994.01624550763517618),(996662.69101955939549953 6542994.80311255995184183, 996659.90240167547017336 6542994.01624550763517618),(996662.69101955939549953 6542994.80311255995184183, 996664.93295634770765901 6542993.3369878027588129),(996667.89205733861308545 6542994.05954674631357193, 996664.93295634770765901 6542993.3369878027588129),(996667.89205733861308545 6542994.05954674631357193, 996670.13725782255642116 6542992.80164186377078295),(996670.13725782255642116 6542992.80164186377078295, 996672.96432189317420125 6542993.29430998675525188),(996675.49101663113106042 6542992.08920585177838802, 996672.96432189317420125 6542993.29430998675525188),(996677.87858522450551391 6542992.33889986388385296, 996675.49101663113106042 6542992.08920585177838802),(996677.87858522450551391 6542992.33889986388385296, 996681.01695903507061303 6542991.01363334897905588),(996681.01695903507061303 6542991.01363334897905588, 996682.4986422877991572 6542991.06987814232707024),(996682.4986422877991572 6542991.06987814232707024, 996686.43688657938037068 6542989.50474618095904589),(996686.43688657938037068 6542989.50474618095904589, 996686.66367841197643429 6542989.29915812890976667),(996686.66367841197643429 6542989.29915812890976667, 996689.37793848034925759 6542988.21187729574739933),(996690.96538174711167812 6542986.80318438541144133, 996689.37793848034925759 6542988.21187729574739933))"
        with self.assertRaises(Exception):
            TrackReader.parseWkt(wkt)
        collection = TrackReader.parsMultiWkt(wkt)
        self.assertEqual(24, collection.size())

        wkt = "MULTILINESTRING((3.1 4.7589,10.001 50,20 25),(-5 -8.2301,-10.004 -8,-15.158 -4.7778))"
        with self.assertRaises(Exception):
            TrackReader.parseWkt(wkt)
        collection = TrackReader.parsMultiWkt(wkt)
        self.assertEqual(2, collection.size())


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


        # On change l'ordre des paramètres pour voir
        ObsTime.setReadFormat("2D/2M/4Y 2h:2m:2s")
        chemin = os.path.join(self.resource_path, 'data/test/csv')
        param = TrackFormat({'ext': 'CSV',
                             'separator': ",",
                             'id_T': -1,
                 'id_N': 2,
                 'id_U': -1,
                 'id_E': 1
                 })
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


    def test_format_astring(self):
        ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        param = TrackFormat({'name': 'CHAMOIS',
                             'ext': 'CSV',
                             'id_E': 5,
                             'id_N': 6,
                             'id_U' : -1,
                             'id_T' : 4,
                             'time_ini': -1,
                             'separator': 'c',
                             'header': 1,
                             'srid': 'ENU',
                             'read_all': True,
                             'no_data_value': -1})
        self.assertEqual(param.asString(),
        "CHAMOIS, CSV, 5, 6, -1, 4, -1, c, 1, #, -1, ENU, 4Y-2M-2D 2h:2m:2s, True")


    def test_read_csv_verbose(self):
        csvpath = os.path.join(self.resource_path, 'data/csv/22245.csv')
        param = TrackFormat({'ext': 'CSV',
                             'id_E': 0,
                             'id_N': 1,
                             'id_U': 2,
                             'id_T': 3,
                             'header': 1})
        trace = TrackReader.readFromFile(csvpath, param, verbose=True)
        self.assertEqual(trace.size(), 52)


if __name__ == '__main__':
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
    suite.addTest(TestTrackReader("test_read_csv_verbose"))

    # WKT
    suite.addTest(TestTrackReader("test_read_wkt_polygon"))
    suite.addTest(TestTrackReader("test_read_wkt_linestring"))
    suite.addTest(TestTrackReader("test_read_wkt_multilinestring"))

    # GPX
    suite.addTest(TestTrackReader("test_read_default_gpx"))
    suite.addTest(TestTrackReader("test_read_gpx_enu_trk"))
    suite.addTest(TestTrackReader("test_read_gpx_geo_trk"))
    suite.addTest(TestTrackReader("test_read_gpx_geo_rte"))
    suite.addTest(TestTrackReader("test_read_gpx_dir"))
    #suite.addTest(TestTrackReader("testReadGpxWithAF"))
    suite.addTest(TestTrackReader("test_read_millisecond"))

    # for resource
    suite.addTest(TestTrackReader("test_format_astring"))

    runner = TextTestRunner()
    runner.run(suite)

