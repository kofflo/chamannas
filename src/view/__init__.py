"""
View package: manages the GUI.

This __init__ file loads the implementation of the classes and the app object for the specific GUI type
as selected in the configuration.

Variables:
    app: the application object with a 'run' callable attribute
    view_errors: list containing the errors detected in this package

Classes:
    Button: a pushbutton widget
    CheckBox: a checkbox widget
    RadioBox: a radio button widget
    Bitmap: an image widget
    Text: a simple text widget
    Calendar: a calendar widget
    SpinControl: a spin control widget
    Menu: a menu widget
    TextControl: a text widget allowing user input
    TextTimedMenu: a menu widget which remains displayed for a specific time
    HutsGrid: a grid widget to display huts information
    DetailedGrid: a grid widget to display detailed information about a hut
    SelectedDetailedGrid: a grid widget to display detailed information about a group of huts
    DeveloperGrid: a grid widget to display information about warnings or errors
    HutsTableView: a frame displaying huts information in a grid table
    HutsMapView: a frame displaying huts information in a map
    DetailedInfoView: a frame displaying detailed information for a hut
    SelectedInfoView: a frame displaying detailed information for a group of huts
    DeveloperInfoView: a frame displaying information about warnings or errors
    AboutDialog: a dialog displaying information about the app
    UpdateDialog: a dialog displaying the available updates for the app
"""
import sys
import src.gui_library
from src import config
from src.view.abstract import view_errors


_config_GUI = config.GUI

# Select the GUI to use based on the configuration,
# using a default GUI if the required one is not supported
if _config_GUI is None:
    _GUI = config.DEFAULT_GUI
elif config.SUPPORTED_GUIS and _config_GUI not in config.SUPPORTED_GUIS:
    view_errors.append({
        'type': 'Wrong GUI',
        'message': f"The required GUI '{config.GUI}' is not valid;"
                   f" '{config.DEFAULT_GUI}' is selected as default"
    })
    _GUI = config.DEFAULT_GUI
else:
    _GUI = _config_GUI

src.gui_library.import_gui_library(_GUI)

from src.gui_library import event_create, app
from src.gui_library import Button, CheckBox, RadioBox, Bitmap, Text, TextControl, \
    Calendar, SpinControl, Menu, TextTimedMenu

if _GUI == 'wx':
    # Import WxPython GUI
    try:
        from src.view.wx.tables import HutsGrid, DetailedGrid, DeveloperGrid, SelectedDetailedGrid
        from src.view.wx.frames import HutsTableView, HutsMapView, DetailedInfoView, SelectedInfoView, \
            DeveloperInfoView, AboutDialog, UpdateDialog

    except ImportError as e:
        print("Fatal error: the required GUI 'wx' cannot be loaded correctly")
        print(e)
        sys.exit(1)

elif _GUI == 'qt5':
    # Import Qt5 GUI
    try:
        from src.view.qt5.tables import HutsGrid, DetailedGrid, DeveloperGrid, SelectedDetailedGrid
        from src.view.qt5.frames import HutsTableView, HutsMapView, DetailedInfoView, SelectedInfoView, \
            DeveloperInfoView, AboutDialog, UpdateDialog

    except ImportError as e:
        print("Fatal error: the required GUI 'qt5' cannot be loaded correctly")
        print(e)
        sys.exit(1)

elif _GUI == 'tk':
    # Import tkinter GUI
    try:
        from src.view.tk.tables import HutsGrid, DetailedGrid, DeveloperGrid, SelectedDetailedGrid
        from src.view.tk.frames import HutsTableView, HutsMapView, DetailedInfoView, SelectedInfoView, \
            DeveloperInfoView, AboutDialog, UpdateDialog

    except ImportError as e:
        print("Fatal error: the required GUI 'tk' cannot be loaded correctly")
        print(e)
        sys.exit(1)

else:
    # An invalid GUI has been requested
    print(f"Fatal error: the required GUI '{_GUI}' is not valid")
    sys.exit(1)
