:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 01/04/2022


Bird's eye view on Tracklib
============================

The aim of this page is to give you a high level overview of how Tracklib works: an introduction 
of the description of the four packages that make up Tracklib Framework.

.. figure:: ./img/DIAG_COMPOSANT_v2.png
   :width: 550px
   :align: center
   
   Package diagram of Tracklib framework


Core 
------

	Definition and implementation of central classes of Tracklib framework: Track, TrackCollection, etc. 
	
	=================== ====================================================================
	Module                Purpose
	=================== ====================================================================
	``Bbox``             Class to manage bounding box
	``Coords``           Classes to manage point coordinates: GeoCoords, ENUCoords, ECEFCoords
	``GPSTime``          Class to manage timestamps
	``Grid``             Class for defining a spatial grid
	``Kernel``           Kernel Class for filtering, smoothing and stochastics simulations
 	``Network``          Node, Edge and Network Class 
	``Obs``              Class to define an observation
	``Operator``         Classes to manage the operators
	``Plot``             Class to plot GPS tracks and its AF
	``Raster``           Class to manipulate rasters
	``SpatialIndex``     Class to manipulate a spatial Index
	``Track``            Class to manage GPS tracks
	``TrackCollection``  Class to manage a collection of tracks
	=================== ====================================================================


IO
----
	Implements for reading and/or writting tracks and networks in CSV, GPX, KML, ASCII file.


Algo
------

	Algorithms implementation for manipulate track like: interpolate, smoothing, segmentation, 
	filtering, simplify, compare, mapping on another track or on network
	
	================== ====================================================================
	Module                Purpose
	================== ====================================================================
	``Analytics``       Functions to compute Analytical Features like speed, ds, abs_curv, etc.
	``Cinematics``      Functions to manage cinematic computations on GPS tracks
	``Comparison``	    Functions to manage comparisons of GPS tracks
	``Dynamics``	    Functions to manage cinematic computations on GPS tracks
	``Filtering``	    Functions to manage filtering of GPS tracks
	``Geometrics``	    Functions to manage general operations on a track
	``Interpolation``	   
	``Mapping``	   	
	``Segmentation``    Functions to manage segmentation of GPS tracks
	``Selection``
	``Simplification``  Functions to manage simplification of GPS tracks
	``Stochastics``
	``Summarising``
	``Synthetics``
	================== ====================================================================


Util
------

	Tools like geometry functions or color function for the visualization
	
	================== ====================================================================
	Module                Purpose
	================== ====================================================================
	``Geometry`` 	    Geometric functions
	================== ====================================================================


