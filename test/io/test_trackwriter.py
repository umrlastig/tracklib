# -*- coding: utf-8 -*-

import os.path
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.core.Coords import ENUCoords
from tracklib.core.Obs import Obs
from tracklib.core.Track import Track
from tracklib.core.GPSTime import GPSTime
from tracklib.io.TrackWriter import TrackWriter
from tracklib.algo import Analytics


class TestTrackWriter(TestCase):
    
    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")

    def test_write_csv_minim(self):
        
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        track = Track()
        p1 = Obs(ENUCoords(0, 0), GPSTime.readTimestamp('2020-01-01 10:00:00'))
        track.addObs(p1)
        p2 = Obs(ENUCoords(0, 1), GPSTime.readTimestamp('2020-01-01 10:00:01'))
        track.addObs(p2)
        
        csvpath = os.path.join(self.resource_path, 'data/test/test_write_csv_minim.wkt')
        TrackWriter.writeToFile(track, csvpath, id_E=0,id_N=1,id_U=2,id_T=3,h=1, separator=";")
        contents = open(csvpath).read()
        
        txt  = "#srid: ENU\n"
        txt += "#E;N;U;time\n"
        txt += "0.000;0.000;0.000;01/01/2020 10:00:00.000\n"
        txt += "0.000;1.000;0.000;01/01/2020 10:00:01.000\n"
        self.assertEqual(contents.strip(), txt.strip())
        
        
    def test_write_csv_2AF(self):
        
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        track = Track()
        p1 = Obs(ENUCoords(0, 0), GPSTime.readTimestamp('2020-01-01 10:00:00'))
        track.addObs(p1)
        p2 = Obs(ENUCoords(0, 1), GPSTime.readTimestamp('2020-01-01 10:00:01'))
        track.addObs(p2)
        p3 = Obs(ENUCoords(1, 1), GPSTime.readTimestamp('2020-01-01 10:00:02'))
        track.addObs(p3)
        p4 = Obs(ENUCoords(1, 2), GPSTime.readTimestamp('2020-01-01 10:00:03'))
        track.addObs(p4)
        p5 = Obs(ENUCoords(2, 2), GPSTime.readTimestamp('2020-01-01 10:00:04'))
        track.addObs(p5)
        
        track.addAnalyticalFeature(Analytics.speed)
        track.compute_abscurv()
        
        csvpath = os.path.join(self.resource_path, 'data/test/test_write_csv_2AF.wkt')
        af_names = ['speed', 'abs_curv']
        TrackWriter.writeToFile(track, csvpath, id_E=0, id_N=1, id_U=2, id_T=3, h=1, 
                               separator=";", af_names=af_names)
        contents = open(csvpath).read()
        
        txt  = "#srid: ENU\n"
        txt += "#E;N;U;time;speed;abs_curv\n"
        txt += "0.000;0.000;0.000;01/01/2020 10:00:00.000;1.0;0\n"
        txt += "0.000;1.000;0.000;01/01/2020 10:00:01.000;0.7071067811865476;1.0\n"
        txt += "1.000;1.000;0.000;01/01/2020 10:00:02.000;0.7071067811865476;2.0\n"
        txt += "1.000;2.000;0.000;01/01/2020 10:00:03.000;0.7071067811865476;3.0\n"
        txt += "2.000;2.000;0.000;01/01/2020 10:00:04.000;1.0;4.0\n"
        self.assertEqual(contents.strip(), txt.strip())
        
        
    def test_write_csv_2AF_desordre(self):
        
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        track = Track()
        p1 = Obs(ENUCoords(0, 0), GPSTime.readTimestamp('2020-01-01 10:00:00'))
        track.addObs(p1)
        p2 = Obs(ENUCoords(0, 1), GPSTime.readTimestamp('2020-01-01 10:00:01'))
        track.addObs(p2)
        p3 = Obs(ENUCoords(1, 1), GPSTime.readTimestamp('2020-01-01 10:00:02'))
        track.addObs(p3)
        p4 = Obs(ENUCoords(1, 2), GPSTime.readTimestamp('2020-01-01 10:00:03'))
        track.addObs(p4)
        p5 = Obs(ENUCoords(2, 2), GPSTime.readTimestamp('2020-01-01 10:00:04'))
        track.addObs(p5)
        
        track.addAnalyticalFeature(Analytics.speed)
        track.compute_abscurv()
        
        csvpath = os.path.join(self.resource_path, 'data/test/test_write_csv_2AF_desordre.wkt')
        af_names = ['speed', 'abs_curv']
        TrackWriter.writeToFile(track, csvpath, id_E=3, id_N=2, id_U=0, id_T=1, h=1, 
                               separator=";", af_names=af_names)
        contents = open(csvpath).read()
        
        txt  = "#srid: ENU\n"
        txt += "#U;time;N;E;speed;abs_curv\n"
        txt += "0.000;01/01/2020 10:00:00.000;0.000;0.000;1.0;0\n"
        txt += "0.000;01/01/2020 10:00:01.000;1.000;0.000;0.7071067811865476;1.0\n"
        txt += "0.000;01/01/2020 10:00:02.000;1.000;1.000;0.7071067811865476;2.0\n"
        txt += "0.000;01/01/2020 10:00:03.000;2.000;1.000;0.7071067811865476;3.0\n"
        txt += "0.000;01/01/2020 10:00:04.000;2.000;2.000;1.0;4.0\n"
        self.assertEqual(contents.strip(), txt.strip())
        
        
    def test_write_csv_path(self):
        
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        track = Track()
        p1 = Obs(ENUCoords(0, 0), GPSTime.readTimestamp('2020-01-01 10:00:00'))
        track.addObs(p1)
        p2 = Obs(ENUCoords(0, 1), GPSTime.readTimestamp('2020-01-01 10:00:01'))
        track.addObs(p2)
        p3 = Obs(ENUCoords(1, 1), GPSTime.readTimestamp('2020-01-01 10:00:02'))
        track.addObs(p3)
        p4 = Obs(ENUCoords(1, 2), GPSTime.readTimestamp('2020-01-01 10:00:03'))
        track.addObs(p4)
        p5 = Obs(ENUCoords(2, 2), GPSTime.readTimestamp('2020-01-01 10:00:04'))
        track.addObs(p5)
        
        csvpath = os.path.join(self.resource_path, 'data/test/test_write_csv_path.wkt')
        TrackWriter.writeToFile(track, csvpath)
        contents = open(csvpath).read()
        
        txt  = "0.000,0.000,0.000,01/01/2020 10:00:00.000\n"
        txt += "0.000,1.000,0.000,01/01/2020 10:00:01.000\n"
        txt += "1.000,1.000,0.000,01/01/2020 10:00:02.000\n"
        txt += "1.000,2.000,0.000,01/01/2020 10:00:03.000\n"
        txt += "2.000,2.000,0.000,01/01/2020 10:00:04.000\n"
        self.assertEqual(contents.strip(), txt.strip())


if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestTrackWriter("test_write_csv_path"))
    suite.addTest(TestTrackWriter("test_write_csv_minim"))
    suite.addTest(TestTrackWriter("test_write_csv_2AF"))
    suite.addTest(TestTrackWriter("test_write_csv_2AF_desordre"))
    runner = TextTestRunner()
    runner.run(suite)


