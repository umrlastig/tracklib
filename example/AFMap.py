# -*- coding: utf-8 -*-

# Matplotlib to create visualizations
# import matplotlib.pyplot as plt

# Import the Tracklib library
import tracklib as tkl

tkl.ObsTime.setReadFormat("2D/2M/4Y 2h:2m:2s")
chemin = '/home/md_vandamme/tracklib/trajlib/reseau/data2/'
fmt = tkl.TrackFormat({"ext": 'CSV',
    "id_E": 1,
    "id_N": 0,
    "id_U": 3,
    "id_T": 2,
    "h": 1,
    "separator": ";",
    "srid": "ENU"})
collection = tkl.TrackSource(chemin, fmt)
total = len(collection)
print ('Number of tracks: ' + str(total))

xMin = 657336
yMin = 6860189
xMax = 657890
yMax = 6860625

ll = tkl.ENUCoords(xMin, yMin)
ur = tkl.ENUCoords(xMax, yMax)
bbox = tkl.Rectangle(ll, ur)

constraintBBox = tkl.Constraint(shape = bbox, mode = tkl.MODE_INSIDE, type=tkl.TYPE_CUT_AND_SELECT)
lakeCollection = constraintBBox.select(collection)
print ('Number of tracks near the lake: ' + str(lakeCollection.size()))
lakeCollection.plot('g-')


bbox = lakeCollection.bbox()
marge = 0.05
resolution = (2, 2)

raster = tkl.Raster(bbox=lakeCollection.bbox(), resolution=resolution, margin=marge,
                align=tkl.BBOX_ALIGN_CENTER)

uidMap = raster.addAFMap("uid")
uidMap.addCountDistinct()

cpt = 1
for trace in lakeCollection:
    trace.uid = cpt
    trace.resample(1, mode=1)
    cpt += 1

tkl.summarize(lakeCollection, raster)
print ('Raster created.')

grid = raster.getAFMap('uid')['count_distinct']
grid.plot(cmap='jet')




