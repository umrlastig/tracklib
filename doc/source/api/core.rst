

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



.. toctree::
  :maxdepth: 1
  :hidden:
  
  GeoCoords <./core/geocoords>
  ENUCoords <./core/enucoords>
  ECEFCoords <./core/ecefcoords>
  Bounding Box <./core/bbox>
  ObsTime <./core/obstime>
  Observation <./core/obs>
  Track <./core/track>
  TrackCollection <./core/trackcollection>