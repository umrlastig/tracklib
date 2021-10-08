# -*- coding: utf-8 -*-

import os.path

class NetworkFormat:

    resource_path = os.path.join(os.path.split(__file__)[0], "../..")
    NETWORK_FILE_FORMAT = os.path.join(resource_path, "resources/network_file_format")

    # -------------------------------------------------------------
    # Load file format from network_file_format
    # -------------------------------------------------------------
    def __init__(self, name = None):
        
        if name != None and name != '':
            self.createFromFile(name)
        else:
            self.name = 'UNDEFINED'
            
            
    def createFromFile(self, name):
        
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
    
    
    '''
    '''
    def createFromDict(self, param):
        
        if param['name'] != None and param['name'] != '':
            self.name = param['name']
        
        if param['pos_edge_id'] != None and param['pos_edge_id'] != '':
            self.pos_edge_id = param['pos_edge_id']
        
        if param['pos_source'] != None and param['pos_source'] != '':
            self.pos_source = param['pos_source']
            
        if param['pos_target'] != None and param['pos_target'] != '':
            self.pos_target = param['pos_target']
            
        if param['pos_wkt'] != None and param['pos_wkt'] != '':
            self.pos_wkt = param['pos_wkt']
            
        if param['pos_poids'] != None and param['pos_poids'] != '':
            self.pos_poids = param['pos_poids']
            
        if param['pos_sens'] != None and param['pos_sens'] != '':
            self.pos_sens = param['pos_sens']
            
        if param['srid'] != None and param['srid'] != '':
            self.srid = param['srid']