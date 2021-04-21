
Quick start 
=============


.. code-block:: python

	import matplotlib.pyplot as plt

	import tracklib.algo.AlgoAF as algo
	import tracklib.algo.Interpolation as interp
	from tracklib.core.GPSTime import GPSTime
	import tracklib.core.Grid as g
	from tracklib.core.Operator import Operator
	import tracklib.core.TrackCollection as trackCollection
	from tracklib.io.GpxReader import GpxReader
	import tracklib.util.CellOperator as celloperator


	# ------------------------------------------------------------------
	# Read data and plot track
	# ------------------------------------------------------------------
	GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
	tracks = GpxReader.readFromGpx("../data/activity_5807084803.gpx")
	trace = tracks.getTrack(0)

	# Transform GEO coordinates to ENU coordinates
	trace.toENUCoords()

	# Plot
	trace.plot()
	
	
.. figure:: ./img/quickstart_1.png
   :width: 550px
   :align: center

   Figure 1 : Trajectory plot 


.. code-block:: python

	# ------------------------------------------------------------------
	#  Compute local speed and display boxplot of speed observations
	# ------------------------------------------------------------------
	trace.estimate_speed()
	
	trace.plotAnalyticalFeature('speed', 'BOXPLOT')   # figure (a)
	trace.plotProfil('SPATIAL_SPEED_PROFIL')          # figure (b)
	trace.plot('POINT', 'speed')                      # figure (c)
	
.. figure:: ./img/Plot_Speed_4methods.png
   :width: 700px
   :align: center

   Figure 2 : Speed observations figures: boxplot (a), profil (b), plot (c) and grid (d)


.. code-block:: python

	# ------------------------------------------------------------------
	#  Summarize analytical features and plot it in image
	# ------------------------------------------------------------------
	collection = trackCollection.TrackCollection([trace])
	(Xmin, Xmax, Ymin, Ymax) = collection.bbox()
	grille = g.Grid(Xmin-10, Ymin-10, Xmax - Xmin + 20, Ymax - Ymin + 20, 3)

	af_algos = [algo.speed]
	cell_operators = [celloperator.co_avg]
	grille.addAnalyticalFunctionForSummarize([trace], af_algos, cell_operators)
	grille.plot(algo.speed, celloperator.co_avg)      # figure (d)



.. code-block:: python

	# ------------------------------------------------------------------
	#  Compute speed change 
	# ------------------------------------------------------------------
	trace.operate(Operator.RECTIFIER, "dv", "absdv")
	trace.plotAnalyticalFeature("absdv", "PLOT")
	
.. figure:: ./img/quickstart_3.png
   :width: 550px
   :align: center

   Figure 3 : Speed change according to the curvilinear abscissa


.. code-block:: python

	# ------------------------------------------------------------------
	#  Segmentation
	# ------------------------------------------------------------------
	trace.segmentation(["absdv"], "speed_decoup", [1.5])
	
	# ------------------------------------------------------------------
	# + récupération d'un sous-ensemble de traces 
	# + interpolation/lissage + ré-estimation des vitesses...
	# ------------------------------------------------------------------
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


.. figure:: ./img/quickstart_4.png
   :width: 550px
   :align: center

   Figure 4 : Segmentation per speed change


- Further examples of tracklib use-cases can be found in the example folder: SpeedProfil.py, Interpolation.py, LoadFromDatabase.py
