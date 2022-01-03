"""Write Networkfiles"""


class NetworkWriter:
    """TODO"""

    @staticmethod
    def writeToCsv(network, path="", separator=",", h=1):
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
