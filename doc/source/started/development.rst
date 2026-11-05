:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 21/09/2020


Development
============


Running Tests
~~~~~~~~~~~~~~
   
To run the unit tests, install the following packages:

.. code-block:: shell

   pip install pytest
   pip install pytest-runner
   pip install pytest-benchmark
   pip install coverage



Running documentation
~~~~~~~~~~~~~~~~~~~~~

To build the documentation, install the following packages:

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
~~~~~~~~~~~

Spyder can be used as an IDE for Tracklib development.

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


Make sure the Tracklib directory is included in Spyder's Python path.



.. |br| raw:: html

   <br />
   



   




