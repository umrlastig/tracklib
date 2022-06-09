# -*- coding: utf-8 -*-



from tracklib.io.AsciiReader import AsciiReader

chemin = 'tracklib/data/asc/test.asc'
grid = AsciiReader.readFromFile(chemin)
print (grid)


    
    