# -*- coding: utf-8 -*-
'''
Read GPS track from gpx file.


'''

import os

from tracklib.core.GPSTime import GPSTime
from tracklib.core.Coords import ENUCoords
from tracklib.core.Obs import Obs
import tracklib.core.Track as Track


class FileReader:

	@staticmethod
	def readFromFile(path, id_T, id_E, id_N, id_U=-1, separator=",", DateIni=-1, h=0):
		'''
		The method assumes a single track in file
		Needs to provide a reference pt in geodetic coords
		'''
		
		GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
		
		track = Track.Track()
			
		with open(path) as fp:
		
			# Header
			for i in range(h):
				fp.readline()
		
			line = fp.readline()
			
			while line:
				
				fields = line.split(separator)
				
				if isinstance(DateIni, int):
					time = GPSTime.readTimestamp(fields[id_T])
				else:
					time = DateIni.addSec((float)(fields[id_T]))
					
				E = (float)(fields[id_E])
				N = (float)(fields[id_N])
				
				if int(E) != -1 and int(N) != -1:
					if (id_U < 0):
						U = 0
					else:
						U = (float)(fields[id_U])
					
					point = Obs(ENUCoords(E,N,U), time)
					track.addObs(point)
				
				line = fp.readline()
				
		fp.close()
		
		#print("File " + path + " loaded: \n" + (str)(track.size()) + " point(s) registered")
		
		return track
	
	
	@staticmethod
	def readFromFiles(pathdir, id_T, id_E, id_N, id_U=-1, separator=","):
		
		TRACES = []
		LISTFILE = os.listdir(pathdir)
		for f in LISTFILE:
	
			p = pathdir + '/' + f
			trace = FileReader.readFromFile(p, id_T, id_E, id_N, id_U, separator)
			TRACES.append(trace)
	
		return TRACES
	
