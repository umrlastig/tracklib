# -*- coding: utf-8 -*-
'''
Write GPS track in Gpx file(s).


'''

import os
from tracklib.core.Track import Track
import tracklib.core.core_utils as utils
import tracklib.core.Operator as Operator
from tracklib.core.TrackCollection import TrackCollection


class GpxWriter:
		
	@staticmethod
	def writeToGpx(tracks, path="", af=None):
		'''
		Transforms track into Gpx string
		# path: file to write gpx (gpx returned in standard output if empty)
		af: AF exported in gpx file
		'''
		if isinstance(tracks, Track):
			collection = TrackCollection()
			collection.addTrack(tracks)
			tracks = collection
			
		output  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
		output += "<gpx>\n"
		for i in range(len(tracks)):
			track = tracks.getTrack(i)
			output += "    <trk>\n"
			output += "        <trkseg>\n"
			for i in range(len(track)):
				x = '{:3.8f}'.format(track[i].position.getX())
				y = '{:3.8f}'.format(track[i].position.getY())
				output += "            <trkpt lat=\""+y+"\" lon=\""+x+"\"></trkpt>\n"        
			output += "        </trkseg>\n"
			output += "    </trk>\n"
		output += "</gpx>\n"
		
		if path:
			f = open(path, "w")
			f.write(output)
			f.close()
			return "KML written in file [" + path + "]" 
			
		return output
		
	
			
		