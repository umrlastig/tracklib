# -*- coding: utf-8 -*-

"""
© Copyright Institut National de l'Information Géographique et Forestière (2020)
Contributors: 
    Yann Méneroux
    Marie-Dominique Van Damme
Creation date: 1th november 2020

tracklib library provides a variety of tools, operators and 
functions to manipulate GPS trajectories. It is a open source contribution 
of the LASTIG laboratory at the Institut National de l'Information 
Géographique et Forestière (the French National Mapping Agency).
See: https://tracklib.readthedocs.io
 
This software is governed by the CeCILL-C license under French law and
abiding by the rules of distribution of free software. You can  use, 
modify and/ or redistribute the software under the terms of the CeCILL-C
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info". 

As a counterpart to the access to the source code and rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability. 

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or 
data to be ensured and,  more generally, to use and operate it in the 
same conditions as regards security. 

The fact that you are presently reading this means that you have had
knowledge of the CeCILL-C license and that you accept its terms.

"""

# For type annotation
from __future__ import annotations   
from typing import Literal   
from tracklib.util.exceptions import *

from tracklib.core import Network

class NetworkWriter:
    """
    Write Network to CSV or KML files.
    """

    @staticmethod
    def writeToCsv(network:Network, path="", separator:str=",", h:Literal[0, 1]=1):
        """TODO"""

        if h == 1:
            output = "link_id" + separator
            output += "source" + separator
            output += "target" + separator
            output += "direction" + separator
            output += "wkt\n"
        else:
            output = ""

        for idedge in network.EDGES:
            edge = network.EDGES[idedge]
            output += edge.id + separator
            output += edge.source.id + separator
            output += edge.target.id + separator
            output += str(edge.orientation) + separator
            output += '"' + edge.geom.toWKT() + '"'
            output += "\n"

        if path:
            f = open(path, "w")
            f.write(output)
            f.close()

        return output
    
