"""
Creation of tiles-based maps.

Variables:
    errors: list containing the errors detected in this module

Functions:
    configure: configure the limit for the tile caching

Classes:
    WebMercator: manages the transformation to and from the WebMercator projection
    HutMap: a map centered on a hut
    NavigableMap: a navigable map displaying huts information
"""
from itertools import product
from collections import OrderedDict
import pathlib
import os
import math

from PIL import Image, ImageDraw, ImageFont
from src.spherical_earth import distance, meters_to_degrees
from src import config
from src.config import ASSETS_PATH_TILES, ASSETS_PATH_ICONS, ASSETS_PATH_FONTS
from src.model import HutStatus

errors = []

_TILE_FILENAME = str(ASSETS_PATH_TILES / '{0}/{1}/{2}.png')
_TILE_SIZE = 256
_EMPTY_TILE_COLOR = (220, 220, 220, 0)
_EMPTY_TILE_BORDER_COLOR = (0, 0, 0)

_HUT_ICON_FILENAME = str(ASSETS_PATH_ICONS / "icon_{0}.png")
_HUT_ICON_SIZE = (25, 25)
_HUT_ICON_BACKUP_SIZE = (19, 19)

_PIN_FILENAME = str(ASSETS_PATH_ICONS / "pin.png")
_PIN_SIZE = (51, 51)
_PIN_BACKUP_SIZE = (3, 3)
_PIN_BACKUP_COLOUR = (0, 0, 0)

_PLUS_FILENAME = str(ASSETS_PATH_ICONS / "plus.png")
_PLUS_SIZE = (32, 32)
_PLUS_BACKUP_SIZE = (28, 28)
_PLUS_BACKUP_COLOUR = (128, 128, 128)
_PLUS_BACKUP_SYMBOL = '+'
_MINUS_FILENAME = str(ASSETS_PATH_ICONS / "minus.png")
_MINUS_SIZE = (32, 32)
_MINUS_BACKUP_SIZE = (28, 28)
_MINUS_BACKUP_COLOUR = (128, 128, 128)
_MINUS_BACKUP_SYMBOL = '-'
_ZOOM_FILENAME = str(ASSETS_PATH_ICONS / "zoom.png")
_ZOOM_SIZE = (32, 32)
_ZOOM_BACKUP_SIZE = (28, 28)
_ZOOM_BACKUP_COLOUR = (128, 128, 128)
_ZOOM_TEXT_SIZE = 20
_ZOOM_TEXT_COLOUR = (255, 255, 255)

_FONT_FILENAME = str(ASSETS_PATH_FONTS / 'GidoleFont/Gidole-Regular.ttf')

# Load the font
try:
    _zoom_font = ImageFont.truetype(_FONT_FILENAME, size=_ZOOM_TEXT_SIZE)
except IOError as font_error:
    _zoom_font = ImageFont.load_default()
    errors.append({'type': type(font_error), 'message': str(font_error) + ": " + _FONT_FILENAME})


# Define the colors for the hut icons
_HUT_STATUS_COLOURS = {
    HutStatus.NO_REQUEST: 'darkgray',
    HutStatus.NO_RESPONSE: 'orange',
    HutStatus.CLOSED: 'lightgray',
    HutStatus.NOT_AVAILABLE: 'red',
    HutStatus.AVAILABLE: 'green',
    'group': 'white'
}

_HUT_STATUS_BACKUP_COLOURS = {
    HutStatus.NO_REQUEST: (127, 127, 127),
    HutStatus.NO_RESPONSE: (255, 127, 39),
    HutStatus.CLOSED: (195, 195, 195),
    HutStatus.NOT_AVAILABLE: (255, 0, 0),
    HutStatus.AVAILABLE: (34, 177, 76),
    'group': (250, 250, 250)
}


def _load_icon(filename, size, backup_size, backup_colour,
               backup_symbol=None, backup_font=None, backup_text_color=None):
    """Load an icon image from a file. If an error occurs, create an image using the backup information.

    :param filename: name of the image file to be loaded
    :param size: size in pixel of the desired image (tuple of two values)
    :param backup_size: size in pixel of the image created as backup (tuple of two values)
    :param backup_colour: background colour of the image created as backup (tuple of three RGB values)
    :param backup_symbol: character to be displayed on the image created as backup
    :param backup_font: font used for the character on the image created as backup
    :param backup_text_color: color used for the character on the image created as backup (tuple of three RGB values)
    :return: a PIL image to be used as icon
    """
    try:
        icon = Image.open(filename)
        icon.thumbnail(size, resample=Image.NEAREST)
        pixels = icon.load()
        # Makes all white pixel transparent
        for i in range(icon.size[0]):
            for j in range(icon.size[1]):
                pixel = pixels[i, j]
                if pixel[0:3] == (255, 255, 255):
                    pixels[i, j] = (255, 255, 255, 0)
    except IOError as e:
        icon = Image.new('RGBA', size, (255, 255, 255, 0))
        icon.paste(Image.new('RGBA', backup_size, backup_colour), box=((size[0] - backup_size[0]) // 2,
                                                                       (size[1] - backup_size[1]) // 2))
        errors.append({'type': type(e), 'message': str(e)})
        if backup_symbol is not None:
            text = backup_symbol
            draw = ImageDraw.Draw(icon, 'RGBA')
            tw, th = draw.textsize(text, font=backup_font)
            text_position = (size[0] - tw) // 2, (size[1] - th) // 2 + 1
            draw.text(text_position, text,
                      fill=backup_text_color, font=backup_font)
    return icon


# Load the icons for the huts and the other symbols
_hut_icons = {}
for _hut_status, _colour in _HUT_STATUS_COLOURS.items():
    _hut_icon_filename = _HUT_ICON_FILENAME.format(_colour)
    _hut_icon = _load_icon(_hut_icon_filename, _HUT_ICON_SIZE,
                           _HUT_ICON_BACKUP_SIZE, _HUT_STATUS_BACKUP_COLOURS[_hut_status])
    _hut_icons[_hut_status] = _hut_icon

_pin_icon = _load_icon(_PIN_FILENAME, _PIN_SIZE, _PIN_BACKUP_SIZE, _PIN_BACKUP_COLOUR)

_plus_icon = _load_icon(_PLUS_FILENAME, _PLUS_SIZE, _PLUS_BACKUP_SIZE, _PLUS_BACKUP_COLOUR,
                        _PLUS_BACKUP_SYMBOL, _zoom_font, _ZOOM_TEXT_COLOUR)
_minus_icon = _load_icon(_MINUS_FILENAME, _MINUS_SIZE, _MINUS_BACKUP_SIZE, _MINUS_BACKUP_COLOUR,
                         _MINUS_BACKUP_SYMBOL, _zoom_font, _ZOOM_TEXT_COLOUR)
_zoom_icon = _load_icon(_ZOOM_FILENAME, _ZOOM_SIZE, _ZOOM_BACKUP_SIZE, _ZOOM_BACKUP_COLOUR)


def configure():
    """Configure the limit for the tile caching."""
    _TilesCluster.configure_cache()


class WebMercator:
    """
    Class that manages the conversions to and from a WebMercator projection.

    All methods are static.

    Methods:
        deg_2_tile: compute the webmercator tile number from latitude/longitude
        tile_2_deg: compute latitude/longitude (left/up corner) of a webmercator tile
        pixel_2_tile: compute the webmercator tile number from the webmercator pixel coordinates
        tile_2_pixel: compute the webmercator pixel coordinates (left/up corner) of a webmercator tile number
        deg_2_pixel: compute the webmercator pixel coordinates from latitude/longitude
        pixel_2_deg: compute latitude/longitude from the webmercator pixel coordinates
    """

    @staticmethod
    def deg_2_tile(lat_deg, lon_deg, zoom):
        """Compute the webmercator tile number from latitude/longitude.

        :param lat_deg: latitude [degrees]
        :param lon_deg: longitude [degrees]
        :param zoom: zoom level
        :return: tuple of webmercator tile number (x, y)
        """
        x_web, y_web = WebMercator._deg_2_webmercator(lat_deg, lon_deg, zoom)
        x_tile = int(x_web)
        y_tile = int(y_web)
        return x_tile, y_tile

    @staticmethod
    def tile_2_deg(x_tile, y_tile, zoom):
        """Compute latitude/longitude (left/up corner) of a webmercator tile.

        :param x_tile: webmercator tile number x
        :param y_tile: webmercator tile number y
        :param zoom: zoom level
        :return: tuple of (latitude, longitude) [degrees]
        """
        x_web, y_web = x_tile, y_tile
        lat_deg, lon_deg = WebMercator._webmercator_2_deg(x_web, y_web, zoom)
        return lat_deg, lon_deg

    @staticmethod
    def pixel_2_tile(x_pixel, y_pixel):
        """Compute the webmercator tile number from the webmercator pixel coordinates.

        :param x_pixel: webmercator pixel coordinate x
        :param y_pixel: webmercator pixel coordinate y
        :return: tuple of webmercator tile number (x, y)
        """
        x_tile = x_pixel // _TILE_SIZE
        y_tile = y_pixel // _TILE_SIZE
        return x_tile, y_tile

    @staticmethod
    def tile_2_pixel(x_tile, y_tile):
        """Compute the webmercator pixel coordinates (left/up corner) of a webmercator tile number.

        :param x_tile: webmercator tile number x
        :param y_tile: webmercator tile number y
        :return: tuple of webmercator pixel coordinates (x, y)
        """
        x_pixel = x_tile * _TILE_SIZE
        y_pixel = y_tile * _TILE_SIZE
        return x_pixel, y_pixel

    @staticmethod
    def deg_2_pixel(lat_deg, lon_deg, zoom):
        """Compute the webmercator pixel coordinates from latitude/longitude.

        :param lat_deg: latitude [degrees]
        :param lon_deg: longitude [degrees]
        :param zoom: zoom level
        :return: tuple of webmercator pixel coordinates (x, y)
        """
        x_web, y_web = WebMercator._deg_2_webmercator(lat_deg, lon_deg, zoom)
        x_pixel = int(x_web * _TILE_SIZE)
        y_pixel = int(y_web * _TILE_SIZE)
        return x_pixel, y_pixel

    @staticmethod
    def pixel_2_deg(x_pixel, y_pixel, zoom):
        """Compute latitude/longitude from the webmercator pixel coordinates.

        :param x_pixel: webmercator pixel coordinate x
        :param y_pixel: webmercator pixel coordinate y
        :param zoom: zoom level
        :return: tuple of (latitude, longitude) [degrees]
        """
        x_web, y_web = x_pixel / _TILE_SIZE, y_pixel / _TILE_SIZE
        lat_deg, lon_deg = WebMercator._webmercator_2_deg(x_web, y_web, zoom)
        return lat_deg, lon_deg

    @staticmethod
    def _deg_2_webmercator(lat_deg, lon_deg, zoom):
        """Convert from latitude/longitude to webmercator coordinates.

        :param lat_deg: latitude [degrees]
        :param lon_deg: longitude [degrees]
        :param zoom: zoom level
        :return: tuple of webmercator coordinates (x, y)
        """
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        x_web = (lon_deg + 180.0) / 360.0 * n
        y_web = (1.0 - math.log(math.tan(lat_rad) + (1.0 / math.cos(lat_rad))) / math.pi) / 2.0 * n
        return x_web, y_web

    @staticmethod
    def _webmercator_2_deg(x_web, y_web, zoom):
        """Convert from webmercator coordinates to latitude/longitude.

        :param x_web: webmercator coordinate x
        :param y_web: webmercator coordinate y
        :param zoom: zoom level
        :return: tuple of (latitude, longitude) [degrees]
        """
        n = 2.0 ** zoom
        lon_deg = x_web / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1.0 - 2.0 * y_web / n)))
        lat_deg = math.degrees(lat_rad)
        return lat_deg, lon_deg


class _TilesCluster:
    """
    Class that manages a cluster of webmercator tiles.

    Methods:
        configure_cache: configure the limit for the tile caching
        check_available_tiles: check which zoom levels of tiles are available in the assets folder
        update_lat_lon: update the cluster geographical area, loading additional tiles if necessary
        get_image: return the image of the tile cluster cropped at the currently defined limits
        deg_2_pixel: convert latitude/longitude to pixel coordinates relative to the currently defined limits
        pixel_2_deg: convert pixel coordinates relative to the currently defined limits to latitude/longitude
        get_image_size: get the size of the image inside the currently defined limits
        delta_pixel_2_deg: convert a shift in pixel coordinates to the corresponding shift in latitude/longitude
    """
    _PIXEL_BORDER = 20
    _MIN_ZOOM = 6
    _COPYRIGHT_STRING = "© OpenStreetMap contributors"
    _COPYRIGHT_STRING_SIZE = 12
    _COPYRIGHT_BG_COLOUR = (224, 224, 224)
    _COPYRIGHT_STRING_COLOUR = (0, 0, 0)
    _TILES_STRING_SIZE = 16
    _TILES_STRING_COLOUR = (0, 0, 0)
    _BACKUP_MIN_ZOOM = 6
    _BACKUP_MAX_ZOOM = 9

    try:
        _copyright_font = ImageFont.truetype(_FONT_FILENAME, size=_COPYRIGHT_STRING_SIZE)
        _tiles_font = ImageFont.truetype(_FONT_FILENAME, size=_TILES_STRING_SIZE)
    except IOError as e:
        _copyright_font = ImageFont.load_default()
        _tiles_font = ImageFont.load_default()
        errors.append({'type': type(e), 'message': str(e) + ": " + _FONT_FILENAME})

    _cached_tiles = OrderedDict()
    _tiles_cache_limit = None
    _tiles_caching = False

    @classmethod
    def configure_cache(cls):
        """Configure the limit for the tile caching."""
        cls._tiles_cache_limit = config.TILES_CACHE
        if cls._tiles_cache_limit is not None and cls._tiles_cache_limit > 0:
            cls._tiles_caching = True
        else:
            cls._tiles_caching = False

    def __init__(self, lat_min, lat_max, lon_min, lon_max, zoom,
                 x_pixel_size=None, y_pixel_size=None,
                 size_type='exact'):
        """Create a cluster covering the specified geographical area; size in pixel can be optionally specified.

        :param lat_min: minimum latitude [degrees]
        :param lat_max: maximum latitude [degrees]
        :param lon_min: minimum longitude [degrees]
        :param lon_max: maximum longitude [degrees]
        :param zoom: zoom level
        :param x_pixel_size: width size in pixel
        :param y_pixel_size: height size in pixel
        :param size_type: 'exact' or 'min', defines if cluster size in pixel has to be exactly or at least as specified
        """

        self.zoom = zoom
        self._image = None
        self._x_pixel_crop_min = self._x_pixel_crop_max = self._y_pixel_crop_min = self._y_pixel_crop_max = None
        self._x_pixel_min = self._x_pixel_max = self._y_pixel_min = self._y_pixel_max = None

        self._load_cluster(lat_min, lat_max, lon_min, lon_max, x_pixel_size, y_pixel_size)
        self._update_limits(lat_min, lat_max, lon_min, lon_max, x_pixel_size, y_pixel_size, size_type)

    @staticmethod
    def check_available_tiles():
        """Check which zoom levels of tiles are available in the assets folder.

        :return: tuple of minimum and maximum zoom
        """
        tiles_folders = []
        try:
            for folder in os.scandir(ASSETS_PATH_TILES):
                if folder.is_dir():
                    try:
                        tiles_folders.append(int(folder.name))
                    except ValueError:
                        pass
        except FileNotFoundError as e:
            errors.append({'type': type(e), 'message': str(e)})
            return _TilesCluster._BACKUP_MIN_ZOOM, _TilesCluster._BACKUP_MAX_ZOOM
        if not tiles_folders:
            return _TilesCluster._BACKUP_MIN_ZOOM, _TilesCluster._BACKUP_MAX_ZOOM
        tiles_folders.sort()
        return tiles_folders[0], tiles_folders[-1]

    def update_lat_lon(self, lat_min, lat_max, lon_min, lon_max,
                       x_pixel_size=None, y_pixel_size=None,
                       size_type='exact'):
        """
        Update the cluster geographical area, loading additional tiles if necessary;
        size in pixel can be optionally specified.

        :param lat_min: minimum latitude [degrees]
        :param lat_max: maximum latitude [degrees]
        :param lon_min: minimum longitude [degrees]
        :param lon_max: maximum longitude [degrees]
        :param x_pixel_size: width size in pixel
        :param y_pixel_size: height size in pixel
        :param size_type: 'exact' or 'min', defines if cluster size in pixel has to be exactly or at least as specified
        """
        # Compute the limits of the new geographical area in pixels
        self._update_limits(lat_min, lat_max, lon_min, lon_max, x_pixel_size, y_pixel_size, size_type)

        # If the computed limits in pixels exceed the limits of the current cluster, load the required tiles
        if (self._x_pixel_crop_min < 0 or self._y_pixel_crop_min < 0
                or self._x_pixel_crop_max > self._x_pixel_max - self._x_pixel_min
                or self._y_pixel_crop_max > self._y_pixel_max - self._y_pixel_min):
            self._load_cluster(lat_min, lat_max, lon_min, lon_max, x_pixel_size, y_pixel_size)
            self._update_limits(lat_min, lat_max, lon_min, lon_max, x_pixel_size, y_pixel_size, size_type)

    def get_image(self):
        """Return the image of the tile cluster cropped at the currently defined limits.

        :return: the cropped PIL image
        """
        cropped_image = self._image.crop((self._x_pixel_crop_min, self._y_pixel_crop_min,
                                          self._x_pixel_crop_max, self._y_pixel_crop_max))
        return cropped_image

    def get_image_size(self):
        """Get the size of the image inside the currently defined limits.

        :return: the size of the image inside the currently defined limits (x, y)
        """
        return self._x_pixel_crop_max - self._x_pixel_crop_min, self._y_pixel_crop_max - self._y_pixel_crop_min

    def deg_2_pixel(self, lat, lon):
        """Convert the specified latitude/longitude to pixel coordinates relative to the currently defined limits.

        :param lat: latitude [degrees]
        :param lon: longitude [degrees]
        :return: tuple of pixel coordinates (x, y)
        """
        raw_x_pixel, raw_y_pixel = self._raw_deg_2_pixel(lat, lon)
        x_pixel = raw_x_pixel - self._x_pixel_crop_min
        y_pixel = raw_y_pixel - self._y_pixel_crop_min
        return x_pixel, y_pixel

    def pixel_2_deg(self, x_pixel, y_pixel):
        """Convert the specified pixel coordinates relative to the currently defined limits to latitude/longitude.

        :param x_pixel: pixel coordinate x
        :param y_pixel: pixel coordinate y
        :return: tuple of coordinates (latitude, longitude) [degrees]
        """
        raw_x_pixel = x_pixel + self._x_pixel_crop_min
        raw_y_pixel = y_pixel + self._y_pixel_crop_min
        return self._raw_pixel_2_deg(raw_x_pixel, raw_y_pixel)

    def delta_pixel_2_deg(self, delta_x_pixel, delta_y_pixel):
        """
        Convert a shift in pixel coordinates to the corresponding shift in latitude/longitude.

        The algorithm uses the center of the currently defined limits as reference point;
        due to the distortion of distances typical of the webmercator projection, the results are approximate
        and they are more accurate when the shift is applied close to the reference point or at high zoom levels.

        :param delta_x_pixel: the x shift in pixel coordinates
        :param delta_y_pixel: the y shift in pixel coordinates
        :return: tuple of shift in coordinates (lat, lon) [degrees]
        """
        x_pixel_center = (self._x_pixel_crop_min + self._x_pixel_crop_max) // 2
        y_pixel_center = (self._y_pixel_crop_min + self._y_pixel_crop_max) // 2
        lat_center, lon_center = self._raw_pixel_2_deg(x_pixel_center, y_pixel_center)
        x_pixel_delta = x_pixel_center + delta_x_pixel
        y_pixel_delta = y_pixel_center + delta_y_pixel
        lat_delta, lon_delta = self._raw_pixel_2_deg(x_pixel_delta, y_pixel_delta)
        return lat_delta - lat_center, lon_delta - lon_center

    @staticmethod
    def add_copyright(image):
        """Add a copyright string to the image.

        :param image: the image to which the copyright string has to be added
        """
        draw = ImageDraw.Draw(image, 'RGBA')
        tw, th = draw.textsize(_TilesCluster._COPYRIGHT_STRING, font=_TilesCluster._copyright_font)
        size_x, size_y = image.size
        text_position = size_x - tw, size_y - th
        draw.rectangle((text_position, (size_x, size_y)), fill=_TilesCluster._COPYRIGHT_BG_COLOUR)
        draw.text(text_position, text=_TilesCluster._COPYRIGHT_STRING,
                  font=_TilesCluster._copyright_font,
                  fill=_TilesCluster._COPYRIGHT_STRING_COLOUR)

    def _update_limits(self, lat_min, lat_max, lon_min, lon_max,
                       x_pixel_size=None, y_pixel_size=None,
                       size_type='exact'):
        """Update the limits of the cluster geographical area; size in pixel can be optionally specified.

        :param lat_min: minimum latitude [degrees]
        :param lat_max: maximum latitude [degrees]
        :param lon_min: minimum longitude [degrees]
        :param lon_max: maximum longitude [degrees]
        :param x_pixel_size: width size in pixel
        :param y_pixel_size: height size in pixel
        :param size_type: 'exact' or 'min', defines if cluster size in pixel has to be exactly or at least as specified
        """
        x_pixel_crop_min, y_pixel_crop_min = self._raw_deg_2_pixel(lat_max, lon_min)
        x_pixel_crop_max, y_pixel_crop_max = self._raw_deg_2_pixel(lat_min, lon_max)

        x_pixel_crop_min -= _TilesCluster._PIXEL_BORDER
        x_pixel_crop_max += _TilesCluster._PIXEL_BORDER
        y_pixel_crop_min -= _TilesCluster._PIXEL_BORDER
        y_pixel_crop_max += _TilesCluster._PIXEL_BORDER

        delta_x_pixel = x_pixel_crop_max - x_pixel_crop_min
        delta_y_pixel = y_pixel_crop_max - y_pixel_crop_min

        if x_pixel_size is not None and ((size_type == 'min' and delta_x_pixel < x_pixel_size) or size_type == 'exact'):
            x_pixel_crop_min -= (x_pixel_size - delta_x_pixel) // 2
            x_pixel_crop_max = x_pixel_crop_min + x_pixel_size

        if y_pixel_size is not None and ((size_type == 'min' and delta_y_pixel < y_pixel_size) or size_type == 'exact'):
            y_pixel_crop_min -= (y_pixel_size - delta_y_pixel) // 2
            y_pixel_crop_max = y_pixel_crop_min + y_pixel_size

        self._x_pixel_crop_min = x_pixel_crop_min
        self._x_pixel_crop_max = x_pixel_crop_max
        self._y_pixel_crop_min = y_pixel_crop_min
        self._y_pixel_crop_max = y_pixel_crop_max

    def _load_cluster(self, lat_min, lat_max, lon_min, lon_max, min_x_pixel_size=None, min_y_pixel_size=None):
        """
        Load the tile images required to cover the specified geographical area;
        minimum size in pixel can be optionally specified.

        :param lat_min: minimum latitude [degrees]
        :param lat_max: maximum latitude [degrees]
        :param lon_min: minimum longitude [degrees]
        :param lon_max: maximum longitude [degrees]
        :param min_x_pixel_size: minimum width size in pixel
        :param min_y_pixel_size: minimum height size in pixel
        """
        # Compute the tile numbers required to cover the specified geographical area
        x_pixel_web_min, y_pixel_web_max = WebMercator.deg_2_pixel(lat_min, lon_min, self.zoom)
        x_pixel_web_max, y_pixel_web_min = WebMercator.deg_2_pixel(lat_max, lon_max, self.zoom)

        x_pixel_web_min -= _TilesCluster._PIXEL_BORDER
        x_pixel_web_max += _TilesCluster._PIXEL_BORDER
        y_pixel_web_min -= _TilesCluster._PIXEL_BORDER
        y_pixel_web_max += _TilesCluster._PIXEL_BORDER

        delta_x_pixel = x_pixel_web_max - x_pixel_web_min
        delta_y_pixel = y_pixel_web_max - y_pixel_web_min

        if min_x_pixel_size is not None and delta_x_pixel < min_x_pixel_size:
            x_pixel_web_min -= (min_x_pixel_size - delta_x_pixel) // 2
            x_pixel_web_max = x_pixel_web_min + min_x_pixel_size
        if min_y_pixel_size is not None and delta_y_pixel < min_y_pixel_size:
            y_pixel_web_min -= (min_y_pixel_size - delta_y_pixel) // 2
            y_pixel_web_max = y_pixel_web_min + min_y_pixel_size

        x_tile_min, y_tile_min = WebMercator.pixel_2_tile(x_pixel_web_min, y_pixel_web_min)
        x_tile_max, y_tile_max = WebMercator.pixel_2_tile(x_pixel_web_max, y_pixel_web_max)

        self._x_pixel_min, self._y_pixel_min = x_tile_min * _TILE_SIZE, y_tile_min * _TILE_SIZE
        self._x_pixel_max, self._y_pixel_max = (x_tile_max + 1) * _TILE_SIZE, (y_tile_max + 1) * _TILE_SIZE

        self._image = Image.new('RGB', (self._x_pixel_max - self._x_pixel_min, self._y_pixel_max - self._y_pixel_min))

        # Load the tile images as required (already loaded images might be cached) and paste them to the cluster image
        for x_tile, y_tile in product(range(x_tile_min, x_tile_max + 1), range(y_tile_min,  y_tile_max + 1)):
            if (self.zoom, x_tile, y_tile) not in _TilesCluster._cached_tiles:
                tile, _ = self._load_tile(x_tile, y_tile, self.zoom, _TilesCluster._MIN_ZOOM)
                if _TilesCluster._tiles_caching:
                    _TilesCluster._cached_tiles[self.zoom, x_tile, y_tile] = tile
            else:
                tile = _TilesCluster._cached_tiles[self.zoom, x_tile, y_tile]
            self._image.paste(tile, box=((x_tile - x_tile_min) * _TILE_SIZE, (y_tile - y_tile_min) * _TILE_SIZE))

        # Purge the cache if the number of cached tiles is beyond the limit
        if _TilesCluster._tiles_caching and len(_TilesCluster._cached_tiles) > _TilesCluster._tiles_cache_limit:
            for _ in range(_TilesCluster._tiles_cache_limit // 2):
                _TilesCluster._cached_tiles.popitem(last=False)

    def _raw_deg_2_pixel(self, lat, lon):
        """Convert the specified latitude/longitude to pixel coordinates relative to the full cluster image.

        :param lat: latitude [degrees]
        :param lon: longitude [degrees]
        :return: tuple of pixel coordinates (x, y)
        """
        x_pixel_web, y_pixel_web = WebMercator.deg_2_pixel(lat, lon, self.zoom)
        x_pixel = x_pixel_web - self._x_pixel_min
        y_pixel = y_pixel_web - self._y_pixel_min
        return x_pixel, y_pixel

    def _raw_pixel_2_deg(self, x_pixel, y_pixel):
        """Convert the specified pixel coordinates relative to the full cluster image to latitude/longitude.

        :param x_pixel: pixel coordinate x
        :param y_pixel: pixel coordinate y
        :return: tuple of coordinates (latitude, longitude) [degrees]
        """
        x_pixel_web = x_pixel + self._x_pixel_min
        y_pixel_web = y_pixel + self._y_pixel_min
        lat, lon = WebMercator.pixel_2_deg(x_pixel_web, y_pixel_web, self.zoom)
        return lat, lon

    @staticmethod
    def _create_empty_tile(x_tile, y_tile, zoom):
        """Create an empty tile (adding written information about the tile if debug is active)

        :param x_tile: x tile number
        :param y_tile: y tile number
        :param zoom: zoom level
        :return: the created empty tile
        """
        tile = Image.new('RGBA', (_TILE_SIZE, _TILE_SIZE), _EMPTY_TILE_COLOR)

        # If debug is active, adds a border and a text with tile information
        if __debug__:
            for i in (0, _TILE_SIZE - 1):
                for j in range(_TILE_SIZE):
                    tile.putpixel((i, j), _EMPTY_TILE_BORDER_COLOR)
                    tile.putpixel((j, i), _EMPTY_TILE_BORDER_COLOR)

            draw = ImageDraw.Draw(tile, 'RGBA')
            text = f'{zoom}_{x_tile}_{y_tile}'
            tw, th = draw.textsize(text, font=_TilesCluster._tiles_font)
            text_position = (_TILE_SIZE - tw) // 2, (_TILE_SIZE - th) // 2 + 1
            draw.text(text_position, text,
                      fill=_TilesCluster._TILES_STRING_COLOUR,
                      font=_TilesCluster._tiles_font)
            errors.append({'type': 'Missing tile', 'message': text})

        return tile

    @staticmethod
    def _load_tile(x_tile, y_tile, zoom, min_zoom=None):
        """
        Load a single tile image from its file or create an empty tile if the file is missing.

        Optionally, if a file is missing, look for the corresponding tile at a lower zoom level
        (down to the specified minimum).

        :param x_tile: x tile number
        :param y_tile: y tile number
        :param zoom: zoom_level
        :param min_zoom: minimum zoom level for the backup search (optional)
        :return: tuple with the ile as a PIL image and a boolean flag indicating if the tile is empty
        """
        if min_zoom is None:
            min_zoom = zoom
        tile = None
        filename = _TILE_FILENAME.format(zoom, x_tile, y_tile)

        if pathlib.Path(filename).is_file():
            try:
                tile = Image.open(filename)
            except IOError:
                tile = None

        # If file is missing, search iteratively for the tile at a lower zoom level and expand it opportunely
        # this is skipped if min_zoom is not specified as input or if debug is active
        if tile is None and min_zoom < zoom and not __debug__:
            tile_out, empty_tile = _TilesCluster._load_tile(x_tile // 2, y_tile // 2, zoom - 1, min_zoom)
            if tile_out is not None and not empty_tile:
                x_pixel_min = (x_tile % 2) * _TILE_SIZE / 2
                y_pixel_min = (y_tile % 2) * _TILE_SIZE / 2
                tile_out = tile_out.crop((x_pixel_min, y_pixel_min,
                                          x_pixel_min + _TILE_SIZE / 2, y_pixel_min + _TILE_SIZE / 2))
                tile = tile_out.resize((_TILE_SIZE, _TILE_SIZE), Image.ANTIALIAS)

        if tile is None:
            tile = _TilesCluster._create_empty_tile(x_tile, y_tile, zoom)
            empty_tile = True
        else:
            empty_tile = False

        return tile, empty_tile


class _GenericMap:
    """Base class for maps with a zoom widget.

    Methods:
        get_map_image: get the map image from the tiles cluster
        check_zoom: check if the provided position in pixel coordinates corresponds to the zoom widget
    """

    def __init__(self, default_zoom, min_zoom, max_zoom):
        """Initialize a new generic map with the specified zoom levels (can be overridden based on tiles availability).

        :param default_zoom: default zoom level
        :param min_zoom: minimum zoom level
        :param max_zoom: maximum zoom level
        """
        min_available_zoom, max_available_zoom = _TilesCluster.check_available_tiles()
        self._min_zoom = max(min_available_zoom, min_zoom)
        self._max_zoom = min(max_available_zoom, max_zoom)
        self._default_zoom = max(min(default_zoom, self._max_zoom), self._min_zoom)

        self._cluster = None
        self._plus_box = ((0, 0), (0, 0))
        self._minus_box = ((0, 0), (0, 0))

    def get_map_image(self):
        """
        Get the map image from the tiles cluster with the applicable widgets and a copyright string.

        :return: the map image
        """
        if self._cluster is not None:
            map_image = self._cluster.get_image()
            self._add_widgets(map_image)
            self._cluster.add_copyright(map_image)
            return map_image
        else:
            return None

    def check_zoom(self, x, y):
        """Check if the provided position in pixel coordinates corresponds to the zoom widget.

        :param x: x position in pixel coordinates
        :param y: y position in pixel coordinates
        :return: 1 if the position corresponds to "+" zoom, -1 if it corresponds to "-" zoom, 0 otherwise
        """
        if self._plus_box[0][0] < x < self._plus_box[1][0] and self._plus_box[0][1] < y < self._plus_box[1][1]:
            return 1
        elif self._minus_box[0][0] < x < self._minus_box[1][0] and self._minus_box[0][1] < y < self._minus_box[1][1]:
            return -1
        else:
            return 0

    def _add_widgets(self, image):
        """Adds the applicable widget to the map image; can be overridden by subclasses to provide additional widgets.

        :param image: the map image to which widgets have to be added
        """
        self._add_zoom_widget(image)

    @property
    def _zoom(self):
        """Get the current zoom level of the tiles cluster.

        :return: the current zoom level
        """
        if self._cluster is not None:
            return self._cluster.zoom
        else:
            return None

    def _add_zoom_widget(self, image):
        """Add a zoom widget to the image (+ and - symbols and zoom level indicator) and computes the widget position.

        :param image: the PIL image to which the zoom widget has to be added
        """
        image.paste(_plus_icon, (image.size[0] - _plus_icon.size[0], 0), _plus_icon)
        self._plus_box = ((image.size[0] - _plus_icon.size[0], 0), (image.size[0], _plus_icon.size[1]))

        zoom_image = Image.Image.copy(_zoom_icon)
        if self._cluster is not None:
            draw = ImageDraw.Draw(zoom_image, 'RGBA')
            text = str(self._zoom)
            tw, th = draw.textsize(text, font=_zoom_font)
            text_position = (zoom_image.size[0] - tw) // 2, (zoom_image.size[1] - th) // 2 - 1
            draw.text(text_position, text, fill=_ZOOM_TEXT_COLOUR, font=_zoom_font)
        image.paste(zoom_image, (image.size[0] - zoom_image.size[0], _plus_icon.size[1]), zoom_image)

        image.paste(_minus_icon, (image.size[0] - _minus_icon.size[0],
                                  _plus_icon.size[1] + zoom_image.size[1]), _minus_icon)
        self._minus_box = ((image.size[0] - _minus_icon.size[0], _plus_icon.size[1] + zoom_image.size[1]),
                           (image.size[0], _plus_icon.size[1] + zoom_image.size[1] + _minus_icon.size[1]))


class HutMap(_GenericMap):
    """Class defining a map centered on a hut with a hut symbol showing its status.

    Methods:
        get_map_image: get the map image from the tiles cluster with the hut symbol
        set_status: set the status of the hut
        update_zoom: update the zoom level
    """

    def __init__(self, lat_hut, lon_hut, width, height, default_zoom, min_zoom, max_zoom):
        """
        Create a new HutMap centered at the specified hut coordinates and with the specified width and height.

        :param lat_hut: latitude of the hut [degrees]
        :param lon_hut: longitude of the hut [degrees]
        :param width: width of the map at the reference zoom level [meters]
        :param height: height of the map at the reference zoom level [meters]
        :param default_zoom: reference zoom level
        :param min_zoom: minimum zoom level
        :param max_zoom: maximum zoom level
        """
        super().__init__(default_zoom, min_zoom, max_zoom)

        self._lat_hut = lat_hut
        self._lon_hut = lon_hut
        self._width = width
        self._height = height

        self._x_pixel_size = self._y_pixel_size = None

        self._load_cluster(self._default_zoom)

        if self._x_pixel_size is None:
            self._x_pixel_size, self._y_pixel_size = self._cluster.get_image_size()

        self._x_pixel_hut = self._x_pixel_size // 2
        self._y_pixel_hut = self._y_pixel_size // 2

        self._hut_status = None

    def set_status(self, status):
        """Set the status of the hut.

        :param status: a HutStatus enum defining the hut status
        """
        if status is None:
            self._hut_status = None
        else:
            self._hut_status = status

    def update_zoom(self, direction):
        """Update the current zoom level.

        :param direction: direction of the zoom level change
        """
        new_zoom = self._zoom + (1 if direction > 0 else -1 if direction < 0 else 0)
        if new_zoom < self._min_zoom:
            return
        if new_zoom > self._max_zoom:
            return
        self._load_cluster(new_zoom)

    def _add_widgets(self, image):
        """Adds the applicable widget to the map image.

        :param image: the image to which the widgets have to be added
        """
        if self._hut_status:
            offset = (self._x_pixel_hut - (_HUT_ICON_SIZE[0] - 1) // 2,
                      self._y_pixel_hut - (_HUT_ICON_SIZE[1] - 1) // 2)
            image.paste(_hut_icons[self._hut_status], offset, _hut_icons[self._hut_status])
        super()._add_widgets(image)

    def _load_cluster(self, zoom):
        """Load the cluster of tiles for the specified zoom level.

        :param zoom: the desired zoom level
        """
        factor = 2**(self._default_zoom - zoom)
        width_for_zoom = self._width * factor
        height_for_zoom = self._height * factor

        d_lat, d_lon = meters_to_degrees(width_for_zoom, height_for_zoom, self._lat_hut)

        lat_min, lon_min = self._lat_hut - d_lat / 2, self._lon_hut - d_lon / 2
        lat_max, lon_max = self._lat_hut + d_lat / 2, self._lon_hut + d_lon / 2

        self._cluster = _TilesCluster(lat_min, lat_max, lon_min, lon_max, zoom,
                                      self._x_pixel_size, self._y_pixel_size, 'exact')


class NavigableMap(_GenericMap):
    """Class defining a navigable map showing the huts and several additional widgets.

    Methods:
        update_huts_data: update the data about the huts to be displayed on the map
        update_zoom_from_point: update the zoom level with new map center point and direction of the zoom level change
        update_zoom_from_widget: update the zoom level specifying the direction of the zoom level change
        update_zoom_from_window: update the zoom level specifying the geographical area to be covered
        update_center_point: update the center point of the map
        get_huts_from_pixel: get the list of huts which are found at the specified pixel location
        get_lat_lon_from_pixel: get the geographical coordinates corresponding to the specified pixel location
        get_lat_lon_map_limits: get the current geographical extension of the map
        get_lat_lon_map_center: get the geographical coordinate of the current map center
        get_delta_lat_lon_from_delta_pixel: get the shift in geographical coordinates from a shift in pixel coordinates
        show_window: show the window widget with the specified coordinates on the map
        hide_window: hide the window widget from the map
        show_ruler: show the ruler widget with the specified start and end points on the map
        hide_ruler: hide the ruler widget from the map
        show_reference_location: show the reference location widget on the map at the specified location
        hide_reference_location: hide the reference location widget from the map
    """
    _WINDOW_COLOUR = (0, 0, 255, 60)
    _RULER_COLOUR = (0, 0, 0, 60)
    _RANGES_COLOUR = (0, 0, 128, 120)
    _RANGES_FOR_ZOOM = {
        6:  [ 50000, 100000, 200000, 400000],
        7:  [ 25000,  50000, 100000, 200000],
        8:  [ 10000,  25000,  50000, 100000],
        9:  [  5000,  10000,  25000,  50000],
        10: [  5000,  10000,  15000,  25000],
        11: [  2000,   4000,   8000,  12000],
        12: [  1000,   2000,   4000,   6000],
        13: [  1000,   2000,   3000,   4000]
    }  # meters
    _GROUP_TEXT_SIZE = 16
    _GROUP_TEXT_COLOUR = (0, 0, 0)
    _RANGES_TEXT_SIZE = 12
    _RANGES_TEXT_COLOUR = (0, 0, 64)
    _RULER_TEXT_SIZE = 12
    _RULER_TEXT_COLOUR = (0, 0, 64)
    _SELF_TEXT_SIZE = 18
    _SELF_TEXT_COLOUR = (255, 255, 255)
    _SELF_TEXT_STRING = "S"

    # Load the fonts
    try:
        _ranges_font = ImageFont.truetype(_FONT_FILENAME, size=_RANGES_TEXT_SIZE)
        _ruler_font = ImageFont.truetype(_FONT_FILENAME, size=_RULER_TEXT_SIZE)
        _group_font = ImageFont.truetype(_FONT_FILENAME, size=_GROUP_TEXT_SIZE)
        _self_font = ImageFont.truetype(_FONT_FILENAME, size=_SELF_TEXT_SIZE)
    except IOError as e:
        _ranges_font = ImageFont.load_default()
        _ruler_font = ImageFont.load_default()
        _group_font = ImageFont.load_default()
        _self_font = ImageFont.load_default()
        errors.append({'type': type(e), 'message': str(e) + ": " + _FONT_FILENAME})

    def __init__(self, pixel_width, pixel_height,
                 default_zoom, min_zoom, max_zoom,
                 default_area):
        """Create a new navigable map with the specified pixel size and zoom levels;
        the initial area covered by the map is also specified.

        :param pixel_width: width in pixel
        :param pixel_height: height in pixel
        :param default_zoom: default zoom level
        :param min_zoom: minimum zoom level
        :param max_zoom: maximum zoom level
        :param default_area: initial area covered by the map as a tuple (lat_min, lat_max, lon_min, lon_max) [degrees]
        """
        super().__init__(default_zoom, min_zoom, max_zoom)

        self._width = pixel_width
        self._height = pixel_height
        self._huts_data = {}

        self._cluster = _TilesCluster(*default_area, self._default_zoom, self._width, self._height)

        self._window = None
        self._ruler = None
        self._reference_location = None

    def update_huts_data(self, huts_data):
        """Update the data about the huts to be displayed on the map.

        The data are provided as a list of dictionaries (one item per hut) with the following keys:
            'index': hut index
            'lat': latitude [degrees]
            'lon': longitude [degrees]
            'status': hut status as a HutStatus enum
            'self_catering': boolean defining if the hut is self catering

        :param huts_data: a list of huts data
        """
        self._huts_data = huts_data
        self._compute_huts_pixel_positions()
        self._compute_huts_groups()

    def update_zoom_from_point(self, lat, lon, direction):
        """Update the zoom level specifying the new map center point and the direction of the zoom level change.

        :param lat: latitude of the new map center point [degrees]
        :param lon: longitude of the new map center point [degrees]
        :param direction: direction of the zoom level change
        """
        new_zoom = self._zoom + (1 if direction > 0 else -1 if direction < 0 else 0)
        if new_zoom < self._min_zoom:
            return
        if new_zoom > self._max_zoom:
            return
        self._update_cluster(lat, lat, lon, lon, new_zoom)

    def update_zoom_from_widget(self, direction):
        """Update the zoom level specifying the direction of the zoom level change (map center point remains fixed).

        :param direction: direction of the zoom level change
        """
        lat, lon = self.get_lat_lon_from_pixel(self._width // 2, self._height // 2)
        self.update_zoom_from_point(lat, lon, direction)

    def update_zoom_from_window(self, lat_min, lat_max, lon_min, lon_max):
        """Update the zoom level specifying the geographical area to be covered.

        :param lat_min: minimum latitude [degrees]
        :param lat_max: maximum latitude [degrees]
        :param lon_min: minimum longitude [degrees]
        :param lon_max: maximum longitude [degrees]
        """
        self._update_cluster(lat_min, lat_max, lon_min, lon_max)

    def update_center_point(self, lat, lon):
        """Update the center point of the map.

        :param lat: new center point latitude [degrees]
        :param lon: new center point longitude [degrees]
        """
        self._update_cluster(lat, lat, lon, lon, self._zoom)

    def get_huts_from_pixel(self, x_pixel, y_pixel):
        """Get the list of huts which are found at the specified pixel location.

        :param x_pixel: x pixel coordinate
        :param y_pixel: y pixel coordinate
        :return: list of huts indexes which are found at the specified pixel location
        """
        for hut_data in self._huts_data.values():
            # Check if the group is not empty i.e. the hut is displayed on the map
            if len(hut_data['group']) > 0:
                if abs(hut_data['x'] - x_pixel) < _HUT_ICON_SIZE[0]//2 and \
                        abs(hut_data['y'] - y_pixel) < _HUT_ICON_SIZE[1]//2:
                    return hut_data['group']
        return []

    def get_lat_lon_from_pixel(self, x_pixel, y_pixel):
        """Get the geographical coordinates corresponding to the specified pixel location.

        :param x_pixel: x pixel coordinate
        :param y_pixel: y pixel coordinate
        :return: tuple of coordinates (latitude, longitude) [degrees]
        """
        return self._cluster.pixel_2_deg(x_pixel, y_pixel)

    def get_delta_lat_lon_from_delta_pixel(self, delta_x_pixel, delta_y_pixel):
        """Get the shift in geographical coordinates corresponding to a shift in pixel coordinates.

        :param delta_x_pixel: shift in x pixel coordinates
        :param delta_y_pixel: shift in y pixel coordinates
        :return: tuple of coordinates shift (latitude, longitude) [degrees]
        """
        return self._cluster.delta_pixel_2_deg(delta_x_pixel, delta_y_pixel)

    def get_lat_lon_map_limits(self):
        """Get the current geographical extension of the map.

        :return: tuple of coordinates (lat_min, lat_max, lon_min, lon_max) [degrees]
        """
        lat_max, lon_min = self._cluster.pixel_2_deg(0, 0)
        lat_min, lon_max = self._cluster.pixel_2_deg(self._width, self._height)
        return lat_min, lat_max, lon_min, lon_max

    def get_lat_lon_map_center(self):
        """Get the geographical coordinate of the current map center.

        :return: tuple of coordinates (latitude, longitude) [degrees]
        """
        return self._cluster.pixel_2_deg(self._width // 2, self._height // 2)

    def show_window(self, lat_min, lat_max, lon_min, lon_max):
        """Show the window widget with the specified coordinates on the map.

        :param lat_min: minimum latitude [degrees]
        :param lat_max: maximum latitude [degrees]
        :param lon_min: minimum longitude [degrees]
        :param lon_max: maximum longitude [degrees]
        :return:
        """
        self._window = (lat_min, lat_max, lon_min, lon_max)

    def hide_window(self):
        """Hide the window widget from the map."""
        self._window = None

    def show_ruler(self, start_lat, start_lon, end_lat, end_lon):
        """Show the ruler widget with the specified start and end points on the map.

        :param start_lat: start latitude [degrees]
        :param start_lon: start longitude [degrees]
        :param end_lat: end latitude [degrees]
        :param end_lon: end longitude [degrees]
        """
        self._ruler = (start_lat, start_lon, end_lat, end_lon)

    def hide_ruler(self):
        """Hide the ruler widget from the map."""
        self._ruler = None

    def show_reference_location(self, lat, lon):
        """Show the reference location widget on the map at the specified location.

        :param lat: latitude [degrees]
        :param lon: longitude [degrees]
        """
        self._reference_location = (lat, lon)

    def hide_reference_location(self):
        """Hide the reference location widget from the map."""
        self._reference_location = None

    def _compute_huts_pixel_positions(self):
        """Compute the position in pixel coordinates of all the huts to be displayed on the map."""
        for hut_data in self._huts_data.values():
            x_pixel_hut, y_pixel_hut = self._cluster.deg_2_pixel(hut_data['lat'], hut_data['lon'])
            hut_data['x'] = x_pixel_hut
            hut_data['y'] = y_pixel_hut

    def _update_cluster(self, lat_min, lat_max, lon_min, lon_max, force_zoom=None):
        """
        Update the tiles cluster to cover the specified geographical area;
        optionally the zoom level can be specified.

        :param lat_min: minimum latitude [degrees]
        :param lat_max: maximum latitude [degrees]
        :param lon_min: minimum longitude [degrees]
        :param lon_max: maximum longitude [degrees]
        :param force_zoom: zoom level
        """
        if force_zoom is not None:
            zoom = force_zoom
        else:
            zoom = self._min_zoom + 1
            while True:
                x_pixel_min, y_pixel_max = WebMercator.deg_2_pixel(lat_min, lon_min, zoom)
                x_pixel_max, y_pixel_min = WebMercator.deg_2_pixel(lat_max, lon_max, zoom)
                delta_x_pixel = x_pixel_max - x_pixel_min
                delta_y_pixel = y_pixel_max - y_pixel_min

                if zoom == self._max_zoom + 1 or delta_x_pixel > self._width or delta_y_pixel > self._height:
                    break
                zoom += 1
            zoom -= 1

        if self._cluster is not None and zoom == self._zoom:
            self._cluster.update_lat_lon(lat_min, lat_max, lon_min, lon_max, self._width, self._height)
        else:
            self._cluster = _TilesCluster(lat_min, lat_max, lon_min, lon_max, zoom, self._width, self._height)

        self._compute_huts_pixel_positions()
        self._compute_huts_groups()

    def _compute_huts_groups(self):
        """Create group of huts wherever they are too close to be correctly displayed on the map.

        The grouping is not performed at the maximum zoom level.
        """
        for hut_data in self._huts_data.values():
            hut_data['group'] = []

        if self._zoom < self._max_zoom:
            self._huts_grouping()
        else:
            for index, hut_data in self._huts_data.items():
                hut_data['group'].append(index)

    def _huts_grouping(self):
        """For every hut, check if its icon would overlap the icon of other huts and group them accordingly."""
        group_indexes = []
        for index, hut_data in self._huts_data.items():
            for index_check in group_indexes:
                hut_data_check = self._huts_data[index_check]
                if self._check_overlap(hut_data['x'], hut_data['y'],
                                       hut_data_check['x'], hut_data_check['y']):
                    # Overlap found: add the hut to another hut's group
                    hut_data_check['group'].append(index)
                    break
            else:
                # No overlap found: add the hut to its own group
                hut_data['group'].append(index)
                group_indexes.append(index)

    @staticmethod
    def _check_overlap(x_first, y_first, x_second, y_second):
        """Check if two hut icons overlap on the map.

        :param x_first: x pixel coordinate of the first hut
        :param y_first: y pixel coordinate of the first hut
        :param x_second: x pixel coordinate of the second hut
        :param y_second: y pixel coordinate of the second hut
        :return: boolean, True if there is an overlap, False otherwise
        """
        delta_x = abs(x_first - x_second)
        delta_y = abs(y_first - y_second)
        return delta_x < _HUT_ICON_SIZE[0] and delta_y < _HUT_ICON_SIZE[1]

    def _add_widgets(self, image):
        """Add all the required widgets to the map image.

        :param image: the map image to which the widgets have to be added
        :return:
        """
        if self._reference_location is not None:
            self._draw_ranges(image)
        for hut_data in self._huts_data.values():
            if len(hut_data['group']) > 0:
                self._draw_hut(image, hut_data['x'], hut_data['y'],
                               hut_data['group'], hut_data['status'], hut_data['self_catering'])
        if self._reference_location is not None:
            self._draw_pin(image)
        if self._window is not None:
            self._draw_window(image)
        if self._ruler is not None:
            self._draw_ruler(image)
        super()._add_widgets(image)

    def _draw_ranges(self, image):
        """Add to the image circular ranges with distance information around the reference location.

        :param image: the map image to which the ranges have to be added
        """
        draw = ImageDraw.Draw(image, 'RGBA')
        for range_value in NavigableMap._RANGES_FOR_ZOOM[self._zoom]:
            x_pixel_pin, y_pixel_pin = self._cluster.deg_2_pixel(*self._reference_location)
            _, delta_lon = meters_to_degrees(range_value, 0, self._reference_location[0])
            x_pixel_range, y_pixel_range = self._cluster.deg_2_pixel(
                self._reference_location[0],
                self._reference_location[1] + delta_lon
            )
            delta_pixel = x_pixel_range - x_pixel_pin
            draw.ellipse((x_pixel_pin - delta_pixel, y_pixel_pin - delta_pixel,
                          x_pixel_pin + delta_pixel, y_pixel_pin + delta_pixel), outline=NavigableMap._RANGES_COLOUR)
            text = "%d km" % (range_value//1000)
            tw, th = draw.textsize(text, font=NavigableMap._ranges_font)
            test_position = (x_pixel_pin - tw//2, y_pixel_pin - delta_pixel - th)
            draw.text(test_position, text,
                      fill=NavigableMap._RANGES_TEXT_COLOUR,
                      font=NavigableMap._ranges_font)

    def _draw_pin(self, image):
        """Add to the image the pin icon at the reference location.

        :param image: the map image to which the pin icon to be added
        """
        x_pixel_pin, y_pixel_pin = self._cluster.deg_2_pixel(*self._reference_location)
        offset = (x_pixel_pin - (_PIN_SIZE[0] - 1) // 2, y_pixel_pin - (_PIN_SIZE[1] - 1) // 2)
        image.paste(_pin_icon, offset, _pin_icon)

    def _draw_window(self, image):
        """Add to the image a rectangular window at the defined location.

        :param image: the map image to which the window have to be added
        """
        draw = ImageDraw.Draw(image, 'RGBA')
        x_pixel_window_min, y_pixel_window_max = self._cluster.deg_2_pixel(self._window[0], self._window[2])
        x_pixel_window_max, y_pixel_window_min = self._cluster.deg_2_pixel(self._window[1], self._window[3])
        draw.rectangle(((x_pixel_window_min, y_pixel_window_min), (x_pixel_window_max, y_pixel_window_max)),
                       fill=NavigableMap._WINDOW_COLOUR)

    def _draw_ruler(self, image):
        """Add to the image a ruler with distance information at the defined location.

        :param image: the map image to which the ruler have to be added
        """
        draw = ImageDraw.Draw(image, 'RGBA')
        x_pixel_start, y_pixel_start = self._cluster.deg_2_pixel(self._ruler[0], self._ruler[1])
        x_pixel_end, y_pixel_end = self._cluster.deg_2_pixel(self._ruler[2], self._ruler[3])
        draw.line(((x_pixel_start, y_pixel_start),
                   (x_pixel_end, y_pixel_end)),
                  fill=NavigableMap._RULER_COLOUR,
                  width=3)
        measured_distance = distance(self._ruler[0], self._ruler[1], self._ruler[2], self._ruler[3])
        x_pixel_mean = (x_pixel_start + x_pixel_end)//2
        y_pixel_mean = (y_pixel_start + y_pixel_end)//2
        text = "{0:.1f} km".format(measured_distance/1000)
        tw, th = draw.textsize(text, font=NavigableMap._ranges_font)
        text_position = x_pixel_mean - tw//2, y_pixel_mean - th//2
        draw.text(text_position, text,
                  fill=NavigableMap._RANGES_TEXT_COLOUR,
                  font=NavigableMap._ranges_font)

    def _draw_hut(self, image, hut_x, hut_y, hut_group, hut_status, hut_self_catering):
        """Add to the image a hut icon with the correct characteristics (position, group, status, self-catering).

        :param image: the map image to which the hut icon have to be added
        :param hut_x: x pixel coordinate of the hut
        :param hut_y: y pixel coordinate of the hut
        :param hut_group: list of huts which belong to this hut's group
        :param hut_status: status of the hut
        :param hut_self_catering: boolean, defines if the hut is self-catering
        """
        offset = (hut_x - (_HUT_ICON_SIZE[0] - 1) // 2, hut_y - (_HUT_ICON_SIZE[1] - 1) // 2)
        if len(hut_group) > 1:
            group_bitmap = Image.Image.copy(_hut_icons['group'])
            draw = ImageDraw.Draw(group_bitmap, 'RGBA')
            text = str(len(hut_group))
            tw, th = draw.textsize(text, font=NavigableMap._group_font)
            text_position = (_HUT_ICON_SIZE[0] - tw) // 2, (_HUT_ICON_SIZE[1] - th) // 2 + 1
            draw.text(text_position, text,
                      fill=NavigableMap._GROUP_TEXT_COLOUR,
                      font=NavigableMap._group_font)
            image.paste(group_bitmap, offset, group_bitmap)
        else:
            hut_bitmap = Image.Image.copy(_hut_icons[hut_status])
            if hut_self_catering:
                draw = ImageDraw.Draw(hut_bitmap, 'RGBA')
                tw, th = draw.textsize(NavigableMap._SELF_TEXT_STRING, font=NavigableMap._self_font)
                text_position = (_HUT_ICON_SIZE[0] - tw) // 2, (_HUT_ICON_SIZE[1] - th) // 2 + 1
                draw.text(text_position, NavigableMap._SELF_TEXT_STRING,
                          fill=NavigableMap._SELF_TEXT_COLOUR,
                          font=NavigableMap._self_font)
            image.paste(hut_bitmap, offset, hut_bitmap)
