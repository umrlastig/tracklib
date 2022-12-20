:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 12/12/2022

.. _examplestrackreader:


Read/Write track(s)
####################

Toutes les méthodes sont statiques et dans la classe *TrackReader* pour la lecture 
et dans la classe *TrackWriter*.


Loading track or track collection
=====================================

**tracklib** permet de charger des données GPS depuis un ou plusieurs fichier de type CSV, GPX
et dont les géométries sont sous forme de coordonnées ou au format wkt. Le timestamp, s'il
existe peut-être fourni en format texte ou en time unix. Les AF peuvent être ou non chargées.
On peut aussi filtrer les données à charger. On peut aussi définir un template.



File or folder, GPX or CSV
-------------------------------

Arguably the most common type of resource is a file. You specify it using the path to the file.
To see all file import options, see API Reference :ref:`trackreader`. 


#. Example for a GPX file ::

    import os
    from tracklib.core.ObsTime import ObsTime
    from tracklib.io.TrackReader import TrackReader
    
    ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
    resource_path = '/home/glagaffe/tracklib/data'
    path = os.path.join(resource_path, 'activity_5807084803.gpx')
    tracks = TrackReader.readFromGpx(path)
    tracks[0].plot()
    

#. Example for a CSV file ::

    import os
    from tracklib.core.ObsTime import ObsTime
    from tracklib.io.TrackReader import TrackReader

    ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
    resource_path = '/home/glagaffe/tracklib/data'
    chemin = os.path.join(resource_path, 'trace10_mm.dat')
    track = TrackReader.readFromCsv(chemin, 2, 3, -1, 1, h=1)
    track.plot()
    
    
#. If you have a list of CVS files in a folder ::

    from tracklib.core.ObsTime import ObsTime
    from tracklib.io.TrackReader import TrackReader
    
    ObsTime.setReadFormat("2D/2M/4Y 2h:2m:2s")
    resource_path = '/home/glagaffe/tracklib/data/test/csv'
    collection = TrackReader.readFromCsv(resource_path, 1, 2, -1, -1)
    print (collection.size(), ' CSV tracks loaded')
    
    
#. If you have a list of GPX files in a folder ::

    from tracklib.core.ObsTime import ObsTime
    from tracklib.io.TrackReader import TrackReader

    resource_path = '/home/glagaffe/tracklib/data/gpx/geo'
    ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
    tracks = TrackReader.readFromGpx(resource_path)
    print (collection.size(), ' GPX tracks loaded')
    

#. WKT


.. code-block:: python

   csvpath = os.path.join(self.resource_path, 'data/wkt/iti.wkt')
   TRACES = TrackReader.readFromWkt(csvpath, 0, -1, -1, "#", 1, "ENUCoords", None, True)


    
    
Position and Time
--------------------

1. Load a track 
 
   .. code-block:: python
   
      from tracklib.core.GPSTime import GPSTime
      from tracklib.io.TrackReader import TrackReader as reader
      
      GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
      track = FileReader.readFromFile('./data/trace1.dat', 2, 3, -1, 4, srid="ENUCoords")


Arguably the most common type of resource. You specify it using the path to the
file, e.g. ::

    img = iio.imread("path/to/my/image.jpg")  # relative path
    img = iio.imread("/path/to/my/image.jpg")  # absolute path on Linux
    img = iio.imread("C:\\path\\to\\my\\image.jpg")  # absolute path on Windows


Notice that this is a convenience shorthand (since it is so common).
Alternatively, you can use the full URI to the resource on your disk ::

    img = iio.imread("file://path/to/my/image.jpg")
    img = iio.imread("file:///path/to/my/image.jpg")
    img = iio.imread("file://C:\\path\\to\\my\\image.jpg")



AF
-----

Arguably the most common type of resource. You specify it using the path to the
file, e.g. ::

    img = iio.imread("path/to/my/image.jpg")  # relative path
    img = iio.imread("/path/to/my/image.jpg")  # absolute path on Linux
    img = iio.imread("C:\\path\\to\\my\\image.jpg")  # absolute path on Windows


Filter
---------

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

Arguably the most common type of resource. You specify it using the path to the
file, e.g. ::

    img = iio.imread("path/to/my/image.jpg")  # relative path
    img = iio.imread("/path/to/my/image.jpg")  # absolute path on Linux
    img = iio.imread("C:\\path\\to\\my\\image.jpg")  # absolute path on Windows



Template
----------

Example:

.. code-block:: python
        
   from tracklib.io.TrackReader import TrackReader
   from tracklib.core.GPSTime import GPSTime
   
   GPSTime.setReadFormat("4Y-2M-2DT2h:2m:2s1Z")

   tracks = TrackReader.readFromGpx('../../../data/activity_5807084803.gpx')
   trace = tracks.getTrack(0)






Export track or track collection
=====================================

blabla

