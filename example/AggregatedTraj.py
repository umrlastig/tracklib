# -*- coding: utf-8 -*-

import tracklib as tkl

import csv
import math
import numpy as np

# For 
from random import randint

# For plotting
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm

color = cm.rainbow(np.linspace(0, 1, 5))

def visualizeAggTraj(i, N=3, track=None, tracks=None, title=None):
    '''
    '''
    ax = plt.subplot2grid((1,N), (0,i))
    
    if tracks != None and isinstance(tracks, tkl.TrackCollection):
        for (i, t) in enumerate(tracks):
            ax.plot(t.getX(), t.getY(), c=color[i])
    
    if tracks != None and isinstance(tracks, tkl.Track):
        central = tracks
        ax.plot(central.getX(), central.getY(), 'c-')
    
    ax.plot(track.getX(), track.getY(), 'k-')
    if title != None:
        ax.set_title(title)
    ax.set_xlabel('')
    ax.set_xticks([])
    ax.set_ylabel('')
    ax.set_yticks([])
    ax.grid()

tkl.seed(123)

SHAPES = ['Almost straight', 'Moderate sinuosity', 'Switchbacks']

# ----------------------------------------------------------
# Generate the path 'Almost straight'
sentier1 = tkl.generate(0.5, dt=10)[::3]
sentier1.scale(8)


# ----------------------------------------------------------
sentier2 = tkl.generate(0.1, dt=10)[::3]
sentier2.scale(2)


# ----------------------------------------------------------
base_lacets = tkl.generate(0.4, dt=10)
sentier3 = tkl.noise(base_lacets, 20, tkl.SincKernel(20),
                    direction=tkl.MODE_DIRECTION_ORTHO)[::3]
sentier3.scale(2.5)


# ----------------------------------------------------------
sentiers = [sentier1, sentier2, sentier3]
print(sentier1.length())
print(sentier2.length())
print(sentier3.length())


# ----------------------------------------------------------
# Plot
print ('')
plt.figure(figsize=(15, 3))
plt.subplots_adjust(top=0.8, wspace=0.2, hspace=0.5)

visualizeAggTraj(0, track=sentier1, title='Almost straight')
visualizeAggTraj(1, track=sentier2, title='Moderate sinuosity')
visualizeAggTraj(2, track=sentier3, title='Switchbacks')
plt.show()


# =============================================================================
# =============================================================================
# =============================================================================


N = 4

# ----------------------------------------------------------
# Generate 'Almost straight'
tracks1 = tkl.core.TrackCollection([sentier1]*N)
tracks1.noise(0.5, tkl.GaussianKernel(50))
tracks1.noise(5, tkl.ExponentialKernel(20))
tracks1.noise(1, tkl.DiracKernel())

# ----------------------------------------------------------
# Generate 'Moderate sinuosity'
tracks2 = tkl.core.TrackCollection([sentier2]*N)
tracks2.noise(0.5, tkl.GaussianKernel(50))
tracks2.noise(5, tkl.ExponentialKernel(20))
tracks2.noise(1, tkl.DiracKernel())

# ----------------------------------------------------------
# Generate 'Switchbacks'
tracks3 = tkl.core.TrackCollection([sentier3]*N)
tracks3.noise(0.5, tkl.GaussianKernel(50))
tracks3.noise(5, tkl.ExponentialKernel(20))
tracks3.noise(1, tkl.DiracKernel())


# ----------------------------------------------------------
# Visualize one realistic noise track
print ('')

plt.figure(figsize=(15, 3))
plt.subplots_adjust(top=0.8, wspace=0.2, hspace=0.5)
visualizeAggTraj(0, N=3, track=sentier1, tracks=tracks1[0:3], title='Almost straight')
visualizeAggTraj(1, N=3, track=sentier2, tracks=tracks2[0:3], title='Moderate sinuosity')
visualizeAggTraj(2, N=3, track=sentier3, tracks=tracks3[0:3], title='Switchbacks')
plt.suptitle('A realistic noise applied in the three path shapes')
plt.show()



# =============================================================================
# =============================================================================
# =============================================================================

E = 20
FRECHET = {'Almost straight': tkl.TrackCollection(),
           'Moderate sinuosity': tkl.TrackCollection(),
           'Switchbacks': tkl.TrackCollection()}
DTW = {'Almost straight': tkl.TrackCollection(),
       'Moderate sinuosity': tkl.TrackCollection(),
       'Switchbacks': tkl.TrackCollection()}

represent_method = tkl.MODE_REP_BARYCENTRE
agg_method = tkl.MODE_AGG_MEDIAN
constraint = False
master = tkl.MODE_MASTER_MEDIAN_LEN
itermax = 15

for s in range(1, E+1):
    print ('Sample size: ', s)

    # create set
    TAB = set()
    while len(TAB) <= s:
        n = randint(0, N-1)
        TAB.add(n)

    sets1 = tkl.TrackCollection()
    sets2 = tkl.TrackCollection()
    sets3 = tkl.TrackCollection()
    for idx in TAB:
        sets1.addTrack(tracks1[idx])
        sets2.addTrack(tracks2[idx])
        sets3.addTrack(tracks3[idx])

    # ---------------------------------------------------------------------------
    # Fréchet
    p = float('inf')
    mode = tkl.MODE_MATCHING_FRECHET
    print ('    FRECHET')

    central1 = tkl.fusion(sets1, master=master, dim=2, mode=mode, p=p, represent_method=represent_method,  agg_method=agg_method,
                         constraint=constraint, verbose=False, iter_max = itermax)
    FRECHET['Almost straight'].addTrack(central1)

    central2 = tkl.fusion(sets2, master=master, dim=2, mode=mode, p=p, represent_method=represent_method,  agg_method=agg_method,
                         constraint=constraint, verbose=False, iter_max = itermax)
    FRECHET['Moderate sinuosity'].addTrack(central2)

    central3 = tkl.fusion(sets3, master=master, dim=2, mode=mode, p=p, represent_method=represent_method,  agg_method=agg_method,
                         constraint=constraint, verbose=False, iter_max = itermax)
    FRECHET['Switchbacks'].addTrack(central3)

    # ---------------------------------------------------------------------------
    # DTW
    p = 2
    mode = tkl.MODE_MATCHING_DTW
    print ('    DTW')
    
    central1 = tkl.fusion(sets1, master=master, dim=2, mode=mode, p=p, represent_method=represent_method,  agg_method=agg_method,
                         constraint=constraint, verbose=False, iter_max = itermax)
    DTW['Almost straight'].addTrack(central1)

    central2 = tkl.fusion(sets2, master=master, dim=2, mode=mode, p=p, represent_method=represent_method,  agg_method=agg_method,
                         constraint=constraint, verbose=False, iter_max = itermax)
    DTW['Moderate sinuosity'].addTrack(central2)

    central3 = tkl.fusion(sets3, master=master, dim=2, mode=mode, p=p, represent_method=represent_method,  agg_method=agg_method,
                         constraint=constraint, verbose=False, iter_max = itermax)
    DTW['Switchbacks'].addTrack(central3)


plt.figure(figsize=(15, 10))
plt.subplots_adjust(top=0.8, wspace=0.2, hspace=0.5)
T = [3, 20]
for i in range(len(T)):
    for s, title in enumerate(SHAPES):
        ax = plt.subplot2grid((len(T), len(SHAPES)), (i, s))
    
        c = FRECHET[title][i]
        ax.plot(c.getX(), c.getY(), label="Fréchet", color="deeppink", linewidth=2.0)
        c = DTW[title][i]
        ax.plot(c.getX(), c.getY(), label="DTW", color="lightseagreen", linewidth=2.0)

        ax.plot(sentiers[s].getX(), sentiers[s].getY(), label='path', color='darkgrey', linestyle='--')
        ax.legend()
        title = title + ", N'=" + str(T[i])
        ax.set_title(title)

plt.show()



# =============================================================================
# =============================================================================
# =============================================================================



def rmse(central, sentier):
    central.resample(npts=1000, mode=1)
    sentier.resample(npts=1000, mode=1)
    m = min(sentier.size(), central.size())
    
    # compute the distance NearestNeighbour
    return tkl.compare(central[0:m], sentier[0:m], tkl.MODE_COMPARISON_POINTWISE, p=2)

TSS = []
T1F=[]; T2F=[]; T3F=[]
T1D=[]; T2D=[]; T3D=[]
for s in range(0, E):
    TSS.append(s+1)
    T1F.append(rmse(FRECHET['Almost straight'][s], sentier1))
    T2F.append(rmse(FRECHET['Moderate sinuosity'][s], sentier2))
    T3F.append(rmse(FRECHET['Switchbacks'][s], sentier3))
    T1D.append(rmse(DTW['Almost straight'][s], sentier1))
    T2D.append(rmse(DTW['Moderate sinuosity'][s], sentier2))
    T3D.append(rmse(DTW['Switchbacks'][s], sentier3))


plt.figure(figsize=(15, 3))
plt.subplots_adjust(top=0.8, wspace=0.2, hspace=0.5)
    
ax1 = plt.subplot2grid((1,3), (0,0))
ax1.plot(TSS, T1D, label="Fréchet", color="deeppink")
ax1.plot(TSS, T1F, label="DTW", color="lightseagreen")
ax1.set_xlabel('sample size')
ax1.set_ylabel("RMSE")
ax1.set_title('Almost straight')
ax1.legend()

ax2 = plt.subplot2grid((1,3), (0,1))
ax2.plot(TSS, T2D, label="Fréchet", color="deeppink")
ax2.plot(TSS, T2F, label="DTW", color="lightseagreen")
ax2.set_xlabel('sample size')
ax2.set_ylabel("RMSE")
ax2.set_title('Moderate sinuosity')
ax2.legend()

ax3 = plt.subplot2grid((1,3), (0,2))
ax3.plot(TSS, T3D, label="Fréchet", color="deeppink")
ax3.plot(TSS, T3F, label="DTW", color="lightseagreen")
ax3.set_xlabel('sample size')
ax3.set_ylabel("RMSE")
ax3.set_title('Switchbacks')
ax3.legend()

plt.show()


# =============================================================================
# =============================================================================
# =============================================================================

def shapeDeviationMeasure(central, sentier):
    # Align the aggregated track with the reference track
    tkl.mapping.mapOn(central, sentier, verbose=False)

    # resample to 1000 points
    central.resample(npts=1000, mode=1)
    sentier.resample(npts=1000, mode=1)

    # compute the distance NearestNeighbour
    return tkl.compare(central, sentier, tkl.MODE_COMPARISON_NN, p=2, verbose=False)
    

TSS = []
T1F=[]; T2F=[]; T3F=[]
T1D=[]; T2D=[]; T3D=[]
for s in range(0, E):
    TSS.append(s+1)
    T1F.append(shapeDeviationMeasure(FRECHET['Almost straight'][s], sentier1))
    T2F.append(shapeDeviationMeasure(FRECHET['Moderate sinuosity'][s], sentier2))
    T3F.append(shapeDeviationMeasure(FRECHET['Switchbacks'][s], sentier3))
    T1D.append(shapeDeviationMeasure(DTW['Almost straight'][s], sentier1))
    T2D.append(shapeDeviationMeasure(DTW['Moderate sinuosity'][s], sentier2))
    T3D.append(shapeDeviationMeasure(DTW['Switchbacks'][s], sentier3))
    

plt.figure(figsize=(15, 3))
plt.subplots_adjust(top=0.8, wspace=0.2, hspace=0.5)
    
ax1 = plt.subplot2grid((1,3), (0,0))
ax1.plot(TSS, T1D, label="Fréchet", color="deeppink")
ax1.plot(TSS, T1F, label="DTW", color="lightseagreen")
ax1.set_xlabel('sample size')
ax1.set_ylabel("Nearest Neighbor distance (m)")
ax1.set_title('Almost straight')
ax1.legend()

ax2 = plt.subplot2grid((1,3), (0,1))
ax2.plot(TSS, T2D, label="Fréchet", color="deeppink")
ax2.plot(TSS, T2F, label="DTW", color="lightseagreen")
ax2.set_xlabel('sample size')
ax2.set_ylabel("Nearest Neighbor distance (m)")
ax2.set_title('Moderate sinuosity')
ax2.legend()

ax3 = plt.subplot2grid((1,3), (0,2))
ax3.plot(TSS, T3D, label="Fréchet", color="deeppink")
ax3.plot(TSS, T3F, label="DTW", color="lightseagreen")
ax3.set_xlabel('sample size')
ax3.set_ylabel("Nearest Neighbor distance (m)")
ax3.set_title('Switchbacks')
ax3.legend()

plt.show()





# =============================================================================
# =============================================================================
# =============================================================================



