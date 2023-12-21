:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 07/03/2021


Welcome to tracklib’s documentation!
=====================================

.. image:: img/TracklibLogo.png
  :width: 200
  :align: center
  

**tracklib** is a Python library that provides a variety of tools, operators and functions to manipulate GPS trajectories.

:View the source code of tracklib: https://github.com/umrlastig/tracklib


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
Currently available Python libraries for trajectories can separately load, simplify, interpolate, summarize or visualize them. 
But, as far as we know, there is no Python library that would contain all these basic functionalities. 
This is what *tracklib* is modestly trying to do. The library provides some conventions, capabilities and techniques to manipulate GPS trajectories.


In *tracklib*, the core model supports a wide range of trajectory applications: 

1. trajectory can be seen as a concept of (geo)located timestamps sequence to study for example an athlete's performance,
2. trajectory can be seen as a concept of a curve which makes it possible to study trajectory shapes, 
3. a full trajectory dataset can be reduced into a regular grid of summarized features, 
4. with map matching process, trajectories can be seen as a network of routes.


Furthermore, adding analytical features (e.g. speed, curvilinear abscissa, inflection point, heading, acceleration, speed change, etc.) 
on a observation or on all observations of a trajectory (function of coordinates or timestamp) is, in general, a complex 
and a boring task. So, to make it easier, *Tracklib* module offers a multitude of operators and predicates 
to simplify the creation of analytical features on a GPS tracks.   



Documentation
**************

.. toctree::
  :maxdepth: 2
  
  Getting Started <started/index>
  User Guide <userguide/index>
  Use Cases <usecase/index>
  API Reference <api/index>




.. Main functionalities
.. *********************

.. * Structured data to store GPS data
.. * Load GPS data from files (GPX, CSV) 
.. * Operation classes for manipulating track
.. * Propose generic method to simplify a track. For example (Douglas Peucker, 
.. Visvalingram algorithms or kernel Filter (Gaussian, Uniform, Dirac, etc.)).
.. * Resample, interpolation and smoothing functions
.. * Summarize GPS information into a grid


