# ------------------------- Operator ------------------------------------------
# Class to manage operators
# -----------------------------------------------------------------------------
import sys
import math
import numpy as np
from abc import abstractmethod

import tracklib.algo.Analytics as algoAF
import tracklib.core.Utils as utils
from tracklib.core.Kernel import Kernel

class UnaryOperator():
    @abstractmethod
    def execute(self, track, af_input):
        sys.exit("Not yet implemented")    
        
class BinaryOperator():
    @abstractmethod
    def execute(self, track, af_input1, af_input2):
        sys.exit("Not yet implemented")    
    
class UnaryVoidOperator():
    @abstractmethod
    def execute(self, track, af_input, af_output):
        sys.exit("Not yet implemented")
    
class BinaryVoidOperator():
    @abstractmethod
    def execute(self, track, af_input1, af_input2, af_output):
        sys.exit("Not yet implemented")    

class ScalarOperator():
    @abstractmethod
    def execute(self, track, af_input1, arg):
        sys.exit("Not yet implemented")            
        
class ScalarVoidOperator():
    @abstractmethod
    def execute(self, track, af_input1, arg, af_output):
        sys.exit("Not yet implemented")    
 
    
# =============================================================================
#   Applying operators through algebraic expressions
# =============================================================================

def makeRPN(expression):
    s = expression
    for operator in ["+-", "*/", "^", "@"]:
        depth = 0
        for p in range(len(s) - 1, -1, -1):
            if s[p] == ')': depth += 1
            if s[p] == '(': depth -= 1
            if not depth and s[p] in operator:
                return (makeRPN(s[:p]) + makeRPN(s[p+1:])) + [s[p]]
    s = s.strip()
    if s[0] == '(':
        return makeRPN(s[1:-1])
    return [s]  	
	
# -----------------------------------------------------------------------------
#      UnaryVoidOperator    
# -----------------------------------------------------------------------------

class Identity(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        f = lambda x: x
        return track.operate(Operator.APPLY, af_input, f, af_output)

class Integrator(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(1, track.size()):
            temp[i] = temp[i-1] + track.getObsAnalyticalFeature(af_input, i)
        algoAF.addListToAF(track, af_output, temp)
        return temp
            
class Differentiator(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(1, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input, i) - track.getObsAnalyticalFeature(af_input, i-1)
        temp[0] = utils.NAN
        algoAF.addListToAF(track, af_output, temp)    
        return temp

class ForwardFiniteDiff(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(1, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input, i+1) - track.getObsAnalyticalFeature(af_input, i)
        temp[0] = utils.NAN
        algoAF.addListToAF(track, af_output, temp)    
        return temp
		
class BackwardFiniteDiff(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(1, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input, i+1) - track.getObsAnalyticalFeature(af_input, i)
        temp[0] = utils.NAN
        algoAF.addListToAF(track, af_output, temp)    
        return temp
		
class CenteredFiniteDiff(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(1, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input, i+1) - track.getObsAnalyticalFeature(af_input, i-1)
        temp[0] = utils.NAN
        algoAF.addListToAF(track, af_output, temp)    
        return temp
		
class SecondOrderFiniteDiff(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(1, track.size()):
            temp[i]  =   track.getObsAnalyticalFeature(af_input, i+1) 
            temp[i] -= 2*track.getObsAnalyticalFeature(af_input, i)
            temp[i] +=   track.getObsAnalyticalFeature(af_input, i-1)
        temp[0] = utils.NAN
        algoAF.addListToAF(track, af_output, temp)    
        return temp
            
class ShiftRight(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        return track.operate(Operator.SHIFT, af_input, +1, af_output)
            
class ShiftLeft(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        return track.operate(Operator.SHIFT, af_input, -1, af_output)
            
class Inverter(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        f = lambda x: -x
        return track.operate(Operator.APPLY, af_input, f, af_output)
		
class Inverser(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        f = lambda x: 1.0/x
        return track.operate(Operator.APPLY, af_input, f, af_output)
            
class Rectifier(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        f = lambda x: -x*(x<0) + x*(x>0)
        return track.operate(Operator.APPLY, af_input, f, af_output)

class Debiaser(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        mean = track.operate(Operator.AVERAGER, af_input)
        return track.operate(Operator.SCALAR_ADDER, af_input, -mean, af_output)
            
class Normalizer(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        mean = track.operate(Operator.AVERAGER, af_input)
        sigma = track.operate(Operator.STDDEV, af_input)
        f = lambda x: (x-mean)/sigma
        return track.operate(Operator.APPLY, af_input, f, af_output)
            
class Square(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        f = lambda x: x*x
        return track.operate(Operator.APPLY, af_input, f, af_output)

class Sqrt(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        return track.operate(Operator.APPLY, af_input, math.sqrt, af_output)

class Diode(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        f = lambda x: x*(x>0)
        return track.operate(Operator.APPLY, af_input, f, af_output)
            
class Sign(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        f = lambda x: 1*(x>=0) - 1*(x<0)
        return track.operate(Operator.APPLY, af_input, f, af_output)
            
class Exp(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        return track.operate(Operator.APPLY, af_input, math.exp, af_output)
        
class Log(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        return track.operate(Operator.APPLY, af_input, math.log, af_output)
		
class Cos(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        return track.operate(Operator.APPLY, af_input, math.cos, af_output)
		
class Sin(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        return track.operate(Operator.APPLY, af_input, math.sin, af_output)
		
class Tan(UnaryVoidOperator):
    def execute(self, track, af_input, af_output):
        return track.operate(Operator.APPLY, af_input, math.tan, af_output)


# -----------------------------------------------------------------------------
#      BinaryVoidOperator    
# -----------------------------------------------------------------------------

class Adder(BinaryVoidOperator):
    def execute(self, track, af_input1, af_input2, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input1, i) + track.getObsAnalyticalFeature(af_input2, i)
        algoAF.addListToAF(track, af_output, temp)
        return temp
            
class Substracter(BinaryVoidOperator):
    def execute(self, track, af_input1, af_input2, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input1, i) - track.getObsAnalyticalFeature(af_input2, i)
        algoAF.addListToAF(track, af_output, temp)
        return temp
    
class Multiplier(BinaryVoidOperator):
    def execute(self, track, af_input1, af_input2, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = track.getObsAnalyticalFeature(af_input1, i)
            temp[i] *= track.getObsAnalyticalFeature(af_input2, i)
        algoAF.addListToAF(track, af_output, temp)
        return temp
            
class Divider(BinaryVoidOperator):
    def execute(self, track, af_input1, af_input2, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            num = track.getObsAnalyticalFeature(af_input1, i)
            denom = track.getObsAnalyticalFeature(af_input2, i)
            if denom == 0:
                temp[i] = utils.NAN
            else:
                temp[i] = num / denom
        algoAF.addListToAF(track, af_output, temp)
        return temp
            
class Power(BinaryVoidOperator):
    def execute(self, track, af_input1, af_input2, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input1, i) ** track.getObsAnalyticalFeature(af_input2, i)
        algoAF.addListToAF(track, af_output, temp)
        return temp
		
class Modulo(BinaryVoidOperator):
    def execute(self, track, af_input1, af_input2, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i] = track.getObsAnalyticalFeature(af_input1, i) % track.getObsAnalyticalFeature(af_input2, i)
        algoAF.addListToAF(track, af_output, temp)
        return temp
		
class Above(BinaryVoidOperator):
    def execute(self, track, af_input1, af_input2, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i] = 0.0 + (track.getObsAnalyticalFeature(af_input1, i) > track.getObsAnalyticalFeature(af_input2, i))
        algoAF.addListToAF(track, af_output, temp)
        return temp

class Below(BinaryVoidOperator):
    def execute(self, track, af_input1, af_input2, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i] = 0.0 + (track.getObsAnalyticalFeature(af_input1, i) < track.getObsAnalyticalFeature(af_input2, i))
        algoAF.addListToAF(track, af_output, temp)
        return temp
        
class QuadraticAdder(BinaryVoidOperator):
    def execute(self, track, af_input1, af_input2, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = track.getObsAnalyticalFeature(af_input1, i)**2
            temp[i] += track.getObsAnalyticalFeature(af_input2, i)**2
            temp[i]  = temp[i]**0.5
        algoAF.addListToAF(track, af_output, temp)
        return temp
    
class Derivator(BinaryVoidOperator):
    def execute(self, track, af_input1, af_input2, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(1, track.size()):
            df = track.getObsAnalyticalFeature(af_input1, i) - track.getObsAnalyticalFeature(af_input1, i-1)
            dt = track.getObsAnalyticalFeature(af_input2, i) - track.getObsAnalyticalFeature(af_input2, i-1)
            temp[i] = df/dt
        algoAF.addListToAF(track, af_output, temp)
        return temp
            
class Renormalizer(BinaryVoidOperator):
    def execute(self, track, af_input1, af_input2, af_output):
        m1 = track.operate(Operator.AVERAGER, af_input1)
        m2 = track.operate(Operator.AVERAGER, af_input2)
        s1 = track.operate(Operator.STDDEV, af_input1)
        s2 = track.operate(Operator.STDDEV, af_input2)
        f = lambda x: (x-m1) * s2/s1 + m2
        return track.operate(Operator.APPLY, af_input, f, af_output)

class PointwiseEqualer(BinaryVoidOperator):
    def execute(self, track, af_input1, af_input2, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i] = (track.getObsAnalyticalFeature(af_input1, i) == track.getObsAnalyticalFeature(af_input2, i))*1
        algoAF.addListToAF(track, af_output, temp)
        return temp
    
class Convolution(BinaryVoidOperator):
    def execute(self, track, af_input1, af_input2, af_output):
        track.createAnalyticalFeature(af_output)
        H = np.fft.fft(track[af_input1])
        G = np.fft.fft(track[af_input2])
        temp = np.abs(np.fft.ifft(H*np.conj(G)))
        algoAF.addListToAF(track, af_output, temp)
        return temp

# -----------------------------------------------------------------------------
#      UnaryOperator    
# -----------------------------------------------------------------------------

class Min(UnaryOperator):
    def execute(self, track, af_input):
        minimum = +1e300
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if (val < minimum):
                minimum = val
        return minimum
        
class Max(UnaryOperator):
    def execute(self, track, af_input):
        maximum = -1e300
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if (val > maximum):
                maximum = val
        return maximum
        
class Argmin(UnaryOperator):
    def execute(self, track, af_input):
        minimum = +1e300
        idmin = 0
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if (val < minimum):
                minimum = val
                idmin = i
        return idmin    
        
class Argmax(UnaryOperator):
    def execute(self, track, af_input):
        maximum = -1e300
        idmax = 0
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if (val > maximum):
                maximum = val
                idmax = i
        return idmax    
        
class Median(UnaryOperator):
    def execute(self, track, af_input):
        vals = track.getAnalyticalFeature(af_input)
        sort_index = np.argsort(np.array(vals))
        N = len(sort_index)
        if (N % 2 == 0):
            return 0.5*(vals[sort_index[(int)(N/2-1)]] + vals[sort_index[(int)(N/2)]])
        else:
            return vals[sort_index[(int)(N/2-1)]]
        
class Zeros(UnaryOperator):
    def execute(self, track, af_input):
        zeros = []
        for i in range(0, track.size()):
            if abs(track.getObsAnalyticalFeature(af_input, i)) == 0:
                zeros.append(i)
        return zeros

class Sum(UnaryOperator):
    def execute(self, track, af_input):
        somme = 0        
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if utils.isnan(val):
                continue
            somme += track.getObsAnalyticalFeature(af_input, i)
        return somme
    
class Averager(UnaryOperator):
    '''The average operator: y = mean(x)'''
    def execute(self, track, af_input):
        mean = 0        
        count = 0
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if utils.isnan(val):
                continue
            count += 1
            mean += track.getObsAnalyticalFeature(af_input, i)
        return mean/count
        
class Variance(UnaryOperator):
    def execute(self, track, af_input):
        mean = track.operate(Operator.AVERAGER, af_input)        
        count = 0
        var = 0
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if utils.isnan(val):
                continue
            count += 1
            var += (track.getObsAnalyticalFeature(af_input, i)-mean)**2
        return var/count
        
class StdDev(UnaryOperator):
    def execute(self, track, af_input):
        return math.sqrt(track.operate(Operator.VARIANCE, af_input))
        
class Mse(UnaryOperator):
    def execute(self, track, af_input):
        mse = 0
        count = 0
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if utils.isnan(val):
                continue
            count += 1
            mse += track.getObsAnalyticalFeature(af_input, i)**2
        return mse/count
        
class Rmse(UnaryOperator):
    def execute(self, track, af_input):
        return math.sqrt(track.operate(Operator.MSE, af_input))
        
class Mad(UnaryOperator):
    def execute(self, track, af_input):
        AD = []
        for i in range(track.size()):
            val = track.getObsAnalyticalFeature(af_input, i)
            if (utils.isnan(val)):
                continue
            AD.append(abs(val))
        sort_index = np.argsort(np.array(AD))
        N = len(sort_index)
        if (N % 2 == 0):
            return 0.5*(AD[sort_index[(int)(N/2-1)]] + AD[sort_index[(int)(N/2)]])
        else:
            return AD[sort_index[(int)(N/2-1)]]
            

# -----------------------------------------------------------------------------
#      BinaryOperator    
# -----------------------------------------------------------------------------

class Covariance(BinaryOperator):
    def execute(self, track, af_input1, af_input2):
        m1 = track.operate(Operator.AVERAGER, af_input1)
        m2 = track.operate(Operator.AVERAGER, af_input2)
        rho = 0
        count = 0
        for i in range(track.size()):
            x1 = track.getObsAnalyticalFeature(af_input1, i)
            x2 = track.getObsAnalyticalFeature(af_input2, i)
            if (utils.isnan(x1) or utils.isnan(x2)):
                continue
            rho += (x1-m1)*(x2-m2)
            count += 1
        return rho/count

class Correlator(BinaryOperator):
    def execute(self, track, af_input1, af_input2):
        s1 = track.operate(Operator.STDDEV, af_input1)
        s2 = track.operate(Operator.STDDEV, af_input2)            
        return track.operate(Operator.COVARIANCE, af_input1, af_input2) / (s1*s2)
                
class L0Diff(BinaryOperator):
    def execute(self, track, af_input1, af_input2):
        ecart = 0
        for i in range(track.size()):
            x1 = track.getObsAnalyticalFeature(af_input1, i)
            x2 = track.getObsAnalyticalFeature(af_input2, i)
            if (utils.isnan(x1) or utils.isnan(x2)):
                continue
            if (x1 == x2):
                continue
            ecart += 1
        return ecart
        
class L1Diff(BinaryOperator):
    def execute(self, track, af_input1, af_input2):
        ecart = 0
        count = 0
        for i in range(track.size()):
            x1 = track.getObsAnalyticalFeature(af_input1, i)
            x2 = track.getObsAnalyticalFeature(af_input2, i)
            if (utils.isnan(x1) or utils.isnan(x2)):
                continue
            count += 1
            ecart += abs(x1-x2)
        return ecart/count
        
class L2Diff(BinaryOperator):
    def execute(self, track, af_input1, af_input2):
        ecart = 0
        count = 0
        for i in range(track.size()):
            x1 = track.getObsAnalyticalFeature(af_input1, i)
            x2 = track.getObsAnalyticalFeature(af_input2, i)
            if (utils.isnan(x1) or utils.isnan(x2)):
                continue
            count += 1
            ecart += (x1-x2)**2
        return math.sqrt(ecart/count)

class LInfDiff(BinaryOperator):
    def execute(self, track, af_input1, af_input2):
        ecart = 0
        for i in range(track.size()):
            x1 = track.getObsAnalyticalFeature(af_input1, i)
            x2 = track.getObsAnalyticalFeature(af_input2, i)
            if (utils.isnan(x1) or utils.isnan(x2)):
                continue
            val = abs(x1-x2)
            if  val > ecart:
                ecart = val
        return ecart

class Equal(BinaryOperator):
    def execute(self, track, af_input1, af_input2):        
        for i in range(track.size()):
            val1 = track.getObsAnalyticalFeature(af_input1, i)
            val2 = track.getObsAnalyticalFeature(af_input2, i)
            if (utils.isnan(val1)) and (utils.isnan(val2)):
                continue
            if val1 != val2:
                return False              
        return True


# -----------------------------------------------------------------------------
#      ScalarOperator    
# -----------------------------------------------------------------------------
class Aggregate(ScalarOperator):
    def execute(self, track, af_input, function):
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = track.getObsAnalyticalFeature(af_input, i)
        return function(temp)

# -----------------------------------------------------------------------------
#      ScalarVoidOperator    
# -----------------------------------------------------------------------------
class Shift(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(track.size()):
            if (i-number < 0) or (i-number >= track.size()):
                temp[i] = utils.NAN
                continue
            temp[i] = track.getObsAnalyticalFeature(af_input, int(i-number))
        algoAF.addListToAF(track, af_output, temp)
        return temp
		
class ShiftRev(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        return track.operate(Operator.SHIFT, af_input, -number, af_output)

class ScalarAdder(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = track.getObsAnalyticalFeature(af_input, i) + number
        algoAF.addListToAF(track, af_output, temp)
        return temp
		
class ScalarSubstracter(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = track.getObsAnalyticalFeature(af_input, i) - number
        algoAF.addListToAF(track, af_output, temp)
        return temp

class ScalarRevSubstracter(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = number - track.getObsAnalyticalFeature(af_input, i)
        algoAF.addListToAF(track, af_output, temp)
        return temp
        
class ScalarMuliplier(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = track.getObsAnalyticalFeature(af_input, i) * number
        algoAF.addListToAF(track, af_output, temp)
        return temp
        
class ScalarDivider(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        return track.operate(Operator.SCALAR_MULTIPLIER, af_input, 1.0/number, af_output)
		
class ScalarRevDivider(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        track.operate(Operator.INVERSER, af_input, af_output)
        return track.operate(Operator.SCALAR_MULTIPLIER, af_output, number, af_output)
        
class ScalarPower(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = track.getObsAnalyticalFeature(af_input, i) ** number
        algoAF.addListToAF(track, af_output, temp)
        return temp
		
class ScalarModulo(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = track.getObsAnalyticalFeature(af_input, i) % number
        algoAF.addListToAF(track, af_output, temp)
        return temp		
		
class ScalarBelow(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = 0.0 + track.getObsAnalyticalFeature(af_input, i) < number
        algoAF.addListToAF(track, af_output, temp)
        return temp
		
class ScalarRevBelow(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = 0.0 + number < track.getObsAnalyticalFeature(af_input, i)
        algoAF.addListToAF(track, af_output, temp)
        return temp
		
class ScalarAbove(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = 0.0 + track.getObsAnalyticalFeature(af_input, i) > number
        algoAF.addListToAF(track, af_output, temp)
        return temp
		
class ScalarRevAbove(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = 0.0 + number > track.getObsAnalyticalFeature(af_input, i)
        algoAF.addListToAF(track, af_output, temp)
        return temp
		
class ScalarRevPower(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = number**track.getObsAnalyticalFeature(af_input, i)
        algoAF.addListToAF(track, af_output, temp)
        return temp
		
class ScalarRevModulo(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = number % track.getObsAnalyticalFeature(af_input, i)
        algoAF.addListToAF(track, af_output, temp)
        return temp
        
class Thresholder(ScalarVoidOperator):
    def execute(self, track, af_input, number, af_output):
        f = lambda x : x*(x<number) + number*(x>=number)
        track.operate(Operator.APPLY, af_input, f, af_output)
        
class Apply(ScalarVoidOperator):
    def execute(self, track, af_input, function, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i]  = function(track.getObsAnalyticalFeature(af_input, i))
        algoAF.addListToAF(track, af_output, temp)
        return temp
    
class Filter(ScalarVoidOperator):

    def execute(self, track, af_input, kernel, af_output):
		        
        # --------------------------------------------------------------        
        # Preparing kernel
        # --------------------------------------------------------------
        boundary = True
        if isinstance(kernel, Kernel):
            boundary = kernel.filterBoundary()
            kernel = kernel.toSlidingWindow()
        else:
            if isinstance(kernel, str):
                kernel = track.getAnalyticalFeature(kernel)
            norm = np.sum(np.array(kernel))
            for i in range(len(kernel)):
                kernel[i] /= norm
        N = len(kernel) 
        if N % 2 == 0:
            sys.exit("Error: kernel must contain an odd number of values in '"+ type(self).__name__ +"' operator")
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        D = (int)(N/2)
        
        # --------------------------------------------------------------
        # Filtering
        # --------------------------------------------------------------
        for i in range(0, track.size()):
            norm = 0
            for j in range(N):
                if i-j+D < 0:
                    continue
                if i-j+D >= track.size():
                    continue
                val = track.getObsAnalyticalFeature(af_input, i-j+D)
                if utils.isnan(val):
                    continue
                temp[i] += val*kernel[j]
                norm += kernel[j]
            temp[i] /= norm
            
        # --------------------------------------------------------------
        # Boundary correction
        # --------------------------------------------------------------
        if not boundary:
            for i in range(D):
                temp[i] = track.getObsAnalyticalFeature(af_input, i)
            for i in range(track.size()-D,track.size()):
                temp[i] = track.getObsAnalyticalFeature(af_input, i)

        algoAF.addListToAF(track, af_output, temp)
        return temp
    
    
class Filter_FFT(ScalarVoidOperator):

    def execute(self, track, af_input, kernel, af_output):
        
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
            sys.exit("Error: kernel must contain an odd number of values in '"+ type(self).__name__ +"' operator")
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        D = (int)(N/2)
        
        # --------------------------------------------------------------
        # Filtering
        # --------------------------------------------------------------
        Nc = track.size() - N
        h = kernel + [0]*Nc
        g = track.getAnalyticalFeature(af_input) 
        
        H = np.fft.fft(h)
        G = np.fft.fft(g)
        temp = np.flip(np.real(np.fft.ifft(H*np.conj(G))))
        temp = np.roll(temp, D)
        
        # --------------------------------------------------------------
        # Boundary correction
        # --------------------------------------------------------------
        if not boundary:
            for i in range(D):
                temp[i] = track.getObsAnalyticalFeature(af_input, i)
            for i in range(track.size()-D,track.size()):
                temp[i] = track.getObsAnalyticalFeature(af_input, i)
                
        algoAF.addListToAF(track, af_output, temp)
        return temp
    
class Random(ScalarVoidOperator):
    def execute(self, track, af_input, probability, af_output):
        track.createAnalyticalFeature(af_output)
        temp = [0]*track.size()
        for i in range(0, track.size()):
            temp[i] = probability() + track.getObsAnalyticalFeature(af_input, i)
        algoAF.addListToAF(track, af_output, temp)
        return temp

# -----------------------------------------------------------------------------
#  Operators        
# -----------------------------------------------------------------------------
class Operator:
    
    # Unary void operator
    IDENTITY = Identity()                                  # y(t) = x(t)
    RECTIFIER = Rectifier()                                # y(t) = |x(t)|
    INTEGRATOR = Integrator()                              # y(t) = y(t-1) + y(t) 
    SHIFT_RIGHT = ShiftRight()                             # y(t) = x(t-1)
    SHIFT_LEFT = ShiftLeft()                               # y(t) = x(t+1)
    INVERTER = Inverter()                                  # y(t) = -x(t)
    INVERSER = Inverser()                                  # y(t) = 1/x(t)
    DEBIASER = Debiaser()                                  # y(t) = x(t) - mean(x)
    SQUARE = Square()                                      # y(t) = x(t)*x(t)
    SQRT = Sqrt()                                          # y(t) = x(t)**(0.5)
    NORMALIZER = Normalizer()                              # y(t) = (x(t) - mean(x))/sigma(x)
    DIFFERENTIATOR = Differentiator()                      # y(t) = x(t) - x(t-1)
    BACKWARD_FINITE_DIFF = BackwardFiniteDiff()            # y(t) = x(t) - x(t-1)
    FORWARD_FINITE_DIFF = ForwardFiniteDiff()              # y(t) = x(t+1) - x(t)
    CENTERED_FINITE_DIFF = CenteredFiniteDiff()            # y(t) = x(t+1) - x(t-1)
    SECOND_ORDER_FINITE_DIFF = SecondOrderFiniteDiff()     # y(t) = x(t+1) - x(t-1)
    DIODE = Diode()                                        # y(t) = 1[x>0] * x(t)
    SIGN = Sign()                                          # y(t) = x(t)/|x(t)|
    EXP = Exp()                                            # y(t) = exp(x(t))
    LOG = Log()                                            # y(t) = log(x(t))
    COS = Cos()                                            # y(t) = cos(x(t))
    SIN = Sin()                                            # y(t) = sin(x(t))
    TAN = Tan()                                            # y(t) = tan(x(t))
    
    # Binary void operator
    ADDER = Adder()                                        # y(t) = x1(t) + x2(t)
    SUBSTRACTER = Substracter()                            # y(t) = x1(t) - x2(t)
    MULTIPLIER = Multiplier()                              # y(t) = x1(t) * x2(t)
    DIVIDER = Divider()                                    # y(t) = x1(t) / x2(t)
    POWER = Power()                                        # y(t) = x1(t) ** x2(t)
    MODULO = Modulo()                                      # y(t) = x1(t) % x2(t)
    ABOVE = Above()                                        # y(t) = x1(t) > x2(t) (boolean)
    BELOW = Below()                                        # y(t) = x1(t) < x2(t) (boolean)
    QUAD_ADDER = QuadraticAdder()                          # y(t) = (x1(t)**2 + x2(t)**2)**0.5
    RENORMALIZER = Renormalizer()                          # y(t) = (x1(t)-m(x1))* s(x2)/s(x1) + m(x2)
    DERIVATOR = Derivator()                                # y(t) = (x1(t)-x1(t-1))/(x2(t)-x2(t-1)) = dx1/dx2
    POINTWISE_EQUALER = PointwiseEqualer()                 # y(t) = 1 if x1(t)=x2(t), 0 otherwise
    CONVOLUTION = Convolution()                            # y(t) = int(x1(h)*x2(t-h)dh)
    
    # Unary operator
    SUM = Sum()                                            # y = sum(x)
    AVERAGER = Averager()                                  # y = mean(x)
    VARIANCE = Variance()                                  # y = Var(x)
    STDDEV = StdDev()                                      # y = sqrt(Var(x))
    MSE = Mse()                                            # y = mean(x**2)
    RMSE = Rmse()                                          # y = sqrt(mean(x**2))
    MAD = Mad()                                            # y = median(|x|)
    MIN = Min()                                            # y = min(x)
    MAX = Max()                                            # y = max(x)
    MEDIAN = Median()                                      # y = median(x)
    ARGMIN = Argmin()                                      # y = min {t | x(t) = min(x)}
    ARGMAX = Argmax()                                      # y = min {t | x(t) = max(x)}
    ZEROS = Zeros()                                        # y = {t | x(t) = 0}
														   
    # Binary operator                                      
    COVARIANCE = Covariance()                              # y = m[x1x2] - m[x1]*m[x2]
    CORRELATOR = Correlator()                              # y = cov(x1,x2)/(sigma(x1)*sigma(x2))
    L0 = L0Diff()                                          # y = #{t | x1(t) != x2(t)}
    L1 = L1Diff()                                          # y = mean(|x1(t)-x2(t)|)
    L2 = L2Diff()                                          # y = mean(|x1(t)-x2(t)|**2)
    LINF = LInfDiff()                                      # y = max(|x1(t)-x2(t)|)
    EQUAL = Equal()                                        # y = 1 if {x1(t) = x2(t) for all t}
    
    # Scalar operator
    AGGREGATE = Aggregate()                                # y(t) = arg({x(t)})   (arg is a list function)
														   
    # Scalar void operator    
    APPLY = Apply()                                        # y(t) = arg(x(t))     (arg is a real function)	
    SHIFT = Shift()                                        # y(t) = x(t-arg)      (arg is a integer)
    SHIFT_REV = ShiftRev()                                 # y(t) = x(t+arg)      (arg is a integer)
    SCALAR_ADDER = ScalarAdder()                           # y(t) = x(t) + arg    (arg is a numeric)
    SCALAR_SUBSTRACTER = ScalarSubstracter()               # y(t) = x(t) - arg    (arg is a numeric)
    SCALAR_MULTIPLIER = ScalarMuliplier()                  # y(t) = arg * x(t)    (arg is a numeric)
    SCALAR_DIVIDER = ScalarDivider()                       # y(t) = x(t) / arg    (arg is a numeric)
    SCALAR_POWER = ScalarPower()                           # y(t) = x(t) ** arg   (arg is a numeric)
    SCALAR_MODULO = ScalarModulo()                         # y(t) = x(t) % arg    (arg is a numeric)
    SCALAR_ABOVE = ScalarAbove()                           # y(t) = x1(t) > arg   (arg is a numeric)
    SCALAR_BELOW = ScalarBelow()                           # y(t) = x1(t) < arg   (arg is a numeric)
    SCALAR_REV_ABOVE = ScalarRevAbove()                    # y(t) = arg < x1(t)   (arg is a numeric)
    SCALAR_REV_BELOW = ScalarRevBelow()                    # y(t) = arg > x1(t)   (arg is a numeric)
    SCALAR_REV_SUBSTRACTER = ScalarRevSubstracter()        # y(t) = arg - x(t)    (arg is a numeric)
    SCALAR_REV_DIVIDER = ScalarRevDivider()                # y(t) = arg / x(t)    (arg is a numeric)
    SCALAR_REV_POWER = ScalarRevPower()                    # y(t) = arg ** x(t)   (arg is a numeric)
    SCALAR_REV_MODULO = ScalarRevModulo()                  # y(t) = arg % x(t)    (arg is a numeric)
    THRESHOLDER = Thresholder()                            # y(t) = 1 if x1(t) >= arg, 0 otherwise (arg is a numeric)
    RANDOM = Random()                                      # y(t) = eta(t) with eta ~ arg
    FILTER = Filter()                                      # y(t) = int[x(z)*h(t-z)dz] (arg is an odd-dimension vector or a kernel)
    FILTER_FFT = Filter_FFT()                              # y(t) = int[x(z)*h(t-z)dz] (fast version with FFT)
    
	# --------------------------------------------
    # Short-cut names for algebraic expression
	# --------------------------------------------
    NAMES_DICT_VOID = {
	
		# Unary void operators
        "I"     : INTEGRATOR, 
        "D"     : DIFFERENTIATOR,
        "D2"    : SECOND_ORDER_FINITE_DIFF,
		"LOG"   : LOG,
		"ABS"   : RECTIFIER,
        "SQRT"  : SQRT,
		"DIODE" : DIODE,
		"SIGN"  : SIGN,
		"EXP"   : EXP,
		"COS"   : COS,
		"SIN"   : SIN,
		"TAN"   : TAN,

		
		# Binary operators	
		"+"    : ADDER,
		"-"    : SUBSTRACTER,
		"*"    : MULTIPLIER,
		"/"    : DIVIDER,
		"^"    : POWER,
        ">"    : ABOVE,
        "<"    : BELOW,
		"%"    : MODULO,
		"!"    : FILTER,
		
	    "s+"    : SCALAR_ADDER,
		"s-"    : SCALAR_SUBSTRACTER,
		"s*"    : SCALAR_MULTIPLIER,
		"s/"    : SCALAR_DIVIDER,
		"s^"    : SCALAR_POWER,
	    "s&"    : SHIFT,
	    "s$"    : SHIFT_REV,
	    "s>"    : SCALAR_ABOVE,
	    "s<"    : SCALAR_BELOW,
	    "s%"    : SCALAR_MODULO,
			
	    "sr+"    : SCALAR_ADDER,
		"sr-"    : SCALAR_REV_SUBSTRACTER,
		"sr*"    : SCALAR_MULTIPLIER,
		"sr/"    : SCALAR_REV_DIVIDER,
		"sr^"    : SCALAR_REV_POWER,
	    "sr>"    : SCALAR_REV_ABOVE,
	    "sr%"    : SCALAR_REV_MODULO,
	    "sr<"    : SCALAR_REV_BELOW}
		
    NAMES_DICT_NON_VOID = {
	
		# Unary operators
        "SUM"    : SUM, 
        "AVG"    : AVERAGER,
        "VAR"    : VARIANCE,
		"STD"    : STDDEV,
		"MSE"    : MSE,
        "RMSE"   : RMSE,
		"MAD"    : MAD,
        "MIN"    : MIN, 
        "MAX"    : MAX,
        "MEDIAN" : MEDIAN,
		"ARGMIN" : ARGMIN,
		"ARGMAX" : ARGMAX}
