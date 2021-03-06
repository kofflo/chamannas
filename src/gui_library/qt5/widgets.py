import PySide2
import PySide2.QtWidgets
import PySide2.QtCore
import PySide2.QtGui

from PIL.ImageQt import ImageQt

from src.gui_library.abstract.widgets import AbstractWidget, AbstractMouseEventsWidget, AbstractLabelledWidget, \
    AbstractButton, AbstractCheckBox, AbstractRadioBox, AbstractBitmap, \
    AbstractText, AbstractCalendar, AbstractSpinControl, AbstractMenu, TextStyle, AbstractTextTimedMenu, \
    AbstractBoxLayout, AbstractGridLayout, Align


def build_font(size, style):
    font = PySide2.QtGui.QFont('Helvetica', size)
    if style is TextStyle.BOLD:
        font.setBold(True)
    elif style is TextStyle.ITALIC:
        font.setItalic(True)
    elif style is TextStyle.BOLD_ITALIC:
        font.setBold(True)
        font.setItalic(True)
    return font


class Widget(AbstractWidget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setMouseTracking(True)

    def enable(self, is_enabled):
        super().enable(is_enabled)
        self.setEnabled(self._is_enabled)

    def hide(self, is_hidden):
        super().hide(is_hidden)
        self.setVisible(not self._is_hidden)


class MouseEventsWidget(AbstractMouseEventsWidget, Widget):

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        q_position = event.localPos()
        position = q_position.x(), q_position.y()
        button = event.button()
        if button is PySide2.QtCore.Qt.LeftButton:
            self.on_left_down(self, position)
        elif button is PySide2.QtCore.Qt.RightButton:
            self.on_right_down(self, position)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        q_position = event.localPos()
        position = q_position.x(), q_position.y()
        button = event.button()
        if button is PySide2.QtCore.Qt.LeftButton:
            self.on_left_up(self, position)
        elif button is PySide2.QtCore.Qt.RightButton:
            self.on_right_up(self, position)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        q_position = event.localPos()
        position = q_position.x(), q_position.y()
        self.on_mouse_motion(self, position)

    def wheelEvent(self, event):
        super().wheelEvent(event)
        q_position = event.position()
        position = q_position.x(), q_position.y()
        q_direction = event.angleDelta()
        direction = q_direction.y()
        self.on_wheel(self, position, direction)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.on_mouse_enter(self)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.on_mouse_leave(self)


class LabelledWidget(AbstractLabelledWidget, Widget):

    @property
    def label(self):
        return super(LabelledWidget, LabelledWidget).label.__get__(self)

    @label.setter
    def label(self, label):
        super(LabelledWidget, LabelledWidget).label.__set__(self, label)
        self.setText(super(LabelledWidget, LabelledWidget).label.__get__(self))


class Button(AbstractButton, LabelledWidget, PySide2.QtWidgets.QPushButton):

    def __init__(self, panel, **kwargs):
        PySide2.QtWidgets.QPushButton.__init__(self, parent=panel)
        super().__init__(**kwargs)
        self.clicked.connect(self._on_click)

    def _on_click(self):
        self.on_click(self)


class CheckBox(AbstractCheckBox, LabelledWidget, PySide2.QtWidgets.QCheckBox):

    def __init__(self, panel, **kwargs):
        PySide2.QtWidgets.QCheckBox.__init__(self, parent=panel)
        super().__init__(**kwargs)
        self.stateChanged.connect(self._on_click)

    def _on_click(self):
        self.on_click(self)

    @property
    def value(self):
        super(CheckBox, CheckBox).value.__set__(self, self.isChecked())
        return super(CheckBox, CheckBox).value.__get__(self)

    @value.setter
    def value(self, value):
        super(CheckBox, CheckBox).value.__set__(self, value)
        self.blockSignals(True)
        self.setChecked(super(CheckBox, CheckBox).value.__get__(self))
        self.blockSignals(False)


class RadioBox(AbstractRadioBox, PySide2.QtWidgets.QGroupBox):

    def __init__(self, panel, **kwargs):
        PySide2.QtWidgets.QGroupBox.__init__(self, parent=panel)
        super().__init__(**kwargs)
        self._button_group = PySide2.QtWidgets.QButtonGroup(parent=panel)

        vbox = PySide2.QtWidgets.QVBoxLayout()
        for choice in self._choices:
            button = PySide2.QtWidgets.QRadioButton(choice, parent=panel)
            self._button_group.addButton(button)
            vbox.addWidget(button)
        self.selection = 0

        self.setLayout(vbox)
        self._button_group.buttonClicked.connect(self._on_click)

    def _on_click(self):
        self.on_click(self)

    @property
    def label(self):
        return super(RadioBox, RadioBox).label.__get__(self)

    @label.setter
    def label(self, label):
        super(RadioBox, RadioBox).label.__set__(self, label)
        self.setTitle(super(RadioBox, RadioBox).label.__get__(self))

    @property
    def selection(self):
        for index, button in enumerate(self._button_group.buttons()):
            if button.isChecked():
                break
        super(RadioBox, RadioBox).selection.__set__(self, index)
        return super(RadioBox, RadioBox).selection.__get__(self)

    @selection.setter
    def selection(self, selection):
        super(RadioBox, RadioBox).selection.__set__(self, selection)
        self._button_group.buttons()[super(RadioBox, RadioBox).selection.__get__(self)].setChecked(True)

    def set_string(self, index, string):
        super().set_string(index, string)
        self._button_group.buttons()[index].setText(self._choices[index])


class Bitmap(AbstractBitmap, MouseEventsWidget, PySide2.QtWidgets.QLabel):

    def __init__(self, panel, **kwargs):
        PySide2.QtWidgets.QLabel.__init__(self, panel)
        self._image_qt = None
        super().__init__(**kwargs)

    @property
    def bitmap(self):
        return super(Bitmap, Bitmap).bitmap.__get__(self)

    @bitmap.setter
    def bitmap(self, bitmap):
        super(Bitmap, Bitmap).bitmap.__set__(self, bitmap)
        if self.bitmap is not None:
            self._image_qt = ImageQt(self.bitmap)
            self.setPixmap(PySide2.QtGui.QPixmap.fromImage(self._image_qt))
            self.setFixedSize(self._image_qt.size())


def rgb2hex(r, g, b, *args):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


class TextWidget(AbstractText):

    @property
    def font_style(self):
        return super(TextWidget, TextWidget).font_style.__get__(self)

    @font_style.setter
    def font_style(self, font_style):
        super(TextWidget, TextWidget).font_style.__set__(self, font_style)
        self.setFont(build_font(self.font_size, self.font_style))

    @property
    def font_size(self):
        return super(TextWidget, TextWidget).font_size.__get__(self)

    @font_size.setter
    def font_size(self, font_size):
        super(TextWidget, TextWidget).font_size.__set__(self, font_size)
        self.setFont(build_font(self.font_size, self.font_style))

    @property
    def foreground_color(self):
        return super(TextWidget, TextWidget).foreground_color.__get__(self)

    @foreground_color.setter
    def foreground_color(self, foreground_color):
        super(TextWidget, TextWidget).foreground_color.__set__(self, foreground_color)
        self._set_style_sheet()

    @property
    def background_color(self):
        return super(TextWidget, TextWidget).background_color.__get__(self)

    @background_color.setter
    def background_color(self, background_color):
        super(TextWidget, TextWidget).background_color.__set__(self, background_color)
        self._set_style_sheet()

    def _set_style_sheet(self):
        if self.foreground_color:
            color_string = rgb2hex(*self.foreground_color)
            foreground_style = 'color : %s;' % color_string
        else:
            foreground_style = ''
        if self.background_color:
            color_string = rgb2hex(*self.background_color)
            background_style = 'background-color : %s;' % color_string
        else:
            background_style = ''
        self.setStyleSheet('QLabel { %s %s }' % (foreground_style, background_style))


class TextControl(TextWidget, LabelledWidget, PySide2.QtWidgets.QLineEdit):

    def __init__(self, panel, **kwargs):
        PySide2.QtWidgets.QLineEdit.__init__(self, panel)
        super().__init__(**kwargs)

    @property
    def label(self):
        super(TextControl, TextControl).label.__set__(self, self.text())
        return super(TextControl, TextControl).label.__get__(self)

    @label.setter
    def label(self, label):
        super(TextControl, TextControl).label.__set__(self, label)
        self.setText(super(TextControl, TextControl).label.__get__(self))


class Text(TextWidget, LabelledWidget, MouseEventsWidget, PySide2.QtWidgets.QLabel):

    def __init__(self, panel, **kwargs):
        PySide2.QtWidgets.QLabel.__init__(self, panel)
        super().__init__(**kwargs)


class Calendar(AbstractCalendar, Widget, PySide2.QtWidgets.QCalendarWidget):

    def __init__(self, panel, **kwargs):
        PySide2.QtWidgets.QCalendarWidget.__init__(self, panel)
        self.setFirstDayOfWeek(PySide2.QtCore.Qt.Monday)
        self.clicked.connect(self._on_date_changed)
        self.setHorizontalHeaderFormat(self.SingleLetterDayNames)
        self.setVerticalHeaderFormat(self.NoVerticalHeader)
        self.setGridVisible(True)
        super().__init__(**kwargs)

    def _on_date_changed(self, event):
        self.on_date_changed(self)

    def paintCell(self, painter, rect, date):
        if not self.minimumDate() <= date <= self.maximumDate():
            painter.setBrush(PySide2.QtGui.QBrush(PySide2.QtCore.Qt.lightGray))
            painter.setPen(PySide2.QtGui.QPen(PySide2.QtCore.Qt.lightGray))
            painter.drawRect(rect)
            painter.setPen(PySide2.QtGui.QPen(PySide2.QtCore.Qt.gray))
            painter.drawText(rect, PySide2.QtCore.Qt.AlignHCenter | PySide2.QtCore.Qt.AlignVCenter, str(date.day()))
        else:
            super().paintCell(painter, rect, date)

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
            qt_lower_date = PySide2.QtCore.QDate(date_as_tuple[0], date_as_tuple[1], date_as_tuple[2])
        else:
            qt_lower_date = PySide2.QtCore.QDate(1, 1, 1)
        if self.upper_date is not None:
            date_as_tuple = self.upper_date.timetuple()
            qt_upper_date = PySide2.QtCore.QDate(date_as_tuple[0], date_as_tuple[1], date_as_tuple[2])
        else:
            qt_upper_date = PySide2.QtCore.QDate(10000, 1, 1)
        self.setDateRange(qt_lower_date, qt_upper_date)

    @property
    def selected_date(self):
        qt_date = self.selectedDate()
        datetime_date = qt_date.toPython()
        super(Calendar, Calendar).selected_date.__set__(self, datetime_date)
        return super(Calendar, Calendar).selected_date.__get__(self)

    @selected_date.setter
    def selected_date(self, date):
        super(Calendar, Calendar).selected_date.__set__(self, date)
        date_as_tuple = super(Calendar, Calendar).selected_date.__get__(self).timetuple()
        self.setSelectedDate(PySide2.QtCore.QDate(date_as_tuple[0], date_as_tuple[1], date_as_tuple[2]))

    def set_language(self, language):
        if language == 'English':
            self.setLocale(PySide2.QtCore.QLocale.English)
        elif language == 'Italiano':
            self.setLocale(PySide2.QtCore.QLocale.Italian)
        elif language == 'Deutsch':
            self.setLocale(PySide2.QtCore.QLocale.German)
        else:
            self.setLocale(PySide2.QtCore.QLocale.English)


class SpinControl(AbstractSpinControl, Widget, PySide2.QtWidgets.QSpinBox):

    def __init__(self, panel, **kwargs):
        PySide2.QtWidgets.QSpinBox.__init__(self, panel)
        super().__init__(**kwargs)
        self.valueChanged.connect(self._on_click)
        self.lineEdit().setReadOnly(True)

    def _on_click(self):
        self.on_click(self)

    @property
    def min_value(self):
        return super(SpinControl, SpinControl).min_value.__get__(self)

    @min_value.setter
    def min_value(self, min_value):
        super(SpinControl, SpinControl).min_value.__set__(self, min_value)
        if self.min_value is not None:
            self.setMinimum(self.min_value)

    @property
    def max_value(self):
        return super(SpinControl, SpinControl).max_value.__get__(self)

    @max_value.setter
    def max_value(self, max_value):
        super(SpinControl, SpinControl).max_value.__set__(self, max_value)
        if self.max_value is not None:
            self.setMaximum(self.max_value)

    @property
    def value(self):
        super(SpinControl, SpinControl).value.__set__(self, PySide2.QtWidgets.QSpinBox.value(self))
        return super(SpinControl, SpinControl).value.__get__(self)

    @value.setter
    def value(self, value):
        super(SpinControl, SpinControl).value.__set__(self, value)
        self.setValue(super(SpinControl, SpinControl).value.__get__(self))


class Menu(AbstractMenu, Widget, PySide2.QtWidgets.QMenu):

    def __init__(self, parent, **kwargs):
        PySide2.QtWidgets.QMenu.__init__(self)
        super().__init__(**kwargs)
        self._parent = parent

    def _on_click(self, entry):
        self.on_click(self, entry)

    def pop_up(self, modal=True):
        super().pop_up()
        if modal:
            self.exec_(PySide2.QtGui.QCursor.pos())
        else:
            self._parent.activateWindow()
            self.popup(PySide2.QtGui.QCursor.pos())

    def _append_menubar(self, menubar, item, is_enabled, on_item_click):
        if item is None:
            return
        elif isinstance(item, Menu):
            item.build_menu(inherited_on_click=self.on_click)
            item.setTitle(item.label)
            menubar.addMenu(item)
            entry = item
        else:
            entry = PySide2.QtWidgets.QAction(item, self)
            ampersand = item.find('&')
            if ampersand != -1:
                shortcut_key = item[ampersand + 1]
                entry.setShortcut('Alt+' + shortcut_key)
            menubar.addAction(entry)
            if on_item_click is not None:
                entry.triggered.connect(lambda checked=False: on_item_click())
            else:
                entry.triggered.connect(lambda checked=False, e=entry: self._on_click(e))
            self._return_items[entry] = item
        entry.setEnabled(is_enabled)

    def _append_menu(self, item, is_enabled, on_item_click):
        if item == self.SEPARATOR:
            entry = self.addSeparator()
        elif isinstance(item, Menu):
            item.build_menu(inherited_on_click=self.on_click)
            item.setTitle(item.label)
            self.addMenu(item)
            entry = item
        else:
            entry = PySide2.QtWidgets.QAction(item, self)
            ampersand = item.find('&')
            if ampersand != -1:
                shortcut_key = item[ampersand + 1]
                entry.setShortcut('Alt+' + shortcut_key)
            self.addAction(entry)
            if on_item_click is not None:
                entry.triggered.connect(lambda checked=False: on_item_click())
            else:
                entry.triggered.connect(lambda checked=False, e=entry: self._on_click(e))
            self._return_items[entry] = item
        entry.setEnabled(is_enabled)

    def closeEvent(self, event):
        self.on_close(self)


class TextTimedMenu(AbstractTextTimedMenu, PySide2.QtWidgets.QDialog):

    _close_signal = PySide2.QtCore.Signal()

    def __init__(self, parent, **kwargs):
        PySide2.QtWidgets.QDialog.__init__(self, parent=None)
        self._close_signal.connect(self._on_close_signal)
        super().__init__(**kwargs)
        self.setWindowFlag(PySide2.QtCore.Qt.FramelessWindowHint)
        self._layout = PySide2.QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.on_close(self)

    def pop_up(self, modal=False):
        super().pop_up()
        self.setLayout(self._layout)
        delta = PySide2.QtCore.QPoint(10, 10)
        self.move(PySide2.QtGui.QCursor.pos() + delta)
        if modal:
            PySide2.QtWidgets.QDialog.exec_(self)
        else:
            PySide2.QtWidgets.QDialog.show(self)

    def _create_text(self, label):
        if label == self.SEPARATOR:
            label = ""
        text = Text(self, label=label)
        self._layout.addWidget(text)
        return text

    def _close(self):
        super()._close()
        for text in self._texts:
            text.leaveEvent = lambda event: None
        self._close_signal.emit()

    def _on_close_signal(self):
        PySide2.QtWidgets.QWidget.close(self)


class QtLayout:

    def create_layout(self, parent):
        raise NotImplementedError()

    def apply_align(self, align, size_policy):
        align_flag = 0
        if align & Align.EXPAND:
            align_flag = -1
            if size_policy is not None:
                size_policy.setHorizontalPolicy(PySide2.QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        return align_flag


class BoxLayout(AbstractBoxLayout, QtLayout):
    _LAYOUT_CLASS = None
    _BEFORE = None
    _AFTER = None
    _ORTO_LAYOUT_CLASS = None
    _ORTO_BEFORE = None
    _ORTO_AFTER = None

    def create_layout(self, parent):
        layout = self._LAYOUT_CLASS()
        layout.setSpacing(0)
        for widget_dict in self._widgets:
            widget = widget_dict['type']
            if widget == 'space':
                layout.addSpacing(widget_dict['space'])
            elif widget == 'stretch':
                layout.addStretch(widget_dict['stretch'])
            else:
                widget_border = widget_dict['border']
                if isinstance(widget_border, int):
                    widget_border = [widget_border] * 4

                widget_align = widget_dict['align']
                if isinstance(widget, QtLayout):
                    widget_layout = widget.create_layout(None)
                    widget_layout.setContentsMargins(widget_border[3], widget_border[0], widget_border[1], widget_border[2])
                    align_layout = self._ORTO_LAYOUT_CLASS()
                    if widget_align & Align.END or widget_align & Align.CENTER:
                        align_layout.addStretch()
                    align_layout.addLayout(widget_layout)
                    if widget_align & Align.START or widget_align & Align.CENTER:
                        align_layout.addStretch()
                    layout.addLayout(align_layout, stretch=widget_dict['stretch'])
                else:
                    widget_size_policy = widget.sizePolicy()
                    align_flag = self.apply_align(widget_align, widget_size_policy)
                    widget.setSizePolicy(widget_size_policy)
                    layout.addSpacing(widget_border[self._BEFORE])
                    border_layout = self._ORTO_LAYOUT_CLASS()
                    border_layout.addSpacing(widget_border[self._ORTO_BEFORE])
                    if align_flag == -1:
                        border_layout.addWidget(widget, stretch=widget_dict['stretch'])
                    else:
                        border_layout.addWidget(widget, alignment=align_flag, stretch=widget_dict['stretch'])
                    border_layout.addSpacing(widget_border[self._ORTO_AFTER])
                    layout.addLayout(border_layout, stretch=widget_dict['stretch'])
                    layout.addSpacing(widget_border[self._AFTER])
        if parent is not None:
            parent.setLayout(layout)

        return layout


class VBoxLayout(BoxLayout):
    _LAYOUT_CLASS = PySide2.QtWidgets.QVBoxLayout
    _BEFORE = 0
    _AFTER = 2
    _ORTO_LAYOUT_CLASS = PySide2.QtWidgets.QHBoxLayout
    _ORTO_BEFORE = 3
    _ORTO_AFTER = 1

    def apply_align(self, align, size_policy):
        align_flag = super().apply_align(align, size_policy)
        if align_flag == 0:
            if align & Align.LEFT:
                align_flag = PySide2.QtCore.Qt.AlignLeft
            elif align & Align.HCENTER:
                align_flag = PySide2.QtCore.Qt.AlignHCenter
            elif align & Align.RIGHT:
                align_flag = PySide2.QtCore.Qt.AlignRight
        return align_flag


class HBoxLayout(BoxLayout):
    _LAYOUT_CLASS = PySide2.QtWidgets.QHBoxLayout
    _BEFORE = 3
    _AFTER = 1
    _ORTO_LAYOUT_CLASS = PySide2.QtWidgets.QVBoxLayout
    _ORTO_BEFORE = 0
    _ORTO_AFTER = 2

    def apply_align(self, align, size_policy):
        align_flag = super().apply_align(align, size_policy)
        if align_flag == 0:
            if align & Align.TOP:
                align_flag = PySide2.QtCore.Qt.AlignTop
            elif align & Align.VCENTER:
                align_flag = PySide2.QtCore.Qt.AlignVCenter
            elif align & Align.BOTTOM:
                align_flag = PySide2.QtCore.Qt.AlignBottom
        return align_flag


class GridLayout(AbstractGridLayout, QtLayout):

    def create_layout(self, parent):
        layout = PySide2.QtWidgets.QGridLayout()
        layout.setHorizontalSpacing(self._hgap)
        layout.setVerticalSpacing(self._vgap)

        for row in range(self._rows):
            if self._row_stretch[row] is not None:
                layout.setRowStretch(row, self._row_stretch[row])

        for col in range(self._cols):
            if self._col_stretch[col] is not None:
                layout.setColumnStretch(col, self._col_stretch[col])

        for row, widgets_row in enumerate(self._widgets):
            for col, widget_dict in enumerate(widgets_row):
                widget = widget_dict['type']
                if widget is None:
                    continue
                elif widget == 'space':
                    layout.addItem(PySide2.QtWidgets.QSpacerItem(widget_dict['width'], widget_dict['height']), row, col)
                else:
                    widget_border = widget_dict['border']
                    if isinstance(widget_border, int):
                        widget_border = [widget_border] * 4
                    widget_align = widget_dict['align']

                    if isinstance(widget, QtLayout):
                        widget_layout = widget.create_layout(None)
                        widget_layout.setContentsMargins(widget_border[3], widget_border[0], widget_border[1], widget_border[2])
                        align_flag = self.apply_align(widget_align, None)
                        if align_flag == -1:
                            align_flag = 0
                        layout.addLayout(widget_layout, row, col, alignment=align_flag)
                    else:
                        widget_size_policy = widget.sizePolicy()
                        align_flag = self.apply_align(widget_align, widget_size_policy)
                        widget.setSizePolicy(widget_size_policy)

                        border_layout = PySide2.QtWidgets.QGridLayout()
                        border_layout.setHorizontalSpacing(0)
                        border_layout.setVerticalSpacing(0)
                        border_layout.addItem(PySide2.QtWidgets.QSpacerItem(widget_border[3], widget_border[0]), 0, 0)
                        border_layout.addWidget(widget, 1, 1)
                        border_layout.addItem(PySide2.QtWidgets.QSpacerItem(widget_border[1], widget_border[2]), 2, 2)

                        layout.addLayout(border_layout, row, col, alignment=align_flag)

        if parent is not None:
            parent.setLayout(layout)
        return layout

    def apply_align(self, align, size_policy):
        align_flag = super().apply_align(align, size_policy)
        if align_flag == 0:
            if align & Align.TOP:
                align_flag = PySide2.QtCore.Qt.AlignTop
            elif align & Align.VCENTER:
                align_flag = PySide2.QtCore.Qt.AlignVCenter
            elif align & Align.BOTTOM:
                align_flag = PySide2.QtCore.Qt.AlignBottom
            if align & Align.LEFT:
                align_flag |= PySide2.QtCore.Qt.AlignLeft
            elif align & Align.HCENTER:
                align_flag |= PySide2.QtCore.Qt.AlignHCenter
            elif align & Align.RIGHT:
                align_flag |= PySide2.QtCore.Qt.AlignRight
        return align_flag
