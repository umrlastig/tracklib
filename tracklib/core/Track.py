# -------------------------- Track -------------------------------
# Class to manage GPS tracks
# Points are referenced in geodetic coordinates
# ----------------------------------------------------------------

import sys
import math
import copy
import numpy as np
import matplotlib.pyplot as plt

from tracklib.core.Coords import ENUCoords
from tracklib.core.GPSTime import GPSTime
from tracklib.core.Obs import Obs
import tracklib.core.Operator as Operator
import tracklib.core.Kernel as Kernel
from tracklib.core.TrackCollection import TrackCollection

import tracklib.core.Utils as Utils
import tracklib.algo.Analytics as algoAF
import tracklib.algo.Geometrics as Geometrics
import tracklib.algo.Mapping as Mapping
import tracklib.algo.Cinematics as Cinematics
import tracklib.algo.Stochastics as Stochastics
import tracklib.algo.Comparison as Comparison
import tracklib.algo.Interpolation as Interpolation
import tracklib.algo.Simplification as Simplification

import tracklib.core.Plot as Plot



class Track:

    def __init__(self, list_of_obs=None, user_id=0, track_id=0, base=None):
        '''
        Takes a (possibly empty) list of points as input
        '''
        if not list_of_obs:
            self.__POINTS = []
        else:
            self.__POINTS = list_of_obs
            
        self.uid = user_id
        self.tid = track_id
        self.base = base   # Base (ECEF coordinates) for ENU projection
        
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
        
    # Average frequency    in Hz (resp. m/pt) for temporal (resp. spatial) mode     
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
            if isinstance(base, int):
                self.base = base
            else:
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

    def toProjCoords(self, srid):
        if not (self.getSRID().upper() == "GEO"):
            print("Error: track must be in GEO coordinate for projection to SRID = " + str(srid))
            exit()            
        for i in range(self.size()):
            self.getObs(i).position = self.getObs(i).position.toProjCoords(srid)
        self.base = srid            
          
    # Function to convert 2D coordinates (GEO or ENU) into image local coordinates
    # Input: two points p1, p2 (image coordinates), P1, P2 (track coordinate system)
    # p1 and p2 are provided as lists. P1 and P2 are GeoCoords or ENUCoords.    
    def toImageCoords(self, P1, P2, p1, p2):
        if not (self.getSRID() in ["Geo", "ENU"]):    
            print("Error: track coordinate system must be GEO or ENU for image projection")
            exit()
            
        sx = (p2[0]-p1[0])/(P2.getX() - P1.getX())
        sy = (p2[1]-p1[1])/(P2.getY() - P1.getY())
    
        for i in range(len(self)):
            xi = (self[i].position.getX()-P1.getX())*sx + p1[0]
            yi = (self[i].position.getY()-P1.getY())*sy + p1[1]
            self[i].position = ENUCoords(xi, yi, self[i].position.getZ())    
     
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
    
    def getX(self, i=None):
        if i is None:
            X = []
            for i in range(self.size()):
                X.append(self.__POINTS[i].position.getX())
        else:
            X = self.__POINTS[i].position.getX()
        return X
        
    def getY(self, i=None):
        if i is None:
            Y = []
            for i in range(self.size()):
                Y.append(self.__POINTS[i].position.getY())
        else:
            Y = self.__POINTS[i].position.getY()
        return Y
        
    def getZ(self, i=None):
        if i is None:
            Z = []
            for i in range(self.size()):
                Z.append(self.__POINTS[i].position.getZ())
        else:
            Z = self.__POINTS[i].position.getZ()
        return Z
        
    def getT(self, i=None):
        if i is None:
            T = []
            for i in range(self.size()):
                T.append(self.__POINTS[i].timestamp.toAbsTime())
        else:
            T = self.__POINTS[i].timestamp.toAbsTime()
        return T
    
    def getTimestamps(self, i=None):
        if i is None:
            T = []
            for i in range(self.size()):
                T.append(self.__POINTS[i].timestamp)
        else:
            T = self.__POINTS[i].timestamp
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
                  
    # Internal methods
    def __transmitAF(self, track):
        self.__analyticalFeaturesDico = track.__analyticalFeaturesDico.copy()
    
    def hasAnalyticalFeature(self, af_name):
        return (af_name in self.__analyticalFeaturesDico) or (af_name in ["x","y","z","t","timestamp"])

    def getAnalyticalFeatures(self, af_names): 
        af_names = Utils.listify(af_names) 
        output = []
        for af in af_names:
            output.append(self.getAnalyticalFeature(af))
        return output    
 
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
        if af_name == "timestamp":
            for i in range(self.size()):
                AF.append(self.__POINTS[i].timestamp)
            return AF
        if not self.hasAnalyticalFeature(af_name):
            sys.exit("Error: track does not contain analytical feature '" + af_name +"'")
        index = self.__analyticalFeaturesDico[af_name]
        for i in range(self.size()):
            AF.append(self.__POINTS[i].features[index])
        return AF    
  
    def getObsAnalyticalFeatures(self, af_names, i):
        af_names = Utils.listify(af_names)
        output = []
        for af in af_names:
            output.append(self.getObsAnalyticalFeature(af, i))
        return output    

    def getObsAnalyticalFeature(self, af_name, i):
        if af_name == "x":
            return self.getObs(i).position.getX()
        if af_name == "y":
            return self.getObs(i).position.getY()
        if af_name == "z":
            return self.getObs(i).position.getZ()
        if af_name == "t":
            return self.getObs(i).timestamp.toAbsTime()
        if af_name == "timestamp":
            return self.getObs(i).timestamp
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
			
    def setOrder(self, name="order", start=0):
        self.createAnalyticalFeature("order", list(range(start, start+self.size())))    
    
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
        if len(self.getListAnalyticalFeatures()) > 0:
            output += "Analytical feature(s):"
            for i in range(len(self.getListAnalyticalFeatures())):
                output += "\n - "+self.getListAnalyticalFeatures()[i] 
            output += "\n-------------------------------------\n"                        
        print(output)
        
        
    def length(self):
        '''
        Total length of curvilinear abscissa
        '''
        s = 0
        for i in range(1,self.size()):
            s += self.getObs(i-1).distanceTo(self.getObs(i))
        return s
        
    # DEPRECATED
    def computeNetDeniv(self, id_ini=0, id_fin=None):
        '''
        Computes net denivellation (in meters)
        '''
        if id_fin is None:
            id_fin = track.size()-1
        return Cinematics.computeNetDeniv(self, id_ini, id_fin)

    # DEPRECATED
    def computeAscDeniv(self, id_ini=0, id_fin=None):
        '''Computes positive denivellation (in meters)'''        
        if id_fin is None:
            id_fin = track.size()-1
        return  computeAscDeniv(self, id_ini, id_fin)
    
     # DEPRECATED   
    def computeDescDeniv(self, id_ini=0, id_fin=None):
        '''Computes negative denivellation (in meters)'''
        if id_fin is None:
            id_fin = track.size()-1 
        return Cinematics.computeDescDeniv(self, id_ini, id_fin)
        
   
   # DEPRECATED
    def toWKT(self):
        '''Transforms track into WKT string'''
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
        track = Track(base=self.base)
        track.setUid(self.uid)
        for k in range(id_ini, id_fin+1):
            track.addObs(self.__POINTS[k])
        track.__transmitAF(self)
        return track
        

    def extractSpanTime(self, tini, tfin=None):
        '''
        Extract span time from a track
        tini: Initial time of extraction
        tfin: final time of extraction
        '''
		
        # Special case: track passed as input
        if isinstance(tini, Track) and (tfin is None):
            return self.extractSpanTime(tini[0].timestamp, tini[-1].timestamp)
            			
        if (tini > tfin):
            ttemp = tini
            tini = tfin
            tfin = ttemp
        track = Track([], self.uid, base=self.base)
        for k in range(self.size()):
            if (self.__POINTS[k].timestamp < tini):
                continue
            if (self.__POINTS[k].timestamp > tfin):
                continue
            track.addObs(self.__POINTS[k].copy())
        track.__transmitAF(self)
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
        if (name in ["x", "y", "z", "t", "timestamp"]):
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
                value = Utils.NAN
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
            
			
    # -------------------------------------------------------------------------
    # General function to perform computations on analytical features
    # -------------------------------------------------------------------------
    # Case 1 : operator and operand listed separately
    #    - operator : to be selected in Operator class
    #    	-> Unary void operator  : arg2 = F(arg1), arg1, arg2 must be provided	
    #    	-> Binary void operator : arg3 = F(arg1, arg2)
    #       -> Unary operator  :  F(arg1), arg1 must be provided	 	
	#       -> Binary operator :  F(arg1, arg2), arg1, arg2 must be provided
    # Note that arg2 may be an AF name or a scalar value. When output AF name 
	# is not provided, it is automatically set as the first AF input in the 
	# formula. AF "x", "y", "z", "t" and "timestamp" are right away available
	# as "virtual" analytical features.
	# -------------------------------------------------------------------------
	# Case 2 : operator and operand listed in an algebraic expression
	# arg1 defines the algebraic expression. If this expression contains '=' 
	# sign, then output is registered as an AF in track, with name defined by 
	# the left-hand side of arg1. For example : track.operate("P=X+Y") performs
	# the sum of AFs X and Y, and returns the result as an AF named P in track.
	#   - Available operators : +, -, /, *, ^ in scalar and AF versions. 
	#   - Available functions : almost all those listed in Operator class
    #   - Functions are expressed with '{}'. E.g: track.operate("P=LOG{X}")
	#   - Special shorthand functions: D for differentiation, I for integration
	#     D2 for second-order differentiation and >> (resp. <<) for advance 
	#     (resp. delay) scalar operators. E.g: track.operate("v=3.6*D{s}/D{t}") 
	#     performs speed computation (in km/h), provided that curvilinear 
	#     abscissa s is already ddefined inside track. It is equivalent to the 
	#     somehow more sophisticated following version with delay operator: 
	#     track.operate("v=3.6*(s-(s>>1))/(t-(t>>1))") 
	#   - It is possible to add external identificator to the computations by 
	#     using passing a dictionnary of variables in arg2. For example, to 
    #     divide an AF A in a track by a (beforehand unknown) variable var:
    #     track.operate("A=A/factor", {'factor' : var}])
    # -------------------------------------------------------------------------		
    def operate(self, operator, arg1=None, arg2=None, arg3=None):

        # Algebraic expression (arg1 = list of externals)
        if isinstance(operator, str):
            if arg1 is None:
                arg1 = []
            output = self.__evaluate(operator, arg1)	
            SUPPRESS_AF = self.getListAnalyticalFeatures()
            for af in SUPPRESS_AF:
                if (af[0] == "#"):
                    self.removeAnalyticalFeature(af)     
            return output			
		
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
    # Return a reversed track (based on index)
    # Important: track may not be valid for some other functions
    # Used mostly to simplify backward kalman filter formulation
    # =========================================================================
    def reverse(self):
        output = self.copy()
        output.__POINTS = output.__POINTS[::-1]
        return output

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
    
    def incrementTime(self, dt=1, offset=0):  
        '''Add 1 sec to each subsequent record. Use incrementTime to 
        get valid timestamps sequence when timestamps are set as default 
        date on 1970/01/01 00:00:00 for example''' 
        for i in range(len(self)):
            self.getObs(i).timestamp = self.getObs(i).timestamp.addSec(i*dt + offset)
        
        
    # DEPRECATED
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

        return Mapping.mapOn(self, reference, TP1, TP2, init, N_ITER_MAX, mode, verbose)

    # =========================================================================
    #  Adding noise to tracks
    # =========================================================================   
    def noise(self, sigma=5, kernel=Kernel.DiracKernel()):
        return Stochastics.noise(self, sigma, kernel)
        

    # =========================================================================
    # Graphical methods
    # =========================================================================
    def plotAsMarkers(self, size=8, frg='k', bkg='w', sym_frg='+', sym_bkg='o', type=None):
        if not type is None:
            if type == Plot.MARKERS_TYPE_NO_ENTRY:
                frg='w'; bkg='r'; sym_frg='_'; sym_bkg='o'
            if type == Plot.MARKERS_TYPE_INTERDICTION:
                frg='w'; bkg='r'; sym_frg='.'; sym_bkg='o'
            if type == Plot.MARKERS_TYPE_SPOT:
                frg='r'; bkg='w'; sym_frg='.'; sym_bkg='o'
            if type == Plot.MARKERS_TYPE_WARNING:
                frg='r'; bkg='w'; sym_frg=' '; sym_bkg='^'
            if type == Plot.MARKERS_TYPE_GIVE_WAY:
                frg='r'; bkg='w'; sym_frg=' '; sym_bkg='v'
            if type == Plot.MARKERS_TYPE_NO_STOP:
                frg='r'; bkg='b'; sym_frg='x'; sym_bkg='o'
            if type == Plot.MARKERS_TYPE_INFORMATION:
                frg='b'; bkg='w'; sym_frg=' '; sym_bkg='s'

        plt.plot(self.getX(), self.getY(), frg+sym_bkg, markersize=size)
        plt.plot(self.getX(), self.getY(), bkg+sym_bkg, markersize=int(0.8*size))
        plt.plot(self.getX(), self.getY(), frg+sym_frg, markersize=int(0.8*size))
    
    		
    # ----------------------------------------------------
	# Method to plot a track (short cut from Plot)
	# Append:
	#  - True : append to the current plot
	#  - False: create a new plot
	#  - Ax   : append to the fiven ax object 
	# ----------------------------------------------------
	# Output:
	#  Ax object (may be input into append parameter)
	# ----------------------------------------------------
    def plot(self, sym='k-', type='LINE', af_name = '', cmap = -1, append=True):
        '''
        af_name: test si isAFTransition
        '''
        plot = Plot.Plot(self)
        plot.sym = sym
        plot.w = 6
        plot.h = 5
        return plot.plot(type, af_name, cmap, append=append)
		
    # ----------------------------------------------------
	# Plot track uncertainty (as error ellipses)
	# Input track must contain an AF with (at least) a 
	# 2 x 2 covariance matrix. If this matrix has dim > 2,
	# first two dimensions are arbitrarily considered
	# ----------------------------------------------------
    def plotEllipses(self, sym='r-', factor=3, af=None, append=True):
        plot = Plot.Plot(self)
        plot.sym = sym
        plot.w = 6
        plot.h = 5
        return plot.plotEllipses(self, sym, factor, af, append)
        
    def plotProfil(self, template = 'SPATIAL_SPEED_PROFIL', afs = []):
        '''
        Représentation du profil de la trace suivant une AF.
        
        Le nom du template doit respecter:  XXX_YYYY_PROFILE
        avec:
            XXX: SPATIAL ou TEMPORAL
            YYY: ALTI, SPEED ou AF_NAME
        
        Le tableau de nom afs: teste si isAFTransition
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



    # ----------------------------------------------------------------------------------------------------
    # Tools to query observations in a track with SQL-like commands. Output depends on the SELECT clause:
    #     - If "SELECT *" then output is a copied track of the original track (with all its AF hopefully)
    #     - If "SELECT f1, f2... fp", then output is a (p x n)-dimensional array, with p = number of fields 
    #       queried and n = number of observations selected by the WHERE conditions.
    #     - If "SELECT AGG1(f1), AGG2(f2)... AGGp(fp)", with AGG1, AGG2,.. AGGp, a set of p aggregators, 
    #       then output is a p-dimensional array, with on value for each aggregator
    #     - If "SELECT AGG(f)", then output is the floating point value returned by the operator.
    # Note that operators take as input only analytical feature names. Therefore, "SELECT COUNT(*)" syntax 
    # is not allowed and must be replaced equivalently by "SELECT COUNT(f)" with any AF name f.
    # General rules: 
    #     - Only SELECT and WHERE keywords (SET and DELETE available soon)
    #     - All analytical features + x, y, z, t, and timestamp are available as fields
    #     - Fields are written without quotes. They must not contain blank spaces
    #     - "t" is time as integer in seconds since 1970/01/01 00:00:00, and "timestamp" is GPSTIme object
    #     - Blank space must be used between every other words, symbols and operators
    #     - WHERE clause may contain as many conditions as needed, separated by OR/AND key words
    #     - Parenthesis are not allowed within WHERE clause. Use boolean algebra rules to reformulate 
    #       query without parenthesis: e.g. A AND (B OR C) = A AND B OR A AND C. Or use successive queries.
    #     - Each condition must contain exactly 3 parts (separated by blank spaces) in this exact order:
    #         (1) the name of an analytical feature to test
    #         (2) a comparison operator among >, <, >=, <=, ==, != and LIKE (with % in str and timestamps)
    #         (3) a threshold value which is automatically casted to the type of the AF given in (1). 
    #             Intended types accepted are: integers, floats, strings, boolean and GPSTime. 
    #             When GPSTime is used as a threshold value, eventhough it may contain 2 parts 
    #            (date and time), it must not be enclosed within quotes. For boolean, "1", "T" and "TRUE"
    #             are considered as logical True, all other values are considered as False.    
    #     - Important: no computation allowed in WHERE conditions. E.g. "... WHERE z-2 > 10" not allowed
    #     - Available aggregators: all unary operators as described in Operator.py, except MSE
    #     - Capital letters must be used for SQL keywords SELECT, WHERE, AND, OR and aggregators 
    # ----------------------------------------------------------------------------------------------------
    def __condition(val1, operator, val2):

        if operator == "LIKE":
            return Utils.compLike(str(val1), val2)

        if isinstance(val1, int):
            val2 = int(val2)
        if isinstance(val1, float):
            val2 = float(val2)
        if isinstance(val1, GPSTime):
            val2 = GPSTime.readTimestamp(val2)
        if isinstance(val1, bool):
            val2 = (val2.upper == "TRUE") or (val2.upper == "T") or (val2 == "1")
            
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
        
        AGG = ["SUM", "AVG", "COUNT", "VAR", "MEDIAN", "ARGMIN", "ARGMAX", "MIN", "MAX", "RMSE", "MAD", "STDDEV", "ZEROS"]
            
        select_part = cmd.split("SELECT")[1].split("WHERE")[0].strip()
        
        if not select_part == "*":
            select_part = select_part.split(",")
            aggregator = []
            for i  in range(len(select_part)):
                for j in range(len(AGG)):
                    if ((AGG[j]+"(") in select_part[i]):
                        aggregator.append(j)
                        select_part[i] = select_part[i].strip()[len(AGG[j])+1:-1]
                        break
           
        temp = cmd.split("WHERE")
        if len(temp) < 2:
            where_part = -1
        else:
            where_part = temp[1]
            if ("(" in where_part) or ("(" in where_part):
                message = "Error: parenthesis not allowed in conditions."
                message += "Use boolean algebra rules to reformulate query or use successive queries"
                print(message)
                exit()
        
        if not select_part == "*":
            LAF = []
            for i in range(len(select_part)):
                LAF.append([])
        
        output = Track()
        BOOL = []        
        
        for i in range(self.size()):
            if where_part== -1:
                select_all = True
            else:
                c0 = where_part.split("OR")
                select_all = False
                for c1 in c0:
                    c2 = c1.split("AND")
                    select = True
                    for c3 in c2:
                        c4 = c3.strip().split(" ")
                        operator = c4[1]
                        for k in range(3,len(c4)):
                            c4[2] += " " + c4[k]
                        select = select and Track.__condition(self[c4[0]][i], operator, c4[2])
                    select_all = select_all or select
            BOOL.append(select_all)
             
        if select_part == "*":            
            for i in range(len(BOOL)):
                if BOOL[i]:
                    output.addObs(self[i])
            output.__analyticalFeaturesDico = self.__analyticalFeaturesDico.copy()
            return output
        else:
            for i in range(len(BOOL)):
                if BOOL[i]:
                    for j in range(len(select_part)):
                        LAF[j].append(self[select_part[j].strip()][i])
                
     
            if len(aggregator) == 0:
                return LAF
                
            OUTPUT = []
            for af in range(len(LAF)):
                AF = LAF[af]
                if AGG[aggregator[af]] == "COUNT":
                    OUTPUT.append(len(AF))
                if (len(aggregator) > 0) and (len(AF) == 0):
                    return None
                if (len(aggregator) > 0) and (len(AF) > 0):
                    tmp = Track()
                    for i in range(len(AF)):
                        tmp.addObs(Obs(ENUCoords(0,0,0)))
                    tmp.createAnalyticalFeature("#tmp", AF)
                    if AGG[aggregator[af]] == "SUM":
                        OUTPUT.append(tmp.operate(Operator.Operator.SUM, "#tmp"))
                    if AGG[aggregator[af]] == "AVG":
                        OUTPUT.append(tmp.operate(Operator.Operator.AVERAGER, "#tmp"))
                    if AGG[aggregator[af]] == "VAR":
                        OUTPUT.append(tmp.operate(Operator.Operator.VARIANCE, "#tmp")) 
                    if AGG[aggregator[af]] == "MEDIAN":
                        OUTPUT.append(tmp.operate(Operator.Operator.MEDIAN, "#tmp")) 
                    if AGG[aggregator[af]] == "MIN":
                        OUTPUT.append(tmp.operate(Operator.Operator.MIN, "#tmp")) 
                    if AGG[aggregator[af]] == "MAX":
                        OUTPUT.append(tmp.operate(Operator.Operator.MAX, "#tmp")) 
                    if AGG[aggregator[af]] == "RMSE":
                        OUTPUT.append(tmp.operate(Operator.Operator.RMSE, "#tmp")) 
                    if AGG[aggregator[af]] == "STDDEV":
                        OUTPUT.append(tmp.operate(Operator.Operator.STDDEV, "#tmp")) 
                    if AGG[aggregator[af]] == "ARGMIN":
                        OUTPUT.append(tmp.operate(Operator.Operator.ARGMIN, "#tmp"))
                    if AGG[aggregator[af]] == "ARGMAX":
                        OUTPUT.append(tmp.operate(Operator.Operator.ARGMAX, "#tmp"))
                    if AGG[aggregator[af]] == "ZEROS":
                        OUTPUT.append(tmp.operate(Operator.Operator.ZEROS, "#tmp"))
                    if AGG[aggregator[af]] == "MAD":
                        OUTPUT.append(tmp.operate(Operator.Operator.MAD, "#tmp"))
            
            if (len(OUTPUT) == 1):
                return OUTPUT[0]            

            return OUTPUT            
   
    # ------------------------------------------------------------ 
    #   Applying operators through algebraic expressions
    # ------------------------------------------------------------
    
    def __makeRPN(expression):
        s = expression
        for operator in ["=", "+-", "*/", "^", "@", "&$"]:
            depth = 0
            for p in range(len(s) - 1, -1, -1):
                if s[p] == ')': depth += 1
                if s[p] == '(': depth -= 1
                if not depth and s[p] in operator:
                    return (Track.__makeRPN(s[:p]) + Track.__makeRPN(s[p+1:])) + [s[p]]
        s = s.strip()
        if s[0] == '(':
            return Track.__makeRPN(s[1:-1])
        return [s]  

    def __applyOperation(self, op1, op2, operator, temp_af_counter):
        # Handling special case of affectation
        if operator == "=":
            if self.hasAnalyticalFeature(op2):
                if self.hasAnalyticalFeature(op1):
                    if op1 in ["x", "y", "z", "t"]:
                        if op1 == "x":
                            self.setXFromAnalyticalFeature(op2)
                        if op1 == "y":
                            self.setYFromAnalyticalFeature(op2)
                        if op1 == "z":
                            self.setZFromAnalyticalFeature(op2)
                        if op1 == "t":
                            self.setTFromAnalyticalFeature(op2)
                        self.removeAnalyticalFeature(op2)
                    else:
                        AF = self.getAnalyticalFeature(op2)
                        self.removeAnalyticalFeature(op1)
                        self.createAnalyticalFeature(op1, AF)
                else:
                    self.createAnalyticalFeature(op1, self.getAnalyticalFeature(op2))
            else:
                self.createAnalyticalFeature(op1, float(op2))
            return
        
		# Floating point operation
        if Utils.isfloat(op1) and Utils.isfloat(op2):
            op1 = float(op1)
            op2 = float(op2)
            if operator == "+":
                return op1 + op2
            if operator == "-":
                return op1 - op2
            if operator == "*":
                return op1 * op2
            if operator == "/":
                return op1 / op2
            if operator == "^":
                return op1 ^ op2

		# Functional operator
        if operator == "@":
            out_af = "#"+str(temp_af_counter)
            if op1 in Operator.Operator.NAMES_DICT_VOID:
                self.operate(Operator.Operator.NAMES_DICT_VOID[op1], op2, out_af)
                return out_af
            if op1 in Operator.Operator.NAMES_DICT_NON_VOID:
                out = self.operate(Operator.Operator.NAMES_DICT_NON_VOID[op1], op2)
                self.createAnalyticalFeature(out_af, [out]*self.size())
                return out_af			
            print("Function '"+op1+ "' is unknown")
            exit(1)                

        op1IsAF = self.hasAnalyticalFeature(op1)
        op2IsAF = self.hasAnalyticalFeature(op2)

        # [AF operator AF] case
        if op1IsAF and op2IsAF:
            out_af = "#"+str(temp_af_counter)
            self.operate(Operator.Operator.NAMES_DICT_VOID[operator], op1, op2, out_af)
            return out_af 

        # [AF operator float] case
        if (op1IsAF and not op2IsAF):	
            out_af = "#"+str(temp_af_counter)
            self.operate(Operator.Operator.NAMES_DICT_VOID["s"+operator], op1, float(op2), out_af)
            return out_af   

        # [float operator AF] case
        if (op2IsAF and not op1IsAF):		
            out_af = "#"+str(temp_af_counter)
            self.operate(Operator.Operator.NAMES_DICT_VOID["sr"+operator], op2, float(op1), out_af)
            return out_af 			

        print("Invalid operator "+str(operator)+ " for operands "+str(op1)+ " and "+str(op2))
        exit(1)		
		
    def __evaluateRPN(self, expression, external=[]):
        stack = []
        operators = ["=", "+", "-", "*", "/", "^", "@", "&", "$"]
        temp_af_counter = 0
		
		# Stack computation
        for e in expression:
            # print("STACK = ", stack)   # DEBUG LINE
            if e in operators:
                operand2 = stack.pop()
                operand1 = stack.pop()
                stack.append(self.__applyOperation(operand1, operand2, e, temp_af_counter))
                temp_af_counter += 1
                continue
            if e in external:
                e = external[e]
            stack.append(e)
        return expression

    def __evaluate(self, expression, external=[]):
        expression = expression.replace("{", "@(").replace("}", ")")
        expression = expression.replace(">>", "&").replace("<<", "$")
        for f_name in Operator.Operator.NAMES_DICT_VOID:
            if f_name[-1] in ['+', '-', '*', '/', '^']:
                continue
            expression = expression.replace(f_name+"(", f_name+"@(")
        for f_name in Operator.Operator.NAMES_DICT_NON_VOID:
            if f_name[-1] in ['+', '-', '*', '/', '^']:
                continue
            expression = expression.replace(f_name+"(", f_name+"@(")
        void = ("=" in expression)
        if not void:
            expression = "#output = "+ expression
        self.__evaluateRPN(Track.__makeRPN(expression), external)
        if not void:
            output = self.getAnalyticalFeature("#output")
            self.removeAnalyticalFeature("#output")
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
    # Rotation of 3D track (coordinates should be ENU/ECEF)
    # Input: 
	#   - track in ENU/ECEF coords
	#   - 3x3 rotation matrix
    # Output: rotated track (in ENU/ECEF coords)
    # ------------------------------------------------------------  
    def rotate3D(self, R):
        if not (self.getSRID() in ["ENU", "ECEF"]):
            print("Error: track to scale must be in ENU/ECEF coordinates")
            exit()
        for i in range(self.size()):
            x = self.getObs(i).position.getX()
            y = self.getObs(i).position.getY()
            z = self.getObs(i).position.getZ()
            self.getObs(i).position.setX(R[0,0]*x + R[0,1]*y + R[0,2]*z)
            self.getObs(i).position.setY(R[1,0]*x + R[1,1]*y + R[1,2]*z)
            self.getObs(i).position.setZ(R[2,0]*x + R[2,1]*y + R[2,2]*z)

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
    # Homothetic transformation of 3D track (coords in ENU/ECEF)
    # Input: 
	#   - track in ENU/ECEF coords
	#   - h homothetic ratio
	#   - center in ENU/ECEF coords (default is centroid)
    # Output: scaled track (in ENU coords)
    # ------------------------------------------------------------  
    def scale3D(self, h, center=None):
        if not (self.getSRID() in ["ENU", "ECEF"]):
            print("Error: track to scale must be in ENU/ECEF coordinates")
            exit()
        if center is None:
            center = self.getCentroid()
        cx = center.getX()
        cy = center.getY()
        cz = center.getZ()
        for i in range(self.size()):
            x = self.getObs(i).position.getX()
            y = self.getObs(i).position.getY()
            z = self.getObs(i).position.getZ()
            self.getObs(i).position.setX(cx + h*(x-cx))
            self.getObs(i).position.setY(cy + h*(y-cy))
            self.getObs(i).position.setZ(cz + h*(z-cz))
            
    # ------------------------------------------------------------
    # Translation of 3D track (coordinates in ENU)
    # Input: track in ENU coords and tx, ty translation parameters
    # Output: translated track (in ENU coords)
    # ------------------------------------------------------------  
    def translate(self, tx, ty, tz=0):
        if not (self.getSRID() == "ENU"):
            print("Error: track to scale must be in ENU coordinates")
            exit()
        for i in range(self.size()):
            self.getObs(i).position.translate(tx, ty, tz)

    # ------------------------------------------------------------
    # Symmetric transformation of 2D track based on an axis x=c, 
	# y=c or z=c. Track must be provided in ENU or ECEF coords
    # Input: dimension (x=0, y=1, z=2) and value c (default 0).
    # Output: translated track (in ENU r ECEF coords)
    # ------------------------------------------------------------  
    def symmetrize(self, dim, val=0):
        if not (self.getSRID() in ["ENU", "ECEF"]):
            print("Error: track to scale must be in ENU/ECEF coordinates")
            exit()
        for i in range(self.size()):
            if (dim == 0) or (dim in ["x", "X", "E"]):
                self.getObs(i).position.setX(val-self.getObs(i).position.getX())        
            if (dim == 1) or (dim in ["y", "Y", "N"]):
                self.getObs(i).position.setY(val-self.getObs(i).position.getY())  
            if (dim == 2) or (dim in ["z", "Z", "U"]):
                self.getObs(i).position.setZ(val-self.getObs(i).position.getZ())    
				
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
        t1 = self   # copy (long) ?
        t2 = track  # copy (long) ?
        AF1 = self.getListAnalyticalFeatures()
        AF2 = track.getListAnalyticalFeatures()
        track = Track(t1.__POINTS + t2.__POINTS, t1.uid, t1.tid, base=t1.base)
        same = True
        if len(AF1) != len(AF2):
            same = False
        else:
            for i in range(len(AF1)):
                same = same and (AF1[i] == AF2[i])
        if same:
            track.__transmitAF(self)        
        return track
        
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
            portion = Track(self.__POINTS[id_ini:id_fin], base=self.base)
            portion.__transmitAF(self)
            SPLITS.addTrack(portion)
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
            output = Track(self.__POINTS[arg:self.size()], self.uid, self.tid, self.base)
            output.__transmitAF(self)
            return output
        
    # ------------------------------------------------------------    
    # [<] Removes last n points of track or time comp  
    # ------------------------------------------------------------    
    def __lt__(self, arg):
        if isinstance(arg, Track):
            t1f = self.getLastObs().timestamp
            t2i = arg.getFirstObs().timestamp            
            return (t1f < t2i)
        else:
            output = Track(self.__POINTS[0:(self.size()-arg)], self.uid, self.tid, self.base)
            output.__transmitAF(self)
            return output
        
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
            track = Track(self.__POINTS[::sample], self.uid, self.tid, base=self.base)
            track.__transmitAF(self)
            return track
        if isinstance(sample, list):
            track = Track(base=self.base)
            for i in range(self.size()):
                if (sample[i%len(sample)]):
                    track.addObs(self.getObs(i))
            track.__transmitAF(self)
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
	# If n is tuple ["af", index] or [index, "af"]
	# If argument is a string starting with "$", it's interpreted
	# as an algebraic operation on analytical features.
    # ------------------------------------------------------------    
    def __getitem__(self, n):
        if isinstance(n, tuple):
            if isinstance(n[0], str):
                return self.getObsAnalyticalFeature(n[0], n[1])
            else: 
                return self.getObsAnalyticalFeature(n[1], n[0])
        if isinstance(n, str):
            n = n.strip()
            if ("+" in n) or ("-" in n) or ("/" in n) or ("*" in n) or ("^" in n):
                return self.operate(n)		
            if (">>" in n) or ("<<" in n) or ("(" in n) or (")" in n):	
                return self.operate(n)				
            return self.getAnalyticalFeature(n)
		
        return self.__POINTS[n]  
    def __setitem__(self, n, obs):
        self.__POINTS[n] = obs    