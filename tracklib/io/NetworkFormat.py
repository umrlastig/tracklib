# -*- coding: utf-8 -*-



class NetworkFormat:

    NETWORK_FILE_FORMAT = "./resources/network_file_format"


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
        self.encode = 'utf-8'
        
        self.srid = FIELDS[11].strip()
        
        self.separator = FIELDS[7].strip()
        self.separator = self.separator.replace("b", " ")
        self.separator = self.separator.replace("c", ",")
        self.separator = self.separator.replace("s", ";")	
