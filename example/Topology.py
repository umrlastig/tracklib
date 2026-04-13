# -*- coding: utf-8 -*-


import matplotlib.pyplot as plt
import tracklib as tkl


NETPATH = r'/home/md_vandamme/res.csv'
output_file = r'/home/md_vandamme/res_topology.csv'

tkl.Topology.create_topology(NETPATH, '2154', output_file)


fmt = tkl.NetworkFormat({
       "pos_edge_id": 0,
       "pos_source": 1,
       "pos_target": 2,
       "pos_wkt": 3,
       "srid": "ENU",
       "separator": ",",
       "header": 1})
network = tkl.NetworkReader.readFromFile(output_file, fmt, verbose=False)
network.plot('k-', 'ro', 'g-', 'r-', 0.5, plt)
