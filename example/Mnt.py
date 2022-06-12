# -*- coding: utf-8 -*-

from tracklib.core.GPSTime import GPSTime
from tracklib.io.AsciiReader import AsciiReader
from tracklib.io.FileReader import FileReader
import tracklib.algo.Mapping as mapping


chemin = 'tracklib/data/asc/test.asc'
raster = AsciiReader.readFromAscFile(chemin)
print (raster.getRasterBand(1))

GPSTime.setReadFormat("4Y/2M/2D 2h:2m:2s")
trace = FileReader.readFromFile('tracklib/data/asc/8961191_v2.csv', 
                                id_E=3, id_N=4, id_U=5, id_T=2, 
                                separator=",", h=1)
print (trace.size())
#trace.plot()

#mapping.mapOnRaster(trace, raster)


    