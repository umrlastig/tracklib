# -*- coding: utf-8 -*-
# -------------------------- Doc -------------------------------
# Geometry Functions  like:
#    - cartesienne
#    - dist_point_droite
#    - projection_droite
#    - proj_segment
#    - proj_polyligne
#    - triangle_area
#    - distance_to_segment
#    - aire_visval
# ----------------------------------------------------------------

import math


# ----------------------------------------
# Fonction equation cartesienne
# Entree : segment
# Sortie : liste de parametres (a,b,c)
# ----------------------------------------
def cartesienne(segment):
    
    parametres = list();
    
    x1 = segment[0]
    y1 = segment[1]
    x2 = segment[2]
    y2 = segment[3]
    
    u1 = x2-x1
    u2 = y2-y1
    
    b = -u1
    a = u2
    
    c = -(a*x1+b*y1)
    
    parametres.append(a)
    parametres.append(b)
    parametres.append(c)
    
    return parametres


# ----------------------------------------
# Fonction distance point-droite
# Entree : paramètres a,b,c d'une droite, 
# coordonnées x et y du point
# Sortie : distance du point à la droite
# ----------------------------------------
def dist_point_droite(param, x, y):
    
    a = param[0]
    b = param[1]
    c = param[2]

    distance = math.fabs(a*x+b*y+c)
    distance /= math.sqrt(a*a+b*b)
    
    return distance
    

# ----------------------------------------
# Fonction projection orthogonal sur une 
# droite, coordonnées x et y
# Entree : paramètres a,b,c d'une droite
# Sortie : coordonnée xproj et yproj du 
# point projeté
# ----------------------------------------
def projection_droite(param, x, y):
    
    a = param[0]
    b = param[1]
    c = param[2]
    
    xv = -b 
    yv = a
    
    norm = math.sqrt(xv*xv+yv*yv)
    
    xb = 0
    yb = -c/b
    
    BH = ((x-xb)*xv+(y-yb)*yv)/norm
    
    xproj = xb + BH*xv/norm
    yproj = yb + BH*yv/norm   
    
    return xproj, yproj
    
# ----------------------------------------
# Fonction complète de projection
# Entree : segment, coordonnées x et y du 
# point
# Sortie : distance du point au segment et 
# coordonnées du projeté
# ----------------------------------------
def proj_segment(segment, x, y):
    
    param = cartesienne(segment)    
    
    a = param[0]
    b = param[1]
    c = param[2]

    distance = math.fabs(a*x+b*y+c)
    distance /= math.sqrt(a*a+b*b)
    
    # Récupération des coordonnées du projeté
    xproj, yproj =  projection_droite(param, x, y)
    
    # Test d'inclusion dans le segment

    x1 = segment[0]
    y1 = segment[1]
    x2 = segment[2]
    y2 = segment[3]    
    
    boolx1 = (xproj >= x1) and (xproj <= x2)    
    boolx2 = (xproj <= x1) and (xproj >= x2)
    boolx = boolx1 or boolx2
    
    booly1 = (yproj >= y1)&(yproj <= y2)    
    booly2 = (yproj <= y1)&(yproj >= y2)
    booly = booly1 or booly2
    
    bool_include = (boolx and booly)
    
     # Si le projeté est dans le segment
    if (bool_include):

        a = param[0]
        b = param[1]
        c = param[2]
    
        xv = -b 
        yv = a
        
        norm = math.sqrt(xv*xv+yv*yv)
    
        xb = 0
        yb = -c/b
    
        BH = ((x-xb)*xv+(y-yb)*yv)/norm
    
        xproj = xb + BH*xv/norm
        yproj = yb + BH*yv/norm   
            
        
        return distance, xproj, yproj
    
    else:
        distance1 = math.sqrt((x-x1)*(x-x1)+(y-y1)*(y-y1))
        distance2 = math.sqrt((x-x2)*(x-x2)+(y-y2)*(y-y2))
        
        if (distance1 <= distance2):
            return distance1, x1, y1
        else:
            return distance2, x2, y2
            
# ----------------------------------------
# Fonction complète de projection entre un
# point et une polyligne
# Entree : polyligne, coordonnées x et y du 
# point
# Sortie : distance du point ) la polyligne
# et coordonnées du projeté
# ----------------------------------------
def proj_polyligne(Xp, Yp, x, y):     
    
    distmin = 1e300
    
    for i in range(len(Xp)-1):
    
        x1 = Xp[i]
        y1 = Yp[i]
        x2 = Xp[i+1]
        y2 = Yp[i+1]

        dist, xp, yp = proj_segment([x1, y1, x2, y2], x, y)
        
        if dist < distmin:
            distmin = dist
            xproj = xp
            yproj = yp
            iproj = i
            
    return distmin, xproj, yproj, iproj



# --------------------------------------------------------------------------
# Function to compute area of triangle with cross product
# --------------------------------------------------------------------------
# Input : 
#   - x0, y0         ::     point 1 coordinates
#   - x1, y1         ::     point 2 coordinates
#    - x2, y2         ::     point 3 coordinates
# --------------------------------------------------------------------------
# Output : area of P1P2P3 in coordinate units
# --------------------------------------------------------------------------
def triangle_area(x0,y0,x1,y1,x2,y2):
    return 0.5*abs((x1-x0)*(y2-y1)-(x2-x1)*(y1-y0))
    
    
# --------------------------------------------------------------------------
# Function to compute distance between a point and a segment
# --------------------------------------------------------------------------
# Input : 
#   - x0, y0         ::     point coordinates
#   - x1, y1         ::     segment first point
#    - x2, y2         ::     segment second point
# --------------------------------------------------------------------------
# Output : distance between point and projection coordinates
# --------------------------------------------------------------------------
def distance_to_segment(x0, y0, x1, y1, x2, y2):

    # Segment length
    l = math.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))

    # Normalized scalar product
    psn = ((x0-x1)*(x2-x1) + (y0-y1)*(y2-y1))/l
    
    X = max(x1, x2)
    Y = max(y1, y2)
    
    x = min(x1, x2)
    y = min(y1, y2)
    
    xproj = x1 + psn/l*(x2-x1)
    yproj =    y1 + psn/l*(y2-y1)
    
    xproj = min(max(xproj, x), X)
    yproj = min(max(yproj, y), Y)
    
    # Compute distance
    d = math.sqrt((x0-xproj)*(x0-xproj)+(y0-yproj)*(y0-yproj))
    
    return d     



# =============================================================================
''' Pour calculer l'aire des triangles dans Visvalingam '''
def aire_visval(track, i):
    x0 = track.getObs(i-1).position.getX()
    y0 = track.getObs(i-1).position.getY()
    x1 = track.getObs(i).position.getX()
    y1 = track.getObs(i).position.getY()
    x2 = track.getObs(i+1).position.getX()
    y2 = track.getObs(i+1).position.getY()
    return triangle_area(x0,y0,x1,y1,x2,y2)


