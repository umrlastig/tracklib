"""Read network files"""

import csv
import json
import os.path
import progressbar
import requests
from xml.dom import minidom

from tracklib.core import ObsTime, ENUCoords, ECEFCoords, GeoCoords, Obs
from tracklib.core.Track import Track
from tracklib.core.Network import Network, Node, Edge
from tracklib.core.SpatialIndex import SpatialIndex
from tracklib.core.Bbox import Bbox
from tracklib.io.NetworkFormat import NetworkFormat
import tracklib.algo.Cinematics as Cinematics


class NetworkReader:
    """
    This class offers static methods to load network from file or from a wfs service.
    """

    @staticmethod
    def readFromFile(path:str, formatfile:str="DEFAULT", verbose=True)->Network:
        """
        Read a network from CSV file with geometry structured in coordinates.
        
        Before to load network data, you need to have a format defined
        in **network_file_format** (in tracklib/resources directory) which 
        describes metadata of the file. If it doesn't exists, you need to create one format.
        
        For example, let's define a format call 'VTT' in the file *network_file_format*
        which corresponds to a network associated with mountain bike tracks.
        So, you add a new line like this:
        
            *VTT, 1, 2, 3, 0, -1, 4, c, 1, True, UTF-8, GEO*
        
        where:
            - the first value 'VTT' represents the format name, 
            - the second value '1' represents the index of column containing edge identifier in the CSV file
            - the third value '2' represents index of column containing source node identifier in the CSV file
            - the fourth value '3' represents index of column containing target node identifier in the CSV file
            - the fifth value '0' represents index of column containing geometry of edge in wkt format in the CSV file. You can specify also optional parameters:
            - a path cost (arbitrarily set to be proportional to the length of the WKT if unlined (-1))
            - an orientation index. An integer arbitrarily set to: 0 to indicate two-way, 1 direct way and -1 indirect way
            - the separating characters (can be multiple characters). Can be: c (comma), b (blankspace), s (semi-column)
            - the number of heading line in format 
            - true to manage double quote
            - the encoding like utf-8
            - srid: coordinate system of points (ENU, Geo or ECEF) 
        
        Parameters
        -----------
        
        :param path: file or directory
        :param formatfile: name of format which describes metadata of the file
        :return: network.
        
        """
        
        if not os.path.isfile(path):
            print ('Error: file not exists')
            return None

        network = Network()
        fmt = NetworkFormat(formatfile)

        num_lines = sum(1 for line in open(path))

        if verbose:
            print("Loading network...")

        with open(path, encoding="utf-8") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=fmt.separator, doublequote=True)

            # Header
            cpt = 0
            for row in spamreader:
                cpt += 1
                if cpt >= fmt.h:
                    break

            if verbose:
                spamreader = progressbar.progressbar(spamreader, max_value=num_lines)

            for row in spamreader:
                (edge, noeudIni, noeudFin) = readLineAndAddToNetwork(row, fmt)
                network.addEdge(edge, noeudIni, noeudFin)

        csvfile.close()

        # Return network loaded
        return network
    
    
    counter = 0

    NB_PER_PAGE = 1000

    URL_SERVER = "https://wxs.ign.fr/choisirgeoportail/geoportail/wfs?"
    URL_SERVER += "service=WFS&version=2.0.0&request=GetFeature&"
    URL_SERVER += "typeName=BDTOPO_V3:troncon_de_route&"
    # URL_SERVER += "srsName=EPSG:2154&"
    URL_SERVER += "outputFormat=json&"
    # URL_SERVER += "BBOX=44.538617443499014,5.808794912294471,45.05505710140573,6.644301708889899"
    # URL_SERVER += "&count=3&startIndex=0"
    
    

    resource_path = os.path.join(os.path.split(__file__)[0], "../..")
    PROXY_FILE_FORMAT = os.path.join(resource_path, "resources/proxy")

    # self.id = id
    # self.coords = coords
    # self.nature = nature
    # self.sens = sens
    # self.fictif = fictif
    # self.pos = pos

    # ===========================
    # tolerance
    # ===========================
    @staticmethod
    def requestFromIgnGeoportail(
        bbox:Bbox, proj=None, margin=0.0, tolerance=0.1, spatialIndex=True, nomproxy=None
    ) -> Network:
        """
        
        Parameters
        -----------

        :param bbox: The bounding box of the selected area (The bounding box must
            be expressed in WGS84).
        :param proj: projection of results, optional. Only 'EPSG:4326' is implemented
        :param margin: f
        :param tolerance: parameter specifies the maximum distance accepted for merging two nodes (edge ends)
        :param nomproxy: name of proxy which describes parameter connexion defined in the tracklib/resources/proxy file
        """

        xmin = bbox.getXmin()
        xmax = bbox.getXmax()
        ymin = bbox.getYmin()
        ymax = bbox.getYmax()
        dx = (xmax - xmin) / 2
        dy = (ymax - ymin) / 2
        
        # Adding margin
        emprise = (
            xmin - margin * dx,
            xmax + margin * dx,
            ymin - margin * dy,
            ymax + margin * dy,
        )

        network = Network()

        cptNode = 0

        if proj == None:
            proj = "EPSG:4326"

        fmt = NetworkFormat()
        fmt.createFromDict(
            {
                "name": "WFS",
                "pos_edge_id": 0,
                "pos_source": 5,
                "pos_target": 6,
                "pos_wkt": 1,
                "pos_poids": 3,
                "pos_sens": 4,
                "srid": "GEO",
            }
        )

        # PROXY
        proxyDict = {}
        if nomproxy != None:
            with open(NetworkReader.PROXY_FILE_FORMAT) as ffmt:
                line = ffmt.readline().strip()
                while line:
                    if line[0] == "#":
                        line = ffmt.readline().strip()
                        continue
                    tab = line.split(",")
                    if tab[0].strip() == nomproxy:
                        FIELDS = tab
                        proxyDict[FIELDS[1].lower()] = FIELDS[2]
                    line = ffmt.readline().strip()
            ffmt.close()

        nbRoute = NetworkReader.__getNbRouteEmprise(emprise, proxyDict)
        
        if nbRoute == 0:
            return None
        
        nbiter = int(nbRoute / NetworkReader.NB_PER_PAGE) + 1

        offset = 0
        for j in range(nbiter):
            print("PAGE " + str(j + 1) + "/" + str(nbiter))
            URL_FEAT = NetworkReader.URL_SERVER
            URL_FEAT += "BBOX=" + str(emprise[2]) + "," + str(emprise[0])
            URL_FEAT += "," + str(emprise[3]) + "," + str(emprise[1])
            URL_FEAT += "&count=" + str(NetworkReader.NB_PER_PAGE)
            URL_FEAT += "&startIndex=" + str(offset)
            URL_FEAT += "&RESULTTYPE=results"
            URL_FEAT += "&srsname=" + proj
            # print (URL_FEAT)

            response = requests.get(URL_FEAT, proxies=proxyDict)
            data = json.loads(response.text)
            features = data["features"]

            for feature in progressbar.progressbar(features):

                row = []

                idd = feature["id"]
                # nature = feature['properties']['nature']
                fictif = feature["properties"]["fictif"]
                if fictif == "True":
                    continue
                row.append(idd)

                # TODO
                # pos = feature['properties']['position_par_rapport_au_sol']

                TAB_OBS = []
                coords = feature["geometry"]["coordinates"]
                if feature["geometry"]["type"] == "LineString":
                    # print (str(len(coords)))
                    # geom = coords
                    # print (coords)

                    typeCoord = "GEOCOORDS"
                    if proj == "EPSG:2154":
                        typeCoord = "ENUCoords"
                    TAB_OBS = tabCoordsLineStringToObs(coords, typeCoord)

                if len(TAB_OBS) < 2:
                    continue

                track = Track(TAB_OBS)
                row.append(track.toWKT())
                row.append("ENU")

                row.append(track.length())

                # Orientation
                sens = feature["properties"]["sens_de_circulation"]
                orientation = Edge.DOUBLE_SENS
                if sens == None or sens == "":
                    orientation = Edge.DOUBLE_SENS
                elif sens == "Double sens" or sens == "Sans objet":
                    orientation = Edge.DOUBLE_SENS
                elif sens == "Direct" or sens == "Sens direct":
                    orientation = Edge.SENS_DIRECT
                elif sens == "Indirect" or sens == "Sens inverse":
                    orientation = Edge.SENS_INVERSE
                else:
                    print(sens)
                row.append(orientation)

                # Source node
                idNoeudIni = str(cptNode)
                p1 = track.getFirstObs().position
                candidates = selectNodes(network, Node("0", p1), tolerance)
                if len(candidates) > 0:
                    c = candidates[0]
                    idNoeudIni = c.id
                else:
                    cptNode += 1

                # Target node
                idNoeudFin = str(cptNode)
                p2 = track.getLastObs().position
                candidates = selectNodes(network, Node("0", p2), tolerance)
                if len(candidates) > 0:
                    c = candidates[0]
                    idNoeudFin = c.id
                else:
                    cptNode += 1

                row.append(idNoeudIni)
                row.append(idNoeudFin)

                (edge, noeudIni, noeudFin) = readLineAndAddToNetwork(row, fmt)
                network.addEdge(edge, noeudIni, noeudFin)

            #
            offset = offset + NetworkReader.NB_PER_PAGE

        if spatialIndex:
            network.spatial_index = SpatialIndex(
                network, resolution=(dx / 1e3, dy / 1e3), margin=0.4
            )
            
            
        return network

    # --------------------------------------------------------------------------
    # Function to count road network features in bbox
    # --------------------------------------------------------------------------
    # Input :
    #   - v: a float value
    # --------------------------------------------------------------------------
    # Output : number
    # --------------------------------------------------------------------------
    @staticmethod
    def __getNbRouteEmprise(bbox, proxyDict):
        """TODO"""

        nb = 0

        URL_HITS = NetworkReader.URL_SERVER
        URL_HITS += "BBOX=" + str(bbox[2]) + "," + str(bbox[0])
        URL_HITS += "," + str(bbox[3]) + "," + str(bbox[1])
        URL_HITS += "&resulttype=hits"
        #print (URL_HITS)

        try:
            res = requests.get(URL_HITS, proxies=proxyDict)
            status = res.raise_for_status()
            print (status, type(status))
        except requests.exceptions.RequestException: 
            print("ERROR: Failed to establish connection")
            return 0
        
        # x = requests.get(url, proxies = { "https" : "https://1.1.0.1:80"})
        # print ('---------' + status, type(status))
        dom = minidom.parseString(res.text)
    
        result = dom.getElementsByTagName("wfs:FeatureCollection")
    
        nb = int(result[0].attributes["numberMatched"].value)
        return nb
        
        

        


def readLineAndAddToNetwork(row, fmt):
    """TODO"""
    edge_id = str(row[fmt.pos_edge_id])
    if fmt.pos_edge_id < 0:
        edge_id = NetworkReader.counter
    NetworkReader.counter = NetworkReader.counter + 1

    geom = str(row[fmt.pos_wkt])
    TAB_OBS = wktLineStringToObs(geom, fmt.srid.upper())

    # Au moins 2 points
    if len(TAB_OBS) < 2:
        return

    track = Track(TAB_OBS)
    Cinematics.computeAbsCurv(track)

    edge = Edge(edge_id, track)

    # Orientation
    orientation = int(row[fmt.pos_sens])
    if orientation not in [Edge.DOUBLE_SENS, Edge.SENS_DIRECT, Edge.SENS_INVERSE]:
        orientation = Edge.DOUBLE_SENS
    edge.orientation = orientation

    # Poids
    if fmt.pos_poids == -1:
        poids = track.length()
    else:
        poids = float(row[fmt.pos_poids])
    edge.weight = poids

    # Source node
    source = str(row[fmt.pos_source])
    noeudIni = Node(source, track.getFirstObs().position)

    # Target node
    target = str(row[fmt.pos_target])
    noeudFin = Node(target, track.getLastObs().position)

    # Return
    return (edge, noeudIni, noeudFin)
    # network.addEdge(edge, noeudIni, noeudFin)


def wktLineStringToObs(wkt, srid):
    """
    Une polyligne de n points est modélisée par une Track (timestamp = 1970/01/01 00 :00 :00)
        Cas LINESTRING()
    """

    # Creation d'une liste vide
    TAB_OBS = list()

    # Separation de la chaine
    coords_string = wkt.split("(")
    coords_string = coords_string[1]
    coords_string = coords_string.split(")")[0]

    coords = coords_string.split(",")

    for i in range(0, len(coords)):
        sl = coords[i].strip().split(" ")
        x = float(sl[0])
        y = float(sl[1])
        if len(sl) == 3:
            z = float(sl[2])
        else:
            z = 0.0

        if not srid.upper() in [
            "ENUCOORDS",
            "ENU",
            "GEOCOORDS",
            "GEO",
            "ECEFCOORDS",
            "ECEF",
        ]:
            print("Error: unknown coordinate type [" + str(srid) + "]")
            exit()

        if srid.upper() in ["ENUCOORDS", "ENU"]:
            point = ENUCoords(x, y, z)
        if srid.upper() in ["GEOCOORDS", "GEO"]:
            point = GeoCoords(x, y, z)
        if srid.upper() in ["ECEFCOORDS", "ECEF"]:
            point = ECEFCoords(x, y, z)

        TAB_OBS.append(Obs(point, ObsTime()))

    return TAB_OBS

def selectNodes(network, node, distance):
    """Selection des autres noeuds dans le cercle dont node.coord est le centre,
    de rayon distance

    :param node: le centre du cercle de recherche.
    :param distance: le rayon du cercle de recherche.

    :return: tableau de NODES liste des noeuds dans le cercle
    """
    NODES = []

    if network.spatial_index is None:
        for key in network.getIndexNodes():
            n = network.NODES[key]
            if n.coord.distance2DTo(node.coord) <= distance:
                NODES.append(n)
    else:
        vicinity_edges = network.spatial_index.neighborhood(node.coord, unit=1)
        for e in vicinity_edges:
            source = network.EDGES[network.getEdgeId(e)].source
            target = network.EDGES[network.getEdgeId(e)].target
            if source.coord.distance2DTo(node.coord) <= distance:
                NODES.append(source)
            if target.coord.distance2DTo(node.coord) <= distance:
                NODES.append(target)

    return NODES


def tabCoordsLineStringToObs(coords, srid):
    """TODO"""

    # Creation d'une liste vide
    TAB_OBS = list()

    for i in range(0, len(coords)):
        sl = coords[i]
        x = float(sl[0])
        y = float(sl[1])
        if len(sl) == 3:
            z = float(sl[2])
        else:
            z = 0.0

        if not srid.upper() in [
            "ENUCOORDS",
            "ENU",
            "GEOCOORDS",
            "GEO",
            "ECEFCOORDS",
            "ECEF",
        ]:
            print("Error: unknown coordinate type [" + str(srid) + "]")
            exit()

        if srid.upper() in ["ENUCOORDS", "ENU"]:
            point = ENUCoords(x, y, z)
        if srid.upper() in ["GEOCOORDS", "GEO"]:
            point = GeoCoords(x, y, z)
        if srid.upper() in ["ECEFCOORDS", "ECEF"]:
            point = ECEFCoords(x, y, z)

        TAB_OBS.append(Obs(point, ObsTime()))

    return TAB_OBS
