import tkinter
import tkinter.ttk
import tkinter.messagebox

from src.view.abstract.frames import AbstractWaitingMessage, \
    AbstractDetailedInfoView, AbstractDeveloperInfoView, AbstractHutsView, \
    AbstractSelectedInfoView, AbstractHutsTableView, AbstractHutsMapView, \
    AbstractMessageDialog, AbstractFilterDialog, AbstractAboutDialog, AbstractUpdateDialog, ROOM_TYPES
from src.gui_library.tk.frames import TkFrame, TkDialog
from src.gui_library.tk.widgets import HBoxLayout, VBoxLayout, GridLayout, Align


class WaitingMessage(AbstractWaitingMessage, TkFrame):

    def _create_gui(self):
        self._message.set_frame(self._toplevel)
        self._stop_button.set_frame(self._toplevel)
        self._message.pack(padx=15, pady=15)
        self._stop_button.pack(padx=15, pady=15, side='right')


class HutsView(AbstractHutsView, TkFrame):

    def _create_date_gui(self, frame):
        widget_sizer = tkinter.Frame(frame)

        self._request_date_label.set_frame(widget_sizer)
        self._date_widget.set_frame(widget_sizer)
        self._number_days_label.set_frame(widget_sizer)
        self._number_days_widget.set_frame(widget_sizer)

        self._request_date_label.grid(row=0, column=0, padx=0, pady=0, sticky='w')
        self._date_widget.grid(row=1, column=0, padx=0, pady=(0, 10), sticky='we')
        self._number_days_label.grid(row=2, column=0, padx=0, pady=(10, 0), sticky='w')
        self._number_days_widget.grid(row=3, column=0, padx=0, pady=0, sticky='we')

        return widget_sizer


class HutsTableView(AbstractHutsTableView, HutsView):

    def _create_gui(self):
        splitter = tkinter.PanedWindow(self._toplevel, orient=tkinter.HORIZONTAL)

        box_left = tkinter.Frame(splitter)

        box_checkboxes = tkinter.Frame(box_left)
        self._checkbox_no_response.set_frame(box_checkboxes)
        self._checkbox_closed.set_frame(box_checkboxes)
        self._checkbox_no_response.grid(row=0, column=0, padx=5)
        self._checkbox_closed.grid(row=0, column=1, padx=5)

        self._grid_displayed._GRID_ROW_NUMBERS = 14
        self._grid_displayed.set_frame(box_left)
        displayed_ysb = tkinter.ttk.Scrollbar(box_left, orient='vertical', command=self._grid_displayed.yview)
        displayed_xsb = tkinter.ttk.Scrollbar(box_left, orient='horizontal', command=self._grid_displayed.xview)
        self._grid_displayed.configure(yscrollcommand=displayed_ysb.set, xscrollcommand=displayed_xsb.set)

        self._selected_huts_label.set_frame(box_left)

        self._grid_selected._GRID_ROW_NUMBERS = 6
        self._grid_selected.set_frame(box_left)
        selected_ysb = tkinter.ttk.Scrollbar(box_left, orient='vertical', command=self._grid_selected.yview)
        selected_xsb = tkinter.ttk.Scrollbar(box_left, orient='horizontal', command=self._grid_selected.xview)
        self._grid_selected.configure(yscrollcommand=selected_ysb.set, xscrollcommand=selected_xsb.set)

        box_right = tkinter.Frame(splitter)
        date_sizer = self._create_date_gui(box_right)
        self._retrieve_info_label.set_frame(box_right)
        self._get_displayed_results_button.set_frame(box_right)
        self._get_selected_results_button.set_frame(box_right)
        self._reference_label.set_frame(box_right)
        self._latitude_label.set_frame(box_right)
        self._latitude_widget.set_frame(box_right)
        self._longitude_label.set_frame(box_right)
        self._longitude_widget.set_frame(box_right)
        self._set_location_button.set_frame(box_right)
        self._close_button.set_frame(box_right)

        splitter.add(box_left)
        splitter.add(box_right)
        splitter.pack(fill=tkinter.BOTH, expand=1)

        box_checkboxes.grid(row=0, column=0, padx=5, pady=(0, 5), sticky='w')
        self._grid_displayed.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        displayed_ysb.grid(row=1, column=1, pady=5, sticky='ns')
        displayed_xsb.grid(row=2, column=0, padx=5, sticky='ew')

        self._selected_huts_label.grid(row=3, column=0, padx=5, pady=(10, 0),  sticky='w')

        self._grid_selected.grid(row=4, column=0, padx=5, pady=5,  sticky='nsew')
        selected_ysb.grid(row=4, column=1, pady=5, sticky='ns')
        selected_xsb.grid(row=5, column=0, padx=5, sticky='ew')

        box_left.columnconfigure(0, weight=1)
        box_left.rowconfigure(1, weight=1)
        box_left.rowconfigure(4, weight=1)

        date_sizer.grid(row=0, column=0, pady=5, sticky='we')
        self._retrieve_info_label.grid(row=1, column=0, pady=(10, 0), sticky='w')
        self._get_displayed_results_button.grid(row=2, column=0, sticky='we')
        self._get_selected_results_button.grid(row=3, column=0, pady=(0, 10), sticky='we')
        self._reference_label.grid(row=4, column=0, pady=(10, 0), sticky='w')
        self._latitude_label.grid(row=5, column=0, sticky='w')
        self._latitude_widget.grid(row=6, column=0, sticky='we')
        self._longitude_label.grid(row=7, column=0, sticky='w')
        self._longitude_widget.grid(row=8, column=0, sticky='we')
        self._set_location_button.grid(row=9, column=0, pady=(0, 10), sticky='we')
        self._close_button.grid(row=10, column=0, pady=10, sticky='we')

        splitter.paneconfigure(box_left, padx=10, pady=10)
        splitter.paneconfigure(box_right, minsize=250, padx=10, pady=10)
        splitter.bind('<Motion>', lambda event: "break")


class HutsMapView(AbstractHutsMapView, HutsView):

    def _create_gui(self):

        box_left = tkinter.Frame(self._toplevel)

        box_right = tkinter.Frame(self._toplevel)

        self._bitmap.set_frame(box_left)
        self._bitmap.grid(row=0, column=0, padx=5, pady=5, sticky='nw')

        date_sizer = self._create_date_gui(box_right)
        self._get_results_button.set_frame(box_right)

        date_sizer.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self._get_results_button.grid(row=1, column=0, padx=5, pady=15, sticky='we')

        box_checkboxes = tkinter.Frame(box_right)

        self._checkbox_no_response.set_frame(box_checkboxes)
        self._checkbox_closed.set_frame(box_checkboxes)
        self._checkbox_reference.set_frame(box_checkboxes)

        self._checkbox_no_response.grid(row=0, column=0, padx=5, pady=(5, 0), sticky='w')
        self._checkbox_closed.grid(row=1, column=0, padx=5, pady=(5, 0), sticky='w')
        self._checkbox_reference.grid(row=2, column=0, padx=5, pady=5, sticky='w')

        box_checkboxes.grid(row=2, column=0, padx=5, pady=5, sticky='w')

        self._huts_choice.set_frame(box_right)
        self._fit_button.set_frame(box_right)
        self._close_button.set_frame(box_right)

        self._huts_choice.grid(row=3, column=0, padx=5, pady=10, sticky='w')
        self._fit_button.grid(row=4, column=0, padx=5, pady=10, sticky='we')
        self._close_button.grid(row=5, column=0, padx=5, pady=10, sticky='we')

        box_left.grid(row=0, column=0, padx=5, pady=5, sticky='nw')
        box_right.grid(row=0, column=1, padx=5, pady=5, sticky='nw')


class SelectedInfoView(AbstractSelectedInfoView, TkFrame):

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
#            self._grid_selected_detailed._MAXIMUM_HEIGHT = self._SELECTED_DETAILED_GRID_HEIGHT
            return main_sizer
        else:
            controls_sizer = tkinter.Frame(self._toplevel)

            self._all_rooms_button.set_frame(controls_sizer)
            for room in ROOM_TYPES:
                self._rooms_checkbox[room].set_frame(controls_sizer)
            self._retrieve_info_button.set_frame(controls_sizer)
            self._close_button.set_frame(controls_sizer)

            self._all_rooms_button.grid(row=0, column=0, padx=(0, 10), pady=10)
            col = 0
            for room in ROOM_TYPES:
                col += 1
                self._rooms_checkbox[room].grid(row=0, column=col, padx=10, pady=10)
            self._retrieve_info_button.grid(row=0, column=col+1, padx=10, pady=10)
            controls_sizer.columnconfigure(col+2, weight=1)
            self._close_button.grid(row=0, column=col+3, padx=(10, 0), pady=10, sticky='e')

            self._grid_selected_detailed.set_frame(self._toplevel)

            controls_sizer.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
            self._grid_selected_detailed.grid(row=1, column=0, padx=10, pady=10, sticky='w')


class DetailedInfoView(AbstractDetailedInfoView, TkFrame):

    def _create_gui(self):
        info_left_sizer = tkinter.Frame(self._toplevel)
        self._hut_text.set_frame(info_left_sizer)
        self._country_text.set_frame(info_left_sizer)
        self._mountain_text.set_frame(info_left_sizer)
        self._height_text.set_frame(info_left_sizer)
        self._self_catering_text.set_frame(info_left_sizer)
        self._bitmap.set_frame(info_left_sizer)
        self._hut_text.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self._country_text.grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self._mountain_text.grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self._height_text.grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self._self_catering_text.grid(row=4, column=0, padx=10, pady=5, sticky='w')
        self._bitmap.grid(row=5, column=0, padx=10, pady=10, sticky='w')

        info_right_sizer = tkinter.Frame(self._toplevel)

        button_sizer = tkinter.Frame(info_right_sizer)
        self._grid_detailed.set_frame(info_right_sizer)
        self._close_button.set_frame(info_right_sizer)

        self._retrieve_info_button.set_frame(button_sizer)
        self._open_web_button.set_frame(button_sizer)
        self._open_booking_button.set_frame(button_sizer)
        self._retrieve_info_button.grid(row=0, column=0, padx=(0, 10), pady=10)
        self._open_web_button.grid(row=0, column=1, padx=10, pady=10)
        self._open_booking_button.grid(row=0, column=2, padx=(10, 0), pady=10)

        button_sizer.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self._grid_detailed.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self._close_button.grid(row=2, column=0, padx=10, pady=10, sticky='e')

        info_left_sizer.grid(row=0, column=0, padx=(10, 0), pady=10, sticky='n')
        info_right_sizer.grid(row=0, column=1, padx=(0, 10), pady=10, sticky='n')


class DeveloperInfoView(AbstractDeveloperInfoView, TkFrame):

    def _create_gui(self):
        left_sizer = tkinter.Frame(self._toplevel)
        self._main_label.set_frame(left_sizer)
        self._no_info_label.set_frame(left_sizer)
        self._grid_developer.set_frame(left_sizer)

        self._main_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self._no_info_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self._grid_developer.grid(row=2, column=0, padx=10, pady=10, sticky='nsw')

        right_sizer = tkinter.Frame(self._toplevel)
        self._log_button.set_frame(right_sizer)
        self._ok_button.set_frame(right_sizer)
        self._log_button.grid(row=0, column=0, padx=10, pady=10)
        self._ok_button.grid(row=1, column=0, padx=10, pady=10)

        left_sizer.grid(row=0, column=0, padx=(10, 0), pady=10)
        right_sizer.grid(row=0, column=1, padx=(0, 10), pady=10)


class MessageDialog(AbstractMessageDialog):

    def __init__(self, parent, message, caption):
        super().__init__(message, title=caption)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        #
        pass

    @property
    def title(self):
        return super(MessageDialog, MessageDialog).title.__get__(self)

    @title.setter
    def title(self, title):
        super(MessageDialog, MessageDialog).title.__set__(self, title)

    @property
    def message(self):
        return super(MessageDialog, MessageDialog).message.__get__(self)

    @message.setter
    def message(self, message):
        super(MessageDialog, MessageDialog).message.__set__(self, message)

    def show_modal(self):
        self.update_gui({})
        return_value = tkinter.messagebox.showerror(title=self.title, message=self.message)
        return return_value == tkinter.messagebox.OK


class FilterDialog(AbstractFilterDialog, TkDialog):

    def _create_gui(self):
        self._min_label.set_frame(self._toplevel)
        self._min_ctrl.set_frame(self._toplevel)
        self._max_label.set_frame(self._toplevel)
        self._max_ctrl.set_frame(self._toplevel)

        self._min_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky='w')
        self._min_ctrl.grid(row=1, column=0, padx=10, pady=(0, 10))
        self._max_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky='w')
        self._max_ctrl.grid(row=3, column=0, padx=10, pady=(0, 10))

        button_sizer = tkinter.Frame(self._toplevel)
        self._ok_button.set_frame(button_sizer)
        self._cancel_button.set_frame(button_sizer)
        self._ok_button.grid(row=0, column=0, padx=10)
        self._cancel_button.grid(row=0, column=1, padx=10)

        button_sizer.grid(row=4, column=0, pady=10)


class UpdateDialog(AbstractUpdateDialog, TkDialog):

    def _create_gui(self):

        self._main_label.set_frame(self._toplevel)

        for filename in self._available_updates:
            self._checkbox[filename].set_frame(self._toplevel)
            self._labels[filename].set_frame(self._toplevel)

        self._main_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        for index, filename in enumerate(self._available_updates):
            self._checkbox[filename].grid(row=index + 1, column=0, pady=10)
            self._labels[filename].grid(row=index + 1, column=1, pady=10, sticky='w')

        last_row = len(self._available_updates)

        button_sizer = tkinter.Frame(self._toplevel)
        self._ok_button.set_frame(button_sizer)
        self._ok_button.grid(row=0, column=0, padx=10)

        if self._available_updates:
            self._cancel_button.set_frame(button_sizer)
            self._cancel_button.grid(row=0, column=1, padx=10)

        button_sizer.grid(row=last_row + 1, column=0, columnspan=2, pady=10)


class AboutDialog(AbstractAboutDialog, TkDialog):

    def __init__(self, **kwargs):
        super().__init__(title=f"About {kwargs['dialog_infos']['name']}", **kwargs)

    def _create_gui(self):
        self._name_label.set_frame(self._toplevel)
        self._desc_label.set_frame(self._toplevel)
        self._copyright_label.set_frame(self._toplevel)
        self._website_label.set_frame(self._toplevel)
        self._developer_label.set_frame(self._toplevel)
        self._ok_button.set_frame(self._toplevel)

        self._name_label.grid(row=0, column=0, padx=10, pady=10)
        self._desc_label.grid(row=1, column=0, padx=10, pady=5)
        self._copyright_label.grid(row=2, column=0, padx=10, pady=5)
        self._website_label.grid(row=3, column=0, padx=10, pady=10)
        self._developer_label.grid(row=4, column=0, padx=10, pady=10)
        self._ok_button.grid(row=5, column=0, padx=10, pady=10)


import src.view.abstract.frames as frames
frames.WaitingMessage = WaitingMessage
frames.FilterDialog = FilterDialog
frames.MessageDialog = MessageDialog
