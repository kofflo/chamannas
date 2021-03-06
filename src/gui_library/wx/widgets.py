import wx
import wx.adv
import datetime
from src.gui_library.abstract.widgets import AbstractWidget, AbstractMouseEventsWidget, AbstractLabelledWidget, \
    AbstractButton, AbstractCheckBox, AbstractRadioBox, AbstractBitmap, \
    AbstractText, AbstractCalendar, AbstractSpinControl, AbstractMenu, TextStyle, AbstractTextTimedMenu


def build_font(size, style):
    font = wx.Font(wx.FontInfo(size))
    if style is TextStyle.BOLD:
        font = font.Bold()
    elif style is TextStyle.ITALIC:
        font = font.Italic()
    elif style is TextStyle.BOLD_ITALIC:
        font = font.Bold().Italic()
    return font


class Widget(AbstractWidget):

    def enable(self, is_enabled):
        super().enable(is_enabled)
        self.Enable(self._is_enabled)

    def hide(self, is_hidden):
        super().hide(is_hidden)
        self.Show(not self._is_hidden)


class MouseEventsWidget(AbstractMouseEventsWidget, Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self.Bind(wx.EVT_RIGHT_DOWN, self._on_right_down)
        self.Bind(wx.EVT_RIGHT_UP, self._on_right_up)
        self.Bind(wx.EVT_MOUSEWHEEL, self._on_wheel)
        self.Bind(wx.EVT_MOTION, self._on_mouse_motion)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_mouse_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_mouse_leave)

    def _on_left_down(self, event):
        position = event.GetPosition().Get()
        self.on_left_down(self, position)

    def _on_left_up(self, event):
        position = event.GetPosition().Get()
        self.on_left_up(self, position)

    def _on_right_down(self, event):
        position = event.GetPosition().Get()
        self.on_right_down(self, position)

    def _on_right_up(self, event):
        position = event.GetPosition().Get()
        self.on_right_up(self, position)

    def _on_wheel(self, event):
        position = event.GetPosition().Get()
        direction = event.GetWheelRotation()
        self.on_wheel(self, position, direction)

    def _on_mouse_motion(self, event):
        position = event.GetPosition().Get()
        self.on_mouse_motion(self, position)

    def _on_mouse_enter(self, event):
        self.on_mouse_enter(self)

    def _on_mouse_leave(self, event):
        self.on_mouse_leave(self)


class LabelledWidget(AbstractLabelledWidget, Widget):

    @property
    def label(self):
        return super(LabelledWidget, LabelledWidget).label.__get__(self)

    @label.setter
    def label(self, label):
        super(LabelledWidget, LabelledWidget).label.__set__(self, label)
        self.SetLabel(super(LabelledWidget, LabelledWidget).label.__get__(self))


class Button(AbstractButton, LabelledWidget, wx.Button):

    def __init__(self, panel, **kwargs):
        wx.Button.__init__(self, panel)
        super().__init__(**kwargs)
        self.Bind(wx.EVT_BUTTON, self._on_click)

    def _on_click(self, event):
        self.on_click(self)


class CheckBox(AbstractCheckBox, LabelledWidget, wx.CheckBox):

    def __init__(self, panel, **kwargs):
        wx.CheckBox.__init__(self, panel)
        super().__init__(**kwargs)
        self.Bind(wx.EVT_CHECKBOX, self._on_click)

    def _on_click(self, event):
        self.on_click(self)

    @property
    def value(self):
        super(CheckBox, CheckBox).value.__set__(self, self.GetValue())
        return super(CheckBox, CheckBox).value.__get__(self)

    @value.setter
    def value(self, value):
        super(CheckBox, CheckBox).value.__set__(self, value)
        self.SetValue(super(CheckBox, CheckBox).value.__get__(self))


class RadioBox(AbstractRadioBox, LabelledWidget, wx.RadioBox):

    def __init__(self, panel, **kwargs):
        wx.RadioBox.__init__(self)
        self._created = False
        super().__init__(**kwargs)
        self.Create(panel, label=self._label, style=wx.RA_SPECIFY_ROWS, choices=self._choices)
        self._created = True
        self.Bind(wx.EVT_RADIOBOX, self._on_click)

    def _on_click(self, event):
        self.on_click(self)

    @property
    def selection(self):
        super(RadioBox, RadioBox).selection.__set__(self, self.GetSelection())
        return super(RadioBox, RadioBox).selection.__get__(self)

    @selection.setter
    def selection(self, selection):
        super(RadioBox, RadioBox).selection.__set__(self, selection)
        self.SetSelection(super(RadioBox, RadioBox).selection.__get__(self))

    def set_string(self, index, string):
        super().set_string(index, string)
        self.SetString(index, self._choices[index])

    @property
    def label(self):
        return super(LabelledWidget, LabelledWidget).label.__get__(self)

    @label.setter
    def label(self, label):
        super(LabelledWidget, LabelledWidget).label.__set__(self, label)
        if self._created:
            self.SetLabel(super(LabelledWidget, LabelledWidget).label.__get__(self))


def pil_2_wx(image):
    width, height = image.size
    if image.mode == 'RGBA':
        return wx.Bitmap.FromBufferAndAlpha(width, height, image.tobytes('raw', 'RGB'), image.tobytes('raw', 'A'))
    else:
        return wx.Bitmap.FromBuffer(width, height, image.tobytes())


class Bitmap(AbstractBitmap, MouseEventsWidget, wx.StaticBitmap):

    def __init__(self, panel, **kwargs):
        wx.StaticBitmap.__init__(self, panel)
        super().__init__(**kwargs)

    @property
    def bitmap(self):
        return super(Bitmap, Bitmap).bitmap.__get__(self)

    @bitmap.setter
    def bitmap(self, bitmap):
        super(Bitmap, Bitmap).bitmap.__set__(self, bitmap)
        if self.bitmap is not None:
            self.SetBitmap(pil_2_wx(self.bitmap))


class TextWidget(AbstractText):

    @property
    def font_style(self):
        return super(TextWidget, TextWidget).font_style.__get__(self)

    @font_style.setter
    def font_style(self, font_style):
        super(TextWidget, TextWidget).font_style.__set__(self, font_style)
        self.SetFont(build_font(self.font_size, self.font_style))

    @property
    def font_size(self):
        return super(TextWidget, TextWidget).font_size.__get__(self)

    @font_size.setter
    def font_size(self, font_size):
        super(TextWidget, TextWidget).font_size.__set__(self, font_size)
        self.SetFont(build_font(self.font_size, self.font_style))

    @property
    def foreground_color(self):
        return super(TextWidget, TextWidget).foreground_color.__get__(self)

    @foreground_color.setter
    def foreground_color(self, foreground_color):
        super(TextWidget, TextWidget).foreground_color.__set__(self, foreground_color)
        if self.foreground_color:
            self.SetForegroundColour(self.foreground_color)
        else:
            self.SetForegroundColour(wx.NullColour)

    @property
    def background_color(self):
        return super(TextWidget, TextWidget).background_color.__get__(self)

    @background_color.setter
    def background_color(self, background_color):
        super(TextWidget, TextWidget).background_color.__set__(self, background_color)
        if self.background_color:
            self.SetBackgroundColour(self.background_color)
        else:
            self.SetBackgroundColour(wx.NullColour)


class TextControl(TextWidget, LabelledWidget, wx.TextCtrl):

    def __init__(self, panel, **kwargs):
        wx.TextCtrl.__init__(self, panel)
        super().__init__(**kwargs)

    @property
    def label(self):
        super(TextControl, TextControl).label.__set__(self, self.GetValue())
        return super(TextControl, TextControl).label.__get__(self)

    @label.setter
    def label(self, label):
        super(TextControl, TextControl).label.__set__(self, label)
        self.SetValue(super(TextControl, TextControl).label.__get__(self))


class Text(TextWidget, MouseEventsWidget, LabelledWidget, wx.StaticText):

    def __init__(self, panel, **kwargs):
        wx.StaticText.__init__(self, panel)
        super().__init__(**kwargs)


class Calendar(AbstractCalendar, Widget, wx.adv.CalendarCtrl):

    def __init__(self, panel, **kwargs):
        wx.adv.CalendarCtrl.__init__(self, panel, style=wx.adv.CAL_MONDAY_FIRST)
        super().__init__(**kwargs)
        self.Bind(wx.adv.EVT_CALENDAR_SEL_CHANGED, self._on_date_changed)

    def _on_date_changed(self, event):
        self.on_date_changed(self)

    @property
    def lower_date(self):
        return super(Calendar, Calendar).lower_date.__get__(self)

    @lower_date.setter
    def lower_date(self, lower_date):
        super(Calendar, Calendar).lower_date.__set__(self, lower_date)
        self._set_date_range()

    @property
    def upper_date(self):
        return super(Calendar, Calendar).upper_date.__get__(self)

    @upper_date.setter
    def upper_date(self, upper_date):
        super(Calendar, Calendar).upper_date.__set__(self, upper_date)
        self._set_date_range()

    def _set_date_range(self):
        if self.lower_date is not None:
            date_as_tuple = self.lower_date.timetuple()
            wx_lower_date = wx.DateTime.FromDMY(date_as_tuple[2], date_as_tuple[1] - 1, date_as_tuple[0])
        else:
            wx_lower_date = wx.DefaultDateTime
        if self.upper_date is not None:
            date_as_tuple = self.upper_date.timetuple()
            wx_upper_date = wx.DateTime.FromDMY(date_as_tuple[2], date_as_tuple[1] - 1, date_as_tuple[0])
        else:
            wx_upper_date = wx.DefaultDateTime
        self.SetDateRange(lowerdate=wx_lower_date, upperdate=wx_upper_date)

    @property
    def selected_date(self):
        wx_date = self.GetDate()
        datetime_date = datetime.date(year=wx_date.year, month=wx_date.month + 1, day=wx_date.day)
        super(Calendar, Calendar).selected_date.__set__(self, datetime_date)
        return super(Calendar, Calendar).selected_date.__get__(self)

    @selected_date.setter
    def selected_date(self, date):
        super(Calendar, Calendar).selected_date.__set__(self, date)
        date_as_tuple = super(Calendar, Calendar).selected_date.__get__(self).timetuple()
        self.SetDate(wx.DateTime.FromDMY(date_as_tuple[2], date_as_tuple[1] - 1, date_as_tuple[0]))


class SpinControl(AbstractSpinControl, Widget, wx.SpinCtrl):

    def __init__(self, panel, **kwargs):
        wx.SpinCtrl.__init__(self, panel, style=wx.SP_ARROW_KEYS)
        super().__init__(**kwargs)
        self.Bind(wx.EVT_CHAR, lambda event: None)
        self.Bind(wx.EVT_SET_FOCUS, lambda event: None)
        self.Bind(wx.EVT_SPINCTRL, self._on_click)

    def _on_click(self, event):
        self.on_click(self)

    @property
    def min_value(self):
        return super(SpinControl, SpinControl).min_value.__get__(self)

    @min_value.setter
    def min_value(self, min_value):
        super(SpinControl, SpinControl).min_value.__set__(self, min_value)
        if self.min_value is not None:
            self.SetMin(self.min_value)

    @property
    def max_value(self):
        return super(SpinControl, SpinControl).max_value.__get__(self)

    @max_value.setter
    def max_value(self, max_value):
        super(SpinControl, SpinControl).max_value.__set__(self, max_value)
        if self.max_value is not None:
            self.SetMax(self.max_value)

    @property
    def value(self):
        super(SpinControl, SpinControl).value.__set__(self, self.GetValue())
        return super(SpinControl, SpinControl).value.__get__(self)

    @value.setter
    def value(self, value):
        super(SpinControl, SpinControl).value.__set__(self, value)
        self.SetValue(super(SpinControl, SpinControl).value.__get__(self))


class Menu(AbstractMenu, Widget, wx.Menu):

    def __init__(self, parent, **kwargs):
        wx.Menu.__init__(self)
        super().__init__(**kwargs)
        self._parent = parent
        self.Bind(wx.EVT_MENU_CLOSE, self._on_close)

    def _on_click(self, event):
        choice_id = event.GetId()
        self.on_click(self, choice_id)

    def pop_up(self):
        super().pop_up()
        self._parent.PopupMenu(self)
        self.Destroy()

    def _append_menubar(self, menubar, item, is_enabled, on_item_click):
        if item == self.SEPARATOR:
            return
        elif isinstance(item, Menu):
            item.build_menu(inherited_on_click=self.on_click)
            menubar.Append(item, item.label)
            menubar.EnableTop(menubar.GetMenuCount() - 1, is_enabled)
        else:
            entry = menubar.Append(wx.ID_ANY, item)
            if on_item_click is not None:
                self._parent.Bind(wx.EVT_MENU, lambda event: on_item_click(), entry)
            else:
                self._parent.Bind(wx.EVT_MENU, self._on_click, entry)
            self._return_items[entry.GetId()] = item
            self.Enable(entry.GetId(), is_enabled)

    def _append_menu(self, item, is_enabled, on_item_click):
        if item == self.SEPARATOR:
            entry = self.Append(wx.ID_SEPARATOR)
        elif isinstance(item, Menu):
            item.build_menu(inherited_on_click=self.on_click)
            entry = self.AppendSubMenu(item, item.label)
        else:
            entry = self.Append(wx.ID_ANY, item)
            if on_item_click is not None:
                self._parent.Bind(wx.EVT_MENU, lambda event: on_item_click(), entry)
            else:
                self._parent.Bind(wx.EVT_MENU, self._on_click, entry)
            self._return_items[entry.GetId()] = item
        self.Enable(entry.GetId(), is_enabled)

    def _on_close(self, event):
        self.on_close(self)


class TextTimedMenu(AbstractTextTimedMenu, wx.PopupWindow):

    def __init__(self, parent, **kwargs):
        wx.PopupWindow.__init__(self, parent)
        super().__init__(**kwargs)

        self._panel = wx.Panel(self)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._panel.SetSizer(self._sizer)
        self._frame_sizer = wx.BoxSizer(wx.VERTICAL)
        self._frame_sizer.Add(self._panel)
        self.Bind(wx.EVT_CLOSE, self._on_close)

    def pop_up(self, modal=False):
        super().pop_up()
        self.SetSizerAndFit(self._frame_sizer)
        self.Position(wx.GetMousePosition(), (10, 10))
        self.make_modal(modal)
        self.Show()

    def make_modal(self, modal):
        if modal and not hasattr(self, '_disabler'):
            self._disabler = wx.WindowDisabler(self)
        if not modal and hasattr(self, '_disabler'):
            del self._disabler

    def _create_text(self, label):
        if label == self.SEPARATOR:
            label = ""
        # It is necessary to put the Text inside a wx.Panel,
        # because under Linux the wx.StaticText
        # does not receive enter and leave events
        text_panel = wx.Panel(self._panel)
        text = Text(text_panel, label=label)
        text_panel.Bind(wx.EVT_ENTER_WINDOW, text._on_mouse_enter)
        text_panel.Bind(wx.EVT_LEAVE_WINDOW, text._on_mouse_leave)
        self._sizer.Add(text_panel, flag=wx.EXPAND)
        return text

    def _set_normal_color(self, text):
        super()._set_normal_color(text)
        panel = text.GetParent()
        panel.SetForegroundColour(self._FOREGROUND_NORMAL_COLOR)
        panel.SetBackgroundColour(self._BACKGROUND_NORMAL_COLOR)

    def _set_highlight_color(self, text):
        super()._set_highlight_color(text)
        panel = text.GetParent()
        panel.SetForegroundColour(self._FOREGROUND_HIGHLIGHT_COLOR)
        panel.SetBackgroundColour(self._BACKGROUND_HIGHLIGHT_COLOR)

    def _set_disabled_color(self, text):
        super()._set_disabled_color(text)
        panel = text.GetParent()
        panel.SetForegroundColour(self._FOREGROUND_DISABLED_COLOR)
        panel.SetBackgroundColour(self._BACKGROUND_DISABLED_COLOR)

    def _close(self):
        super()._close()
        self.make_modal(False)
        self.Close()
        wx.CallAfter(self.Destroy)

    def _on_mouse_enter_item(self, obj):
        super()._on_mouse_enter_item(obj)
        self.Refresh()

    def _on_mouse_leave_item(self, obj):
        super()._on_mouse_leave_item(obj)
        self.Refresh()

    def _on_close(self, event):
        self.on_close(self)

