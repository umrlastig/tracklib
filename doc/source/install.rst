:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 21/09/2020


Install
*********

Installing from source
==========================

1. You may install the latest development version by cloning the GitLab repository:

.. code-block:: shell

   git clone https://github.com/IGNF/tracklib.git
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
   
   
5 If you want to run unit tests, you have to install these dependencies:

.. code-block:: shell

   pip install pytest
   pip install pytest-runner
   pip install pytest-benchmark


6. If you want to generate the documentation, you have to install some dependencies are required:

.. code-block:: shell

   pip install sphinx
   pip install recommonmark
   pip install sphinx_rtd_theme

To launch the documentation:

.. code-block:: shell

   cd doc
   make html


7. A python IDE make the development more easy. To use spyder, you have to create a new project with an existing directory. 

.. container:: centerside
  
     .. figure:: ./img/spyder_project.png
        :width: 650px
        :align: center
      
        Figure 1 - Tracklib project in Spyder



.. |br| raw:: html

   <br />


Installing with pip
=====================

You can download it from PyPI repository using pip:

.. code-block:: shell
   
   TODO


