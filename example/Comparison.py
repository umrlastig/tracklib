
import matplotlib.pyplot as plt

import tracklib.algo.Stochastics as Stochastics
import tracklib.algo.Synthetics as Synthetics
import tracklib.algo.Comparison as Comparison

from tracklib.algo.Stochastics import NoiseProcess

from tracklib.core.Kernel import GaussianKernel



# -----------------------------------------------------------------------
# Example 0: comparison between two tracks
# Mode:
#   - 'NN'   :  Fast but sometimes incorrect + artifacts problem
#   - 'DTW'  :  Very slow but optimal 
#   - 'FDTW' :  Fast and nearly optimal for well-behaved inputs
# -----------------------------------------------------------------------

def example0(mode='FDTW'):

    Stochastics.seed(1234)

    track1 = Synthetics.generate(2e-1, dt=30)
    track2 = track1.noise(10, GaussianKernel(25))
	
    track1.plot('r-')
    track2.plot('r-')
	
    profile = Comparison.differenceProfile(track2, track1, mode, p=2)
    Comparison.plotDifferenceProfile(profile, track1)
	
    plt.show()

	
example0()	

# -----------------------------------------------------------------------
# Example 1: central profile of a track collection
# Mode:
#   - 'NN'   :  Fast but sometimes incorrect + artifacts problem
#   - 'DTW'  :  Very slow but optimal 
#   - 'FDTW' :  Fast and nearly optimal for well-behaved inputs
# N is the number of tracks to generate
# -----------------------------------------------------------------------

def example1(mode='FDTW', N=5):

    track = Synthetics.generate(1e-1, dt=30)
    tracks = NoiseProcess(5, GaussianKernel(5)).noise(track, N)

    central = Comparison.centralTrack(tracks, mode=mode)

    tracks.plot('r-')
    central.plot('b-')
    plt.show()


# example1()

