import os
import sys
import math
import random
import numpy as np
import matplotlib.pyplot as plt

sys.path.append('~/Bureau/KitYann/2-Tracklib/tracklib/tracklib')


# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt

# On charge les données
from tracklib.core.ObsTime import ObsTime
from tracklib.io.TrackReader import TrackReader
from tracklib.io.NetworkReader import NetworkReader
from tracklib.core.SpatialIndex import SpatialIndex
import tracklib.algo.Mapping as mapping
import tracklib.algo.Comparison as Comparison
import tracklib.algo.Analytics as Analytics





# Tests sur la gestion des AF

track = TrackReader.readFromGpx("2023-03-04_10-41_Sat_OSM.gpx")[0][:6000]


# Create AF from dedicated function
track.createAnalyticalFeature("an_af", 0)

# Remove an AF from dedicated function
track.removeAnalyticalFeature("an_af")

# Create AF from dedicated function with list
track.createAnalyticalFeature("another_af", [1]*len(track))

# Update AF from dedicated function
track.updateAnalyticalFeature("another_af", 10)

# Update AF from dedicated function with list
track.updateAnalyticalFeature("another_af", [20]*len(track))


# Forbidden names
# track.createAnalyticalFeature("x")
# track.createAnalyticalFeature("y")
# track.createAnalyticalFeature("z")
# track.createAnalyticalFeature("t")
# track.createAnalyticalFeature("timestamp")
# track.createAnalyticalFeature("idx")

# Shortcut to create AF
track["af"] = 0

# Shortcut to create from list
track["af"] = [i for i in range(len(track))]

# Acces value of all AF
A = track["af"] 

# Access value of the AF of given obs
x = track["af", 3]
x = track[3, "af"]

# Modify value of the AF of given obs
track["af", 3] = 123
track[5, "af"] = 123

# Remove AF with special set instruction
track["af"] = "#DELETE"
track["another_af"] = "#DELETE"

# Add analytical feature from function
def algo(track, i):
    return i

track.addAnalyticalFeature(algo, "compteur")
track["compteur"] = algo

# Add analytical feature from Built in AF
track["speed"] = Analytics.speed
track["speed"] = "#DELETE"




# Init random AF with lambda function
track["random_af"] = lambda track, i : random.random()-0.5


# Operation on an AF
print(track["2*random_af"])
track["cumul = I(random_af)"]

# Search on AF values
track.query("SELECT * WHERE compteur<20")


# Plot an AF
plt.plot(track["cumul"])
plt.show()

track.print(10)
