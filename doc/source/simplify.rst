:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 07/03/2021


Simplification of GPS tracks
=============================

The process "Track simplification" returns a new track. Tolerance is in the unit of track observation coordinates.


Douglas Peucker Simplication
*****************************


Ref: Algorithms for the Reduction of the Number of Points Required to Represent a Digitized Line or its Caricature. 
David H. Douglas
Thomas K. Peucker
https://utpjournals.press/doi/10.3138/FM57-6770-U75U-7727


.. code-block:: python

  from tracklib.io.FileReader import FileReader
  import tracklib.algo.Simplification as Simplification

  chemin = './data/lacet/ecrins.csv'
  tracks = FileReader.readFromWKTFile(chemin, 0, 1, 2, ",", 1, 
                                    "ENUCoords", None, True)
  trace = tracks["903959","%"][0]
  trace = trace.extract(70,120)

  trace.summary()

  # ---------------------------------------------------
  tolerance = 20
  trace2 = Simplification.simplify(trace, tolerance, 
			 Simplification.MODE_SIMPLIFY_DOUGLAS_PEUCKER)
  trace.plot(append = False, sym='g-')
  trace2.plot(append = True, sym='b-')



Visvalingram Simplification
****************************

Line generalisation by repeated elimination of points - https://www.tandfonline.com/doi/abs/10.1179/000870493786962263




Kernel simplification
**********************

Build a kernel:

For example a Gaussian Filter:

.. code-block:: python

   kernel = GaussianKernel(201)
   track.operate(Operator.FILTER, "x", kernel, "x2")
   track.operate(Operator.FILTER, "y", kernel, "y2")
   plt.plot(track.getT(), track.getAnalyticalFeature("y"), 'b-', markersize=1.5)
   plt.plot(track.getT(), track.getAnalyticalFeature("y2"), 'r-')
   plt.show()


Squaring algorithm
*******************

.. figure:: ./img/simplify_squaring.png
   :width: 550px
   :align: center

   Figure 1 : Simplification with squaring algorithm


.. code-block:: python

  from tracklib.io.FileReader import FileReader
  import tracklib.algo.Simplification as Simplification

  chemin = './data/lacet/ecrins.csv'
  tracks = FileReader.readFromWKTFile(chemin, 0, 1, 2, ",", 1, 
                                    "ENUCoords", None, True)
  trace = tracks["903959","%"][0]
  trace = trace.extract(70,120)

  trace.summary()

  # ---------------------------------------------------
  tolerance = 3
  trace1 = Simplification.simplify(trace, tolerance, 
			 Simplification.MODE_SIMPLIFY_SQUARING)
  trace.plot(append = False, sym='g-')
  trace1.plot(append = True, sym='b-')

