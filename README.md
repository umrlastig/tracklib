
# Tracklib
**Tracklib** library provide a variety of tools, operators and functions to manipulate GPS tracks

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![build status](https://travis-ci.org/umrlastig/tracklib.svg?branch=main)](https://travis-ci.org/umrlastig/tracklib)
[![codecov](https://codecov.io/gh/umrlastig/tracklib/branch/main/graph/badge.svg?token=pHLaV21j2O)](https://codecov.io/gh/umrlastig/tracklib)
[![Documentation Status](https://readthedocs.org/projects/tracklib/badge/?version=latest)](https://tracklib.readthedocs.io/en/latest/?badge=latest)


## README Contents

- [Documentation](#Documentation)
- [Quickstart](#Quickstart)
- Development & Contributions
    - [License](#License)
    - [Authors](#Authors)
	- [Institute](#Institute)
- [Attribution (citation)](#Attribution)


## Documentation

The official documentation is available at **[ReadTheDocs](https://tracklib.readthedocs.io)**


## Quickstart 

```python
import matplotlib.pyplot as plt

import tracklib.algo.Interpolation as interp
import tracklib.core.Obs as obs
from tracklib.core.GPSTime import GPSTime
from tracklib.io.GpxReader import GpxReader
from tracklib.core.Coords import GeoCoords
from tracklib.core.Operator import Operator

# ------------------------------------------------------------------
# Read data and plot track
# ------------------------------------------------------------------
GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
tracks = GpxReader.readFromGpx("../data/activity_5807084803.gpx")
trace = tracks[0]

base_geo = trace.getFirstObs().position
base = GeoCoords(base_geo.getX(), base_geo.getY(), base_geo.getZ())
for i in range(trace.size()):
	x = trace.getObs(i).position.getX()
	y = trace.getObs(i).position.getY()
	z = trace.getObs(i).position.getZ()
	geo = GeoCoords(x, y, z)
	enu = geo.toENUCoords(base)
	trace.setObs(i, obs.Obs(enu,trace.getObs(i).timestamp))

trace.plot()
```

Trajectory plot:

![png](https://tracklib.readthedocs.io/en/latest/_images/quickstart_1.png)

```python
# ------------------------------------------------------------------
#  Compute local speed and display boxplot of speed observations
# ------------------------------------------------------------------
trace.estimate_speed()
trace.operate(Operator.DIFFERENTIATOR, "speed", "dv")
trace.plotAnalyticalFeature('speed', 'BOXPLOT')
```

Speed observations boxplot:

![png](https://tracklib.readthedocs.io/en/latest/_images/quickstart_2.png)

```python
# ------------------------------------------------------------------
#  Compute speed change 
# ------------------------------------------------------------------
trace.operate(Operator.RECTIFIER, "dv", "absdv")
trace.plotAnalyticalFeature("absdv", "PLOT")
```

Speed change according to the curvilinear abscissa:

![png](https://tracklib.readthedocs.io/en/latest/_images/quickstart_3.png)

```python
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
```

Segmentation per speed change:

![png](https://tracklib.readthedocs.io/en/latest/_images/quickstart_4.png)


## Development & Contributions

### License
- Cecill-C

### Authors
- Yann Méneroux
- Marie-Dominique Van Damme

### Institute
- LASTIG, Univ Gustave Eiffel, ENSG, IGN










