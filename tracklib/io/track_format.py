# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Yann Méneroux
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



File format to read and write GPS tracks to CSV file(s).

"""

import os.path
from typing import Union

from tracklib.util.exceptions import *
from tracklib.core import ObsTime
from tracklib.algo.selection import Selector

class TrackFormat:
    '''
        A format is a structure to store paramaters needeed to load a Track

        Mandatory parameter
        -------------------

        # ext:       file having this extension will be automatically read and written in this format
           default value is CSV
           value in {CVS, GPX, WKT}
        #   name:      format name (used as input in FileReader and FileWriter)
        
        
        #   col_id_X:  index (starts from 0) of column containing coordinate X (for ECEF), longitude (GEO) or E (ENU)
        #   col_id_Y:  index (starts from 0) of column containing coordinate Y (for ECEF), latitude (GEO) or N (ENU)
        #   col_id_Z:  index (starts from 0) of column containing Z (for ECEF), height or altitude (GEO/ENU)
        #   col_id_T:  index (starts from 0) of column containing timestamp (in seconds or in time_fmt format)

        #   srid:      coordinate system of points (ENU, Geo or ECEF) 
        
        #   date_ini:  initial date (in time_fmt format) if timestamps are provided in seconds (-1 if not used)
        #   time_fmt:  timestamp format (format definition according to GPSTime class)

        #   sep:       separating characters (can be multiple characters). Can be c (comma), b (blankspace), s (semi-column)
        #   header:    number of heading line in format 
        #   cmt:       comment character (lines starting with cmt on the top left are skipped)
        #   no_data:   a special float or integer indicating that record is non-valid and should be skipped
        #   read_all:  read all fields in data file (registered as analytical features) 

    '''

    resource_path = os.path.join(os.path.split(__file__)[0], "../..")
    TRACK_FILE_FORMAT = os.path.join(resource_path, "resources/track_file_format")


    # -------------------------------------------------------------
    # Load file format from track_file_format
    # -------------------------------------------------------------
    def __init__(self, name:Union[str, dict]="DEFAULT"):
        """TODO"""

        self.ext = None

        # Base default features
        self.name = "UNDEFINED"

        self.id_user = -1
        self.id_track = -1

        self.id_E = -1
        self.id_N = -1
        self.id_U = -1
        self.id_T = -1

        self.type = 'trk' # rteType, wptType
        self.id_wkt = -1

        if isinstance(name, dict) and name['ext'] == "CSV":
            self.srid = "ENU"
        elif isinstance(name, dict) and name['ext'] == "GPX":
            self.srid = "GEO"
        elif isinstance(name, dict) and name['ext'] == "WKT":
            self.srid = "ENU"
        else:
            self.srid = "ENU"


        self.time_ini = -1
        self.time_fmt = ObsTime.getReadFormat()
        self.time_unit = 1

        self.separator = ","
        self.header = 0
        self.cmt = "#"
        self.no_data_value = -999999
        self.doublequote = False
        self.encoding = "UTF-8"

        self.selector = None

        self.af_names = []
        self.read_all = False

        if isinstance(name, dict):
            # Features updated from hashtable
            self.createFromDict(name)

        elif isinstance (name, str) and name != 'DEFAULT':
            # Features updated from file
            self.createFromFile(name)



    def createFromDict(self, param):
        """TODO"""
        list_of_fields = []

        if "name" in param:
            self.name = param["name"]
        if "ext" in param:
            self.ext = param["ext"]

        if "srid" in param:
            self.srid = param["srid"]
        if "time_ini" in param:
            self.time_ini = param["time_ini"]
        if "time_fmt" in param:
            self.time_fmt = param["time_fmt"]
        if "time_unit" in param:
            self.time_unit = param["time_unit"]

        if "id_user" in param:
            self.id_user = param["id_user"]
        if "id_track" in param:
            self.id_track = param["id_track"]

        if "id_E" in param:
            self.id_E = param["id_E"]
        if "id_N" in param:
            self.id_N = param["id_N"]
        if "id_U" in param:
            self.id_U = param["id_U"]
        if "id_T" in param:
            self.id_T = param["id_T"]
        if "id_wkt" in param:
            self.id_wkt = param["id_wkt"]
        if "type" in param:
            self.type = param["type"]
            # type: Literal["trk", "rte"]="trk"

        if "separator" in param:
            self.separator = param["separator"]            
        if "header" in param:
            self.header = param["header"]
        if "cmt" in param:
            self.cmt = param["cmt"]
        if "no_data_value" in param:
            self.no_data_value = param["no_data_value"]
        if "doublequote" in param:
            self.doublequote = param["doublequote"]
        if "encoding" in param:
            self.encoding = param["encoding"]

        if "selector" in param:
            self.selector = param["selector"]

#        if "af_names" in param:
#            self.af_names = af_names
        if "read_all" in param:
            self.read_all = param['read_all']



    def createFromFile(self, name):
        """TODO"""

        FIELDS = []
        with open(TrackFormat.TRACK_FILE_FORMAT) as ffmt:
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
        self.ext = str(FIELDS[1].strip())

        self.id_E = int(FIELDS[2].strip())
        self.id_N = int(FIELDS[3].strip())
        self.id_U = int(FIELDS[4].strip())
        self.id_T = int(FIELDS[5].strip())

        self.time_ini = FIELDS[6].strip()
        if self.time_ini == "-1":
            self.time_ini = -1
        else:
            fmt_temp = ObsTime.getReadFormat()
            ObsTime.setReadFormat(self.time_fmt)
            self.time_ini = ObsTime(self.time_ini)
            ObsTime.setReadFormat(fmt_temp)
        self.time_unit = 1
        self.time_fmt = FIELDS[12].strip()

        self.header = int(FIELDS[8].strip())
        self.cmt = FIELDS[9].strip()
        self.doublequote = True
        self.encoding = "utf-8"
        self.no_data_value = float(FIELDS[10].strip())

        self.srid = FIELDS[11].strip()

        self.separator = FIELDS[7].strip()
        self.separator = self.separator.replace("b", " ")
        self.separator = self.separator.replace("c", ",")
        self.separator = self.separator.replace("s", ";")

        self.read_all = FIELDS[13].strip().upper() == "TRUE"


    def __str__(self):
        output  = "----------------------------------------\n"
        output += "Track file format:\n"
        output += "----------------------------------------\n"
        output += "Name:         " + str(self.name) + "\n"
        output += "Ext:          " + str(self.ext) + "\n"
        output += "\n"
        output += "SRID:         " + str(self.srid) + "\n"
        output += "\n"
        output += "CSV format: \n"
        output += "----------- \n"
        output += "id_E:         " + str(self.id_E) + "\n"
        output += "id_N:         " + str(self.id_N) + "\n"
        output += "id_U:         " + str(self.id_U) + "\n"
        output += "id_T:         " + str(self.id_T) + "\n"
        #output += "Source:       " + str(self.pos_source) + "\n"
        #output += "Target:       " + str(self.pos_target) + "\n"
        #output += "Geom:         " + str(self.pos_wkt) + "\n"
        #output += "Weight:       " + str(self.pos_weight) + "\n"
        #output += "Direction:    " + str(self.pos_direction) + "\n"
        #output += "Seperator:    [" + str(self.separator) + "]\n"
        #output += "Header:       " + str(self.header) + "\n"
        #output += "Double-quote: " + str(self.doublequote) + "\n"
        #output += "Encoding:     " + str(self.encoding) + "\n"

        output += "\n"
        output += "GPX format: \n"

        output += "----------------------------------------\n"


        '''

        self.id_user = -1
        self.id_track = -1

        self.id_E = -1
        self.id_N = -1
        self.id_U = -1
        self.id_T = -1

        self.type = 'trkType' # rteType, wptType
        self.id_wkt = -1

        self.srid = "ENUCoords"

        self.time_ini = -1
        self.time_fmt = ObsTime.getReadFormat()

        self.separator = ","
        self.header = 0
        self.cmt = "#"
        self.no_data_value = -999999
        self.doublequote = False
        self.encoding = "UTF-8"

        self.selector = None

        self.af_names = []
        self.read_all = False
        
        '''

        return output


    def asString(self):
        sep = self.separator 
        sep = sep.replace(" ", "b")
        sep = sep.replace(",", "c")
        sep = sep.replace(";", "s")
        
        out  = str(self.name) +", "
        #out += str(self.pos_edge_id) +", "
        #out += str(self.pos_source) +", "
        #out += str(self.pos_target) +", "
        #out += str(self.pos_wkt) +", "
        #out += str(self.pos_weight) +", "
        #out += str(self.pos_direction) +", "
        #out += str(sep) +", "
        #out += str(self.header) +", "
        #out += str(self.doublequote) +", "
        #out += str(self.encoding) +", "
        #out += str(self.srid)
        return out


    def controlFormat(self):
        '''
        '''

        if self.separator == "":
            raise WrongArgumentError("Incorrect value for 'separator' in track file format: " + str(self.separator))

        if self.selector != None and not isinstance(self.selector, Selector):
            raise WrongArgumentError("Incorrect value for 'selector' in track file format: " + str(type(self.selector)))


        # ---------------------------------------------------------------------
        #     CSV file
        if self.ext == "CSV":
            if self.id_E < 0:
                raise WrongArgumentError("Incorrect value for 'id_E' in track file format: " + str(self.id_E))
            if self.id_N < 0:
                raise WrongArgumentError("Incorrect value for 'id_N' in track file format: " + str(self.id_N))
        
        '''
        # ---------------------------------------------------------------------
        #     WKT file
        if self.ext == "WKT":
            if self.separator == " ":
                raise WrongArgumentError("Error: separator must not be space for reading WKT file")
        '''






