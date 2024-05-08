# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Marie-Dominique Van Damme
Creation date: 1th november 2020

tracklib library provides a variety of tools, operators and 
functions to manipulate GPS trajectories. It is a open source contribution 
of the LASTIG laboratory at the Institut National de l'Information 
Géographique et Forestière (the French National Mapping Agency).
See: https://tracklib.readthedocs.io
 
This software is governed by the CeCILL-C license under French law and
abiding by the rules of distribution of free software. You can  use, 
modify and/ or redistribute the software under the terms of the CeCILL-C
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info". 

As a counterpart to the access to the source code and rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability. 

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or 
data to be ensured and,  more generally, to use and operate it in the 
same conditions as regards security. 

The fact that you are presently reading this means that you have had
knowledge of the CeCILL-C license and that you accept its terms.


Write Networks

"""

import os.path
from tracklib.util.exceptions import *


class NetworkFormat:
    """TODO"""

    resource_path = os.path.join(os.path.split(__file__)[0], "../..")
    NETWORK_FILE_FORMAT = os.path.join(resource_path, "resources/network_file_format")

    # -------------------------------------------------------------
    # Load file format from network_file_format
    # -------------------------------------------------------------
    def __init__(self, name=None):
        """TODO"""

        if name != None and name != "":
            self.createFromFile(name)
        else:
            self.name = "UNDEFINED"

    def createFromFile(self, name):
        """TODO"""

        FIELDS = []
        with open(NetworkFormat.NETWORK_FILE_FORMAT) as ffmt:
            line = ffmt.readline().strip()
            while line:
                if line[0] == "#":
                    line = ffmt.readline().strip()
                    continue
                tab = line.split(",")
                if tab[0].strip() == name:
                    FIELDS = tab
                    break
                line = ffmt.readline().strip()
        ffmt.close()

        if len(FIELDS) < 1:
            print("Error: import format not recognize")
            exit()

        self.name = name
        self.pos_edge_id = int(FIELDS[1].strip())
        self.pos_source = int(FIELDS[2].strip())
        self.pos_target = int(FIELDS[3].strip())
        self.pos_wkt = int(FIELDS[4].strip())
        self.pos_poids = int(FIELDS[5].strip())
        self.pos_sens = int(FIELDS[6].strip())

        self.h = int(FIELDS[8].strip())
        self.doublequote = True
        self.encode = "utf-8"

        self.srid = FIELDS[11].strip()

        self.separator = FIELDS[7].strip()
        self.separator = self.separator.replace("b", " ")
        self.separator = self.separator.replace("c", ",")
        self.separator = self.separator.replace("s", ";")

    """
    """

    def createFromDict(self, param):
        """TODO"""

        if param["name"] != None and param["name"] != "":
            self.name = param["name"]

        if param["pos_edge_id"] != None and param["pos_edge_id"] != "":
            self.pos_edge_id = param["pos_edge_id"]

        if param["pos_source"] != None and param["pos_source"] != "":
            self.pos_source = param["pos_source"]

        if param["pos_target"] != None and param["pos_target"] != "":
            self.pos_target = param["pos_target"]

        if param["pos_wkt"] != None and param["pos_wkt"] != "":
            self.pos_wkt = param["pos_wkt"]

        if param["pos_poids"] != None and param["pos_poids"] != "":
            self.pos_poids = param["pos_poids"]

        if param["pos_sens"] != None and param["pos_sens"] != "":
            self.pos_sens = param["pos_sens"]

        if param["srid"] != None and param["srid"] != "":
            self.srid = param["srid"]
