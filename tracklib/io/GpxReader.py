# -*- coding: utf-8 -*-
'''
Read GPS track from gpx file.
'''

from xml.dom import minidom

from tracklib.core.GPSTime import GPSTime
from tracklib.core.Coords import GeoCoords
from tracklib.core.Obs import Obs
import tracklib.core.Track as t
from tracklib.core.TrackCollection import TrackCollection

class GpxReader:

    @staticmethod
    def readFromGpx(path):
        '''
        The method assumes a single track in file
        Needs to provide a reference pt in geodetic coords
        
        @return collection of track
        '''
        
        tracks = []
        
        format_old = GPSTime.getReadFormat()
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        doc = minidom.parse(path)
        trkpts = doc.getElementsByTagName('trkpt')
        
        trace = t.Track()
        for trkpt in trkpts:
            lon = float(trkpt.attributes['lon'].value)
            lat = float(trkpt.attributes['lat'].value)
            
            hgt = 0
            eles = trkpt.getElementsByTagName('ele')
            if eles.length > 0:
               hgt = float(eles[0].firstChild.data)
            
            time = ''
            times = trkpt.getElementsByTagName('time')
            if times.length > 0:
                time = GPSTime(times[0].firstChild.data)
            
            coords =  (GeoCoords(lon, lat, hgt))
            
            point = Obs(coords, time)
            trace.addObs(point)
            
        tracks.append(trace)

        # pourquoi ?
        GPSTime.setReadFormat(format_old)
        
        collection = TrackCollection(tracks)
        return collection
    
    
