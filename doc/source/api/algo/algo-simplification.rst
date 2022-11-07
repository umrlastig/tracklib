Simplification
==============

We present on this page four filtering algorithms for track by using 
Douglas & Peucker simplification, Visvalingram simplification, squaring algorithms
and ...

The process "Track simplification" generally returns a new simplified track. 
Tolerance is in the unit of track observation coordinates.


  
Generic method
----------------

.. autofunction:: tracklib.algo.Simplification.simplify



Application
------------

We use the same sample track in the different examples. For loading the data:

.. code-block:: python

  from tracklib.io.TrackReader import TrackReader
  import tracklib.algo.Simplification as Simplification

  chemin = './data/lacet/ecrins.csv'
  tracks = TrackReader.readFromWkt(chemin, 0, 1, 2, ",", 1, 
                                    "ENUCoords", None, True)
  trace = tracks["903959","%"][0]
  trace = trace.extract(70,120)

  trace.summary()


Douglas-Peucker (1)
^^^^^^^^^^^^^^^^^^^

The Douglas-Peucker algorithm reduce the number of a line by reducing
the number of points. The result should keep the original shape.

Example:

.. code-block:: python

  tolerance = 20
  trace2 = Simplification.simplify(trace, tolerance,
             Simplification.MODE_SIMPLIFY_DOUGLAS_PEUCKER)
  trace.plot(append = False, sym='g-')
  trace2.plot(append = True, sym='b-')


.. figure:: ../../img/simplify_douglaspeucker.png
   :width: 450px
   :align: center

   Figure 2 : Simplification with Douglas Peucker


.. note:: Reference: David Douglas, Thomas Peucker: Algorithms for the
        reduction of the number of points required to represent a digitized
        line or its caricature. In Cartographica: The International Journal
        for Geographic Information and Geovisualization.
        Volume 10, Issue 2, Pages 112–122, 1973,
        `https://utpjournals.press/doi/10.3138/FM57-6770-U75U-7727 <https://utpjournals.press/doi/10.3138/FM57-6770-U75U-7727>`_



Visvalingram (2)
^^^^^^^^^^^^^^^^

The Visvalingram algorithm simplify the geometry of the track by reducing
the number of points but the result presents less angular results than
the Douglas-Peucker algorithm.

Example:

.. code-block:: python

  tolerance = 50
  trace3 = Simplification.simplify(trace, tolerance,
             Simplification.MODE_SIMPLIFY_VISVALINGAM)
  trace.plot(append = False, sym='g-', label='original track')
  trace3.plot(append = True, sym='b-', label='simplify:visvalingam')
  plt.legend()


.. figure:: ../../img/simplify_visvalingam.png
   :width: 450px
   :align: center

   Figure 1 : Simplification with Visvalingram

.. note:: Reference: M. Visvalingam & J. D. Whyatt (1993) Line generalisation by repeated elimination of points, The Cartographic Journal, 30:1, 46-51, DOI:
          `10.1179/000870493786962263 <10.1179/000870493786962263>`_


Squaring algorithm (3)
^^^^^^^^^^^^^^^^^^^^^^

Function to simplify a GPS track with squaring algorithm.

Example:

.. code-block:: python

  tolerance = 3
  trace1 = Simplification.simplify(trace, tolerance,
             Simplification.MODE_SIMPLIFY_SQUARING)
  trace.plot(append = False, sym='g-')
  trace1.plot(append = True, sym='b-')


.. figure:: ../../img/simplify_squaring.png
   :width: 450px
   :align: center

   Figure 3 : Simplification with squaring algorithm


.. note:: Reference: Lokhat, Imran & Touya, Guillaume. (2016).
          Enhancing building footprints with squaring operations.
          Journal of Spatial Information Science. 13.
          `10.5311/JOSIS.2016.13.276 <http://dx.doi.org/10.5311/JOSIS.2016.13.276>`_

