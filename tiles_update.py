"""
Create the missing tiles. Requires Maperitive.

Run with:
python tiles_update.py
"""
from pathlib import Path
import shutil
import os
from src import model, map_tools, config
import prettysusi
prettysusi.initialize('wx')
from src.view.frames import DetailedInfoView

# Configuration of Maperitive
_TILES_SOURCE_PATH = r'C:\Users\PC\tiles'
_SCRIPT_FILE = "chamannas.mscript"
_MAPERITIVE_PATH = r'"C:\Users\PC\Maperitive\Maperitive.exe"'
_MAPERITIVE_SCRIPT_STRING = "add-web-map\ngenerate-tiles bounds={minlon},{minlat},{maxlon},{maxlat} minzoom={zoom} maxzoom={zoom} tilesdir={tiles_source}\n"
_MAPERITIVE_OPTIONS = "-exitafter"

# Map constants
_DETAILED_MAP_WIDTH = DetailedInfoView._DETAILED_MAP_WIDTH
_DETAILED_MAP_HEIGHT = DetailedInfoView._DETAILED_MAP_HEIGHT
_DETAILED_MAP_MIN_ZOOM = DetailedInfoView._DETAILED_MAP_MIN_ZOOM
_DETAILED_MAP_REF_ZOOM = DetailedInfoView._DETAILED_MAP_REF_ZOOM
_DETAILED_MAP_MAX_ZOOM = DetailedInfoView._DETAILED_MAP_MAX_ZOOM

# Create the model instance
huts_model = model.HutsModel()

# Create a map for each zoom level and each hut
for index, hut in huts_model._huts_dictionary.items():
    hut_map = map_tools.HutMap(hut['lat'], hut['lon'],
                               _DETAILED_MAP_WIDTH, _DETAILED_MAP_HEIGHT,
                               _DETAILED_MAP_REF_ZOOM, _DETAILED_MAP_MIN_ZOOM, _DETAILED_MAP_MAX_ZOOM)
    for k in range(_DETAILED_MAP_REF_ZOOM - _DETAILED_MAP_MIN_ZOOM):
        hut_map.update_zoom(-1)
    for k in range(_DETAILED_MAP_MAX_ZOOM - _DETAILED_MAP_MIN_ZOOM):
        hut_map.update_zoom(1)

# Look for missing tiles that need to be generated
missing_tiles = set()
for error in map_tools.errors:
    if error['type'] == 'Missing tile':
        missing_tiles.add(error['message'])

if not missing_tiles:
    print("No tiles missing")
    exit(0)

print(str(len(missing_tiles)), " missing tiles")

# create script
tiles_source = Path(_TILES_SOURCE_PATH)
tiles_source.mkdir(parents=True, exist_ok=True)
script = tiles_source / _SCRIPT_FILE
with open(script, "w") as f:
    for i, missing_tile in enumerate(missing_tiles):
        print("Generating the script for tile ", str(i+1), "/", str(len(missing_tiles)))
        zoom, x, y = list(map(int, missing_tile.split('_')))
        maxlat, minlon = map_tools.WebMercator.tile_2_deg(x, y, zoom)
        minlat, maxlon = map_tools.WebMercator.tile_2_deg(x + 1, y + 1, zoom)
        lat = (minlat + maxlat) / 2
        lon = (minlon + maxlon) / 2
        f.write(_MAPERITIVE_SCRIPT_STRING.format(
            minlat=lat,
            minlon=lon,
            maxlat=lat,
            maxlon=lon,
            zoom=zoom,
            tiles_source=_TILES_SOURCE_PATH
        ))

# run script
command_line = " ".join([str(_MAPERITIVE_PATH), _MAPERITIVE_OPTIONS, str(script)])
os.system(command_line)

# copy the generated tiles to the chamannas tiles path
tiles_destination = Path(config.ASSETS_PATH_TILES)

for missing_tile in missing_tiles:
    zoom, x, y = missing_tile.split('_')
    source_file = tiles_source / zoom / x / (y + '.png')
    destination_file = tiles_destination / zoom / x / (y + '.png')
    if source_file.is_file():
        os.makedirs(os.path.dirname(destination_file), exist_ok=True)
        print("Copying ", str(source_file), " to the destination folder")
        shutil.copy(source_file, destination_file)
    else:
        print(str(source_file), " not found in source folder")
