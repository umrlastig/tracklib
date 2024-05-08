# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Yann Méneroux
Creation date: 1th november 2020

tracklib library provides a variety of tools, operators and 
functions to manipulate GPS trajectories. It is a open source contribution 
of the LASTIG laboratory at the Institut National de l'Information 
Géographique et Forestière (the French National Mapping Agency).
See: https://tracklib.readthedocs.io
 
This software is governed by the CeCILL-C license under French law and
abiding by the rules of distribution of free software. You can  use, 
modify and/ or redistribute the software under the terms of the CeCILL-C
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info". 

As a counterpart to the access to the source code and rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability. 

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or 
data to be ensured and,  more generally, to use and operate it in the 
same conditions as regards security. 

The fact that you are presently reading this means that you have had
knowledge of the CeCILL-C license and that you accept its terms.



This modules contains the classes to manage the operators

"""


import sys
import math
import numpy as np
from abc import abstractmethod
from tracklib.util.exceptions import *

from . import NAN, isnan, addListToAF, Kernel


class UnaryOperator:
    """Abstract Class to define a Unary Operator"""

    @abstractmethod
    def execute(self, track, af_input):
        """Execution of the operator

        :param track: TODO
        :param af_input: TODO
        """
        raise NotYetImplementedError("Not yet implemented")


class BinaryOperator:
    """Abstract Class to define a Binary Operator"""

    @abstractmethod
    def execute(self, track, af_input1, af_input2):
        """Execution of the operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        """
        raise NotYetImplementedError("Not yet implemented")


class UnaryVoidOperator:
    """Abstract Class to define a Unary Void Operator"""

    @abstractmethod
    def execute(self, track, af_input, af_output):
        """Execution of the operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        """
        raise NotYetImplementedError("Not yet implemented")


class BinaryVoidOperator:
    """Abstract Class to define a Binary Void Operator"""

    @abstractmethod
    def execute(self, track, af_input1, af_input2, af_output):
        """Execution of the operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        :param af_output: TODO
        """
        raise NotYetImplementedError("Not yet implemented")


class ScalarOperator:
    """Abstract Class to define a Scalar Operator"""

    @abstractmethod
    def execute(self, track, af_input1, arg):
        """Execution of the operator

        :param track: TODO
        :param af_input1: TODO
        :param arg: TODO
        """
        NotYetImplementedError("Not yet implemented")


class ScalarVoidOperator:
    """Abstract Class to define a Scalar Void Operator"""

    @abstractmethod
    def execute(self, track, af_input1, arg, af_output):
        """Execution of the operator

        :param track: TODO
        :param af_input1: TODO
        :param arg: TODO
        :param af_output:
        """
        NotYetImplementedError("Not yet implemented")



# -----------------------------------------------------------------------------
#      UnaryVoidOperator
# -----------------------------------------------------------------------------
class Identity(UnaryVoidOperator):
    """Identity operator"""

    def execute(self, track, af_input, af_output):
        """Execute the identity operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        f = lambda x: x
        return track.operate(Operator.APPLY, af_input, f, af_output)


class Integrator(UnaryVoidOperator):
    """Integrator operator"""

    def execute(self, track, af_input, af_output):
        """Execute the integrator operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(1, track.size()):
            temp[i] = temp[i - 1] + track.getObsAnalyticalFeature(af_input, i)
        addListToAF(track, af_output, temp)
        return temp


class Differentiator(UnaryVoidOperator):
    """Differentiator Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Differentiator operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(1, track.size()):
            temp[i] = track.getObsAnalyticalFeature(
                af_input, i
            ) - track.getObsAnalyticalFeature(af_input, i - 1)
        temp[0] = NAN
        addListToAF(track, af_output, temp)
        return temp


class ForwardFiniteDiff(UnaryVoidOperator):
    """ForwardFiniteDiff Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the ForwardFiniteDiff operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()-1):
            temp[i] = track.getObsAnalyticalFeature(
                af_input, i + 1
            ) - track.getObsAnalyticalFeature(af_input, i)
        temp[track.size()-1] = NAN
        addListToAF(track, af_output, temp)
        return temp


class BackwardFiniteDiff(UnaryVoidOperator):
    """BackwardFiniteDiff Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the BackwardFiniteDiff operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(1, track.size()):
            temp[i] = track.getObsAnalyticalFeature(
                af_input, i 
            ) - track.getObsAnalyticalFeature(af_input, i - 1)
        temp[0] = NAN
        addListToAF(track, af_output, temp)
        return temp


class CenteredFiniteDiff(UnaryVoidOperator):
    """CenteredFiniteDiff Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the CenteredFiniteDiff operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(1, track.size()-1):
            temp[i] = track.getObsAnalyticalFeature(
                af_input, i + 1
            ) - track.getObsAnalyticalFeature(af_input, i - 1)
        temp[0] = NAN
        temp[track.size()-1] = NAN
        addListToAF(track, af_output, temp)
        return temp


class SecondOrderFiniteDiff(UnaryVoidOperator):
    """SecondOrderFiniteDiff Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the SecondOrderFiniteDiff operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(1, track.size()-1):
            temp[i] = track.getObsAnalyticalFeature(af_input, i + 1)
            temp[i] -= 2 * track.getObsAnalyticalFeature(af_input, i)
            temp[i] += track.getObsAnalyticalFeature(af_input, i - 1)
        temp[0] = NAN
        temp[track.size()-1] = NAN
        addListToAF(track, af_output, temp)
        return temp


class ShiftRight(UnaryVoidOperator):
    """ShiftRight Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the ShiftRight operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        return track.operate(Operator.SHIFT, af_input, +1, af_output)
		
class ShiftCircularRight(UnaryVoidOperator):
    """ShiftRight Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the ShiftRight operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        return track.operate(Operator.SHIFT_CIRCULAR, af_input, +1, af_output)


class ShiftLeft(UnaryVoidOperator):
    """ShiftLeft Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the ShiftCircularLeft operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        return track.operate(Operator.SHIFT, af_input, -1, af_output)
		
class ShiftCircularLeft(UnaryVoidOperator):
    """ShiftLeft Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the ShiftCircularLeft operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        return track.operate(Operator.SHIFT_CIRCULAR, af_input, -1, af_output)


class Inverter(UnaryVoidOperator):
    """Inverter Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Inverter operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        f = lambda x: -x
        return track.operate(Operator.APPLY, af_input, f, af_output)


class Inverser(UnaryVoidOperator):
    """Inverser Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Inverser operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        f = lambda x: 1.0 / x
        return track.operate(Operator.APPLY, af_input, f, af_output)
		
class Reverser(UnaryVoidOperator):
    """Reverser Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Reverser operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input, track.size()-i-1)
        track[af_output] = temp


class Rectifier(UnaryVoidOperator):
    """Rectifier Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Rectifier operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        f = lambda x: -x * (x < 0) + x * (x > 0)
        return track.operate(Operator.APPLY, af_input, f, af_output)


class Debiaser(UnaryVoidOperator):
    """Debiaser Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Debiaser operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        mean = track.operate(Operator.AVERAGER, af_input)
        return track.operate(Operator.SCALAR_ADDER, af_input, -mean, af_output)


class Normalizer(UnaryVoidOperator):
    """Normalizer Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Normaliser operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        mean = track.operate(Operator.AVERAGER, af_input)
        sigma = track.operate(Operator.STDDEV, af_input)
        f = lambda x: (x - mean) / sigma
        return track.operate(Operator.APPLY, af_input, f, af_output)


class Square(UnaryVoidOperator):
    """Square Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Square operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        f = lambda x: x * x
        return track.operate(Operator.APPLY, af_input, f, af_output)


class Sqrt(UnaryVoidOperator):
    """Sqrt Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Sqrt operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        return track.operate(Operator.APPLY, af_input, math.sqrt, af_output)


class Diode(UnaryVoidOperator):
    """Diode Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Diode operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        f = lambda x: x * (x > 0)
        return track.operate(Operator.APPLY, af_input, f, af_output)


class Sign(UnaryVoidOperator):
    """Sign Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Sign operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        f = lambda x: 1 * (x >= 0) - 1 * (x < 0)
        return track.operate(Operator.APPLY, af_input, f, af_output)


class Exp(UnaryVoidOperator):
    """Exp Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Exp operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        return track.operate(Operator.APPLY, af_input, math.exp, af_output)


class Log(UnaryVoidOperator):
    """Log Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Log operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        temp = [0] * track.size()
        for i in range(0, track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if val > 0:
                temp[i] = math.log(val)
            else:
                temp[i] = 0
        track[af_output] = temp


class Cos(UnaryVoidOperator):
    """Cos Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Cos operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        return track.operate(Operator.APPLY, af_input, math.cos, af_output)


class Sin(UnaryVoidOperator):
    """Sin operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Sin operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        return track.operate(Operator.APPLY, af_input, math.sin, af_output)


class Tan(UnaryVoidOperator):
    """Tan Operator"""

    def execute(self, track, af_input, af_output):
        """Execute the Tan operator

        :param track: TODO
        :param af_input: TODO
        :param af_output: TODO
        :return: TODO
        """
        return track.operate(Operator.APPLY, af_input, math.tan, af_output)


# -----------------------------------------------------------------------------
#      BinaryVoidOperator
# -----------------------------------------------------------------------------
class Adder(BinaryVoidOperator):
    """Adder Operator"""

    def execute(self, track, af_input1, af_input2, af_output):
        """Execute the Normaliser operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(
                af_input1, i
            ) + track.getObsAnalyticalFeature(af_input2, i)
        addListToAF(track, af_output, temp)
        return temp


class Substracter(BinaryVoidOperator):
    """Substracter Operator"""

    def execute(self, track, af_input1, af_input2, af_output):
        """Execute the Substracter operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(
                af_input1, i
            ) - track.getObsAnalyticalFeature(af_input2, i)
        addListToAF(track, af_output, temp)
        return temp


class Multiplier(BinaryVoidOperator):
    """Multiplier Operator"""

    def execute(self, track, af_input1, af_input2, af_output):
        """Execute the Multiplier operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input1, i)
            temp[i] *= track.getObsAnalyticalFeature(af_input2, i)
        addListToAF(track, af_output, temp)
        return temp


class Divider(BinaryVoidOperator):
    """Divider Operator"""

    def execute(self, track, af_input1, af_input2, af_output):
        """Execute the Divier operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            num = track.getObsAnalyticalFeature(af_input1, i)
            denom = track.getObsAnalyticalFeature(af_input2, i)
            if denom == 0:
                temp[i] = NAN
            else:
                temp[i] = num / denom
        addListToAF(track, af_output, temp)
        return temp


class Power(BinaryVoidOperator):
    """Power operator"""

    def execute(self, track, af_input1, af_input2, af_output):
        """Execute the Power operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(
                af_input1, i
            ) ** track.getObsAnalyticalFeature(af_input2, i)
        addListToAF(track, af_output, temp)
        return temp


class Modulo(BinaryVoidOperator):
    """Modulo Operator"""

    def execute(self, track, af_input1, af_input2, af_output):
        """Execute the Modulo operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(
                af_input1, i
            ) % track.getObsAnalyticalFeature(af_input2, i)
        addListToAF(track, af_output, temp)
        return temp


class Above(BinaryVoidOperator):
    """Above Operator"""

    def execute(self, track, af_input1, af_input2, af_output):
        """Execute the Above operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = 0.0 + (
                track.getObsAnalyticalFeature(af_input1, i)
                > track.getObsAnalyticalFeature(af_input2, i)
            )
        addListToAF(track, af_output, temp)
        return temp


class Below(BinaryVoidOperator):
    """Below Operator"""

    def execute(self, track, af_input1, af_input2, af_output):
        """Execute the Below operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = 0.0 + (
                track.getObsAnalyticalFeature(af_input1, i)
                < track.getObsAnalyticalFeature(af_input2, i)
            )
        addListToAF(track, af_output, temp)
        return temp


class QuadraticAdder(BinaryVoidOperator):
    """Quadratic Adder Operator"""

    def execute(self, track, af_input1, af_input2, af_output):
        """Execute the Quadratic Adder operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input1, i) ** 2
            temp[i] += track.getObsAnalyticalFeature(af_input2, i) ** 2
            temp[i] = temp[i] ** 0.5
        addListToAF(track, af_output, temp)
        return temp


class Derivator(BinaryVoidOperator):
    """Derivator Operator"""

    def execute(self, track, af_input1, af_input2, af_output):
        """Execute the Derivator operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(1, track.size()):
            df = track.getObsAnalyticalFeature(
                af_input1, i
            ) - track.getObsAnalyticalFeature(af_input1, i - 1)
            dt = track.getObsAnalyticalFeature(
                af_input2, i
            ) - track.getObsAnalyticalFeature(af_input2, i - 1)
            temp[i] = df / dt
        addListToAF(track, af_output, temp)
        return temp


class Renormalizer(BinaryVoidOperator):
    """Renormalizer Operator"""

    def execute(self, track, af_input1, af_input2, af_output):
        """Execute the Renormalizer operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        :param af_output: TODO
        :return: TODO
        """
        m1 = track.operate(Operator.AVERAGER, af_input1)
        m2 = track.operate(Operator.AVERAGER, af_input2)
        s1 = track.operate(Operator.STDDEV, af_input1)
        s2 = track.operate(Operator.STDDEV, af_input2)
        #f = lambda x: (x - m1) * s2 / s1 + m2
        #return track.operate(Operator.APPLY, af_input1, af_input2, f, af_output)
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            x1 = track.getObsAnalyticalFeature(af_input1, i)
            temp[i] = (x1 - m1) * s2 / s1 + m2
        addListToAF(track, af_output, temp)
        return temp


class PointwiseEqualer(BinaryVoidOperator):
    """Pointwiser Equaler Operator"""

    def execute(self, track, af_input1, af_input2, af_output):
        """Execute the Pointwiser Equaler operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = (
                track.getObsAnalyticalFeature(af_input1, i)
                == track.getObsAnalyticalFeature(af_input2, i)
            ) * 1
        addListToAF(track, af_output, temp)
        return temp


class Convolution(BinaryVoidOperator):
    """Convolution Operator"""

    def execute(self, track, af_input1, af_input2, af_output):
        """Execute the Convolution operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        H = np.fft.fft(track[af_input1])
        G = np.fft.fft(track[af_input2])
        temp = np.abs(np.fft.ifft(H * np.conj(G)))
        addListToAF(track, af_output, temp)
        return temp
		
class Correlator(BinaryVoidOperator):
    """Correlator Operator"""

    def execute(self, track, af_input1, af_input2, af_output):
        """Execute the Correlator operator

        :param track: TODO
        :param af_input1: TODO
        :param af_input2: TODO
        :param af_output: TODO
        :return: TODO
        """
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            track.operate(Operator.SHIFT_CIRCULAR, af_input1, i, "temp") 
            temp[i] = track.operate(Operator.CORRELATION, "temp", af_input2)
        addListToAF(track, af_output, temp)
        return temp


# -----------------------------------------------------------------------------
#      UnaryOperator
# -----------------------------------------------------------------------------
class Min(UnaryOperator):
    """Min Operator"""

    def execute(self, track, af_input):
        """TODO"""
        minimum = +1e300
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if val < minimum:
                minimum = val
        return minimum


class Max(UnaryOperator):
    """TODO"""

    def execute(self, track, af_input):
        """TODO"""
        maximum = -1e300
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if val > maximum:
                maximum = val
        return maximum


class Argmin(UnaryOperator):
    """TODO"""

    def execute(self, track, af_input):
        """TODO"""
        minimum = +1e300
        idmin = 0
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if val < minimum:
                minimum = val
                idmin = i
        return idmin


class Argmax(UnaryOperator):
    """TODO"""

    def execute(self, track, af_input):
        """TODO"""
        maximum = -1e300
        idmax = 0
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if val > maximum:
                maximum = val
                idmax = i
        return idmax


class Median(UnaryOperator):
    """TODO"""

    def execute(self, track, af_input):
        """TODO"""
        vals = track.getAnalyticalFeature(af_input)
        sort_index = np.argsort(np.array(vals))
        N = len(sort_index)
        if N % 2 == 0:
            return 0.5 * (
                vals[sort_index[(int)(N / 2 - 1)]] + vals[sort_index[(int)(N / 2)]]
            )
        else:
            return vals[sort_index[(int)(N // 2)]]


class Zeros(UnaryOperator):
    """TODO"""

    def execute(self, track, af_input):
        """TODO"""
        zeros = []
        for i in range(0, track.size()):
            if abs(track.getObsAnalyticalFeature(af_input, i)) == 0:
                zeros.append(i)
        return zeros


class Sum(UnaryOperator):
    """TODO"""

    def execute(self, track, af_input):
        """TODO"""
        somme = 0
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if isnan(val):
                continue
            somme += track.getObsAnalyticalFeature(af_input, i)
        return somme


class Averager(UnaryOperator):
    """The average operator: y = mean(x)"""

    def execute(self, track, af_input):
        """TODO"""
        mean = 0
        count = 0
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if isnan(val):
                continue
            count += 1
            mean += track.getObsAnalyticalFeature(af_input, i)
        return mean / count


class Variance(UnaryOperator):
    """TODO"""

    def execute(self, track, af_input):
        """TODO"""
        mean = track.operate(Operator.AVERAGER, af_input)
        count = 0
        var = 0
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if isnan(val):
                continue
            count += 1
            var += (track.getObsAnalyticalFeature(af_input, i) - mean) ** 2
        return var / count


class StdDev(UnaryOperator):
    """TODO"""

    def execute(self, track, af_input):
        """TODO"""
        return math.sqrt(track.operate(Operator.VARIANCE, af_input))


class Mse(UnaryOperator):
    """TODO"""

    def execute(self, track, af_input):
        """TODO"""
        mse = 0
        count = 0
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if isnan(val):
                continue
            count += 1
            mse += track.getObsAnalyticalFeature(af_input, i) ** 2
        return mse / count


class Rmse(UnaryOperator):
    """Rmse Operator"""

    def execute(self, track, af_input):
        """Execution of Rmse operator"""
        return math.sqrt(track.operate(Operator.MSE, af_input))


class Mad(UnaryOperator):
    """TODO"""

    def execute(self, track, af_input):
        """TODO"""
        AD = []
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if isnan(val):
                continue
            AD.append(abs(val))
        sort_index = np.argsort(np.array(AD))
        N = len(sort_index)
        if N % 2 == 0:
            return 0.5 * (
                AD[sort_index[(int)(N / 2 - 1)]] + AD[sort_index[(int)(N / 2)]]
            )
        else:
            return AD[sort_index[(int)(N / 2 - 1)]]


# -----------------------------------------------------------------------------
#      BinaryOperator
# -----------------------------------------------------------------------------
class Covariance(BinaryOperator):
    """TODO"""

    def execute(self, track, af_input1, af_input2):
        """TODO"""
        m1 = track.operate(Operator.AVERAGER, af_input1)
        m2 = track.operate(Operator.AVERAGER, af_input2)
        rho = 0
        count = 0
        for i in range(track.size()):
            x1 = track.getObsAnalyticalFeature(af_input1, i)
            x2 = track.getObsAnalyticalFeature(af_input2, i)
            if isnan(x1) or isnan(x2):
                continue
            rho += (x1 - m1) * (x2 - m2)
            count += 1
        return rho / count


class Correlation(BinaryOperator):
    """TODO"""

    def execute(self, track, af_input1, af_input2):
        """TODO"""
        s1 = track.operate(Operator.STDDEV, af_input1)
        s2 = track.operate(Operator.STDDEV, af_input2)
        return track.operate(Operator.COVARIANCE, af_input1, af_input2) / (s1 * s2)


class L0Diff(BinaryOperator):
    """TODO"""

    def execute(self, track, af_input1, af_input2):
        """TODO"""
        ecart = 0
        for i in range(track.size()):
            x1 = track.getObsAnalyticalFeature(af_input1, i)
            x2 = track.getObsAnalyticalFeature(af_input2, i)
            if isnan(x1) or isnan(x2):
                continue
            if x1 == x2:
                continue
            ecart += 1
        return ecart


class L1Diff(BinaryOperator):
    """TODO"""

    def execute(self, track, af_input1, af_input2):
        """TODO"""
        ecart = 0
        count = 0
        for i in range(track.size()):
            x1 = track.getObsAnalyticalFeature(af_input1, i)
            x2 = track.getObsAnalyticalFeature(af_input2, i)
            if isnan(x1) or isnan(x2):
                continue
            count += 1
            ecart += abs(x1 - x2)
        return ecart / count


class L2Diff(BinaryOperator):
    """TODO"""

    def execute(self, track, af_input1, af_input2):
        """TODO"""
        ecart = 0
        count = 0
        for i in range(track.size()):
            x1 = track.getObsAnalyticalFeature(af_input1, i)
            x2 = track.getObsAnalyticalFeature(af_input2, i)
            if isnan(x1) or isnan(x2):
                continue
            count += 1
            ecart += (x1 - x2) ** 2
        return math.sqrt(ecart / count)


class LInfDiff(BinaryOperator):
    """TODO"""

    def execute(self, track, af_input1, af_input2):
        """TODO"""
        ecart = 0
        for i in range(track.size()):
            x1 = track.getObsAnalyticalFeature(af_input1, i)
            x2 = track.getObsAnalyticalFeature(af_input2, i)
            if isnan(x1) or isnan(x2):
                continue
            val = abs(x1 - x2)
            if val > ecart:
                ecart = val
        return ecart


class Equal(BinaryOperator):
    """TODO"""

    def execute(self, track, af_input1, af_input2):
        """TODO"""
        for i in range(track.size()):
            val1 = track.getObsAnalyticalFeature(af_input1, i)
            val2 = track.getObsAnalyticalFeature(af_input2, i)
            if (isnan(val1)) and (isnan(val2)):
                continue
            if val1 != val2:
                return False
        return True


# -----------------------------------------------------------------------------
#      ScalarOperator
# -----------------------------------------------------------------------------
class Aggregate(ScalarOperator):
    """TODO"""

    def execute(self, track, af_input, function):
        """TODO"""
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input, i)
        return function(temp)


# -----------------------------------------------------------------------------
#      ScalarVoidOperator
# -----------------------------------------------------------------------------
class Shift(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(track.size()):
            if (i - number < 0) or (i - number >= track.size()):
                temp[i] = NAN
                continue
            temp[i] = track.getObsAnalyticalFeature(af_input, int(i - number))
        addListToAF(track, af_output, temp)
        return temp


class ShiftCircular(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input, int((i-number)%track.size()))
        addListToAF(track, af_output, temp)
        return temp


class ShiftRev(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        return track.operate(Operator.SHIFT, af_input, -number, af_output)
		
class ShiftCircularRev(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        return track.operate(Operator.SHIFT_CIRCULAR, af_input, -number, af_output)


class ScalarAdder(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input, i) + number
        addListToAF(track, af_output, temp)
        return temp


class ScalarSubstracter(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input, i) - number
        addListToAF(track, af_output, temp)
        return temp


class ScalarRevSubstracter(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = number - track.getObsAnalyticalFeature(af_input, i)
        addListToAF(track, af_output, temp)
        return temp


class ScalarMuliplier(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input, i) * number
        addListToAF(track, af_output, temp)
        return temp


class ScalarDivider(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        return track.operate(
            Operator.SCALAR_MULTIPLIER, af_input, 1.0 / number, af_output
        )


class ScalarRevDivider(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        track.operate(Operator.INVERSER, af_input, af_output)
        return track.operate(Operator.SCALAR_MULTIPLIER, af_output, number, af_output)


class ScalarPower(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input, i) ** number
        addListToAF(track, af_output, temp)
        return temp


class ScalarModulo(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input, i) % number
        addListToAF(track, af_output, temp)
        return temp


class ScalarBelow(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = 0.0 + track.getObsAnalyticalFeature(af_input, i) < number
        addListToAF(track, af_output, temp)
        return temp


class ScalarRevBelow(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = 0.0 + number < track.getObsAnalyticalFeature(af_input, i)
        addListToAF(track, af_output, temp)
        return temp


class ScalarAbove(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = 0.0 + track.getObsAnalyticalFeature(af_input, i) > number
        addListToAF(track, af_output, temp)
        return temp


class ScalarRevAbove(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = 0.0 + number > track.getObsAnalyticalFeature(af_input, i)
        addListToAF(track, af_output, temp)
        return temp


class ScalarRevPower(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = number ** track.getObsAnalyticalFeature(af_input, i)
        addListToAF(track, af_output, temp)
        return temp


class ScalarRevModulo(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = number % track.getObsAnalyticalFeature(af_input, i)
        addListToAF(track, af_output, temp)
        return temp


class Thresholder(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, number, af_output):
        """TODO"""
        f = lambda x: x * (x < number) + number * (x >= number)
        track.operate(Operator.APPLY, af_input, f, af_output)


class Apply(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, function, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = function(track.getObsAnalyticalFeature(af_input, i))
        addListToAF(track, af_output, temp)
        return temp


class Filter(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, kernel, af_output):
        """TODO"""

        # --------------------------------------------------------------
        # Preparing kernel
        # --------------------------------------------------------------
        boundary = False
        if isinstance(kernel, Kernel):
            boundary = kernel.filterBoundary()
            if (str(kernel) == 'Dirac kernel'):
                kernel = [0,1,0]
            else:
                kernel = kernel.toSlidingWindow()
        else:
            if isinstance(kernel, str):
                kernel = track.getAnalyticalFeature(kernel)
            norm = np.sum(np.array(kernel))
            for i in range(len(kernel)):
                kernel[i] /= norm
        N = len(kernel)
        if N % 2 == 0:
            raise KernelError(
                "Error: kernel must contain an odd number of values in '"
                + type(self).__name__
                + "' operator"
            )
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        D = (int)(N / 2)

        # --------------------------------------------------------------
        # Filtering
        # --------------------------------------------------------------
        for i in range(0, track.size()):
            norm = 0
            for j in range(N):
                if i - j + D < 0:
                    continue
                if i - j + D >= track.size():
                    continue
                val = track.getObsAnalyticalFeature(af_input, i - j + D)
                if isnan(val):
                    continue
                temp[i] += val * kernel[j]
                norm += kernel[j]
            temp[i] /= norm

        # --------------------------------------------------------------
        # Boundary correction if boundary is filtered
        # --------------------------------------------------------------
        if not boundary:
            for i in range(D):
                temp[i] = track.getObsAnalyticalFeature(af_input, i)
            for i in range(track.size() - D, track.size()):
                temp[i] = track.getObsAnalyticalFeature(af_input, i)

        addListToAF(track, af_output, temp)
        return temp


class Filter_FFT(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, kernel, af_output):
        """TODO"""

        # --------------------------------------------------------------
        # Preparing kernel
        # --------------------------------------------------------------
        boundary = True
        if isinstance(kernel, Kernel):
            boundary = kernel.filterBoundary()
            kernel = kernel.toSlidingWindow()
        else:
            norm = np.sum(np.array(kernel))
            for i in range(len(kernel)):
                kernel[i] /= norm
        N = len(kernel)
        if N % 2 == 0:
            raise KernelError(
                "Error: kernel must contain an odd number of values in '"
                + type(self).__name__
                + "' operator"
            )
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        D = (int)(N / 2)

        # --------------------------------------------------------------
        # Filtering
        # --------------------------------------------------------------
        Nc = track.size() - N
        h = kernel + [0] * Nc
        g = track.getAnalyticalFeature(af_input)

        H = np.fft.fft(h)
        G = np.fft.fft(g)
        temp = np.flip(np.real(np.fft.ifft(H * np.conj(G))))
        temp = np.roll(temp, D)

        # --------------------------------------------------------------
        # Boundary correction
        # --------------------------------------------------------------
        if not boundary:
            for i in range(D):
                temp[i] = track.getObsAnalyticalFeature(af_input, i)
            for i in range(track.size() - D, track.size()):
                temp[i] = track.getObsAnalyticalFeature(af_input, i)

        addListToAF(track, af_output, temp)
        return temp


class Random(ScalarVoidOperator):
    """TODO"""

    def execute(self, track, af_input, probability, af_output):
        """TODO"""
        track.createAnalyticalFeature(af_output)
        temp = [0] * track.size()
        for i in range(0, track.size()):
            temp[i] = probability() + track.getObsAnalyticalFeature(af_input, i)
        addListToAF(track, af_output, temp)
        return temp


# -----------------------------------------------------------------------------
#  Operators
# -----------------------------------------------------------------------------
class Operator:
    """Class defining the usable operators

    The following operators are defined :

        1. Unary void operators:

            - `IDENTITY`: :math:`y(t) = x(t)`
            - `RECTIFIER`: :math:`y(t) = \|x(t)\|`
            - `INTEGRATOR`: :math:`y(t) = y(t-1) + y(t)`
            - `SHIFT_RIGHT`: :math:`y(t) = x(t-1)`
            - `SHIFT_LEFT`: :math:`y(t) = x(t+1)`
            - `SHIFT_CIRCULAR_RIGHT`: :math:`y(t) = x((t-1)%n)`
            - `SHIFT_CIRCULAR_LEFT`: :math:`y(t) = x((t+1)%n)`
            - `INVERTER`: :math:`y(t) = -x(t)`
            - `INVERSER`: :math:`y(t) = 1/x(t)`
            - `DEBIASER`: :math:`y(t) = x(t) - \\bar{x}`
            - `SQUARE`: :math:`y(t) = x(t \cdot x(t)`
            - `SQRT`: :math:`y(t) = x(t)^{1/2}`
            - `NORMALIZER`: :math:`y(t) = \\frac{(x(t) - \\bar{x})}{\sigma(x)}`
            - `DIFFERENTIATOR`: :math:`y(t) = x(t) - x(t-1)`
            - `BACKWARD_FINITE_DIFF`: :math:`y(t) = x(t) - x(t-1)`
            - `FORWARD_FINITE_DIFF`: :math:`y(t) = x(t+1) - x(t)`
            - `CENTERED_FINITE_DIFF`: :math:`y(t) = x(t+1) - x(t-1)`
            - `SECOND_ORDER_FINITE_DIFF`: :math:`y(t) = x(t+1) - x(t-1)`
            - `DIODE`: :math:`y(t) = 1[x>0] \cdot x(t)`
            - `SIGN`: :math:`y(t) = \\frac{x(t)}{\|x(t)\|}`
            - `EXP`:  :math:`y(t) = \exp(x(t))`
            - `LOG`:  :math:`y(t) = \log(x(t))`
            - `COS`:  :math:`y(t) = \cos(x(t))`
            - `SIN`:  :math:`y(t) = \sin(x(t))`
            - `TAN`:  :math:`y(t) = \\tan(x(t))`

        2. Binary void operators:

            - `ADDER`: :math:`y(t) = x1(t) + x2(t)`
            - `SUBSTRACTER`: :math:`y(t) = x1(t) - x2(t)`
            - `MULTIPLIER`: :math:`y(t) = x1(t) \cdot x2(t)`
            - `DIVIDER`: :math:`y(t) = x1(t) / x2(t)`
            - `POWER`: :math:`y(t) = x1(t) ^ {x2(t)}`
            - `MODULO`: :math:`y(t) = x1(t) % x2(t)`
            - `ABOVE`: :math:`y(t) = x1(t) > x2(t)`
            - `BELOW`: :math:`y(t) = x1(t) < x2(t)`
            - `QUAD_ADDER`: :math:`y(t) = (x1(t)^2 + x2(t)^2)^0.5`
            - `RENORMALIZER`: :math:`y(t) = (x1(t)-m(x1)) \cdot \\frac{s(x2)}{s(x1)} + m(x2)`
            - `DERIVATOR`: :math:`y(t) = \\frac{(x1(t)-x1(t-1))}{(x2(t)-x2(t-1))} = \\frac{dx1}{dx2}`
            - `POINTWISE_EQUALER`: :math:`y(t) = 1\ \\text{if}\ x1(t)=x2(t),\ 0\ \\text{otherwise}`
            - `CONVOLUTION`: :math:`y(t) = int(x1(h) \cdot x2(t-h)dh)`

        3. Unary operator

            - `SUM`: :math:`y = \Sigma x`
            - `AVERAGER`: :math:`y = \\bar{x}`
            - `VARIANCE`: :math:`y = \\var(x)`
            - `STDDEV`: :math:`y = \sqrt{\\var(x)}`
            - `MSE`: :math:`y = \\bar{x^2}`
            - `RMSE`: :math:`y = \sqrt{\\bar{x^2}}`
            - `MAD`: :math:`y = \\text{median}(|x|)`
            - `MIN`: :math:`y = \min(x)`
            - `MAX`: :math:`y = \max(x)`
            - `MEDIAN`: :math:`y = \\text{median}(x)`
            - `ARGMIN`: :math:`y = \min {t | x(t) = \min(x)}`
            - `ARGMAX`: :math:`y = \min {t | x(t) = \max(x)}`
            - `ZEROS`: :math:`y = {t | x(t) = 0}`

        4. Binary operator

            - `COVARIANCE`:  :math:`y = m[x1x2] - m[x1] \cdot m[x2]`
            - `CORRELATOR`:  :math:`y = \\frac{\cov(x1,x2)}{\sigma(x1) \cdot sigma(x2)}`
            - `L0`:  :math:`y = {t | x1(t) \\neq x2(t)}`
            - `L1`:  :math:`y = \\bar{|x1(t)-x2(t)|}`
            - `L2`:  :math:`y = \\bar{|x1(t)-x2(t)|^2}`
            - `LINF`:  :math:`y = \max(|x1(t)-x2(t)|)`
            - `EQUAL`:  :math:`y = 1\ \\text{if} {x1(t) = x2(t)\ \\text{for all t}}`

        5. Scalar operator

            - `AGGREGATE`: :math:`y(t) = arg({x(t)})`   (arg is a list function)

        6. Scalar void operator

            -  `APPLY`:  :math:`y(t) = arg(x(t))` (arg is a real function)
            -  `SHIFT`:  :math:`y(t) = x(t-arg)` (arg is a integer)
            -  `SHIFT_REV`:  :math:`y(t) = x(t+arg)` (arg is a integer)
            -  `SHIFT_CIRCULAR`:  :math:`y(t) = x((t-arg)%n)` (arg is a integer)
            -  `SHIFT_CIRCULAR_REV`:  :math:`y(t) = x((t+arg)%n)` (arg is a integer)
            -  `SCALAR_ADDER`:  :math:`y(t) = x(t) + arg` (arg is a numeric)
            -  `SCALAR_SUBSTRACTER`: :math:`:(t) = x(t) - arg` (arg is a numeric)
            -  `SCALAR_MULTIPLIER`:  :math:`y(t) = arg * x(t)` (arg is a numeric)
            -  `SCALAR_DIVIDER`:  :math:`y(t) = x(t) / arg` (arg is a numeric)
            -  `SCALAR_POWER`:  :math:`y(t) = x(t) ** arg` (arg is a numeric)
            -  `SCALAR_MODULO`:  :math:`y(t) = x(t) % arg` (arg is a numeric)
            -  `SCALAR_ABOVE`:  :math:`y(t) = x1(t) > arg` (arg is a numeric)
            -  `SCALAR_BELOW`:  :math:`y(t) = x1(t) < arg` (arg is a numeric)
            -  `SCALAR_REV_ABOVE`:  :math:`y(t) = arg < x1(t)` (arg is a numeric)
            -  `SCALAR_REV_BELOW`:  :math:`y(t) = arg > x1(t)` (arg is a numeric)
            -  `SCALAR_REV_SUBSTRACTER`:  :math:`y(t) = arg - x(t)` (arg is a numeric)
            -  `SCALAR_REV_DIVIDER`:  :math:`y(t) = arg / x(t)` (arg is a numeric)
            -  `SCALAR_REV_POWER`:  :math:`y(t) = arg ** x(t)` (arg is a numeric)
            -  `SCALAR_REV_MODULO`:  :math:`y(t) = arg % x(t)` (arg is a numeric)
            -  `THRESHOLDER`:  :math:`= y(t) = 1 if x1(t) >= arg, 0 otherwise` (arg is a numeric)
            -  `RANDOM`:  :math:`y(t) = eta(t) with eta ~ arg`
            -  `FILTER`:  :math:`= y(t) = int[x(z)*h(t-z)dz]` (arg is an odd-dimension vector or a kernel)
            -  `FILTER_FFT`:  :math:`y(t) = int[x(z)*h(t-z)dz]` (fast version with FFT)
    """

    # Unary void operator
    IDENTITY = Identity()  # y(t) = x(t)
    RECTIFIER = Rectifier()  # y(t) = |x(t)|
    INTEGRATOR = Integrator()  # y(t) = y(t-1) + y(t)
    SHIFT_RIGHT = ShiftRight()  # y(t) = x(t-1)
    SHIFT_LEFT = ShiftLeft()  # y(t) = x(t+1)
    SHIFT_CIRCULAR_RIGHT = ShiftCircularRight()  # y(t) = x((t-1)%n)
    SHIFT_CIRCULAR_LEFT = ShiftCircularLeft()  # y(t) = x((t+1)%n)
    INVERTER = Inverter()  # y(t) = -x(t)
    INVERSER = Inverser()  # y(t) = 1/x(t)
    REVERSER = Reverser()  # y(t) = x(n-t)
    DEBIASER = Debiaser()  # y(t) = x(t) - mean(x)
    SQUARE = Square()  # y(t) = x(t)*x(t)
    SQRT = Sqrt()  # y(t) = x(t)**(0.5)
    NORMALIZER = Normalizer()  # y(t) = (x(t) - mean(x))/sigma(x)
    DIFFERENTIATOR = Differentiator()  # y(t) = x(t) - x(t-1)
    BACKWARD_FINITE_DIFF = BackwardFiniteDiff()  # y(t) = x(t) - x(t-1)
    FORWARD_FINITE_DIFF = ForwardFiniteDiff()  # y(t) = x(t+1) - x(t)
    CENTERED_FINITE_DIFF = CenteredFiniteDiff()  # y(t) = x(t+1) - x(t-1)
    SECOND_ORDER_FINITE_DIFF = SecondOrderFiniteDiff()  # y(t) = x(t+1) + x(t-1) - 2*x(t)
    DIODE = Diode()  # y(t) = 1[x>0] * x(t)
    SIGN = Sign()  # y(t) = x(t)/|x(t)|
    EXP = Exp()  # y(t) = exp(x(t))
    LOG = Log()  # y(t) = log(x(t))
    COS = Cos()  # y(t) = cos(x(t))
    SIN = Sin()  # y(t) = sin(x(t))
    TAN = Tan()  # y(t) = tan(x(t))

    # Binary void operator
    ADDER = Adder()  # y(t) = x1(t) + x2(t)
    SUBSTRACTER = Substracter()  # y(t) = x1(t) - x2(t)
    MULTIPLIER = Multiplier()  # y(t) = x1(t) * x2(t)
    DIVIDER = Divider()  # y(t) = x1(t) / x2(t)
    POWER = Power()  # y(t) = x1(t) ** x2(t)
    MODULO = Modulo()  # y(t) = x1(t) % x2(t)
    ABOVE = Above()  # y(t) = x1(t) > x2(t) (boolean)
    BELOW = Below()  # y(t) = x1(t) < x2(t) (boolean)
    QUAD_ADDER = QuadraticAdder()  # y(t) = (x1(t)**2 + x2(t)**2)**0.5
    RENORMALIZER = Renormalizer()  # y(t) = (x1(t)-m(x1))* s(x2)/s(x1) + m(x2)
    DERIVATOR = Derivator()  # y(t) = (x1(t)-x1(t-1))/(x2(t)-x2(t-1)) = dx1/dx2
    POINTWISE_EQUALER = PointwiseEqualer()  # y(t) = 1 if x1(t)=x2(t), 0 otherwise
    CONVOLUTION = Convolution()  # y(t) = int(x1(h)*x2(t-h)dh)
    CORRELATOR = Correlator()  # y(t) = cov(x1(k+t),x2(k))/(sigma(x1)*sigma(x2))

    # Unary operator
    SUM = Sum()  # y = sum(x)
    AVERAGER = Averager()  # y = mean(x)
    VARIANCE = Variance()  # y = Var(x)
    STDDEV = StdDev()  # y = sqrt(Var(x))
    MSE = Mse()  # y = mean(x**2)
    RMSE = Rmse()  # y = sqrt(mean(x**2))
    MAD = Mad()  # y = median(|x|)
    MIN = Min()  # y = min(x)
    MAX = Max()  # y = max(x)
    MEDIAN = Median()  # y = median(x)
    ARGMIN = Argmin()  # y = min {t | x(t) = min(x)}
    ARGMAX = Argmax()  # y = min {t | x(t) = max(x)}
    ZEROS = Zeros()  # y = {t | x(t) = 0}

    # Binary operator
    COVARIANCE = Covariance()  # y = m[x1x2] - m[x1]*m[x2]
    CORRELATION = Correlation()  # y = cov(x1,x2)/(sigma(x1)*sigma(x2))
    L0 = L0Diff()  # y = #{t | x1(t) != x2(t)}
    L1 = L1Diff()  # y = mean(|x1(t)-x2(t)|)
    L2 = L2Diff()  # y = mean(|x1(t)-x2(t)|**2)
    LINF = LInfDiff()  # y = max(|x1(t)-x2(t)|)
    EQUAL = Equal()  # y = 1 if {x1(t) = x2(t) for all t}

    # Scalar operator
    AGGREGATE = Aggregate()  # y(t) = arg({x(t)})   (arg is a list function)

    # Scalar void operator
    APPLY = Apply()  # y(t) = arg(x(t))     (arg is a real function)
    SHIFT = Shift()  # y(t) = x(t-arg)      (arg is a integer)
    SHIFT_CIRCULAR = ShiftCircular()  # y(t) = x((t-arg)%n)  (arg is a integer)
    SHIFT_REV = ShiftRev()  # y(t) = x(t+arg)      (arg is a integer)
    SHIFT_CIRCULAR_REV = ShiftCircularRev()  # y(t) = x((t+arg)%n)  (arg is a integer)
    SCALAR_ADDER = ScalarAdder()  # y(t) = x(t) + arg    (arg is a numeric)
    SCALAR_SUBSTRACTER = ScalarSubstracter()  # y(t) = x(t) - arg    (arg is a numeric)
    SCALAR_MULTIPLIER = ScalarMuliplier()  # y(t) = arg * x(t)    (arg is a numeric)
    SCALAR_DIVIDER = ScalarDivider()  # y(t) = x(t) / arg    (arg is a numeric)
    SCALAR_POWER = ScalarPower()  # y(t) = x(t) ** arg   (arg is a numeric)
    SCALAR_MODULO = ScalarModulo()  # y(t) = x(t) % arg    (arg is a numeric)
    SCALAR_ABOVE = ScalarAbove()  # y(t) = x1(t) > arg   (arg is a numeric)
    SCALAR_BELOW = ScalarBelow()  # y(t) = x1(t) < arg   (arg is a numeric)
    SCALAR_REV_ABOVE = ScalarRevAbove()  # y(t) = arg < x1(t)   (arg is a numeric)
    SCALAR_REV_BELOW = ScalarRevBelow()  # y(t) = arg > x1(t)   (arg is a numeric)
    SCALAR_REV_SUBSTRACTER = (
        ScalarRevSubstracter()
    )  # y(t) = arg - x(t)    (arg is a numeric)
    SCALAR_REV_DIVIDER = ScalarRevDivider()  # y(t) = arg / x(t)    (arg is a numeric)
    SCALAR_REV_POWER = ScalarRevPower()  # y(t) = arg ** x(t)   (arg is a numeric)
    SCALAR_REV_MODULO = ScalarRevModulo()  # y(t) = arg % x(t)    (arg is a numeric)
    THRESHOLDER = (
        Thresholder()
    )  # y(t) = 1 if x1(t) >= arg, 0 otherwise (arg is a numeric)
    RANDOM = Random()  # y(t) = eta(t) with eta ~ arg
    FILTER = (
        Filter()
    )  # y(t) = int[x(z)*h(t-z)dz] (arg is an odd-dimension vector or a kernel)
    FILTER_FFT = Filter_FFT()  # y(t) = int[x(z)*h(t-z)dz] (fast version with FFT)

    # --------------------------------------------
    # Short-cut names for algebraic expression
    # --------------------------------------------
    NAMES_DICT_VOID = {
        # Unary void operators
        "I": INTEGRATOR,
        "D": DIFFERENTIATOR,
        "D2": SECOND_ORDER_FINITE_DIFF,
        "LOG": LOG,
        "ABS": RECTIFIER,
        "SQRT": SQRT,
        "DIODE": DIODE,
        "SIGN": SIGN,
        "EXP": EXP,
        "COS": COS,
        "SIN": SIN,
        "TAN": TAN,
        # Binary operators
        "+": ADDER,
        "-": SUBSTRACTER,
        "*": MULTIPLIER,
        "/": DIVIDER,
        "^": POWER,
        ">": ABOVE,
        "<": BELOW,
        "%": MODULO,
        "!": FILTER,
        "s+": SCALAR_ADDER,
        "s-": SCALAR_SUBSTRACTER,
        "s*": SCALAR_MULTIPLIER,
        "s/": SCALAR_DIVIDER,
        "s^": SCALAR_POWER,
        "s&": SHIFT_CIRCULAR,
        "s$": SHIFT_CIRCULAR_REV,
        "s>": SCALAR_ABOVE,
        "s<": SCALAR_BELOW,
        "s%": SCALAR_MODULO,
        "sr+": SCALAR_ADDER,
        "sr-": SCALAR_REV_SUBSTRACTER,
        "sr*": SCALAR_MULTIPLIER,
        "sr/": SCALAR_REV_DIVIDER,
        "sr^": SCALAR_REV_POWER,
        "sr>": SCALAR_REV_ABOVE,
        "sr%": SCALAR_REV_MODULO,
        "sr<": SCALAR_REV_BELOW,
    }

    NAMES_DICT_NON_VOID = {
        # Unary operators
        "SUM": SUM,
        "AVG": AVERAGER,
        "VAR": VARIANCE,
        "STD": STDDEV,
        "MSE": MSE,
        "RMSE": RMSE,
        "MAD": MAD,
        "MIN": MIN,
        "MAX": MAX,
        "MEDIAN": MEDIAN,
        "ARGMIN": ARGMIN,
        "ARGMAX": ARGMAX,
    }
