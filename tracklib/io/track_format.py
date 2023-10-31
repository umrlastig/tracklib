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

from tracklib.core import ObsTime


class TrackFormat:
    """TODO"""

    resource_path = os.path.join(os.path.split(__file__)[0], "../..")
    TRACK_FILE_FORMAT = os.path.join(resource_path, "resources/track_file_format")

    @staticmethod
    def __search_fmt_from_ext_or_name(file_format_path, arg, ext=0):
        """TODO"""
        # ext = 0 for search by name and 1 for search by ext
        if ext == 1:
            arg = arg.split(".")[-1]
        with open(file_format_path) as ffmt:
            line = ffmt.readline().strip()
            while line:
                if line[0] == "#":
                    line = ffmt.readline().strip()
                    continue
                fields = line.split(",")
                if fields[ext].strip() == arg:
                    return fields
                line = ffmt.readline().strip()
        word = "extension"
        if ext == 0:
            word = "format"
        print(
            "ERROR: "
            + word
            + " ["
            + arg
            + "] is not a standard format in "
            + file_format_path
        )
        exit()

    # -------------------------------------------------------------
    # Load file format from track_file_format
    # ext:
    #    1 to infer format through extension
    #    0 to infer format directly through name
    #   -1 no format inference
    # -------------------------------------------------------------
    def __init__(self, arg, ext=-1):
        """TODO"""

        if ext >= 0:

            fields = TrackFormat.__search_fmt_from_ext_or_name(
                TrackFormat.TRACK_FILE_FORMAT, arg, ext
            )

            self.name = fields[0].strip()
            self.id_E = int(fields[2].strip())
            self.id_N = int(fields[3].strip())
            self.id_U = int(fields[4].strip())
            self.id_T = int(fields[5].strip())
            self.DateIni = fields[6].strip()
            self.separator = fields[7].strip()
            self.h = int(fields[8].strip())
            self.com = fields[9].strip()
            self.no_data_value = float(fields[10].strip())
            self.srid = fields[11].strip()
            self.read_all = fields[13].strip().upper() == "TRUE"

            self.time_fmt = fields[12].strip()

            self.separator = self.separator.replace("b", " ")
            self.separator = self.separator.replace("c", ",")
            self.separator = self.separator.replace("s", ";")

            if self.DateIni == "-1":
                self.DateIni = -1
            else:
                fmt_temp = ObsTime.getReadFormat()
                ObsTime.setReadFormat(self.time_fmt)
                self.DateIni = ObsTime(self.DateIni)
                ObsTime.setReadFormat(fmt_temp)
        else:

            self.id_E = -1
            self.id_N = -1
            self.id_U = -1
            self.id_T = -1
            self.DateIni = -1
            self.separator = ","
            self.h = 0
            self.com = "#"
            self.no_data_value = -999999
            self.srid = "ENUCoords"
            self.read_all = False

            self.time_fmt = ObsTime.getReadFormat()
