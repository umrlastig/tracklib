:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 07/03/2021


Summarize GPS information into a grid
============================================

This functionality of tracklib reduce the full dataset of GPS traces into a regular grid of summarized features. 
In each cell, n aggregated features (such as mean and standard deviation of speeds, number of traces, most frequent bearing ...) 
are computed to produce a set of raster maps, which may be seen as a single image with one channel.

.. figure:: ./img/summarize.png
   :width: 450px
   :align: center

   Figure 1 : Computation of mean speeds feature



Example
---------

.. code-block:: python

	import os
	import time

	from tracklib.core.Coords import GeoCoords
	import tracklib.io.GpxReader as gpx
	import tracklib.algo.AlgoAF as algo
	from tracklib.core.GPSTime import GPSTime

	import tracklib.core.Grid as g
	import tracklib.core.TrackCollection as trackCollection
	import tracklib.util.CellOperator as celloperator


	GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2s1Z")


	pathdir = '/PATH/GPS/'
	LISTFILE = os.listdir(pathdir)
	TRACES = []
	for f in LISTFILE:

		(lon, lat, ele) = gpx.GpxReader.readFirstPointFromGpx(pathdir + f)
		time.sleep(3)
		base_geo = GeoCoords(lon, lat, ele)
		base = GeoCoords(base_geo.getX(), base_geo.getY(), base_geo.getZ())
		traces = gpx.GpxReader.readFromGpx(pathdir + f, base)

		trace = traces[0]

		trace.addAnalyticalFeature(algo.ds)
		trace.addAnalyticalFeature(algo.speed)

		TRACES.append(trace)


	collection = trackCollection.TrackCollection(TRACES)
	#collection.plot()

	# Calcul de l'emprise
	(Xmin, Xmax, Ymin, Ymax) = collection.bbox()
	XSize = Xmax - Xmin
	YSize = Ymax - Ymin
	PixelSize = 500

	grille = g.Grid(Xmin, Ymin, XSize, YSize, PixelSize)

	# Summarize
	af_algos = [algo.speed, algo.speed]
	cell_operators = [celloperator.co_avg, celloperator.co_max]
	grille.addAnalyticalFunctionForSummarize(TRACES, af_algos, cell_operators)
	grille.plot(algo.speed, celloperator.co_avg)
	grille.plot(algo.speed, celloperator.co_max)



.. figure:: ./img/speed_features.png
   :width: 650px
   :align: center

   Figure 2 : Two features: mean speeds (left) and max speeds (right
