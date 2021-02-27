# -*- coding: utf-8 -*-
'''
Read GPS track from gpx file.
'''

from xml.dom import minidom

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
            
            if (ref == None):
                coords = ENUCoords(lon, lat, hgt)
            else:
                coords =  (GeoCoords(lon, lat, hgt)).toENUCoords(ref)
            
            point = Obs(coords, time)
            trace.addObs(point)
            
        tracks.append(trace)

        # pourquoi ?
        GPSTime.setReadFormat(format_old)
        
        return tracks
    
    
    @staticmethod
    def readFirstPointFromGpx(path):
        
        r = ()
        
        doc = minidom.parse(path)
        trkpts = doc.getElementsByTagName('trkpt')
        
        for trkpt in trkpts:
            lon = float(trkpt.attributes['lon'].value)
            lat = float(trkpt.attributes['lat'].value)
            
            hgt = 0
            eles = trkpt.getElementsByTagName('ele')
            if eles.length > 0:
               hgt = float(eles[0].firstChild.data)
            
            r = (lon,lat,hgt)
        
        return r
                
        
