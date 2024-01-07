import PySide6
import PySide6.QtWidgets
import PySide6.QtCore
import PySide6.QtGui

from PIL.ImageQt import ImageQt

from ..abstract.widgets import AbstractWidget, AbstractMouseEventsWidget, AbstractLabelledWidget, \
    AbstractButton, AbstractCheckBox, AbstractRadioBox, AbstractBitmap, \
    AbstractText, AbstractCalendar, AbstractSpinControl, AbstractMenu, TextStyle, AbstractTextTimedMenu


def build_font(size, style):
    font = PySide6.QtGui.QFont('Helvetica', size)
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
        # corrects using current curson position due to error in qt6 that does not update mouse event position
        q_global_position = event.globalPos()
        cursor_position = PySide6.QtGui.QCursor.pos()
        position = (position[0] + cursor_position.x() - q_global_position.x(),
                    position[1] + cursor_position.y() - q_global_position.y())
        # end of correction
        button = event.button()
        if button is PySide6.QtCore.Qt.LeftButton:
            self.on_left_down(self, position)
        elif button is PySide6.QtCore.Qt.RightButton:
            self.on_right_down(self, position)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        q_position = event.localPos()
        position = q_position.x(), q_position.y()
        button = event.button()
        if button is PySide6.QtCore.Qt.LeftButton:
            self.on_left_up(self, position)
        elif button is PySide6.QtCore.Qt.RightButton:
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


class Button(AbstractButton, LabelledWidget, PySide6.QtWidgets.QPushButton):

    def __init__(self, panel, **kwargs):
        PySide6.QtWidgets.QPushButton.__init__(self, parent=panel)
        super().__init__(**kwargs)
        self.clicked.connect(self._on_click)

    def _on_click(self):
        self.on_click(self)


class CheckBox(AbstractCheckBox, LabelledWidget, PySide6.QtWidgets.QCheckBox):

    def __init__(self, panel, **kwargs):
        PySide6.QtWidgets.QCheckBox.__init__(self, parent=panel)
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


class RadioBox(AbstractRadioBox, PySide6.QtWidgets.QGroupBox):

    def __init__(self, panel, **kwargs):
        PySide6.QtWidgets.QGroupBox.__init__(self, parent=panel)
        super().__init__(**kwargs)
        self._button_group = PySide6.QtWidgets.QButtonGroup(parent=panel)

        vbox = PySide6.QtWidgets.QVBoxLayout()
        for choice in self._choices:
            button = PySide6.QtWidgets.QRadioButton(choice, parent=panel)
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


class Bitmap(AbstractBitmap, MouseEventsWidget, PySide6.QtWidgets.QLabel):

    def __init__(self, panel, **kwargs):
        PySide6.QtWidgets.QLabel.__init__(self, panel)
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
            self.setPixmap(PySide6.QtGui.QPixmap.fromImage(self._image_qt))
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


class TextControl(TextWidget, LabelledWidget, PySide6.QtWidgets.QLineEdit):

    def __init__(self, panel, **kwargs):
        PySide6.QtWidgets.QLineEdit.__init__(self, panel)
        super().__init__(**kwargs)

    @property
    def label(self):
        super(TextControl, TextControl).label.__set__(self, self.text())
        return super(TextControl, TextControl).label.__get__(self)

    @label.setter
    def label(self, label):
        super(TextControl, TextControl).label.__set__(self, label)
        self.setText(super(TextControl, TextControl).label.__get__(self))


class Text(TextWidget, LabelledWidget, MouseEventsWidget, PySide6.QtWidgets.QLabel):

    def __init__(self, panel, **kwargs):
        PySide6.QtWidgets.QLabel.__init__(self, panel)
        super().__init__(**kwargs)


class Calendar(AbstractCalendar, Widget, PySide6.QtWidgets.QCalendarWidget):

    def __init__(self, panel, **kwargs):
        PySide6.QtWidgets.QCalendarWidget.__init__(self, panel)
        self.setFirstDayOfWeek(PySide6.QtCore.Qt.Monday)
        self.clicked.connect(self._on_date_changed)
        self.setHorizontalHeaderFormat(self.HorizontalHeaderFormat.SingleLetterDayNames)
        self.setVerticalHeaderFormat(self.VerticalHeaderFormat.NoVerticalHeader)
        self.setGridVisible(True)
        super().__init__(**kwargs)

    def _on_date_changed(self, event):
        self.on_date_changed(self)

    def paintCell(self, painter, rect, date):
        if not self.minimumDate() <= date <= self.maximumDate():
            painter.setBrush(PySide6.QtGui.QBrush(PySide6.QtCore.Qt.lightGray))
            painter.setPen(PySide6.QtGui.QPen(PySide6.QtCore.Qt.lightGray))
            painter.drawRect(rect)
            painter.setPen(PySide6.QtGui.QPen(PySide6.QtCore.Qt.gray))
            painter.drawText(rect, PySide6.QtCore.Qt.AlignHCenter | PySide6.QtCore.Qt.AlignVCenter, str(date.day()))
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
            qt_lower_date = PySide6.QtCore.QDate(date_as_tuple[0], date_as_tuple[1], date_as_tuple[2])
        else:
            qt_lower_date = PySide6.QtCore.QDate(1, 1, 1)
        if self.upper_date is not None:
            date_as_tuple = self.upper_date.timetuple()
            qt_upper_date = PySide6.QtCore.QDate(date_as_tuple[0], date_as_tuple[1], date_as_tuple[2])
        else:
            qt_upper_date = PySide6.QtCore.QDate(10000, 1, 1)
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
        self.setSelectedDate(PySide6.QtCore.QDate(date_as_tuple[0], date_as_tuple[1], date_as_tuple[2]))

    def set_language(self, language):
        if language == 'English':
            self.setLocale(PySide6.QtCore.QLocale.English)
        elif language == 'Italiano':
            self.setLocale(PySide6.QtCore.QLocale.Italian)
        elif language == 'Deutsch':
            self.setLocale(PySide6.QtCore.QLocale.German)
        else:
            self.setLocale(PySide6.QtCore.QLocale.English)


class SpinControl(AbstractSpinControl, Widget, PySide6.QtWidgets.QSpinBox):

    def __init__(self, panel, **kwargs):
        PySide6.QtWidgets.QSpinBox.__init__(self, panel)
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
        super(SpinControl, SpinControl).value.__set__(self, PySide6.QtWidgets.QSpinBox.value(self))
        return super(SpinControl, SpinControl).value.__get__(self)

    @value.setter
    def value(self, value):
        super(SpinControl, SpinControl).value.__set__(self, value)
        self.setValue(super(SpinControl, SpinControl).value.__get__(self))


class Menu(AbstractMenu, Widget, PySide6.QtWidgets.QMenu):

    def __init__(self, parent, **kwargs):
        PySide6.QtWidgets.QMenu.__init__(self)
        super().__init__(**kwargs)
        self._parent = parent

    def _on_click(self, entry):
        self.on_click(self, entry)

    def pop_up(self):
        super().pop_up()
        self.exec(PySide6.QtGui.QCursor.pos())

    def _append_menubar(self, menubar, item, is_enabled, on_item_click):
        if item is None:
            return
        elif isinstance(item, Menu):
            item.build_menu(inherited_on_click=self.on_click)
            item.setTitle(item.label)
            menubar.addMenu(item)
            entry = item
        else:
            entry = PySide6.QtWidgets.QAction(item, self)
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
            entry = PySide6.QtGui.QAction(item, self)
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


class TextTimedMenu(AbstractTextTimedMenu, PySide6.QtWidgets.QDialog):

    _close_signal = PySide6.QtCore.Signal()

    def __init__(self, parent, **kwargs):
        PySide6.QtWidgets.QDialog.__init__(self, parent=None)
        self._close_signal.connect(self._on_close_signal)
        super().__init__(**kwargs)
        self.setWindowFlag(PySide6.QtCore.Qt.FramelessWindowHint)
        self._layout = PySide6.QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.on_close(self)

    def pop_up(self, modal=False):
        super().pop_up()
        self.setLayout(self._layout)
        delta = PySide6.QtCore.QPoint(10, 10)
        self.move(PySide6.QtGui.QCursor.pos() + delta)
        if modal:
            PySide6.QtWidgets.QDialog.exec(self)
        else:
            PySide6.QtWidgets.QDialog.show(self)

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
        PySide6.QtWidgets.QWidget.close(self)
