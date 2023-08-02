:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 21/09/2020


Installation
============

Tracklib is supported on Python versions 3.8+.


Dependencies
~~~~~~~~~~~~

The following projects are required dependencies of Tracklib:

* `NumPy <https://pypi.org/project/numpy/>`_ - NumPy for data arrays access.
* `matplotlib <https://pypi.org/project/matplotlib/>`_ - Used for colormaps and 2D plotting.
* `scikit-image <https://pypi.org/project/scikit-image/>`_ - Used for image processing in Python.
* `progressbar2 <https://pypi.org/project/progressbar2/>`_ - A progress bar to display the progress of a long running operation.


PyPI
~~~~

.. image:: https://img.shields.io/pypi/v/tracklib.svg?logo=python&logoColor=white
   :target: https://pypi.python.org/pypi/tracklib/

Tracklib can be installed from `PyPI <https://pypi.org/project/tracklib/>`_
using ``pip``::

    pip install tracklib


Installing the Current Development Branch from GitHub in current environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To install ``tracklib`` from the latest up-to-date development branch from github, 
use one of the following:

.. code::

   pip install -U git+https://github.com/umrlastig/tracklib.git@main

Alternatively, you can clone the repository with git and install it with pip.

.. code::

   git clone https://github.com/umrlastig/tracklib.git
   cd tracklib
   pip install -e .


Installing the Current Development Branch from GitHub in a new python environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. You may install the latest development version by cloning the GitLab repository:

.. code-block:: shell

   git clone https://github.com/umrlastig/tracklib.git
   cd tracklib


2. Then you can create a new environment:

.. code-block:: shell

   [sudo apt-get install python3-venv]
   python3 -m venv tracklibenv
   source tracklibenv/bin/activate


3. You have to install required dependencies:

.. code-block:: shell

   pip install --upgrade pip
   pip install wheel
   pip install setuptools
   pip install twine


4. You may using pip to install tracklib from the local directory

.. code-block:: shell

   pip install -e .
   python setup.py install
 
 
5. Later, if you want to quit

.. code-block:: shell
   
   deactivate
 

Running test
~~~~~~~~~~~~
   
If you want to run unit tests, you have to install these dependencies:

.. code-block:: shell

   pip install pytest
   pip install pytest-runner
   pip install pytest-benchmark
   pip install coverage


Running documentation
~~~~~~~~~~~~~~~~~~~~~

If you want to generate the documentation, you have to install some dependencies are required:

.. code-block:: shell

   pip install sphinx
   pip install recommonmark
   pip install sphinx_rtd_theme
   pip install sphinx-autodoc-typehints


To launch the documentation:

.. code-block:: shell

   cd doc
   make html



Spyder IDE
~~~~~~~~~~

A python IDE make the development more easy. 

.. code-block:: shell

   pip install spyder
   pip install spyder-kernels
   spyder &


To use spyder, you have to create a new project with an existing directory. 

.. container:: centerside
  
     .. figure:: ../img/spyder_project.png
        :width: 650px
        :align: center
      
        Figure 1 - Tracklib project in Spyder



.. |br| raw:: html

   <br />
   



   




