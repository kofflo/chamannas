from . import app

if app is None:
    raise ImportError("The gui_library has not been correctly imported\nRun gui_library.initialize(GUI_TYPE) first.")

from .abstract.frames import FrameStyle, CursorStyle
from . import Frame, Dialog, MessageDialog
