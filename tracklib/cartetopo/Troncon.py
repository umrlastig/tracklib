# -*- coding: utf-8 -*-


# ----------------------------------------------------
#   Troncon IGN
#   Geometrie : tableau de 3 coordonnées
#
class Troncon:
    
    def __init__(self, id, coords, nature, sens, fictif, pos):
        self.id = id
        self.coords = coords
        self.nature = nature
        self.sens = sens
        self.fictif = fictif
        self.pos = pos
        
    