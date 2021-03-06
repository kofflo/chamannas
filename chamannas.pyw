"""
Main script which runs the application.

Run with:
python chamannas.pyw [-v (table | map)] [-g (wx | qt5 | tk)]

Options:
-v (--view): selects the main view
    table: opens the tables window as main wiew [default]
    map: opens the map window as main wiew
-g (--graphics): selects the graphic library for the GUI
    wx: wxPython
    qt5: Qt 5
    tk: Tkinter

The following data files are used by the application:

./assets
    /data
        /config.yaml            Configuration file (mandatory)
        /huts.txt               List of mountain huts (mandatory)
        /mountain_ranges.txt    List of mountain ranges [in different languages]
        /regions.txt            List of regions [in different languages]
        /strings.txt            All strings used within the GUI [in different languages]
        /preferences.yaml       Temporary preferences, updated on application exit
        /results.yaml           Cached huts places results
    /fonts
        /GidoleFont
            /Gidole-Regular.ttf Font used in the map
    /icons
        /app_icon.png           Application icon
        /icon_darkgray.png      Icon of darkgray hut
        /icon_green.png         Icon of green hut
        /icon_lightgray.png     Icon of lightgray hut
        /icon_orange.png        Icon of orange hut
        /icon_red.png           Icon of red hut
        /icon_white.png         Icon of white hut
        /minus.png              Icon of minus symbol
        /pin.png                Icon of pin symbol
        /plus.png               Icon of plus symbol
        /zoom.png               Icon of zoom symbol
    /tiles
        /z                      Tiles for zoom level "z"
            /x                  Tiles for column "x"
                /y.png          Tile for row "y"
"""
import argparse

_SUPPORTED_GRAPHICS = ['wx', 'qt5', 'tk']

# Define the command line arguments
parser = argparse.ArgumentParser(description="Search for available beds in mountain huts.")
parser.add_argument('-g', '--graphics', type=str, nargs=1, choices=_SUPPORTED_GRAPHICS,
                    help="Graphic library for the GUI")
parser.add_argument('-v', '--view', type=str, nargs=1, choices=['table', 'map'],
                    help="View at start")

args = parser.parse_args()

from src import config

# Load the configuration
config.load(args)

from src import model, controller, i18n, map_tools, web_request, view

# Load the internationalization features
i18n.load()

# Configure the tiles cache
map_tools.configure()

# Configure the base url for web data retrieval
web_request.configure()

# Create the model instance
huts_model = model.HutsModel()

# Select the main view
main_view = 'table'
if config.VIEW is not None:
    main_view = config.VIEW
if main_view == 'map':
    # Create the controller instance with a map view
    huts_controller = controller.HutsController(huts_model, 'map')
else:
    # Create the controller instance with a table view
    huts_controller = controller.HutsController(huts_model, 'table')

# Start the app main loop
view.app.run()

# On exit, save the preferences and the results dictionary
_, all_selected = huts_model.get_selected()
reference_location = huts_model.get_reference_location()
preferences = {
    'LANGUAGE': i18n.get_current_language_string(),
    'REFERENCE_LOCATION': [reference_location['lat'], reference_location['lon']],
    'SELECTED': all_selected,
    'GUI': config.GUI,
    'VIEW': config.VIEW
}
config.save_preferences(preferences)

results_dictionary = huts_model.get_results_dictionary()
results = {
    'RESULTS_DICTIONARY': results_dictionary
}
config.save_results(results)
