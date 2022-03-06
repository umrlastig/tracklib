#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from tracklib.io.FileReader import FileReader
import tracklib.algo.Simplification as Simplification


chemin = './data/lacet/ecrins.csv'
tracks = FileReader.readFromWKTFile(chemin, 0, 1, 2, ",", 1, 
                                    "ENUCoords", None, True)
trace = tracks["903959","%"][0]
print (trace.size())
trace = trace.extract(70,120)

#trace.toENUCoords()
trace.summary()

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
tolerance = 20
trace2 = Simplification.simplify(
             trace, tolerance, 
			 Simplification.MODE_SIMPLIFY_DOUGLAS_PEUCKER
)
trace.plot(append = False, sym='g-')
trace2.plot(append = True, sym='b-')