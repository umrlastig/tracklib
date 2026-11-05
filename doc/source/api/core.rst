

Core Package
-------------

.. grid:: 3
   :gutter: 3

   .. grid-item-card:: 📈 Track
      :link: ./core/track
      :link-type: doc

      Represents a single trajectory composed of ordered observations.

   .. grid-item-card:: 🗂️ TrackCollection
      :link: ./core/trackcollection
      :link-type: doc

      A collection of tracks.

   .. grid-item-card:: ◻️ Bounding Box
      :link: ./core/bbox
      :link-type: doc

      Axis-aligned spatial bounding box.

   .. grid-item-card:: 📍 Observation
      :link: ./core/obs
      :link-type: doc

      A single observation containing a position and a timestamp.

   .. grid-item-card:: 🕒 ObsTime
      :link: ./core/obstime
      :link-type: doc

      Representation and manipulation of observation timestamps.


.. grid:: 3
   :gutter: 2

   .. grid-item-card:: 🌍 GeoCoords
      :link: ./core/geocoords
      :link-type: doc

      Geographic coordinates (longitude, latitude, altitude).

   .. grid-item-card:: 🧭 ENUCoords
      :link: ./core/enucoords
      :link-type: doc

      Local East-North-Up coordinate system.

   .. grid-item-card:: 🌐 ECEFCoords
      :link: ./core/ecefcoords
      :link-type: doc

      Earth-Centered Earth-Fixed coordinate system.


.. grid:: 3
   :gutter: 2

   .. grid-item-card:: ∿ Kernels
      :link: ./core/kernel
      :link-type: doc

      Kernels for filtering, smoothing, and stochastic simulations.

   .. grid-item-card:: ƒ Operators
      :link: ./core/operator
      :link-type: doc

      Operators to perform computations on analytical features.


.. grid:: 3
   :gutter: 2

   .. grid-item-card:: ▤ SpatialIndex
      :link: ./core/spatialindex
      :link-type: doc

      Spatial index for efficient spatial queries.



.. grid:: 3
   :gutter: 2

   .. grid-item-card:: ● Node
      :link: ./core/node
      :link-type: doc

      A node (vertex) in a network.

   .. grid-item-card:: ━ Edge
      :link: ./core/edge
      :link-type: doc

      An edge connecting two nodes in a network.

   .. grid-item-card:: 🕸️ Network
      :link: ./core/network
      :link-type: doc

      A topological network composed of nodes and edges.



.. grid:: 3
   :gutter: 2

   .. grid-item-card:: 🗺️ AFMap
      :link: ./core/afmap
      :link-type: doc

      Represents an analytical feature as a collection of named value matrices.

   .. grid-item-card:: ▦ Raster
      :link: ./core/raster
      :link-type: doc

      Represents a collection of AFMaps, each describing a different analytical feature.

   .. grid-item-card:: 📊 AFBand
      :link: ./core/band
      :link-type: doc

      Represents an aggregate of matrix values, such as `sum`, `count`, or `avg`.


.. toctree::
  :maxdepth: 1
  :hidden:
  
  GeoCoords <./core/geocoords>
  ENUCoords <./core/enucoords>
  ECEFCoords <./core/ecefcoords>
  ObsTime <./core/obstime>
  Observation <./core/obs>
  Track <./core/track>
  Bounding Box <./core/bbox>
  TrackCollection <./core/trackcollection>
  Kernels <./core/kernel>
  Operators <./core/operator>
  SpatialIndex <./core/spatialindex>
  Node <./core/node>
  Edge <./core/edge>
  Network <./core/network>
  AFMap <./core/afmap>
  AFBand <./core/band>
  Raster <./core/raster>
