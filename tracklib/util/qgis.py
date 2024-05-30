# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Marie-Dominique Van Damme
Creation date: 1th november 2020

tracklib library provides a variety of tools, operators and 
functions to manipulate GPS trajectories. It is a open source contribution 
of the LASTIG laboratory at the Institut National de l'Information 
Géographique et Forestière (the French National Mapping Agency).
See: https://tracklib.readthedocs.io
 
This software is governed by the CeCILL-C license under French law and
abiding by the rules of distribution of free software. You can  use, 
modify and/ or redistribute the software under the terms of the CeCILL-C
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info". 

As a counterpart to the access to the source code and rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability. 

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or 
data to be ensured and,  more generally, to use and operate it in the 
same conditions as regards security. 

The fact that you are presently reading this means that you have had
knowledge of the CeCILL-C license and that you accept its terms.
"""

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
    
    
#vertFonce = '51,160,44'   # vertex
#orange = '255,127,0'
#jaune = '246,240,44'
#bleu = '68,174,240'       # bend
#rose = '237,55,234'       # switchbacks : 0
#turquoise = '54,202,202'  # switchbacks : 1
    
# bleu QColor.fromRgb(22, 73, 229)
# vert QColor.fromRgb(10, 174, 23)
# cyan QColor.fromRgb(10, 222, 236)
# magenat QColor.fromRgb(180, 32, 90)
# jaune QColor.fromRgb(240, 222, 14)
# orange QColor.fromRgb(253, 176, 32)
    
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
        

    @staticmethod
    def simpleLightOrange(layerLine):
        symbolL1 = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'0.6',
            'color': QColor.fromRgb(253, 176, 32)})
        layerLine.renderer().setSymbol(symbolL1)

    @staticmethod
    def simpleLightCyan(layerLine):
        symbolL1 = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'0.6',
            'color': QColor.fromRgb(10, 222, 236)})
        layerLine.renderer().setSymbol(symbolL1)

    @staticmethod
    def simpleLightVertFonce(layerLine):
        symbolL1 = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'0.6',
            'color': QColor.fromRgb(51, 160, 44)})
        layerLine.renderer().setSymbol(symbolL1)


class PointStyle:
    @staticmethod
    def simpleBlack(layerPoint):
        symbol = QgsMarkerSymbol.createSimple({
            'name': 'circle',
            'color': 'black', 
            # 'outline_color': '0,0,0'
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
    def plotTracks(collection, type="LINE", AF=False, style=None,
                   title=None):
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
            
        if title is None and type == 'LINE':
            title = "Tracks"
        elif title is None and type == 'POINT':
            title = "Tracks points"
            
        FEATURES = QGIS.__createTablePoints(collection, type)
        
        if type == 'POINT':
            layer = QgsVectorLayer("Point?" + crs, title, "memory")
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
            layer = QgsVectorLayer("LineString?" + crs, title, "memory")
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
            #tid = int(track.tid)
            #if tid > 0:
            #    id = tid
            #else:
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
    
    
    def plotMMLink(track):
        """
        Plot the map matched track on network links.
        """
        layerLinkMM = QgsVectorLayer("LineString?crs=2154", "Link MM", "memory")
        pr = layerLinkMM.dataProvider()
        layerLinkMM.updateFields()
        for k in range(track.size()):
            pt1 = QgsPointXY(track[k].position.getX(), track[k].position.getY())
            pt2 = QgsPointXY(track["hmm_inference", k][0].getX(), track["hmm_inference", k][0].getY())
            fet = QgsFeature()
            #fet.setAttributes(attrs)
            fet.setGeometry(QgsGeometry.fromPolylineXY([pt1, pt2]))
            pr.addFeatures([fet])
        layerLinkMM.updateExtents()
        QgsProject.instance().addMapLayer(layerLinkMM)
        

'''
    # SpatialIndex
    def plotSpatialIndex(self, si, base:bool=True, append=True):
        """
        Plot spatial index and collection structure together in the
        same reference frame (geographic reference frame)
            - base: plot support network or track collection if True
        """
        
        layerGrid = QgsVectorLayer("LineString?crs=2154", "Grid", "memory")
        pr = layerGrid.dataProvider()
        layerGrid.updateFields()
        
        layerIndex = QgsVectorLayer("Polygon?crs=2154", "Index", "memory")
        pr2 = layerIndex.dataProvider()
        layerIndex.updateFields()
            
        for i in range(0, si.csize):
            xi = i * si.dX + si.xmin
            # ax1.plot([xi, xi], [si.ymin, si.ymax], "-", color="gray")
            
            pt1 = QgsPointXY(xi, si.ymin)
            pt2 = QgsPointXY(xi, si.ymax)
            fet = QgsFeature()
            #fet.setAttributes(attrs)
            fet.setGeometry(QgsGeometry.fromPolylineXY([pt1, pt2]))
            pr.addFeatures([fet])
        
        for j in range(0, si.lsize):
            yj = j * si.dY + si.ymin
            pt1 = QgsPointXY(si.xmin, yj)
            pt2 = QgsPointXY(si.xmax, yj)
            fet = QgsFeature()
            #fet.setAttributes(attrs)
            fet.setGeometry(QgsGeometry.fromPolylineXY([pt1, pt2]))
            pr.addFeatures([fet])


        for i in range(si.csize):
            xi1 = i * si.dX + si.xmin
            xi2 = xi1 + si.dX
            for j in range(si.lsize):
                yj1 = j * si.dY + si.ymin
                yj2 = yj1 + si.dY
                if len(si.grid[i][j]) > 0:
                    
                    p = QgsGeometry.fromPolygonXY( [[
                            QgsPointXY( xi1, yj1 ),
                            QgsPointXY( xi2, yj1 ),
                            QgsPointXY( xi2, yj2 ),
                            QgsPointXY( xi1, yj2 ),
                            QgsPointXY( xi1, yj1 ) ]] )
                    fet = QgsFeature()
                    #fet.setAttributes(attrs)
                    fet.setGeometry(p)
                    pr2.addFeatures([fet])
                    
        layerGrid.updateExtents()
        QgsProject.instance().addMapLayer(layerGrid)
        
        symbolL1 = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'0.8',
            'color':'gray'})
        layerGrid.renderer().setSymbol(symbolL1)
        
        layerIndex.updateExtents()
        QgsProject.instance().addMapLayer(layerIndex)
        
        props3 = {'color': '180,180,180', 'size':'1', 'color_border' : '180,180,180'}
        symbol3 = QgsFillSymbol.createSimple(props3)
        layerIndex.renderer().setSymbol(symbol3)
'''
    
    
        
'''
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
    def getStyleLigneAF(af, colors, values = [0,1]):
        
        # virage: getStyleLigneAF('bend', [bleu], [0])
        # lacet: getStyleLigneAF('switchbacks', [rose,turquoise], [0,1])
        
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
    
 '''   
 
COLORS_PALETTE = {
 'dimgray': '#696969', 'gray': '#808080', 'darkgray': '#a9a9a9', 'silver': '#c0c0c0',
'gainsboro': '#dcdcdc', 'darkslategray': '#2f4f4f', 'darkolivegreen': '#556b2f',
'saddlebrown': '#8b4513', 'olivedrab': '#6b8e23', 'sienna': '#a0522d',
'brown': '#a52a2a', 'seagreen': '#2e8b57', 'midnightblue': '#191970',
'darkgreen': '#006400', 'slategray': '#708090', 'darkred': '#8b0000',
'olive': '#808000', 'darkslateblue': '#483d8b', 'firebrick': '#b22222',
'cadetblue': '#5f9ea0', 'green': '#008000', 'mediumseagreen': '#3cb371',
'rosybrown': '#bc8f8f', 'rebeccapurple': '#663399', 'darkgoldenrod': '#b8860b',
'darkkhaki': '#bdb76b', 'darkcyan': '#008b8b', 'peru': '#cd853f',
'steelblue': '#4682b4', 'chocolate': '#d2691e', 'yellowgreen': '#9acd32',
'lightseagreen': '#20b2aa', 'indianred': '#cd5c5c', 'darkblue': '#00008b',
'indigo': '#4b0082', 'limegreen': '#32cd32', 'goldenrod': '#daa520',
'purple2': '#7f007f', 'darkseagreen': '#8fbc8f', 'maroon3': '#b03060',
'mediumaquamarine': '#66cdaa', 'darkorchid': '#9932cc', 'red': '#ff0000',
'orangered': '#ff4500', 'darkturquoise': '#00ced1', 'darkorange': '#ff8c00',
'orange': '#ffa500', 'gold': '#ffd700', 'slateblue': '#6a5acd',
'yellow': '#ffff00', 'mediumvioletred': '#c71585', 'mediumblue': '#0000cd',
'lawngreen': '#7cfc00', 'burlywood': '#deb887', 'turquoise': '#40e0d0',
'lime': '#00ff00', 'darkviolet': '#9400d3', 'mediumorchid': '#ba55d3',
'mediumspringgreen': '#00fa9a', 'blueviolet': '#8a2be2', 'springgreen': '#00ff7f',
'royalblue': '#4169e1', 'darksalmon': '#e9967a', 'crimson': '#dc143c',
'aqua': '#00ffff', 'deepskyblue': '#00bfff', 'sandybrown': '#f4a460',
'mediumpurple': '#9370db', 'blue': '#0000ff', 'purple3': '#a020f0',
'lightcoral': '#f08080', 'greenyellow':'#adff2f', 'tomato': '#ff6347',
'orchid': '#da70d6', 'thistle': '#d8bfd8', 'lightsteelblue': '#b0c4de',
'coral': '#ff7f50', 'fuchsia': '#ff00ff', 'dodgerblue': '#1e90ff',
'palevioletred': '#db7093', 'khaki': '#f0e68c', 'salmon': '#fa8072',
'palegoldenrod': '#eee8aa', 'laserlemon': '#ffff54', 'cornflower': '#6495ed',
'plum': '#dda0dd', 'lightgreen': '#90ee90', 'lightblue': '#add8e6',
'skyblue': '#87ceeb', 'deeppink': '#ff1493', 'mediumslateblue': '#7b68ee',
'lightsalmon': '#ffa07a', 'paleturquoise': '#afeeee', 'violet': '#ee82ee',
'lightskyblue': '#87cefa', 'aquamarine': '#7fffd4', 'moccasin': '#ffe4b5',
'peachpuff': '#ffdab9', 'hotpink': '#ff69b4', 'pink': '#ffc0cb'}

