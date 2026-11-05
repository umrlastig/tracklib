.. currentmodule:: algo.comparison


Comparison 
==========

.. py:module:: algo.comparison

This page presents three methods for comparing and aggregating trajectories based on distance or pseudo-distance measures:

.. autosummary::
   :nosignatures:

   compare
   match
   fusion


.. raw:: html

   <h3 style="background-color:#3A8EBA;color:#FFFFFF;padding:8px;">Parameters Common to Most Methods</h3>

- - - - - - - - - - - - - - - - - - - - - -


Considering a set of trajectories, where each trajectory is defined as :
    an 𝑛 ordered points: X = (x𝑖 )𝑖=1..𝑛 , with x𝑖 ∈ R2 and GPS records in a 2D space.

Let 𝑑 be a distance (Euclidian, Manhattan, etc.) between those points: 
    𝑑 : R2 ×R2 → R+ 


Parameter ``dim``
^^^^^^^^^^^^^^^^^^

Note that heights and timestamps for example, could also be considered with x𝑖 , y𝑖 ∈ R3 or R4 , and defining 𝑑 accordingly to measure distance between three-dimensional timestamped records.

The parameter ``dim`` represents the dimension of records. Possible values for *dim* are:

- dim = 1: 1D altimetric euclidian distance
- dim = 2: 2D planimetric euclidian distance
- dim = 3: 3D distance euclidian distance
- lambda function between ENUCoords: direct application of lambda function


Parameter ``p``
^^^^^^^^^^^^^^^^

Some matching methods use distance measures based on the :math:`L_p`-norm.

In these cases, ``p`` specifies the norm used to compute the distance, with :math:`p \in \{1, 2, \infty\}`.


For example, in :math:`\mathbb{R}^n`:

.. math::

   \|x\|_p = \left(\sum_{i=1}^{n}|x_i|^p\right)^{1/p}

where:

- :math:`n` is the **dimension of the space**;
- :math:`p` is the **parameter defining the norm**.

Thus:

- :math:`p=1` → **Manhattan norm**;
- :math:`p=2` → **Euclidean norm**;
- :math:`p=\infty` → **Chebyshev norm** (or **infinity norm**), corresponding to the maximum absolute coordinate value: :math:`|x|\infty = \max{1 \leq i \leq n} |x_i|`


.. raw:: html

   <h3 style="background-color:#3A8EBA;color:#FFFFFF;padding:8px;">API Methods</h3>

- - - - - - - - - - - - - - - - - - - - - -


Comparison of two tracks
^^^^^^^^^^^^^^^^^^^^^^^^

Compare two tracks to measure a distance between them. List of available distances to compare two tracks are listed below. The three last columns indicate:

- [p] : Methods indexed by [p] are parameterized with Lp norm (default p = 1)
- [m] : Methods indexed by [m] are based on the output of a matching
- [s] : Methods indexed by [s] are symetric (compare(t1, t2) = compare(t2, t1))

.. list-table::
   :header-rows: 1
   :widths: 20 40 3 3 3

   * - Mode
     - Description
     - [p]
     - [m]
     - [s]
   * - ``MODE_COMPARISON_POINTWISE``
     - Distances btw points at each index
     - Yes
     - Yes
     - Yes
   * - ``MODE_COMPARISON_NN``
     - Distances between nearest neighbours. No have distance property.
     - Yes
     - Yes
     - No
   * - ``MODE_COMPARISON_HAUSDORFF``
     - Haussdorf distance
     - No
     - No
     - Yes
   * - ``MODE_COMPARISON_DI_HAUSDORFF``
     - Directed Hausdorff distance from A to B
     - No
     - No
     - No
   * - ``MODE_COMPARISON_AREAL``  
     - Mac Master aeral distance. It is a semi distance.
     - No
     - No
     - Yes
   * - ``MODE_COMPARISON_RADIAL``
     - Radial distance (for closed loops). It is a pseudo-distance.
     - No
     - No
     - Yes
   * - ``MODE_COMPARISON_DTW``
     - Distances between DTW pairs. It is a semi-distance.
     - Yes
     - Yes
     - Yes
   * - ``MODE_COMPARISON_FDTW``
     - Distances between FDTW pairs. It is a semi-distance.
     - Yes
     - Yes
     - Yes
   * - ``MODE_COMPARISON_FRECHET``
     - Distance between Frechet pairs.
     - No
     - Yes
     - Yes 
   * - ``MODE_COMPARISON_SYNC`` 
     - Time-synchronized comparison.
     - Yes
     - Yes
     - Yes


.. currentmodule:: algo.comparison

.. autofunction:: compare


Matching two tracks
^^^^^^^^^^^^^^^^^^^^

.. raw:: html

   <div style="background-color:#FFF6D4;padding:8px;">See the Jupyter notebook: <a href="https://tracklib.readthedocs.io/en/latest/howto/COMP_Matching.html">Matching two tracks</a></div>
   <br/>

.. currentmodule:: algo.comparison

.. autofunction:: match


Tracks aggregation
^^^^^^^^^^^^^^^^^^^

.. raw:: html

   <div style="background-color:#FFF6D4;padding:8px;">See the Jupyter notebook: <a href="https://tracklib.readthedocs.io/en/latest/howto/COMP_Fusion.html">Aggregating trajectories</a></div>
   <br/>

.. currentmodule:: algo.comparison

.. autofunction:: fusion

