

Operation classes for manipulating track
==========================================

La librairie tracklib propose une multitude d'opérateurs et de fonctions (containing operators and functions) 
qui permettent de simplifier au maximum la création d'analytical features sur une trace with points of track.. 
Les opérateurs opèrent aussi bien sur les coordonnées que sur le timestamp de la trace. Il est aussi possible de se créer son propore opérateur.
Les opérations sur les points sont fournies et leur appel évite les parcours des points de la trace.

Ces opérateurs retournent aussi bien une valeur qu'un attribut de la trace ou un attribut du point

which are relational, Boolean, logical, combinatorial, and bitwise,   (math-like expressions) 

work with one or more inputs to develop new values. Functions perform specialized tasks, such as computing slope from elevation, 
and they usually return numeric values. 


You don't have to be a programmer to know how to use operators and functions effectively, you just have to be taught how to use them
is a high-level computational language used for performing cartographic spatial analysis using raster da


Operators statement syntax
*****************************

Pour créer un nouvel opérateur:


.. code-block:: python

   class <nom_operateur>(<type_operateur>):
       
	   def execute(self, track, af_input, kernel, af_output):
           temp = [0]*track.size()
           track.createAnalyticalFeature(af_output)
           utils.addListToAF(track, af_output, temp)
           return temp


Depends on what you want to create, **type_operateur** will specify your choice.








Functions disponibles
***********************

Unary void operator
----------------------



Unary operator
-----------------

* SUM : Sum operator (y = sum(x))
* AVERAGER: Average operator (y = mean(x))
* VARIANCE: (y = Var(x))
* STDDEV = StdDev()							 # y = sqrt(Var(x))
* MSE = Mse()									 # y = mean(x**2)
* RMSE = Rmse()								 # y = sqrt(mean(x**2))
* MAD = Mad()								 	 # y = median(|x|)
* MIN = Min()									 # y = min(x)
* MAX = Max()									 # y = max(x)
* MEDIAN = Median()							 # y = median(x)
* ARGMIN = Argmin()							 # y = min {t | x(t) = min(x)}
* ARGMAX = Argmax()							 # y = min {t | x(t) = max(x)}
* ZEROS = Zeros()								 # y = {t | x(t) = 0}


Scalar void operator
---------------------

Ces opérateurs permettent 

* SHIFT: y(t) = x(t-arg) with arg a integer
* APPLY: y(t) = arg(x(t)) with arg a real function
* FILTER: y(t) = int[x(z)*h(t-z)dz] with arg an odd-dimension vector or a kernel
* SCALAR_ADDER: 
* RANDOM
* THRESHOLDER

Examples
***********

Slope
---------



Turning function, sinuosity ?
------------------------------




