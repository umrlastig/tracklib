# -*- coding: utf-8 -*-

from typing import Literal   

from tracklib.core.Track import Track
from tracklib.core.TrackCollection import TrackCollection

#import os # This is is needed in the pyqgis console also
from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsProject, QgsVectorLayer, QgsField
from qgis.core import QgsPointXY, QgsFeature, QgsGeometry
from qgis.core import QgsMarkerSymbol

class QgisWriter:
    """
    Write GPS tracks in Qgis.
    """
    
    @staticmethod
    def writeTracksToQgisLayer(tracks, type: Literal["LINE", "POINT"] = "LINE", af=None):
        """
        Transforms track into a Qgis Layer.
        :param type: "POINT" or "LINE"
        :param af: AF used for coloring in POINT mode
        """
        
        if isinstance(tracks, Track):
            collection = TrackCollection()
            collection.addTrack(tracks)
            tracks = collection
        
        layerPoint = QgsVectorLayer("Point?crs=epsg:2154", "Tracks", "memory")
        pr = layerPoint.dataProvider()
        pr.addAttributes([QgsField("idtrace", QVariant.Int)])
        pr.addAttributes([QgsField("idpoint", QVariant.Int)])
        layerPoint.updateFields()

        for i in range(tracks.size()):
            track = tracks.getTrack(i)
            for j in range(track.size()):
                obs = track.getObs(j)
                X = float(obs.position.getX())
                Y = float(obs.position.getY())
                pt = QgsPointXY(X, Y)
                gPoint = QgsGeometry.fromPointXY(pt)
                fet = QgsFeature()
                
                fet.setGeometry(gPoint)
                fet.setAttributes([i+1, j+1]) 
                pr.addFeatures([fet])

        symbol = QgsMarkerSymbol.createSimple({
            'name': 'circle', 
            'color': 'orange', 
            'size': '0.8', 
            'outline_color': 'orange'})
        layerPoint.renderer().setSymbol(symbol)

        layerPoint.updateExtents()
        QgsProject.instance().addMapLayer(layerPoint)

        
