:Author: Marie-Dominique Van Damme
:Version: 1.1
:License: --
:Date: 04/08/2023


Write python's code with tracklib in QGIS (ubuntu)
===================================================

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

  
   
   

