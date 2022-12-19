import matplotlib.pyplot as plt

import tracklib.core.Utils as utils
import tracklib.algo.Interpolation as interp
from tracklib.core.ObsTime import GPSTime
from tracklib.core.Track import Track 
from tracklib.core.ObsCoords import GeoCoords
from tracklib.core.Obs import Obs
from tracklib.core.Operator import Operator
from tracklib.core.Kernel import GaussianKernel
from tracklib.io.TrackReader import TrackReader


import sys
import math
import time
import random
import numpy as np


# ---------------------------------------------------
# Lecture des donnees
# ---------------------------------------------------
GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
GPSTime.setPrintFormat("4Y-2M-2D 2h:2m:2s.3z")


chemin = "./data/trace0.gps"

GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")

track = TrackReader.readFromFile(chemin, 2, 3, -1, 1, separator=",")


track = track.extract(100,300)
track %= 20


#			- MODE_SPATIAL        (1)
#			- MODE_TEMPORAL       (2)
#		algorithm: 
#			- ALGO_LINEAR            (1)
#			- ALGO_THIN_SPLINES      (2)
#			- ALGO_B_SPLINES         (3)
#			- ALGO_GAUSSIAN_PROCESS  (4)

plt.plot(track.getX(), track.getY(), "ko", markersize=2.5)	

interp.SPLINE_PENALIZATION = 1e-2
track.resample(50, interp.ALGO_THIN_SPLINES, interp.MODE_SPATIAL)


plt.plot(track.getX(), track.getY(), "b-", linewidth=1)	

#print(track)

plt.show()


'''

path2 = "../data/rawGps1Data.pos"

start = GPSTime("2019-09-08 00:00:00")
track2 = FileReader.readFromFile(path2, 1, 3, 2, 4, " ", start, 18)

for i in range(1,50):

	track = track2.extractSpanTime(GPSTime("2019-09-12 13:07:00"), GPSTime("2019-09-12 13:11:00"))

	plt.clf()
	plt.plot(track.getX(), track.getY(), 'ko', markersize=1)

	interp.SPLINE_PENALIZATION = 1.0/(50-i)**3
	track.resample(0.00001, interp.MODE_SPLINE_SPATIAL)

	plt.plot(track.getX(), track.getY(), 'r-', linewidth=1)
	plt.title('lambda = '+'{:1.5f}'.format(interp.SPLINE_PENALIZATION))

	plt.savefig('images/im'+'{:02d}'.format(i)+'.png')

	#plt.show()
'''

'''

path1 = "../data/imu_opk_Vincennes1909121306.txt"
path2 = "../data/rtk_l93.txt"

GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")

start = GPSTime("2019-09-08 00:00:00")
end = GPSTime("2019-09-12 13:12:00")

RHO = []


for decalage in range(0,60):
	
	ref = FileReader.readFromFile(path1, 0, 1, 2, 3, " ", start)
	ref.addSeconds(decalage)
	ref = ref.extractSpanTime(ref.getFirstObs().timestamp, end)
	
	track = FileReader.readFromFile(path2, 0, 1, 2, 3, "     ", start, 18)
	track = track.extractSpanTime(ref.getFirstObs().timestamp, ref.getLastObs().timestamp)

	ref.synchronize(track)


	DX = []
	DY = []
	for i in range(ref.size()):
		DX.append(ref.getObs(i).position.getX()-track.getObs(i).position.getX())
		DY.append(ref.getObs(i).position.getY()-track.getObs(i).position.getY())
		

	rho = np.corrcoef(DX,DY)
	print(decalage, "sec => rho:", rho[0,1])
	RHO.append(rho[0,1])


id = np.argmin(RHO)

plt.subplot(1,2,1)
plt.plot(range(0,60), RHO, 'b-', linewidth=1)
plt.plot([id,id], [0,0.3], 'k--', linewidth=1)



plt.subplot(1,2,2)

ref = FileReader.readFromFile(path1, 0, 1, 2, 3, " ", start)
ref.addSeconds(id)
ref = ref.extractSpanTime(ref.getFirstObs().timestamp, end)
	
track = FileReader.readFromFile(path2, 0, 1, 2, 3, "     ", start, 18)
track = track.extractSpanTime(ref.getFirstObs().timestamp, ref.getLastObs().timestamp)

ref.synchronize(track)

plt.plot(ref.getX(), ref.getY(), 'g-', linewidth=1)
plt.plot(track.getX(), track.getY(), 'r-', linewidth=1)

plt.show()
'''

'''

GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
GPSTime.setPrintFormat("4Y-2M-2D 2h:2m:2s.3z")

path = "../data/trace0.gps"

GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")

track = FileReader.readFromFile(path,1,2,3)

track = track.extract(100,300)

track.resample(10, Track.MODE_INTERP_SPATIAL)

K = GaussianKernel(65)
A = 10

K.plot()

for i in range(1):
	noised = track.noise(A, K)
	plt.plot(noised.getX(), noised.getY(), "r-", linewidth=1.0)

plt.plot(track.getX(), track.getY(), "k--", linewidth=1.0)	
plt.show()

'''


'''
GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
GPSTime.setPrintFormat("4Y-2M-2D 2h:2m:2s.3z")

path = "../data/trace0.gps"

GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")

track = FileReader.readFromFile(path,1,2,3)

kernel = GaussianKernel(75)
kernel.plot()

track = track.extract(100,300)

sparse = track % 10

smooth = sparse.gaussian_process(1, kernel, 2000, 2, cp_var=True)

sparse.estimate_speed()
smooth.estimate_speed()

plt.subplot(211)
plt.plot(sparse.getX(), sparse.getY(), 'ko', markersize=2)
plt.plot(smooth.getX(), smooth.getY(), 'r-', linewidth=0.5)


plt.subplot(212)
plt.plot(sparse.getT(), sparse.getAnalyticalFeature("speed"), 'k+', markersize=5.0)
plt.plot(smooth.getT(), smooth.getAnalyticalFeature("speed"), 'g--', linewidth=1.0)

plt.show()
'''


'''

def compute_speed_smooth(tracks):
	track = tracks[0].copy()
	track.estimate_speed()
	track.operate(Operator.FILTER_FFT, "speed", GaussianKernel(10), "smooth_speed")
	return track.getAnalyticalFeature("smooth_speed")
	
speed = compute_speed_smooth([track])
plt.plot(track.getT(), speed, 'k--')

speeds = Track.randomizer([track], compute_speed_smooth, 15, GaussianKernel(500))

for i in range(10):	
	plt.plot(track.getT(), speeds[i], 'r-', linewidth=1)

plt.show()
'''

'''
track.resample(5, Track.MODE_INTERP_SPATIAL)
track.summary()
track.compute_abscurv()
track.estimate_speed()

kernel = GaussianKernel(25)
kernel.plot()

kernel.setFilterBoundary(True)


for i in range(0):
	track.operate(Operator.FILTER, "speed", kernel, "smoothed_speed")
	print("Filtering track number", i+1, "ok")

for i in range(1):
	track.operate(Operator.FILTER_FFT, "speed", kernel, "smoothed_speed")
	print("Filtering track number", i+1, "ok")

plt.plot(track.getAnalyticalFeature("abs_curv"), track.getAnalyticalFeature("speed"), 'k-', linewidth=0.25)
plt.plot(track.getAnalyticalFeature("abs_curv"), track.getAnalyticalFeature("smoothed_speed"), 'r-', linewidth=1.25)
plt.show()
'''





'''
t1 = track.copy()
t2 = track.copy()

t1.resample(300, Track.MODE_INTERP_SPATIAL)
t2.resample(10, Track.MODE_INTERP_TEMPORAL)

t3 = t1 // t2
t2 = t2 // t3
t1 = t3

t1.summary()
t2.summary()

print(t1.compare(t2))
	

plt.plot(t1.getX(), t1.getY(), 'go', markersize=1.0)
plt.plot(t2.getX(), t2.getY(), 'ro', markersize=1.0)

plt.show()
'''

'''	
simplified = utils.douglas_peucker2(track, 1)

plt.plot(track.getX(), track.getY(), 'k-')
plt.plot(simplified.getX(), simplified.getY(), 'r-')
plt.show()
'''

'''
def vx(x,y):
	return 1.0/100.0
def vy(x,y):
	return (x**2-x-2)/100.0


TRACKS = Track.generateDataSet(vx,vy,100,(-5,-10),(5,10))

for i in range(len(TRACKS)):
	track = TRACKS[i]
	plt.plot(track.getX(), track.getY(), 'k-', linewidth=0.5)


plt.show()
'''

