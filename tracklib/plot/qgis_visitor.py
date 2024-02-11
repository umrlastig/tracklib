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

from __future__ import annotations 
from typing import Literal   

import tracklib as tracklib
from tracklib.core import ObsTime, makeCoords, Obs

from tracklib.plot import IPlotVisitor

try:
    from qgis.PyQt.QtCore import QVariant
    from qgis.core import QgsProject, QgsVectorLayer, QgsField
    from qgis.core import QgsPointXY, QgsFeature, QgsGeometry
    from qgis.core import QgsMarkerSymbol, QgsLineSymbol
    from qgis.core import QgsFillSymbol
    from PyQt5.QtGui import QColor
    from qgis.core import QgsCategorizedSymbolRenderer, QgsRendererCategory
    from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform
except ImportError:
    print ('Code running in a no qgis environment')
    
    
class QgisVisitor(IPlotVisitor):
    
    def __init__(self):
        
        self.StyleLigneNoire = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'1.00',
            'color':QColor.fromRgb(0, 0, 0)})
        self.StyleLigneGris = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'1.00',
            'color':QColor.fromRgb(204, 209, 209)})
        self.StyleLigneRouge = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'1.00',
            'color':QColor.fromRgb(255, 0, 0)})
        self.StyleLigneBleue = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'1.00',
            'color':QColor.fromRgb(22, 73, 229)})
        self.StyleLigneVerte = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'1.00',
            'color':QColor.fromRgb(10, 174, 23)})
        self.StyleLigneCyan = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'1.00',
            'color':QColor.fromRgb(10, 222, 236)})
        self.StyleLigneMagenta = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'1.00',
            'color':QColor.fromRgb(180, 32, 90)})
        self.StyleLigneJaune = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'1.00',
            'color':QColor.fromRgb(240, 222, 14)})
        self.StyleLigneOrange = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'1.00',
            'color':QColor.fromRgb(253, 176, 32)})
    
        self.StylePointBleu = QgsMarkerSymbol.createSimple({
            'name': 'square', 
            'color': 'blue', 
            'size':'0.8'})

    
    def plotTrackAsMarkers(
        self, track, size=8, frg="k", bkg="w", sym_frg="+", sym_bkg="o", type=None, 
        append=True
    ):
        
        layerTrackPoint = self.__createPoint(track, "Point")
        layerTrackPoint.renderer().setSymbol(self.StylePointBleu)
        QgsProject.instance().addMapLayer(layerTrackPoint)
        
        
    def plotTrackProfil(
        self, track, template="SPATIAL_SPEED_PROFIL", afs=[], 
                   linestyle = '-', linewidth=1, color='g', append=False):
        pass
        
        
    def plotTrackEllipses(self, track, sym="r-", factor=3, af=None, append=True):
        """
        Plot track uncertainty (as error ellipses)
        Input track must contain an AF with (at least) a
        2 x 2 covariance matrix. If this matrix has dim > 2,
        first two dimensions are arbitrarily considered
        """
        pass
    
    
    def plotTrack(self, track, sym="k-", type="LINE", af_name="", cmap=-1, append=True, 
             size=5, style=None, color=None, w=6.4, h=4.8, title="", xlabel=None, ylabel=None,
             xlim=None, ylim=None):
        """
        Method to plot a track (short cut from Plot)
        Append:
            - True : append to the current plot
            - False: create a new plot
            - Ax   : append to the fiven ax object
        ----------------------------------------------------
        Output:
            Ax object (may be input into append parameter)
    
        af_name: test si isAFTransition
        """
        
        if type == "POINT":
            layerTrackPoint = self.__createPoint(track, track.tid)
            layerTrackPoint.renderer().setSymbol(self.StylePointBleu)
            QgsProject.instance().addMapLayer(layerTrackPoint)
        
        elif type == "LINE":
            layerTrackLine = self.__createLigne(track, "Track")
            
            if sym == "k-":
                symb = self.StyleLigneNoire
            elif sym == "gr-":
                symb = self.StyleLigneGris
            elif sym == "r-":
                symb = self.StyleLigneRouge
            elif sym == "b-":
                symb = self.StyleLigneBleue
            elif sym == "g-":
                symb = self.StyleLigneVerte
            elif sym == "c-":
                symb = self.StyleLigneCyan
            elif sym == "m-":
                symb = self.StyleLigneMagenta
            elif sym == "o-":
                symb = self.StyleLigneOrange
            elif sym == "y-":
                symb = self.StyleLigneJaune
            
            symb.setWidth(1.4)
            layerTrackLine.renderer().setSymbol(symb)
            
            QgsProject.instance().addMapLayer(layerTrackLine)
        
    def plotAnalyticalFeature(self, track, af_name, template="BOXPLOT", append=False):
        """
        Plot AF values by abcisse curvilign.
        """
        pass
    
    def plotFirstObs(self, track, color='r', text='S', dx=0, dy=0, markersize=4, append=False):
        """TODO"""
        pass
    
    def plotLastObs(self, track, ptcolor="r", pttext="E", dx=0, dy=0, markersize=4, append=False):
        """TODO"""
        pass
    
    
    
            


    
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
        
    
    def highlightCellInSpatialIndex(self, si, i, j, sym="r-", size=0.5):
        """
        Plot a specific cell (i,j).
        """
        pass
    

    



    def __createLigne(self, track, titre):
        layerTrackLine = QgsVectorLayer ("LineString?crs=epsg:2154", titre, "memory")
        pr = layerTrackLine.dataProvider()
        pr.addAttributes([QgsField("idtrace", QVariant.String)])
        layerTrackLine.updateFields()
    
        for j in range(1, track.size()):
            obs1 = track.getObs(j-1)
            X1 = float(obs1.position.getX())
            Y1 = float(obs1.position.getY())
                
            obs2 = track.getObs(j)
            X2 = float(obs2.position.getX())
            Y2 = float(obs2.position.getY())
                
            pt1 = QgsPointXY(X1, Y1)
            pt2 = QgsPointXY(X2, Y2)
            gLine = QgsGeometry.fromPolylineXY([pt1, pt2])
                    
            tid = str(track.tid)
            attrs = [tid, j]
                
            fet = QgsFeature()
            fet.setAttributes(attrs)
            fet.setGeometry(gLine)
            pr.addFeatures([fet])
            
        layerTrackLine.updateExtents()
        layerTrackLine.commitChanges()
            
        return layerTrackLine


    def __createPoint(self, track, titre):
        layerTrackPoint = QgsVectorLayer ("Point?crs=epsg:2154", titre, "memory")
        pr = layerTrackPoint.dataProvider()
        pr.addAttributes([QgsField("idtrace", QVariant.Int)])
        pr.addAttributes([QgsField("idpoint", QVariant.Int)])
        layerTrackPoint.updateFields()
    
        for j in range(track.size()):
            obs = track.getObs(j)
            X = float(obs.position.getX())
            Y = float(obs.position.getY())
            pt = QgsPointXY(X, Y)
            gPoint = QgsGeometry.fromPointXY(pt)
                    
            tid = str(track.tid)
            attrs = [tid, j]
                
            fet = QgsFeature()
            fet.setAttributes(attrs)
            fet.setGeometry(gPoint)
            pr.addFeatures([fet])
            
        layerTrackPoint.updateExtents()
        layerTrackPoint.commitChanges()
        
        return layerTrackPoint


class QgisUtil:
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
            
