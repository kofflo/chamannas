import sys

app = None
event_create = None
Button, CheckBox, RadioBox, Bitmap, Text, TextControl,\
    Calendar, SpinControl, Menu, TextTimedMenu = [None] * 10


def import_gui_library(gui):

    global app, event_create
    global Button, CheckBox, RadioBox, Bitmap, Text, TextControl, Calendar, SpinControl, Menu, TextTimedMenu

    if gui == 'wx':
        # Import WxPython GUI
        try:
            from wx import App

            from src.gui_library.wx import event_create
            from src.gui_library.wx.widgets import Button, CheckBox, RadioBox, Bitmap, Text, TextControl,\
                Calendar, SpinControl, Menu, TextTimedMenu

            app = App()
            app.run = app.MainLoop

        except ImportError as e:
            print("Fatal error: the required GUI 'wx' cannot be loaded correctly")
            print(e)
            sys.exit(1)

    elif gui == 'qt5':
        # Import Qt5 GUI
        try:
            from PySide2.QtWidgets import QApplication

            from src.gui_library.qt5 import event_create
            from src.gui_library.qt5.widgets import Button, CheckBox, RadioBox, Bitmap, Text, TextControl,\
                Calendar, SpinControl, Menu, TextTimedMenu

            app = QApplication([])
            app.run = app.exec_

        except ImportError as e:
            print("Fatal error: the required GUI 'qt5' cannot be loaded correctly")
            print(e)
            sys.exit(1)

    elif gui == 'tk':
        # Import tkinter GUI
        try:
            from tkinter import Tk, ttk
            app = Tk()

            from src.gui_library.tk import event_create
            from src.gui_library.tk.widgets import Button, CheckBox, RadioBox, Bitmap, Text, TextControl,\
                Calendar, SpinControl, Menu, TextTimedMenu

            app.withdraw()
            app.run = app.mainloop

        except ImportError as e:
            print("Fatal error: the required GUI 'tk' cannot be loaded correctly")
            print(e)
            sys.exit(1)

    else:
        # An invalid GUI has been requested
        print(f"Fatal error: the required GUI '{gui}' is not valid")
        sys.exit(1)
