:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 07/03/2021


Core concept
============

The concept mostly important in tracklib is, as its name suggest, a :py:class:`tracklib.Track`. But to have a quick overview
of the different structures that exist in tracklib, we've put together a glossary of its terms. 


.. glossary::

    Track
        A track is a GPS track or something that can be represented as a sequence of ``Obs``
    
    GeoCoords, ENUCoords, ECEFCoords
        A structure that labels point coordinates. :py:class:`GeoCoords` : for representation 
        og geographic coordinates (lon, lat, alti). :py:`ENUCoords` : for local projection (East, North, Up)
        and :py:`ECEFCoords` : for Earth-Centered-Earth-Fixed coordinates (X, Y, Z)
    
    ObsTime
        Represents the time instant of an phenomenom observation
        
    Observation
        observation in a GPS track. Points are referenced in geodetic coordinates
        
    TrackCollection
        A collection of tracks
    
    Bbox
        Represents a boundary box



