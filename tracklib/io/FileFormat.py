"""File format to read and write GPS tracks to CSV file(s)."""

import os.path

from tracklib.core.GPSTime import GPSTime


class FileFormat:

    resource_path = os.path.join(os.path.split(__file__)[0], "../..")
    TRACK_FILE_FORMAT = os.path.join(resource_path, "resources/track_file_format")

    @staticmethod
    def __search_fmt_from_ext_or_name(file_format_path, arg, ext=0):
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

        if ext >= 0:

            fields = FileFormat.__search_fmt_from_ext_or_name(
                FileFormat.TRACK_FILE_FORMAT, arg, ext
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
                fmt_temp = GPSTime.getReadFormat()
                GPSTime.setReadFormat(self.time_fmt)
                self.DateIni = GPSTime(self.DateIni)
                GPSTime.setReadFormat(fmt_temp)
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

            self.time_fmt = GPSTime.getReadFormat()
