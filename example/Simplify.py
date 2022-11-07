#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from tracklib.io.FileReader import FileReader
import tracklib.algo.Simplification as Simplification
from tracklib.core.Kernel import GaussianKernel
from tracklib.core.Operator import Operator

chemin = './data/lacet/ecrins.csv'
tracks = FileReader.readFromWkt(chemin, 0, 1, 2, ",", 1, 
                                    "ENUCoords", None, True)
trace = tracks["903959","%"][0]
#print (trace.size())
trace = trace.extract(70,120)

#trace.toENUCoords()
#trace.summary()

# ---------------------------------------------------
tolerance = 3
trace1 = Simplification.simplify(
             trace, tolerance, 
			 Simplification.MODE_SIMPLIFY_SQUARING
)
trace.plot(append = False, sym='g-', label='original track')
trace1.plot(append = True, sym='b-', label='simplify:squaring')
plt.legend()


# ---------------------------------------------------
tolerance = 25
trace2 = Simplification.simplify(
             trace, tolerance, 
			 Simplification.MODE_SIMPLIFY_DOUGLAS_PEUCKER
)
trace.plot(append = False, sym='g-', label='original track')
trace2.plot(append = True, sym='b-', label='simplify:douglas peucker')
plt.legend()


# ---------------------------------------------------
tolerance = 25
trace3 = Simplification.simplify(
             trace, tolerance, 
			 Simplification.MODE_SIMPLIFY_VISVALINGAM
)
trace.plot(append = False, sym='g-', label='original track')
trace3.plot(append = True, sym='b-', label='simplify:visvalingam')
plt.legend()


# ---------------------------------------------------
kernel = GaussianKernel(3)
trace.operate(Operator.FILTER, "x", kernel, "x_filtered")
trace.operate(Operator.FILTER, "y", kernel, "y_filtered")
trace.plot(append = False, sym='g-', label='original track')
plt.plot(trace.getAnalyticalFeature("x_filtered"), trace.getAnalyticalFeature("y_filtered"), 
		 'b-', label='simplify:gaussian filter')
plt.legend()


