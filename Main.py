import tracklib as tkl
import matplotlib.pyplot as plt



tkl.stochastics.seed(123)
track = tkl.synthetics.generate(0.1)
track.plot('b-')

N = 5
tracks = tkl.core.TrackCollection([track]*N)
tracks.noise(3, tkl.kernel.ExponentialKernel(100))

for t in tracks:
     plt.plot(t["x"], t["y"], 'k-', linewidth=.25)

#central1 = tkl.algo.comparison.fusion(tracks, lambda A, B : A + B**2);    
central1 = tkl.fusion(tracks, lambda A, B : A + B**2);    

central1.plot('r-')

plt.show()
