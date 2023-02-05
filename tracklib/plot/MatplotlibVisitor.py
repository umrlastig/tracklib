# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt


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
        
