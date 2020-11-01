# -*- coding: utf-8 -*-
'''
Read GPS track from gpx file.
'''

from tracklib.core.GPSTime import GPSTime
from tracklib.core.Coords import ENUCoords, GeoCoords
from tracklib.core.Obs import Obs
import tracklib.core.Track as t

class GpxReader:

	@staticmethod
	def readFromGpx(path, ref=None):
		'''
		The method assumes a single track in file
		Needs to provide a reference pt in geodetic coords
		'''
		
		tracks = []
		
		format_old = GPSTime.getReadFormat()
		GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2s.3zZ")
		
		with open(path) as fp:
			line = fp.readline()
			while line:
				if (line.find("<trkseg>") >= 0):
					tracks.append(t.Track());
				if (line.find("<trkpt") >= 0):
					tab = line.split("\"")
					xy = [float(tab[3]), (float)(tab[1])]
				if (line.find("<ele") >= 0):
					line = line.split("<ele>")[1]
					line = line.split("</ele>")[0]
					hgt = (float)(line)
				if (line.find("<time") >= 0):
					line = line.split("<time>")[1]
					line = line.split("</time>")[0]
					time = GPSTime(line)
				if (line.find("</trkpt>") >= 0):	
					if (ref == None):
						coords = ENUCoords(xy[0], xy[1], hgt)
					else:
						coords =  (GeoCoords(xy[0], xy[1], hgt)).toENUCoords(ref)
					point = Obs(coords, time)
					tracks[-1].addObs(point)
				line = fp.readline()
				
		fp.close()
		
		GPSTime.setReadFormat(format_old)
		
		return tracks
	
	
