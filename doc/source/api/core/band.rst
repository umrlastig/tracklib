

.. currentmodule:: core.raster

AFBand
--------

.. autoclass:: Band
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~Band.__init__

   .. rubric:: Methods

   .. autosummary::
      
      ~Band.getName
      ~Band.getGrid
      ~Band.plot
      ~Band.histogram
      ~Band.setGrid

   .. rubric:: Static Methods

   .. autosummary::
      
      ~Band.initialize
      ~Band.accumulate
      ~Band.finalize

   
CountDistinctBand
------------------

.. autoclass:: CountDistinctBand
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~CountDistinctBand.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~CountDistinctBand.getCellUniqueValue
      ~CountDistinctBand.initialize
      ~CountDistinctBand.accumulate
      ~CountDistinctBand.finalize


CountBand
----------

.. autoclass:: CountBand
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~CountBand.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~CountBand.initialize
      ~CountBand.accumulate


MeanBand
----------

.. autoclass:: MeanBand
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~MeanBand.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~MeanBand.initialize
      ~MeanBand.accumulate
      ~MeanBand.finalize


SumBand
--------

.. autoclass:: SumBand
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~SumBand.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~SumBand.initialize
      ~SumBand.accumulate


MaxBand
----------

.. autoclass:: MaxBand
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~MaxBand.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~MaxBand.initialize
      ~MaxBand.accumulate


MinBand
----------

.. autoclass:: MinBand
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~MinBand.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~MinBand.initialize
      ~MinBand.accumulate


GridBand
----------

.. autoclass:: GridBand
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~GridBand.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~GridBand.initialize
      ~GridBand.accumulate


DominantBand
--------------

.. autoclass:: DominantBand
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~DominantBand.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~DominantBand.initialize
      ~DominantBand.accumulate
      ~DominantBand.finalize


MedianBand
------------

.. autoclass:: MedianBand
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~MedianBand.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~MedianBand.initialize
      ~MedianBand.accumulate
      ~MedianBand.finalize
      