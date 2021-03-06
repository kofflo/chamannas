import tkinter
import tkinter.font
import tkinter.ttk
import tkcalendar
from tkinter import DISABLED, NORMAL, END

from PIL import ImageTk
from threading import Timer

from src.gui_library.abstract.widgets import AbstractWidget, AbstractMouseEventsWidget, AbstractLabelledWidget, \
    AbstractButton, AbstractCheckBox, AbstractRadioBox, AbstractBitmap, \
    AbstractText, AbstractCalendar, AbstractSpinControl, AbstractMenu, TextStyle, AbstractTextTimedMenu
from src.gui_library.tk import ttk_style


def rgb2hex(r, g, b, *args):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def build_font(size, style):
    if style is TextStyle.BOLD:
        font = tkinter.font.Font(size=size, weight='bold')
    elif style is TextStyle.ITALIC:
        font = tkinter.font.Font(size=size, slant='italic')
    elif style is TextStyle.BOLD_ITALIC:
        font = tkinter.font.Font(size=size, weight='bold', slant='italic')
    else:
        font = tkinter.font.Font(size=size)
    return font


class Widget(AbstractWidget):

    def __init__(self, **kwargs):
        self._widget = None
        super().__init__(**kwargs)

    def __getattr__(self, item):
        if '_widget' in self.__dict__ and self._widget is not None:
            return getattr(self._widget, item)
        else:
            return None

    def __setattr__(self, key, value):
        if hasattr(self, key) or self._widget is None:
            super().__setattr__(key, value)
        else:
            setattr(self._widget, key, value)

    def enable(self, is_enabled):
        super().enable(is_enabled)
        if self._widget is not None:
            if self._is_enabled:
                self.configure(state=NORMAL)
            else:
                self.configure(state=DISABLED)

    def hide(self, is_hidden):
        super().hide(is_hidden)
        if self._widget is not None:
            if self._is_hidden:
                self.grid_remove()
            else:
                self.grid()

    def set_frame(self, frame):
        if self._is_enabled:
            self.configure(state=NORMAL)
        else:
            self.configure(state=DISABLED)
        # TODO with hide!


class MouseEventsWidget(AbstractMouseEventsWidget, Widget):

    def set_frame(self, frame):
        self.bind('<Button-1>', self._on_left_down)
        self.bind('<ButtonRelease-1>', self._on_left_up)
        self.bind('<Button-3>', self._on_right_down)
        self.bind('<ButtonRelease-3>', self._on_right_up)
        self.bind('<MouseWheel>', self._on_wheel)
        self.bind('<Motion>', self._on_mouse_motion)
        self.bind('<Enter>', self._on_mouse_enter)
        self.bind('<Leave>', self._on_mouse_leave)
        super().set_frame(frame)

    def _on_left_down(self, event):
        position = event.x, event.y
        self.on_left_down(self, position)

    def _on_left_up(self, event):
        position = event.x, event.y
        self.on_left_up(self, position)

    def _on_right_down(self, event):
        position = event.x, event.y
        self.on_right_down(self, position)

    def _on_right_up(self, event):
        position = event.x, event.y
        self.on_right_up(self, position)

    def _on_wheel(self, event):
        position = event.x, event.y
        direction = event.delta
        self.on_wheel(self, position, direction)

    def _on_mouse_motion(self, event):
        position = event.x, event.y
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
        if self._widget is not None:
            self.configure(text=super(LabelledWidget, LabelledWidget).label.__get__(self))
            if isinstance(self._widget, tkinter.ttk.Checkbutton):
                self.state(['!alternate'])

    def set_frame(self, frame):
        self.configure(text=super(LabelledWidget, LabelledWidget).label.__get__(self))
        super().set_frame(frame)
        if isinstance(self._widget, tkinter.ttk.Checkbutton):
            self.state(['!alternate'])


class Button(AbstractButton, LabelledWidget):

    def __init__(self, panel, **kwargs):
        super().__init__(**kwargs)

    def _on_click(self):
        self.on_click(self)

    def set_frame(self, frame):
        self._widget = tkinter.ttk.Button(frame, command=self._on_click)
        super().set_frame(frame)


class CheckBox(AbstractCheckBox, LabelledWidget):

    def __init__(self, panel, **kwargs):
        super().__init__(**kwargs)

    def _on_click(self):
        self.on_click(self)

    def set_frame(self, frame):
        self._widget = tkinter.ttk.Checkbutton(frame, command=self._on_click)
        if super(CheckBox, CheckBox).value.__get__(self):
            self.state(['selected'])
        else:
            self.state(['!selected'])
        super().set_frame(frame)

    @property
    def value(self):
        if self._widget is not None:
            state = 'selected' in self.state()
            super(CheckBox, CheckBox).value.__set__(self, state)
        return super(CheckBox, CheckBox).value.__get__(self)

    @value.setter
    def value(self, value):
        super(CheckBox, CheckBox).value.__set__(self, value)
        if self._widget is not None:
            if super(CheckBox, CheckBox).value.__get__(self):
                self.state(['selected'])
            else:
                self.state(['!selected'])


class RadioBox(AbstractRadioBox, Widget):

    def __init__(self, panel, **kwargs):
        super().__init__(**kwargs)
        self._var = tkinter.IntVar()
        self._rb = []

    def set_frame(self, frame):
        self._widget = tkinter.Frame(frame)
        for index, choice in enumerate(self._choices):
            rb = tkinter.ttk.Radiobutton(self._widget, text=choice, value=index, variable=self._var,
                                         command=self._on_click)
            rb.pack(fill='x')
            self._rb.append(rb)
        self._var.set(super(RadioBox, RadioBox).selection.__get__(self))
        for index in range(len(self._choices)):
            self._rb[index].configure(text=self._choices[index])
        super().set_frame(frame)

    def _on_click(self):
        self.on_click(self)

    @property
    def selection(self):
        if self._widget is not None:
            super(RadioBox, RadioBox).selection.__set__(self, self._var.get())
        return super(RadioBox, RadioBox).selection.__get__(self)

    @selection.setter
    def selection(self, selection):
        super(RadioBox, RadioBox).selection.__set__(self, selection)
        if self._widget is not None:
            self._var.set(super(RadioBox, RadioBox).selection.__get__(self))

    def set_string(self, index, string):
        super().set_string(index, string)
        if self._widget is not None:
            self._rb[index].configure(text=self._choices[index])

    def configure(self, *args, **kwargs):
        for rb in self._rb:
            rb.configure(*args, **kwargs)


class Bitmap(AbstractBitmap, MouseEventsWidget, Widget):

    def __init__(self, panel, **kwargs):
        super().__init__(**kwargs)
        self._tk_image = None

    def set_frame(self, frame):
        self._widget = tkinter.ttk.Label(frame)
        if self.bitmap is not None:
            self._tk_image = ImageTk.PhotoImage(self.bitmap)
            self.configure(image=self._tk_image)
        super().set_frame(frame)

    @property
    def bitmap(self):
        return super(Bitmap, Bitmap).bitmap.__get__(self)

    @bitmap.setter
    def bitmap(self, bitmap):
        super(Bitmap, Bitmap).bitmap.__set__(self, bitmap)
        if self.bitmap is not None:
            self._tk_image = ImageTk.PhotoImage(self.bitmap)
            if self._widget is not None:
                self.configure(image=self._tk_image)


class TextWidget(AbstractText, Widget):

    def _get_style_id(self):
        if self._widget is not None:
            if isinstance(self._widget, tkinter.ttk.Label):
                return 'TLabel'
            elif isinstance(self._widget, tkinter.ttk.Entry):
                return 'TEntry'
            else:
                raise TypeError('Widget does not support TTK style')
        else:
            return None

    def set_frame(self, frame):
        self.configure(font=build_font(self.font_size, self.font_style))
        self.configure(font=build_font(self.font_size, self.font_style))
        if self.foreground_color:
            ttk_style.configure(str(id(self)) + '.' + self._get_style_id(), foreground=rgb2hex(*self.foreground_color))
        else:
            default_fg = ttk_style.lookup(self._get_style_id(), 'foreground')
            ttk_style.configure(str(id(self)) + '.' + self._get_style_id(), foreground=default_fg)
        if self.background_color:
            ttk_style.configure(str(id(self)) + '.' + self._get_style_id(), background=rgb2hex(*self.background_color))
        else:
            default_bg = ttk_style.lookup(self._get_style_id(), 'background')
            ttk_style.configure(str(id(self)) + '.' + self._get_style_id(), background=default_bg)
        self.configure(style=str(id(self)) + '.' + self._get_style_id())
        super().set_frame(frame)

    @property
    def font_style(self):
        return super(TextWidget, TextWidget).font_style.__get__(self)

    @font_style.setter
    def font_style(self, font_style):
        super(TextWidget, TextWidget).font_style.__set__(self, font_style)
        if self._widget is not None:
            self.configure(font=build_font(self.font_size, self.font_style))

    @property
    def font_size(self):
        return super(TextWidget, TextWidget).font_size.__get__(self)

    @font_size.setter
    def font_size(self, font_size):
        super(TextWidget, TextWidget).font_size.__set__(self, font_size)
        if self._widget is not None:
            self.configure(font=build_font(self.font_size, self.font_style))

    @property
    def foreground_color(self):
        return super(TextWidget, TextWidget).foreground_color.__get__(self)

    @foreground_color.setter
    def foreground_color(self, foreground_color):
        super(TextWidget, TextWidget).foreground_color.__set__(self, foreground_color)
        if self._widget is not None:
            if self.foreground_color:
                ttk_style.configure(str(id(self)) + '.' + self._get_style_id(),
                                    foreground=rgb2hex(*self.foreground_color))
            else:
                default_fg = ttk_style.lookup(self._get_style_id(), 'foreground')
                ttk_style.configure(str(id(self)) + '.' + self._get_style_id(), foreground=default_fg)
            self.configure(style=str(id(self)) + '.' + self._get_style_id())

    @property
    def background_color(self):
        return super(TextWidget, TextWidget).background_color.__get__(self)

    @background_color.setter
    def background_color(self, background_color):
        super(TextWidget, TextWidget).background_color.__set__(self, background_color)
        if self._widget is not None:
            if self.background_color:
                ttk_style.configure(str(id(self)) + '.' + self._get_style_id(),
                                    background=rgb2hex(*self.background_color))
            else:
                default_bg = ttk_style.lookup(self._get_style_id(), 'background')
                ttk_style.configure(str(id(self)) + '.' + self._get_style_id(), background=default_bg)
            self.configure(style=str(id(self)) + '.' + self._get_style_id())


class TextControl(TextWidget):

    def __init__(self, panel, **kwargs):
        super().__init__(**kwargs)

    def set_frame(self, frame):
        self._widget = tkinter.ttk.Entry(frame)
        self.insert(0, super(TextControl, TextControl).label.__get__(self))
        super().set_frame(frame)

    @property
    def label(self):
        if self._widget is not None:
            super(TextControl, TextControl).label.__set__(self, self.get())
        return super(TextControl, TextControl).label.__get__(self)

    @label.setter
    def label(self, label):
        super(TextControl, TextControl).label.__set__(self, label)
        if self._widget is not None:
            self.delete(0, END)
            self.insert(0, super(TextControl, TextControl).label.__get__(self))


class Text(TextWidget, MouseEventsWidget, LabelledWidget):

    def __init__(self, panel, **kwargs):
        super().__init__(**kwargs)

    def set_frame(self, frame):
        self._widget = tkinter.ttk.Label(frame)
        super().set_frame(frame)


class Calendar(AbstractCalendar, Widget):

    def __init__(self, panel, **kwargs):
        super().__init__(**kwargs)

    def set_frame(self, frame):
        self._widget = tkcalendar.Calendar(frame, firstweekday='monday')
        self.bind('<<CalendarSelected>>', self._on_date_changed)
        self.configure(mindate=super(Calendar, Calendar).lower_date.__get__(self))
        self.configure(maxdate=super(Calendar, Calendar).upper_date.__get__(self))
        super(Calendar, Calendar).selected_date.__set__(self, self.selection_get())
        super().set_frame(frame)

    def _on_date_changed(self, event):
        self.on_date_changed(self)

    @property
    def lower_date(self):
        return super(Calendar, Calendar).lower_date.__get__(self)

    @lower_date.setter
    def lower_date(self, lower_date):
        super(Calendar, Calendar).lower_date.__set__(self, lower_date)
        if self._widget is not None:
            self.configure(mindate=super(Calendar, Calendar).lower_date.__get__(self))

    @property
    def upper_date(self):
        return super(Calendar, Calendar).upper_date.__get__(self)

    @upper_date.setter
    def upper_date(self, upper_date):
        super(Calendar, Calendar).upper_date.__set__(self, upper_date)
        if self._widget is not None:
            self.configure(maxdate=super(Calendar, Calendar).upper_date.__get__(self))

    @property
    def selected_date(self):
        if self._widget is not None:
            super(Calendar, Calendar).selected_date.__set__(self, self.selection_get())
        return super(Calendar, Calendar).selected_date.__get__(self)

    @selected_date.setter
    def selected_date(self, date):
        super(Calendar, Calendar).selected_date.__set__(self, date)
        if self._widget is not None:
            self.selection_set(super(Calendar, Calendar).selected_date.__get__(self))

    def set_language(self, language):
        if self._widget is not None:
            if language == 'English':
                self.configure(locale='en_UK')
            elif language == 'Italiano':
                self.configure(locale='it_IT')
            elif language == 'Deutsch':
                self.configure(locale='de_DE')
            else:
                self.configure(locale='en_UK')


class SpinControl(AbstractSpinControl, Widget):

    def __init__(self, panel, **kwargs):
        super().__init__(**kwargs)

    def set_frame(self, frame):
        self._widget = tkinter.ttk.Spinbox(frame, command=self._on_click)
        self.insert(0, super(SpinControl, SpinControl).value.__get__(self))
        self.state(['readonly'])
        if self.min_value is not None:
            self.configure(from_=self.min_value)
        if self.max_value is not None:
            self.configure(to=self.max_value)
        super().set_frame(frame)

    def _on_click(self):
        self.on_click(self)

    @property
    def min_value(self):
        return super(SpinControl, SpinControl).min_value.__get__(self)

    @min_value.setter
    def min_value(self, min_value):
        super(SpinControl, SpinControl).min_value.__set__(self, min_value)
        if self._widget is not None:
            if self.min_value is not None:
                self.configure(from_=self.min_value)

    @property
    def max_value(self):
        return super(SpinControl, SpinControl).max_value.__get__(self)

    @max_value.setter
    def max_value(self, max_value):
        super(SpinControl, SpinControl).max_value.__set__(self, max_value)
        if self._widget is not None:
            if self.max_value is not None:
                self.configure(to=self.max_value)

    @property
    def value(self):
        if self._widget is not None:
            super(SpinControl, SpinControl).value.__set__(self, int(self.get()))
        return super(SpinControl, SpinControl).value.__get__(self)

    @value.setter
    def value(self, value):
        super(SpinControl, SpinControl).value.__set__(self, value)
        if self._widget is not None:
            self.state(['!readonly'])
            self.delete(0, END)
            self.insert(0, super(SpinControl, SpinControl).value.__get__(self))
            self.state(['readonly'])


class Menu(AbstractMenu, Widget):

    _TIMER_FORCE_CLOSE = 0.1

    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self._parent = parent
        self._wait_var = tkinter.IntVar()
        self._wait_var.set(0)

    def _on_click(self, item):
        self.on_click(self, item)

    def build_menu(self, menubar=None, inherited_on_click=None):
        if self._widget is None:
            self._widget = tkinter.Menu(self._parent.toplevel, tearoff=0)
        super().build_menu(menubar, inherited_on_click)

    def pop_up(self):
        if self._widget is not None:
            self.delete(0, END)
        super().pop_up()
        self.tk_popup(self._parent.toplevel.winfo_pointerx(), self._parent.toplevel.winfo_pointery())
        self.on_close(self)
        # Start a timer to force the wait variable to change
        # even if the menu has been closed without clicking on it
        Timer(self._TIMER_FORCE_CLOSE, self._force_close).start()
        # Wait until the item click function has been executed or the timer has expired
        self._widget.wait_variable(self._wait_var)

    def _force_close(self):
        self._wait_var.set(1)

    def _append_menubar(self, menubar, item, is_enabled, on_item_click):
        if item == self.SEPARATOR:
            return
        menubar._append_menu(item, is_enabled, on_item_click)

    def _append_menu(self, item, is_enabled, on_item_click):
        if item == self.SEPARATOR:
            self.add_separator()
        elif isinstance(item, Menu):
            item.build_menu(inherited_on_click=self.on_click)
            self.add_cascade(label=item.label, menu=item._widget)
        else:
            ampersand = item.find('&')
            if ampersand != -1:
                shortcut_key = item[ampersand + 1].lower()
                item = item[:ampersand] + item[ampersand + 1:]
            else:
                shortcut_key = None
            tab = item.find('\t')
            if tab != -1:
                accelerator = item[tab + 1:]
                item = item[:tab]
            else:
                accelerator = None
            if on_item_click is None:
                def _on_item_click():
                    self._on_click(item)
                    self._wait_var.set(1)
            else:
                def _on_item_click():
                    on_item_click()
                    self._wait_var.set(1)
            self.add_command(label=item, command=_on_item_click, underline=ampersand, accelerator=accelerator)
            if shortcut_key:
                self._parent.toplevel.bind_all(f'<Alt-{shortcut_key}>', lambda event: _on_item_click())
            self._return_items[item] = item
        if not is_enabled:
            self.entryconfig(item, state="disabled")


class TextTimedMenu(AbstractTextTimedMenu, Widget):

    def __init__(self, parent, **kwargs):
        self._parent = parent
        super().__init__(**kwargs)

    def set_frame(self, frame):
        self._widget = tkinter.Toplevel(frame)
        self._widget.overrideredirect(True)
        self._widget.protocol('WM_DELETE_WINDOW', lambda: self.on_close(self))

    def pop_up(self, modal=False):
        # TODO MODAL (does it make sense????)
        self.set_frame(self._parent.toplevel)
        super().pop_up()
        x_mouse = self._parent.toplevel.winfo_pointerx()
        y_mouse = self._parent.toplevel.winfo_pointery()
        self._widget.geometry(f"+{x_mouse + 10}+{y_mouse + 10}")
        self._widget.bind('<<CloseWidget>>', self._on_close_signal)

    def _create_text(self, label):
        if label == self.SEPARATOR:
            label = ""
        text = Text(None, label=label)
        text.set_frame(self._widget)
        text.label = label
        text.pack(expand=True, fill='x')
        return text

    def _close(self):
        super()._close()
        self._widget.event_generate('<<CloseWidget>>')

    def _on_mouse_enter_item(self, obj):
        super()._on_mouse_enter_item(obj)

    def _on_mouse_leave_item(self, obj):
        super()._on_mouse_leave_item(obj)

    def _on_close_signal(self, event):
        self.on_close(self)
        self._widget.destroy()
