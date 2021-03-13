
# Tracklib
**Tracklib** library provide a variety of tools, operators and functions to manipulate GPS tracks

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![build status](https://travis-ci.org/umrlastig/tracklib.svg?branch=main)](https://travis-ci.org/umrlastig/tracklib)
[![codecov](https://codecov.io/gh/umrlastig/tracklib/branch/main/graph/badge.svg?token=pHLaV21j2O)](https://codecov.io/gh/umrlastig/tracklib)
[![Documentation Status](https://readthedocs.org/projects/tracklib/badge/?version=latest)](https://tracklib.readthedocs.io/en/latest/?badge=latest)


# Documentation

The official documentation is available at **[ReadTheDocs](https://tracklib.readthedocs.io)**


# Quickstart 

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




# Development & Contributions

### License
- Cecill-C

### Authors
- Yann Méneroux
- Marie-Dominique Van Damme

### Institute
- LASTIG, Univ Gustave Eiffel, ENSG, IGN










