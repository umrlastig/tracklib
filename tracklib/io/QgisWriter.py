# -*- coding: utf-8 -*-

from typing import Literal   

from tracklib.core.Track import Track
from tracklib.core.TrackCollection import TrackCollection

#import os # This is is needed in the pyqgis console also
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsProject, QgsVectorLayer, QgsField
from qgis.core import QgsPointXY, QgsFeature, QgsGeometry
from qgis.core import QgsMarkerSymbol, QgsLineSymbol

class QgisWriter:
    """
    Write GPS tracks in Qgis.
    """
    
    @staticmethod
    def writeTracksToQgisLayer(tracks, type: Literal["LINE", "POINT"] = "LINE", 
                               af=False, layerName = "Tracks"):
        """
        Transforms track into a Qgis Layer.
        :param type: "POINT" or "LINE"
        :param af: AF exported in qgis layer like attributes
        """
        
        if isinstance(tracks, Track):
            collection = TrackCollection()
            collection.addTrack(tracks)
            tracks = collection
        
        if type == 'POINT':
            layerTracks = QgsVectorLayer("Point?crs=epsg:2154", layerName, "memory")
        if type == 'LINE':
            layerTracks = QgsVectorLayer("LineString?crs=epsg:2154", layerName, "memory")

            
        pr = layerTracks.dataProvider()
        pr.addAttributes([QgsField("idtrace", QVariant.Int)])
        pr.addAttributes([QgsField("idpoint", QVariant.Int)])
        # z 
        # timestamp
        
        
        if af:
            for af_name in tracks.getTrack(0).getListAnalyticalFeatures():
                pr.addAttributes([QgsField(af_name, QVariant.Double)])
                # f.write(str())
        
        layerTracks.updateFields()

        for i in range(tracks.size()):
            track = tracks.getTrack(i)
            
            ptOld = None
            for j in range(track.size()):
                obs = track.getObs(j)
                X = float(obs.position.getX())
                Y = float(obs.position.getY())
                pt = QgsPointXY(X, Y)
                gPoint = QgsGeometry.fromPointXY(pt)
                
                attrs = [i+1, j+1]
                # AF
                if af:
                    for af_name in track.getListAnalyticalFeatures():
                        attrs.append(track.getObsAnalyticalFeature(af_name, j))
                        
                if type == 'POINT':                
                    fet = QgsFeature()
                    fet.setAttributes(attrs)
                    fet.setGeometry(gPoint)
                    pr.addFeatures([fet])
                    
                if type == 'LINE' and ptOld != None:
                    fet = QgsFeature()
                    fet.setAttributes(attrs) 
                    fet.setGeometry(QgsGeometry.fromPolylineXY([ptOld, pt]))
                    pr.addFeatures([fet])
                
                ptOld = pt
                
        if type == 'POINT':
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'circle', 
                'color': 'orange', 
                'size': '0.8', 
                'outline_color': 'orange'})
            layerTracks.renderer().setSymbol(symbol)
        if type == 'LINE':
            symbolL = QgsLineSymbol.createSimple({
                'penstyle':'solid', 
                'width':'0.6',
                'line_style':'dash'})
            symbolL.setColor(QColor.fromRgb(255, 127, 0))
            layerTracks.renderer().setSymbol(symbolL)

        layerTracks.updateExtents()
        QgsProject.instance().addMapLayer(layerTracks)

        
