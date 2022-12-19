import math
import matplotlib.pyplot as plt

from tracklib.core.ObsTime import GPSTime
from tracklib.core.ObsCoords import ENUCoords
from tracklib.core.Track import Track
from tracklib.core.Obs import Obs

from tracklib.algo.Geometrics import Circle, minCircle

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


def example2():
    trace1 = Track()
    time = GPSTime()
    
    p1 = Obs(ENUCoords(659002.120, 6860722.478, 53.400), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658999.339, 6860723.499, 53.500), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.435, 6860724.179, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658996.338, 6860724.632, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658995.826, 6860724.858, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658995.533, 6860724.971, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658995.459, 6860724.972, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658995.459, 6860724.972, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658995.459, 6860724.972, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658995.313, 6860725.084, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658994.947, 6860725.198, 53.600), time)
    trace1.addObs(p1)
    
    p1 = Obs(ENUCoords(658994.508, 6860725.423, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658994.143, 6860725.648, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658993.852, 6860725.984, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658993.707, 6860726.318, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658993.637, 6860726.764, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658993.567, 6860727.209, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658993.497, 6860727.654, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658993.427, 6860728.099, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658993.283, 6860728.545, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658993.066, 6860728.992, 53.700), time)
    trace1.addObs(p1)
    
    p1 = Obs(ENUCoords(658992.848, 6860729.327, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658992.484, 6860729.663, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658992.118, 6860729.888, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658991.679, 6860730.113, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658991.167, 6860730.339, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658990.728, 6860730.454, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658990.362, 6860730.568, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658990.068, 6860730.570, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.848, 6860730.571, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.628, 6860730.684, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.555, 6860730.684, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.482, 6860730.685, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.408, 6860730.685, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.408, 6860730.685, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.408, 6860730.685, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.408, 6860730.685, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.335, 6860730.686, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.336, 6860730.797, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.262, 6860730.798, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.262, 6860730.798, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.189, 6860730.798, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.189, 6860730.798, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.189, 6860730.798, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.189, 6860730.798, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.189, 6860730.798, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.263, 6860730.909, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.336, 6860730.908, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.557, 6860730.907, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658989.703, 6860730.906, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658990.070, 6860730.903, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658990.585, 6860731.011, 53.800), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658991.393, 6860731.116, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658992.348, 6860731.221, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658993.377, 6860731.436, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658994.478, 6860731.428, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658995.432, 6860731.532, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658996.093, 6860731.528, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658996.460, 6860731.525, 53.700), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658996.679, 6860731.412, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658996.753, 6860731.412, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658996.827, 6860731.523, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658996.974, 6860731.633, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.048, 6860731.743, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.049, 6860731.855, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.123, 6860731.965, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.124, 6860732.076, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.198, 6860732.187, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.199, 6860732.298, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.200, 6860732.409, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.273, 6860732.409, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.273, 6860732.409, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.273, 6860732.409, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.273, 6860732.409, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.273, 6860732.409, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.273, 6860732.409, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.273, 6860732.409, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.273, 6860732.409, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.274, 6860732.520, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.274, 6860732.520, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.274, 6860732.520, 53.600), time)
    trace1.addObs(p1)
    p1 = Obs(ENUCoords(658997.274, 6860732.520, 53.600), time)
    trace1.addObs(p1)

    
    plt.plot(trace1.getX(), trace1.getY(), 'ro')

    cercle = minCircle(trace1)
    if cercle != None:
        print (cercle.radius, cercle.center)
        plt.plot(trace1.getX(), trace1.getY(), 'ro')
        cercle.plot()

if __name__ == '__main__':
    #example0()
    #example1()
    example2()



