# -*- coding: utf-8 -*-

#

def wktToLine(wkt):
    '''
    Une polyligne de n points est modélisée par une liste de 2n coordonnées réelles [x0,y0,x1,y1,...xn,yn]
    '''
    
    # Creation d'une liste vide
    LIGNE = list()

    # Separation de la chaine
    coords_string = wkt.split("(")
    coords_string = coords_string[1]
    coords_string = coords_string.split(")")[0]

    coords = coords_string.split(",")

    # Parcours des points
    for i in range(0, len(coords)):
        x, y = coords[i].strip().split(" ")

        LIGNE.append((float)(x))
        LIGNE.append((float)(y))

    return LIGNE

