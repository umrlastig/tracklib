:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 21/09/2020



Run tracklib as an 3rd party python library for QGIS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Check in the QGIS Python Console with which version of python, Qgis runs. To find out where: 

.. code-block:: python

   import sys
   sys.executable


.. code-block:: shell
   
   >> '/usr/bin/python3'


2. Then install dependencies in linux console:

.. code-block:: shell

   /usr/bin/python3 -m pip install -r /home/glagaffe/tracklib/requirements.txt


3. At the end, add tracklib to the python system path:

.. code-block:: shell

   sys.path.append('/home/glagaffe/tracklib')
