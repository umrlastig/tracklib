

.. currentmodule:: core.kernel

Kernel
--------

.. autoclass:: Kernel
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~Kernel.__init__

   .. rubric:: Methods

   .. autosummary::
      
      ~Kernel.setFilterBoundary
      ~Kernel.filterBoundary
      ~Kernel.setFunction
      ~Kernel.getFunction
      ~Kernel.plot
      ~Kernel.evaluate
      ~Kernel.toSlidingWindow

   
DiracKernel
------------------

.. autoclass:: DiracKernel
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~DiracKernel.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~DiracKernel.__str__


UniformKernel
---------------

.. autoclass:: UniformKernel
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~UniformKernel.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~UniformKernel.__str__



TriangularKernel
-------------------

.. autoclass:: TriangularKernel
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~TriangularKernel.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~TriangularKernel.__str__



GaussianKernel
----------------

.. autoclass:: GaussianKernel
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~GaussianKernel.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~GaussianKernel.__str__


ExponentialKernel
-------------------

.. autoclass:: ExponentialKernel
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~ExponentialKernel.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~ExponentialKernel.__str__


CubicKernel
-------------

.. autoclass:: CubicKernel
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~CubicKernel.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~CubicKernel.__str__



SphericKernel
---------------

.. autoclass:: SphericKernel
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~SphericKernel.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~SphericKernel.__str__


EpanechnikovKernel
---------------------

.. autoclass:: EpanechnikovKernel
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~EpanechnikovKernel.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~EpanechnikovKernel.__str__


SincKernel
------------

.. autoclass:: SincKernel
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~SincKernel.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~SincKernel.__str__


ExperimentalKernel
--------------------

.. autoclass:: ExperimentalKernel
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Constructor

   .. autosummary::
      
      ~ExperimentalKernel.__init__
   
   .. rubric:: Methods

   .. autosummary::

      ~ExperimentalKernel.__str__
      ~ExperimentalKernel.addTrackPair
      ~ExperimentalKernel.addTrackCollection
      ~ExperimentalKernel.addDifferenceProfile
      ~ExperimentalKernel.plot

