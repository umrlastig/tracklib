import os
import sys
import math
import random
import numpy as np
import matplotlib.pyplot as plt

from tracklib.core.Operator import Operator
from tracklib.io.FileReader import FileReader
from tracklib.io.FileWriter import FileWriter
from tracklib.core.GPSTime import GPSTime
from tracklib.core.Track import Track
from tracklib.core.Coords import ECEFCoords
from tracklib.core.Coords import GeoCoords
from tracklib.core.Coords import ENUCoords

from tracklib.algo.Selection import TrackConstraint
import tracklib.algo.Stochastics as Stochastics
import tracklib.algo.Synthetics as Synthetics
import tracklib.algo.Geometrics as Geometrics
import tracklib.algo.Comparison as Comparison
import tracklib.algo.Cinematics as Cinematics
import tracklib.algo.Dynamics as Dynamics
import tracklib.algo.Interpolation as Interpolation
import tracklib.algo.Simplification as Simplification
import tracklib.algo.Segmentation as Segmentation
import tracklib.algo.Mapping as Mapping
import tracklib.algo.Filtering as Filtering
from tracklib.algo.Dynamics import Kalman

from tracklib.io.KmlWriter import KmlWriter
from tracklib.core.Coords import ENUCoords

from tracklib.io.GpxWriter import GpxWriter
from tracklib.io.GpxReader import GpxReader
from tracklib.core.TrackCollection import TrackCollection
from tracklib.core.Kernel import DiracKernel
from tracklib.core.Kernel import GaussianKernel
from tracklib.core.Kernel import ExponentialKernel
from tracklib.core.Kernel import ExperimentalKernel

from tracklib.core.Obs import Obs
import tracklib.core.Plot as Plot
from tracklib.core.Network import Node
from tracklib.core.Network import Edge
from tracklib.core.Network import Network
from tracklib.io.NetworkReader import NetworkReader

# -----------------------------------------------------------------------
# Example 0: a simple example with simulated data
# -----------------------------------------------------------------------
# Simple standard (linear) Kalman Filter with 4 states [x, y, vx, vy] 
# and two measurements [x, y]
# -----------------------------------------------------------------------
def example0():

    Stochastics.seed(123)
    track1 = Synthetics.generate(0.2, dt=10)
    track2 = track1.noise(1)
    
    F = np.array([
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [0, 0, 1, 0],
        [0, 0, 0, 1]])
    H = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0]])
    Q = np.array([
        [1e-8, 0, 0, 0],
        [0, 1e-8, 0, 0],
        [0, 0, 2e-4, 0],
        [0, 0, 0, 2e-4]])
    R = np.array([
        [1, 0],
        [0, 1]])
    X0 = np.array([
        [track2[0].position.getX()],
        [track2[0].position.getY()],
    	[0],
    	[0]])
    P0 = np.array([
        [3, 0, 0, 0],
        [0, 3, 0, 0],
        [0, 0, 1e1, 0],
        [0, 0, 0, 1e1]])
    
    UKF = Kalman()
    UKF.setTransition(F, Q)
    UKF.setObservation(H, R)
    UKF.setInitState(X0, P0)
    UKF.summary()
    
    UKF.estimate(track2, ["x", "y"])
    	
    
    track1.plot('k--')
    plt.plot(track2['kf_0'], track2['kf_1'], 'b-')
    track2.plot('r+')
    
    plt.show()



# -----------------------------------------------------------------------
# Example 1: a simple example with simulated data
# -----------------------------------------------------------------------
# Context: a vehicle is tracked simultaneously by two beacons (balise1 
# and balise2), each of them measuring time travel of a radio-electric
# signal and converting it to a distance measurement. These observations
# are available at every time step and are noised. On the other hand, 
# the vehicule records its own speed with high precision but with random
# drift over time. In this example, we design a kalman filter to merge 
# beacon absolute and low-accuracy data, with high-accuracy relative 
# speed measurements. 
# -----------------------------------------------------------------------
# Variations:
#    - Try with only one beacon (in this case, speed measurements are 
#      mandatory to have a well-posed problem).
#    - Let's imagine that the beacons have a measurement bias constant
#      over time. Let's note b1 and b2, the unknown values of these 
#      biases. The goal is now to estimate b1 and b2 along with the 
#      vehicle position. Measurement equations become 
#      yi(t) = distance(vehicle, beacon i) + bi(t)
#      and bi transition rule is : bi(t+1) = bi(t) + w   (w ~ 1e-16)
#    - Based on the previous study case with biased measurements, an 
#      interesting experiment is to change the bias of one of the two 
#      beacons during the process (for example at time step k=50). We 
#      then observe how all bias parameter estimations are impacted 
#      simultaneously, along with the position parameters. This "jump"
#      may be detected before being included in the Kalman loop, by 
#      carefully inspecting the innovation values ("kf_balise1_inov" and 
#      "kf_balise2_inov") to detect incorrect measurement. 
# -----------------------------------------------------------------------
def example1(withBiases=False, withCycleSlip=False):

    Stochastics.seed(123)
    
    track_gt = Synthetics.generate(0.15)
    
    B1 = [-20,30]
    B2 = [30,10]
	
    b1 = 0 + withBiases*25
    b2 = 0 + withBiases*32
    sp = 0 + withCycleSlip*10
    
    track_odo = track_gt.copy()
    track_odo = Stochastics.NoiseProcess(2, GaussianKernel(10)).noise(track_odo)
    track_odo.op("dx=D(x)")
    track_odo.op("dy=D(y)")
    
    track = track_gt.noise(0.5)
    track.biop(track_odo, "vx=dx°2")
    track.biop(track_odo, "vy=dy°")
	
    externals = {"x1":B1[0], "y1":B1[1], "x2":B2[0], "y2":B2[1], "b1":b1, "b2":b2, "sp":sp}
    track.op("balise1 = SQRT((x-x1)^2+(y-y1)^2)-b1-sp*(idx>50)", externals)
    track.op("balise2 = SQRT((x-x2)^2+(y-y2)^2)-b2", externals)
	
    track = track > 1
    
    track_gt.plot('k--')
    plt.plot(B1[0], B1[1], 'k^')
    plt.plot(B2[0], B2[1], 'k^')
    track.plot('b+')
    
    def F(x, k, track):
    	return np.array([
    		[x[0,0] + track["vx", k]], 
    		[x[1,0] + track["vy", k]],
    		[x[2,0]],
    		[x[3,0]]])
    
    def H(x):
    	return np.array([
    	[((x[0,0]-B1[0])**2+(x[1,0]-B1[1])**2)**0.5]-x[2,0],
    	[((x[0,0]-B2[0])**2+(x[1,0]-B2[1])**2)**0.5]-x[3,0]])
    
    Q = 1e-1*np.eye(4,4); Q[2,2] = 1e-10; Q[3,3] = 1e-10
    R = 0.5**2*np.eye(2,2);
    
    X0 = np.array([[-50], [40], [0], [0]])
    P0 = 1e1*np.eye(4,4); P0[2,2] = 1e2; P0[3,3] = 1e2
    
    UKF = Kalman()
    UKF.setTransition(F, Q)
    UKF.setObservation(H, R)
    UKF.setInitState(X0, P0)
    UKF.summary()
    
    UKF.estimate(track, ["balise1", "balise2"], mode = Dynamics.MODE_STATES_AS_2D_POSITIONS)
    
    track.plot('r-')

    # Innovation
    #fig, ax1 = plt.subplots(figsize=(5, 3))
    #ax1.plot(track["kf_balise1_inov"], 'r-')
    #ax1.plot(track["kf_balise2_inov"], 'g-')
    
    #ax1.plot(np.array(track["x"])-np.array(track_gt["x"])[1:], 'b-')
    #ax1.plot(np.array(track["y"])-np.array(track_gt["y"])[1:], 'b-')
    
    # Statistics
    #print("Std gps =", '{:3.2f}'.format(track.operate(Operator.RMSE,"kf_balise1_inov")), "m")
    #print("Std cam =", '{:3.2f}'.format(track.operate(Operator.RMSE,"kf_balise2_inov")), "m")
    
    fig, ax1 = plt.subplots(figsize=(5, 3))
    #ax1.plot(track["kf_2"], 'r.')
    #ax1.plot(track["kf_3"], 'g.')
    
    ax1.plot(track["kf_balise1_inov"], 'r-')
    ax1.plot(track["kf_balise2_inov"], 'g-')
    
    plt.show()


# -----------------------------------------------------------------------
# Example 2: GNSS/Camera hybridation
# -----------------------------------------------------------------------
# Context: a pedestrian is walking with a camera (taking images every 
# 2 seconds) and a GPS receiver (1 point per second). We want to merge 
# GPS absolute and low-accuracy data, with high-accuracy relative 
# photogrammetric measurements. 
# -----------------------------------------------------------------------
def example2():

    path_cam = "data/hybridation_gnss_camera.dat"
    path_gps = "data/hybridation_gnss_camera.pos"
    
    GPSTime.setReadFormat("2D/2M/4Y-2h:2m:2s.3z")
    
    track_cam = FileReader.readFromFile(path_cam, 1, 2, 3, 0, " ", srid="ENUCoords")
    track_gps = FileReader.readFromFile(path_gps, 1, 2, 3, 0, " ", srid="ENUCoords")
    track_cam.incrementTime(0, 18-3600)
    
    
    
    ini_time = GPSTime("06/06/2021-16:02:00.000")
    fin_time = GPSTime("06/06/2021-16:12:12.000")
    track_cam = track_cam.extractSpanTime(ini_time, fin_time)
    track_gps = track_gps.extractSpanTime(ini_time, fin_time)
    track_gps = track_gps // track_cam
    
    Mapping.mapOn(track_cam, track_gps, TP1=list(range(0, 50, 10)))
    
    def vx(track, i):
    	if i == len(track)-1:
    		return track[i].position.getX()-track[i-1].position.getX()
    	return track[i+1].position.getX()-track[i].position.getX()
    def vy(track, i):
    	if i == len(track)-1:
    		return track[i].position.getY()-track[i-1].position.getY()
    	return track[i+1].position.getY()-track[i].position.getY()
    
    
    track_cam.addAnalyticalFeature(vx)
    track_cam.addAnalyticalFeature(vy)
    track_gps.createAnalyticalFeature("vx", track_cam["vx"])
    track_gps.createAnalyticalFeature("vy", track_cam["vy"])
    
    def F(x, k, track):
    	vx = track.getObsAnalyticalFeature("vx", k)
    	vy = track.getObsAnalyticalFeature("vy", k)
    	return Dynamics.DYN_MAT_2D_CST_POS() @ x + np.array([[vx], [vy]])
    	
    H = np.eye(2,2)
    
    Q = 1e-1*np.eye(2,2);
    R = 1.8**2*np.eye(2,2);
    
    X0 = np.zeros((2,1)); 
    P0 = R
    
    UKF = Kalman(spreading=1)
    UKF.setTransition(F, Q)
    UKF.setObservation(H, R)
    UKF.setInitState(X0, 1e2*P0)
    
    UKF.summary()
    
    track_filtered = track_gps.copy()
    UKF.estimate(track_filtered, ["x","y"], mode = Dynamics.MODE_STATES_AS_2D_POSITIONS)
    
    track_filtered.summary()
    
    
    
    # Track plot
    track_gps.plot('k+')
    track_cam.plot('r-')
    track_filtered.plot('g-')
    #track_filtered.plotEllipses('g-', factor=10)
    
    
    
    # Statistics
    print("Std gps =", '{:3.2f}'.format(track_filtered.operate(Operator.RMSE,"kf_x_inov")), "m")
    
    plt.show()


# -----------------------------------------------------------------------
# Example 3: GNSS kalman integration
# -----------------------------------------------------------------------
# Context: a vehicle is driving at approximately constant speed in 
# a straight road. The speed and the road heading are unknown. The 
# vehicle is equipped with a GPS receiver. Measurements to 5 satellites 
# are available at every time step (m0 to m4). These measurements are 
# already corrected from tropospheric and ionospheric delays, satellite 
# clock error, relativistic effects and Earth rotation. As a consequence 
# they can be considered as distances to the receiver, provided that they
# are corrected by a biais, accounting for the receiver internal clock 
# error. Hence, each measurement mi to the satelliet Si(xi,yi,zi) given 
# at time step t by : mi(t) = distance(R(t), Si(t)) + b(t) where bi is 
# the time clock error converted in distance (by multiplication to speed 
# of light in vacuum) and R(t) is the receiver position at time step t. 
# Note that the term b(t) is the same for all satellites Si. It is
# assumed that b varies according to a 1st order Taylor expansion :
# b(t+1) = b(t) + d(t) + w(t) where d(t) is the clock time drift at time 
# step t, and w(t) is a low-variance noise (~ 1 or 2 meters) denoting
# clock drift derivative. All terms in this equations are expressed in 
# distance units.
# For a given speed v and heading h (both parameters are to be estimated 
# during the process), the transition rule states that :
#    E(t+1) = E(t) + v.sin(h)
#    N(t+1) = N(t) + v.cos(h)
# where E and N are local planimetric coordinates of the vehicle. However 
# satellite coordinates are expressed in Earth-Centered Earth-Fixed 
# (ECEF). All the computation process is expressed in ECEF. Then, a local
# planimetric projection to ENU local coordinates are necessary at each 
# transition step of the kalman filter. The transition of speed and 
# heading (which are assumed to be approximately constant on the road) is 
#    v(t+1) = v(t) + nv(t), with nv a noise of variance 0.1 m/s
#    h(t+1) = h(t) + nh(t), with nh a noise of variance 0.001 rad/s
# Eventually, clock drift is also assumed to be constant :
#    d(t+1) = d(t) + nd(t), with nd a noise of variance 1 m/s
# To sum up, the filter contains:
#    7 parameters: X, Y, Z, heading h, speed v, clock error b, clock 
#                  and drift d.
#    5 observations: one for each visible satellite (note that these 
#                    satellites are not constant over time)
# Initial values of parameters to be estimated are given by:
#    X, Y, Z: a random point in Vincennes down town (a few 100 meters 
#             from the actual vehicle departure)
#    Speed       :  0 m/s  (+/- 10)
#    Heading     :  0°     (+/- pi)
#    Clock error :  0      (+/- 1e6 m) 
#    Clock drift :  0      (+/- 1e3 m/s)
# -----------------------------------------------------------------------
def example3():

    start = GeoCoords(2.4320023,  48.84298, 100).toECEFCoords()
    print(start)
    
    path = "tracklib/data/psr.dat"
    
    track = Track()
    
    for i in range(47):
    	track.addObs(Obs(ECEFCoords(0,0,0)))
    track.createAnalyticalFeature("m0",[0]*47); track.createAnalyticalFeature("sx0",[0]*47); track.createAnalyticalFeature("sy0",[0]*47); track.createAnalyticalFeature("sz0",[0]*47); 
    track.createAnalyticalFeature("m1",[0]*47); track.createAnalyticalFeature("sx1",[0]*47); track.createAnalyticalFeature("sy1",[0]*47); track.createAnalyticalFeature("sz1",[0]*47); 
    track.createAnalyticalFeature("m2",[0]*47); track.createAnalyticalFeature("sx2",[0]*47); track.createAnalyticalFeature("sy2",[0]*47); track.createAnalyticalFeature("sz2",[0]*47); 
    track.createAnalyticalFeature("m3",[0]*47); track.createAnalyticalFeature("sx3",[0]*47); track.createAnalyticalFeature("sy3",[0]*47); track.createAnalyticalFeature("sz3",[0]*47); 
    track.createAnalyticalFeature("m4",[0]*47); track.createAnalyticalFeature("sx4",[0]*47); track.createAnalyticalFeature("sy4",[0]*47); track.createAnalyticalFeature("sz4",[0]*47); 
    
    with open(path) as fp:
    	line = True
    	for i in range(47):
    		for j in range(5):
    			line = fp.readline()
    			vals = line[:-2].split(",")
    			track.setObsAnalyticalFeature("sx"+str(j), i, float(vals[1]))
    			track.setObsAnalyticalFeature("sy"+str(j), i, float(vals[2]))
    			track.setObsAnalyticalFeature("sz"+str(j), i, float(vals[3]))
    			track.setObsAnalyticalFeature("m"+str(j) , i, float(vals[4]))
    		line = fp.readline()
    
    
    def F(x):
    	plan = ECEFCoords(x[0,0], x[1,0], x[2,0]).toENUCoords(start)
    	plan.E += x[5,0]*math.sin(x[4,0])
    	plan.N += x[5,0]*math.cos(x[4,0])
    	xyz = plan.toECEFCoords(start)
    	return np.array([
    	[xyz.X],
    	[xyz.Y],
    	[xyz.Z],
    	[x[3,0]+x[6,0]],
    	[x[4,0]],
    	[x[5,0]],
    	[x[6,0]]])
    	
    
    def H(x, k, track):
    	return np.array([
    	[((x[0,0]-track["sx0",k])**2 + (x[1,0]-track["sy0",k])**2 + (x[2,0]-track["sz0",k])**2)**0.5 + x[3,0]],
    	[((x[0,0]-track["sx1",k])**2 + (x[1,0]-track["sy1",k])**2 + (x[2,0]-track["sz1",k])**2)**0.5 + x[3,0]],
    	[((x[0,0]-track["sx2",k])**2 + (x[1,0]-track["sy2",k])**2 + (x[2,0]-track["sz2",k])**2)**0.5 + x[3,0]],
    	[((x[0,0]-track["sx3",k])**2 + (x[1,0]-track["sy3",k])**2 + (x[2,0]-track["sz3",k])**2)**0.5 + x[3,0]],
    	[((x[0,0]-track["sx4",k])**2 + (x[1,0]-track["sy4",k])**2 + (x[2,0]-track["sz4",k])**2)**0.5 + x[3,0]]])
    
    Q = 1e0*np.eye(7,7); Q[3,3] = 0; Q[4,4] = 1e-10; Q[5,5] = 1e-1; Q[6,6] = 1e-1
    R = 1e1*np.eye(5,5);
    
    X0 = np.array([[start.getX()], [start.getY()], [start.getZ()], [0], [0], [0], [0]])
    P0 = 1e5*np.eye(7,7); P0[3,3] = 1e6; P0[4,4] = 1e1; P0[5,5] = 1e1; P0[6,6] = 1e3
    
    UKF = Kalman(spreading=1)
    UKF.setTransition(F, Q)
    UKF.setObservation(H, R)
    UKF.setInitState(X0, P0)
    UKF.summary()
    
    UKF.estimate(track, ["m0","m1","m2","m3","m4"], mode = Dynamics.MODE_STATES_AS_3D_POSITIONS)
    
    track.toGeoCoords()
    
    
    track.plot('r-')
    
    plt.show()
    
    KmlWriter.writeToKml(track, path="couplage.kml", type="LINE")


# -----------------------------------------------------------------------
# Example 4: GNSS computation with 3 satellites
# -----------------------------------------------------------------------
# Context: receiver clock error drift is estimated in order to keep 
# track of position even without required minimal number of satellites
# -----------------------------------------------------------------------
def example4():

    start = GeoCoords(2.4320023,  48.84298, 100).toECEFCoords()
    
    
    path = "tracklib/data/psr_all.dat"
    
    track = Track()
    
    Nepochs = 534
    for i in range(Nepochs):
    	track.addObs(Obs(ECEFCoords(0,0,0)))
    track.createAnalyticalFeature("m0",[0]*Nepochs); track.createAnalyticalFeature("sx0",[0]*Nepochs); track.createAnalyticalFeature("sy0",[0]*Nepochs); track.createAnalyticalFeature("sz0",[0]*Nepochs); 
    track.createAnalyticalFeature("m1",[0]*Nepochs); track.createAnalyticalFeature("sx1",[0]*Nepochs); track.createAnalyticalFeature("sy1",[0]*Nepochs); track.createAnalyticalFeature("sz1",[0]*Nepochs); 
    track.createAnalyticalFeature("m2",[0]*Nepochs); track.createAnalyticalFeature("sx2",[0]*Nepochs); track.createAnalyticalFeature("sy2",[0]*Nepochs); track.createAnalyticalFeature("sz2",[0]*Nepochs); 
    track.createAnalyticalFeature("m3",[0]*Nepochs); track.createAnalyticalFeature("sx3",[0]*Nepochs); track.createAnalyticalFeature("sy3",[0]*Nepochs); track.createAnalyticalFeature("sz3",[0]*Nepochs); 
    track.createAnalyticalFeature("m4",[0]*Nepochs); track.createAnalyticalFeature("sx4",[0]*Nepochs); track.createAnalyticalFeature("sy4",[0]*Nepochs); track.createAnalyticalFeature("sz4",[0]*Nepochs); 
    track.createAnalyticalFeature("m5",[0]*Nepochs); track.createAnalyticalFeature("sx5",[0]*Nepochs); track.createAnalyticalFeature("sy5",[0]*Nepochs); track.createAnalyticalFeature("sz5",[0]*Nepochs); 
    
    
    with open(path) as fp:
    	line = True
    	for i in range(Nepochs):
    		for j in range(6):
    			line = fp.readline()
    			vals = line[:-1].split(",")
    			track.setObsAnalyticalFeature("sx"+str(j), i, float(vals[1]))
    			track.setObsAnalyticalFeature("sy"+str(j), i, float(vals[2]))
    			track.setObsAnalyticalFeature("sz"+str(j), i, float(vals[3]))
    			track.setObsAnalyticalFeature("m"+str(j) , i, float(vals[4]))
    		line = fp.readline()
    
    track = track%[False, True]
    
    
    
    def F(x):
    	return np.array([
    	[x[0,0]],
    	[x[1,0]],
    	[x[2,0]],
    	[x[3,0]+x[4,0]],
    	[x[4,0]]])
    
    def H(x, k, track):		
    	return np.array([
    	[((x[0,0]-track["sx0",k])**2 + (x[1,0]-track["sy0",k])**2 + (x[2,0]-track["sz0",k])**2)**0.5 + x[3,0]],
    	[((x[0,0]-track["sx1",k])**2 + (x[1,0]-track["sy1",k])**2 + (x[2,0]-track["sz1",k])**2)**0.5 + x[3,0]],
    	[((x[0,0]-track["sx2",k])**2 + (x[1,0]-track["sy2",k])**2 + (x[2,0]-track["sz2",k])**2)**0.5 + x[3,0]],
    	[((x[0,0]-track["sx3",k])**2 + (x[1,0]-track["sy3",k])**2 + (x[2,0]-track["sz3",k])**2)**0.5 + x[3,0]],
    	[((x[0,0]-track["sx4",k])**2 + (x[1,0]-track["sy4",k])**2 + (x[2,0]-track["sz4",k])**2)**0.5 + x[3,0]],
    	[((x[0,0]-track["sx5",k])**2 + (x[1,0]-track["sy5",k])**2 + (x[2,0]-track["sz5",k])**2)**0.5 + x[3,0]]])
    
    
    Q = 1e0*np.eye(5,5); Q[3,3] = 0; Q[4,4] = 1e0
    def R(k):
    	P = 1e1*np.eye(6,6)
    	if (k>=70) and (k<267):
    		for i in range(3,6):
    			P[i,i] = 1e16
    	return P 
    	
    for k in range(70, 267):
    	for i in range(3,6):
    		track.setObsAnalyticalFeature("m"+str(i),k, 20000000)
    
    X0 = np.array([[start.X], [start.Y], [start.Z], [0], [0]])
    P0 = 1e5*np.eye(5,5); P0[3,3] = 1e8; P0[4,4] = 1e6
    
    UKF = Kalman(spreading=1)
    UKF.setTransition(F, Q)
    UKF.setObservation(H, R)
    UKF.setInitState(X0, P0)
    UKF.summary()
    
    UKF.estimate(track, ["m0","m1","m2","m3","m4","m5"], mode = Dynamics.MODE_STATES_AS_3D_POSITIONS)
    track.toGeoCoords()
    
    
    KmlWriter.writeToKml(track, path="couplage.kml", type="POINT", c1=[0,1,0,1])
    
    
    track.plot('r+')
    plt.show()

