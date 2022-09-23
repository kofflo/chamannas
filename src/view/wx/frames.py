import wx
import wx.adv
import wx.lib.newevent

from src.view.abstract.frames import AbstractWaitingMessage, \
    AbstractDetailedInfoView, AbstractDeveloperInfoView, AbstractHutsView, \
    AbstractSelectedInfoView, AbstractHutsTableView, AbstractHutsMapView, \
    AbstractMessageDialog, AbstractFilterDialog, AbstractAboutDialog, AbstractUpdateDialog, ROOM_TYPES
from src.gui_library.wx.frames import WxFrame, WxDialog
from src.gui_library.wx.layouts import HBoxLayout, VBoxLayout, GridLayout, Align

from src import i18n


class WaitingMessage(AbstractWaitingMessage, WxFrame):

    _NEW_VERSION = True

    def _create_gui(self):
#        info_sizer = wx.BoxSizer(wx.VERTICAL)
#        info_sizer.Add(self._message, flag=wx.EXPAND | wx.ALL, border=15)
#        info_sizer.Add(self._stop_button, flag=wx.ALIGN_RIGHT | wx.ALL, border=15)
#        self._panel.SetSizer(info_sizer)
        info_sizer = VBoxLayout()
        info_sizer.add(self._message, align=Align.EXPAND, border=20)
        info_sizer.add(self._stop_button, align=Align.RIGHT, border=15)
        return info_sizer


class HutsView(AbstractHutsView, WxFrame):

    def _create_date_gui(self):
        if self._NEW_VERSION:
            widget_sizer = VBoxLayout()
            widget_sizer.add(self._request_date_label, align=Align.EXPAND, border=(10, 10, 0, 10))
            widget_sizer.add(self._date_widget, align=Align.EXPAND, border=(0, 10, 10, 10))
            widget_sizer.add(self._number_days_label, align=Align.EXPAND, border=(10, 10, 0, 10))
            widget_sizer.add(self._number_days_widget, align=Align.EXPAND, border=(0, 10, 10, 10))
            return widget_sizer
        else:
            widget_sizer = wx.BoxSizer(wx.VERTICAL)

            widget_sizer.Add(self._request_date_label,
                             flag=wx.EXPAND | wx.LEFT | wx.UP | wx.RIGHT, border=10)

            widget_sizer.Add(self._date_widget,
                             flag=wx.EXPAND | wx.LEFT | wx.DOWN | wx.RIGHT, border=10)

            widget_sizer.Add(self._number_days_label,
                             flag=wx.EXPAND | wx.LEFT | wx.UP | wx.RIGHT, border=10)

            widget_sizer.Add(self._number_days_widget,
                             flag=wx.EXPAND | wx.LEFT | wx.DOWN | wx.RIGHT, border=10)

            return widget_sizer


class HutsTableView(AbstractHutsTableView, HutsView):

    _SELECTED_GRID_HEIGHT = 160
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
            self._grid_selected._MINIMUM_HEIGHT = self._SELECTED_GRID_HEIGHT
            self._grid_selected._MAXIMUM_HEIGHT = self._SELECTED_GRID_HEIGHT
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
            main_sizer = wx.BoxSizer(wx.HORIZONTAL)

            box_left = wx.BoxSizer(wx.VERTICAL)

            box_checkboxes = wx.BoxSizer(wx.HORIZONTAL)

            box_checkboxes.Add(self._checkbox_no_response, proportion=0, flag=wx.ALL, border=10)
            box_checkboxes.Add(self._checkbox_closed, proportion=0, flag=wx.ALL, border=10)
            box_left.Add(box_checkboxes, proportion=0, flag=wx.ALIGN_RIGHT)

            box_left.Add(self._grid_displayed, proportion=20, flag=wx.EXPAND)

            box_left.Add(self._selected_huts_label, proportion=0,
                         flag=wx.EXPAND | wx.LEFT | wx.UP | wx.RIGHT, border=10)

            box_left.Add(self._grid_selected, proportion=0, flag=wx.EXPAND)
            self._grid_selected.SetMinSize(wx.Size(width=-1, height=self._SELECTED_GRID_HEIGHT))
            self._grid_selected.SetMaxSize(wx.Size(width=-1, height=self._SELECTED_GRID_HEIGHT))

            box_right = wx.BoxSizer(wx.VERTICAL)

            date_sizer = self._create_date_gui()
            box_right.Add(date_sizer)

            box_right.Add(self._retrieve_info_label, proportion=0,
                          flag=wx.EXPAND | wx.LEFT | wx.UP | wx.RIGHT, border=10)

            box_right.Add(self._get_displayed_results_button, proportion=0,
                          flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

            box_right.AddSpacer(5)

            box_right.Add(self._get_selected_results_button, proportion=0,
                          flag=wx.EXPAND | wx.LEFT | wx.DOWN | wx.RIGHT, border=10)

            box_right.Add(self._reference_label, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.UP | wx.RIGHT, border=10)
            box_right.AddSpacer(5)

            box_right.Add(self._latitude_label, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

            box_right.Add(self._latitude_widget, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
            box_right.AddSpacer(5)

            box_right.Add(self._longitude_label, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

            box_right.Add(self._longitude_widget, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
            box_right.AddSpacer(5)

            box_right.Add(self._set_location_button, proportion=0,
                          flag=wx.EXPAND | wx.LEFT | wx.DOWN | wx.RIGHT, border=10)

            box_right.Add(self._close_button, flag=wx.EXPAND | wx.ALL, border=10)

            main_sizer.Add(box_left, 1, wx.EXPAND | wx.ALL)
            main_sizer.Add(box_right, 0, wx.ALL)

            self._panel.SetSizer(main_sizer)


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
            main_sizer = wx.BoxSizer(wx.HORIZONTAL)

            box_left = wx.BoxSizer(wx.VERTICAL)

            box_left.Add(self._bitmap, flag=wx.ALL, border=10)

            box_right = wx.BoxSizer(wx.VERTICAL)

            date_sizer = self._create_date_gui()
            box_right.Add(date_sizer)

            box_right.Add(self._get_results_button, proportion=0, flag=wx.EXPAND | wx.ALL, border=10)

            box_right.AddSpacer(5)

            box_checkboxes = wx.BoxSizer(wx.VERTICAL)

            box_checkboxes.Add(self._checkbox_no_response, proportion=0, flag=wx.ALL, border=5)
            box_checkboxes.Add(self._checkbox_closed, proportion=0, flag=wx.ALL, border=5)
            box_checkboxes.Add(self._checkbox_reference, proportion=0, flag=wx.ALL, border=5)
            box_right.Add(box_checkboxes, proportion=0, flag=wx.EXPAND | wx.ALL, border=10)

            box_right.Add(self._huts_choice, flag=wx.EXPAND | wx.ALL, border=10)

            box_right.Add(self._fit_button, flag=wx.EXPAND | wx.ALL, border=10)

            box_right.Add(self._close_button, flag=wx.EXPAND | wx.ALL, border=10)

            main_sizer.Add(box_left, 1, wx.EXPAND | wx.ALL)
            main_sizer.Add(box_right, 0, wx.ALL)

            self._panel.SetSizer(main_sizer)


class SelectedInfoView(AbstractSelectedInfoView, WxFrame):

    _NEW_VERSION = False
    _SELECTED_DETAILED_GRID_HEIGHT = 400
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
            self._grid_selected_detailed._MAXIMUM_HEIGHT = self._SELECTED_DETAILED_GRID_HEIGHT
            return main_sizer
        else:
            main_sizer = wx.BoxSizer(wx.VERTICAL)
            controls_sizer = wx.BoxSizer(wx.HORIZONTAL)
            controls_sizer.Add(self._all_rooms_button, flag=wx.ALL, border=10)
            for room in ROOM_TYPES:
                controls_sizer.Add(self._rooms_checkbox[room], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=10)
            controls_sizer.Add(self._retrieve_info_button, flag=wx.ALL, border=10)
            controls_sizer.AddStretchSpacer()
            controls_sizer.Add(self._close_button, flag=wx.ALL, border=10)
            main_sizer.Add(controls_sizer, flag=wx.EXPAND)
            main_sizer.Add(self._grid_selected_detailed, proportion=0, flag=wx.ALL, border=10)
            self._grid_selected_detailed.SetMaxSize(wx.Size(width=-1, height=self._SELECTED_DETAILED_GRID_HEIGHT))
            self._panel.SetSizer(main_sizer)


class DetailedInfoView(AbstractDetailedInfoView, WxFrame):

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
            info_left_sizer = wx.BoxSizer(wx.VERTICAL)

            info_left_sizer.Add(self._hut_text, proportion=0, flag=wx.EXPAND | wx.ALL, border=10)

            info_left_sizer.Add(self._country_text, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, border=10)
            info_left_sizer.AddSpacer(5)

            info_left_sizer.Add(self._mountain_text, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
            info_left_sizer.AddSpacer(5)

            info_left_sizer.Add(self._height_text, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=10)

            info_left_sizer.Add(self._self_catering_text, proportion=0, flag=wx.EXPAND | wx.ALL, border=10)

            info_left_sizer.Add(self._bitmap, flag=wx.ALL, border=10)

            info_right_sizer = wx.BoxSizer(wx.VERTICAL)

            button_sizer = wx.BoxSizer(wx.HORIZONTAL)

            button_sizer.Add(self._retrieve_info_button, flag=wx.ALL, border=10)

            button_sizer.Add(self._open_web_button, flag=wx.ALL, border=10)

            button_sizer.Add(self._open_booking_button, flag=wx.ALL, border=10)

            info_right_sizer.Add(button_sizer, flag=wx.TOP | wx.BOTTOM, border=10)

            info_right_sizer.Add(self._grid_detailed, proportion=0, flag=wx.ALL, border=10)

            info_right_sizer.AddStretchSpacer()

            info_right_sizer.Add(self._close_button, flag=wx.ALL | wx.ALIGN_RIGHT, border=10)

            info_sizer = wx.BoxSizer(wx.HORIZONTAL)

            info_sizer.Add(info_left_sizer)
            info_sizer.Add(info_right_sizer, flag=wx.EXPAND)

            self._panel.SetSizer(info_sizer)


class DeveloperInfoView(AbstractDeveloperInfoView, WxFrame):

    _DEVELOPER_GRID_HEIGHT = 100
    _NEW_VERSION = True


    def _create_gui(self):
        if self._NEW_VERSION:
            left_sizer = VBoxLayout()
            right_sizer = VBoxLayout()
            left_sizer.add(self._main_label, align=Align.EXPAND, border=10)
            left_sizer.add(self._no_info_label, align=Align.EXPAND, border=10)
            left_sizer.add(self._grid_developer, align=Align.EXPAND, border=10)
            # TODO!!!!!
            self._grid_developer.SetMinSize(wx.Size(width=-1, height=self._DEVELOPER_GRID_HEIGHT))
            right_sizer.add_space(30)
            right_sizer.add(self._log_button, border=10)
            right_sizer.add(self._ok_button, align=Align.EXPAND, border=10)
            info_sizer = HBoxLayout()
            info_sizer.add(left_sizer, border=10)
            info_sizer.add(right_sizer, border=10)
            return info_sizer
        else:
            left_sizer = wx.BoxSizer(wx.VERTICAL)
            right_sizer = wx.BoxSizer(wx.VERTICAL)

            left_sizer.Add(self._main_label, flag=wx.EXPAND | wx.ALL, border=10)

            left_sizer.Add(self._no_info_label, flag=wx.EXPAND | wx.ALL, border=10)

            left_sizer.Add(self._grid_developer, flag=wx.EXPAND | wx.ALL, border=10)
            self._grid_developer.SetMinSize(wx.Size(width=-1, height=self._DEVELOPER_GRID_HEIGHT))

            right_sizer.AddSpacer(30)

            right_sizer.Add(self._log_button, flag=wx.ALL, border=10)

            right_sizer.Add(self._ok_button, flag=wx.ALL | wx.EXPAND, border=10)

            info_sizer = wx.BoxSizer(wx.HORIZONTAL)
            info_sizer.Add(left_sizer, flag=wx.ALL, border=10, proportion=3)
            info_sizer.Add(right_sizer, flag=wx.ALL, border=10, proportion=1)

            self._panel.SetSizer(info_sizer)


class MessageDialog(AbstractMessageDialog, wx.MessageDialog):

    def __init__(self, parent, message, caption):
        wx.MessageDialog.__init__(self, parent, "", "", wx.OK | wx.ICON_ERROR)
        super().__init__(message, title=caption)

    @property
    def title(self):
        return super(MessageDialog, MessageDialog).title.__get__(self)

    @title.setter
    def title(self, title):
        super(MessageDialog, MessageDialog).title.__set__(self, title)
        self.SetTitle(title)

    @property
    def message(self):
        return super(MessageDialog, MessageDialog).message.__get__(self)

    @message.setter
    def message(self, message):
        super(MessageDialog, MessageDialog).message.__set__(self, message)
        self.SetMessage(message)

    def show_modal(self):
        self.update_gui({})
        return self.ShowModal() == wx.ID_OK


class FilterDialog(AbstractFilterDialog, WxDialog):

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
            sizer = wx.BoxSizer(wx.VERTICAL)

            sizer.Add(self._min_label, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.UP | wx.RIGHT, border=10)
            sizer.Add(self._min_ctrl, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.DOWN | wx.RIGHT, border=10)
            sizer.Add(self._max_label, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.UP | wx.RIGHT, border=10)
            sizer.Add(self._max_ctrl, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.DOWN | wx.RIGHT, border=10)

            button_sizer = wx.BoxSizer(wx.HORIZONTAL)
            button_sizer.Add(self._ok_button, flag=wx.RIGHT, border=10)
            button_sizer.Add(self._cancel_button, flag=wx.LEFT, border=10)

            sizer.Add(button_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=10)

            self.SetSizerAndFit(sizer)


class UpdateDialog(AbstractUpdateDialog, WxDialog):

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
            sizer = wx.BoxSizer(wx.VERTICAL)

            sizer.Add(self._main_label, flag=wx.EXPAND | wx.ALL, border=10)

            if self._available_updates:
                grid_sizer = wx.FlexGridSizer(2, len(self._available_updates), 5)
                grid_sizer.AddGrowableCol(1, 1)

                for filename in self._available_updates:
                    grid_sizer.Add(self._checkbox[filename], flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=10)
                    grid_sizer.Add(self._labels[filename], flag=wx.EXPAND | wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, border=10, proportion=4)

                sizer.Add(grid_sizer)

            button_sizer = wx.BoxSizer(wx.HORIZONTAL)
            button_sizer.Add(self._ok_button, flag=wx.RIGHT, border=10)
            button_sizer.Add(self._cancel_button, flag=wx.LEFT, border=10)

            sizer.Add(button_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=10)

            self.SetSizerAndFit(sizer)


class AboutDialog(AbstractAboutDialog):

    _PROPERTIES = {
        'SetName': 'name',
        'SetVersion': 'version',
        'SetDescription': 'description',
        'SetCopyright': 'copyright',
        'SetWebSite': 'website',
        'AddDeveloper': 'developer'
    }

    def __init__(self, parent, dialog_infos):
        self._about_info = wx.adv.AboutDialogInfo()
        super().__init__(dialog_infos, title=f"About {dialog_infos['name']}")
#    def __init__(self,  **kwargs):  # TODO what is better?
#        self._about_info = wx.adv.AboutDialogInfo()
#        del kwargs['parent']
#        super().__init__(**kwargs)

    def update_gui(self, data):
        for method_name, property_name in self._PROPERTIES.items():
            try:
                property_value = self._dialog_infos[property_name]
                if isinstance(property_value, list):
                    property_value = property_value[i18n.get_current_language()]
                getattr(self._about_info, method_name)(property_value)
            except KeyError:
                pass

    def show_modal(self):
        self.update_gui({})
        wx.adv.AboutBox(self._about_info)
        return True


import src.view.abstract.frames as frames
frames.WaitingMessage = WaitingMessage
frames.FilterDialog = FilterDialog
frames.MessageDialog = MessageDialog
