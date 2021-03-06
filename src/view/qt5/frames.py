import PySide2
import PySide2.QtWidgets
import PySide2.QtCore

from src.view.abstract_view.frames import AbstractWaitingMessage, \
    AbstractDetailedInfoView, AbstractDeveloperInfoView, AbstractHutsView, \
    AbstractSelectedInfoView, AbstractHutsTableView, AbstractHutsMapView, \
    AbstractMessageDialog, AbstractFilterDialog, AbstractAboutDialog, AbstractUpdateDialog, ROOM_TYPES
from src.gui_library.qt5.frames import QtFrame, QtDialog


class WaitingMessage(AbstractWaitingMessage, QtFrame):

    def _create_gui(self):
        info_sizer = PySide2.QtWidgets.QVBoxLayout()
        info_sizer.addWidget(self._message)
        info_sizer.addWidget(self._stop_button, alignment=PySide2.QtCore.Qt.AlignRight)
        self._layout.addLayout(info_sizer)


class HutsView(AbstractHutsView, QtFrame):

    def _create_date_gui(self):
        widget_sizer = PySide2.QtWidgets.QVBoxLayout()

        widget_sizer.addWidget(self._request_date_label, stretch=0)

        widget_sizer.addWidget(self._date_widget, stretch=0)

        widget_sizer.addWidget(self._number_days_label, stretch=0)

        widget_sizer.addWidget(self._number_days_widget, stretch=0)

        return widget_sizer


class HutsTableView(AbstractHutsTableView, HutsView):

    _SELECTED_GRID_HEIGHT = 240

    def _create_gui(self):

        main_sizer = PySide2.QtWidgets.QHBoxLayout()

        box_left = PySide2.QtWidgets.QVBoxLayout()

        box_checkboxes = PySide2.QtWidgets.QHBoxLayout()

        box_checkboxes.addStretch()
        box_checkboxes.addWidget(self._checkbox_no_response, stretch=0)
        box_checkboxes.addWidget(self._checkbox_closed, stretch=0)
        box_left.addLayout(box_checkboxes, stretch=0)

        box_left.addWidget(self._grid_displayed, stretch=20)

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

    def _create_gui(self):

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

    def _create_gui(self):
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

        grid_sizer.addStretch(1)

        main_sizer.addLayout(grid_sizer)

        self._layout.addLayout(main_sizer)


class DetailedInfoView(AbstractDetailedInfoView, QtFrame):

    def _create_gui(self):
        info_left_sizer = PySide2.QtWidgets.QVBoxLayout()

        info_left_sizer.addWidget(self._hut_text, stretch=0)

        info_left_sizer.addWidget(self._country_text, stretch=0)

        info_left_sizer.addWidget(self._mountain_text, stretch=0)

        info_left_sizer.addWidget(self._height_text, stretch=0)

        info_left_sizer.addWidget(self._self_catering_text, stretch=0)

        info_left_sizer.addWidget(self._bitmap)

        info_left_sizer.addStretch()

        info_right_sizer = PySide2.QtWidgets.QVBoxLayout()

        button_sizer = PySide2.QtWidgets.QHBoxLayout()

        button_sizer.addWidget(self._retrieve_info_button)

        button_sizer.addWidget(self._open_web_button)

        button_sizer.addWidget(self._open_booking_button)

        info_right_sizer.addLayout(button_sizer)

        table_sizer = PySide2.QtWidgets.QHBoxLayout()

        table_sizer.addWidget(self._grid_detailed, alignment=PySide2.QtCore.Qt.AlignLeft, stretch=0)

        info_right_sizer.addLayout(table_sizer)

        info_right_sizer.addStretch()

        info_right_sizer.addWidget(self._close_button, alignment=PySide2.QtCore.Qt.AlignRight)

        info_sizer = PySide2.QtWidgets.QHBoxLayout()

        info_sizer.addLayout(info_left_sizer)
        info_sizer.addLayout(info_right_sizer)

        self._layout.addLayout(info_sizer)


class DeveloperInfoView(AbstractDeveloperInfoView, QtFrame):

    def _create_gui(self):
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

    def _create_gui(self):

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

    def __init__(self, **kwargs):
        super().__init__(title=f"About {kwargs['dialog_infos']['name']}", **kwargs)

    def _create_gui(self):
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

    def _create_gui(self):

        sizer = PySide2.QtWidgets.QVBoxLayout()

        sizer.addWidget(self._main_label)

        sizer.addSpacing(15)

        if self._available_updates:
            grid_sizer = PySide2.QtWidgets.QGridLayout()
            grid_sizer.setColumnStretch(0, 1)
            grid_sizer.setColumnStretch(1, 5)

            for row, filename in enumerate(self._available_updates):
                grid_sizer.addWidget(self._checkbox[filename], row, 0)
                grid_sizer.addWidget(self._labels[filename], row, 1)

            sizer.addLayout(grid_sizer)

        sizer.addSpacing(15)

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


import src.view.abstract_view.frames as frames
frames.WaitingMessage = WaitingMessage
frames.FilterDialog = FilterDialog
frames.MessageDialog = MessageDialog
