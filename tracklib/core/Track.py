# -------------------------- Track -------------------------------
# Class to manage GPS tracks
# Points are referenced in geodetic coordinates
# ----------------------------------------------------------------

import sys
import math
import copy
import random
import progressbar
import numpy as np
import matplotlib.pyplot as plt

from tracklib.core.Coords import ENUCoords
from tracklib.core.GPSTime import GPSTime
from tracklib.core.Obs import Obs
import tracklib.core.Operator as Operator
import tracklib.core.Kernel as Kernel
from tracklib.core.Kernel import GaussianKernel
from tracklib.core.TrackCollection import TrackCollection

import tracklib.core.Utils as utils
import tracklib.algo.Analytics as algoAF
import tracklib.algo.Geometrics as Geometrics
import tracklib.algo.Cinematics as Cinematics
import tracklib.algo.Stochastics as Stochastics
import tracklib.algo.Comparison as Comparison
import tracklib.algo.Interpolation as Interpolation
import tracklib.algo.Simplification as Simplification

import tracklib.core.Plot as Plot


class Track:

    def __init__(self, list_of_obs=None, user_id=0, track_id=0):
        '''
        Takes a (possibly empty) list of points as input
        '''
        if not list_of_obs:
            self.__POINTS = []
        else:
            self.__POINTS = list_of_obs
            
        self.uid = user_id
        self.tid = track_id
        self.base = None   # Base (ECEF coordinates) for ENU projection
        
        self.__analyticalFeaturesDico = {}
        
        
    def copy(self):
        return copy.deepcopy(self)
    
    def __str__(self):
        output = ""
        for i in range(self.size()):
            output += (str)(self.__POINTS[i])+'\n'     
        return output
		
    def getSRID(self):
        return str(type(self.getFirstObs().position)).split(".")[-1][0:-8]
		
    def duration(self):
        return self.getLastObs().timestamp - self.getFirstObs().timestamp
		
    # Average frequency	in Hz (resp. m/pt) for temporal (resp. spatial) mode 	
    def frequency(self, mode="temporal"):
        if ((mode == "spatial") or (mode == 1)):
            return self.size()/self.length()
        if ((mode == "temporal") or (mode == 0)):
            return self.size()/self.duration()
			
	# Inverse of average frequency in pt/sec (resp. pt/m) for temporal (resp. spatial) mode 	
    def interval(self, mode="temporal"):
        return 1.0/self.frequency(mode)
    

    # =========================================================================
    # Track coordinate transformation
    # =========================================================================
    
    def toECEFCoords(self, base=None):
        if (self.getSRID() == "Geo"):
            for i in range(self.size()):
                self.getObs(i).position = self.getObs(i).position.toECEFCoords()
            return
        if (self.getSRID() == "ENU"):
            if (base == None):
                if (self.base == None):
                    print("Error: base coordinates should be specified for conversion ENU -> ECEF")
                    exit()
                else:
                    base = self.base
            for i in range(self.size()):
                self.getObs(i).position = self.getObs(i).position.toECEFCoords(base)
            return

    def toENUCoords(self, base=None):
        if (self.getSRID() in ["Geo", "ECEF"]):
            if (base == None):
                base = self.getFirstObs().position
                message = "Warning: no reference point (base) provided for local projection to ENU coordinates. "
                message += "Arbitrarily used: " + str(base)
                print(message)
            for i in range(self.size()):
                self.getObs(i).position = self.getObs(i).position.toENUCoords(base)
            self.base = base.toGeoCoords() 
            return
        if (self.getSRID() == "ENU"):
            if (base == None):
                print("Error: new base coordinates should be specified for conversion ENU -> ENU")
                exit()
            if (self.base == None):
                print("Error: former base coordinates should be specified for conversion ENU -> ENU")
                exit()
            for i in range(self.size()):
                self.getObs(i).position = self.getObs(i).position.toENUCoords(self.base, base)          				
            self.base = base.toGeoCoords()
            return
			
    def toGeoCoords(self, base=None):
        if (self.getSRID() == "ECEF"):
            for i in range(self.size()):
                self.getObs(i).position = self.getObs(i).position.toGeoCoords()            
        if (self.getSRID() == "ENU"):
            if (base == None):
                if (self.base == None):
                    print("Error: base coordinates should be specified for conversion ENU -> Geo")
                    exit()
                else:
                    base = self.base
            for i in range(self.size()):
                self.getObs(i).position = self.getObs(i).position.toGeoCoords(base)            	
          

    # =========================================================================
    # Basic methods to get metadata and/or data
    # =========================================================================
    def size(self):
        return len(self.__POINTS)
        
    def getFirstObs(self):
        return self.__POINTS[0]
        
    def getLastObs(self):
        return self.__POINTS[self.size()-1]
        
    def getObsList(self):
        return self.__POINTS
    
    def getObs(self, i):
        if (i < 0):
            raise IndexError
        return self.__POINTS[i]
    
    def getX(self):
        X = []
        for i in range(self.size()):
            X.append(self.__POINTS[i].position.getX())
        return X
        
    def getY(self):
        Y = []
        for i in range(self.size()):
            Y.append(self.__POINTS[i].position.getY())
        return Y
        
    def getZ(self):
        Z = []
        for i in range(self.size()):
            Z.append(self.__POINTS[i].position.getZ())
        return Z
        
    def getT(self):
        T = []
        for i in range(self.size()):
            T.append(self.__POINTS[i].timestamp.toAbsTime())
        return T
    
    def getTimestamps(self):
        T = []
        for i in range(self.size()):
            T.append(self.__POINTS[i].timestamp)
        return T
		
    def getCentroid(self):
        m = self.getObs(0).position.copy()
        m.setX(self.operate(Operator.Operator.AVERAGER, 'x'))
        m.setY(self.operate(Operator.Operator.AVERAGER, 'y'))
        m.setZ(self.operate(Operator.Operator.AVERAGER, 'z'))	
        return m	
		
    def getMinX(self):
        return self.operate(Operator.Operator.MIN, 'x')

    def getMinY(self):
        return self.operate(Operator.Operator.MIN, 'y')

    def getMinZ(self):
        return self.operate(Operator.Operator.MIN, 'z')

    def getMaxX(self):
        return self.operate(Operator.Operator.MAX, 'x')

    def getMaxY(self):
        return self.operate(Operator.Operator.MAX, 'y')

    def getMaxZ(self):
        return self.operate(Operator.Operator.MAX, 'z')	
	
    def getLowerLeftPoint(self):
        ll = self.getObs(0).position.copy()
        ll.setX(self.getMinX())
        ll.setY(self.getMinY())
        ll.setZ(self.getMinZ())
        return ll

    def getUpperRightPoint(self):
        ur = self.getObs(0).position.copy()
        ur.setX(self.getMaxX())
        ur.setY(self.getMaxY())
        ur.setZ(self.getMaxZ())
        return ur

    def getBBox(self):
        return [self.getLowerLeftPoint(), self.getUpperRightPoint()]		

    def shiftTo(self, idx_point, new_coords=ENUCoords(0,0,0)):
        if (self.getSRID() != "ENU"):
            print("Error: shift may be applied only to ENU coords")
            exit()
        delta = self.getObs(idx_point).position - new_coords
        for i in range(self.size()):
            self.getObs(i).position = delta + self.getObs(i).position
                  
    
    def hasAnalyticalFeature(self, af_name):
        return af_name in self.__analyticalFeaturesDico
        
    def getAnalyticalFeature(self, af_name):
        AF = []
        if af_name == "x":
            for i in range(self.size()):
                AF.append(self.__POINTS[i].position.getX())
            return AF
        if af_name == "y":
            for i in range(self.size()):
                AF.append(self.__POINTS[i].position.getY())
            return AF
        if af_name == "z":
            for i in range(self.size()):
                AF.append(self.__POINTS[i].position.getZ())
            return AF
        if af_name == "t":
            for i in range(self.size()):
                AF.append(self.__POINTS[i].timestamp.toAbsTime())
            return AF
        if not self.hasAnalyticalFeature(af_name):
            sys.exit("Error: track does not contain analytical feature '" + af_name +"'")
        index = self.__analyticalFeaturesDico[af_name]
        for i in range(self.size()):
            AF.append(self.__POINTS[i].features[index])
        return AF    
                
    def getObsAnalyticalFeature(self, af_name, i):
        if af_name == "x":
            return self.getObs(i).position.getX()
        if af_name == "y":
            return self.getObs(i).position.getY()
        if af_name == "z":
            return self.getObs(i).position.getZ()
        if af_name == "t":
            return self.getObs(i).timestamp.toAbsTime()
        if not af_name in self.__analyticalFeaturesDico:
            sys.exit("Error: track does not contain analytical feature '" + af_name +"'") 
        index = self.__analyticalFeaturesDico[af_name]
        return self.__POINTS[i].features[index]
    
    def setObsAnalyticalFeature(self, af_name, i, val):
        if af_name == "x":
            self.getObs(i).position.setX(val)
            return
        if af_name == "y":
            self.getObs(i).position.setY(val)
            return
        if af_name == "z":
            self.getObs(i).position.setZ(val)
            return
        if not af_name in self.__analyticalFeaturesDico:
            sys.exit("Error: track does not contain analytical feature '" + af_name +"'") 
        index = self.__analyticalFeaturesDico[af_name]
        self.__POINTS[i].features[index] = val
        
    def getListAnalyticalFeatures(self):
        return list(self.__analyticalFeaturesDico.keys())
    
    def setXFromAnalyticalFeature(self, af_name):
        for i in range(self.size()):
            self.getObs(i).position.setX(self.getObsAnalyticalFeature(af_name,i))
    def setYFromAnalyticalFeature(self, af_name):
        for i in range(self.size()):
            self.getObs(i).position.setY(self.getObsAnalyticalFeature(af_name,i))
    def setZFromAnalyticalFeature(self, af_name):
        for i in range(self.size()):
            self.getObs(i).position.setZ(self.getObsAnalyticalFeature(af_name,i))
    def setTFromAnalyticalFeature(self, af_name):
        for i in range(self.size()):
            self.getObs(i).timestamp = self.getObsAnalyticalFeature(af_name,i)
            
    def isAFTransition(self, af_name):
        '''
        Return true if AF is transition marker.
        For example return true if AF values are like: 
            000000000000010000100000000000000000001000000100000
        Values are contained in {0, 1}. 1 means there is a regime change
        '''
        tabmarqueurs = self.getAnalyticalFeature(af_name)
        marqueurs = set(tabmarqueurs)
        if utils.NAN in marqueurs:
            marqueurs.remove(utils.NAN)
        if len(marqueurs.intersection([0, 1])) == 2:
            return True
        else:
            return False
    
    # =========================================================================
    # Basic methods to handle track object
    # =========================================================================
    
    def sort(self):
        sort_index = np.argsort(np.array(self.getTimestamps()))
        new_list = []
        for i in range(self.size()):
            new_list.append(self.__POINTS[sort_index[i]])
        self.__POINTS = new_list
        
    def isSorted(self):
        for i in range(self.size()-1):
            if (self.__POINTS[i+1].timestamp - self.__POINTS[i].timestamp <= 0):
                return False
        return True
        
    def addObs(self, obs):
        self.__POINTS.append(obs)
        
    def insertObs(self, obs, i=None):
        if i == None:
            self.insertObsInChronoOrder(obs)
        else:
            self.__POINTS.insert(i, obs)                
        
    def insertObsInChronoOrder(self, obs):
        self.insertObs(obs, self.__getInsertionIndex(obs.timestamp))
        
    def setObs(self, i, obs):
        self.__POINTS[i] = obs
        
    def setObsList(self, list_of_obs):
        self.__POINTS = list_of_obs
        
    def removeObs(self, arg):
        return self.removeObsList([arg])
    
    def popObs(self, idx):
        obs = self.getObs(idx)
        self.removeObs(idx)
        return obs
    
    def removeObsList(self, tab):
        if (len(tab) == 0):
            return 0
        tab.sort()
        for i in range(len(tab)-1):
            if (tab[i] == tab[i+1]):
                print("Error: dupplicated index or timestamp in 'removePoints' argument")
                return 0
        if isinstance(tab[0], int):
            return self.__removeObsListById(tab)
        if isinstance(tab[0], GPSTime):
            return self.__removeObsByListTimestamp(tab)
        print("Error: 'removePoint' is not implemented for type", type(tab[0]))
        return 0
    
    def setUid(self, used_id):
        self.uid = used_id
        
    def setTid(self, trace_id):
        self.tid = trace_id
        
    # ------------------------------------------------------------------    
    # Timestamp sort in O(n)
    # ------------------------------------------------------------------
    def sortRadix(self):
        
        SEC = []
        for sec in range(60*1000):
            SEC.append([])
        for i in range(self.size()):
            SEC[self.getObs(i).timestamp.sec*1000 + self.getObs(i).timestamp.ms].append(i)
           
        MIN = []
        for sec in range(60):
            MIN.append([])   
        for i in range(len(SEC)):
            for j in range(len(SEC[i])):
                id = SEC[i][j]
                MIN[self.getObs(id).timestamp.min].append(id)
       
        HOURS = []
        for hour in range(24):
            HOURS.append([])
        for i in range(len(MIN)):
            for j in range(len(MIN[i])):
                id = MIN[i][j]
                HOURS[self.getObs(id).timestamp.hour].append(id)
            
        DAYS = []
        for day in range(31):
            DAYS.append([])
        for i in range(len(HOURS)):
            for j in range(len(HOURS[i])):
                id = HOURS[i][j]
                DAYS[self.getObs(id).timestamp.day-1].append(id)
                   
        MONTHS = []
        for month in range(12):
            MONTHS.append([])
        for i in range(len(DAYS)):
            for j in range(len(DAYS[i])):
                id = DAYS[i][j]
                MONTHS[self.getObs(id).timestamp.month-1].append(id)
      
        YEARS = []
        for year in range(100):
            YEARS.append([])
        for i in range(len(MONTHS)):
            for j in range(len(MONTHS[i])):
                id = MONTHS[i][j]
                YEARS[self.getObs(id).timestamp.year-1970].append(id)
         
        
        new_list = []
        for i in range(len(YEARS)):
            for j in range(len(YEARS[i])):
                id = YEARS[i][j]
                new_list.append(self.__POINTS[id])
           
        self.__POINTS = new_list


    # =========================================================================
    # Basic private methods to handle track object
    # =========================================================================
    def __removeObsById(self, i):
        length = self.size()
        del self.__POINTS[i]
        return (length - self.size())
    
    def __removeObsByTimestamp(self, tps):
        for i in range(self.size()):
            if (self.__POINTS[i].timestamp == tps):
                self.__removeObsById(i)
                return 1
        return 0
    
    def __removeObsListById(self, tab_idx):
        counter = 0
        for i in range(len(tab_idx)-1,-1,-1):
            counter += self.__removeObsById(tab_idx[i])
        return counter
    
    def __removeObsListByTimestamp(self, tab_tps):
        counter = 0
        for i in range(len(tab_tps)):
            counter += self.__removeObsByTimestamp(tab_tps[i])
        return counter
    
    def __getInsertionIndex(self, timestamp):
        N = self.size()
        if N == 0:
            return 0
        if N == 1:
            return (self.getFirstObs().timestamp < timestamp)*1
        delta = 2**((int)(math.log(N)/math.log(2))-1)
        id = 0
        while (delta != 0):
            id = id + delta
            if (id >= N):
                delta = -abs(delta >> 1)
                continue
            if (id == 0):
                break
            if (self.getObs(id).timestamp > timestamp):
                delta = -abs(delta >> 1)
            else:
                delta = +abs(delta >> 1)
        while(self.getObs(id).timestamp > timestamp):
            if (id == 0):
                break
            id -= 1
        while(self.getObs(id).timestamp <= timestamp):
            id += 1
            if (id == N):
                break
        return id
		
		
    def print(self, af_names="#all_features"):
        '''Console print of track with analytical features'''
        if self.size() == 0:
            return
        if af_names == "#all_features":
            af_names = self.getListAnalyticalFeatures()
        if not isinstance(af_names, list):
            af_names = [af_names]
        print("-----------------------------------------------------------------")
        line = "Analytical features:  "
        for i in range(len(af_names)):
            line += af_names[i]+"  "
        print(line)
        print("-----------------------------------------------------------------")
        for i in range(self.size()):
            output = (str)(self.__POINTS[i])+ ",  "
            for j in range(len(af_names)):
                output += str(self.getObsAnalyticalFeature(af_names[j], i))
                if j < len(af_names)-1:
                    output += ","
            print(output)
		 
    def summary(self):
        '''
        Print summary (complete wkt below)
        '''
        output  = "-------------------------------------\n"
        output += "GPS track #" + str(self.tid) +" of user " + str(self.uid) + ":\n"
        output += "-------------------------------------\n"
        output += "  Nb of pt(s):   " + str(len(self.__POINTS)) + "\n"
        if (len(self.__POINTS) > 0):
            t1 = self.getFirstObs().timestamp
            t2 = self.getLastObs().timestamp
            output += "  Ref sys id   : " + self.getSRID() + "\n"
            output += "  Starting at  : " + (str)(t1) + "\n"
            output += "  Ending at    : " + (str)(t2) + "\n"
            output += "  Duration     : " + (str)('{:7.3f}'.format(t2-t1)) + " s\n"
            output += "  Length       : " + (str)('{:1.3f}'.format(self.length())) + " m\n"
        output += "-------------------------------------\n"
        print(output)
        
        
    def length(self):
        '''
        Total length of curvilinear abscissa
        '''
        s = 0
        for i in range(1,self.size()):
            s += self.getObs(i-1).distanceTo(self.getObs(i))
        return s
        
    
    def computeNetDeniv(self, id_ini, id_fin):
        '''
        Computes net denivellation (in meters)
        '''
        return self.__POINTS[id_fin].position.getZ() - self.__POINTS[id_ini].position.getZ()


    def computeAscDeniv(self, id_ini, id_fin):
        '''
        Computes positive denivellation (in meters)
        '''
        dp = 0
        
        for i in range(id_ini, id_fin):
            Z1 = self.__POINTS[i].position.getZ()
            Z2 = self.__POINTS[i+1].position.getZ()
            if (Z2 > Z1):
                dp += Z2-Z1
    
        return dp 
    
    
    def computeDescDeniv(self, id_ini, id_fin):
        '''
        Computes negative denivellation (in meters)
        '''
        dn = 0
        
        for i in range(id_ini, id_fin):
            Z1 = self.__POINTS[i].position.getZ()
            Z2 = self.__POINTS[i+1].position.getZ()
            if (Z2 < Z1):
                dn += Z2-Z1
    
        return dn
        
   
    def toWKT(self):
        '''
        Transforms track into WKT string
        '''
        output = "LINESTRING(("
        for i in range(self.size()):
            output += (str)(self.__POINTS[i].position.E) + " " 
            output += (str)(self.__POINTS[i].position.N)
            if (i != self.size()-1):
                output += ","
        output += "))"
        return output
		
     
    def extract(self, id_ini, id_fin):
        '''
        Extract between two indices from a track
        id_ini: Initial index of extraction
        id_fin: final index of extraction
        '''
        track = Track()
        track.setUid(self.uid)
        for k in range(id_ini, id_fin+1):
            track.addObs(self.__POINTS[k])
        #track.__analyticalFeaturesDico = self.__analyticalFeaturesDico
        return track
        
    
    def extractSpanTime(self, tini, tfin):
        '''
        Extract span time from a track
        tini: Initial time of extraction
        tfin: final time of extraction
        '''
        if (tini > tfin):
            ttemp = tini
            tini = tfin
            tfin = ttemp
        track = Track([], self.uid)
        for k in range(self.size()):
            if (self.__POINTS[k].timestamp < tini):
                continue
            if (self.__POINTS[k].timestamp > tfin):
                continue
            track.addObs(self.__POINTS[k].copy())
        track.__analyticalFeaturesDico = self.__analyticalFeaturesDico
        return track
        
    def addSeconds(self, sec_number):
        '''Adds seconds to timestamps in track
        sec_number: number of seconds to add (may be < 0)'''
        for i in range(self.size()):
            self.getObs(i).timestamp = self.getObs(i).timestamp.addSec(sec_number)
    
    
    # =========================================================================
    # Analytical algorithms
    # =========================================================================
    def __controlName(name):
        if (name in ["x", "y", "z", "t"]):
            sys.exit("Error: analytical feature name '" + name +"' is not available")
    
    def addAnalyticalFeature(self, algorithm, name=None):
        '''
        Execute l'algo de l'AF.
        L'AF est déjà dans le dico, dans les features de Obs et initialisé.
        '''
        if (name == None):
            name = algorithm.__name__
        Track.__controlName(name)
        
        if not self.hasAnalyticalFeature(name):
            self.createAnalyticalFeature(name) 
        
        idAF = self.__analyticalFeaturesDico[name]
        
        for i in range(self.size()):
            value = 0
            try:
                value = algorithm(self, i)
            except IndexError:
                value = utils.NAN
            self.getObs(i).features[idAF] = value

        return self.getAnalyticalFeature(name)
    
    def createAnalyticalFeature(self, name, val_init=0.0):
        '''
        Ajout de l'AF dans le dico et dans le features de Obs.
        Initialise tous les obs.
        '''
        if name == None:
            return
        Track.__controlName(name)
        if self.size() <= 0:
            sys.exit("Error: can't add AF '" + name + "', there is no observation in track")
        if self.hasAnalyticalFeature(name):
            return
        idAF = len(self.__analyticalFeaturesDico)
        self.__analyticalFeaturesDico[name] = idAF
        if isinstance(val_init, list):
            for i in range(self.size()):
                self.getObs(i).features.append(val_init[i])
        else:
            for i in range(self.size()):
                self.getObs(i).features.append(val_init)


    def removeAnalyticalFeature(self, name):
        if not self.hasAnalyticalFeature(name):
            sys.exit("Error: track does not contain analytical feature '" + name +"'") 
        idAF = self.__analyticalFeaturesDico[name]
        for i in range(self.size()):
            del self.getObs(i).features[idAF]
        del self.__analyticalFeaturesDico[name]
        keys = self.__analyticalFeaturesDico.keys()
        for k in keys:
            if self.__analyticalFeaturesDico[k] > idAF:
                self.__analyticalFeaturesDico[k] -= 1
            
    def operate(self, operator, arg1, arg2=None, arg3=None):
        # UnaryOperator
        if (isinstance(operator, Operator.UnaryOperator)):
            if isinstance(arg1, str):
                return operator.execute(self, arg1)
            output = [0]*len(arg1)
            for i in range(output):
                output[i] = operator.execute(self, arg1[i])
            return output
        
        # BinaryOperator
        if (isinstance(operator, Operator.BinaryOperator)):
            if isinstance(arg1, str):
                return operator.execute(self, arg1, arg2)
            if len(arg1) != len(arg2):
                sys.exit("Error in "+type(operator).__name__+": non-concordant number in input features")
            output = [0]*len(arg1)
            for i in range(output):
                output[i] = operator.execute(self, arg1[i], arg2[i])
            return output
        
        # ScalarOperator
        if (isinstance(operator, Operator.ScalarOperator)):
            if isinstance(arg1, str):
                return operator.execute(self, arg1, arg2)
            output = [0]*len(arg1)
            for i in range(len(arg1)):
                output[i] = operator.execute(self, arg1[i], arg2)
            return output
    
        # UnaryVoidOperator
        if (isinstance(operator, Operator.UnaryVoidOperator)):
            if arg2 == None:
                arg2 = arg1
            if isinstance(arg1, str):
                return operator.execute(self, arg1, arg2)
            if len(arg1) != len(arg2):
                sys.exit("Error in "+type(operator).__name__+": non-concordant number in input and output features")
            for i in range(len(arg1)):
                operator.execute(self, arg1[i], arg2[i])
        
        # BinaryVoidOperator
        if (isinstance(operator, Operator.BinaryVoidOperator)):
            if arg3 == None:
                arg3 = arg1
            if isinstance(arg1, str):
                return operator.execute(self, arg1, arg2, arg3)
            if len(arg1) != len(arg2):
                sys.exit("Error in "+type(operator).__name__+": non-concordant number in input features")
            if len(arg1) != len(arg3):
                sys.exit("Error in "+type(operator).__name__+": non-concordant number in input and output features")
            for i in range(len(arg1)):
                operator.execute(self, arg1[i], arg2[i], arg3[i])
        
        # ScalarVoidOperator
        if (isinstance(operator, Operator.ScalarVoidOperator)):
            if arg3 == None:
                arg3 = arg1
            if isinstance(arg1, str):
                return operator.execute(self, arg1, arg2, arg3)
            if len(arg1) != len(arg3):
                sys.exit("Error in "+type(operator).__name__+": non-concordant number in input and output features")
            for i in range(len(arg1)):
                operator.execute(self, arg1[i], arg2, arg3[i])



    # =========================================================================
    #  Resampling
    # =========================================================================
    
    def resample(self, delta, algo=1, mode=2):
        '''Resampling a track with linear interpolation
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
			
		# (Temporaire)
        if not (self.getSRID() == "ENU"):
            print("Error: track data must be in ENU coordinates for resampling")
            exit()
			
        Interpolation.resample(self, delta, algo, mode)
        self.__analyticalFeaturesDico = {}
   
    
    def incrementTime(self, dt=1):  
        '''Add 1 sec to each subsequent record. Use incrementTime to 
        get valid timestamps sequence when timestamps are set as default 
        date on 1970/01/01 00:00:00 for example''' 
        for i in range(len(self)):
            self.getObs(i).timestamp = self.getObs(i).timestamp.addSec(i*dt)
        
        
    def mapOn(self, reference, TP1, TP2=[], init=[], N_ITER_MAX=20, mode="2D", verbose=True):
    
        '''Geometric affine transformation to align two tracks with diferent
		coordinate systems. For "2D" mode, coordinates must be ENU or Geo. For 
		"3D" mode, any type of coordinates is valid. In general, it is recommended 
		to avoid usage of non-metric Geo coordinates for mapping operation, since 
		it is relying on an isotropic error model. Inputs:
		   - reference: another track we want to align on or a list of points
		   - TP1: list of tie points indices (relative to track self)
		   - TP2: list of tie points indices (relative to track)
		   - mode: could be "2D" (default) or "3D"
        if TP2 is not specified, it is assumed equal to TP1.
		TP1 and TP2 must have same size. Adjustment is performed with least squares.
		The general transformation from point X to point X' is provided below:
		                         X' = kRX + T
		with: k a positive real value, R a 2D or 3D rotation matrix and T a 2D or 
		3D translation vector. Transformation parameters are returned in standard 
		output in the following format: [theta, k, tx, ty] (theta in radians)
		Track argument may also be replaced ny a list of points.
		Note that mapOn does not handle negative determinant (symetries not allowed)
		'''   

        if (mode == "3D"):
            print("Mode 3D is not implemented yet")
            exit()	

        if (len(init) == 0):
            init = [0,1,0,0]		
		
        if (len(TP2) == 0):
            TP2 = TP1
        if not (len(TP1) == len(TP2)):
            print("Error: tie points lists must have same size")
            exit()
			
        P1 = [self.getObs(i).position.copy() for i in TP1]
		
        if isinstance(reference, Track):
            P2 = [reference.getObs(i).position.copy() for i in TP2]
        else:
            P2 = reference
		
        n = len(P1)

        if verbose:
            print("-----------------------------------------------------------------")
            print("NUMBER OF TIE POINTS: " + str(len(TP1)))
            print("-----------------------------------------------------------------")			
            N = int(math.log(self.size())/math.log(10))+1
            for i in range(len(TP1)):
                message = "POINT " + ('{:0'+str(N)+'d}').format(TP1[i]) + "   "  
                message += str(self.getObs(TP1[i]).timestamp) + "   ERROR = "
                message += str('{:10.2f}'.format(P1[i].distance2DTo(P2[i]))) + " m"
                print(message)
            print("-----------------------------------------------------------------")
			
        J = np.zeros((2*n, 4))
        B = np.zeros((2*n, 1))
        X = np.matrix([init[1],init[0],init[2],init[3]]).transpose()
		
		# Iterations
        for iter in range(N_ITER_MAX):
        
            # Current parameters
            k  = X[0,0]        
            tx = X[1,0]
            ty = X[2,0]
            a  = X[3,0]; ca = math.cos(a); sa = math.sin(a)			
            
            for i in range(0,2*n,2):
                x1 = P1[int(i/2)].getX(); y1 = P1[int(i/2)].getY()
                x2 = P2[int(i/2)].getX(); y2 = P2[int(i/2)].getY()
                x2_th = k*(ca*x1-sa*y1)+tx
                y2_th = k*(sa*x1+ca*y1)+ty		
                J[i,0]   = ca*x1-sa*y1;  J[i,1]   = 1;  J[i,2]   = 0;   J[i,3]   = -k*(sa*x1+ca*y1);   B[i]   = x2-x2_th
                J[i+1,0] = sa*x1+ca*y1;  J[i+1,1] = 0;  J[i+1,2] = 1;   J[i+1,3] = +k*(ca*x1-sa*y1);   B[i+1] = y2-y2_th
            	
            dX = np.linalg.solve(J.transpose()@J, J.transpose()@B)
            X = X+dX
			
            cv_param = max(max(max(dX[0,0]*1e4, dX[1,0]*1e4), dX[2,0]*1e4),  dX[3,0]*1e4)
            if (cv_param < 1):
                break               
            
            if verbose:
                N = int(math.log(N_ITER_MAX-1)/math.log(10)) + 1
                message = "ITERATION " + ('{:0'+str(N)+'d}').format(iter) + "  "
                message += "RMSE = " + '{:10.5f}'.format(math.sqrt(B.transpose()@B/(2*n))) + " m    "
                message += "MAX = " + '{:10.5f}'.format(np.max(B)) + " m    "
                print(message)
				
        if verbose:
            print("-----------------------------------------------------------------")
            print("CONVERGENCE REACHED AFTER " + str(iter) + " ITERATIONS")
            glob_res = 0.0
            for l in range(0,2*n,2):
                res = math.sqrt(B[l]**2+B[l+1]**2)
                glob_res += res
                message = "RESIDUAL (2D) POINT " + str(int(l/2)) + ":  "
                message += '{:4.3f}'.format(res) + " m"
                print(message)
            print("GLOBAL 2D RESIDUAL ON TIE POINTS: " + '{:5.3f}'.format(glob_res/n) + " m")
            print("-----------------------------------------------------------------")
            message = "Theta = " + '{:3.2f}'.format(X[3,0]) + " rad   k = " + '{:5.3f}'.format(X[0,0])
            message += "  Tx = " + '{:8.3f}'.format(X[1,0]) + " m  Ty = " + '{:8.3f}'.format(X[2,0]) + " m"
            print(message)
            print("-----------------------------------------------------------------")
		
        self.rotate(X[3,0])
        self.scale(X[0,0])
        self.translate(X[1,0],X[2,0])

        return [X[3,0], X[0,0], X[1,0], X[2,0]]

    # =========================================================================
    #  Adding noise to tracks
    # =========================================================================   
    def noise(self, sigma=5, kernel=Kernel.DiracKernel()):
        return Stochastics.noise(self, sigma, kernel)
        

    # =========================================================================
    # Graphical methods
    # =========================================================================
    def plotAsMarkers(self, size=8, frg='k', bkg='w', sym='+'):
        plt.plot(self.getX(), self.getY(), frg+'o', markersize=size)
        plt.plot(self.getX(), self.getY(), bkg+'o', markersize=int(0.8*size))
        plt.plot(self.getX(), self.getY(), frg+sym, markersize=int(0.8*size))
	
	
    def plot(self, type='LINE', af_name = '', cmap = -1):
        '''
        af_name: test si isAFTransition
        '''
        plot = Plot.Plot(self)
        plot.plot(type, af_name, cmap)
        
        
    def plotProfil(self, template = 'SPATIAL_SPEED_PROFIL', afs = []):
        '''
        Représentation du profil de la trace suivant une AF.
        
        Le nom du template doit respecter:  XXX_YYYY_PROFILE
        avec:
            XXX: SPATIAL ou TEMPORAL
            YYY: ALTI, SPEED ou AF_NAME
        
        Le tableau de nom afs: test si isAFTransition
        '''
        
        nomaxes = template.split('_')
        if len(nomaxes) != 3:
            sys.exit("Error: pour le profil il faut respecter XXX_YYY_PROFIL")
            
        if nomaxes[0] != 'SPATIAL' and nomaxes[0] != 'TEMPORAL':
            sys.exit("Error: pour le profil il faut respecter XXX_YYY_PROFIL avec XXX SPATIAL or TEMPORAL")

        if nomaxes[2] != 'PROFIL':
            sys.exit("Error: pour le profil il faut respecter XXX_YYY_PROFIL")
            
        if nomaxes[1] != 'SPEED' and nomaxes[1] != 'ALTI' and not self.hasAnalyticalFeature(nomaxes[1]):
            sys.exit("Error: pour le profil il faut respecter XXX_YYY_PROFIL avec YYY: ALTI, SPEED or existing AF")
            
        
        plot = Plot.Plot(self)
        plot.plotProfil(template, afs)

        
    def plotAnalyticalFeature(self, af_name, template='BOXPLOT'):
        '''
        TEMPLATE: BOXPLOT
        '''
        plot = Plot.Plot(self)
        plot.plotAnalyticalFeature(af_name, template) 

        
        
    # =========================================================================
    # Track simplification (returns a new track)
    # Tolerance is in the unit of track observation coordinates
    #   MODE_SIMPLIFY_DOUGLAS_PEUCKER (1)
    #   MODE_SIMPLIFY_VISVALINGAM (2)
    # =========================================================================    
    # DEPRECATED
    def simplify(self, tolerance, mode = Simplification.MODE_SIMPLIFY_DOUGLAS_PEUCKER):
        return Simplification.simplify(self, tolerance, mode)
        
    
    # =========================================================================
    #    Built-in Analytical Features 
    # =========================================================================
    def estimate_speed(self, kernel=None):
        '''Compute and return speed for each points
        2nd order time centered time finite difference 
        if raw speeds are required. If kernel is specified  
        smoothed speed estimation is computed.'''
        if kernel is None:
            return self.estimate_raw_speed()
        else:
            return self.smoothed_speed_calculation(kernel)
	
	# DEPRECATED
    def estimate_raw_speed(self):
        return Cinematics.estimate_speed(self)
	
	# DEPRECATED	
    def smoothed_speed_calculation(self, kernel):
        return Cinematics.smoothed_speed_calculation(self, kernel)
        
    def getSpeed(self):
        if self.hasAnalyticalFeature(algoAF.BIAF_SPEED):
            return self.getAnalyticalFeature(algoAF.BIAF_SPEED)
        else:
            sys.exit("Error: 'estimate_speed' has not been called yet")

    # DEPRECATED
    def computeAvgSpeed(self, id_ini=0, id_fin=None):
        '''Computes mean speed (m/s) between two points'''
        if id_fin is None:
            id_fin = self.size()-1
        return Cinematics.computeAvgSpeed(self, id_ini, id_fin)
    
    # DEPRECATED
    def computeAvgAscSpeed(self, id_ini=0, id_fin=None):
        '''
        Computes average ascending speed (m/s)
        TODO : à adapter
        '''
        if id_fin is None:
            id_fin = self.size()-1
        return Cinematics.computeAvgAscSpeed(self, id_ini, id_fin)
    
    # DEPRECATED    
    def compute_abscurv(self):
        '''
        Compute and return curvilinear abscissa for each points
        '''
        return Cinematics.computeAbsCurv(self)
        
    def getAbsCurv(self):
        if self.hasAnalyticalFeature(algoAF.BIAF_ABS_CURV):
            return self.getAnalyticalFeature(algoAF.BIAF_ABS_CURV)
        else:
            sys.exit("Error: 'compute_abscurv' has not been called yet")

    
	# DEPRECATED
    def getCurvAbsBetweenTwoPoints(self, id_ini=0, id_fin=None):
        '''
        Computes and return the curvilinear abscissa between two points
        TODO : adapter avec le filtre
        '''
        if id_fin is None:
            id_fin = self.size()-1
        return Cinematics.computeCurvAbsBetweenTwoPoints(self, id_ini, id_fin)



    # ------------------------------------------------------------
    # Tools to query obs in a track with SQL-like commands
    # Output track is a copy of the original track
	# Blank spaces should be used between each word or symbol
	# Be careful, parenthesis not allowed ! Use De Morgan rules.
	# TO DO: problem with AF transmission (as usual)
    # ------------------------------------------------------------  
    def __condition(val1, operator, val2):
        if isinstance(val1, int):
            val2 = int(val2)
        if isinstance(val1, float):
            val2 = float(val2)
        if operator == "<":
            return val1 < val2
        if operator == ">":
            return val1 > val2
        if operator == "<=":
            return val1 <= val2
        if operator == ">=":
            return val1 >= val2
        if (operator == "=") or (operator == "=="):
            return val1 == val2
        if operator == "!=":
            return val1 != val2				
	
    def query(self, cmd):
	
        cmd = cmd.strip()
        if ("(" in cmd) or ("(" in cmd):
            print("Error: parenthesis not allowed in query. Use De Morgan rules to reformulate query")
            exit()
			
        select_part = cmd.split("SELECT")[1].split("WHERE")[0].strip()
        where_part = cmd.split("WHERE")[1]
		
        if not select_part == "*":
            select_part = select_part.split(",")
            print(select_part)
		
        output = Track()
        BOOL = []		
		
        for i in range(self.size()):
            c0 = where_part.split("OR")
            select_all = False
            for c1 in c0:
                c2 = c1.split("AND")
                select = True
                for c3 in c2:
                    c4 = c3.strip().split(" ")
                    operator = c4[1]
                    select = select and Track.__condition(self[c4[0]][i], operator, c4[2])
                select_all = select_all or select
            BOOL.append(select_all)
			
        for i in range(len(BOOL)):
            if BOOL[i]:
                output.addObs(self[i])
        if select_part == "*":
            return output
  
    # ------------------------------------------------------------
    # Rotation of 2D track (coordinates should be ENU)
	# Input: track in ENU coords and theta angle (in radians)
	# Output: rotated track (in ENU coords)
    # ------------------------------------------------------------  
    def rotate(self, theta):
        if not (self.getSRID() == "ENU"):
            print("Error: track to rotate must be in ENU coordinates")
            exit()
        for i in range(self.size()):
            self.getObs(i).position.rotate(theta)

    # ------------------------------------------------------------
    # Homothetic transformation of 2D track (coordinates in ENU)
	# Input: track in ENU coords and h homothetic ratio
	# Output: scaled track (in ENU coords)
    # ------------------------------------------------------------  
    def scale(self, h):
        if not (self.getSRID() == "ENU"):
            print("Error: track to scale must be in ENU coordinates")
            exit()
        for i in range(self.size()):
            self.getObs(i).position.scale(h)
			
    # ------------------------------------------------------------
    # Translation of 2D track (coordinates in ENU)
	# Input: track in ENU coords and tx, ty translation parameters
	# Output: translated track (in ENU coords)
    # ------------------------------------------------------------  
    def translate(self, tx, ty):
        if not (self.getSRID() == "ENU"):
            print("Error: track to scale must be in ENU coordinates")
            exit()
        for i in range(self.size()):
            self.getObs(i).position.translate(tx, ty)
		
				
    # ------------------------------------------------------------
    # Removal of idle points at the begining or end of track
	# Input: parameter to set and mode in "begin" or "end"
	# Output: cleared track
    # ------------------------------------------------------------ 	
    def removeIdleEnds(self, parameter, mode="begin"):
        track = self.copy() 
        n = track.size()
        if track.size() <= 5:
            return track
        if mode == "begin": 
            init_center = track.extract(0,4).getCentroid()
            for i in range(1,n-4):
                portion = track.extract(i,i+4)
                d = portion.getCentroid().distance2DTo(init_center)
                sdx = portion.operate(Operator.Operator.STDDEV, "x")
                sdy = portion.operate(Operator.Operator.STDDEV, "y")
                sdz = portion.operate(Operator.Operator.STDDEV, "z")						
                if d > parameter + (sdx*sdx+sdy*sdy+sdz*sdz)**0.5:
                    break
            if i == n-5:
                return track
            return track.extract(i-4,n-1)
        if mode == "end":
            init_center = track.extract(n-5,n-1).getCentroid()
            for i in range(n-5,5,-1):
                portion = track.extract(i-4,i)
                d = portion.getCentroid().distance2DTo(init_center)
                sdx = portion.operate(Operator.Operator.STDDEV, "x")
                sdy = portion.operate(Operator.Operator.STDDEV, "y")
                sdz = portion.operate(Operator.Operator.STDDEV, "z")	
                if d > parameter + math.sqrt(sdx*sdx+sdy*sdy+sdz*sdz)**0.5:
                    break
            if i == 5:
                return track
            return track.extract(0,i-4)	
            

    # ------------------------------------------------------------
    # [+] Concatenation of two tracks
    # ------------------------------------------------------------
    def __add__(self, track):
        return Track(self.__POINTS + track.__POINTS, self.uid, self.tid)
        
    # ------------------------------------------------------------
    # [/] Even split of tracks (returns n+1 segments)
    # ------------------------------------------------------------
    def __truediv__(self, number):
        N = (int)(self.size()/number)
        R = self.size()-N*number
        SPLITS = TrackCollection()
        for i in range(number+1):
            id_ini = i*N
            id_fin = min((i+1)*N, self.size())+1
            SPLITS.addTrack(Track(self.__POINTS[id_ini:id_fin]))
        return SPLITS
        
	# ------------------------------------------------------------	
    # [>] Removes first n points of track or time comp    
    # ------------------------------------------------------------	
    def __gt__(self, arg):
        if isinstance(arg, Track):
            t1i = self.getFirstObs().timestamp
            t2f = arg.getLastObs().timestamp            
            return (t1i > t2f)			
        else:
            return Track(self.__POINTS[arg:self.size()], self.uid, self.tid)	
		
	# ------------------------------------------------------------	
    # [<] Removes last n points of track or time comp  
    # ------------------------------------------------------------	
    def __lt__(self, arg):
        if isinstance(arg, Track):
            t1f = self.getLastObs().timestamp
            t2i = arg.getFirstObs().timestamp            
            return (t1f < t2i)
        else:
            return Track(self.__POINTS[0:(self.size()-arg)], self.uid, self.tid)
		
	# ------------------------------------------------------------	
    # [>=] Remove idle points at the start of track or time comp   
    # ------------------------------------------------------------
    def __ge__(self, arg):
        if isinstance(arg, Track):
            t1i = self.getFirstObs().timestamp
            t1f = self.getLastObs().timestamp
            t2i = arg.getFirstObs().timestamp
            t2f = arg.getLastObs().timestamp            
            return ((t1f >= t2f) and (t1i >= t2i))
        else:
            return self.removeIdleEnds(arg, "begin")

	# ------------------------------------------------------------	
    # [<=] Remove idle points at the end of track or time comp    
    # ------------------------------------------------------------
    def __le__(self, arg):
        if isinstance(arg, Track):
            t1i = self.getFirstObs().timestamp
            t1f = self.getLastObs().timestamp
            t2i = arg.getFirstObs().timestamp
            t2f = arg.getLastObs().timestamp            
            return ((t1f <= t2f) and (t1i <= t2i))
        else:
            return self.removeIdleEnds(arg, "end")
		
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
    # [**] Resample according to a number of points  
    # Linear interpolation and temporal resampling
    # ------------------------------------------------------------
    def __pow__(self, nb_points):
        output = self.copy()
        dt = output.duration()/(nb_points) * (1-1e-3)
        output.resample(dt) # Linear / temporal
        return output
	
	# ------------------------------------------------------------	
    # [abs] Available operator     
    # ------------------------------------------------------------
    def __abs__(self):
        return None
		
	# ------------------------------------------------------------	
    # [len] Number of points in track    
    # ------------------------------------------------------------
    def __len__(self):
        return self.size()
	
	# ------------------------------------------------------------	
    # [-] Computes difference profile of 2 tracks    
    # ------------------------------------------------------------
    def __sub__(self, arg):
        if isinstance(arg, int): 
            print("Available operator not implemented yet")
            return None
        else:
            return Comparison.differenceProfile(self, arg)
        
    # ------------------------------------------------------------
    # [*] Temporal resampling of track or track intersections
    # ------------------------------------------------------------
    def __mul__(self, arg):
        if isinstance(arg, Track):
            return Geometrics.intersection(self, arg)
        else:
            track = self.copy()
            dt = (track.frequency("temporal")/arg)*(1-1e-3)
            track.resample(dt)  # Linear / Temporal
            return track
        
    # ------------------------------------------------------------
    # [%] Remove one point out of n (or according to list pattern)
    # ------------------------------------------------------------    
    def __mod__(self, sample):
        if isinstance(sample, int):
            return Track(self.__POINTS[::sample], self.uid, self.tid)
        if isinstance(sample, list):
            track = Track()
            for i in range(self.size()):
                if (sample[i%len(sample)]):
                    track.addObs(self.getObs(i))
            return track
        
    # ------------------------------------------------------------
    # [//] Time resample of a track according to another track
    # ------------------------------------------------------------    
    def __floordiv__(self, track):
        track_resampled = self.copy()
        track_resampled.resample(track, Interpolation.MODE_TEMPORAL)
        return track_resampled    
	
	# ------------------------------------------------------------
    # [[n]] Get and set obs number n (or AF vector with name n)
    # ------------------------------------------------------------    
    def __getitem__(self, n):
        if isinstance(n, str):
            return self.getAnalyticalFeature(n)
        return self.__POINTS[n]  
    def __setitem__(self, n, obs):
        self.__POINTS[n] = obs	