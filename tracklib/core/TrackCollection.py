# -------------------------- Track Collection ---------------------------------
# Class to manage collection of tracks
# -----------------------------------------------------------------------------

import tracklib.core.Plot as Plot

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
            
            
    def plot(self, template='TRACK2D', afs = []):
        
        for trace in self.__TRACES:
            plot = Plot.Plot(trace)
            plot.plot(template, afs)
        #plot.show()