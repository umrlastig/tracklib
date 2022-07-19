"""
Different stop detection implementations:
    - using acceleration criteria
    - matrix cost
    - st-dbscan
"""

import os.path
import matplotlib.pyplot as plt

from tracklib.core.GPSTime import GPSTime
import tracklib.algo.Interpolation as interpolation
from tracklib.io.GpxReader import GpxReader
import tracklib.algo.Analytics as stop
from tracklib.core.Plot import Plot
from tracklib.algo.Segmentation import findStopsGlobal


# -----------------------------------------------------------------------------
#   Comparaison de 2 méthodes pour détecter les points stops
# -----------------------------------------------------------------------------

resource_path = os.path.join(os.path.split(__file__)[0], "..")
path = os.path.join(resource_path, 'data/vincennes.gpx')
GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
tracks = GpxReader.readFromGpx(path, srid='ENU')
trace = tracks[0]
trace = trace.extract(1150, 2500)
#trace.toENUCoords()

#trace.summary()
#trace.plot()

# Interpolation spatiale
#trace.resample(5, interpolation.MODE_SPATIAL) # 5
trace.compute_abscurv()
#trace.addAnalyticalFeature(stop.acceleration)

# Plot
plot = Plot(trace)

# -----------------------------------------------------------------------------
# Première méthode
trace.createAnalyticalFeature('stop_point_with_time_window_criteria', stop.VAL_AF_TIME_WINDOW_NONE)
trace.addAnalyticalFeature(stop.stop_point_with_time_window_criteria, 'stop_point_with_time_window_criteria')

# -----------------------------------------------------------------------------
# Deuxième méthode
trace.addAnalyticalFeature(stop.stop_point_with_acceleration_criteria)

# -----------------------------------------------------------------------------
# Méthode 
stops = findStopsGlobal(trace, downsampling=5, diameter=30, duration=40)
# print (len(stops))
trace.createAnalyticalFeature('cost_matrix', stop.VAL_AF_TIME_WINDOW_MOVE)
for i in range(trace.size()):
    for s in range(stops.size()):
        idstop = stops.getObsAnalyticalFeature('id_ini', s)
        if idstop == i:
            trace.setObsAnalyticalFeature('cost_matrix', i, stop.VAL_AF_TIME_WINDOW_STOP)


# -----------------------------------------------------------------------------
# # On dessine
TAB_AFS = ['stop_point_with_time_window_criteria', 
           'stop_point_with_acceleration_criteria', 
           'cost_matrix']
plot.plotProfil('SPATIAL_SPEED_PROFIL', TAB_AFS)








