# --------------------------- Analytics ---------------------------------------
# Class to manage general operations on a track
# -----------------------------------------------------------------------------
import sys
import math
import copy
import numpy as np
import random
import matplotlib.pyplot as plt

from tracklib.core.Obs import Obs
from tracklib.core.Coords import ENUCoords
from tracklib.core.GPSTime import GPSTime

import tracklib.core.Track as Track
import tracklib.core.Utils as Utils
import tracklib.core.Operator as Operator
import tracklib.core.TrackCollection as TrackCollection

import tracklib.algo.Interpolation as interp

MODE_ENCLOSING_BBOX = 0
MODE_ENCLOSING_MBR = 1
MODE_ENCLOSING_CIRCLE = 2
MODE_ENCLOSING_CONVEX = 3


class Circle:

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        
    def plot(self, sym='r-'):
        X = [0]*100
        Y = [0]*100
        for t in range(len(X)-1):
            X[t] = self.radius*math.cos(2*math.pi*t/len(X)) + self.center.getX()
            Y[t] = self.radius*math.sin(2*math.pi*t/len(Y)) + self.center.getY()
        X[len(X)-1] = X[0]
        Y[len(Y)-1] = Y[0]
        plt.plot(X, Y, sym)
        
    def contains(self, point):
        return (point.getX()-self.center.getX())**2 + (point.getX()-self.center.getY())**2 <= self.radius**2
        
    def copy(self):
        return copy.deepcopy(self)
        
    def translate(self, dx, dy):
       self.center.translate(dx, dy)    
       
class Rectangle:

    def __init__(self, pmin, pmax):
        self.pmin = pmin
        self.pmax = pmax 
        
    def plot(self, sym='r-'):        
        XR = [self.pmin.getX(), self.pmax.getX(), self.pmax.getX(), self.pmin.getX(), self.pmin.getX()]
        YR = [self.pmin.getY(), self.pmin.getY(), self.pmax.getY(), self.pmax.getY(), self.pmin.getY()]
        plt.plot(XR, YR, sym)
        
    def contains(self, point):
        inside_x = (self.pmin.getX() < point.getX()) and (point.getX() < self.pmax.getX())
        inside_y = (self.pmin.getY() < point.getY()) and (point.getY() < self.pmax.getY())
        return inside_x and inside_y

    def copy(self):
        return copy.deepcopy(self)
        
    # --------------------------------------------------
    # Translation (2D) of shape (dx, dy in ground units)
    # --------------------------------------------------
    def translate(self, dx, dy):
       self.pmin.translate(dx, dy)    
       self.pmax.translate(dx, dy)
       
    # --------------------------------------------------
    # Rotation (2D) of shape (theta in radians)
    # --------------------------------------------------
    def rotate(self, theta):
        self.pmin = self.pmin.rotate(theta)
        self.pmax = self.pmax.rotate(theta)
    
    # --------------------------------------------------
    # Homotehtic transformation (2D) of shape
    # --------------------------------------------------
    def scale(self, h):
        self.pmin = self.pmin.scale(h)
        self.pmax = self.pmax.scale(h)

class Polygon:

    def __init__(self, X, Y):
        self.X = X
        self.Y = Y
        if not ((self.X[-1] == self.X[0]) and (self.Y[-1] == self.Y[0])):
            self.X.append(self.X[0])
            self.Y.append(self.Y[0])
            
    def plot(self, sym='r-'):
        plt.plot(self.X, self.Y, sym)
        
    def contains(self, point):
        return inclusion(self.X, self.Y, point.getX(), point.getY())
        
    def copy(self):
        return copy.deepcopy(self) 

    # --------------------------------------------------
    # Translation (2D) of shape (dx, dy in ground units)
    # --------------------------------------------------
    def translate(self, dx, dy):
       for i in range(len(self.X)):
           self.X[i] = self.X[i] + dx
           self.Y[i] = self.Y[i] + dy    
           
    # --------------------------------------------------
    # Rotation (2D) of shape (theta in radians)
    # --------------------------------------------------
    def rotate(self, theta):
        cr = math.cos(theta)
        sr = math.sin(theta)
        for i in range(len(self.X)):
            xr = +cr*self.X[i] - sr*self.Y[i]
            yr = +sr*self.X[i] + cr*self.Y[i]
            self.X[i] = xr
            self.Y[i] = yr
    
    # --------------------------------------------------
    # Homotehtic transformation (2D) of shape
    # --------------------------------------------------
    def scale(self, h):
        for i in range(len(self.X)):
            self.X[i] *= h
            self.Y[i] *= h
        
# --------------------------------------------------------
# Fonction booleenne d'inlcusion d'un pt dans un polygone
# Un polygone est defini comme une liste de points :
# --------------------------------------------------------
def inclusion(X, Y, x, y):
    
    cmax = 2*max(np.max(X), np.max(Y))
    segment = list()
    
    segment.append(x)
    segment.append(y)
    segment.append(cmax)
    segment.append(cmax)
    
    n = 0  # Number of intersections
    
    for i in range(len(X)-1):
        
        edge = list()
        edge.append(X[i])
        edge.append(Y[i])
        edge.append(X[i+1])
        edge.append(Y[i+1])
        
        if __intersects(segment, edge):
            n += 1
            
    return (n % 2 == 1)

def __right(a,b,c):
    return ((a == c) or (b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]) < 0)
    
# ----------------------------------------
# Function to get enclosing shape
# ----------------------------------------
def boundingShape(track, mode=MODE_ENCLOSING_BBOX):
    if mode == MODE_ENCLOSING_BBOX:
        return track.getBBox()
    if mode == MODE_ENCLOSING_MBR:
        return minimumBoundingRectangle(track)
    if mode == MODE_ENCLOSING_CIRCLE:
        return minCircle(track)
    if mode == MODE_ENCLOSING_CONVEX:
        return convexHull(track)

# ----------------------------------------
# Fonction equation cartesienne
# Entree : segment
# Sortie : liste de parametres (a,b,c)
# ----------------------------------------
def __cartesienne(segment):
    
    parametres = list();
    
    x1 = segment[0]
    y1 = segment[1]
    x2 = segment[2]
    y2 = segment[3]
    
    u1 = x2-x1
    u2 = y2-y1
    
    b = -u1
    a = u2
    
    c = -(a*x1+b*y1)
    
    parametres.append(a)
    parametres.append(b)
    parametres.append(c)
    
    return parametres        

# ----------------------------------------
# Fonction de test d'equation de droite
# Entrees : paramatres et coords (x,y)
# Sortie : en particulier 0 si le point 
# appartient a la droite
# ----------------------------------------
def __eval(param, x, y):
    
    a = param[0]
    b = param[1]
    c = param[2]
    
    return a*x+b*y+c

# ----------------------------------------
# Fonction booleenne d'intersection
# Entrees : segment1 et segment2
# Sortie : true s'il y a intersection
# ----------------------------------------
def __intersects(segment1, segment2):
    
    param_1 = __cartesienne(segment1)
    param_2 = __cartesienne(segment2)

    a1 = param_1[0]
    b1 = param_1[1]
    c1 = param_1[2]
    
    a2 = param_2[0]
    b2 = param_2[1]
    c2 = param_2[2]

    x11 = segment1[0]
    y11 = segment1[1]
    x12 = segment1[2]
    y12 = segment1[3]
    
    x21 = segment2[0]
    y21 = segment2[1]
    x22 = segment2[2]
    y22 = segment2[3]
    
    
    val11 = __eval(param_1,x21,y21)
    val12 = __eval(param_1,x22,y22)
    
    val21 = __eval(param_2,x11,y11)
    val22 = __eval(param_2,x12,y12)
    
    val1 = val11*val12
    val2 = val21*val22
    
    return (val1 <= 0) & (val2 <= 0)
    
 
# ----------------------------------------
# Intersection between 2 tracks
# withTime: time constraint (in secs)
# (-1 if no time constraint)
# ---------------------------------------- 
def intersection(track1, track2, withTime=-1):

    if not (track1.getSRID() == track2.getSRID()):
        print("Error: tracks must have same SRID to compute intersections")
        exit()
    
    I = Track.Track()
    TMP_I = []
    TMP_J = []
    TMP_TPS2 = []
    
    for i in range(len(track1)-1):
    
        x11 = track1[i].position.getX()
        y11 = track1[i].position.getY()
        x12 = track1[i+1].position.getX()
        y12 = track1[i+1].position.getY()
        seg1 = [x11,y11,x12,y12]
    
        for j in range(len(track2)-1):
            
            x21 = track2[j].position.getX()
            y21 = track2[j].position.getY()
            x22 = track2[j+1].position.getX()
            y22 = track2[j+1].position.getY()
            seg2 = [x21,y21,x22,y22]
            
            if (__intersects(seg1, seg2)):
                P1 = __cartesienne(seg1)
                P2 = __cartesienne(seg2)
                A = np.zeros((2,2))
                B = np.zeros((2,1))
                A[0,0] = P1[0]; A[0,1] = P1[1]; B[0,0] = -P1[2]
                A[1,0] = P2[0]; A[1,1] = P2[1]; B[1,0] = -P2[2]
                
                X = np.linalg.solve(A,B)
                
                x = X[0,0]
                y = X[1,0]
                p = Utils.makeCoords(x, y, 0, track1.getSRID())
                
                # Linear interpolation on track 1
                w1 = p.distance2DTo(track1[i].position)
                w2 = p.distance2DTo(track1[i+1].position)
                p.setZ((w1*track1[i+1].position.getZ() + w2*track1[i].position.getZ())/(w1+w2))
                t1 = track1[i].timestamp.toAbsTime()
                t2 = track1[i].timestamp.toAbsTime()
                ta = (w1*t2 + w2*t1)/(w1+w2)
                
                # Linear interpolation on track 2
                w1 = p.distance2DTo(track2[j].position)
                w2 = p.distance2DTo(track2[j+1].position)
                t1 = track2[i].timestamp.toAbsTime()
                t2 = track2[i].timestamp.toAbsTime()
                tb = (w1*t2 + w2*t1)/(w1+w2)
                
                # Add intersection
                if ((withTime==-1) or (abs(tb-ta) < withTime)):
                    I.addObs(Obs(p, GPSTime.readUnixTime(ta)))
                    TMP_TPS2.append(GPSTime.readUnixTime(tb))
                    TMP_I.append(i)
                    TMP_J.append(j)
                
    if I.size() > 0:
        I.createAnalyticalFeature("timestamp2", TMP_TPS2);
        I.createAnalyticalFeature("id1", TMP_I)
        I.createAnalyticalFeature("id2", TMP_J)
    
    return I
 
# ----------------------------------------
# Intersection between 2 tracks (boolean)
# ---------------------------------------- 
def intersects(track1, track2):

    for i in range(len(track1)-1):
    
        x11 = track1[i].position.getX()
        y11 = track1[i].position.getY()
        x12 = track1[i+1].position.getX()
        y12 = track1[i+1].position.getY()
        seg1 = [x11,y11,x12,y12]
    
        for j in range(len(track2)-1):
            
            x21 = track2[j].position.getX()
            y21 = track2[j].position.getY()
            x22 = track2[j+1].position.getX()
            y22 = track2[j+1].position.getY()
            seg2 = [x21,y21,x22,y22]
            
            if __intersects(seg1, seg2):
                return True
                
    return False
   
def __dist_point_droite(param, x, y):
    
    a = param[0]
    b = param[1]
    c = param[2]

    distance = math.fabs(a*x+b*y+c)
    distance /= math.sqrt(a*a+b*b)
    
    return distance        
        
def __transform(theta, tx, ty, X, Y):

    XR = [0] * len(X)
    YR = [0] * len(Y)
    
    ct = math.cos(theta)
    st = math.sin(theta)

    for j in range(len(X)):
        XR[j] = ct*(X[j]-tx)+st*(Y[j]-ty)
        YR[j] = -st*(X[j]-tx)+ct*(Y[j]-ty)
        
    return XR, YR
        
def __transform_inverse(theta, tx, ty, X, Y):
        
    XR = [0] * len(X)
    YR = [0] * len(Y)
    
    ct = math.cos(theta)
    st = math.sin(theta)
    
    for j in range(len(X)):
        XR[j] = ct*X[j]-st*Y[j]+tx
        YR[j] = st*X[j]+ct*Y[j]+ty
        
    return XR, YR
                

def __convexHull(T):
    '''
    Finds the convex hull of a set of coordinates, returned as 
    a list of x an y coordinates : [x1, y1, x2, y2,...]
    Computation is performed with Jarvis march algorithm
    with O(n^2) time complexity. It may be needed to resample
    track if computation is too long.'''
        
    X = [p[0] for p in T]
    H = [X.index(min(X))]

    while((len(H) < 3) or (H[-1] != H[0])):
        H.append(0)
        for i in range(len(T)):
            if not (__right(T[H[-2]], T[H[-1]], T[i])):
                H[-1] = i
   
    return (H)


def convexHull(track):
    '''
    Finds the convex hull of a track, returned as 
    a list of x an y coordinates : [x1, y1, x2, y2,...]
    Computation is performed with Jarvis march algorithm
    with O(n^2) time complexity. It may be needed to resample
    track if computation is too long.'''
    
    T = []
    for i in range(len(track)):
        T.append([track[i].position.getX(), track[i].position.getY()])
        
    X = [p[0] for p in T]
    H = [X.index(min(X))]

    while((len(H) < 3) or (H[-1] != H[0])):
        H.append(0)
        for i in range(len(T)):
            if not (__right(T[H[-2]], T[H[-1]], T[i])):
                H[-1] = i
    T2 = []
    for i in range(len(H)):
        T2.append(T[H[i]][0])
        T2.append(T[H[i]][1])
    return T2


def diameter(track):
    '''
    Finds longest distance between points on track 
    The two selected points are returned in a vector
    along with the minimal distance : [min_dist, p1, p2].
    Exhaustive search in O(n^2) time complexity'''
    
    dmax = 0
    idmax = [0,0]
    
    for i in range(len(track)):
        for j in range(len(track)):
            d = track.getObs(i).distance2DTo(track.getObs(j))
            if d > dmax:
                dmax = d
                idmax = [i,j]
    return [dmax, idmax[0], idmax[1]]
    
    
def __circle(p1, p2=None, p3=None):
    ''' Finds circle through 1, 2 or 3 points
    Returns [C, R]'''
    if not isinstance(p1, ENUCoords):
        print("Error: ENU coordinates are required for min circle computation")
        exit()
    if p2 is None:
        return [p1, 0.0]
    if p3 is None:
        centre = p1+p2
        centre.scale(0.5)
        return [centre, p1.distance2DTo(p2)/2]
        
    if (p1.distance2DTo(p2) == 0):
        p2.setX(p2.getX()+random.random()*1e-10)
        p2.setY(p2.getY()+random.random()*1e-10)
            
    if (p1.distance2DTo(p3) == 0):
        p3.setX(p3.getX()+random.random()*1e-10)
        p3.setY(p3.getY()+random.random()*1e-10)
        
    if (p2.distance2DTo(p3) == 0):
        p3.setX(p3.getX()+random.random()*1e-10)
        p3.setY(p3.getY()+random.random()*1e-10)
    
    C12 = __circle(p1, p2)
    C23 = __circle(p2, p3)
    C13 = __circle(p1, p3)
    CANDIDATS = []
    
    if (C12[0].distance2DTo(p3) < C12[1]):
        CANDIDATS.append(C12)
    if (C23[0].distance2DTo(p1) < C23[1]):
        CANDIDATS.append(C23)
    if (C13[0].distance2DTo(p2) < C13[1]):
        CANDIDATS.append(C13)

    if len(CANDIDATS) > 0:
        min = CANDIDATS[0][1]
        argmin = 0
        for i in range(len(CANDIDATS)):
            if CANDIDATS[i][1] < min:
                min = CANDIDATS[i][1]
                argmin = i
        return CANDIDATS[argmin]
        

    x = np.complex(p1.getX(), p1.getY())
    y = np.complex(p2.getX(), p2.getY())
    z = np.complex(p3.getX(), p3.getY())

    w = z-x; w /= y-x; c = (x-y)*(w-abs(w)**2)/2j/np.imag(w)-x
    centre = p1.copy(); 
    centre.setX(-np.real(c)); 
    centre.setY(-np.imag(c));    
    return [centre, np.abs(c+x)]
    
def __welzl(P, R):
    '''Finds minimal bounding circle with Welzl's algorithm'''
    
    P = P.copy()
    R = R.copy()
    
    if ((len(P) == 0) or (len(R) == 3)):
        if len(R) == 0:
            return [ENUCoords(0,0,0), 0]
        if len(R) == 1:
            return __circle(R[0])
        if len(R) == 2:
            return __circle(R[0], R[1])
        return __circle(R[0], R[1], R[2])
    id = random.randint(0,len(P)-1)
    
    p = P[id]
    P2 = []
    for i in range(len(P)):
        if i == id:
            continue
        P2.append(P[i])
    P = P2
    D = __welzl(P, R)
    if (p.distance2DTo(D[0]) < D[1]):
        return D
    else:
        R.append(p)
        return __welzl(P, R)
    
    
    
def plotPolygon(P, color=[1,0,0,1]):
    '''Function to plot a polygon  from a vector:
    R = [x1,y1,x2,y2,x3,y3,...x1,y1]
    Needs to call plt.show() after this function'''    
    XR = P[::2]
    YR = P[1::2]
    plt.plot(XR, YR, color=color)
    

def minCircle(track):
    '''
    Finds minimal bounding circle with Welzl's recursive 
    algorithm in O(n) complexity. Output is given as a list 
    [p, R], where p is a Coords object defining circle center
    and R is its radius. Due to recursion limits, only tracks 
    with fewer than 800 points can be processed'''    
    if not track.getSRID() == "ENU":
        print("Error: ENU coordinates are required for min circle computation")
        exit()
    if track.size() > 0.5*sys.getrecursionlimit():
        message  = "Error: too many points in track to compute minimal enclosing circle. "
        message += "Downsample track, or use \"sys.setrecursionlimit("
        message += str(int((2*track.size())/1000)*1000 + 1000)+") or higher\""
        print(message)
        exit()
    
    centre = track.getFirstObs().position.copy()
    
    P = [obs.position for obs in track]
    R = []
        
    return __welzl(P,R)
    
def minCircleMatrix(track):
    '''Computes matrix of all min circles in a track.
        M[i,j] gives the radius of the min circle enclosing 
        points in track from obs i to obs j (included)'''
    
    M = np.zeros((track.size(), track.size()))
    for i in range(track.size()):
        print(i, "/", track.size())
        for j in range(i, track.size()-1):
            M[i,j] = minCircle(track.extract(i,j))[1]
    M = M + np.transpose(M)
    return M
    
# ------------------------------------------------------------
# Output :     R = [[x1,y1],[x2,y2],[x3,y3],[x4,y4], area, l, L]    
# ------------------------------------------------------------
def __mbr(COORDS):
        
    HULL = __convexHull(COORDS)
    XH = [COORDS[p][0] for p in HULL]
    YH = [COORDS[p][1] for p in HULL]

        
    BEST_RECTANGLE = []
    RECTANGLE_AREA = 10**301
    BEST_l = 0
    BEST_L = 0
    
    for i in range(len(HULL)-1):
    
        param = __cartesienne([XH[i], YH[i], XH[i+1], YH[i+1]])    
        theta = math.atan((YH[i+1]-YH[i])/(XH[i+1]-XH[i]))
    
        # 3 parameters transformation
        XHR, YHR = __transform(theta, XH[i], YH[i], XH, YH)
            
        mx = min(XHR)
        my = min(YHR)
        if (max(YHR) > abs(min(YHR))):
            my = max(YHR)
        Mx = max(XHR)

        
        XRR = [mx, Mx, Mx, mx, mx]
        YRR = [0, 0, my, my, 0]
    
        # 3 parameters inverse transformation
        XR, YR = __transform_inverse(theta,  XH[i], YH[i], XRR, YRR)
            
        new_area = (Mx-mx)*abs(my)
        if (new_area < RECTANGLE_AREA):
            BEST_RECTANGLE = [[XR[0], YR[0]], [XR[1], YR[1]], [XR[2], YR[2]], [XR[3], YR[3]], [XR[0], YR[0]]]
            RECTANGLE_AREA = new_area
            BEST_l = (Mx-mx)
            BEST_L = abs(my)
            
    if BEST_L < BEST_l:
        G = BEST_l; BEST_l = BEST_L; BEST_L = G
        
    return [BEST_RECTANGLE, RECTANGLE_AREA, BEST_l, BEST_L]
    

def minimumBoundingRectangle(track):    
    T = []
    for i in range(len(track)):
        T.append([track[i].position.getX(), track[i].position.getY()])
    return __mbr(T)








