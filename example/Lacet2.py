# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt

from tracklib.io.FileReader import FileReader
import tracklib.algo.Interpolation as interpolation
import tracklib.algo.Cinematics as Cinematics
from tracklib.core.Kernel import GaussianKernel
from tracklib.core.Operator import Operator
import tracklib.core.Utils as utils

# =============================================================================
tracks = FileReader.readFromWKTFile('./data/lacet/ecrins.csv', 0, 1, 2, ",", 1, 
                                    "ENUCoords", None, True)

trace = tracks["903959","%"][0]
trace = trace.extract(270, 300)
trace.resample(5, interpolation.MODE_SPATIAL)
trace.plot(append = False, sym='g-', label='original track')
print (trace.size())


# =============================================================================
#  Point d'inflexion
kernel = GaussianKernel(3)
trace.operate(Operator.FILTER, "x", kernel, "x_filtered")
trace.operate(Operator.FILTER, "y", kernel, "y_filtered")
trace.operate("x=x_filtered")
trace.operate("y=y_filtered")

trace.plot(append = True, sym='b-', label='gaussian filter')
print (trace.size())
plt.legend()


# =============================================================================
#  Point d'inflexion
    
COLS = utils.getColorMap((220, 220, 220), (255, 0, 0))
trace.addAnalyticalFeature(Cinematics.isInflection, "pointinflexion")
trace.plot(type='POINT', af_name='pointinflexion', append = False, cmap = COLS)


# =============================================================================
#  Sommet

trace.addAnalyticalFeature(Cinematics.vertex, "sommet")
COLS = utils.getColorMap((220, 220, 220), (45, 192, 150))
trace.plot(type='POINT', af_name='sommet', append = False, cmap = COLS)

# =============================================================================




