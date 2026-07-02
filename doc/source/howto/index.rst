:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 25/06/2026



Processing Guides
==================

This section contains practical guides for common Tracklib processing tasks.


Comparison
"""""""""""

..      Compare two trajectories and quantify their similarity.
..      Merge several trajectories into a representative track.


.. grid:: 2
   :gutter: 3

   .. grid-item-card:: Matching Two Tracks
      :link: COMP_Matching.html

      .. image:: ../_static/icons/match.png
         :width: 120px
         :align: center


   .. grid-item-card:: Aggregate Trajectories
      :link: COMP_Fusion.html

      .. image:: ../_static/icons/merge.png
         :width: 120px
         :align: center

.. toctree::
  :maxdepth: 1
  :hidden:

   Matching Two Tracks <COMP_Matching>
   Aggregate Trajectories <COMP_Fusion>
   

Filtering
""""""""""

.. toctree::
  :maxdepth: 1

   Apply a Band-Stop Fourier filter <FIL_Band-stopFourierFilter>


Interpolation
"""""""""""""""

.. toctree::
  :maxdepth: 1

   Interpolate a Track <INT_Interpolation>


Mapping
"""""""""""""""

.. toctree::
  :maxdepth: 1

   Map-Match a Track to a Network <MAP_MapMatchingOnNetwork>
   Map DTM Data onto a GNSS Track <MAP_MapOnRaster>
   Align two tracks <MAP_MapOn>


Segmentation
"""""""""""""""

.. toctree::
  :maxdepth: 1

   Segment a Track <SEG_Segmentation>
   Detect Return Trips <SEG_ReturnTrip>


Selection
"""""""""""""""

.. toctree::
  :maxdepth: 1

   Query a Track with SQL-like Commands <SEL_Query>
   Select GNSS Tracks <SEL_Selection>



Simplification
"""""""""""""""

.. toctree::
  :maxdepth: 1


   Simplify GNSS Tracks <SIMP_Simplification>


Summarizing
""""""""""""

.. toctree::
  :maxdepth: 1

   Build an Analytical Feature Map <SUM_AFMap>


Synthetic Tracks
""""""""""""""""""


.. grid:: 3
   :gutter: 2

   .. grid-item-card:: Generate Synthetic Tracks
      :link: SYN_Synthetics.html

      .. image:: ../_static/icons/synthetics.png
         :width: 120px
         :align: center


   .. grid-item-card:: Create a Realistic Synthetic Track
      :link: SYN_SyntheticRealistic.html

      .. image:: ../_static/icons/realistic.png
         :width: 120px
         :align: center


   .. grid-item-card:: Generate Tracks on a Network
      :link: SYN_SyntheticCollectionIssuedFromNetwork.html

      .. image:: ../_static/icons/netgen.png
         :width: 120px
         :align: center

.. toctree::
  :maxdepth: 1
  :hidden:

   Generate Synthetic Tracks <SYN_Synthetics>
   Create a Realistic Synthetic Track <SYN_SyntheticRealistic>
   Generate a TrackCollection from a Network <SYN_SyntheticCollectionIssuedFromNetwork>


.. Computing analytical features
.. Creating custom analytical features   
   
   



.. raw:: html

   <br />
   <br/>

