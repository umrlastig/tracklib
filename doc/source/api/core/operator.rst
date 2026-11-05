

.. currentmodule:: core.operators


Operators
----------

Operators to perform computations on analytical features.


UnaryOperator
^^^^^^^^^^^^^^

.. autoclass:: UnaryOperator
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Methods

   .. autosummary::
      
      ~UnaryOperator.execute

Min

Max

Argmin

Argmax

Median

Zeros

Sum

Averager

Variance

StdDev

Mse

Rmse

Mad




BinaryOperator
^^^^^^^^^^^^^^^

.. autoclass:: BinaryOperator
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Methods

   .. autosummary::

      ~BinaryOperator.execute


Covariance

Correlation

L0Diff

L1Diff

L2Diff

LInfDiff

Equal




UnaryVoidOperator
^^^^^^^^^^^^^^^^^^^

.. autoclass:: UnaryVoidOperator
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Methods

   .. autosummary::

      ~UnaryVoidOperator.execute


Identity

Integrator

Differentiator

ForwardFiniteDiff

BackwardFiniteDiff

CenteredFiniteDiff

SecondOrderFiniteDiff

ShiftRight

ShiftCircularRight

ShiftLeft

ShiftCircularLeft

Inverter

Inverser

Reverser

Rectifier

Debiaser

Normalizer

Square

Sqrt

Diode

Sign

Exp

Log

Cos

Sin

Tan




BinaryVoidOperator
^^^^^^^^^^^^^^^^^^^

.. autoclass:: BinaryVoidOperator
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Methods

   .. autosummary::

      ~BinaryVoidOperator.execute

Adder

Substracter

Multiplier

Divider

Power

Modulo

Above

Below

QuadraticAdder

Derivator

Renormalizer

PointwiseEqualer

Convolution

Correlator



ScalarOperator
^^^^^^^^^^^^^^^

.. autoclass:: ScalarOperator
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Methods

   .. autosummary::

      ~ScalarOperator.execute


Aggregate




ScalarVoidOperator
^^^^^^^^^^^^^^^^^^^

.. autoclass:: ScalarVoidOperator
   :no-index:
   :exclude-members: __init__, __str__
   :show-inheritance:

   .. rubric:: Methods

   .. autosummary::

      ~ScalarVoidOperator.execute


Shift

ShiftCircular

ShiftRev

ShiftCircularRev

ScalarAdder

ScalarSubstracter

ScalarRevSubstracter

ScalarMuliplier

ScalarDivider

ScalarRevDivider

ScalarPower

ScalarModulo

ScalarBelow

ScalarRevBelow

ScalarAbove

ScalarRevAbove

ScalarRevPower

ScalarRevModulo

Thresholder

Apply

Filter

Filter_FFT

Random

