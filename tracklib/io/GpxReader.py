# -*- coding: utf-8 -*-
'''
Read GPS track from gpx file.
'''

from xml.dom import minidom

from tracklib.core.GPSTime import GPSTime
from tracklib.core.Obs import Obs
import tracklib.core.Utils as utils
import tracklib.core.Track as t
from tracklib.core.TrackCollection import TrackCollection


class GpxReader:

    @staticmethod
    def readFromGpx(path, srid="GEO"):
        '''
        Reads (multiple) tracks in .gpx file
        '''
        
        tracks = TrackCollection()
        
        format_old = GPSTime.getReadFormat()
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        doc = minidom.parse(path)
		
        trks = doc.getElementsByTagName('trk')
        
        for trk in trks:
            trace = t.Track()
            trkpts = trk.getElementsByTagName('trkpt')
            for trkpt in trkpts:
                lon = float(trkpt.attributes['lon'].value)
                lat = float(trkpt.attributes['lat'].value)
            
                hgt = utils.NAN
                eles = trkpt.getElementsByTagName('ele')
                if eles.length > 0:
                   hgt = float(eles[0].firstChild.data)
            
                time = ''
                times = trkpt.getElementsByTagName('time')
                if times.length > 0:
                    time = GPSTime(times[0].firstChild.data)
                else:
                    time = GPSTime()

                point = Obs(utils.makeCoords(lon, lat, hgt, srid), time)
                trace.addObs(point)
            
            tracks.addTrack(trace)

        # pourquoi ? 
		# --> pour remettre le format comme il etait avant la lectre :)
        GPSTime.setReadFormat(format_old)
        
        collection = TrackCollection(tracks)
        return collection
    

