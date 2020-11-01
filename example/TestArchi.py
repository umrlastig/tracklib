
#import matplotlib.pyplot as plt
#
#from tracklib.core.GPSTime import GPSTime
#import tracklib.core.core_utils as utils
#from tracklib.core.Operator import Operator
#from tracklib.core.Kernel import GaussianKernel
#import tracklib.algo.Interpolation as interpolation
#from tracklib.io.FileReader import FileReader
#import tracklib.core.Track as core_Track

#GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
#
#time = GPSTime.readTimestamp("2018-05-30 14:31:25")
#point1 = Obs(ENUCoords(0, 0, 782), time)
#point2 = Obs(ENUCoords(10, 0, 782), time)
#
#print(point1.distanceTo(point2))
#
#s = Operator.SUM


#GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
#track = core_Track.Track.generate(TestOperateurMethods.x2, TestOperateurMethods.y2)
#		
#track.createAnalyticalFeature("a")
#track.operate(Operator.RANDOM, "a", TestOperateurMethods.prob, "randx")
#track.operate(Operator.RANDOM, "a", TestOperateurMethods.prob, "randy")
#
#track.operate(Operator.INTEGRATOR, "randx", "randx")
#track.operate(Operator.INTEGRATOR, "randy", "randy")
#
#track.operate(Operator.SCALAR_MULTIPLIER, "randx", 0.5, "noisex")
#track.operate(Operator.SCALAR_MULTIPLIER, "randx", 0.5, "noisey")
#
#track.operate(Operator.ADDER, "x", "noisex", "x_noised")
#track.operate(Operator.ADDER, "y", "noisey", "y_noised")
#
#kernel = GaussianKernel(31)
#
#track.operate(Operator.FILTER, "x_noised", kernel, "x_filtered")
#track.operate(Operator.FILTER, "y_noised", kernel, "y_filtered")
#
#plt.plot(track.getAnalyticalFeature("x"), track.getAnalyticalFeature("y"), 'k--')
#plt.plot(track.getAnalyticalFeature("x_noised"), track.getAnalyticalFeature("y_noised"), 'b-')
#plt.plot(track.getAnalyticalFeature("x_filtered"), track.getAnalyticalFeature("y_filtered"), 'r-')
#
#plt.show()
