# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt

import tracklib.core.Network as network
import tracklib.core.SpatialIndex as index
import tracklib.plot.IPlotVisitor as iplot
import tracklib.plot.Plot as Plot

from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsProject, QgsVectorLayer, QgsField
from qgis.core import QgsPointXY, QgsFeature, QgsGeometry
from qgis.core import QgsMarkerSymbol, QgsLineSymbol, QgsSimpleLineSymbolLayer
from qgis.core import QgsFillSymbol


class QgisVisitor(iplot.IPlotVisitor):
    
    
    def plotTrackAsMarkers(
        self, track, size=8, frg="k", bkg="w", sym_frg="+", sym_bkg="o", type=None, 
        append=True
    ):
        
        layerTrack = QgsVectorLayer ("Point?crs=epsg:2154", "MM", "memory")
        pr = layerTrack.dataProvider()
        pr.addAttributes([QgsField("idtrace", QVariant.Int)])
        pr.addAttributes([QgsField("idpoint", QVariant.Int)])
        layerTrack.updateFields()

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
                attrs = [1, j]
            
            fet = QgsFeature()
            fet.setAttributes(attrs)
            fet.setGeometry(gPoint)
            pr.addFeatures([fet])
        
        layerTrack.updateExtents()
        layerTrack.commitChanges()
        symbol = QgsMarkerSymbol.createSimple({'name': 'square', 'color': 'blue', 'size':'0.8'})
        layerTrack.renderer().setSymbol(symbol)
        QgsProject.instance().addMapLayer(layerTrack)
        
        
    def plotTrackEllipses(self, track, sym="r-", factor=3, af=None, append=True):
        """
        Plot track uncertainty (as error ellipses)
        Input track must contain an AF with (at least) a
        2 x 2 covariance matrix. If this matrix has dim > 2,
        first two dimensions are arbitrarily considered
        """
        pass
    
    
    def plotTrack(self, track, sym="k-", type="LINE", af_name="", cmap=-1, append=True, 
             label=None, pointsize=5):
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
        pass
    
    
    def plotSpatialIndex(self, si: index.SpatialIndex, base:bool=True, append=True):
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
    

    def plotNetwork(self, net, edges: str = "k-", nodes: str = "",
        direct: str = "k--", indirect: str = "k--", size: float = 0.5, append=plt):
        """
        Plot network
        """
        layerNetwork = QgsVectorLayer("LineString?crs=2154", "Network", "memory")
        pr = layerNetwork.dataProvider()
        layerNetwork.updateFields()

        L = list(net.EDGES.items())
        for i in range(len(L)):
            edge = L[i][1]
            for j in range(edge.geom.size() - 1):
                pt1 = QgsPointXY(edge.geom.getX()[j], edge.geom.getY()[j])
                pt2 = QgsPointXY(edge.geom.getX()[j + 1], edge.geom.getY()[j + 1])
                fet = QgsFeature()
                #fet.setAttributes(attrs)
                fet.setGeometry(QgsGeometry.fromPolylineXY([pt1, pt2]))
                pr.addFeatures([fet])
        
        layerNetwork.updateExtents()
        QgsProject.instance().addMapLayer(layerNetwork)
        
        symbolL1 = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'0.8',
            'color':'blue'})
        layerNetwork.renderer().setSymbol(symbolL1)
        
        symbolL1 = QgsLineSymbol.createSimple({
            'penstyle':'solid',
            'width':'1.06',
            'color':'black'})
        layerNetwork.renderer().setSymbol(symbolL1)
        symbol_l2 = QgsSimpleLineSymbolLayer.create ({
            'color':'white',
            'width':'0.8',
            'line_style':'solid'})
        symbolL1.appendSymbolLayer(symbol_l2)
    