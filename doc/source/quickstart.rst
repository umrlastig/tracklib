
Quick start 
=============

.. code-block:: python

	'''

	lecture d'un gpx 
	+ calcul de la vitesse brut 
	+ segmentation (avec les AF) sur le changement de vitesse 
	+ récupération d'un sous-ensemble de traces 
	+ interpolation/lissage + ré-estimation des vitesses...

	'''

	import matplotlib.pyplot as plt

	import tracklib.algo.Interpolation as interp
	import tracklib.core.Obs as obs
	from tracklib.core.GPSTime import GPSTime
	from tracklib.io.GpxReader import GpxReader
	from tracklib.core.Coords import GeoCoords
	from tracklib.core.Operator import Operator


	# ---------------------------------------------------
	# Lecture des donnees
	# ---------------------------------------------------
	GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
	tracks = GpxReader.readFromGpx("../data/activity_5807084803.gpx")
	trace = tracks[0]

	base_geo = trace.getFirstObs().position
	base = GeoCoords(base_geo.getX(), base_geo.getY(), base_geo.getZ())
	for i in range(trace.size()):
		geo = GeoCoords(trace.getObs(i).position.getX(), trace.getObs(i).position.getY(), trace.getObs(i).position.getZ())
		enu = geo.toENUCoords(base)
		trace.setObs(i, obs.Obs(enu,trace.getObs(i).timestamp))


	start = trace.getFirstObs().timestamp

	trace.estimate_speed()
	trace.operate(Operator.DIFFERENTIATOR, "speed", "dv")
	trace.operate(Operator.RECTIFIER, "dv", "absdv")
	trace.segmentation(["absdv"], "speed_decoup", [1.5])

	trace.plotAnalyticalFeature("absdv", "PLOT")

	seg = trace.split_segmentation("speed_decoup")



	COLORS = ['k-','r-','g-','b-','y-','m-','c-']

	trace.plot()


	count = 0
	interp.SPLINE_PENALIZATION = 1e-2
	for i in range(len(seg)):
		trace = seg[i]
		if (trace.length() < 50):
			continue

		count += 1
		trace.resample(1, interp.ALGO_THIN_SPLINES, interp.MODE_SPATIAL)
		trace.estimate_speed()
		v = round(trace.length()/(trace.getLastObs().timestamp-trace.getFirstObs().timestamp)*3.6,2)
		vm = round(trace.operate(Operator.MAX, "speed")*3.6,2)
		vc = round(100/(trace.getObs(150).timestamp-trace.getObs(50).timestamp)*3.6,2)
		print("Rep", count, ":  vmoy = ", v, "km/h   vmax = ", vm, " km/h   vc = ", vc, "km/h")
		plt.plot(trace.getX(), trace.getY(), COLORS[i%7])


	plt.show()


