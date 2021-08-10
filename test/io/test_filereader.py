# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt

from tracklib.io.FileReader import FileReader



# =============================================================
# csvpath = '../../data/wkt/bati.wkt'
# TRACES = FileReader.readFromWKTFile(csvpath, 0)
# for trace in TRACES:
#     plt.plot(trace.getX(), trace.getY())
# plt.show()


# =============================================================
csvpath = '../../data/wkt/iti.wkt'
TRACES = FileReader.readFromWKTFile(csvpath, 0, -1, -1, "#", 1, "ENUCoords", None, True)
# id_user=-1, id_track=-1, separator=";", h=0, srid="ENUCoords", bboxFilter=None

for trace in TRACES:
    plt.plot(trace.getX(), trace.getY())
plt.show()



