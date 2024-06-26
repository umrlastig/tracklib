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

        # Base default features
        self.name = "UNDEFINED"
        self.pos_edge_id = -1
        self.pos_source = -1
        self.pos_target = -1
        self.pos_wkt = -1
        self.pos_weight = -1
        self.pos_direction = -1
        self.separator = ","
        self.header = 1
        self.doublequote = -1
        self.encoding = "UTF-8"
        self.srid = "ENU"
        
        # Features updated from file
        if 'str' in str(type(name)):
            self.createFromFile(name)
            return
         
        # Features updated from hash   
        if 'dict' in str(type(name)):    
            self.createFromDict(name)
            return

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
        self.pos_weight = int(FIELDS[5].strip())
        self.pos_direction = int(FIELDS[6].strip())

        self.header = int(FIELDS[8].strip())
        self.doublequote = True
        self.encoding = "utf-8"

        self.srid = FIELDS[11].strip()

        self.separator = FIELDS[7].strip()
        self.separator = self.separator.replace("b", " ")
        self.separator = self.separator.replace("c", ",")
        self.separator = self.separator.replace("s", ";")

    """
    """

    def createFromDict(self, param):
        """TODO"""
        list_of_fields = []
        if "name" in param:
            self.name = param["name"]
        if "pos_edge_id" in param:
            self.pos_edge_id = param["pos_edge_id"]
        if "pos_source" in param:
            self.pos_source = param["pos_source"]
        if "pos_target" in param:
            self.pos_target = param["pos_target"]            
        if "pos_wkt" in param:
            self.pos_wkt = param["pos_wkt"]                  
        if "pos_weight" in param:
            self.pos_weight = param["pos_weight"]            
        if "pos_direction" in param:
            self.pos_direction = param["pos_direction"]            
        if "separator" in param:
            self.separator = param["separator"]            
        if "header" in param:
            self.header = param["header"]
        if "doublequote" in param:
            self.doublequote = param["doublequote"]
        if "encoding" in param:
            self.encoding = param["encoding"]            
        if "srid" in param:
            self.srid = param["srid"]                      

    def __str__(self):
        output  = "----------------------------------------\n"
        output += "Network file format:\n"
        output += "----------------------------------------\n"
        output += "Name:         " + str(self.name) + "\n"
        output += "Edge:         " + str(self.pos_edge_id) + "\n"
        output += "Source:       " + str(self.pos_source) + "\n"
        output += "Target:       " + str(self.pos_target) + "\n"
        output += "Geom:         " + str(self.pos_wkt) + "\n"
        output += "Weight:       " + str(self.pos_weight) + "\n"
        output += "Direction:    " + str(self.pos_direction) + "\n"
        output += "Seperator:    [" + str(self.separator) + "]\n"
        output += "Header:       " + str(self.header) + "\n"
        output += "Double-quote: " + str(self.doublequote) + "\n"
        output += "Encoding:     " + str(self.encoding) + "\n"
        output += "SRID:         " + str(self.srid) + "\n"
        output += "----------------------------------------\n"
        return output

    def controlFormat(self):
        if self.pos_edge_id < 0:
            raise WrongArgumentError("Incorrect value for 'pos_edge_id' in network file format: " + str(self.pos_edge_id))
        if self.pos_source < 0:
            raise WrongArgumentError("Incorrect value for 'pos_source' in network file format: " + str(self.pos_source))
        if self.pos_target < 0:
            raise WrongArgumentError("Incorrect value for 'pos_target' in network file format: " + str(self.pos_target))
        if self.pos_wkt < 0:
            raise WrongArgumentError("Incorrect value for 'pos_wkt' in network file format: " + str(self.pos_wkt))
        if self.separator == "":
            raise WrongArgumentError("Incorrect value for 'separator' in network file format: " + str(self.separator))
