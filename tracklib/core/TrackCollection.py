# -------------------------- Track Collection ---------------------------------
# Class to manage collection of tracks
# -----------------------------------------------------------------------------

import matplotlib.pyplot as plt

import tracklib.core.Operator as Operator
import tracklib.core.Plot as Plot
import tracklib.util.CellOperator as Sum

class TrackCollection:
    
    
    def __init__(self, TRACES):
        '''
        TRACES: list of Track
        '''
        self.__TRACES = TRACES
        
    def size(self):
        return len(self.__TRACES)
    
    def getTracks(self):
        return self.__TRACES
    
    
    def summary(self):
        '''
        Print summary (complete wkt below)
        '''
        output  = "-------------------------------------\n"
        output += "Number of GPS track: " + str(len(self.__TRACES)) + "\n"
        output += "-------------------------------------\n"
        SIZES = []
        for trace in self.__TRACES:
            SIZES.append(trace.size())
        output += "  Nb of pt(s):   " + str(SIZES) + "\n"
        # output += "  Nb of pt(s):   " + str(len(self.__POINTS)) + "\n"
        print(output)
    
    
    def addAnalyticalFeature(self, algorithm, name=None):
        for trace in self.__TRACES:
            trace.addAnalyticalFeature(algorithm, name)
            
            
    def plot(self):
        fig = plt.figure(figsize = (10, 8))
        
        #plt.xlim([xmin, xmax])
        (xmin, xmax, ymin, ymax) = self.bbox()
        plt.xlim([xmin, xmax])
        plt.ylim([ymin, ymax])
        
        for trace in self.__TRACES:
            X = trace.getX()
            Y = trace.getY()
            plt.plot(X, Y)
        plt.show()
        
    
    #def summarize(self, ):
        
        
    def bbox(self):
        tarray_xmin = []
        tarray_xmax = []
        tarray_ymin = []
        tarray_ymax = []
        
        for trace in self.__TRACES:
            tarray_xmin.append(trace.operate(Operator.Operator.MIN, 'x'))
            tarray_xmax.append(trace.operate(Operator.Operator.MAX, 'x'))
            tarray_ymin.append(trace.operate(Operator.Operator.MIN, 'y'))
            tarray_ymax.append(trace.operate(Operator.Operator.MAX, 'y'))
            
        xmin = Sum.co_min(tarray_xmin)
        xmax = Sum.co_max(tarray_xmax)
        ymin = Sum.co_min(tarray_ymin)
        ymax = Sum.co_max(tarray_ymax)
        
        return (xmin, xmax, ymin, ymax)
        
        
