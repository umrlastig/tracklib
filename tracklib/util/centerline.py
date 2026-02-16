import sys
import fiona
import datetime
import progressbar
import numpy as np

from scipy.spatial import Voronoi

import shapely
from shapely.ops import unary_union
from shapely.geometry import mapping, shape
from shapely.geometry import LineString, Point


# =================================================================================================
# CLASS FOR COMPUTING CENTER LINES
# =================================================================================================
class Centerline(object):

    def __init__(self, inputGEOM, dist=0.5):
        self.inputGEOM = inputGEOM
        self.dist = abs(dist)

    def createCenterline(self):
        """
        Calculates the centerline of a polygon.

        Densifies the border of a polygon which is then represented by a Numpy
        array of points necessary for creating the Voronoi diagram. Once the
        diagram is created, the ridges located within the polygon are
        joined and returned.

        Returns:
            a union of lines that are located within the polygon.
        """

        minx = int(min(self.inputGEOM.envelope.exterior.xy[0]))
        miny = int(min(self.inputGEOM.envelope.exterior.xy[1]))

        print("\r\n*Upsampling polygon borders...")
        border = np.array(self.densifyBorder(self.inputGEOM, minx, miny))

        vor = Voronoi(border)
        vertex = vor.vertices

        print("\r\n*Computing polygon skeleton...")
        lst_lines = []
        Nvor = len(list(vor.ridge_vertices))
        bar = progressbar.ProgressBar(max_value = Nvor)
        for j, ridge in enumerate(vor.ridge_vertices):
            bar.update(j)
            '''
            if -1 not in ridge:
                line = LineString([
                    (vertex[ridge[0]][0] + minx, vertex[ridge[0]][1] + miny),
                    (vertex[ridge[1]][0] + minx, vertex[ridge[1]][1] + miny)])

                if line.within(self.inputGEOM) and len(line.coords[0]) > 1:
                    lst_lines.append(line)
            '''

            if -1 not in ridge:
                line = LineString([
                    (vertex[ridge[0]][0] + minx, vertex[ridge[0]][1] + miny),
                    (vertex[ridge[1]][0] + minx, vertex[ridge[1]][1] + miny)])
                if len(line.coords[0]) > 1:
                    lst_lines.append(line)
        
        bar.finish()
            
        print("\r\n*Filtering skeleton to form center line")            
        lst_lines_out = []
        bar = progressbar.ProgressBar(max_value = len(lst_lines))
        for i in range(len(lst_lines)):
            bar.update(i)
            if (shapely.contains(self.inputGEOM, lst_lines[i])):
                lst_lines_out.append(lst_lines[i])                   
        bar.finish()
        
        return unary_union(lst_lines_out)

    def densifyBorder(self, polygon, minx, miny):
        """
        Densifies the border of a polygon by a given factor (by default: 5).

        The function tests the complexity of the polygons geometry, i.e. does
        the polygon have holes or not. If the polygon doesn't have any holes,
        its exterior is extracted and densified by a given factor. If the
        polygon has holes, the boundary of each hole as well as its exterior is
        extracted and densified by a given factor.

        Returns:
            a list of points where each point is represented by a list of its
            reduced coordinates.

        Example:
            [[X1, Y1], [X2, Y2], ..., [Xn, Yn]
        """

        if len(polygon.interiors) == 0:
            exterIN = LineString(polygon.exterior)
            points = self.fixedInterpolation(exterIN, minx, miny, verbose=True)

        else:
            exterIN = LineString(polygon.exterior)
            points = self.fixedInterpolation(exterIN, minx, miny, verbose=True)

            for j in range(len(polygon.interiors)):
                interIN = LineString(polygon.interiors[j])
                points += self.fixedInterpolation(interIN, minx, miny)

        return points

    def fixedInterpolation(self, line, minx, miny, verbose=False):
        """
        A helping function which is used in densifying the border of a polygon.

        It places points on the border at the specified distance. By default the
        distance is 5 (meters) which means that the first point will be placed
        5 m from the starting point, the second point will be placed at the
        distance of 1.0 m from the first point, etc. Naturally, the loop breaks
        when the summarized distance exceeds the length of the line.

        Returns:
            a list of points where each point is represented by a list of its
            reduced coordinates.

        Example:
            [[X1, Y1], [X2, Y2], ..., [Xn, Yn]
        """

        count = self.dist
        newline = []

        startpoint = [line.xy[0][0] - minx, line.xy[1][0] - miny]
        endpoint = [line.xy[0][-1] - minx, line.xy[1][-1] - miny]
        newline.append(startpoint)

        if (verbose):
            bar = progressbar.ProgressBar(max_value=int(line.length)+1)

        while count < line.length:
            point = line.interpolate(count)
            newline.append([point.x - minx, point.y - miny])
            if (verbose):
                bar.update(int(count))
            count += self.dist
        newline.append(endpoint)
       
        if (verbose):
            bar.finish()

        return newline


# =================================================================================================
# MAIN CLASS FOR EXECUTING CENTER LINE COMPUTATION ON A SHAPE FILE
# =================================================================================================
class Shp2centerline(object):

    def __init__(self, inputSHP, outputSHP, dist):
        self.inshp = inputSHP
        self.outshp = outputSHP
        self.dist = abs(dist)
        self.dct_polygons = {}
        self.dct_centerlines = {}

        # ------------------------------------------------------------------------
        # Load polygon from input file
        # ------------------------------------------------------------------------
        print('*Importing polygons from: [' + self.inshp + ']... ', end='')
        self.importSHP()
        print("done\r\n")
        
        # ------------------------------------------------------------------------
        # Computing center line
        # ------------------------------------------------------------------------    
        print('*Center line computation')
        self.run()
        
        # ------------------------------------------------------------------------
        # Output center line
        # ------------------------------------------------------------------------  
        print('\r\n*Exporting center line to: [' + self.outshp+ ']... ', end='')
        self.export2SHP()
        print("done")

    def run(self):
        """
        Starts processing the imported SHP file.
        It sedns the polygon's geometry allong with the interpolation distance
        to the Centerline class to create a Centerline object.
        The results (the polygon's ID and the geometry of the centerline) are
        added to the dictionary.
        """

        for key in self.dct_polygons.keys():
            poly_geom = self.dct_polygons[key]
            centerlineObj = Centerline(poly_geom, self.dist)

            self.dct_centerlines[key] = centerlineObj.createCenterline()

    def importSHP(self):
        """
        Imports the Shapefile into a dictionary. Shapefile needs to have an ID
        column with unique values.

        Returns:
            a dictionary where the ID is the key, and the value is a polygon
            geometry.
        """

        with fiona.open(self.inshp, 'r', encoding='UTF-8') as fileIN:
            for polygon in fileIN:
                polygonID = polygon['properties'][u'id']
                geom = shape(polygon['geometry'])

                self.dct_polygons[polygonID] = geom

    def export2SHP(self):
        """
        Creates a Shapefile and fills it with centerlines and their IDs.

        The dictionary contains the IDs of the centerlines (keys) and their
        geometries (values). The ID of a centerline is the same as the ID of
        the polygon it represents.
        """

        newschema = {'geometry': 'MultiLineString',
                     'id': 'int',
                     'properties': {'id': 'int'}}

        with fiona.open(self.outshp, 'w', encoding='UTF-8',
                        schema=newschema, driver='ESRI Shapefile') as SHPfile:

            for i, key in enumerate(self.dct_centerlines):
                geom = self.dct_centerlines[key]
                newline = {}

                newline['id'] = key
                newline['geometry'] = mapping(geom)
                newline['properties'] = {'id': key}

                SHPfile.write(newline)




# =================================================================================================
# MAIN SCRIPT
# =================================================================================================
if __name__ == "__main__":
	
    main_text   = "----------------------------------------------------------------------\r\n"
    main_text  += "CENTER LINE COMPUTATION ON A POLYGON                                  \r\n"
    main_text  += "----------------------------------------------------------------------\r\n"
    print(main_text, end='')
    
    usage_text  = "Usage: python centeline <in> <out> <interp>                           \r\n"
    usage_text += "----------------------------------------------------------------------\r\n"
    usage_text += "Inputs:                                                               \r\n"
    usage_text += "      - <in>     : input shape file (.shp)                            \r\n" 
    usage_text += "      - <out>    : output shape file (.shp)     [def. <in>_ctl.shp]   \r\n"
    usage_text += "      - <interp> : interpolation distance (m)   [def. 5]              \r\n"
    usage_text += "----------------------------------------------------------------------\r\n"
    usage_text += "Output: shape file containing center line as a multi-linestring       \r\n" 
    usage_text += "----------------------------------------------------------------------\r\n"
	
    if (len(sys.argv) == 1):
        print(usage_text)
        sys.exit(0)
        
    if (sys.argv[-1] in ("-h", "-help", "--h", "--help")):
        print(usage_text)
        sys.exit(0)
        
    input_file  = sys.argv[1]
    output_file = input_file.split(".")[0] + "_ctl.shp"
    interp_dist = 25
    
    
    if (len(sys.argv) > 2):
        output_file = sys.argv[2]
    if (len(sys.argv) > 3):
        interp_dist = float(sys.argv[3])
      
    confirm_text  = "INPUT FILE            :  " +       input_file + "\r\n"  
    confirm_text += "OUTPUT FILE           :  " +      output_file + "\r\n"  
    confirm_text += "INTERPOLATION DISTANCE:  " + str(interp_dist) + " m\r\n"  
    confirm_text += "----------------------------------------------------------------------\r\n"
    print(confirm_text, end='')
    
    t1 = datetime.datetime.now().timestamp()

    Shp2centerline(input_file, output_file, interp_dist)
    
    dt = datetime.datetime.now().timestamp()-t1
    end_text   = "----------------------------------------------------------------------\r\n"
    end_text  += "COMPUTATION DONE          "                                                      
    end_text  += "[Elapased time: " + str(round(dt, 3)) + " sec]                        \r\n"
    end_text  += "----------------------------------------------------------------------\r\n"
    print(end_text)
