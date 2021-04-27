# -*- coding: utf-8 -*-



class NetworkFormat:

    NETWORK_FILE_FORMAT = "../../resources/network_file_format"


    # -------------------------------------------------------------
    # Load file format from network_file_format
    # -------------------------------------------------------------
    def __init__(self, name):
        
        FIELDS = []
        with open(NetworkFormat.NETWORK_FILE_FORMAT) as ffmt:
            line = ffmt.readline().strip()
            while(line):
                if (line[0] == "#"):
                    line = ffmt.readline().strip()
                    continue
                tab = line.split(",")
                print (tab)
                if tab[0].strip() == name:
                    FIELDS = tab
                    break
                line = ffmt.readline().strip()
        ffmt.close()
        
        self.name = name
        self.edge_id = int(FIELDS[1].strip())
        self.source = int(FIELDS[2].strip())
        self.target = int(FIELDS[3].strip())
        self.wkt = str(FIELDS[4].strip())
        self.poids = float(FIELDS[5].strip())
        self.sens = int(FIELDS[6].strip())
        self.separator = FIELDS[7].strip()            
        self.h = int(FIELDS[8].strip())
        self.srid = FIELDS[9].strip()
        
        
