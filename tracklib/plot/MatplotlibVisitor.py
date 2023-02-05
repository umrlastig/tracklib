# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt

import tracklib.core.Network as network
import tracklib.core.SpatialIndex as index
import tracklib.plot.IPlotVisitor as iplot


class MatplotlibVisitor(iplot.IPlotVisitor):
    
    def plotSpatialIndex(self, si: index.SpatialIndex, base:bool=True, append=True):
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
            ax1.plot([xi, xi], [si.ymin, si.ymax], "-", color="blue")
        
        for j in range(0, si.lsize):
            yj = j * si.dY + si.ymin
            ax1.plot([si.xmin, si.xmax], [yj, yj], "-", color="blue")


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
                if edge.orientation == network.Edge.DOUBLE_SENS:
                    x1b.append(edge.geom.getX()[j])
                    x2b.append(edge.geom.getX()[j + 1])
                    y1b.append(edge.geom.getY()[j])
                    y2b.append(edge.geom.getY()[j + 1])
                else:
                    if edge.orientation == network.Edge.SENS_DIRECT:
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
        