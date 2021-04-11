"""
Example detect stop points with two methods.
"""

from tracklib.core.GPSTime import GPSTime
import tracklib.algo.Interpolation as interpolation
from tracklib.io.GpxReader import GpxReader
import tracklib.algo.AlgoAF as stop

# -----------------------------------------------------------------------------
#   Comparaison de 2 méthodes pour détecter les points stops
# -----------------------------------------------------------------------------

path = '../data/vincennes.gpx'
GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
tracks = GpxReader.readFromGpx(path)
trace = tracks[0]

trace.summary()
trace.plot()

# Interpolation spatiale
trace.resample(5, interpolation.MODE_SPATIAL)
trace.compute_abscurv()

# Première méthode
trace.createAnalyticalFeature('stop_point_with_time_window_criteria', stop.VAL_AF_TIME_WINDOW_NONE)
trace.addAnalyticalFeature(stop.stop_point_with_time_window_criteria, 'stop_point_with_time_window_criteria')


# Autre méthode
trace.addAnalyticalFeature(stop.stop_point_with_acceleration_criteria)


# On dessine
TAB_AFS = ['stop_point_with_time_window_criteria', 'stop_point_with_acceleration_criteria']
trace.plotProfil('SPATIAL_SPEED_PROFIL', TAB_AFS)
#trace.plotProfil('SPATIAL_ALTI_PROFIL', TAB_AFS)
#trace.plotProfil('TEMPORAL_SPEED_PROFIL', TAB_AFS)
#trace.plotProfil('TEMPORAL_ALTI_PROFIL', TAB_AFS)

