:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 07/11/2022

TrackReader
=============

TrackReader class offers static methods to load track or track collection
from GPX, CSV or NMEA files. 
Geometry can be structured in coordinates or in a wkt.


CSV files
----------

Examples:

1. Load a track 
 
   .. code-block:: python
   
      from tracklib.core.GPSTime import GPSTime
      from tracklib.io.TrackReader import TrackReader as reader
      
      GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
      track = FileReader.readFromFile('./data/trace1.dat', 2, 3, -1, 4, srid="ENUCoords")
        
2. Load a track collection by specifying a directory in the variable 'path'.
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


API documentation:

.. automethod:: tracklib.io.TrackReader.TrackReader.readFromCsv




GPX files
----------

Example:

.. code-block:: python
        
   from tracklib.io.TrackReader import TrackReader
   from tracklib.core.GPSTime import GPSTime
   
   GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2s1Z")

   tracks = TrackReader.readFromGpx('../../../data/activity_5807084803.gpx')
   trace = tracks.getTrack(0)


API documentation:

.. automethod:: tracklib.io.TrackReader.TrackReader.readFromGpx



WKT files
----------

Example:

.. code-block:: python

   csvpath = os.path.join(self.resource_path, 'data/wkt/iti.wkt')
   TRACES = TrackReader.readFromWkt(csvpath, 0, -1, -1, "#", 1, "ENUCoords", None, True)


API documentation:

.. automethod:: tracklib.io.TrackReader.TrackReader.readFromWkt



NMA files
----------

API documentation:

.. automethod:: tracklib.io.TrackReader.TrackReader.readFromNMEA





