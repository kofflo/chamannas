from enum import Enum, Flag, auto
import datetime
from threading import Timer


class TextStyle(Enum):
    NORMAL = auto()
    BOLD = auto()
    ITALIC = auto()
    BOLD_ITALIC = auto()


class AbstractWidget:

    def __init__(self, *, is_enabled=True, is_hidden=False):
        self._is_enabled = is_enabled
        self._is_hidden = is_hidden

    def enable(self, is_enabled):
        self._is_enabled = is_enabled

    def hide(self, is_hidden):
        self._is_hidden = is_hidden


class AbstractMouseEventsWidget(AbstractWidget):

    def on_left_down(self, obj, position):
        #
        pass

    def on_left_up(self, obj, position):
        #
        pass

    def on_right_down(self, obj, position):
        #
        pass

    def on_right_up(self, obj, position):
        #
        pass

    def on_wheel(self, obj, position, rotation):
        #
        pass

    def on_mouse_motion(self, obj, position):
        #
        pass

    def on_mouse_enter(self, obj):
        #
        pass

    def on_mouse_leave(self, obj):
        #
        pass


class AbstractLabelledWidget(AbstractWidget):

    def __init__(self, *, label="", **kwargs):
        super().__init__(**kwargs)
        self.label = label

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label


class AbstractButton(AbstractLabelledWidget):

    def __init__(self, *, on_click=None, **kwargs):
        super().__init__(**kwargs)
        if on_click is not None:
            self.on_click = on_click

    def on_click(self, obj):
        #
        pass


class AbstractCheckBox(AbstractButton):

    def __init__(self, *, value=False, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class AbstractRadioBox(AbstractLabelledWidget):

    def __init__(self, *, choices=None, num_choices=1, selection=0,  on_click=None, **kwargs):
        super().__init__(**kwargs)
        if choices is None:
            self._choices = [''] * num_choices
        else:
            self._choices = choices
        self._selection = selection
        if on_click is not None:
            self.on_click = on_click

    def on_click(self, obj):
        #
        pass

    @property
    def selection(self):
        return self._selection

    @selection.setter
    def selection(self, selection):
        if 0 <= selection < len(self._choices):
            self._selection = selection

    def set_string(self, index, string):
        if 0 <= index < len(self._choices):
            self._choices[index] = string


class AbstractBitmap:

    def __init__(self, *, bitmap=None, **kwargs):
        self.bitmap = bitmap
        super().__init__(**kwargs)

    @property
    def bitmap(self):
        return self._bitmap

    @bitmap.setter
    def bitmap(self, bitmap):
        self._bitmap = bitmap


class AbstractText(AbstractLabelledWidget):

    def __init__(self, *, font_style=TextStyle.NORMAL, font_size=9,
                 foreground_color=None, background_color=None,
                 **kwargs):
        super().__init__(**kwargs)
        self._font_size = font_size
        self.font_style = font_style
        self.font_size = font_size
        self._background_color = None
        self.foreground_color = foreground_color
        self.background_color = background_color

    @property
    def font_style(self):
        return self._font_style

    @font_style.setter
    def font_style(self, font_style):
        self._font_style = font_style

    @property
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, font_size):
        self._font_size = font_size

    @property
    def foreground_color(self):
        return self._foreground_color

    @foreground_color.setter
    def foreground_color(self, foreground_color):
        self._foreground_color = foreground_color

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, background_color):
        self._background_color = background_color


class AbstractCalendar(AbstractWidget):

    def __init__(self, *, lower_date=None, upper_date=None, selected_date=None, **kwargs):
        super().__init__(**kwargs)
        if selected_date is None:
            selected_date = datetime.date.today()
        self._selected_date = selected_date
        self._upper_date = upper_date
        self.lower_date = lower_date
        self.upper_date = upper_date
        self.selected_date = selected_date

    @property
    def lower_date(self):
        return self._lower_date

    @lower_date.setter
    def lower_date(self, lower_date):
        if lower_date is None or self._upper_date is None or lower_date <= self._upper_date:
            self._lower_date = lower_date
        if self._lower_date is not None and self.selected_date < self._lower_date:
            self.selected_date = self._lower_date

    @property
    def upper_date(self):
        return self._upper_date

    @upper_date.setter
    def upper_date(self, upper_date):
        if upper_date is None or self._lower_date is None or upper_date >= self._lower_date:
            self._upper_date = upper_date
        if self._upper_date is not None and self.selected_date > self._upper_date:
            self.selected_date = self._upper_date

    @property
    def selected_date(self):
        return self._selected_date

    @selected_date.setter
    def selected_date(self, date):
        if (self._lower_date is None or date >= self._lower_date) and \
           (self._upper_date is None or date <= self._upper_date):
            self._selected_date = date

    def on_date_changed(self, obj):
        #
        pass

    def set_language(self, language):
        #
        pass


class AbstractSpinControl(AbstractWidget):

    def __init__(self, *, min_value=None, max_value=None, value=0, **kwargs):
        super().__init__(**kwargs)
        self._value = value
        self._max_value = max_value
        self.min_value = min_value
        self.max_value = max_value
        self.value = value

    def enable(self, is_enabled):
        self._is_enabled = is_enabled

    @property
    def min_value(self):
        return self._min_value

    @min_value.setter
    def min_value(self, min_value):
        if min_value is None or self._max_value is None or min_value <= self._max_value:
            self._min_value = min_value
        if self._min_value is not None and self.value < self._min_value:
            self.value = self._min_value

    @property
    def max_value(self):
        return self._max_value

    @max_value.setter
    def max_value(self, max_value):
        if max_value is None or self._min_value is None or max_value >= self._min_value:
            self._max_value = max_value
        if self._max_value is not None and self.value > self._max_value:
            self.value = self._max_value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if (self._min_value is None or value >= self._min_value) and \
           (self._max_value is None or value <= self._max_value):
            self._value = value

    def on_click(self, obj):
        #
        pass


class AbstractMenu(AbstractLabelledWidget):

    SEPARATOR = None

    def __init__(self, *, items=None, on_click=None, **kwargs):
        super().__init__(**kwargs)
        self._items = []
        self._return_items = {}
        if items is not None:
            for item in items:
                if isinstance(item, list) or isinstance(item, tuple):
                    self._items.append(item)
                else:
                    self._items.append((item, True, None))
        if on_click is not None:
            self.on_click = on_click
            self._inherit = False
        else:
            self._inherit = True

    def append(self, item, enabled=True, on_item_click=None):
        self._items.append((item, enabled, on_item_click))

    def build_menu(self, menubar=None, inherited_on_click=None):
        if self._inherit is True and inherited_on_click is not None:
            self.on_click = inherited_on_click
        for menu_id, value in enumerate(self._items):
            item, is_enabled, on_item_click = value
            if menubar is not None:
                self._append_menubar(menubar, item, is_enabled, on_item_click)
            else:
                self._append_menu(item, is_enabled, on_item_click)

    def _append_menubar(self, menubar, item, is_enabled, on_item_click):
        raise NotImplementedError

    def _append_menu(self, item, is_enabled, on_item_click):
        raise NotImplementedError

    def on_click(self, obj, choice_id):
        #
        pass

    def pop_up(self):
        self.build_menu()

    def get_item_label(self, item_id):
        return self._return_items[item_id]

    def on_close(self, obj):
        #
        pass


class AbstractTimedMenu(AbstractMenu):

    _TIMER_DURATION = 0.2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._timer = None

    def command_close(self):
        if self._timer is None and not self._mouse_inside_widget():
            self._timer = Timer(self._TIMER_DURATION, self._close)
            self._timer.start()

    def force_close(self):
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        self._close()

    def prevent_close(self):
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def _close(self):
        if self._timer is not None:
            self._timer.cancel()
        else:
            self._timer = None

    def _on_mouse_enter(self, obj):
        self.prevent_close()
        self.on_mouse_enter(obj)

    def _on_mouse_leave(self, obj):
        self.command_close()
        self.on_mouse_leave(obj)

    def on_mouse_enter(self, obj):
        #
        pass

    def on_mouse_leave(self, obj):
        #
        pass

    def _mouse_inside_widget(self):
        raise NotImplementedError


class AbstractTextTimedMenu(AbstractTimedMenu):

    _FOREGROUND_NORMAL_COLOR = (0, 0, 0)
    _BACKGROUND_NORMAL_COLOR = (255, 255, 255)
    _FOREGROUND_HIGHLIGHT_COLOR = (255, 255, 255)
    _BACKGROUND_HIGHLIGHT_COLOR = (0, 120, 215)
    _FOREGROUND_DISABLED_COLOR = (80, 80, 80)
    _BACKGROUND_DISABLED_COLOR = (255, 255, 255)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mouse_inside = {}
        self._texts = {}

    def _create_text(self, label):
        raise NotImplementedError

    def _append_menu(self, item, is_enabled, on_item_click):
        if isinstance(item, AbstractMenu):
            for menu_id, value in enumerate(item._items):
                sub_item, sub_is_enabled, sub_on_item_click = value
                self._append_menu(sub_item, sub_is_enabled and is_enabled, sub_on_item_click)
        else:
            text = self._create_text(label=item)
            self._mouse_inside[text] = False
            self._texts[text] = item
            self._return_items[text] = item
            if item is not self.SEPARATOR and is_enabled:
                if on_item_click is not None:
                    text.on_left_down = lambda obj, pos: (self._close(), on_item_click())
                    text.on_right_down = lambda obj, pos: (self._close(), on_item_click())
                else:
                    text.on_left_down = self._on_item_click
                    text.on_right_down = self._on_item_click
                text.on_mouse_enter = self._on_mouse_enter_item
                text.on_mouse_leave = self._on_mouse_leave_item
                self._set_normal_color(text)
            else:
                text.on_mouse_enter = self._on_mouse_enter_disabled_item
                text.on_mouse_leave = self._on_mouse_leave_disabled_item
                self._set_disabled_color(text)

    def _set_normal_color(self, text):
        text.foreground_color = self._FOREGROUND_NORMAL_COLOR
        text.background_color = self._BACKGROUND_NORMAL_COLOR

    def _set_highlight_color(self, text):
        text.foreground_color = self._FOREGROUND_HIGHLIGHT_COLOR
        text.background_color = self._BACKGROUND_HIGHLIGHT_COLOR

    def _set_disabled_color(self, text):
        text.foreground_color = self._FOREGROUND_DISABLED_COLOR
        text.background_color = self._BACKGROUND_DISABLED_COLOR

    def _on_mouse_enter_item(self, obj):
        self._mouse_inside[obj] = True
        self._set_highlight_color(obj)
        self._on_mouse_enter(self)

    def _on_mouse_leave_item(self, obj):
        self._mouse_inside[obj] = False
        self._set_normal_color(obj)
        if not self._mouse_inside_widget():
            self._on_mouse_leave(self)

    def _on_mouse_enter_disabled_item(self, obj):
        self._mouse_inside[obj] = True
        self._on_mouse_enter(self)

    def _on_mouse_leave_disabled_item(self, obj):
        self._mouse_inside[obj] = False
        if not self._mouse_inside_widget():
            self._on_mouse_leave(self)

    def _on_item_click(self, obj, position):
        self._close()
        self.on_click(self, obj)

    def _mouse_inside_widget(self):
        return any(self._mouse_inside.values())


class Align(Flag):
    LEFT = auto()
    HCENTER = auto()
    RIGHT = auto()
    TOP = auto()
    VCENTER = auto()
    BOTTOM = auto()
    START = LEFT | TOP
    CENTER = HCENTER | VCENTER
    END = RIGHT | BOTTOM
    EXPAND = auto()


class AbstractLayout:

    def create_layout(self, parent):
        raise NotImplementedError()


class AbstractBoxLayout(AbstractLayout):
    def __init__(self):
        self._widgets = []

    def add(self, widget, align=Align.START, border=0, stretch=0):
        self._widgets.append({'type': widget, 'align': align, 'border': border, 'stretch': stretch})

    def add_space(self, space):
        self._widgets.append({'type': 'space', 'space': space})

    def add_stretch(self, stretch=1):
        self._widgets.append({'type': 'stretch', 'stretch': stretch})


class AbstractGridLayout(AbstractLayout):
    def __init__(self, rows, cols, vgap, hgap):
        self._rows = rows
        self._cols = cols
        self._widgets = [[None] * self._cols for _ in range(self._rows)]
        self._row_stretch = [None] * self._rows
        self._col_stretch = [None] * self._rows
        self._vgap = vgap
        self._hgap = hgap

    def add(self, row, col, widget, align=Align.CENTER, border=0):
        self._widgets[row][col] = {'type': widget, 'align': align, 'border': border}

    def add_space(self, row, col, width, height):
        self._widgets[row][col] = {'type': 'space', 'width': width, 'height': height}

    def create_sizer(self):
        raise NotImplementedError()

    def row_stretch(self, row, stretch):
        self._row_stretch[row] = stretch

    def col_stretch(self, col, stretch):
        self._col_stretch[col] = stretch
