:Author: Marie-Dominique Van Damme
:Version: 1.1
:License: --
:Date: 04/08/2023


.. Write python's code with tracklib in QGIS (ubuntu)

Coding with tracklib in QGIS (ubuntu)
=====================================

If you want to run ``tracklib`` as an 3rd party python library for QGIS, it's possible. First you have to configure QGis environment, 
then you can test if the example below.


Set environment
~~~~~~~~~~~~~~~

1. Install tracklib

.. code-block:: python

   pip install tracklib


2. Check in the QGIS Python Console with which version of python, Qgis runs. To find out where: 

.. code-block:: python

   import sys
   sys.executable

.. code-block:: shell
   
   >> '/usr/bin/python3'

3. Then install dependencies in linux console:

.. code-block:: shell

   /usr/bin/pip3 install tracklib

4. At the end, check if the python's site-packages directory is in the qgis path:

* The location of python's site-packages directory can be found using:

.. code-block:: shell

   /usr/bin/python3 -m site --user-site

* Open QGis desktop, then the python console

* Display the QGis system path:

.. code-block:: shell

    print (sys.path)
 
* if the python's site-packages directory is not in the QGis system path, add it like this:

.. code-block:: shell

   sys.path.append('here_python's site-packages directory')
   

Run the example
~~~~~~~~~~~~~~~

The example load a CSV file containing routes (geometry defined by a wkt) and display it in QGis desktop.


.. code-block:: python
   
	import tracklib as tkl

	csvpath = '/home/glagaffe/tracklib/tracklib/data/lacet/ecrins.csv'
	tracks = tkl.TrackReader.readFromWkt(csvpath, 0, 1, 2, ",", 1, "ENUCoords", None, True)

	trace = tracks["917262","%"][0].extract(22, 180)
	trace.resample(5, tkl.MODE_SPATIAL)

	vqgis = tkl.QgisVisitor()
	trace.plotAsMarkers(v=vqgis)
	


The result looks like this:

.. container:: centerside
  
   .. figure:: ../img/visu_qgis.png
      :width: 500px
      :align: center
		
      Display a track computed by tracklib in QGis
	




.. /usr/bin/pip3 install tracklib
.. /usr/bin/python3 /home/marie-dominique/TestImport.py
 

