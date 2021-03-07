

Operation classes for manipulating track
==========================================

La librairie tracklib propose une multitude d'opérateurs et de fonctions 
qui permettent de simplifier au maximum la création d'analytical features sur une trace. 
Les opérateurs opèrent aussi bien sur les coordonnées que sur le timestamp de la trace. 

.. with points of track
.. (containing operators and functions) 


Les opérations sur les points sont fournies et leur appel évite les parcours des points de la trace. 
Il est aussi possible de se créer son propore opérateur.


Ces opérateurs retournent aussi bien un attribut de la trace, un attribut du point ou une valeur pour la trace

.. which are relational, Boolean, logical, combinatorial, and bitwise,   (math-like expressions) 
.. work with one or more inputs to develop new values. Functions perform specialized tasks, such as computing slope from elevation, 
.. and they usually return numeric values. 
.. you don't have to be a programmer to know how to use operators and functions effectively, you just have to be taught how to use them
.. is a high-level computational language used for performing cartographic spatial analysis using raster da


Fonctions existantes: x(), y(), 

Fonctions à disposition: ds, speed, abs_curv

D'autres algorithmes dans : AlgoAF



Available operators
***********************

Unary void operator
----------------------

Binary void operator
----------------------


Unary operator
-----------------

.. Ces opérateurs permettent 

+------------+---------------------+-------------------------------+
| SUM        | Sum operator        | y = sum(x)                    |
+------------+---------------------+-------------------------------+
| AVERAGER   | Average operator    | y = mean(x)                   |
+------------+---------------------+-------------------------------+
| VARIANCE   |                     | y = Var(x)                    |
+------------+---------------------+-------------------------------+
| STDDEV     | Standard deviation  | y = sqrt(Var(x))              |
+------------+---------------------+-------------------------------+
| MSE        | Mean square         | y = mean(x**2)                |
+------------+---------------------+-------------------------------+
| RMSE       | Root mean square    | y = sqrt(mean(x**2))          |
+------------+---------------------+-------------------------------+
| MAD        |                     | y = median(abs(x))            |
+------------+---------------------+-------------------------------+
| MIN        |                     | y = min(x)                    |
+------------+---------------------+-------------------------------+
| MAX        |                     | y = max(x)                    |
+------------+---------------------+-------------------------------+
| MEDIAN     |                     | y = median(x)                 |
+------------+---------------------+-------------------------------+
| ARGMIN     |                     | y = min {t | x(t) = min(x)}   |
+------------+---------------------+-------------------------------+
| ARGMAX     |                     | y = min {t | x(t) = max(x)}   |
+------------+---------------------+-------------------------------+
| ZEROS      |                     | y = {t | x(t) = 0}            |
+------------+---------------------+-------------------------------+


Binary operator
-------------------


Scalar operator
-----------------


Scalar void operator
---------------------

.. Ces opérateurs permettent 

+---------------+---------------------+------------------------------------------------------------------------+
| SHIFT         |                     | y(t) = x(t-arg) with arg a integer                                     |
+---------------+---------------------+------------------------------------------------------------------------+
| APPLY         |                     | y(t) = arg(x(t)) with arg a real function                              |
+---------------+---------------------+------------------------------------------------------------------------+
| FILTER        |                     | y(t) = int[x(z)*h(t-z)dz] with arg an odd-dimension vector or a kernel |
+---------------+---------------------+------------------------------------------------------------------------+
| SCALAR_ADDER  |                     |                                                                        |
+---------------+---------------------+------------------------------------------------------------------------+
| RANDOM        |                     |                                                                        |
+---------------+---------------------+------------------------------------------------------------------------+
| THRESHOLDER   |                     |                                                                        |
+---------------+---------------------+------------------------------------------------------------------------+


Examples
***********


**TODO**

.. Simulate GPS data
.. --------------------

.. Generate analytical track

.. .. figure:: ./img/generate_random.png
..    :width: 350px
..    :align: center


.. Création d'une trace aléatoire (avec timestamp) suivant la forme d'une cardioïde + un bruit de type marche aléatoire:

.. .. figure:: ./img/generate.png
..   :width: 350px
..   :align: center





Operators statement syntax
*****************************

To create a new operator *nom_operateur*:

.. code-block:: python

   class nom_operateur (<type_operateur>):
       
	   def execute(self, track, af_input, kernel, af_output):
           temp = [0]*track.size()
           track.createAnalyticalFeature(af_output)
           utils.addListToAF(track, af_output, temp)
           return temp


Depends on what you want to create, **type_operateur** will specify your choice.




