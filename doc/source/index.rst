:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 07/03/2021


Welcome to tracklib’s documentation!
=====================================

**tracklib** is a Python library that provides a variety of tools, operators and functions to manipulate GPS trajectories.

:Source Code: https://github.com/umrlastig/tracklib

|TracklibBuildTest| |codecov| |rtd| |licence|

.. |TracklibBuildTest| image:: https://github.com/umrlastig/tracklib/actions/workflows/ci.yml/badge.svg
                  :alt: Tracklib build & test
                  :target: https://github.com/umrlastig/tracklib/actions/workflows/ci.yml
.. |codecov| image:: https://codecov.io/gh/umrlastig/tracklib/branch/main/graph/badge.svg?token=pHLaV21j2O
                   :alt: Code coverage
                   :target: https://codecov.io/gh/umrlastig/tracklib
.. |rtd| image:: https://readthedocs.org/projects/tracklib/badge/?version=latest
               :alt: Documentation status
               :target: https://tracklib.readthedocs.io/en/latest/?badge=latest
.. |licence| image:: https://img.shields.io/badge/Licence-Cecill--C-blue.svg?style=flat
                   :alt Software License
				   :target https://github.com/umrlastig/tracklib/blob/main/LICENCE

Background
***********

More and more datasets of GPS trajectories are now available and they are studied very frequently in many scientific domains. 
Python libraries for trajectories are available to load, simplify, interpolate, summarize and visualize them. 
But there is no Python library that would contain all these basic functionality.  

Furthermore, adding analytical features on a observation or on all observation of a trajectory (function of coordinates or timestamp) 
is, in general, a complex and a boring task. So, to make it easier, *Tracklib* module offers a multitude of operators 
and functions to simplify the creation of analytical features on a GPS tracks. 


Main functionalities
*********************

* Structured data to store GPS data
* Load GPS data from files (GPX, CSV) 
* Operation classes for manipulating track
* Propose generic method to simplify a track. For example (Douglas Peucker, 
  Visvalingram algorithms or kernel Filter (Gaussian, Uniform, Dirac, etc.)).
* Resample, interpolation and smoothing functions
* Summarize GPS information into a grid


Documentation
**************

.. toctree::
  :maxdepth: 2
  
  User Guide <userguide/index>
  Use Cases <notebook/index>
  API Reference <api/index>




