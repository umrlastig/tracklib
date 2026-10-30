.. currentmodule:: core.spatial_index



Spatial Index
--------------

.. py:module:: core.spatial_index

.. autoclass:: SpatialIndex
   :members:
   :exclude-members: __addSegment, __addPoint, __getCell, __neighboringcells, __addCellValuesInTAB, __cellsCrossSegment
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~SpatialIndex.__init__

   .. rubric:: Methods

   .. autosummary::

      ~SpatialIndex.bbox
      ~SpatialIndex.covers
      ~SpatialIndex.addFeature
      ~SpatialIndex.removeFeature
      ~SpatialIndex.plot
      ~SpatialIndex.highlight
      ~SpatialIndex.request
      ~SpatialIndex.neighborhood
      ~SpatialIndex.groundDistanceToUnits
      ~SpatialIndex.__str__
      ~SpatialIndex.save

   .. rubric:: Static Methods

   .. autosummary::
      
      ~SpatialIndex.load

