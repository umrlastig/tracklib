:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 07/03/2021


Simplification of GPS tracks
=============================

The process "Track simplification" returns a new track. Tolerance is in the unit of track observation coordinates.


Douglas Peucker Simplication
*******************************


Ref: Algorithms for the Reduction of the Number of Points Required to Represent a Digitized Line or its Caricature. 
David H. Douglas
Thomas K. Peucker
https://utpjournals.press/doi/10.3138/FM57-6770-U75U-7727



Visvalingram Simplification
********************************

Line generalisation by repeated elimination of points - https://www.tandfonline.com/doi/abs/10.1179/000870493786962263




Kernel simplification
*************************

Build a kernel:

For example a Gaussian Filter:

.. code-block:: python

   kernel = GaussianKernel(201)
   track.operate(Operator.FILTER, "x", kernel, "x2")
   track.operate(Operator.FILTER, "y", kernel, "y2")
   plt.plot(track.getT(), track.getAnalyticalFeature("y"), 'b-', markersize=1.5)
   plt.plot(track.getT(), track.getAnalyticalFeature("y2"), 'r-')
   plt.show()

