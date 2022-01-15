# -*- coding: utf-8 -*-

import os.path
from unittest import TestCase, TestSuite, TextTestRunner

from tracklib.core.Coords import ENUCoords
from tracklib.core.Obs import Obs
from tracklib.core.Track import Track
from tracklib.core.GPSTime import GPSTime
from tracklib.io.FileWriter import FileWriter


class TestFileWriter(TestCase):
    
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
        FileWriter.writeToFile(track, csvpath, id_E=0,id_N=1,id_U=2,id_T=3,h=1, separator=";")
        contents = open(csvpath).read()
        
        txt  = "#srid: ENU\n"
        txt += "#E;N;U;time\n"
        txt += "0.000;0.000;0.000;01/01/2020 10:00:00\n"
        txt += "0.000;1.000;0.000;01/01/2020 10:00:01\n"
        self.assertEqual(contents.strip(), txt.strip())
        


if __name__ == '__main__':
    #unittest.main()
    suite = TestSuite()
    suite.addTest(TestFileWriter("test_write_csv_minim"))
    runner = TextTestRunner()
    runner.run(suite)


