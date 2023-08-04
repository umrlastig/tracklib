# -*- coding: utf-8 -*-

from __future__ import annotations 
from typing import Literal   

import tracklib as tracklib
from tracklib.core import ObsTime, makeCoords, Obs


try:
    # import os # This is is needed in the pyqgis console also
    from qgis.PyQt.QtCore import QVariant
    from qgis.PyQt.QtGui import QColor
    from qgis.core import QgsProject, QgsVectorLayer, QgsField
    from qgis.core import QgsPointXY, QgsFeature, QgsGeometry
    from qgis.core import QgsMarkerSymbol, QgsLineSymbol
    from qgis.core import QgsCategorizedSymbolRenderer, QgsRendererCategory
    from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform
except ImportError:
    print ('no qgis')


class Qgis:
    '''
    Class to visualize GPS tracks and its AF in Qgis.
    '''
    
    vertFonce = '51,160,44'   # vertex
    #vertClair = '#b2df8a'
    orange = '255,127,0'
    jaune = '246,240,44'
    bleu = '68,174,240'       # bend
    rose = '237,55,234'       # switchbacks : 0
    turquoise = '54,202,202'  # switchbacks : 1
    
    @staticmethod
    def getStylePoint(renderer, color = '0,0,0', size = '0.8'):
        symbol = QgsMarkerSymbol.createSimple({
                 'name': 'circle', 
                 'color': color, 
                 'size': size, 
                 'outline_color': '0,0,0'})
        renderer.setSymbol(symbol)
        
    
    @staticmethod
    def getStylePointAF(af, colors, values = [1]):
        categories = []
            
        for k in range(len(values)):
            symbolEdge = QgsMarkerSymbol.createSimple({'name': 'square', 
                                                   'color': colors[k], 
                                                   'size': '0.8', 
                                                   'outline_color': colors[k],
                                                   'color_border': colors[k]})
            #symbolEdge.setColor(QColor.fromRgb(31, 120, 180))
            symbolEdge.setSize(1.8)
            categoryEdge = QgsRendererCategory(values[k], symbolEdge, str(values[k]))
            categories.append(categoryEdge)
            
        # On construit une expression pour appliquer les categories
        expression = af # field name
        renderer = QgsCategorizedSymbolRenderer(expression, categories)
        
        return renderer
        
    
    @staticmethod
    def getStyleLigne(renderer):
        symbolL = QgsLineSymbol.createSimple({
            'penstyle':'solid', 
            'width':'0.6',
            'line_style':'dash'})
        symbolL.setColor(QColor.fromRgb(255, 127, 0))
        renderer.setSymbol(symbolL)
        
    
    @staticmethod
    def getStyleLigneAF(af, colors, values = [0,1]):
        '''
        virage: getStyleLigneAF('bend', [bleu], [0])
        lacet: getStyleLigneAF('switchbacks', [rose,turquoise], [0,1])
        '''
        
        categories = []
        
        for k in range(len(values)):
            symbolL = QgsLineSymbol.createSimple({
                'penstyle':'solid', 
                'width':'0.6',
                'color': colors[k],  # '255,127,0'
                'line_style':'dash'})
            categoryEdge = QgsRendererCategory(values[k], symbolL, str(values[k]))
            categories.append(categoryEdge)
        
        expression = af # field name
        renderer = QgsCategorizedSymbolRenderer(expression, categories)
        
        return renderer
    
    """
    Write GPS tracks in Qgis.
    """
    @staticmethod
    def createTracksLayer(tracks, type: Literal["LINE", "POINT"] = "LINE", 
                               af=False, layerName = "Tracks",
                               crs="epsg:2154"):
        """
        Transforms track into a Qgis Layer.
        :param type: "POINT" or "LINE"
        :param af: AF exported in qgis layer like attributes
        """
        
        if isinstance(tracks, tracklib.Track):
            collection = tracklib.TrackCollection()
            collection.addTrack(tracks)
            tracks = collection
        
        if type == 'POINT':
            layerTracks = QgsVectorLayer("Point?crs=" + crs, layerName, "memory")
        if type == 'LINE':
            layerTracks = QgsVectorLayer("LineString?crs=" + crs, layerName, "memory")

            
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
                
                tid = int(track.tid)
                if tid > 0:
                    attrs = [tid, j]
                else:
                    attrs = [i, j]
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
                
        layerTracks.updateExtents()
        
        return layerTracks
    
    
    @staticmethod
    def buildLinearTracksLayer(tracks, layerName = "Linear Tracks", crs="epsg:2154"):
        """
        Parameters
        ----------
        tracks : TYPE
            DESCRIPTION.
        layerName : TYPE, optional
            DESCRIPTION. The default is "Linear Tracks".
        crs : TYPE, optional
            DESCRIPTION. The default is "epsg:2154".

        Returns
        -------
        None.

        """
        
        if isinstance(tracks, tracklib.Track):
            collection = tracklib.TrackCollection()
            collection.addTrack(tracks)
            tracks = collection
        
        layerTracks = QgsVectorLayer("LineString?crs=" + crs, layerName, "memory")
            
        pr = layerTracks.dataProvider()
        pr.addAttributes([QgsField("idtrace", QVariant.Int)])
        
        layerTracks.updateFields()

        for i in range(tracks.size()):
            track = tracks.getTrack(i)
            tid = track.tid
            
            tid = int(track.tid)
            if tid > 0:
                attrs = [tid]
            else:
                attrs = [i]
            
            points = []
            for j in range(track.size()):
                obs = track.getObs(j)
                X = float(obs.position.getX())
                Y = float(obs.position.getY())
                pt = QgsPointXY(X, Y)
                points.append(pt)
                
            fet = QgsFeature()
            fet.setAttributes(attrs) 
            fet.setGeometry(QgsGeometry.fromPolylineXY(points))
            pr.addFeatures([fet])
                
        layerTracks.updateExtents()
        
        return layerTracks
        

        
    """
    Write GPS tracks in Qgis.
    """
    @staticmethod
    def removeAllLayers():
        QgsProject.instance().removeAllMapLayers()



    @staticmethod
    def transformTrack(tracks, source=4326, target=2154):
        """
          Convert coordinates from one projection system to another.
        """
        
        crsSrc = QgsCoordinateReferenceSystem(source)    
        crsDest = QgsCoordinateReferenceSystem(target)
        xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
        
        for i in range(tracks.size()):
            track = tracks.getTrack(i)
            for j in range(track.size()):
                obs = track.getObs(j)
                X = float(obs.position.getX())
                Y = float(obs.position.getY())
                pt = QgsPointXY(X, Y)
                geom = QgsGeometry.fromPointXY(pt)
                geom.transform(xform)
                
                time = ObsTime()
                obs = Obs(makeCoords(geom.asPoint().x(), geom.asPoint().y(), 0, "ENUCoords"), time)
                track.setObs(j, obs)
            
        
        

        
    

