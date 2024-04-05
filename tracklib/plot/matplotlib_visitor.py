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

import math
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import numpy as np
from numpy import sin, pi, cos
from PIL import Image
import progressbar
import sys

import tracklib as tracklib
from tracklib.plot import IPlotVisitor

from tracklib.core import isnan, NAN, getColorMap
from tracklib.algo import BIAF_ABS_CURV, computeAbsCurv
from tracklib.core import Operator

MARKERS_TYPE_NO_ENTRY = 0
MARKERS_TYPE_INFORMATION = 1
MARKERS_TYPE_NO_STOP = 2
MARKERS_TYPE_GIVE_WAY = 3
MARKERS_TYPE_WARNING = 4
MARKERS_TYPE_SPOT = 5
MARKERS_TYPE_INTERDICTION = 6
MARKERS_TYPE_BOWTIE = 7


COLOR_POINT = [
    "gold",
    "orangered",
    "dodgerblue",
    "purple",
    "lime",
    "turquoise",
]



class MatplotlibVisitor(IPlotVisitor):
    
    def plotTrackAsMarkers(
        self, track, size=8, frg="k", bkg="w", sym_frg="+", sym_bkg="o", 
        type=None, append=True
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
            if type == MARKERS_TYPE_BOWTIE:
                frg = "b"
                bkg = "w"
                sym_frg = r'$\bowtie$'  # clubsuit
                sym_bkg = "o"    
            

        ax1.plot(track.getX(), track.getY(), marker=sym_bkg, color=frg, 
                 markersize=size, linestyle='None')
        ax1.plot(track.getX(), track.getY(), marker=sym_bkg, color=bkg, 
                 markersize=int(0.8 * size), linestyle='None')
        ax1.plot(track.getX(), track.getY(), marker=sym_frg, color=frg, 
                 markersize=int(0.8 * size), linestyle='None')
        
        return ax1
    
    
    def plotTrackProfil(self, track, template="SPATIAL_SPEED_PROFIL", 
                        afs=[], linestyle = '-', linewidth=1, color='g', 
                        append=False):
        """
        Représentation du profil de la trace suivant une AF.
        
        Le nom du template doit respecter: XXX_YYYY_PROFILE avec:
            - XXX: SPATIAL ou TEMPORAL
            - YYY: ALTI, SPEED ou AF_NAME
        
        Example:
            SPATIAL_SPEED_PROFIL, SPATIAL_ALTI_PROFIL,
            TEMPORAL_SPEED_PROFIL, TEMPORAL_ALTI_PROFIL

        On sait déjà que l'abscurv est calculée si nécessaire

        afs: tableau des nom d'afs, on test s'ils sont des isAFTransition.

        """
        
        #return plot.plotProfil(template, afs, append, linestyle, linewidth)
        
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(8, 3))
        else:
            ax1 = append
        
        nomaxes = template.split("_")
        if len(nomaxes) != 3:
            sys.exit("Error: pour le profil il faut respecter XXX_YYY_PROFIL")

        if nomaxes[0] != "SPATIAL" and nomaxes[0] != "TEMPORAL":
            sys.exit(
                "Error: pour le profil il faut respecter XXX_YYY_PROFIL avec XXX SPATIAL or TEMPORAL"
            )

        if nomaxes[2] != "PROFIL":
            sys.exit("Error: pour le profil il faut respecter XXX_YYY_PROFIL")

        if (
            nomaxes[1] != "SPEED"
            and nomaxes[1] != "ALTI"
            and not track.hasAnalyticalFeature(nomaxes[1])
        ):
            sys.exit(
                "Error: pour le profil il faut respecter XXX_YYY_PROFIL avec YYY: ALTI, SPEED or existing AF"
            )
        
        
        tabplot = []
        tablegend = []
        nomaxes = template.split("_")

        axe1 = nomaxes[0]
        if axe1 == "SPATIAL":
            computeAbsCurv(track)
            X = track.getAbsCurv()
            xmin = track.operate(Operator.MIN, "abs_curv")
            xmax = track.operate(Operator.MAX, "abs_curv")
            xtitle = "curvilinear abscissa"
        elif axe1 == "TEMPORAL":
            X = track.getT()
            xmin = track.operate(Operator.MIN, "t")
            xmax = track.operate(Operator.MAX, "t")
            xtitle = "timestamp"
        
        axe2 = nomaxes[1]
        if axe2 == "SPEED":
            Y = track.estimate_speed()
            ymax = track.operate(Operator.MAX, "speed")
        elif axe2 == "ALTI":
            Y = track.getZ()
            ymax = track.operate(Operator.MAX, "z")
        else:
            Y = track.getAnalyticalFeature(axe2)
            ymax = track.operate(Operator.MAX, axe2)

        tablegend.append("PROFIL")

        #fig, ax1 = plt.subplots(figsize=(10, 3))

        # "-"
        l = ax1.plot(X, Y, color=color, linestyle=linestyle,
                     linewidth=linewidth)

        tabplot.append(l)
        ax1.set_xlim(xmin, xmax)

        ax1.set(xlabel=xtitle, ylabel=axe2)
        ax1.set_title("'" + axe2 + "' profil according to " + xtitle)

        # ---------------------------------------------------------------------
        #   Ajout de la représentation des AF.
        # ---------------------------------------------------------------------
        limit = ymax + 0.5
        for (indice, af_name) in enumerate(afs):

            if track.isAFTransition(af_name):
            #if 1 == 1:
                tabmarqueurs = track.getAnalyticalFeature(af_name)
                marqueurs = set(tabmarqueurs)
                if NAN in marqueurs:
                    marqueurs.remove(NAN)

                xaf = []
                yaf = []
                for i in range(len(tabmarqueurs)):
                    val = tabmarqueurs[i]
                    if val == 1:
                        xaf.append(X[i])
                        yaf.append(limit + indice * 0.3)

                l = ax1.plot(
                    xaf,
                    yaf,
                    "o",
                    color=COLOR_POINT[indice],
                    markersize=2.5,
                    label=af_name,
                )
                tabplot.append(l)
                tablegend.append(af_name)

        # ---------------------------------------------------------------------
        # Legend
        if len(tabplot) > 1:
            # chartBox = ax1.get_position()
            # ax1.set_position([chartBox.x0, chartBox.y0, chartBox.width, chartBox.height*0.8])
            ax1.legend(
                #tabplot,
                labels=tablegend,
                loc="lower center",
                borderaxespad=0.1,
                title="",
                bbox_to_anchor=(0.5, -0.55),
            )
        
    
    def plotTrackEllipses(self, track, sym="r-", factor=3, af=None, append=True):
        """
        Plot track uncertainty (as error ellipses)
        Input track must contain an AF with (at least) a
        2 x 2 covariance matrix. If this matrix has dim > 2,
        first two dimensions are arbitrarily considered
        """
        
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(6, 5))
        else:
            ax1 = append
        
        if af is None:
            if "cov" in track.getListAnalyticalFeatures():
                af = "cov"
            if "kf_P" in track.getListAnalyticalFeatures():
                af = "kf_P"
        
        
        for k in range(len(track)):
            P = track.getObsAnalyticalFeature(af, k)[0:2, 0:2]
            [V, D] = np.linalg.eig(P)

            alpha = math.atan(-D[0,1] / D[0,0]) * 180 / math.pi
            Xhat = track[k].position.getX()
            Yhat = track[k].position.getY()
            SDXhat = math.sqrt(V[0])
            SDYhat = math.sqrt(V[1])
            

            e = Ellipse((Xhat, Yhat), factor * SDXhat, factor * SDYhat, angle=alpha)
            e.set_fill(False)
            e.set_linewidth(0.5)
            e.set_edgecolor(sym[0])
            ax1.add_artist(e)

        
    
    def plotTrack(self, track, sym="k-", type="LINE", af_name="", cmap=-1, append=True, 
             size=5, style=None, color=None, w=6.4, h=4.8, title="", xlabel=None, ylabel=None,
             xlim=None, ylim=None):
        """
        Method to plot a track (short cut from Plot).
        Représentation d'une trace sous forme de ligne ou de point.
        On peut visualiser la valeur d'une AF avec une couleur sur les points.
        
        Append:
            - True : append to the current plot
            - False: create a new plot
            - Ax   : append to the fiven ax object
        ----------------------------------------------------
        Output:
            Ax object (may be input into append parameter)
            
    
        af_name: test si isAFTransition
        """
        
        if type == "CIRCULAR":
            self.__plotCircular(track, w, h, title, append)
            return 
        
        if type not in ['LINE', 'POINT'] and not '-' in sym:
            type = "POINT"
            
        margin=0.1
        pointsize = size
        if not '-' in sym:
            type = "POINT"
        tcolor = sym[0]
        marker = sym[1]
        
        if style is not None:
            marker = style
        if color is not None:
            tcolor = color

        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(w, h))
        else:
            ax1 = append
            
        X = track.getX()
        Y = track.getY()
        
        xmin = track.operate(Operator.MIN, "x")
        xmax = track.operate(Operator.MAX, "x")
        ymin = track.operate(Operator.MIN, "y")
        ymax = track.operate(Operator.MAX, "y")

        dx = xmax - xmin
        dy = ymax - ymin
        xmin = xmin - dx * margin
        ymin = ymin - dy * margin
        xmax = xmax + dx * margin
        ymax = ymax + dy * margin
        
        if af_name != None and af_name != "":
            
            if track.isAFTransition(af_name):
                tabmarqueurs = track.getAnalyticalFeature(af_name)
                xaf = []
                yaf = []
                for i in range(len(tabmarqueurs)):
                    val = tabmarqueurs[i]
                    if val == 1:
                        xaf.append(track.getObs(i).position.getX())
                        yaf.append(track.getObs(i).position.getY())

                ax1.plot(xaf, yaf, "o", color=color, markersize=size,
                    label=af_name )
                #tabplot.append(l)
                #tablegend.append(af_name)
            else:
                if cmap == -1:
                    cmap = getColorMap((255, 0, 0), (32, 178, 170))
                
                values = track.getAnalyticalFeature(af_name)
                s = [pointsize + values[n] for n in range(len(X))]
                scatter = ax1.scatter(X, Y, c=values, cmap=cmap, s=s)
                fig = plt.gcf()
                fig.colorbar(scatter, ax=ax1)
        
        elif type == "POINT":
            ax1.scatter(X, Y, s=pointsize, c=tcolor, marker=marker)
        
        else:
            # type == LINE
            ax1.plot(X, Y, color=tcolor, linestyle=marker, linewidth=1.5)

        # AXES: label + limit        
        if xlabel is None and ylabel is None:
            # tenir compte du type Coord
            if track.getSRID() == "Geo":
                ax1.set(xlabel="lon (deg)", ylabel="lat (deg)")
            if track.getSRID() == "ENU":
                ax1.set(xlabel="E (m)", ylabel="N (m)")
            if track.getSRID() == "ECEF":
                print("Warning: can't plot track in ECEF coordinate system")
                ax1.set(xlabel="X(m)", ylabel="Y(m)")
        else:
            ax1.set_xlabel(xlabel)
            ax1.set_ylabel(ylabel)

        # decoration
        if xlim is None:
            ax1.set_xlim(xmin, xmax)
        else:
            ax1.set_xlim(xlim[0], xlim[1])
        if ylim is None:
            ax1.set_ylim(ymin, ymax)
        else:
            ax1.set_ylim(ylim[0], ylim[1])
        
        if title != "":
            ax1.set_title(title)
        else:
            ax1.set_title("Track " + str(track.uid))
        
        
    def __plotCircular(self, track, w, h, title, append):
        
        if isinstance(append, bool):
            if append:
                ax = plt.gca()
            else:
                fig, ax = plt.subplots(figsize=(w, h))
        else:
            ax = append
        
        computeAbsCurv(track)
        
        r = 0.7
        decal = 0.05
        msize = 5
        ms = 2

        borne = 0.9
        plt.xlim([-borne, borne])
        plt.ylim([-borne, borne])

        # Départ
        ax.plot(r * cos(decal), r * sin(decal), 'ro', markersize=msize)
        ax.plot((r-0.1) * cos(decal), (r-0.1) * sin(decal), 'ro', markersize=msize)
        plt.text(r + 1.1*decal, 0 + 1.1*decal, 'S')
        
        # Arrivée
        ax.plot(r * cos(2*pi-decal), r * sin(2*pi-decal), 'ro', markersize=msize)
        ax.plot((r-0.1) * cos(2*pi-decal), (r-0.1) * sin(2*pi-decal), 'ro', markersize=msize)
        plt.text(r + decal, 0 - decal, 'E')
        
        T = track.getT()
        tmin = track.operate(Operator.MIN, "t")
        tmax = track.operate(Operator.MAX, "t")
        
        X1 = []
        X2 = []
        Y1 = []
        Y2 = []
        for i in range(0, track.size()):
            abscurv = track.getObsAnalyticalFeature('abs_curv', i)
            abstemp = T[i] - tmin
            
            alpha1 = abscurv * (2 * pi - 2*decal) / track.length() + decal
            X1.append(r * cos(alpha1))
            Y1.append(r * sin(alpha1))
            
            alpha2 = abstemp * (2 * pi - 2*decal) / (tmax - tmin) + decal
            X2.append((r-0.1) * cos(alpha2))
            Y2.append((r-0.1) * sin(alpha2))
    
        ax.plot(X1, Y1, 'ko', markersize=ms, label='Reference: length')
        ax.plot(X2, Y2, 'bo', markersize=ms, label='Reference: duration')
        ax.legend()  # handles=[line1, line2]
        
        if title != "":
            ax.set_title(title)
        else:
            ax.set_title("Track " + str(track.uid))
        
        
    def __plotBoxplot(self, track, af_name, ax1):
        """TODO"""
        ax1.set(xlabel=af_name)
        ax1.set_title(af_name + " observations boxplot")
        
        data = []
        values = track.getAnalyticalFeature(af_name)
        for i in range(len(values)):
            val = values[i]
            if not isnan(val):
                data.append(val)
        ax1.boxplot(data, vert=False)
        
    def __plotAF(self, track, af_name, ax1):
        """TODO"""
        ax1.set(xlabel="absciss curvilign")
        ax1.set_title(af_name + " observations boxplot")
        
        x = []
        data = []
        values = track.getAnalyticalFeature(af_name)
        for i in range(len(values)):
            val = values[i]
            if not isnan(val):
                x.append(track.getObsAnalyticalFeature('abs_curv', i))
                data.append(val)
        ax1.plot(x, data)
        
    def plotAnalyticalFeature(self, track, af_name, template="BOXPLOT", append=False):
        """
        Plot AF values by abcisse curvilign.
        """
        
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(8, 2))
        else:
            ax1 = append
        
        if not track.hasAnalyticalFeature(BIAF_ABS_CURV):
            computeAbsCurv(track)

        if template == 'BOXPLOT':
            self.__plotBoxplot(track, af_name, ax1)
        else:
            self.__plotAF(track, af_name, ax1)
        
        
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
    
    
    

    # ==========================================================================
    # ==========================================================================

    
    
def plotOnImage(track, image_path, sym="r.", markersize=1):
    """TODO"""
    N = len(track)
    img = Image.open(image_path)
    plt.imshow(img)
    plt.plot(track.getX(), track.getY(), sym, markersize)


def videoOnImage(track, image_path, sym="r.", markersize=1):
    """TODO"""
    N = len(track)
    img = Image.open(image_path)
    plt.imshow(img)
    for i in progressbar.progressbar(range(len(track))):
        for j in range(i):
            plt.plot(
                track[j].position.getX(), track[j].position.getY(), "r.", markersize=1
            )
        plt.savefig("export" + "{:04d}".format(i) + ".png")
