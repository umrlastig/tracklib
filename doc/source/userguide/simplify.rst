:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 07/03/2021, 06/03/2022


Simplify a track
=================

The process "Track simplification" generally returns a new track. Tolerance is in the unit of track observation coordinates.


Douglas Peucker Simplication
*****************************

Ref: Algorithms for the Reduction of the Number of Points Required to Represent a Digitized Line or its Caricature. 
David H. Douglas
Thomas K. Peucker
https://utpjournals.press/doi/10.3138/FM57-6770-U75U-7727


.. figure:: ../img/simplify_douglaspeucker.png
   :width: 450px
   :align: center

   Figure 1 : Simplification with Douglas Peucker


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


.. figure:: ../img/simplify_visvalingam.png
   :width: 450px
   :align: center

   Figure 1 : Simplification with Visvalingram


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
  tolerance = 50
  trace3 = Simplification.simplify(trace, tolerance, 
			 Simplification.MODE_SIMPLIFY_VISVALINGAM)
  trace.plot(append = False, sym='g-', label='original track')
  trace3.plot(append = True, sym='b-', label='simplify:visvalingam')
  plt.legend()



Kernel simplification
**********************

.. figure:: ../img/simplify_gaussian_filter.png
   :width: 450px
   :align: center

   Figure 1 : Simplification with a gaussian kernel filter


Build a kernel. For example a [Gaussian Filter](https://tracklib.readthedocs.io/en/latest/api_documentation/core/core-kernel.html#tracklib.core.Kernel.GaussianKernel):


.. code-block:: python

  import matplotlib.pyplot as plt
  from tracklib.io.FileReader import FileReader
  import tracklib.algo.Simplification as Simplification
  from tracklib.core.Kernel import GaussianKernel
  from tracklib.core.Operator import Operator

  chemin = './data/lacet/ecrins.csv'
  tracks = FileReader.readFromWKTFile(chemin, 0, 1, 2, ",", 1, 
                                    "ENUCoords", None, True)
  trace = tracks["903959","%"][0]
  trace = trace.extract(70,120)

  trace.summary()

  # ---------------------------------------------------
  kernel = GaussianKernel(3)
  trace.operate(Operator.FILTER, "x", kernel, "x_filtered")
  trace.operate(Operator.FILTER, "y", kernel, "y_filtered")
  trace.plot(append = False, sym='g-', label='original track')
  plt.plot(trace.getAnalyticalFeature("x_filtered"), trace.getAnalyticalFeature("y_filtered"), 
		 'b-', label='simplify:gaussian filter')
  plt.legend()



Squaring algorithm
*******************

.. figure:: ../img/simplify_squaring.png
   :width: 450px
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

