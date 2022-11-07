# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os.path

from tracklib.core.GPSTime import GPSTime
from tracklib.io.FileReader import FileReader
import tracklib.algo.Interpolation as interpolation
from tracklib.core.Kernel import GaussianKernel
from tracklib.core.Operator import Operator
import tracklib.algo.Filtering as flt

# =============================================================================
resource_path = os.path.join(os.path.split(__file__)[0], "..")
csvpath = os.path.join(resource_path, 'data/lacet/ecrins.csv')
tracks = FileReader.readFromWkt(csvpath, 0, 1, 2, ",", 1, 
                                    "ENUCoords", None, True)

trace = tracks["903959","%"][0]
trace = trace.extract(280, 300)
trace.plot()
trace.plot('kx', pointsize=20)

for i in range(trace.size()):
    if i > 1:
        t = trace.getObs(i-1).timestamp.addSec(1)
        trace.getObs(i).timestamp = t
    else:
        t = GPSTime.random()
        trace.getObs(i).timestamp = t

print (trace.size())

#trace.resample(5, interpolation.MODE_SPATIAL)
# trace.plot('ko', pointsize=2)
#trace.plot(append = False, sym='g-', label='original track')
# print (trace.size())

#trace2 = trace.copy()

# =============================================================================
#  Point d'inflexion
# kernel = GaussianKernel(3)
# trace.operate(Operator.FILTER, "x", kernel, "x_filtered")
# trace.operate(Operator.FILTER, "y", kernel, "y_filtered")
# trace.operate("x=x_filtered")
# trace.operate("y=y_filtered")

# trace.plot(append = True, sym='b-', label='gaussian filter')
# print (trace.size())
# plt.legend()

interpolation.GP_KERNEL = GaussianKernel(2.8)
trace.resample(delta=50, algo = interpolation.ALGO_GAUSSIAN_PROCESS) 
trace.plot('r-')


#interpolation.GP_KERNEL = GaussianKernel(3)
#trace.resample(delta=10, algo = interpolation.ALGO_GAUSSIAN_PROCESS, 
#               mode = interpolation.MODE_TEMPORAL)  
#print (trace.size())
#trace2.plot('r-')


#trace = flt.filter_seq(trace, kernel=GaussianKernel(3), 
#                       dim=flt.FILTER_XY)
#trace.plot('r-')


# -------------------------
# interpolation.GP_KERNEL = GaussianKernel(10)
# interpolation.GP_SMOOTHING = 0.001
# trace.resample(delta=10, algo = interpolation.ALGO_GAUSSIAN_PROCESS)  
# print (trace.size())
# #self.view(self.track, sym)	
# trace.plot(sym='r-', append=False)





