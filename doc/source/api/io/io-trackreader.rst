:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 11/11/2022

TrackReader
=============


CSV files
----------

.. automethod:: tracklib.io.TrackReader.TrackReader.readFromCsv


Examples
^^^^^^^^
        
1. Load a track collection by specifying a directory in the variable 'path'.
   Timestamp is in milliseconds.
   Select only tracks inside a defined bounding box.
   
   .. code-block:: python
   
      from tracklib.io.TrackReader import TrackReader as reader
      from tracklib.core.GPSTime import GPSTime
      from tracklib.core.Coords import ENUCoords
      import tracklib.algo.Geometrics as Geometrics
      from tracklib.algo.Selection import Constraint
      from tracklib.algo.Selection import TYPE_CUT_AND_SELECT, MODE_INSIDE
      from tracklib.algo.Selection import Selector   
   
      Xmin = 29.72
      Xmax = 29.77
      Ymin = 62.585
      Ymax = 62.615

      ll = ENUCoords(Xmin, Ymin)
      ur = ENUCoords(Xmax, Ymax)
      bbox = Geometrics.Rectangle(ll, ur)

      constraintBBox = Constraint(shape = bbox, mode = MODE_INSIDE, type=TYPE_CUT_AND_SELECT)
      s = Selector([constraintBBox])

      PATH = '/home/marie-dominique/DATA/GPX/MOPSI/0/'
      GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
      dateInitiale = '1970-01-01 00:00:00'
      collection = reader.readFromCsv(path=PATH, id_E=1, id_N=0, id_T=2, 
                                      srid="GeoCoords",
                                      DateIni = GPSTime.readTimestamp(dateInitiale),
                                      selector = s,
                                      separator = ' ', verbose = True)


GPX files
----------

Read from a GPX files

.. automethod:: tracklib.io.TrackReader.readFromGpx


WKT files
----------

Read from a CSV files with a wkt geometry


.. automethod:: tracklib.io.TrackReader.TrackReader.readFromWKTFile



NMA files
----------

.. automethod:: tracklib.io.TrackReader.readFromNMEAFile





Ancien
--------

.. automodule:: tracklib.io.TrackReader
    :members:
