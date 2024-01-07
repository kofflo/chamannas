from enum import Enum, auto
from .. import event_create
from src.config import ASSETS_PATH_ICONS

_APP_ICON_FILENAME = str(ASSETS_PATH_ICONS / "app_icon.png")


class FrameStyle(Enum):
    NORMAL = auto()
    FIXED_SIZE = auto()
    DIALOG = auto()


class CursorStyle(Enum):
    ARROW = auto()
    SIZING = auto()


class AbstractFrame:

    _STYLE = FrameStyle.NORMAL
    _close_event = event_create()
    _update_gui_event = event_create()

    def __init__(self, *, parent=None, title="", icon=None):
        self.parent = parent
        if parent is not None:
            parent.child_views.append(self)
        self.child_views = []
        self.title = title
        self.icon = icon
        self.event_connect(self._close_event, self._on_close_event)
        self.event_connect(self._update_gui_event, self._on_update_gui_event)

    def event_connect(self, event, on_event):
        raise NotImplementedError

    def event_trigger(self, event, **kwargs):
        raise NotImplementedError

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, icon):
        self._icon = icon

    def show(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def _create_widgets(self, panel):
        raise NotImplementedError

    def update_gui(self, data):
        for child_view in self.child_views:
            child_view.update_gui(data)
        self._refresh_widgets()
        self._fit_frame()

    def detach(self):
        if self.parent is not None:
            self.parent.child_views.remove(self)

    def on_close(self, obj):
        #
        pass

    def _fit_frame(self):
        raise NotImplementedError

    def _set_menubar(self, menu):
        raise NotImplementedError

    def set_focus(self):
        raise NotImplementedError

    def _set_cursor(self, cursor):
        raise NotImplementedError

    def _refresh_widgets(self):
        #
        pass

    def _on_close_event(self):
        self.close()

    def _on_update_gui_event(self, data):
        self.update_gui(data)

    def close_from_thread(self):
        self.event_trigger(self._close_event)

    def update_gui_from_thread(self, data):
        self.event_trigger(self._update_gui_event, data=data)


class AbstractIconFrame(AbstractFrame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, icon=_APP_ICON_FILENAME)


class AbstractDialog:

    def __init__(self, *, title):
        self.title = title
        self._return_value = False

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    def update_gui(self, data):
        #
        pass

    def show_modal(self):
        raise NotImplementedError

    def _on_ok(self, obj):
        self._return_value = True

    def _on_cancel(self, obj):
        self._return_value = False

    def _create_widgets(self, panel):
        raise NotImplementedError


class AbstractMessageDialog(AbstractDialog):

    def __init__(self, message, **kwargs):
        self.message = message
        super().__init__(**kwargs)

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        self._message = message
