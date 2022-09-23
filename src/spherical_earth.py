"""
Utility functions for the spherical Earth.

Functions:
   distance: compute the distance between two points
   meters_to_degrees: convert distances in meters to the corresponding differences in latitude and longitude
"""

import math

_EARTH_RADIUS = 6371000  # meters


def _hav(phi):
    """
    Haversine formula.

    :param phi: angle [rad]
    :return: the haversine value
    """
    return (math.sin(phi/2))**2


def distance(lat1, lon1, lat2, lon2):
    """Compute the distance between two points on the spherical Earth.

    :param lat1: latitude of the first point [degrees]
    :param lon1: longitude of the first point [degrees]
    :param lat2: latitude of the second point [degrees]
    :param lon2: longitude of the second point [degrees]
    :return: distance between the points [meters]
    """
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    h = _hav(lat2_rad - lat1_rad) + math.cos(lat1_rad) * math.cos(lat2_rad) * _hav(lon2_rad - lon1_rad)
    return 2 * _EARTH_RADIUS * math.asin(math.sqrt(h))


def meters_to_degrees(x, y, lat):
    """Convert distances in meters to the corresponding differences in latitude and longitude on the spherical Earth.

    :param x: distance along the meridian [m]
    :param y: distance along the parallel [m]
    :param lat: latitude of the mid point [degrees]
    :return: a tuple containing the difference in latitude and longitude [degrees]
    """
    d_lat = math.degrees(y / _EARTH_RADIUS)
    d_lon = math.degrees(x / (_EARTH_RADIUS * math.cos(math.radians(lat))))
    return d_lat, d_lon
