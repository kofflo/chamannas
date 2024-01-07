import PySide6
import PySide6.QtWidgets
import PySide6.QtCore
import PySide6.QtGui

from ..abstract.frames import AbstractIconFrame, FrameStyle, CursorStyle, AbstractDialog, AbstractMessageDialog


class Frame(AbstractIconFrame, PySide6.QtWidgets.QMainWindow):

    def __init__(self, *, parent, pos=None, size=None, **kwargs):

        PySide6.QtWidgets.QMainWindow.__init__(self)

        if self._STYLE is FrameStyle.FIXED_SIZE:
            self.layout().setSizeConstraint(PySide6.QtWidgets.QLayout.SetFixedSize)
            self.setWindowFlags(self.windowFlags() | PySide6.QtCore.Qt.CustomizeWindowHint)
            self.setWindowFlags(self.windowFlags() | PySide6.QtCore.Qt.WindowMinimizeButtonHint)
            self.setWindowFlags(self.windowFlags() & ~PySide6.QtCore.Qt.WindowMaximizeButtonHint)
            self.setWindowFlags(self.windowFlags() | PySide6.QtCore.Qt.WindowCloseButtonHint)
        elif self._STYLE is FrameStyle.DIALOG:
            self.setWindowFlags(self.windowFlags() | PySide6.QtCore.Qt.CustomizeWindowHint)
            self.setWindowFlags(self.windowFlags()
                                & ~PySide6.QtCore.Qt.WindowMinimizeButtonHint
                                & ~PySide6.QtCore.Qt.WindowMaximizeButtonHint
                                & ~PySide6.QtCore.Qt.WindowCloseButtonHint)

        if size is not None:
            self.resize(*size)

        if pos is not None:
            self.move(*pos)

        super().__init__(parent=parent, **kwargs)
        self._size = size
        self._panel = self
        self._create_widgets(self._panel)

        central_widget = PySide6.QtWidgets.QWidget()
        self._create_menu()
        self._create_gui().create_layout(central_widget)
        self.setCentralWidget(central_widget)

    def event_connect(self, event, on_event):
        event.connect(lambda kwargs: on_event(**kwargs))

    def event_trigger(self, event, **kwargs):
        event.emit(kwargs)

    def closeEvent(self, event):
        self.detach()
        for child in self.child_views:
            child.close()
        self.on_close(self)
        super().closeEvent(event)

    def _create_menu(self):
        #
        pass

    def _create_gui(self):
        raise NotImplementedError

    @property
    def title(self):
        return super(Frame, Frame).title.__get__(self)

    @title.setter
    def title(self, title):
        super(Frame, Frame).title.__set__(self, title)
        self.setWindowTitle(title)

    @property
    def icon(self):
        return super(Frame, Frame).icon.__get__(self)

    @icon.setter
    def icon(self, icon):
        super(Frame, Frame).icon.__set__(self, icon)
        if self.icon is not None:
            app_icon = PySide6.QtGui.QIcon(self.icon)
            self.setWindowIcon(app_icon)

    def show(self):
        PySide6.QtWidgets.QMainWindow.show(self)
        self._refresh_widgets()

    def close(self):
        PySide6.QtWidgets.QMainWindow.close(self)

    def _set_menubar(self, menu):
        menubar = self.menuBar()
        menubar.clear()
        menu.build_menu(menubar=menubar)

    def _fit_frame(self):
        #
        pass

    def _set_cursor(self, cursor):
        if cursor is CursorStyle.SIZING:
            PySide6.QtGui.QGuiApplication.setOverrideCursor(PySide6.QtCore.Qt.SizeAllCursor)
        elif cursor is CursorStyle.ARROW:
            PySide6.QtGui.QGuiApplication.setOverrideCursor(PySide6.QtCore.Qt.ArrowCursor)

    def set_focus(self):
        self.activateWindow()


class Dialog(AbstractDialog, PySide6.QtWidgets.QDialog):

    def __init__(self, parent, **kwargs):
        PySide6.QtWidgets.QDialog.__init__(self, parent)
        super().__init__(**kwargs)
        self.setWindowFlags(self.windowFlags() & ~PySide6.QtGui.Qt.WindowContextHelpButtonHint)
        self._create_widgets(self)
        self._create_gui().create_layout(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.destroy()

    @property
    def title(self):
        return super(Dialog, Dialog).title.__get__(self)

    @title.setter
    def title(self, title):
        super(Dialog, Dialog).title.__set__(self, title)
        self.setWindowTitle(title)

    def show_modal(self):
        self.update_gui({})
        self.layout().setSizeConstraint(PySide6.QtWidgets.QLayout.SetFixedSize)
        self.exec()
        return self._return_value

    def _on_ok(self, obj):
        super()._on_ok(obj)
        self.accept()

    def _on_cancel(self, obj):
        super()._on_cancel(obj)
        self.reject()


class MessageDialog(AbstractMessageDialog, PySide6.QtWidgets.QMessageBox):

    def __init__(self, parent, message, title):
        PySide6.QtWidgets.QMessageBox.__init__(self, parent)
        self.setIcon(self.Critical)
        super().__init__(message, title=title)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.destroy()

    @property
    def title(self):
        return super(MessageDialog, MessageDialog).title.__get__(self)

    @title.setter
    def title(self, title):
        super(MessageDialog, MessageDialog).title.__set__(self, title)
        self.setWindowTitle(title)

    @property
    def message(self):
        return super(MessageDialog, MessageDialog).message.__get__(self)

    @message.setter
    def message(self, message):
        super(MessageDialog, MessageDialog).message.__set__(self, message)
        self.setText(message)

    def show_modal(self):
        self.update_gui({})
        self.exec()
        return self.result() == self.Accepted
