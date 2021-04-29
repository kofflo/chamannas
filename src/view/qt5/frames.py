import PySide2
import PySide2.QtWidgets
import PySide2.QtCore

from src.view.abstract.frames import AbstractWaitingMessage, \
    AbstractDetailedInfoView, AbstractDeveloperInfoView, AbstractHutsView, \
    AbstractSelectedInfoView, AbstractHutsTableView, AbstractHutsMapView, \
    AbstractMessageDialog, AbstractFilterDialog, AbstractAboutDialog, AbstractUpdateDialog, ROOM_TYPES
from src.gui_library.qt5.frames import QtFrame, QtDialog
from src.gui_library.qt5.layouts import HBoxLayout, VBoxLayout, GridLayout, Align


class WaitingMessage(AbstractWaitingMessage, QtFrame):

    _NEW_VERSION = True

    def _create_gui(self):
        info_sizer = VBoxLayout()
        info_sizer.add(self._message, align=Align.EXPAND, border=20)
        info_sizer.add(self._stop_button, align=Align.RIGHT, border=15)
        return info_sizer


class HutsView(AbstractHutsView, QtFrame):

    _NEW_VERSION = True

    def _create_date_gui(self):
        if self._NEW_VERSION:
            widget_sizer = VBoxLayout()
            widget_sizer.add(self._request_date_label, align=Align.EXPAND, border=(10, 10, 0, 10))
            widget_sizer.add(self._date_widget, align=Align.EXPAND, border=(0, 10, 10, 10))
            widget_sizer.add(self._number_days_label, align=Align.EXPAND, border=(10, 10, 0, 10))
            widget_sizer.add(self._number_days_widget, align=Align.EXPAND, border=(0, 10, 10, 10))
            return widget_sizer
        else:
            widget_sizer = PySide2.QtWidgets.QVBoxLayout()

            widget_sizer.addWidget(self._request_date_label, stretch=0)

            widget_sizer.addWidget(self._date_widget, stretch=0)

            widget_sizer.addWidget(self._number_days_label, stretch=0)

            widget_sizer.addWidget(self._number_days_widget, stretch=0)

            return widget_sizer



class HutsTableView(AbstractHutsTableView, HutsView):

    _SELECTED_GRID_HEIGHT = 240
    _NEW_VERSION = True

    def _create_gui(self):
        if self._NEW_VERSION:
            main_sizer = HBoxLayout()
            box_left = VBoxLayout()
            box_checkboxes = HBoxLayout()
            box_checkboxes.add(self._checkbox_no_response, border=10)
            box_checkboxes.add(self._checkbox_closed, border=10)
            box_left.add(box_checkboxes, align=Align.RIGHT)
            box_left.add(self._grid_displayed, align=Align.EXPAND, stretch=1)
            box_left.add(self._selected_huts_label, align=Align.EXPAND, border=(10, 10, 0, 10))
            box_left.add(self._grid_selected, align=Align.EXPAND)
#            self._grid_selected.setMinimumHeight(self._SELECTED_GRID_HEIGHT)
#            self._grid_selected.setMaximumHeight(self._SELECTED_GRID_HEIGHT)
            self._grid_selected._MAXIMUM_HEIGHT = self._SELECTED_GRID_HEIGHT
            self._grid_selected._MINIMUM_HEIGHT = self._SELECTED_GRID_HEIGHT
#            size_policy = self._grid_selected.sizePolicy()
#            size_policy.setVerticalPolicy(PySide2.QtWidgets.QSizePolicy.Policy.Maximum)
#            self._grid_selected.setSizePolicy(size_policy)
            box_right = VBoxLayout()
            date_sizer = self._create_date_gui()
            box_right.add(date_sizer)
            box_right.add(self._retrieve_info_label, align=Align.EXPAND, border=(10, 10, 0, 10))
            box_right.add(self._get_displayed_results_button, align=Align.EXPAND, border=(0, 10, 5, 10))
            box_right.add(self._get_selected_results_button, align=Align.EXPAND, border=(0, 10, 10, 10))
            box_right.add(self._reference_label, align=Align.EXPAND, border=(10, 10, 5, 10))
            box_right.add(self._latitude_label, align=Align.EXPAND, border=(0, 10, 0, 10))
            box_right.add(self._latitude_widget, align=Align.EXPAND, border=(0, 10, 5, 10))
            box_right.add(self._longitude_label, align=Align.EXPAND, border=(0, 10, 0, 10))
            box_right.add(self._longitude_widget, align=Align.EXPAND, border=(0, 10, 5, 10))
            box_right.add(self._set_location_button, align=Align.EXPAND, border=(0, 10, 10, 10))
            box_right.add(self._close_button, align=Align.EXPAND, border=10)
            main_sizer.add(box_left, stretch=1, align=Align.EXPAND)
            main_sizer.add(box_right, align=Align.EXPAND)
            return main_sizer
        else:

            main_sizer = PySide2.QtWidgets.QHBoxLayout()

            box_left = PySide2.QtWidgets.QVBoxLayout()

            box_checkboxes = PySide2.QtWidgets.QHBoxLayout()

            box_checkboxes.addStretch()
            box_checkboxes.addWidget(self._checkbox_no_response, stretch=0)
            box_checkboxes.addWidget(self._checkbox_closed, stretch=0)
            box_left.addLayout(box_checkboxes, stretch=0)

            box_left.addWidget(self._grid_displayed, stretch=1)

            box_left.addWidget(self._selected_huts_label, stretch=0)

            box_left.addWidget(self._grid_selected, stretch=0)
            self._grid_selected.setMinimumHeight(self._SELECTED_GRID_HEIGHT)
            self._grid_selected.setMaximumHeight(self._SELECTED_GRID_HEIGHT)

            box_right = PySide2.QtWidgets.QVBoxLayout()

            date_sizer = self._create_date_gui()
            box_right.addLayout(date_sizer)

            box_right.addSpacing(20)

            box_right.addWidget(self._retrieve_info_label, stretch=0)

            box_right.addWidget(self._get_displayed_results_button, stretch=0)

            box_right.addWidget(self._get_selected_results_button, stretch=0)

            box_right.addSpacing(20)

            box_right.addWidget(self._reference_label, stretch=0)

            box_right.addWidget(self._latitude_label, stretch=0)

            box_right.addWidget(self._latitude_widget, stretch=0)

            box_right.addWidget(self._longitude_label, stretch=0)

            box_right.addWidget(self._longitude_widget, stretch=0)

            box_right.addWidget(self._set_location_button, stretch=0)

            box_right.addSpacing(20)

            box_right.addWidget(self._close_button)

            main_sizer.addLayout(box_left, stretch=1)
            main_sizer.addLayout(box_right, stretch=0)

            self._layout.addLayout(main_sizer)


class HutsMapView(AbstractHutsMapView, HutsView):

    _NEW_VERSION = True

    def _create_gui(self):
        if self._NEW_VERSION:
            main_sizer = HBoxLayout()
            box_left = VBoxLayout()
            box_left.add(self._bitmap, border=10)
            box_right = VBoxLayout()
            date_sizer = self._create_date_gui()
            box_right.add(date_sizer)
            box_right.add(self._get_results_button, align=Align.EXPAND, border=10)
            box_right.add_space(5)
            box_checkboxes = VBoxLayout()
            box_checkboxes.add(self._checkbox_no_response, border=5)
            box_checkboxes.add(self._checkbox_closed, border=5)
            box_checkboxes.add(self._checkbox_reference, border=5)
            box_right.add(box_checkboxes, align=Align.EXPAND, border=10)
            box_right.add(self._huts_choice, align=Align.EXPAND, border=10)
            box_right.add(self._fit_button, align=Align.EXPAND, border=10)
            box_right.add(self._close_button, align=Align.EXPAND, border=10)
            main_sizer.add(box_left, align=Align.EXPAND, stretch=1)
            main_sizer.add(box_right)
            return main_sizer
        else:

            main_sizer = PySide2.QtWidgets.QHBoxLayout()

            box_left = PySide2.QtWidgets.QVBoxLayout()

            box_left.addWidget(self._bitmap)

            box_right = PySide2.QtWidgets.QVBoxLayout()

            date_sizer = self._create_date_gui()
            box_right.addLayout(date_sizer)

            box_right.addSpacing(20)

            box_right.addWidget(self._get_results_button, stretch=0)

            box_right.addSpacing(20)

            box_checkboxes = PySide2.QtWidgets.QVBoxLayout()

            box_checkboxes.addWidget(self._checkbox_no_response, stretch=0)
            box_checkboxes.addWidget(self._checkbox_closed, stretch=0)
            box_checkboxes.addWidget(self._checkbox_reference, stretch=0)
            box_right.addLayout(box_checkboxes, stretch=0)

            box_right.addWidget(self._huts_choice)

            box_right.addSpacing(20)

            box_right.addWidget(self._fit_button)

            box_right.addSpacing(20)

            box_right.addWidget(self._close_button)

            main_sizer.addLayout(box_left, stretch=1)
            main_sizer.addLayout(box_right, stretch=0)

            self._layout.addLayout(main_sizer)


class SelectedInfoView(AbstractSelectedInfoView, QtFrame):

    _NEW_VERSION = True

    def _create_gui(self):
        if self._NEW_VERSION:
            main_sizer = VBoxLayout()
            controls_sizer = HBoxLayout()
            controls_sizer.add(self._all_rooms_button, border=10)
            for room in ROOM_TYPES:
                controls_sizer.add(self._rooms_checkbox[room], align=Align.CENTER, border=10)
            controls_sizer.add(self._retrieve_info_button, border=10)
            controls_sizer.add_stretch()
            controls_sizer.add(self._close_button, border=10)
            main_sizer.add(controls_sizer, align=Align.EXPAND)
            main_sizer.add(self._grid_selected_detailed, align=Align.LEFT, border=10)
            return main_sizer
        else:
            main_sizer = PySide2.QtWidgets.QVBoxLayout()

            controls_sizer = PySide2.QtWidgets.QHBoxLayout()

            controls_sizer.addWidget(self._all_rooms_button)

            for room in ROOM_TYPES:
                controls_sizer.addWidget(self._rooms_checkbox[room])

            controls_sizer.addSpacing(20)

            controls_sizer.addWidget(self._retrieve_info_button)

            controls_sizer.addSpacing(20)

            controls_sizer.addStretch()

            controls_sizer.addWidget(self._close_button)

            main_sizer.addLayout(controls_sizer)

            grid_sizer = PySide2.QtWidgets.QHBoxLayout()

            grid_sizer.addWidget(self._grid_selected_detailed, stretch=2)
            self._grid_selected_detailed.setMaximumHeight(self._SELECTED_DETAILED_GRID_HEIGHT)

            grid_sizer.addStretch(1)

            main_sizer.addLayout(grid_sizer)

            self._layout.addLayout(main_sizer)


class DetailedInfoView(AbstractDetailedInfoView, QtFrame):

    _NEW_VERSION = True

    def _create_gui(self):
        if self._NEW_VERSION:
            info_left_sizer = VBoxLayout()

            info_left_sizer.add(self._hut_text, align=Align.EXPAND, border=10)
            info_left_sizer.add(self._country_text, align=Align.EXPAND, border=(10, 10, 5, 10))
            info_left_sizer.add(self._mountain_text, align=Align.EXPAND, border=(0, 10, 5, 10))
            info_left_sizer.add(self._height_text, align=Align.EXPAND, border=(0, 10, 10, 10))
            info_left_sizer.add(self._self_catering_text, align=Align.EXPAND, border=10)
            info_left_sizer.add(self._bitmap, border=10)
            info_left_sizer.add_stretch()
            info_right_sizer = VBoxLayout()
            button_sizer = HBoxLayout()
            button_sizer.add(self._retrieve_info_button, border=10)
            button_sizer.add(self._open_web_button, border=10)
            button_sizer.add(self._open_booking_button, border=10)
            info_right_sizer.add(button_sizer, border=(10, 0, 10, 0))
            info_right_sizer.add(self._grid_detailed, align=Align.LEFT, border=10)
            info_right_sizer.add_stretch()
            info_right_sizer.add(self._close_button, align=Align.RIGHT, border=10)

            info_sizer = HBoxLayout()
            info_sizer.add(info_left_sizer)
            info_sizer.add(info_right_sizer, align=Align.EXPAND)
            return info_sizer
        else:
            info_left_sizer = PySide2.QtWidgets.QVBoxLayout()

            info_left_sizer.addWidget(self._hut_text)#, stretch=0)

            info_left_sizer.addWidget(self._country_text)#, stretch=0)

            info_left_sizer.addWidget(self._mountain_text)#, stretch=0)

            info_left_sizer.addWidget(self._height_text)#, stretch=0)

            info_left_sizer.addWidget(self._self_catering_text)#, stretch=0)

            info_left_sizer.addWidget(self._bitmap)

            info_left_sizer.addStretch()

            info_right_sizer = PySide2.QtWidgets.QVBoxLayout()

            button_sizer = PySide2.QtWidgets.QHBoxLayout()

            button_sizer.addWidget(self._retrieve_info_button)

            button_sizer.addWidget(self._open_web_button)

            button_sizer.addWidget(self._open_booking_button)

            info_right_sizer.addLayout(button_sizer)

            table_sizer = PySide2.QtWidgets.QHBoxLayout()

            table_sizer.addWidget(self._grid_detailed, stretch=0)

            info_right_sizer.addLayout(table_sizer)

            info_right_sizer.addStretch()

            info_right_sizer.addWidget(self._close_button)

            info_sizer = PySide2.QtWidgets.QHBoxLayout()

            info_sizer.addLayout(info_left_sizer)
            info_sizer.addLayout(info_right_sizer)

            self._layout.addLayout(info_sizer)


class DeveloperInfoView(AbstractDeveloperInfoView, QtFrame):

    _NEW_VERSION = True

    def _create_gui(self):
        if self._NEW_VERSION:
            left_sizer = VBoxLayout()
            right_sizer = VBoxLayout()
            left_sizer.add(self._main_label, align=Align.EXPAND, border=10)
            left_sizer.add(self._no_info_label, align=Align.EXPAND, border=10)
            left_sizer.add(self._grid_developer, align=Align.EXPAND, border=10)
            right_sizer.add_space(30)
            right_sizer.add(self._log_button, border=10)
            right_sizer.add(self._ok_button, align=Align.EXPAND, border=10)
            info_sizer = HBoxLayout()
            info_sizer.add(left_sizer, border=10)
            info_sizer.add(right_sizer, border=10)
            return info_sizer
        else:
            left_sizer = PySide2.QtWidgets.QVBoxLayout()
            right_sizer = PySide2.QtWidgets.QVBoxLayout()

            left_sizer.addWidget(self._main_label)

            left_sizer.addSpacing(20)

            left_sizer.addWidget(self._no_info_label)

            left_sizer.addWidget(self._grid_developer, stretch=0)

            right_sizer.addWidget(self._log_button)

            right_sizer.addWidget(self._ok_button)

            info_sizer = PySide2.QtWidgets.QHBoxLayout()
            info_sizer.addLayout(left_sizer)
            info_sizer.addSpacing(20)
            info_sizer.addLayout(right_sizer)

            self._layout.addLayout(info_sizer)



class FilterDialog(AbstractFilterDialog, QtDialog):

    _NEW_VERSION = True

    def _create_gui(self):
        if self._NEW_VERSION:
            sizer = VBoxLayout()
            sizer.add(self._min_label, align=Align.EXPAND, border=(10, 10, 0, 10))
            sizer.add(self._min_ctrl, align=Align.EXPAND, border=(0, 10, 10, 10))
            sizer.add(self._max_label, align=Align.EXPAND, border=(10, 10, 0, 10))
            sizer.add(self._max_ctrl, align=Align.EXPAND, border=(0, 10, 10, 10))
            button_sizer = HBoxLayout()
            button_sizer.add(self._ok_button, border=(0, 10, 0, 0))
            button_sizer.add(self._cancel_button, border=(0, 0, 0, 10))
            sizer.add(button_sizer, align=Align.EXPAND, border=10)
            return sizer
        else:

            sizer = PySide2.QtWidgets.QVBoxLayout()

            sizer.addWidget(self._min_label, stretch=0)
            sizer.addWidget(self._min_ctrl, stretch=0)
            sizer.addWidget(self._max_label, stretch=0)
            sizer.addWidget(self._max_ctrl, stretch=0)

            button_sizer = PySide2.QtWidgets.QHBoxLayout()
            button_sizer.addWidget(self._ok_button)
            button_sizer.addWidget(self._cancel_button)

            sizer.addLayout(button_sizer, stretch=0)

            self.setLayout(sizer)


class AboutDialog(AbstractAboutDialog, QtDialog):

# TODO: serve init????
    def __init__(self, **kwargs):
        super().__init__(title=f"About {kwargs['dialog_infos']['name']}", **kwargs)

    _NEW_VERSION = True

    def _create_gui(self):
        if self._NEW_VERSION:
            sizer = VBoxLayout()
            sizer.add(self._name_label, align=Align.HCENTER, border=(10, 10, 0, 10))
            sizer.add(self._desc_label, align=Align.HCENTER, border=(10, 10, 0, 10))
            sizer.add(self._copyright_label, align=Align.HCENTER, border=(10, 10, 10, 10))
            sizer.add(self._website_label, align=Align.HCENTER, border=(10, 10, 20, 10))
            sizer.add(self._developer_label, align=Align.LEFT, border=(10, 10, 10, 10))
            sizer.add(self._ok_button, align=Align.RIGHT, border=(10, 10, 10, 10))
            return sizer
        else:
            self.setWindowTitle(self.title)
            sizer = PySide2.QtWidgets.QVBoxLayout()
            sizer.addWidget(self._name_label, alignment=PySide2.QtCore.Qt.AlignHCenter)
            sizer.addWidget(self._desc_label, alignment=PySide2.QtCore.Qt.AlignHCenter)
            sizer.addWidget(self._copyright_label, alignment=PySide2.QtCore.Qt.AlignHCenter)
            sizer.addWidget(self._website_label, alignment=PySide2.QtCore.Qt.AlignHCenter)
            sizer.addSpacing(10)
            sizer.addWidget(self._developer_label, alignment=PySide2.QtCore.Qt.AlignLeft)
            sizer.addSpacing(10)
            sizer.addWidget(self._ok_button, alignment=PySide2.QtCore.Qt.AlignRight)
            self.setLayout(sizer)


class UpdateDialog(AbstractUpdateDialog, QtDialog):

    _NEW_VERSION = True

    def _create_gui(self):
        if self._NEW_VERSION:
            sizer = VBoxLayout()
            sizer.add(self._main_label, align=Align.EXPAND, border=10)
            if self._available_updates:
                grid_sizer = GridLayout(len(self._available_updates), 2, 25, 25)
                grid_sizer.col_stretch(0, 1)
                grid_sizer.col_stretch(1, 5)
                for row, filename in enumerate(self._available_updates):
                    grid_sizer.add(row, 0, self._checkbox[filename], Align.CENTER)
                    grid_sizer.add(row, 1, self._labels[filename], Align.LEFT | Align.VCENTER)
                sizer.add(grid_sizer, align=Align.EXPAND, border=15)
            button_sizer = HBoxLayout()
            button_sizer.add(self._ok_button, border=(0, 10, 0, 0))
            button_sizer.add(self._cancel_button, border=(0, 0, 0, 10))
            sizer.add(button_sizer, align=Align.EXPAND, border=10)
            return sizer
        else:
            sizer = PySide2.QtWidgets.QVBoxLayout()

            sizer.addWidget(self._main_label)

            if self._available_updates:
                grid_sizer = PySide2.QtWidgets.QGridLayout()
                grid_sizer.setColumnStretch(0, 1)
                grid_sizer.setColumnStretch(1, 5)

                for row, filename in enumerate(self._available_updates):
                    grid_sizer.addWidget(self._checkbox[filename], row, 0)
                    grid_sizer.addWidget(self._labels[filename], row, 1)

                sizer.addLayout(grid_sizer)

            button_sizer = PySide2.QtWidgets.QHBoxLayout()
            button_sizer.addWidget(self._ok_button)
            button_sizer.addWidget(self._cancel_button)

            sizer.addLayout(button_sizer, stretch=0)

            self.setLayout(sizer)


class MessageDialog(AbstractMessageDialog, PySide2.QtWidgets.QMessageBox):

    def __init__(self, parent, message, caption):
        PySide2.QtWidgets.QMessageBox.__init__(self, parent)
        self.setIcon(self.Critical)
        super().__init__(message, title=caption)

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
        self.exec_()
        return self.result() == self.Accepted


import src.view.abstract.frames as frames
frames.WaitingMessage = WaitingMessage
frames.FilterDialog = FilterDialog
frames.MessageDialog = MessageDialog
