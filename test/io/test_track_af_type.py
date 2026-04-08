# -*- coding: utf-8 -*-

import os.path
from unittest import TestCase, TestSuite, TextTestRunner
from tracklib import (Track, TrackReader, TrackWriter,
                      TrackFormat, TYPE_CUT_AND_SELECT, MODE_CROSSES,
                      Constraint, Polygon, TrackCollection)


class TestAfType(TestCase):
    

    def setUp (self):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../..")


    def test_af_num_version(self):
        csvpath = os.path.join(self.resource_path, 'data/collection/')
        fmt = TrackFormat({'ext': 'CSV',
                               'srid': 'ENU',
                               'id_E': 1, 'id_N': 0, 'id_U': 3, 'id_T': 2,
                               'time_fmt': '2D/2M/4Y 2h:2m:2s',
                               'separator': ';',
                               'header': 0,
                               'cmt': '#',
                               'read_all': True})
        rawCollection = TrackReader.readFromFile(csvpath, fmt)

        X = [950987, 951409, 950696, 949467, 947934, 948545, 950987]
        Y = [6513197, 6512091, 6511113, 6510719, 6511949, 6512621, 6513197]
        poly = Polygon(X, Y)
        constraintBBox = Constraint(shape=poly, mode=MODE_CROSSES, type=TYPE_CUT_AND_SELECT)


        cutCollection = TrackCollection()
        for trace in rawCollection:

            selection = constraintBBox.select(TrackCollection([trace]))
            if len(selection) <= 0:
                continue

            idxSelect = 1
            o1 = None
            tn = Track()
            for o2 in selection.getTrack(0):
                if o1 is not None:
                    if o1.distance2DTo(o2) > 50:
                        # on coupe la trace pour créer un nouveau morceau
                        if tn.size() >= 10:

                            num = trace.getObsAnalyticalFeature('num', 0)
                            # print (num, type(num))
                            tn.createAnalyticalFeature('num', num)

                            # idxSelect = 10
                            version = "v" + str(idxSelect)
                            tn.createAnalyticalFeature('version', version)
                            cutCollection.addTrack(tn)
                            idxSelect += 1

                        tn = Track()
                tn.addObs(o2)
                o1 = o2

            if tn.size() >= 10:
                num = str(trace.getObsAnalyticalFeature('num', 0))
                version = "v" + str(idxSelect)
                tn.createAnalyticalFeature('num', num)
                tn.createAnalyticalFeature('version', version)
                cutCollection.addTrack(tn)


        print ('Number of tracks after segmentation: ' + str(cutCollection.size()))
        print ('    Example num : ', str(cutCollection.getTrack(2).getObsAnalyticalFeature('num', 0)))
        print ('    Example version : ', str(cutCollection.getTrack(2).getObsAnalyticalFeature('version', 0)))


        print (cutCollection.size())
        trace = cutCollection.getTrack(0)

        num = trace.getObsAnalyticalFeature('num', 0)
        print ('num', num, type(num))
        version = trace.getObsAnalyticalFeature('version', 0)
        print ('version', version, type(version))


        #idxSelect = 10
        #version = "v" + str(idxSelect)
        #trace.createAnalyticalFeature('version', version)
        



        '''
        #self.assertEqual(470, trace.size(), "Size of track")
        af_names = ['num', 'version']
        outcsvpath = os.path.join(self.resource_path, 'data/csv/6337_v1.csv')
        TrackWriter.writeToFile(trace, outcsvpath,
                                     id_E=1, id_N=0, id_U=3, id_T=2,
                                     h=1, separator=";", af_names=af_names)





        #version = trace.getObsAnalyticalFeature('version', 0)
        #print (version, type(version))


        fmt = TrackFormat({'ext': 'CSV',
                               'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': -1,
                               'srid': 'ENUCoords',
                               'separator': ';',
                               'header': 0,
                               'cmt': '#',
                               'read_all': True,
                               'verbose': False})
        trace = TrackReader.readFromFile(outcsvpath, fmt)

        num = trace.getObsAnalyticalFeature('num', 0)
        print (num, type(num))

        version = trace.getObsAnalyticalFeature('version', 0)
        print (version, type(version))
        '''




if __name__ == '__main__':

    suite = TestSuite()

    suite.addTest(TestAfType("test_af_num_version"))

    runner = TextTestRunner()
    runner.run(suite)