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



This module contains the class to plot GPS tracks and its AF

"""

import math
import numpy as np
from numpy import sin, pi, cos
import progressbar
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from PIL import Image
import sys

from tracklib.core import NAN, getColorMap, isnan
from tracklib.algo import BIAF_ABS_CURV, computeAbsCurv
from tracklib.core import Operator

# MODE_REPRESENT_TRACK2D = 1
# MODE_REPRESENT_SPEED_PROFIL = 2

COLOR_POINT = [
    "gold",
    "orangered",
    "dodgerblue",
    "purple",
    "lime",
    "turquoise",
]  #: TODO

MARKERS_TYPE_NO_ENTRY = 0
MARKERS_TYPE_INFORMATION = 1
MARKERS_TYPE_NO_STOP = 2
MARKERS_TYPE_GIVE_WAY = 3
MARKERS_TYPE_WARNING = 4
MARKERS_TYPE_SPOT = 5
MARKERS_TYPE_INTERDICTION = 6


class Plot:
    """
    This module contains the class to plot GPS tracks and its AF
    """

    def __init__(self, track):
        """TODO"""
        self.track = track
        self.color = "forestgreen"
        self.sym = "g-"
        self.marker = "-"
        self.w = 10
        self.h = 3
        self.pointsize = 5

    def __isAFTransition(self, track, af_name):
        """
        Return true if AF is transition marker.
        For example return true if AF values are like:
            000000000000010000100000000000000000001000000100000
        Values are contained in {0, 1}. 1 means there is a regime change
        """
        tabmarqueurs = track.getAnalyticalFeature(af_name)
        marqueurs = set(tabmarqueurs)
        if NAN in marqueurs:
            marqueurs.remove(NAN)
        if len(marqueurs.intersection([0, 1])) == 2:
            return True
        else:
            return False

    # ----------------------------------------------------
    # Append:
    #  - True : append to the current plot
    #  - False: create a new plot
    #  - Ax   : append to the fiven ax object
    # ----------------------------------------------------
    # Output:
    #  Ax object (may be input into append parameter)
    # ----------------------------------------------------
    def plot(self, type="LINE", af_name=None, cmap=-1, margin=0.1, append=False,
			 label=None, title="", xlabel=None, ylabel=None,
             xlim=None, ylim=None):
        """
        Représentation d'une trace sous forme de ligne ou de point.
        
        On peut visualiser la valeur d'une AF avec une couleur sur les points.
        """

        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(self.w, self.h))
        else:
            ax1 = append

        X = self.track.getX()
        Y = self.track.getY()

        xmin = self.track.operate(Operator.MIN, "x")
        xmax = self.track.operate(Operator.MAX, "x")
        ymin = self.track.operate(Operator.MIN, "y")
        ymax = self.track.operate(Operator.MAX, "y")

        dx = xmax - xmin
        dy = ymax - ymin
        xmin = xmin - dx * margin
        ymin = ymin - dy * margin
        xmax = xmax + dx * margin
        ymax = ymax + dy * margin

        if af_name != None and af_name != "":
            if cmap == -1:
                cmap = getColorMap((255, 0, 0), (32, 178, 170))
            values = self.track.getAnalyticalFeature(af_name)

            #s = [self.pointsize + values[n]*15 for n in range(len(X))]
            s = [self.pointsize + values[n] for n in range(len(X))]
            scatter = ax1.scatter(X, Y, c=values, cmap=cmap, s=s, label=label)
            # plt.scatter(X, Y, s=self.pointsize, c=self.color)

            fig = plt.gcf()
            fig.colorbar(scatter, ax=ax1)
        
        elif type == "POINT":
            ax1.scatter(X, Y, s=self.pointsize, c=self.color, marker=self.marker)
            
        elif type == "CIRCULAR":
            self.__plotCircular(ax1)
        
        else:
            # type == LINE
            ax1.plot(X, Y, "-", color=self.color, label=label)

        if type != 'CIRCULAR':
            
            if xlabel is None and ylabel is None:
                # tenir compte du type Coord
                if self.track.getSRID() == "Geo":
                    ax1.set(xlabel="lon (deg)", ylabel="lat (deg)")
                if self.track.getSRID() == "ENU":
                    ax1.set(xlabel="E (m)", ylabel="N (m)")
                if self.track.getSRID() == "ECEF":
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
            ax1.set_title("Track " + str(self.track.uid))

        return ax1
    
    
    def __plotCircular(self, ax):
        
        computeAbsCurv(self.track)
        
        r = 0.7
        decal = 0.05
        msize = 5
        ms = 2

        #t = arange(decal, 2*pi-decal, 0.01)
        #x = r * cos(t)
        #y = r * sin(t)
        
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
        
        T = self.track.getT()
        tmin = self.track.operate(Operator.MIN, "t")
        tmax = self.track.operate(Operator.MAX, "t")
        
        X1 = []
        X2 = []
        Y1 = []
        Y2 = []
        for i in range(0, self.track.size()):
            abscurv = self.track.getObsAnalyticalFeature('abs_curv', i)
            abstemp = T[i] - tmin
            
            alpha1 = abscurv * (2 * pi - 2*decal) / self.track.length() + decal
            X1.append(r * cos(alpha1))
            Y1.append(r * sin(alpha1))
            
            alpha2 = abstemp * (2 * pi - 2*decal) / (tmax - tmin) + decal
            X2.append((r-0.1) * cos(alpha2))
            Y2.append((r-0.1) * sin(alpha2))
    
        ax.plot(X1, Y1, 'ko', markersize=ms, label='Reference: length')
        ax.plot(X2, Y2, 'bo', markersize=ms, label='Reference: duration')
        ax.legend()  # handles=[line1, line2]
        

    # ----------------------------------------------------
    # Plot track uncertainty (as error ellipses)
    # Input track must contain an AF with (at least) a
    # 2 x 2 covariance matrix. If this matrix has dim > 2,
    # first two dimensions are arbitrarily considered
    # ----------------------------------------------------
    def plotEllipses(self, track, sym="r-", factor=3, af=None, append=False):
        """TODO"""

        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(self.w, self.h))
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
            alpha = math.atan(-D[0][1] / D[0][0]) * 180 / math.pi
            Xhat = track[k].position.getX()
            Yhat = track[k].position.getY()
            SDXhat = D[0, 0]
            SDYhat = D[1, 1]

            e = Ellipse((Xhat, Yhat), factor * SDXhat, factor * SDYhat, angle=alpha)
            e.set_fill(False)
            e.set_linewidth(0.5)
            e.set_edgecolor(sym[0])
            ax1.add_artist(e)

        return ax1


    def plotAnalyticalFeature(self, af_name, template="BOXPLOT", append=False):
        """
        Plot AF values by abcisse curvilign.
        """
        
        if not self.track.hasAnalyticalFeature(BIAF_ABS_CURV):
            computeAbsCurv(self.track)

        if template == 'BOXPLOT':
            self.__plotBoxplot(af_name, append=append)
        else:
            self.__plotAF(af_name, append=append)
            

    def __plotBoxplot(self, af_name, append=False):
        """TODO"""
        
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(self.w, self.h))
        else:
            ax1 = append

        #fig, ax1 = plt.subplots(figsize=(6, 2))
        #ax1.set(xlabel="absciss curvilign")
        ax1.set(xlabel=af_name)
        ax1.set_title(af_name + " observations boxplot")
        
        data = []
        values = self.track.getAnalyticalFeature(af_name)
        for i in range(len(values)):
            val = values[i]
            if not isnan(val):
                data.append(val)
        
        ax1.boxplot(data, vert=False)
        
    def __plotAF(self, af_name, append=False):
        """TODO"""
        
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(self.w, self.h))
        else:
            ax1 = append

        #fig, ax1 = plt.subplots(figsize=(6, 2))
        ax1.set(xlabel="absciss curvilign")
        ax1.set_title(af_name + " observations boxplot")
        
        x = []
        data = []
        values = self.track.getAnalyticalFeature(af_name)
        for i in range(len(values)):
            val = values[i]
            if not isnan(val):
                x.append(self.track.getObsAnalyticalFeature('abs_curv', i))
                data.append(val)
        
        ax1.plot(x, data)


    def plotProfil(self, template="SPATIAL_SPEED_PROFIL", afs=[], append=False,
                   linestyle = '-', linewidth=1):
        """Représentation du profil de la trace suivant une AF.

        Le nom du template doit respecter: XXX_YYYY_PROFILE avec:

            - XXX: SPATIAL ou TEMPORAL
            - YYY: ALTI, SPEED ou AF_NAME
        
        Example:
            SPATIAL_SPEED_PROFIL, SPATIAL_ALTI_PROFIL,
                  TEMPORAL_SPEED_PROFIL, TEMPORAL_ALTI_PROFIL


        Le tableau de nom afs: teste si isAFTransition
        
        On sait déjà que l'abscurv est calculée si nécessaire

        afs: uniquement si 'isAFTransition'
        """
        
        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(self.w, self.h))
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
            and not self.track.hasAnalyticalFeature(nomaxes[1])
        ):
            sys.exit(
                "Error: pour le profil il faut respecter XXX_YYY_PROFIL avec YYY: ALTI, SPEED or existing AF"
            )
        
        tabplot = []
        tablegend = []
        nomaxes = template.split("_")

        axe1 = nomaxes[0]
        if axe1 == "SPATIAL":
            computeAbsCurv(self.track)
            X = self.track.getAbsCurv()
            xmin = self.track.operate(Operator.MIN, "abs_curv")
            xmax = self.track.operate(Operator.MAX, "abs_curv")
            xtitle = "curvilinear abscissa"
        elif axe1 == "TEMPORAL":
            X = self.track.getT()
            xmin = self.track.operate(Operator.MIN, "t")
            xmax = self.track.operate(Operator.MAX, "t")
            xtitle = "timestamp"

        axe2 = nomaxes[1]
        if axe2 == "SPEED":
            Y = self.track.estimate_speed()
            ymax = self.track.operate(Operator.MAX, "speed")
        elif axe2 == "ALTI":
            Y = self.track.getZ()
            ymax = self.track.operate(Operator.MAX, "z")
        else:
            Y = self.track.getAnalyticalFeature(axe2)
            ymax = self.track.operate(Operator.MAX, axe2)

        tablegend.append("PROFIL")

        #fig, ax1 = plt.subplots(figsize=(10, 3))

        # "-"
        l = ax1.plot(X, Y, color=self.color, linestyle=linestyle,
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

            if self.__isAFTransition(self.track, af_name):
            #if 1 == 1:
                tabmarqueurs = self.track.getAnalyticalFeature(af_name)
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

        

    def __plotProfile(self, af_name):
        """TODO"""

        fig, ax1 = plt.subplots(figsize=(8, 3))
        ax1.set(xlabel="absciss curvilign")

        ax1.plot(
            self.track.getAbsCurv(),
            self.track.getAnalyticalFeature(af_name),
            "b-",
            markersize=2.5,
        )



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
