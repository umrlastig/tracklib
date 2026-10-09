.. currentmodule:: algo.mapping


Mapping
========

.. py:module:: algo.mapping


This page presents four methods for mapping GNSS trajectories on geographic features like transport network
or inversement, mapping geographic features on GNSS trajectories like mnt or a another track.


.. autosummary::
   :nosignatures:

   mapOnNetwork
   mapOnRaster
   mapOn
   mapOnTrack


.. raw:: html

   <h3 style="background-color:#3A8EBA;color:#FFFFFF;padding:8px;">API Methods</h3>

- - - - - - - - - - - - - - - - - - - - - -


Map-match a track on a network
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. raw:: html

   <div style="background-color:#FFF6D4;padding:8px;">See the Jupyter notebook: <a href="https://tracklib.readthedocs.io/en/latest/howto/MAP_MapMatchingOnNetwork.html">Map-match a track on a network</a></div>
   <br/>

.. currentmodule:: algo.mapping

.. autofunction:: mapOnNetwork



Raster data transfer to track.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. raw:: html

   <div style="background-color:#FFF6D4;padding:8px;">See the Jupyter notebook: <a href="https://tracklib.readthedocs.io/en/latest/howto/MAP_MapOnRaster.html">Map DTM Data onto a GPS Track</a></div>
   <br/>

.. currentmodule:: algo.mapping

.. autofunction:: mapOnRaster


Geometric affine transformation to align two tracks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. raw:: html

   <div style="background-color:#FFF6D4;padding:8px;">See the Jupyter notebook: <a href="https://tracklib.readthedocs.io/en/latest/howto/MAP_MapOn.html">Align two tracks</a></div>
   <br/>

.. currentmodule:: algo.mapping

.. autofunction:: mapOn


Map observation coordinates on track
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. currentmodule:: algo.mapping

.. autofunction:: mapOnTrack
