# -*- coding: utf-8 -*-

from tracklib import Track, TrackCollection

try:
    from qgis.PyQt.QtCore import QVariant
    from qgis.core import QgsProject, QgsVectorLayer, QgsField
    from qgis.core import QgsPointXY, QgsFeature, QgsGeometry
    from qgis.core import QgsMarkerSymbol, QgsLineSymbol, QgsSimpleLineSymbolLayer
    #from qgis.core import QgsFillSymbol
    from PyQt5.QtGui import QColor
    #from qgis.core import QgsCategorizedSymbolRenderer, QgsRendererCategory
    #from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform
except ImportError:
    print ('Code running in a no qgis environment')
    
    
class LineStyle:
    @staticmethod
    def simpleBlue(layerLine):
        symbolL1 = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'0.6',
            'color':'blue'})
        layerLine.renderer().setSymbol(symbolL1)
        
    @staticmethod
    def topoRoad(layerLine):
        symbolL1 = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'1.06',
            'color':'black'})
        symbol_l2 = QgsSimpleLineSymbolLayer.create ({
            'color':'white',
            'width':'0.8',
            'line_style':'solid'})
        symbolL1.appendSymbolLayer(symbol_l2)
        layerLine.renderer().setSymbol(symbolL1)
        
    @staticmethod
    def simpleLightGreen(layerLine):
        symbolL1 = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'0.6',
            'color': QColor.fromRgb(190, 207, 80)})
        layerLine.renderer().setSymbol(symbolL1)
        



class PointStyle:
    @staticmethod
    def simpleBlack(layerPoint):
        symbol = QgsMarkerSymbol.createSimple({
            'color': 'black', 
            'size':'1.4'})
        layerPoint.renderer().setSymbol(symbol)
        
    @staticmethod
    def simpleSquareBlue(layerPoint):
        symbol = QgsMarkerSymbol.createSimple({
            'name': 'square', 
            'color': 'blue', 
            'size':'1.4'})
        layerPoint.renderer().setSymbol(symbol)
    
    @staticmethod
    def simpleLightGreen(layerPoint):
        symbol = QgsMarkerSymbol.createSimple({
            'name': 'square', 
            'color': QColor.fromRgb(190, 207, 80), 
            'size':'1.4'})
        layerPoint.renderer().setSymbol(symbol)


class QGIS:
    '''
    To plot track and network in QGIS.
    '''
    
    @staticmethod
    def plotNetwork(network, edgeStyle='topoRoad'):
           # direct: str = "k--", indirect: str = "k--"):
        """
        Plot a network, edges and nodes
        """

        if network.getSRID() == 'Geo':
            crs = 'crs=EPSG:4326'
        else:
            crs = 'crs=EPSG:2154'
            
        layerEdges = QgsVectorLayer("LineString?" + crs, "Edges", "memory")
        pr1 = layerEdges.dataProvider()
        pr1.addAttributes([QgsField("idedge", QVariant.String)])
        pr1.addAttributes([QgsField("source", QVariant.Int)])
        pr1.addAttributes([QgsField("target", QVariant.Int)])
        pr1.addAttributes([QgsField("orientation", QVariant.Int)])
        pr1.addAttributes([QgsField("weight", QVariant.Double)])
        layerEdges.updateFields()
        
        layerNodes = QgsVectorLayer("Point?" + crs, "Nodes", "memory")
        pr2 = layerNodes.dataProvider()
        pr2.addAttributes([QgsField("idnode", QVariant.String)])
        layerNodes.updateFields()

        L = list(network.EDGES.items())
        for i in range(len(L)):
            edge = L[i][1]
            POINTS = []
            for j in range(edge.geom.size()):
                pt = QgsPointXY(edge.geom.getX()[j], edge.geom.getY()[j])
                POINTS.append(pt)
            fet = QgsFeature()
            fet.setAttributes([str(edge.id), int(edge.source.id), int(edge.target.id),
                                   edge.orientation, edge.weight])
            fet.setGeometry(QgsGeometry.fromPolylineXY(POINTS))
            pr1.addFeatures([fet])
        layerEdges.updateExtents()
        LineStyle.topoRoad(layerEdges)
        
        L = list(network.NODES.items())
        for i in range(len(L)):
            node = L[i][1]
            pt = QgsPointXY(node.coord.getX(), node.coord.getY())
            fet = QgsFeature()
            fet.setAttributes([str(node.id)])
            fet.setGeometry(QgsGeometry.fromPointXY(pt))
            pr2.addFeatures([fet])
        layerNodes.updateExtents()
        PointStyle.simpleBlack(layerNodes)
        
        QgsProject.instance().addMapLayer(layerEdges)
        QgsProject.instance().addMapLayer(layerNodes)


    @staticmethod
    def plotTracks(collection, type="LINE", AF=False, style=None):
        '''
        Plot a track or a collection of tracks.
        
        :param collection: may be a Track or a TrackCollection
        :param type: 'LINE' or 'POINT'
        :param AF: if True, add all analytical features as fields
        '''
        
        if isinstance(collection, Track):
            c = TrackCollection()
            c.addTrack(collection)
            collection = c
            
        if collection.getSRID() == 'Geo':
            crs = 'crs=EPSG:4326'
        else:
            crs = 'crs=EPSG:2154'
            
        FEATURES = QGIS.__createTablePoints(collection, type)
        
        if type == 'POINT':
            layer = QgsVectorLayer("Point?" + crs, "Tracks points", "memory")
            pr = layer.dataProvider()
            pr.addAttributes([QgsField("idtrace", QVariant.Int)])
            pr.addAttributes([QgsField("idpoint", QVariant.Int)])
            #if AF:
            #    for af_name in collection.getTrack(0).getListAnalyticalFeatures():
            #        pr.addAttributes([QgsField(af_name, QVariant.Double)])
            layer.updateFields()
            for f in FEATURES:
                pr.addFeatures([f])
            layer.updateExtents()
            
            if style == None:
                PointStyle.simpleLightGreen(layer)
            else:
                style(layer)
            
            QgsProject.instance().addMapLayer(layer)
        
        elif type == 'LINE':
            layer = QgsVectorLayer("LineString?" + crs, "Tracks", "memory")
            pr = layer.dataProvider()
            pr.addAttributes([QgsField("idtrace", QVariant.Int)])
            pr.addAttributes([QgsField("nbpoint", QVariant.Int)])
            layer.updateFields()
            for f in FEATURES:
                pr.addFeatures([f])
            layer.updateExtents()
            
            if style == None:
                LineStyle.simpleLightGreen(layer)
            else:
                style(layer)
                
            QgsProject.instance().addMapLayer(layer)

    def __createTablePoints(collection, type):
        FEATURES = []
        for i in range(collection.size()):
            track = collection.getTrack(i)
            tid = int(track.tid)
            if tid > 0:
                id = tid
            else:
                id = i
            POINTS = []
            for j in range(track.size()):
                obs = track.getObs(j)
                X = float(obs.position.getX())
                Y = float(obs.position.getY())
                pt = QgsPointXY(X, Y)
                POINTS.append(pt)
                gPoint = QgsGeometry.fromPointXY(pt)
                
                attrs = [id, j]
                # AF
                #if AF:
                #    for af_name in track.getListAnalyticalFeatures():
                #        attrs.append(track.getObsAnalyticalFeature(af_name, j))
                        
                if type == 'POINT':                
                    fet = QgsFeature()
                    fet.setAttributes(attrs)
                    fet.setGeometry(gPoint)
                    FEATURES.append(fet)
                    
            if type == 'LINE':
                fet = QgsFeature()
                fet.setAttributes([id, track.size()]) 
                fet.setGeometry(QgsGeometry.fromPolylineXY(POINTS))
                FEATURES.append(fet)
                
        return FEATURES
    
    
    def plotMMLink(self, track):
        """
        Plot the map matched track on network links.
        """
        layerLinkMM = QgsVectorLayer("LineString?crs=2154", "Link MM", "memory")
        pr = layerLinkMM.dataProvider()
        layerLinkMM.updateFields()
        for k in range(len(track)):
            pt1 = QgsPointXY(track[k].position.getX(), track[k].position.getY())
            pt2 = QgsPointXY(track["hmm_inference", k][0].getX(), track["hmm_inference", k][0].getY())
            fet = QgsFeature()
            #fet.setAttributes(attrs)
            fet.setGeometry(QgsGeometry.fromPolylineXY([pt1, pt2]))
            pr.addFeatures([fet])
        layerLinkMM.updateExtents()
        QgsProject.instance().addMapLayer(layerLinkMM)
        
        
        