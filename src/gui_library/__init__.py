import sys

app = None
event_create = None
Button, CheckBox, RadioBox, Bitmap, Text, TextControl, \
    Calendar, SpinControl, Menu, TextTimedMenu = [None] * 10
Grid = None
Frame, Dialog, MessageDialog = [None] * 3
VBoxLayout, HBoxLayout, GridLayout = [None] * 3


def initialize(gui):

    global app, event_create
    global Button, CheckBox, RadioBox, Bitmap, Text, TextControl, Calendar, SpinControl, Menu, TextTimedMenu
    global Grid
    global Frame, Dialog, MessageDialog
    global VBoxLayout, HBoxLayout, GridLayout

    if gui == 'wx':
        # Import WxPython GUI
        try:
            from wx import App

            from .wx import event_create
            from .wx.widgets import Button, CheckBox, RadioBox, Bitmap, Text, TextControl,\
                Calendar, SpinControl, Menu, TextTimedMenu
            from .wx.layouts import VBoxLayout, HBoxLayout, GridLayout
            from .wx.frames import Frame, Dialog, MessageDialog
            from .wx.tables import Grid

            app = App()
            app.run = app.MainLoop

        except ImportError as e:
            print("Fatal error: the required GUI 'wx' cannot be loaded correctly")
            print(e)
            sys.exit(1)

    elif gui == 'qt':
        # Import Qt GUI
        try:
            from PySide6.QtWidgets import QApplication

            from .qt import event_create
            from .qt.widgets import Button, CheckBox, RadioBox, Bitmap, Text, TextControl,\
                Calendar, SpinControl, Menu, TextTimedMenu
            from .qt.tables import Grid
            from .qt.frames import Frame, Dialog, MessageDialog
            from .qt.layouts import VBoxLayout, HBoxLayout, GridLayout

            app = QApplication([])
            app.run = app.exec

        except ImportError as e:
            print("Fatal error: the required GUI 'qt' cannot be loaded correctly")
            print(e)
            sys.exit(1)

    elif gui == 'tk':
        # Import tkinter GUI
        try:
            from tkinter import Tk, ttk
            app = Tk()

            from .tk import event_create
            from .tk.widgets import Button, CheckBox, RadioBox, Bitmap, Text, TextControl,\
                Calendar, SpinControl, Menu, TextTimedMenu
            from .tk.tables import Grid
            from .tk.frames import Frame, Dialog, MessageDialog
            from .tk.layouts import VBoxLayout, HBoxLayout, GridLayout

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
