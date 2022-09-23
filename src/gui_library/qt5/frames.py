import PySide2
import PySide2.QtWidgets
import PySide2.QtCore
import PySide2.QtGui

from src.view.abstract.frames import AbstractIconFrame, FrameStyle, CursorStyle, AbstractDialog


class QtFrame(AbstractIconFrame, PySide2.QtWidgets.QMainWindow):

    _NEW_VERSION = False

    def __init__(self, *, parent, pos=None, size=None, **kwargs):

        PySide2.QtWidgets.QMainWindow.__init__(self)

        if self._STYLE is FrameStyle.FIXED_SIZE:
            self.layout().setSizeConstraint(PySide2.QtWidgets.QLayout.SetFixedSize)
            self.setWindowFlags(self.windowFlags() | PySide2.QtCore.Qt.CustomizeWindowHint)
            self.setWindowFlags(self.windowFlags() & ~PySide2.QtCore.Qt.WindowMaximizeButtonHint)
        elif self._STYLE is FrameStyle.DIALOG:
            self.setWindowFlags(self.windowFlags() | PySide2.QtCore.Qt.CustomizeWindowHint)
            self.setWindowFlags(self.windowFlags()
                                & ~PySide2.QtCore.Qt.WindowMinimizeButtonHint
                                & ~PySide2.QtCore.Qt.WindowMaximizeButtonHint
                                & ~PySide2.QtCore.Qt.WindowCloseButtonHint)

        if size is not None:
            self.resize(*size)

        if pos is not None:
            self.move(*pos)

        super().__init__(parent=parent, **kwargs)
        self._size = size
        self._panel = self
        self._create_widgets(self._panel)

        central_widget = PySide2.QtWidgets.QWidget()
        self._create_menu()
        self._create_gui().create_layout(central_widget)
        self.setCentralWidget(central_widget)

    def event_connect(self, event, on_event):
        event.connect(lambda kwargs: on_event(**kwargs))

    def event_trigger(self, event, **kwargs):
        event.emit(kwargs)

    def closeEvent(self, event):
        self.detach()
        self.on_close(self)
        super().closeEvent(event)

    def _create_menu(self):
        #
        pass

    def _create_gui(self):
        raise NotImplementedError

    @property
    def title(self):
        return super(QtFrame, QtFrame).title.__get__(self)

    @title.setter
    def title(self, title):
        super(QtFrame, QtFrame).title.__set__(self, title)
        self.setWindowTitle(title)

    @property
    def icon(self):
        return super(QtFrame, QtFrame).icon.__get__(self)

    @icon.setter
    def icon(self, icon):
        super(QtFrame, QtFrame).icon.__set__(self, icon)
        if self.icon is not None:
            app_icon = PySide2.QtGui.QIcon(self.icon)
            self.setWindowIcon(app_icon)

    def show(self):
        PySide2.QtWidgets.QMainWindow.show(self)
        self._refresh_widgets()

    def close(self):
        PySide2.QtWidgets.QMainWindow.close(self)

    def _set_menubar(self, menu):
        menubar = self.menuBar()
        menubar.clear()
        menu.build_menu(menubar=menubar)

    def _fit_frame(self):
        #
        pass

    def _set_cursor(self, cursor):
        if cursor is CursorStyle.SIZING:
            PySide2.QtGui.QGuiApplication.setOverrideCursor(PySide2.QtCore.Qt.SizeAllCursor)
        elif cursor is CursorStyle.ARROW:
            PySide2.QtGui.QGuiApplication.setOverrideCursor(PySide2.QtCore.Qt.ArrowCursor)

    def set_focus(self):
        self.activateWindow()


class QtDialog(AbstractDialog, PySide2.QtWidgets.QDialog):

    def __init__(self, parent, **kwargs):
        PySide2.QtWidgets.QDialog.__init__(self, parent)
        super().__init__(**kwargs)
        self.setWindowFlags(self.windowFlags() & ~PySide2.QtGui.Qt.WindowContextHelpButtonHint)
        self._create_widgets(self)
        self._create_gui().create_layout(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.destroy()

    @property
    def title(self):
        return super(QtDialog, QtDialog).title.__get__(self)

    @title.setter
    def title(self, title):
        super(QtDialog, QtDialog).title.__set__(self, title)
        self.setWindowTitle(title)

    def show_modal(self):
        self.update_gui({})
        self.layout().setSizeConstraint(PySide2.QtWidgets.QLayout.SetFixedSize)
        self.exec_()
        return self._return_value

    def _on_ok(self, obj):
        super()._on_ok(obj)
        self.accept()

    def _on_cancel(self, obj):
        super()._on_cancel(obj)
        self.reject()
