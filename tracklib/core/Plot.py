"""
This module contains the class to plot GPS tracks and its AF
"""

import math
import numpy as np
import progressbar
import matplotlib.pyplot as plt
from tracklib.algo.Analytics import BIAF_ABS_CURV
import tracklib.core.Utils as utils

from matplotlib.patches import Ellipse

from PIL import Image

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
    """TODO"""

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
        if utils.NAN in marqueurs:
            marqueurs.remove(utils.NAN)
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
			 label=None):
        """TODO

        Représentation d'une trace sous forme de ligne ou de point.
        On peut visualiser la valeur d'une AF avec une couleur sur les points.
        """

        import tracklib.core.Operator as Operator

        if isinstance(append, bool):
            if append:
                ax1 = plt.gca()
            else:
                fig, ax1 = plt.subplots(figsize=(self.w, self.h))
        else:
            ax1 = append

        X = self.track.getX()
        Y = self.track.getY()

        xmin = self.track.operate(Operator.Operator.MIN, "x")
        xmax = self.track.operate(Operator.Operator.MAX, "x")
        ymin = self.track.operate(Operator.Operator.MIN, "y")
        ymax = self.track.operate(Operator.Operator.MAX, "y")

        dx = xmax - xmin
        dy = ymax - ymin
        xmin = xmin - dx * margin
        ymin = ymin - dy * margin
        xmax = xmax + dx * margin
        ymax = ymax + dy * margin

        if af_name != None and af_name != "":
            if cmap == -1:
                cmap = utils.getColorMap((255, 0, 0), (32, 178, 170))
            values = self.track.getAnalyticalFeature(af_name)

            s = [self.pointsize + values[n]*15 for n in range(len(X))]
            scatter = ax1.scatter(X, Y, c=values, cmap=cmap, s=s, label=label)
            # plt.scatter(X, Y, s=self.pointsize, c=self.color)
            if not append:
                fig.colorbar(scatter, ax=ax1)
        elif type == "POINT":
            ax1.scatter(X, Y, s=self.pointsize, c=self.color, marker=self.marker)
        else:
            ax1.plot(X, Y, "-", color=self.color, label=label)

        # TODO : tenir compte du type Coord
        if self.track.getSRID() == "Geo":
            ax1.set(xlabel="lon (deg)", ylabel="lat (deg)")
        if self.track.getSRID() == "ENU":
            ax1.set(xlabel="E (m)", ylabel="N (m)")
        if self.track.getSRID() == "ECEF":
            print("Warning: can't plot track in ECEF coordinate system")
            ax1.set(xlabel="X(m)", ylabel="Y(m)")

        if not append:
            plt.xlim([xmin, xmax])
            plt.ylim([ymin, ymax])
            plt.title("Track " + str(self.track.uid))

        return ax1

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

    def plotAnalyticalFeature(self, af_name, template="BOXPLOT"):
        """TODO

        Plot AF values by abcisse curvilign.
        """
        if not self.track.hasAnalyticalFeature(BIAF_ABS_CURV):
            self.track.compute_abscurv()

        # if template == 'BOXPLOT':
        self.__plotBoxplot(af_name)

    def __plotBoxplot(self, af_name):
        """TODO"""

        fig, ax1 = plt.subplots(figsize=(6, 2))
        ax1.set(xlabel="absciss curvilign")
        ax1.set_title(af_name + " observations boxplot")
        ax1.boxplot(self.track.getAnalyticalFeature(af_name), vert=False)

    def plotProfil(self, template="SPATIAL_SPEED_PROFIL", afs=[]):
        """TODO

        TEMPLATE:
            SPATIAL_SPEED_PROFIL, SPATIAL_ALTI_PROFIL,
                  TEMPORAL_SPEED_PROFIL, TEMPORAL_ALTI_PROFIL

        On sait déjà que l'abscur est calculée si nécessaire

        afs: uniquement si 'isAFTransition'
        """
        import tracklib.core.Operator as Operator

        tabplot = []
        tablegend = []
        nomaxes = template.split("_")

        axe1 = nomaxes[0]
        if axe1 == "SPATIAL":
            X = self.track.compute_abscurv()
            xmin = self.track.operate(Operator.Operator.MIN, "abs_curv")
            xmax = self.track.operate(Operator.Operator.MAX, "abs_curv")
            xtitle = "curvilinear abscissa"
        elif axe1 == "TEMPORAL":
            X = self.track.getT()
            xmin = self.track.operate(Operator.Operator.MIN, "t")
            xmax = self.track.operate(Operator.Operator.MAX, "t")
            xtitle = "timestamp"

        axe2 = nomaxes[1]
        if axe2 == "SPEED":
            Y = self.track.estimate_speed()
            ymax = self.track.operate(Operator.Operator.MAX, "speed")
        elif axe2 == "ALTI":
            Y = self.track.getZ()
            ymax = self.track.operate(Operator.Operator.MAX, "z")
        else:
            Y = self.track.getAnalyticalFeature(axe2)
            ymax = self.track.operate(Operator.Operator.MAX, axe2)

        tablegend.append("PROFIL")

        fig, ax1 = plt.subplots(figsize=(10, 3))

        l = ax1.plot(X, Y, "-", color=self.color)

        tabplot.append(l)
        plt.xlim([xmin, xmax])

        ax1.set(xlabel=xtitle, ylabel=axe2)
        ax1.set_title("'" + axe2 + "' profil according to " + xtitle)

        # ---------------------------------------------------------------------
        #   Ajout de la représentation des AF.
        # ---------------------------------------------------------------------
        limit = ymax + 0.5
        for (indice, af_name) in enumerate(afs):

            if self.__isAFTransition(self.track, af_name):
                print("---")

                tabmarqueurs = self.track.getAnalyticalFeature(af_name)
                marqueurs = set(tabmarqueurs)
                if utils.NAN in marqueurs:
                    marqueurs.remove(utils.NAN)

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
                tabplot,
                labels=tablegend,
                loc="lower center",
                borderaxespad=0.1,
                title="",
                bbox_to_anchor=(0.5, -0.55),
            )

        if len(afs) > 0 and afs[0] != None:
            plt.title(afs[0])

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
