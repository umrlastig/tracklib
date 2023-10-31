# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Yann Méneroux
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

import matplotlib.pyplot as plt

import tracklib as tracklib
from tracklib.plot import (Plot, 
                           IPlotVisitor,
                           MARKERS_TYPE_NO_ENTRY,
                           MARKERS_TYPE_INTERDICTION,
                           MARKERS_TYPE_SPOT,
                           MARKERS_TYPE_WARNING,
                           MARKERS_TYPE_GIVE_WAY,
                           MARKERS_TYPE_NO_STOP,
                           MARKERS_TYPE_INFORMATION)




class MatplotlibVisitor(IPlotVisitor):
    
    def plotTrackAsMarkers(
        self, track, size=8, frg="k", bkg="w", sym_frg="+", sym_bkg="o", type=None, 
        append=True
    ):
        """TODO"""
        
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(10, 3))
        else:
            ax1 = plt
        
        if not type is None:
            if type == MARKERS_TYPE_NO_ENTRY:
                frg = "w"
                bkg = "r"
                sym_frg = "_"
                sym_bkg = "o"
            if type == MARKERS_TYPE_INTERDICTION:
                frg = "w"
                bkg = "r"
                sym_frg = "."
                sym_bkg = "o"
            if type == MARKERS_TYPE_SPOT:
                frg = "r"
                bkg = "w"
                sym_frg = "."
                sym_bkg = "o"
            if type == MARKERS_TYPE_WARNING:
                frg = "r"
                bkg = "w"
                sym_frg = " "
                sym_bkg = "^"
            if type == MARKERS_TYPE_GIVE_WAY:
                frg = "r"
                bkg = "w"
                sym_frg = " "
                sym_bkg = "v"
            if type == MARKERS_TYPE_NO_STOP:
                frg = "r"
                bkg = "b"
                sym_frg = "x"
                sym_bkg = "o"
            if type == MARKERS_TYPE_INFORMATION:
                frg = "b"
                bkg = "w"
                sym_frg = " "
                sym_bkg = "s"

        ax1.plot(track.getX(), track.getY(), frg + sym_bkg, markersize=size)
        ax1.plot(track.getX(), track.getY(), bkg + sym_bkg, markersize=int(0.8 * size))
        ax1.plot(track.getX(), track.getY(), frg + sym_frg, markersize=int(0.8 * size))
        #for i in range(track.size()):
        #    val = track.getObsAnalyticalFeature('Temp', i)
        #    plt.text(track.getX()[i]+0.1, track.getY()[i]+0.1, str(val))
        return ax1
    
    def plotTrackProfil(
        self, track, template="SPATIAL_SPEED_PROFIL", afs=[], append=False,
                   linestyle = '-', linewidth=1):
        """
        Plot a profil track.
        """
        plot = Plot(track)
        return plot.plotProfil(template, afs, append, linestyle, linewidth)
    
    def plotTrackEllipses(self, track, sym="r-", factor=3, af=None, append=True):
        """
        Plot track uncertainty (as error ellipses)
        Input track must contain an AF with (at least) a
        2 x 2 covariance matrix. If this matrix has dim > 2,
        first two dimensions are arbitrarily considered
        """
        plot = Plot(track)
        plot.sym = sym
        plot.w = 6
        plot.h = 5
        return plot.plotEllipses(track, sym, factor, af, append)
    
    def plotTrack(self, track, sym="k-", type="LINE", af_name="", cmap=-1, append=True, 
             label=None, size=5, w=6.4, h=4.8, title="", xlabel=None, ylabel=None,
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
        plot = Plot(track)
        plot.sym = sym
        if not '-' in sym and type != 'CIRCULAR':
            type = "POINT"
            plot.pointsize = 20
        plot.pointsize = size
        plot.color = sym[0]
        plot.marker = sym[1]
        plot.w = w
        plot.h = h
        return plot.plot(type, af_name, cmap, append=append, label=label, 
                         title=title, xlabel=xlabel, ylabel=ylabel, xlim=xlim, 
                         ylim=ylim)
    
    def plotMMLink(self, track):
        """
        Plot the map matched track on network links.
        """
        pass
    
    # SpatialIndex
    def plotSpatialIndex(self, si, base:bool=True, append=True):
        """
        Plot spatial index and collection structure together in the
        same reference frame (geographic reference frame)
            - base: plot support network or track collection if True
        """
        
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(10, 3))
        else:
            ax1 = plt
            
        #fig = plt.figure()
        #ax = fig.add_subplot(
        #    111, xlim=(si.xmin, si.xmax), ylim=(si.ymin, si.ymax)
        #)

        for i in range(0, si.csize):
            xi = i * si.dX + si.xmin
            ax1.plot([xi, xi], [si.ymin, si.ymax], "-", color="gray")
        
        for j in range(0, si.lsize):
            yj = j * si.dY + si.ymin
            ax1.plot([si.xmin, si.xmax], [yj, yj], "-", color="gray")


        if base:
            si.collection.plot(append=ax1)

        for i in range(si.csize):
            xi1 = i * si.dX + si.xmin
            xi2 = xi1 + si.dX
            for j in range(si.lsize):
                yj1 = j * si.dY + si.ymin
                yj2 = yj1 + si.dY
                if len(si.grid[i][j]) > 0:
                    polygon = plt.Polygon(
                        [[xi1, yj1], [xi2, yj1], [xi2, yj2], [xi1, yj2], [xi1, yj1]]
                    )
                    ax1.add_patch(polygon)
                    polygon.set_facecolor("lightcyan")
                    
                    
    def plotFirstObs(self, track, ptcolor="r", pttext="S", dx=0, dy=0, markersize=4, 
                     append=False):
        """TODO"""
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(10, 3))
        else:
            ax1 = plt
            
        pt = track.getFirstObs().position
        ax1.plot(pt.getX(), pt.getY(), ptcolor+'o', markersize=markersize)
        ax1.text(pt.getX() + dx, pt.getY() + dy, pttext)
        
    
    def plotLastObs(self, track, ptcolor="r", pttext="E", dx=0, dy=0, markersize=4, 
                     append=False):
        """TODO"""
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(10, 3))
        else:
            ax1 = plt
            
        pt = track.getLastObs().position
        ax1.plot(pt.getX(), pt.getY(), ptcolor+'o', markersize=markersize)
        ax1.text(pt.getX() + dx, pt.getY() + dy, pttext)
                    
    
    def highlightCellInSpatialIndex(self, si, i, j, sym="r-", size=0.5):
        """
        Plot a specific cell (i,j).
        """
        x0 = si.xmin + i * si.dX
        x1 = x0 + si.dX
        y0 = si.ymin + j * si.dY
        y1 = y0 + si.dY
        X = [x0, x1, x1, x0, x0]
        Y = [y0, y0, y1, y1, y0]
        plt.plot(X, Y, sym, linewidth=size)
        


    def plotNetwork(self, net, edges: str = "k-", nodes: str = "",
        direct: str = "k--", indirect: str = "k--", size: float = 0.5, append=plt):
        """
        Plot network
        """
        
        """Plot the network

        :param edges: TODO
        :param nodes: TODO
        :param direct: TODO
        :param indirect: TODO
        :param size: TODO
        :param append: TODO
        """

        x1b = []
        y1b = []
        x1i = []
        y1i = []
        x1d = []
        y1d = []
        x2b = []
        y2b = []
        x2i = []
        y2i = []
        x2d = []
        y2d = []
        exb = []
        eyb = []
        exi = []
        eyi = []
        exd = []
        eyd = []
        nx = []
        ny = []
        
        L = list(net.EDGES.items())
        for i in range(len(L)):
            edge = L[i][1]
            for j in range(edge.geom.size() - 1):
                if edge.orientation == tracklib.Edge.DOUBLE_SENS:
                    x1b.append(edge.geom.getX()[j])
                    x2b.append(edge.geom.getX()[j + 1])
                    y1b.append(edge.geom.getY()[j])
                    y2b.append(edge.geom.getY()[j + 1])
                else:
                    if edge.orientation == tracklib.Edge.SENS_DIRECT:
                        x1d.append(edge.geom.getX()[j])
                        x2d.append(edge.geom.getX()[j + 1])
                        y1d.append(edge.geom.getY()[j])
                        y2d.append(edge.geom.getY()[j + 1])
                    else:
                        x1i.append(edge.geom.getX()[j])
                        x2i.append(edge.geom.getX()[j + 1])
                        y1i.append(edge.geom.getY()[j])
                        y2i.append(edge.geom.getY()[j + 1])
            nx.append(edge.geom.getX()[0])
            nx.append(edge.geom.getX()[-1])
            ny.append(edge.geom.getY()[0])
            ny.append(edge.geom.getY()[-1])
        
        for s, t, u, v in zip(x1b, y1b, x2b, y2b):
            exb.append(s)
            exb.append(u)
            exb.append(None)
            eyb.append(t)
            eyb.append(v)
            eyb.append(None)
        for s, t, u, v in zip(x1d, y1d, x2d, y2d):
            exd.append(s)
            exd.append(u)
            exd.append(None)
            eyd.append(t)
            eyd.append(v)
            eyd.append(None)

        for s, t, u, v in zip(x1i, y1i, x2i, y2i):
            exi.append(s)
            exi.append(u)
            exi.append(None)
            eyi.append(t)
            eyi.append(v)
            eyi.append(None)

        if len(edges) > 0:
            append.plot(exb, eyb, edges, linewidth=size, label="double sens")
        if len(direct) > 0:
            append.plot(exd, eyd, direct, linewidth=size, label="direct")
        if len(indirect) > 0:
            append.plot(exi, eyi, indirect, linewidth=size, label="indirect")
        if len(nodes) > 0:
            append.plot(nx, ny, nodes, markersize=4 * size)
        