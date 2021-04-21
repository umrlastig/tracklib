# -*- coding: utf-8 -*-

import json
import requests
from xml.dom import minidom

from tracklib.cartetopo.Troncon import Troncon

class IgnReader:
    
    NB_PER_PAGE = 1000;
    
    URL_SERVER = "https://wxs.ign.fr/choisirgeoportail/geoportail/wfs?"
    URL_SERVER += "service=WFS&version=2.0.0&request=GetFeature&"
    URL_SERVER += "typeName=BDTOPO_V3:troncon_de_route&"
    #URL_SERVER += "srsName=EPSG:2154&"
    URL_SERVER += "outputFormat=json&"
    #URL_SERVER += "BBOX=44.538617443499014,5.808794912294471,45.05505710140573,6.644301708889899"
    #URL_SERVER += "&count=3&startIndex=0"
    

    # ===========================
    # tolerance
    # ===========================
    @staticmethod
    def getNetwork(bbox, proj):
        
        TRONCONS = []
        
        nbRoute = IgnReader.__getNbRouteEmprise(bbox)
        nbiter = int(nbRoute / IgnReader.NB_PER_PAGE) + 1
        
        offset = 0
        for j in range(nbiter):
            URL_FEAT = IgnReader.URL_SERVER
            URL_FEAT += "BBOX=" + str(bbox[1]) + "," + str(bbox[0])  
            URL_FEAT += "," + str(bbox[3]) + "," + str(bbox[2])
            URL_FEAT += "&count=" + str(IgnReader.NB_PER_PAGE) 
            URL_FEAT += "&startIndex=" + str(offset)
            URL_FEAT += "&RESULTTYPE=results"
            # print (URL_FEAT)

            response = requests.get(URL_FEAT)
            data = json.loads(response.text)
            features = data['features']
            for feature in features:
                idd = feature['id']
                nature = feature['properties']['nature']
                sens = feature['properties']['sens_de_circulation']
                fictif = feature['properties']['fictif']
                pos = feature['properties']['position_par_rapport_au_sol']
                
                coords = feature['geometry']['coordinates']
                geom = ''
                if (feature['geometry']['type'] == 'LineString'):
                    #print (str(len(coords)))
                    geom = coords
                
                t = Troncon(idd, geom, nature, sens, fictif, pos)
                TRONCONS.append(t)
                
            offset = offset + IgnReader.NB_PER_PAGE
        
        return TRONCONS

    
    
    
    
    
    # --------------------------------------------------------------------------
    # Function to count road network features in bbox
    # --------------------------------------------------------------------------
    # Input : 
    #   - v: a float value
    # --------------------------------------------------------------------------
    # Output : number 
    # --------------------------------------------------------------------------
    @staticmethod
    def __getNbRouteEmprise(bbox):
        
        nb = 0
        
        URL_HITS = IgnReader.URL_SERVER 
        URL_HITS += "BBOX=" + str(bbox[1]) + "," + str(bbox[0])  
        URL_HITS += "," + str(bbox[3]) + "," + str(bbox[2])
        URL_HITS += "&resulttype=hits"
        
        res = requests.get(URL_HITS)
        # x = requests.get(url, proxies = { "https" : "https://1.1.0.1:80"})
        dom = minidom.parseString(res.text)
        result = dom.getElementsByTagName('wfs:FeatureCollection')
        
        nb = int(result[0].attributes['numberMatched'].value)
        
        return nb
        


if __name__ == '__main__':

    xmin = 6.06779213241985538
    xmax = 6.30425230208879839
    ymin = 44.915438233863199
    ymax = 44.99425829041950919
    proj = "EPSG:2154"
    
    TRONCONS = IgnReader.getNetwork((xmin, ymin, xmax, ymax), proj)
    print (len(TRONCONS))
    