# -*- coding: utf-8 -*-

from tracklib.core.ObsTime import GPSTime
from tracklib.io.RasterReader import RasterReader
from tracklib.io.FileReader import FileReader
import tracklib.algo.Mapping as mapping


chemin = 'tracklib/data/asc/test.asc'
raster = RasterReader.readFromAscFile(chemin)
print (raster.getRasterBand(1))
band = raster.getRasterBand(1)
print ('ele MNT VT:', band.grid[465][1151])


GPSTime.setReadFormat("4Y/2M/2D 2h:2m:2s")
trace = FileReader.readFromFile('tracklib/data/asc/8961191_v3.csv', 
                                id_E=0, id_N=1, id_U=3, id_T=4, 
                                separator=",", h=1)
print (trace.size())
#trace.plot()

mapping.mapOnRaster(trace, raster)
#print (trace.getListAnalyticalFeatures())


for j in range(trace.size()):
    pos = trace.getObs(j).position
    if pos.getX() == 942323.41762134002055973:
        print ('ele MNT AF:', trace.getObsAnalyticalFeature('grid1', j))
        print ('ele Z:', pos.getZ())
#Point ( 6434246.95822110027074814)	
    