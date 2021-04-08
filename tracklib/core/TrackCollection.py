# -------------------------- Track Collection ---------------------------------
# Class to manage collection of tracks
# -----------------------------------------------------------------------------
import random

import matplotlib.pyplot as plt

import tracklib.core.Operator as Operator
import tracklib.core.Plot as Plot
import tracklib.util.CellOperator as Sum

import tracklib.core.core_utils as utils
import tracklib.algo.Interpolation as Interpolation
import tracklib.algo.Simplification as Simplification



class TrackCollection:
    
    
    def __init__(self, TRACES=[]):
        '''
        TRACES: list of Track
        '''
        self.__TRACES = TRACES
		
    def addTrack(self, track):
        self.__TRACES.append(track)
        
    def size(self):
        return len(self.__TRACES)
    
    def getTracks(self):
        return self.__TRACES
		
    def getTrack(self, i):
        return self.__TRACES[i]
		
    def copy(self):
        TRACKS = TrackCollection()
        for i in range(self.size()):
            TRACKS.addTrack(self.getTrack(i).copy())
        return TRACKS
		
    # Average frequency	of tracks	
    def frequency(self, mode="temporal"):
        m = 0
        for track in self:
            m += track.frequency(mode)
        return m/self.size()
		
    # =========================================================================
    # Track collection coordinate transformation
    # =========================================================================	
    
    def toECEFCoords(self, base=None):
        if (self.__TRACES[0].getSRID() == "Geo"):
            for track in self.__TRACES:
                track.toECEFCoords()
            return
        if (self.__TRACES[0].getSRID() == "ENU"):
            if (base == None):
                print("Error: base coordinates should be specified for conversion ENU -> ECEF")
                exit()
            for track in self.__TRACES:
                track.toECEFCoords(base)
            return

    def toENUCoords(self, base=None):
        if (self.__TRACES[0].getSRID() in ["Geo", "ECEF"]):
            if (base == None):
                base = self.__TRACES[0].getFirstObs().position
                message = "Warning: no reference point (base) provided for local projection to ENU coordinates. "
                message += "Arbitrarily used: " + str(base)
                print(message)
            for track in self.__TRACES:
                track.toENUCoords(base)
            return
        if (self.__TRACES[0].getSRID() == "ENU"):
            if (base == None):
                print("Error: new base coordinates should be specified for conversion ENU -> ENU")
                exit() 
            for track in self.__TRACES:
                if (track.base == None):
                    print("Error: former base coordinates should be specified for conversion ENU -> ENU")
                    exit()
                track.toENUCoords(track.base, base)          				
            track.base = base.toGeoCoords()
            return
			
    def toGeoCoords(self, base=None):
        if (self.__TRACES[0].getSRID() == "ECEF"):
            for track in self.__TRACES:
                track.toGeoCoords()            
        if (self.__TRACES[0].getSRID() == "ENU"):
            if (base == None):
                print("Error: base coordinates should be specified for conversion ENU -> Geo")
                exit()
            for track in self.__TRACES:
                track.toGeoCoords(base)            	
          
    
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
            
            
    def plot(self, symbols=['r-'], markersize=[4]):
        (xmin, xmax, ymin, ymax) = self.bbox()
        plt.xlim([xmin, xmax])
        plt.ylim([ymin, ymax])
        Ns = len(symbols)
        Ms = len(markersize)
        for i in range(len(self.__TRACES)):
            trace = self.__TRACES[i]
            X = trace.getX()
            Y = trace.getY()
            plt.plot(X, Y, symbols[i%Ns], markersize=markersize[i%Ms])
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
        
    def toKML(self, color=None):
        '''
        Transforms track into KML string
        '''
        output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        output += "<kml xmlns=\"http://earth.google.com/kml/2.1\">\n"
        output += "<Document>\n"
		
        col = color
        
        for i in range(len(self.__TRACES)):
            track = self.__TRACES[i]
            output += "<Placemark>\n"
            output += "<name>Track " + str(i) + " [" + str(track.tid) + "/" + str(track.uid) + "]</name>\n"
            output += "<Style>\n"
            output += "<LineStyle>\n"
            if color == None:
                col = "{:06x}".format(random.randint(0, 0xFFFFFF))
            output += "<color>ff" + utils.rgbToHex(col)[2:] + "</color>\n"
            output += "</LineStyle>\n"
            output += "</Style>\n"
            output += "<LineString>\n"
            output += "<coordinates>\n"
            
            for i in range(track.size()):
                output += '{:15.12f}'.format(track.getObs(i).position.getX()) + "," 
                output += '{:15.12f}'.format(track.getObs(i).position.getY()) + ","
                output += '{:15.12f}'.format(track.getObs(i).position.getZ()) + "\n"
            
            output += "</coordinates>\n"
            output += "</LineString>\n"
            output += "</Placemark>\n"
			
        output += "</Document>\n"
        output += "</kml>\n"
        		
        return output
		
    def resample(self, delta, algo=1, mode=2):
        '''Resampling tracks with linear interpolation
        delta: interpolation interval (time in sec if 
        temporal mode is selected, space in meters if 
        spatial). Available modes are:
            - MODE_SPATIAL        (1)
            - MODE_TEMPORAL       (2)
        algorithm: 
            - ALGO_LINEAR            (1)
            - ALGO_THIN_SPLINES      (2)
            - ALGO_B_SPLINES         (3)
            - ALGO_GAUSSIAN_PROCESS  (4)
        In temporal mode, argument may be:
            - an integer or float: interval in seconds
            - a list of timestamps where interpolation 
            should be computed
            - a reference track'''
        for track in self:
           track.resample(delta, algo, mode)
		   
    # =========================================================================
    # Tracks simplification (returns a new track)
    # Tolerance is in the unit of track observation coordinates
    #   MODE_SIMPLIFY_DOUGLAS_PEUCKER (1)
    #   MODE_SIMPLIFY_VISVALINGAM (2)
    # =========================================================================    
    def simplify(self, tolerance, mode = Simplification.MODE_SIMPLIFY_DOUGLAS_PEUCKER):
        output = self.copy()
        for i in range(len(output)):
           output[i] = output[i].simplify(tolerance, mode)
		    
    # ------------------------------------------------------------
    # [+] Concatenation of two tracks
    # ------------------------------------------------------------
    def __add__(self, collection):
        return Track(self.__TRACES + collection.__TRACES, self.uid, self.tid)
        
    # ------------------------------------------------------------
    # [/] Even split track collection (returns n+1 collections)
    # ------------------------------------------------------------
    def __truediv__(self, number):
        N = (int)(self.size()/number)
        R = self.size()-N*number
        SPLITS = []
        for i in range(number+1):
            id_ini = i*N
            id_fin = min((i+1)*N, self.size())+1
            SPLITS.append(TrackCollection(self[id_ini:id_fin].copy()))
        return SPLITS
        
	# ------------------------------------------------------------	
    # [>] Removes first n points of track     
    # ------------------------------------------------------------	
    def __gt__(self, nb_points):
        output = self.copy()
        for i in range(self.size()):
            output[i] = output[i] > nb_points
        return output
		
	# ------------------------------------------------------------	
    # [<] Removes last n points of track     
    # ------------------------------------------------------------	
    def __lt__(self, nb_points):
        output = self.copy()
        for i in range(self.size()):
            output[i] = output[i] < nb_points
        return output
		
	# ------------------------------------------------------------	
    # [>=] Available operator     
    # ------------------------------------------------------------
    def __ge__(self, arg):
        return None	

	# ------------------------------------------------------------	
    # [<=] Available operator     
    # ------------------------------------------------------------
    def __le__(self, arg):
        return None	
		
	# ------------------------------------------------------------	
    # [!=] Available operator      
    # ------------------------------------------------------------
    def __neq__(self, arg):
        return None
		
	# ------------------------------------------------------------	
    # [Unary -] Available operator      
    # ------------------------------------------------------------
    def __neg__(self, arg):
        return None	
		
	# ------------------------------------------------------------	
    # [**] Resample (spatial) according to a number of points  
    # Linear interpolation and temporal resampling
    # ------------------------------------------------------------
    def __pow__(self, nb_points):
        output = self.copy()
        for i in range(self.size()):
            output[i] **= nb_points
        return output
	
	# ------------------------------------------------------------	
    # [abs] Available operator     
    # ------------------------------------------------------------
    def __abs__(self):
        return None
		
	# ------------------------------------------------------------	
    # [len] Number of tracks in track collection    
    # ------------------------------------------------------------
    def __len__(self):
        return self.size()
	
	# ------------------------------------------------------------	
    # [-] Computes difference profile of 2 tracks    
    # ------------------------------------------------------------
    def __sub__(self, arg):
        print("Available operator not implemented yet")

        
    # ------------------------------------------------------------
    # [*] Temporal resampling of tracks
    # ------------------------------------------------------------
    def __mul__(self, number):
        output = self.copy()
        for i in range(self.size()):
            output[i] *= number
        return output
        
    # ------------------------------------------------------------
    # [%] Remove one point out of n (or according to list pattern)
    # ------------------------------------------------------------    
    def __mod__(self, sample):
        output = self.copy()
        for i in range(self.size()):
            output[i] %= sample
        return output   
        
    # ------------------------------------------------------------
    # [//] Time resample of a tracks according to another track
    # ------------------------------------------------------------    
    def __floordiv__(self, track):
        output = self.copy()
        for t in output.__TRACES:
            t.resample(track)  # Mode temporal / linear
        return output    
	
	# ------------------------------------------------------------
    # [[n]] Get and set track number n
    # ------------------------------------------------------------    
    def __getitem__(self, n):
        return self.__TRACES[n]  
    def __setitem__(self, n, track):
        self.__TRACES[n] = track  	