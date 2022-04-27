import math
import matplotlib.pyplot as plt

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


if __name__ == '__main__':
    example0()



