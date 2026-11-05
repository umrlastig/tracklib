:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 21/09/2020


Install as an editable library
===============================

Tracklib supports Python 3.8 and later.


Dependencies
~~~~~~~~~~~~

Tracklib depends on the following Python packages:

* `numpy <https://pypi.org/project/numpy/>`_ – Provides efficient array operations.
* `matplotlib <https://pypi.org/project/matplotlib/>`_ – Used for colormaps and 2D plotting.
* `progressbar2 <https://pypi.org/project/progressbar2/>`_ – Displays the progress of long-running operations.
* `rtree <https://pypi.org/project/rtree/>`_ – Python bindings for libspatialindex, used for spatial indexing.
* `requests <https://pypi.org/project/requests/>`_ – Used to query HTTP web services.




Option 1: Installing from GitHub
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install the latest development version directly from GitHub, run:

.. code::

   pip install -U git+https://github.com/umrlastig/tracklib.git@main

Alternatively, you can clone the repository with git and install it with pip.

.. code::

   git clone https://github.com/umrlastig/tracklib.git
   cd tracklib
   pip install -e .



Option 2: Installing in a New Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Clone the GitHub repository:

.. code-block:: shell

   git clone https://github.com/umrlastig/tracklib.git
   cd tracklib


2. Create and activate a new virtual environment:

.. code-block:: shell

   [sudo apt-get install python3-venv]
   python3 -m venv tracklibenv
   source tracklibenv/bin/activate


3. Upgrade the packaging tools:

.. code-block:: shell

   pip install --upgrade pip
   pip install wheel
   pip install setuptools
   pip install twine


4. Install Tracklib in editable mode:

.. code-block:: shell

   pip install -e .
 
 
5. Deactivate the virtual environment when you're done:

.. code-block:: shell
   
   deactivate
 




.. |br| raw:: html

   <br />
   



   




