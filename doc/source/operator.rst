

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


Fonctions existantes et x(), y()



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

Simulate GPS data
--------------------

Generate analytical track

.. figure:: ./img/generate_random.png
   :width: 350px
   :align: center


Création d'une trace aléatoire (avec timestamps) suivant la forme d'une cardioïde + un bruit de type marche aléatoire:

.. figure:: ./img/generate.png
   :width: 350px
   :align: center


.. code-block:: python

   def x(t):
       return 10*math.cos(2*math.pi*t)*(1+math.cos(2*math.pi*t))
   def y(t):
       return 10*math.sin(2*math.pi*t)*(1+math.cos(2*math.pi*t))

   track = Track.generate(x,y)

   def prob():
       return random.random()-0.5

   track.operate(Operator.RANDOM, "", prob, "randx")
   track.operate(Operator.RANDOM, "", prob, "randy")

   track.operate(Operator.INTEGRATOR, "randx", "noisex")
   track.operate(Operator.INTEGRATOR, "randy", "noisey")

   track.operate(Operator.SCALAR_MULTIPLIER, "noisex", 0.5, "noisex")
   track.operate(Operator.SCALAR_MULTIPLIER, "noisey", 0.5, "noisey")

   track.operate(Operator.ADDER, "x", "noisex", "x_noised")
   track.operate(Operator.ADDER, "y", "noisey", "y_noised")

   kernel = GaussianKernel(21)

   track.operate(Operator.FILTER, "x_noised", kernel, "x_filtered")
   track.operate(Operator.FILTER, "y_noised", kernel, "y_filtered")

   plt.plot(track.getAnalyticalFeature("x"), track.getAnalyticalFeature("y"), 'k--')
   plt.plot(track.getAnalyticalFeature("x_noised"), track.getAnalyticalFeature("y_noised"), 'b-')
   plt.plot(track.getAnalyticalFeature("x_filtered"), track.getAnalyticalFeature("y_filtered"), 'r-')

   plt.show()







