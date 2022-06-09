import math
import matplotlib.pyplot as plt

import tracklib.algo.Synthetics as Synthetics
import tracklib.algo.Comparison as Comparison
import tracklib.algo.Dynamics as Dynamics

from tracklib.core.Kernel import GaussianKernel


# -----------------------------------------------------------------------
# Example 0: DTW computation with HMM
# -----------------------------------------------------------------------

def example0():

    track1 = Synthetics.generate(1e-1, dt=30)
    track2 = track1.noise(10, GaussianKernel(25))

	
    S = lambda track, k: [p for p in range(max(0,k-30),  min(len(track2)-1, k+30))]
    #S = lambda t, k: [p for p in range(0, len(track2)-1)]
    Q = lambda i,j,k,t: (j<i+30)*(j>=i)*1
    P = lambda s,y,k,t: math.exp(-track2[s].position.distance2DTo(y))

    Dynamics.HMM(S, Q, P).estimate(track1, ["x","y"], mode=Dynamics.MODE_OBS_AS_2D_POSITIONS, verbose=2)
	 

    track1.plot('r-')
    track2.plot('b-')
    Comparison.plotDifferenceProfile(track1, track2, "hmm_inference")
    plt.show()
    
    
if __name__ == '__main__':
    example0()

