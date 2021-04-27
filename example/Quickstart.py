'''

lecture d'un gpx 
+ calcul de la vitesse brut 
+ segmentation (avec les AF) sur le changement de vitesse 
+ récupération d'un sous-ensemble de traces 
+ interpolation/lissage + ré-estimation des vitesses...

'''
import matplotlib.pyplot as plt

from tracklib.core.GPSTime import GPSTime
from tracklib.io.GpxReader import GpxReader
from tracklib.core.Operator import Operator

import tracklib.algo.Analytics as algo
import tracklib.algo.Interpolation as interp

import tracklib.core.Grid as g
import tracklib.core.TrackCollection as trackCollection
import tracklib.algo.Summarize as summ

# ---------------------------------------------------
# Lecture des donnees
# ---------------------------------------------------
GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
tracks = GpxReader.readFromGpx("../data/activity_5807084803.gpx")
trace = tracks.getTrack(0)

# Transformation GEO coordinates to ENU
trace.toENUCoords()

# Display
trace.plot()
#trace.plot('POINT')

# ================================================
# SPEED : different 
trace.estimate_speed()

trace.plotAnalyticalFeature('speed', 'BOXPLOT')
trace.plotProfil('SPATIAL_SPEED_PROFIL')
trace.plot('POINT', 'speed')


# =====================================================
collection = trackCollection.TrackCollection([trace])
(Xmin, Xmax, Ymin, Ymax) = collection.bbox()
grille = g.Grid(Xmin-10, Ymin-10, Xmax - Xmin + 20, Ymax - Ymin + 20, 3)

af_algos = [algo.speed]
cell_operators = [summ.co_avg]
grille.addAnalyticalFunctionForSummarize(collection, af_algos, cell_operators)
grille.plot(algo.speed, summ.co_avg)


# ================================================
trace.operate(Operator.DIFFERENTIATOR, "speed", "dv")
trace.operate(Operator.RECTIFIER, "dv", "absdv")
trace.plotProfil("SPATIAL_absdv_PROFIL")
plt.show()


# ================================================
trace.segmentation(["absdv"], "speed_decoup", [1.5])
seg = trace.split_segmentation("speed_decoup")

COLORS = ['k-','r-','g-','b-','y-','m-','c-']

count = 0
interp.SPLINE_PENALIZATION = 1e-2
for i in range(len(seg)):
    trace = seg[i]
    if (trace.length() < 50):
        continue

    count += 1
    trace.resample(1, interp.ALGO_THIN_SPLINES, interp.MODE_SPATIAL)
    trace.estimate_speed()
    diff = trace.getLastObs().timestamp-trace.getFirstObs().timestamp
    v = round(trace.length()/diff*3.6,2)
    vm = round(trace.operate(Operator.MAX, "speed")*3.6,2)
    vc = round(100/(trace.getObs(150).timestamp-trace.getObs(50).timestamp)*3.6,2)
    print("Rep", count, ":  vmoy = ", v, "km/h   vmax = ", vm, " km/h   vc = ", vc, "km/h")
    plt.plot(trace.getX(), trace.getY(), COLORS[i%7])


plt.show()


