import math
import matplotlib.pyplot as plt

from tracklib.core.GPSTime import GPSTime
from tracklib.core.Coords import ENUCoords
from tracklib.core.Track import Track
from tracklib.core.Obs import Obs

import tracklib.algo.Stochastics as Stochastics
import tracklib.algo.Synthetics as Synthetics
import tracklib.algo.Geometrics as Geometrics
import tracklib.algo.Interpolation as Interpolation


# -----------------------------------------------------------------------
# Example 0: simple circle regression
# -----------------------------------------------------------------------
def x_t(t):
    return math.cos(2*math.pi*t)
def y_t(t):
    return math.sin(2*math.pi*t)

def example0():

    track = Synthetics.generate(x_t,y_t, dt=5)
    Interpolation.resample(track, 0.1, 1, 1)
    track = Stochastics.noise(track, 0.02)


    circle = Geometrics.fitCircle(track)
    circle.plot()

    plt.plot(track.getX(), track.getY(), 'b+')
    plt.show()


def example1():
    trace1 = Track()
    time = GPSTime()
    
    p1 = Obs(ENUCoords(659007.266, 6860734.006, 53.500), time)
    trace1.addObs(p1)
    p2 = Obs(ENUCoords(658996.748, 6860730.745, 53.600), time)
    trace1.addObs(p2)
    p3 = Obs(ENUCoords(658996.748, 6860730.745, 53.600), time)
    trace1.addObs(p3)
    
    plt.plot(trace1.getX(), trace1.getY(), 'ro')


if __name__ == '__main__':
    #example0()
    example1()



