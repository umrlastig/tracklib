:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 12/12/2022

.. _examplestrackreader:


Read/Write track(s)
####################

Toutes les méthodes sont statiques dans la classe *TrackReader* pour la lecture 
et dans la classe *TrackWriter* pour écrire les données.


Loading track or track collection
=====================================

**tracklib** permet de charger des données GPS depuis un ou plusieurs fichiers de type CSV, GPX
et dont les géométries sont sous forme de coordonnées ou au format wkt. Le timestamp, s'il
existe peut-être fourni en format texte ou en time unix. Les AF peuvent être ou non chargées.
On peut aussi filtrer les données à charger. On peut aussi définir un template.



File or folder, GPX or CSV
-------------------------------

Arguably the most common type of resource is a file. You specify it using the path to the file.
To see all file import options, see :ref:`trackreader` in API Reference. 


#. Example for a GPX file ::

    import os
    from tracklib.core.ObsTime import ObsTime
    from tracklib.io.TrackReader import TrackReader
    
    ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
    resource_path = '/home/glagaffe/tracklib/data'
    filepath = os.path.join(resource_path, 'activity_5807084803.gpx')
    tracks = TrackReader.readFromGpx(filepath)
    tracks[0].plot()
    

#. Example for a CSV file ::

    import os
    from tracklib.core.ObsTime import ObsTime
    from tracklib.io.TrackReader import TrackReader

    ObsTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
    resource_path = '/home/glagaffe/tracklib/data'
    filepath = os.path.join(resource_path, 'trace10_mm.dat')
    track = TrackReader.readFromCsv(filepath, 2, 3, -1, 1, h=1)
    track.plot()
    
    
#. Example for a CSV file with a geometry structured in WKT 
   (track is associated with a linestring) ::

    import os
    from tracklib.core.ObsTime import ObsTime
    from tracklib.io.TrackReader import TrackReader

    resource_path = '/home/glagaffe/tracklib/data/wkt'
    csvpath = os.path.join(resource_path, 'iti.wkt')
    TRACES = TrackReader.readFromWkt(csvpath, id_geom=0, 
                                 separator="#", h=1, doublequote=True)
    print (len(TRACES))
    
    
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
    


Time field
-----------

Le format du champ time peut être défini de différentes façons dans les fichiers CSV:

- champ texte, on spécifie le format ::

    ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
    ObsTime.setReadFormat("2D/2M/4Y 2h:2m:2s")

- pas de champ time, -1 

    idT = -1


- Timestamp is in milliseconds ::

    PATH = '/home/marie-dominique/DATA/GPX/MOPSI/0/'
    dateInitiale = '1970-01-01 00:00:00'
    collection = reader.readFromCsv(path=PATH, id_E=1, id_N=0, id_T=2, 
                                      srid="GeoCoords",
                                      DateIni = GPSTime.readTimestamp(dateInitiale),
                                      selector = s,
                                      separator = ' ', verbose = True)


Crs field
----------

Pour les 3 méthodes d'import, *readFromGpx*, *readFromCsv* et *readFromWkt* 
vous pouvez préciser quel type de coordonnées vous avez: 

geographic coordinates ::

    srid="GeoCoords"
    # or
    srid = "GEO" 
    
or local projection (ENU or ENUCoords) ::

    srid="ENUCoords"
    # or
    srid="ENU"


Loading tracks with Analytical Features
----------------------------------------

If the CVS file contains AF, to load all of them ::

    ObsTime.setReadFormat("2D/2M/4Y 2h:2m:2s")
    chemin = os.path.join(self.resource_path, 'data/test/ecrins_interpol4.csv')
    track = TrackReader.readFromCsv(chemin, 0, 1, 2, 3, separator=";",read_all=True)


Select tracks inside a defined bounding box
--------------------------------------------

Load a track collection by specifying and a directory in the variable 'path'.
Timestamp is in milliseconds. Select only tracks inside a defined bounding box ::
   
   
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


Template
----------

First, it is necessary to define the template in resources/track_file_format ::

    RTKLIB    , pos, 2, 1, 3, 0, -1, bb, 1, %, -999999, GEO, 4Y/2M/2D 2h:2m:2s.3z, FALSE


Then to load the file ::

    resource_path = '/home/glagaffe/tracklib/data/'
    csvpath = os.path.join(resource_path, 'raw_gps.pos')
    gps = TrackReader.readFromCsv(csvpath, "RTKLIB") 
    print (gps.size())




Export track or track collection
==================================

* To export only the basics attributes of a track, position and timestamp ::

    csvpath = os.path.join(self.resource_path, 'data/test/test_write_csv_minim.wkt')
    TrackWriter.writeToFile(track, csvpath, id_E=0,id_N=1,id_U=2,id_T=3,h=1, separator=";")
        

* To export basic attributes and analytical features ::

    csvpath = os.path.join(self.resource_path, 'data/test/test_write_csv_2AF.wkt')
    af_names = ['speed', 'abs_curv']
    TrackWriter.writeToFile(track, csvpath, id_E=0, id_N=1, id_U=2, id_T=3, h=1, 
                               separator=";", af_names=af_names)


* Write one or many tracks in one or many GPX files ::

    TrackWriter.writeToGpx(self.collection, path=gpxpath, af=True, oneFile=False)


* Write in a KML ::

    kmlpath = os.path.join(self.resource_path, 'data/test/couplage.kml')
    TrackWriter.writeToKml(trace, path=kmlpath, type="LINE", af='speed')


