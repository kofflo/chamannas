"""
Definition of different types of windows for the GUI interface.
All table classes are derived from the PrettYSUsI Frame or Dialog class.

Classes:
    HutsTableView: the main frame with huts information in table form
    HutsMapView: the main frame with huts information in the map
    DetailedInfoView:
    SelectedInfoView:
    DeveloperInfoView:
    FilterDialog: the dialog used to allow filtering of the table data
    AboutDialog: the dialog used to show the About information
    UpdateDialog: the dialog used to select the updates to the program to apply
    WaitingMessage: the frame (in dialog style) used to display a waiting message
"""
import ast
import datetime

from src.map_tools import NavigableMap, HutMap
from src import i18n
from src import config
from src.model import ROOM_TYPES
from prettysusi.widgets import Button, CheckBox, RadioBox, Bitmap, Text, Calendar, SpinControl, Menu, TextControl, \
     TextTimedMenu
from prettysusi import event_create
from prettysusi.frames import FrameStyle, CursorStyle
from prettysusi.widgets import TextStyle
from prettysusi.frames import Frame, Dialog, MessageDialog
from prettysusi.layouts import HBoxLayout, VBoxLayout, GridLayout
from prettysusi.layouts import Align

from src.view.tables import HutsGrid, DetailedGrid, DeveloperGrid, SelectedDetailedGrid
from src.config import ASSETS_PATH_ICONS

# File containing the program icon
_APP_ICON_FILENAME = str(ASSETS_PATH_ICONS / "app_icon.png")

# Symbol to be used as check
_CHECKED_SYMBOL = '  \u2713'


class _HutsInfoFrame(Frame):
    """Superclass for all frames showing huts information.

    Methods:
        From superclass:
        title: return the title of the frame
        icon: return the icon of the frame
        show: show the frame
        hide: hide the frame
        set_focus: set the focus of the frame
        set_cursor: set the cursor shape
        close: close the frame
        on_close: executed when the frame is closed
        update_gui: update the frame content
        on_update_gui: executed when updating the frame content
        set_layout: set the layout of the frame
        event_connect: connect an event to a function
        event_trigger: trigger the event
    """

    def __init__(self, *, controller, **kwargs):
        """Initialise the frame.

        :param controller: the controller object used to control the view
        :param kwargs: additional parameters for superclass
        """
        self._controller = controller
        self._menu_chosen_item = None
        self._retrieve_enabled = True
        super().__init__(icon=_APP_ICON_FILENAME, **kwargs)

    def _update_gui_for_retrieve_enabled(self, is_enabled):
        """Update the frame based on the enabling status of the data retrieval.

        :param is_enabled: boolean defining if the data retrieval is enabled
        """
        self._retrieve_enabled = is_enabled


class _HutsView(_HutsInfoFrame):
    """Superclass for main frames showing huts information.

    Methods:
        show_waiting_message_huts:
        update_waiting_message_huts:
        show_waiting_message_updates
        show_waiting_message_huts
        close_waiting_message
        post_after_updates_event

        From superclass:
        title: return the title of the frame
        icon: return the icon of the frame
        show: show the frame
        hide: hide the frame
        set_focus: set the focus of the frame
        set_cursor: set the cursor shape
        close: close the frame
        on_close: executed when the frame is closed
        update_gui: update the frame content
        on_update_gui: executed when updating the frame content
        set_layout: set the layout of the frame
        event_connect: connect an event to a function
        event_trigger: trigger the event
    """

    _after_update_event = event_create()

    def __init__(self, **kwargs):
        """Initialise the frame.

        :param kwargs: additional parameters for superclass
        """
        super().__init__(**kwargs)
        self.event_connect(self._after_update_event, self._on_after_update)
        self._waiting_message = None
        self._all_updates = {}
        self._update_cancelled = False

    def show_waiting_message_huts(self, cancel_function, outstanding):
        """Show the waiting message when retrieving huts information.

        :param cancel_function: function to be executed if the data retrieval is cancelled
        :param outstanding: number of outstanding huts
        """
        if self._waiting_message is not None:
            self.close_waiting_message()
        title = i18n.all_strings['waiting caption huts']
        self._waiting_message = WaitingMessage(cancel_function=cancel_function, parent=self, title=title)
        label = i18n.all_strings['waiting message huts'].format(outstanding)
        self._waiting_message.update_gui({'message': label})
        self._waiting_message.show()

    def update_waiting_message_huts(self, outstanding):
        """Update the waiting message when retrieving huts information.

        :param outstanding: number of outstanding huts
        """
        label = i18n.all_strings['waiting message huts'].format(outstanding)
        self._waiting_message.update_gui({'message': label})

    def show_waiting_message_updates(self, cancel_function, message):
        """Show the waiting message when retrieving updates.

        :param cancel_function: function to be executed if the update is cancelled
        :param message: message to display
        """
        if self._waiting_message is not None:
            self.close_waiting_message()
        title = i18n.all_strings['waiting caption updates']
        self._waiting_message = WaitingMessage(cancel_function=cancel_function, parent=self, title=title)
        label = i18n.all_strings['waiting message updates'].format(i18n.all_strings[message])
        self._waiting_message.update_gui({'message': label})
        self._waiting_message.show()

    def update_waiting_message_updates(self, message):
        """Update the waiting message when retrieving updates.

        :param message: message to display
        """
        label = i18n.all_strings['waiting message updates'].format(i18n.all_strings[message])
        self._waiting_message.update_gui({'message': label})

    def close_waiting_message(self):
        """Close the waiting message."""
        self._waiting_message.close()
        self._waiting_message = None

    def _update_gui_for_retrieve_enabled(self, is_enabled):
        """Update the frame based on the enabling status of the data retrieval.

        :param is_enabled: boolean defining if the data retrieval is enabled
        """
        super()._update_gui_for_retrieve_enabled(is_enabled)
        self._create_menu()

    def _create_date_widgets(self):
        """Create the widgets used to choose the request dates."""
        self._request_date_label = Text(parent=self, label=i18n.all_strings['request date'])

        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        self._date_widget = Calendar(parent=self, lower_date=tomorrow, selected_date=tomorrow)
        self._date_widget.on_date_changed = self._on_dates_selected

        self._number_days_label = Text(parent=self, label=i18n.all_strings['number of days'])

        self._number_days_widget = SpinControl(parent=self, min_value=1, max_value=1)
        self._number_days_widget.on_click = self._on_dates_selected

    def _create_menu(self):
        """Create the frame menu."""
        menubar = Menu(parent=self)

        label = ast.literal_eval(i18n.all_strings['menu main'])[0]
        menu_main = Menu(parent=self, label=label)

        self._other_view_menu(menu_main)

        if self.parent is not None:
            menubar.append(menu_main)
            self._set_menubar(menubar)
            return

        label = ast.literal_eval(i18n.all_strings['menu language'])[0]
        menu_language = Menu(parent=self, label=label)
        languages = i18n.get_languages_list()
        if languages:
            menu_main.append(menu_language)
            for lang_index, lang_string in enumerate(languages):
                menu_string = '&' + lang_string
                if lang_index == i18n.get_current_language_index():
                    menu_string += _CHECKED_SYMBOL
                menu_string += '\tAlt-' + lang_string[0]
                menu_language.append(menu_string, on_item_click=lambda lang=lang_index: self._on_language(lang))

        label = ast.literal_eval(i18n.all_strings['menu preferences'])[0]
        menu_preferences = Menu(parent=self, label=label)
        menu_main.append(menu_preferences)

        if config.SUPPORTED_GUIS is not None:
            label = ast.literal_eval(i18n.all_strings['menu gui'])[0]
            menu_gui = Menu(parent=self, label=label)
            menu_preferences.append(menu_gui)
            for gui_type in config.SUPPORTED_GUIS:
                menu_string = i18n.all_strings[gui_type]
                if gui_type == config.GUI:
                    menu_string += _CHECKED_SYMBOL
                menu_gui.append(menu_string, on_item_click=lambda gt=gui_type: self._on_menu_gui(gt))

        label = ast.literal_eval(i18n.all_strings['menu view'])[0]
        menu_view = Menu(parent=self, label=label)
        menu_preferences.append(menu_view)
        for view_type in ['table', 'map']:
            menu_string = i18n.all_strings[view_type]
            if view_type == config.VIEW:
                menu_string += _CHECKED_SYMBOL
            menu_view.append(menu_string, on_item_click=lambda vt=view_type: self._on_menu_view(vt))

        label = ast.literal_eval(i18n.all_strings['menu exit'])[0]
        menu_main.append(label, on_item_click=self._on_menu_command_close)

        label = ast.literal_eval(i18n.all_strings['menu help'])[0]
        menu_help = Menu(parent=self, label=label)

        if self._retrieve_enabled:
            label = ast.literal_eval(i18n.all_strings['menu updates'])[0]
            menu_help.append(label, on_item_click=self._on_updates)

        label = ast.literal_eval(i18n.all_strings['menu about'])[0]
        menu_help.append(label, on_item_click=self._on_about)

        label = ast.literal_eval(i18n.all_strings['menu developer'])[0]
        menu_develop = Menu(parent=self, label=label)

        label = ast.literal_eval(i18n.all_strings['menu warnings'])[0]
        menu_develop.append(label, on_item_click=self._on_show_warnings)
        label = ast.literal_eval(i18n.all_strings['menu errors'])[0]
        menu_develop.append(label, on_item_click=self._on_show_errors)

        menubar.append(menu_main)
        menubar.append(menu_develop)
        menubar.append(menu_help)

        self._set_menubar(menubar)

    def _on_about(self):
        """Open the About dialog"""
        self._controller.command_open_about_dialog(self)

    def _on_updates(self):
        """Search for updates."""
        self._controller.command_search_for_updates()

    def _on_language(self, lang):
        """Set the frame language.

        :param lang: the language to set
        """
        self._controller.command_language(lang)

    def _on_menu_gui(self, gui_type):
        """Set the GUI framework to use at the next program start.

        :param gui_type: the GUI framework to use
        """
        self._controller.command_preference_gui(gui_type)
        self._create_menu()

    def _on_menu_view(self, view_type):
        """Set the default view type (table or map).

        :param view_type: the view type to be set as default
        """
        self._controller.command_preference_view(view_type)
        self._create_menu()

    def _on_show_warnings(self):
        """Open the developer frame showing the triggered warnings."""
        self._controller.command_open_warnings_frame(self)

    def _on_show_errors(self):
        """Open the developer frame showing the triggered errors."""
        self._controller.command_open_errors_frame(self)

    def _on_menu_command_close(self):
        """Close the frame."""
        self.close()

    def _on_button_command_close(self, _obj):
        """Close the frame."""
        self.close()

    def on_update_gui(self, data):
        """Update the frame with the provided data.

        :param data: the data to use to update the frame
        """
        if 'displayed' in data:
            self._update_displayed(data['displayed'])
        if 'selected' in data:
            self._update_selected(data['selected'])
        if 'huts_data' in data:
            self._update_huts_data(data['huts_data'])
        if 'filter_displayed_keys' in data:
            self._update_filter_displayed_keys(data['filter_displayed_keys'])
        if 'reference_location' in data:
            self._update_reference_location(data['reference_location'])
        if 'dates' in data:
            self._update_dates(data['dates'])
        if 'retrieve_enabled' in data:
            self._update_gui_for_retrieve_enabled(data['retrieve_enabled'])
        if 'language' in data:
            self._update_gui_for_language()
        if 'config' in data:
            self._update_gui_for_config()

    def _update_displayed(self, displayed):
        """Update the displayed huts.

        :param displayed: the indexes of the huts to display.
        """
        raise NotImplementedError

    def _update_selected(self, data):
        """Update the selected huts.

        :param data: tuple of indexes of the selected huts currently shown and of all the selected huts
        """
        raise NotImplementedError

    def _update_huts_data(self, data):
        """Update the huts information with the provided data.

        :param data: the data to use to update the huts information
        """
        raise NotImplementedError

    def _update_reference_location(self, location):
        """Update the reference location to a new position.

        :param location: the new position of the reference location
        """
        raise NotImplementedError

    def _update_filter_displayed_keys(self, filter_displayed_keys):
        """Update the view based on the filters applied to the displayed huts.

        :param filter_displayed_keys: the information about the filters applied to the displayed huts.
        """
        raise NotImplementedError

    def _update_dates(self, request_dates):
        """Update the view based on the request dates.

        :param request_dates: the request dates
        """
        self._date_widget.selected_date = request_dates[0]
        self._number_days_widget.value = len(request_dates)

    def _update_gui_for_language(self):
        """Update the frame using the current selected language."""
        self._date_widget.set_language(i18n.get_current_language_code())

    def _update_gui_for_config(self):
        """Update the frame using the configuration data."""
        self._number_days_widget.max_value = config.MAX_NIGHTS

    def _on_dates_selected(self, _obj):
        """Update the selected request dates."""
        date = self._date_widget.selected_date
        data = {'request_date': date,
                'number_days': self._number_days_widget.value}
        self._controller.command_update_dates(data)

    def _other_view_menu(self, menu_main):
        """Create the menu entry for the other type of main frame and append it to the menu.

        :param menu_main: the menu to which to append
        """
        raise NotImplementedError()

    def post_after_updates_event(self, all_updates, update_cancelled):
        """Trigger the event after an update to allow the use of the retrieved updates.

        :param all_updates: the information about the retrieved updates
        :param update_cancelled: boolean defining if the update has been cancelled
        """
        self.event_trigger(self._after_update_event, all_updates=all_updates, update_cancelled=update_cancelled)

    def _on_after_update(self, all_updates, update_cancelled):
        """Open the dialog used to command the execution of updates.

        :param all_updates: the information about the retrieved updates
        :param update_cancelled: boolean defining if the update has been cancelled
        """
        self._controller.command_open_update_dialog(self, all_updates, update_cancelled)

    def _create_date_gui(self):
        """Create the compound widget used to select the request dates.

        :return: the layout containing the compound widget
        """
        widget_sizer = VBoxLayout()
        widget_sizer.add(self._request_date_label, align=Align.EXPAND, border=(10, 10, 0, 10))
        widget_sizer.add(self._date_widget, align=Align.EXPAND, border=(0, 10, 10, 10))
        widget_sizer.add(self._number_days_label, align=Align.EXPAND, border=(10, 10, 0, 10))
        widget_sizer.add(self._number_days_widget, align=Align.EXPAND, border=(0, 10, 10, 10))
        return widget_sizer

    def _on_response_check(self, _obj):
        """Filter the displayed and selected huts based on the response status"""
        data = {'which': 'displayed', 'key': 'response', 'parameters': None}
        self._controller.command_filter(data)
        data = {'which': 'selected', 'key': 'response', 'parameters': None}
        self._controller.command_filter(data)

    def _on_closed_check(self, _obj):
        """Filter the displayed and selected huts based on the closed/open status"""
        data = {'which': 'displayed', 'key': 'open', 'parameters': None}
        self._controller.command_filter(data)
        data = {'which': 'selected', 'key': 'open', 'parameters': None}
        self._controller.command_filter(data)


class HutsTableView(_HutsView):
    """Define the main frame with huts information in table form.

    Methods:
        From superclass:
        title: return the title of the frame
        icon: return the icon of the frame
        show: show the frame
        hide: hide the frame
        set_focus: set the focus of the frame
        set_cursor: set the cursor shape
        close: close the frame
        on_close: executed when the frame is closed
        update_gui: update the frame content
        on_update_gui: executed when updating the frame content
        set_layout: set the layout of the frame
        event_connect: connect an event to a function
        event_trigger: trigger the event
    """

    _TABLE_VIEW_SIZE = (1000, 600)
    _SELECTED_GRID_HEIGHT = 240

    def __init__(self, *, parent=None, **kwargs):
        """Initialise the frame.

        :param parent: the parent frame (None if it is the main application frame)
        :param kwargs: additional parameters for superclass
        """
        self._keys = ['name',
                      'country',
                      'region',
                      'mountain_range',
                      'self_catering',
                      'height',
                      'distance',
                      'available'] + ROOM_TYPES

        self._filter_type_for_key = {'name': None,
                                     'country': 'select',
                                     'region': 'select',
                                     'mountain_range': 'select',
                                     'self_catering': 'bool',
                                     'height': 'minmax',
                                     'distance': 'minmax',
                                     'data_requested': 'bool',
                                     'response': 'bool',
                                     'open': 'bool',
                                     'available': 'minmax'}
        for room in ROOM_TYPES:
            self._filter_type_for_key[room] = 'minmax'

        self._filter_keys = {'displayed': {}, 'selected': {}}
        self._displayed = None
        self._selected = None
        self._columns_width_to_reset = False
        super().__init__(parent=parent, size=self._TABLE_VIEW_SIZE, title=i18n.all_strings['title'], **kwargs)
        self._create_gui()

    def on_update_gui(self, data):
        """Update the frame with the provided data.

        :param data: the data to use to update the frame
        """
        if 'filter_selected_keys' in data:
            self._update_filter_selected_keys(data['filter_selected_keys'])
        if 'sort_displayed_key' in data:
            self._update_sort_displayed_key(data['sort_displayed_key'])
        if 'sort_selected_key' in data:
            self._update_sort_selected_key(data['sort_selected_key'])
        if 'columns_width' in data:
            self._columns_width_to_reset = True
        super().on_update_gui(data)
        if self._columns_width_to_reset:
            self._reset_columns_width()
            self._columns_width_to_reset = False
        self._grid_displayed.refresh()
        self._grid_selected.refresh()

    def _reset_columns_width(self):
        """Sets the width of the columns of the two tables based on the content."""
        self._grid_displayed.unfreeze_cols_width()
        self._grid_displayed.refresh()
        self._grid_displayed.freeze_cols_width()
        self._grid_selected.set_cols_width_as(self._grid_displayed)

    def _other_view_menu(self, menu_main):
        """Create the menu entry for the other type of main frame and append it to the menu.

        :param menu_main: the menu to which to append
        """
        label = ast.literal_eval(i18n.all_strings['menu map view'])[0]
        menu_main.append(label, on_item_click=self._on_map_view)

    def _on_map_view(self):
        """Open a frame with the map view."""
        if self.parent is not None and isinstance(self.parent, HutsMapView):
            self.parent.set_focus()
            return
        for child_view in self.child_views:
            if isinstance(child_view, HutsMapView):
                child_view.set_focus()
                return
        self._controller.command_open_map_view(parent=self)

    def _create_grid(self, grid_id):
        """Create a table (for displayed or selected huts).

        :param grid_id: the type of table (displayed or selected huts)
        :return: the created table
        """
        grid = HutsGrid(self)
        grid.grid_id = grid_id

        grid.on_cell_left_double_click = self._command_select
        grid.on_cell_right_click = self._hut_pop_up_menu
        grid.on_label_left_click = self._command_sort
        grid.on_label_right_click = self._command_filter

        return grid

    def _create_widgets(self):
        """Create all the widgets of the frame."""
        self._create_date_widgets()

        self._checkbox_no_response = CheckBox(parent=self,
                                              on_click=self._on_response_check)

        self._checkbox_closed = CheckBox(parent=self,
                                         on_click=self._on_closed_check)

        self._grid_displayed = self._create_grid('displayed')
        self._grid_displayed.update_data(keys=self._keys)

        self._selected_huts_label = Text(parent=self)

        self._grid_selected = self._create_grid('selected')
        self._grid_selected.update_data(keys=self._keys)

        self._retrieve_info_label = Text(parent=self)

        self._get_displayed_results_button = Button(parent=self,
                                                    on_click=self._on_get_huts_info_displayed)

        self._get_selected_results_button = Button(parent=self,
                                                   on_click=self._on_get_huts_info_selected)

        self._reference_label = Text(parent=self)

        self._latitude_label = Text(parent=self)

        self._latitude_widget = TextControl(parent=self)

        self._longitude_label = Text(parent=self)

        self._longitude_widget = TextControl(parent=self)

        self._set_location_button = Button(parent=self,
                                           on_click=self._on_update_location_button)

        self._close_button = Button(parent=self,
                                    on_click=self._on_button_command_close)

    def _update_gui_for_retrieve_enabled(self, is_enabled):
        """Update the frame based on the enabling status of the data retrieval.

        :param is_enabled: boolean defining if the data retrieval is enabled
        """
        self._get_displayed_results_button.enable(is_enabled)
        self._get_selected_results_button.enable(is_enabled)
        super()._update_gui_for_retrieve_enabled(is_enabled)

    def _update_gui_for_language(self):
        """Update the frame using the current selected language."""
        super()._update_gui_for_language()
        self._create_menu()
        self.title = i18n.all_strings['title']
        self._checkbox_no_response.label = i18n.all_strings['hide no response']
        self._checkbox_closed.label = i18n.all_strings['hide closed']
        self._selected_huts_label.label = i18n.all_strings['selected huts']
        self._request_date_label.label = i18n.all_strings['request date']
        self._number_days_label.label = i18n.all_strings['number of days']
        self._retrieve_info_label.label = i18n.all_strings['retrieve info']
        self._get_displayed_results_button.label = i18n.all_strings['retrieve displayed']
        self._get_selected_results_button.label = i18n.all_strings['retrieve selected']
        self._reference_label.label = i18n.all_strings['reference']
        self._latitude_label.label = i18n.all_strings['latitude']
        self._longitude_label.label = i18n.all_strings['longitude']
        self._set_location_button.label = i18n.all_strings['update location']
        self._close_button.label = i18n.all_strings['close table view']

    def _update_filter_displayed_keys(self, filter_displayed_keys):
        """Update the view based on the filters applied to the displayed huts.

        :param filter_displayed_keys: the information about the filters applied to the displayed huts
        """
        self._filter_keys['displayed'] = filter_displayed_keys
        self._checkbox_closed.value = 'open' in filter_displayed_keys
        self._checkbox_no_response.value = 'response' in filter_displayed_keys
        self._grid_displayed.update_data(filter_keys=filter_displayed_keys)

    def _update_filter_selected_keys(self, filter_selected_keys):
        """Update the view based on the filters applied to the selected huts.

        :param filter_selected_keys: the information about the filters applied to the selected huts
        """
        self._filter_keys['selected'] = filter_selected_keys
        self._grid_selected.update_data(filter_keys=filter_selected_keys)

    def _update_sort_displayed_key(self, sort_displayed_params):
        """Update the view based on the sort key and order applied to the displayed huts.

        :param sort_displayed_params: the information about sort key and order applied to the displayed huts
        """
        self._grid_displayed.update_data(sort_key=sort_displayed_params[0], sort_ascending=sort_displayed_params[1])

    def _update_sort_selected_key(self, sort_selected_params):
        """Update the view based on the sort key and order applied to the selected huts.

        :param sort_selected_params: the information about sort key and order applied to the selected huts
        """
        self._grid_selected.update_data(sort_key=sort_selected_params[0], sort_ascending=sort_selected_params[1])

    def _update_huts_data(self, huts_data):
        """Update the huts information with the provided data.

        :param huts_data: the data to use to update the huts information
        """
        self._grid_displayed.update_data(data_dictionary=huts_data)
        self._grid_selected.update_data(data_dictionary=huts_data)

    def _update_displayed(self, displayed):
        """Update the displayed huts.

        :param displayed: the indexes of the huts to display.
        """
        self._displayed = displayed
        self._grid_displayed.update_data(indexes=displayed)

    def _update_selected(self, data):
        """Update the selected huts.

        :param data: tuple of indexes of the selected huts currently shown and of all the selected huts
        """
        selected, all_selected = data
        self._selected = selected
        self._grid_displayed.update_data(selected=all_selected)
        self._grid_selected.update_data(selected)

    def _update_reference_location(self, location):
        """Update the reference location to a new position.

        :param location: the new position of the reference location
        """
        self._latitude_widget.label = '{0:.5f}'.format(location['lat'])
        self._longitude_widget.label = '{0:.5f}'.format(location['lon'])

    def _on_get_huts_info_displayed(self, _obj):
        """Command the retrieval of huts data for all displayed huts."""
        data = {'which': 'displayed'}
        self._controller.command_update_results(data)

    def _on_get_huts_info_selected(self, _obj):
        """Command the retrieval of huts data for all selected huts."""
        data = {'which': 'selected'}
        self._controller.command_update_results(data)

    def _on_update_location_button(self, _obj):
        """Command the update of the reference position."""
        try:
            lat = float(self._latitude_widget.label)
            lon = float(self._longitude_widget.label)
            if -90. < lat < 90. and -180. < lon < 180.:
                data = {'which': 'latlon', 'lat': lat, 'lon': lon}
                self._controller.command_update_reference_location(data)
            else:
                raise ValueError()
        except ValueError:
            with MessageDialog(parent=self, title=i18n.all_strings['error'],
                               message=i18n.all_strings['invalid location']) as dialog:
                dialog.show_modal()

    def _command_select(self, obj, row, _col):
        """Command the selection/deselection of a hut.

        :param obj: the table where the hut has been clicked (displayed or selected)
        :param row: the row index of the hut
        """
        if obj.grid_id == 'displayed':
            index = self._displayed[row]
        else:
            index = self._selected[row]
        data = {'which': index}
        self._controller.command_select(data)

    def _command_sort(self, obj, _row, col):
        """Command the sorting of a table.

        :param obj: the table to be sorted (displayed or selected)
        :param col: the column of the key to be used to sort
        """
        key = self._keys[col]
        data = {'which': obj.grid_id, 'key': key}
        self._controller.command_sort(data)

    def _command_filter(self, obj, _row, col):
        """Command the filtering of a table.

        :param obj: the table to be filtered (displayed or selected)
        :param col: the column of the key to be used to filter
        """
        key = self._keys[col]
        filter_type = self._filter_type_for_key[key]
        parameters = None
        if key in self._filter_keys[obj.grid_id]:
            filter_dict = {i18n.all_strings['remove filter']: None}
            parameters = self._filter_pop_up_menu(filter_dict)
        elif filter_type == 'select':
            filter_dict = obj.get_values_for_filter(key)
            parameters = self._filter_pop_up_menu(filter_dict)
        elif filter_type == 'bool':
            filter_dict = {i18n.all_strings['yes']: True, i18n.all_strings['no']: False}
            parameters = self._filter_pop_up_menu(filter_dict)
        elif filter_type == 'minmax':
            parameters = self._value_entry(key)
        if parameters is None:
            return
        data = {'which': obj.grid_id, 'key': key, 'parameters': parameters}
        self._controller.command_filter(data)

    def _filter_pop_up_menu(self, filter_dict):
        """Create and show the pop-up menu for the table filtering and returns the selection.

        :param filter_dict: the dictionary with entries for the pop-up menu
        :return: the value selected for the filtering
        """
        menu_labels = sorted(list(filter_dict))

        self._menu_chosen_item = None
        menu = Menu(parent=self, items=menu_labels, on_click=self._on_menu_item)
        menu.pop_up()

        if self._menu_chosen_item is not None:
            return {'value': filter_dict[self._menu_chosen_item]}
        else:
            return None

    def _value_entry(self, key):
        """Create and show a dialog to read the minimum and maximum values to be used for filtering.

        :param key: the key to which the filter is applied
        :return: the entered minimum and maximum values
        """
        title = i18n.all_strings['filter'].format(i18n.all_strings[key])

        with FilterDialog(parent=self, title=title) as dialog:
            result = dialog.show_modal()
            if result:
                min_value, max_value = dialog.filter_values
                if min_value is None and max_value is None:
                    return None
                else:
                    return {'min': min_value, 'max': max_value}
            else:
                return None

    def _hut_pop_up_menu(self, obj, row, _col):
        """Create and show the pop-up menu for a hut.

        :param obj: the table where the hut has been clicked (displayed or selected)
        :param row: the row index of the hut
        """
        if obj.grid_id == 'displayed':
            index = self._displayed[row]
        else:
            index = self._selected[row]

        menu_labels = []
        select_label = i18n.all_strings['select'] if index not in self._selected \
            else i18n.all_strings['deselect']
        menu_labels.append(select_label)
        menu_labels.append(i18n.all_strings['show details'])
        if self._retrieve_enabled:
            menu_labels.append(i18n.all_strings['retrieve'])
        menu_labels.append(Menu.SEPARATOR)
        menu_labels.append(i18n.all_strings['set location'])
        menu_labels.append(i18n.all_strings['open web'])
        menu_labels.append(i18n.all_strings['open booking'])
        menu_labels.append(Menu.SEPARATOR)
        select_all_label = i18n.all_strings['select all'] if obj.grid_id == 'displayed' \
            else i18n.all_strings['deselect all']
        menu_labels.append(select_all_label)
        if obj.grid_id == 'selected':
            menu_labels.append(Menu.SEPARATOR)
            menu_labels.append(i18n.all_strings['show details selected'])

        self._menu_chosen_item = None
        menu = Menu(parent=self, items=menu_labels, on_click=self._on_menu_item)
        menu.pop_up()

        if self._menu_chosen_item == select_label:
            self._controller.command_select({'which': index})
        elif self._menu_chosen_item == i18n.all_strings['show details']:
            self._controller.command_open_info_frame(index, self)
        elif self._menu_chosen_item == i18n.all_strings['retrieve']:
            self._controller.command_update_results({'which': 'huts', 'indexes': [index]})
        elif self._menu_chosen_item == i18n.all_strings['set location']:
            self._controller.command_update_reference_location({'which': 'hut', 'index': index})
        elif self._menu_chosen_item == i18n.all_strings['open web']:
            self._controller.command_open_hut_page({'which': index})
        elif self._menu_chosen_item == i18n.all_strings['open booking']:
            self._controller.command_open_book_page({'which': index})
        elif self._menu_chosen_item == select_all_label:
            data = {'which': obj.grid_id}
            self._controller.command_select_all(data)
        elif self._menu_chosen_item == i18n.all_strings['show details selected']:
            self._controller.command_open_selected_frame(self)
        else:
            return

    def _on_menu_item(self, obj, choice_id):
        """Executed when a menu item is clicked.

        :param obj: the clicked menu
        :param choice_id: the index of the clicked item
        """
        self._menu_chosen_item = obj.get_item_label(choice_id)

    def _create_gui(self):
        """Build the view by creating all widgets, positioning them in a layout and setting this as frame layout."""
        self._create_widgets()
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
        main_sizer.add(box_left, align=Align.EXPAND, stretch=1)
        main_sizer.add(box_right, align=Align.EXPAND)
        self.set_layout(main_sizer)


class HutsMapView(_HutsView):
    """Define the main frame with huts information in the map.

    Methods:
        From superclass:
        title: return the title of the frame
        icon: return the icon of the frame
        show: show the frame
        hide: hide the frame
        set_focus: set the focus of the frame
        set_cursor: set the cursor shape
        close: close the frame
        on_close: executed when the frame is closed
        update_gui: update the frame content
        on_update_gui: executed when updating the frame content
        set_layout: set the layout of the frame
        event_connect: connect an event to a function
        event_trigger: trigger the event
    """

    _STYLE = FrameStyle.FIXED_SIZE

    _DEFAULT_MAP_WINDOW = [46.0, 52.0, 4.5, 16.5]  # [degrees]
    _MAP_X_PIXEL_DIMENSION = 550
    _MAP_Y_PIXEL_DIMENSION = 550
    _DEFAULT_MAP_ZOOM = 6
    _MAP_MIN_ZOOM = 6
    _MAP_MAX_ZOOM = 13

    def __init__(self, *, parent=None, **kwargs):
        """Initialise the frame.

        :param parent: the parent frame (None if it is the main application frame)
        :param kwargs: additional parameters for superclass
        """
        self._huts_data = None
        self._hut_map = None
        self._info_pop_up = None
        self._pop_up_group = None
        self._left_drag_start = None
        self._right_drag_start = None
        self._measure_distance_start = None
        self._keep_window = False
        self._reference_location = None
        self._displayed = None
        self._selected = None
        super().__init__(parent=parent, title=i18n.all_strings['map title'], **kwargs)
        self._create_gui()

    def _create_widgets(self):
        """Build the view by creating all widgets and positioning them in a layout."""
        self._hut_map = NavigableMap(self._MAP_X_PIXEL_DIMENSION, self._MAP_Y_PIXEL_DIMENSION,
                                     self._DEFAULT_MAP_ZOOM, self._MAP_MIN_ZOOM, self._MAP_MAX_ZOOM,
                                     self._DEFAULT_MAP_WINDOW)

        self._bitmap = Bitmap(parent=self, bitmap=self._hut_map.get_map_image())
        self._bitmap.on_left_down = self._on_left_down
        self._bitmap.on_left_up = self._on_left_up
        self._bitmap.on_right_down = self._on_right_down
        self._bitmap.on_right_up = self._on_right_up
        self._bitmap.on_mouse_motion = self._on_mouse_motion
        self._bitmap.on_mouse_leave = self._on_mouse_leave
        self._bitmap.on_wheel = self._on_mouse_wheel

        self._create_date_widgets()

        self._get_results_button = Button(parent=self,
                                          on_click=self._on_get_huts_info)

        self._checkbox_no_response = CheckBox(parent=self,
                                              on_click=self._on_response_check)

        self._checkbox_closed = CheckBox(parent=self,
                                         on_click=self._on_closed_check)

        self._checkbox_reference = CheckBox(parent=self,
                                            on_click=self._on_reference_check)

        self._huts_choice = RadioBox(parent=self,
                                     num_choices=2,
                                     on_click=self._on_huts_choice)

        self._fit_button = Button(parent=self,
                                  on_click=self._on_fit_button)

        self._close_button = Button(parent=self,
                                    on_click=self._on_button_command_close)

    def _other_view_menu(self, menu_main):
        """Create the menu entry for the other type of main frame and append it to the menu.

        :param menu_main: the menu to which to append
        """
        label = ast.literal_eval(i18n.all_strings['menu table view'])[0]
        menu_main.append(label, on_item_click=self._on_table_view)

    def _on_table_view(self):
        """Open a frame with the table view."""
        if self.parent is not None and isinstance(self.parent, HutsTableView):
            self.parent.set_focus()
            return
        for child_view in self.child_views:
            if isinstance(child_view, HutsTableView):
                child_view.set_focus()
                return
        self._controller.command_open_table_view(parent=self)

    def _on_reference_check(self, _obj):
        """Hide or show the reference location widget based on the checkbox selection."""
        self._show_reference_location()

    def _on_get_huts_info(self, _obj):
        """Command the retrieval of huts data for all huts shown on the map."""
        data = {'which': 'displayed' if self._huts_choice.selection == 0 else 'selected'}
        self._controller.command_update_results(data)

    def on_update_gui(self, data):
        """Update the frame with the provided data.

        :param data: the data to use to update the frame
        """
        super().on_update_gui(data)
        self._update_shown_huts()

    def _update_huts_data(self, huts_data):
        """Update the huts information with the provided data.

        :param huts_data: the data to use to update the huts information
        """
        self._huts_data = huts_data

    def _on_huts_choice(self, _obj):
        """Show on the map all the displayed or only the selected huts based on the checkbox selection."""
        self._update_shown_huts()

    def _update_shown_huts(self):
        """Update the huts shown on the map."""
        if self._huts_choice.selection == 0:
            huts_data = {index: self._huts_data[index] for index in self._displayed}
        else:
            huts_data = {index: self._huts_data[index] for index in self._selected}
        self._hut_map.update_huts_data(huts_data)
        self._update_map()

    def _update_filter_displayed_keys(self, filter_displayed_keys):
        """Update the view based on the filters applied to the displayed huts.

        :param filter_displayed_keys: the information about the filters applied to the displayed huts.
        """
        self._checkbox_closed.value = 'open' in filter_displayed_keys
        self._checkbox_no_response.value = 'response' in filter_displayed_keys

    def _update_map(self):
        """Regenerate and update the displayed map."""
        self._bitmap.bitmap = self._hut_map.get_map_image()

    def _update_selected(self, data):
        """Update the selected huts.

        :param data: tuple of indexes of the selected huts currently shown and of all the selected huts
        """
        selected, all_selected = data
        self._selected = selected

    def _update_displayed(self, displayed):
        """Update the displayed huts.

        :param displayed: the indexes of the huts to display.
        """
        self._displayed = displayed

    def _update_reference_location(self, location):
        """Update the reference location to a new position.

        :param location: the new position of the reference location
        """
        self._reference_location = location
        self._show_reference_location()

    def _show_reference_location(self):
        """Show or hide the widget of the reference location based on the checkbox selection."""
        if self._checkbox_reference.value:
            self._hut_map.show_reference_location(self._reference_location['lat'],
                                                  self._reference_location['lon'])
        else:
            self._hut_map.hide_reference_location()
        self._update_map()

    def _on_fit_button(self, _obj):
        """Zoom the map to fit on the currently shown huts."""
        if self._huts_choice.selection == 0:
            self._update_zoom_from_huts({index: self._huts_data[index] for index in self._displayed})
        else:
            self._update_zoom_from_huts({index: self._huts_data[index] for index in self._selected})
        self._update_map()

    def _get_window_boundaries(self, position):
        """Get the coordinates of the window selected with the mouse on the map.

        :param position: the position of the mouse when the window selected is finalized
        :return: the four coordinates defining the limits of the selected window
        """
        start_lat, start_lon = self._hut_map.get_lat_lon_from_pixel(*self._right_drag_start)
        end_lat, end_lon = self._hut_map.get_lat_lon_from_pixel(*position)
        lat_min = min(start_lat, end_lat)
        lat_max = max(start_lat, end_lat)
        lon_min = min(start_lon, end_lon)
        lon_max = max(start_lon, end_lon)
        return lat_min, lat_max, lon_min, lon_max

    def _on_left_down(self, _obj, position):
        """Executed when the left mouse button is pressed down while the cursor is on the map.

        :param position: the position of the mouse
        """
        if self._measure_distance_start is not None:
            self._measure_distance_start = None
            self._hut_map.hide_ruler()
            self._update_map()
            return
        elif self._info_pop_up is not None:
            self._info_pop_up.force_close()
        delta_zoom = self._hut_map.check_zoom(*position)
        if delta_zoom != 0:
            self._hut_map.update_zoom_from_widget(delta_zoom)
            self._update_map()
            return
        huts = self._hut_map.get_huts_from_pixel(*position)
        if huts:
            if len(huts) == 1:
                self._hut_menu(huts[0])
            else:
                self._multi_hut_menu(huts)
        else:
            self._left_drag_start = position
            self.map_center = self._hut_map.get_lat_lon_map_center()
            self.set_cursor(CursorStyle.SIZING)

    def _on_left_up(self, _obj, _position):
        """Executed when the left mouse button is released while the cursor is on the map."""
        self._left_drag_start = None
        self.set_cursor(CursorStyle.ARROW)

    def _on_right_down(self, _obj, position):
        """Executed when the right mouse button is pressed down while the cursor is on the map.

        :param position: the position of the mouse
        """
        if self._measure_distance_start is not None:
            self._measure_distance_start = None
            self._hut_map.hide_ruler()
            self._update_map()
            return
        elif self._info_pop_up is not None:
            self._info_pop_up.force_close()
        huts = self._hut_map.get_huts_from_pixel(*position)
        if huts:
            if len(huts) == 1:
                self._hut_menu(huts[0])
            else:
                self._multi_hut_menu(huts)
        else:
            self._right_drag_start = position

    def _on_right_up(self, _obj, position):
        """Executed when the right mouse button is released while the cursor is on the map.

        :param position: the position of the mouse
        """
        if self._right_drag_start is not None:
            if position == self._right_drag_start:
                self._point_menu(*self._hut_map.get_lat_lon_from_pixel(*position))
            else:
                self._keep_window = True
                self._window_menu(*self._get_window_boundaries(position))
                self._keep_window = False
        self._right_drag_start = None

    def _on_mouse_motion(self, _obj, position):
        """Executed when the mouse is moved while the cursor is on the map.

        :param position: the position of the mouse
        """
        if self._left_drag_start is not None:
            delta_x_pixel = self._left_drag_start[0] - position[0]
            delta_y_pixel = self._left_drag_start[1] - position[1]
            delta_lat, delta_lon = self._hut_map.get_delta_lat_lon_from_delta_pixel(delta_x_pixel, delta_y_pixel)
            new_center_lat = self.map_center[0] + delta_lat
            new_center_lon = self.map_center[1] + delta_lon
            self._hut_map.update_center_point(new_center_lat, new_center_lon)
            self._update_map()
        elif self._right_drag_start is not None:
            self._hut_map.show_window(*self._get_window_boundaries(position))
            self._update_map()
        elif self._measure_distance_start is not None:
            start_lat, start_lon = self._measure_distance_start
            end_lat, end_lon = self._hut_map.get_lat_lon_from_pixel(*position)
            self._hut_map.show_ruler(start_lat, start_lon, end_lat, end_lon)
            self._update_map()
        else:
            huts = self._hut_map.get_huts_from_pixel(*position)
            if len(huts) > 0:
                if self._info_pop_up is None:
                    self._info_pop_up = self._get_info_pop_up(huts)
                    self._info_pop_up.pop_up()
                elif huts[0] == self._pop_up_group:
                    self._info_pop_up.prevent_close()
                else:
                    self._info_pop_up.force_close()
                    self._info_pop_up = self._get_info_pop_up(huts)
                    self._info_pop_up.pop_up()
            else:
                if self._info_pop_up is not None:
                    self._info_pop_up.command_close()

    def _on_mouse_leave(self, _obj):
        """Executed when the mouse leaves the map."""
        if self._info_pop_up is not None:
            self._info_pop_up.command_close()
        self._left_drag_start = None
        self.set_cursor(CursorStyle.ARROW)
        self._right_drag_start = None
        if not self._keep_window:
            self._hut_map.hide_window()
        self._measure_distance_start = None
        self._hut_map.hide_ruler()
        self._update_map()

    def _get_info_pop_up(self, huts):
        """Create the information pop-up menu for multiple huts.

        :param huts: the huts in the group for which the pop-up menu is created
        :return: the pop-up menu object
        """
        menu_items = []
        for i, hut in enumerate(huts):
            menu_items.append((self._huts_data[hut]['name'] + " (" + str(int(self._huts_data[hut]['height'])) + " m)",
                               True, lambda h=hut: self._hut_menu(h)))
        self._pop_up_group = huts[0]
        info_pop_up = TextTimedMenu(parent=self, items=menu_items)
        info_pop_up.on_close = self._on_close_pop_up
        return info_pop_up

    def _on_close_pop_up(self, _obj):
        """Executed when the pop-up menu is closed."""
        self._info_pop_up = None
        self._pop_up_group = None

    def _window_menu(self, lat_min, lat_max, lon_min, lon_max):
        """Create and show the pop-up menu for a selected window.

        :param lat_min: minimum latitude of the window
        :param lat_max: maximum latitude of the window
        :param lon_min: minimum longitude of the window
        :param lon_max: maximum longitude of the window
        """
        menu_labels = []
        menu_labels.append(i18n.all_strings['zoom to window'])
        select_label = i18n.all_strings['select in window'] \
            if self._huts_choice.selection == 0 else i18n.all_strings['deselect in window']
        menu_labels.append(select_label)
        if self._huts_choice.selection == 1:
            menu_labels.append(i18n.all_strings['select only in window'])

        self._menu_chosen_item = None
        menu = Menu(parent=self, items=menu_labels, on_click=self._on_menu_item)
        menu.pop_up()

        self._hut_map.hide_window()
        if self._menu_chosen_item == i18n.all_strings['zoom to window']:
            self._hut_map.update_zoom_from_window(lat_min, lat_max, lon_min, lon_max)
            self._update_map()
        elif self._menu_chosen_item == select_label:
            data = {
                'which': self._displayed if self._huts_choice.selection == 0 else self._selected,
                'window':  (lat_min, lat_max, lon_min, lon_max),
                'type': 'select' if self._huts_choice.selection == 0 else 'deselect'
            }
            self._controller.command_select_window(data)
        elif self._menu_chosen_item == i18n.all_strings['select only in window']:
            data = {
                'which': self._selected,
                'window':  (lat_min, lat_max, lon_min, lon_max),
                'type': 'select only'
            }
            self._controller.command_select_window(data)
        else:
            return

    def _hut_menu(self, index):
        """Create and show the pop-up menu for a hut.

        :param index: the index of the hut
        """
        hut_info = self._huts_data[index]

        menu_labels = []
        name_label = hut_info['name']
        menu_labels.append((name_label, False, None))
        menu_labels.append(Menu.SEPARATOR)
        select_label = i18n.all_strings['select'] \
            if index not in self._selected else i18n.all_strings['deselect']
        menu_labels.append(select_label)
        menu_labels.append(i18n.all_strings['show details'])
        if self._retrieve_enabled:
            menu_labels.append(i18n.all_strings['retrieve'])
        menu_labels.append(Menu.SEPARATOR)
        menu_labels.append(i18n.all_strings['open web'])
        menu_labels.append(i18n.all_strings['open booking'])
        menu_labels.append(i18n.all_strings['zoom on hut'])
        menu_labels.append(Menu.SEPARATOR)
        menu_labels.append(i18n.all_strings['set location'])
        menu_labels.append(i18n.all_strings['measure distance'])

        self._menu_chosen_item = None
        menu = Menu(parent=self, items=menu_labels, on_click=self._on_menu_item)
        menu.pop_up()

        if self._menu_chosen_item == select_label:
            self._controller.command_select({'which': index})
        elif self._menu_chosen_item == i18n.all_strings['show details']:
            self._controller.command_open_info_frame(index, self)
        elif self._menu_chosen_item == i18n.all_strings['retrieve']:
            self._controller.command_update_results({'which': 'huts', 'indexes': [index]})
        elif self._menu_chosen_item == i18n.all_strings['set location']:
            self._controller.command_update_reference_location({'which': 'hut', 'index': index})
        elif self._menu_chosen_item == i18n.all_strings['open web']:
            self._controller.command_open_hut_page({'which': index})
        elif self._menu_chosen_item == i18n.all_strings['open booking']:
            self._controller.command_open_book_page({'which': index})
        elif self._menu_chosen_item == i18n.all_strings['zoom on hut']:
            huts_data = {index: self._huts_data[index]}
            self._update_zoom_from_huts(huts_data)
            self._update_map()
        elif self._menu_chosen_item == i18n.all_strings['measure distance']:
            self._measure_distance_start = hut_info['lat'], hut_info['lon']
        else:
            return

    def _update_zoom_from_huts(self, huts_data):
        """Zoom the map on one or more huts.

        :param huts_data: dictionary containing the information about the huts
        """
        lat_min = min(hut_data['lat'] for hut_data in huts_data.values())
        lat_max = max(hut_data['lat'] for hut_data in huts_data.values())
        lon_min = min(hut_data['lon'] for hut_data in huts_data.values())
        lon_max = max(hut_data['lon'] for hut_data in huts_data.values())

        self._hut_map.update_zoom_from_window(lat_min, lat_max, lon_min, lon_max)

    def _multi_hut_menu(self, indexes):
        """Create and show the pop-up menu for a group of huts.

        :param indexes: the indexes of the huts in the group
        """
        menu_labels = []
        select_all_label = i18n.all_strings['select all group'] \
            if self._huts_choice.selection == 0 else i18n.all_strings['deselect all group']
        menu_labels.append(select_all_label)
        menu_labels.append(i18n.all_strings['zoom on group'])
        if self._retrieve_enabled:
            menu_labels.append(i18n.all_strings['retrieve group'])

        self._menu_chosen_item = None
        menu = Menu(parent=self, items=menu_labels, on_click=self._on_menu_item)
        menu.pop_up()

        if self._menu_chosen_item == select_all_label:
            data = {
                'which': indexes,
                'type': 'select' if self._huts_choice.selection == 0 else 'deselect'
            }
            self._controller.command_select_multi(data)
        elif self._menu_chosen_item == i18n.all_strings['zoom on group']:
            huts_data = {index: self._huts_data[index] for index in indexes}
            self._update_zoom_from_huts(huts_data)
            self._update_map()
        elif self._menu_chosen_item == i18n.all_strings['retrieve group']:
            self._controller.command_update_results({'which': 'huts', 'indexes': indexes})
        else:
            return

    def _point_menu(self, lat, lon):
        """Create and show the pop-up menu for a point on the map.

        :param lat: the latitude of the point
        :param lon: the longitude of the point
        """
        menu_labels = []
        menu_labels.append(i18n.all_strings['set location'])
        menu_labels.append(i18n.all_strings['measure distance'])
        menu_labels.append(Menu.SEPARATOR)
        select_all_label = i18n.all_strings['select all shown'] if self._huts_choice.selection == 0 \
            else i18n.all_strings['deselect all shown']
        menu_labels.append(select_all_label)
        menu_labels.append(Menu.SEPARATOR)
        menu_labels.append(i18n.all_strings['show details selected'])

        self._menu_chosen_item = None
        menu = Menu(parent=self, items=menu_labels, on_click=self._on_menu_item)
        menu.pop_up()

        if self._menu_chosen_item == i18n.all_strings['set location']:
            self._controller.command_update_reference_location({'which': 'latlon', 'lat': lat, 'lon': lon})
        elif self._menu_chosen_item == i18n.all_strings['measure distance']:
            self._measure_distance_start = (lat, lon)
        elif self._menu_chosen_item == select_all_label:
            lat_min, lat_max, lon_min, lon_max = self._hut_map.get_lat_lon_map_limits()
            data = {
                'which': self._displayed if self._huts_choice.selection == 0 else self._selected,
                'window':  (lat_min, lat_max, lon_min, lon_max),
                'type': 'select' if self._huts_choice.selection == 0 else 'deselect'
            }
            self._controller.command_select_window(data)
        elif self._menu_chosen_item == i18n.all_strings['show details selected']:
            self._controller.command_open_selected_frame(self)
        else:
            return

    def _on_menu_item(self, obj, choice_id):
        """Executed when a menu item is clicked.

        :param obj: the clicked menu
        :param choice_id: the index of the clicked item
        """
        self._menu_chosen_item = obj.get_item_label(choice_id)

    def _on_mouse_wheel(self, _obj, position, direction):
        """Update the zoom based on the mousewheel movement.

        :param position: the mouse position
        :param direction: the direction of the mousewheel movement
        """
        if self._info_pop_up is not None:
            self._info_pop_up.force_close()
        self._measure_distance_start = None
        self._hut_map.hide_ruler()
        self._left_drag_start = None
        self.set_cursor(CursorStyle.ARROW)
        self._right_drag_start = None
        self._hut_map.hide_window()
        self._hut_map.update_zoom_from_point(*self._hut_map.get_lat_lon_from_pixel(*position), direction)
        self._update_map()

    def _update_gui_for_retrieve_enabled(self, is_enabled):
        """Update the frame based on the enabling status of the data retrieval.

        :param is_enabled: boolean defining if the data retrieval is enabled
        """
        self._get_results_button.enable(is_enabled)
        super()._update_gui_for_retrieve_enabled(is_enabled)

    def _update_gui_for_language(self):
        """Update the frame using the current selected language."""
        super()._update_gui_for_language()
        self._create_menu()
        self.title = i18n.all_strings['title']
        self._request_date_label.label = i18n.all_strings['request date']
        self._number_days_label.label = i18n.all_strings['number of days']
        self._get_results_button.label = i18n.all_strings['retrieve shown']
        self._checkbox_no_response.label = i18n.all_strings['hide no response']
        self._checkbox_closed.label = i18n.all_strings['hide closed']
        self._checkbox_reference.label = i18n.all_strings['show reference']
        self._huts_choice.set_string(0, i18n.all_strings['show displayed'])
        self._huts_choice.set_string(1, i18n.all_strings['show selected'])
        self._fit_button.label = i18n.all_strings['fit zoom']
        self._close_button.label = i18n.all_strings['close map']

    def _create_gui(self):
        """Build the view by creating all widgets, positioning them in a layout and setting this as frame layout."""
        self._create_widgets()
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
        self.set_layout(main_sizer)


class DetailedInfoView(_HutsInfoFrame):
    """Define the frame with detailed information about a single hut.

    Methods:
        From superclass:
        title: return the title of the frame
        icon: return the icon of the frame
        show: show the frame
        hide: hide the frame
        set_focus: set the focus of the frame
        set_cursor: set the cursor shape
        close: close the frame
        on_close: executed when the frame is closed
        update_gui: update the frame content
        on_update_gui: executed when updating the frame content
        set_layout: set the layout of the frame
        event_connect: connect an event to a function
        event_trigger: trigger the event
    """

    _DETAILED_MAP_WIDTH = 60000  # [meters]
    _DETAILED_MAP_HEIGHT = 60000  # [meters]
    _DETAILED_MAP_REF_ZOOM = 9
    _DETAILED_MAP_MIN_ZOOM = 6
    _DETAILED_MAP_MAX_ZOOM = 13
    _STYLE = FrameStyle.FIXED_SIZE

    def __init__(self, *, index, hut_info, **kwargs):
        """Initialise the frame.

        :param index: the index of the hut
        :param hut_info: the information about the hut
        :param kwargs: additional parameters for superclass
        """
        self._index = index
        self._hut_info = hut_info
        self._hut_map = HutMap(self._hut_info['lat'], self._hut_info['lon'],
                               self._DETAILED_MAP_WIDTH, self._DETAILED_MAP_HEIGHT,
                               self._DETAILED_MAP_REF_ZOOM, self._DETAILED_MAP_MIN_ZOOM, self._DETAILED_MAP_MAX_ZOOM)
        super().__init__(title=i18n.all_strings['detailed info'], **kwargs)
        self._create_gui()
        self._self_catering_text.hide(not self._hut_info['self_catering'])
        self._hut_text.label = self._hut_info['name']

    def _create_widgets(self):
        """Create all the widgets of the frame."""
        self._hut_text = Text(parent=self, font_size=11, font_style=TextStyle.BOLD)

        self._country_text = Text(parent=self, font_size=10)

        self._mountain_text = Text(parent=self, font_size=10)

        self._height_text = Text(parent=self, font_size=10)

        self._self_catering_text = Text(parent=self, font_size=10)

        self._bitmap = Bitmap(parent=self)
        self._bitmap.on_wheel = self._on_wheel
        self._bitmap.on_left_down = self._on_click

        self._retrieve_info_button = Button(parent=self,
                                            on_click=self._on_retrieve_info)

        self._open_web_button = Button(parent=self,
                                       on_click=self._on_open_web)

        self._open_booking_button = Button(parent=self,
                                           on_click=self._on_open_booking)

        self._grid_detailed = DetailedGrid(self)

        self._close_button = Button(parent=self,
                                    on_click=self._on_button_close)

    def on_update_gui(self, data):
        """Update the frame with the provided data.

        :param data: the data to use to update the frame
        """
        if 'huts_data' in data:
            self._update_huts_data(data['huts_data'])
        if 'retrieve_enabled' in data:
            self._update_gui_for_retrieve_enabled(data['retrieve_enabled'])
        if 'language' in data:
            self._update_gui_for_language()
        self._grid_detailed.refresh()

    def _update_huts_data(self, huts_data):
        """Update the information about the hut.

        :param huts_data: the dictionary of information about all huts
        """
        self._hut_info = huts_data[self._index]
        self._hut_map.set_status(self._hut_info['status'])
        self._grid_detailed.update_data(self._hut_info)
        self._update_bitmap()

    def _on_button_close(self, _obj):
        """Close the frame."""
        self.close()

    def _update_zoom(self, direction):
        """Update the zoom of the map.

        :param direction: the direction of the zoom update (higher or lower zoom)
        """
        self._hut_map.update_zoom(direction)
        self._update_bitmap()

    def _on_retrieve_info(self, _obj):
        """Command the retrieval of huts data for the hut."""
        self._controller.command_update_results({'which': 'huts', 'indexes': [self._index]})

    def _on_open_web(self, _obj):
        """Open the information web page of the hut."""
        self._controller.command_open_hut_page({'which': self._index})

    def _on_open_booking(self, _obj):
        """Open the booking web page of the hut."""
        self._controller.command_open_book_page({'which': self._index})

    def _on_click(self, _obj, position):
        """Update the map zoom based on the click on the zoom icon in the map.

        :param position: the mouse position used to identify the requested zoom update
        """
        delta_zoom = self._hut_map.check_zoom(*position)
        if delta_zoom != 0:
            self._update_zoom(delta_zoom)

    def _on_wheel(self, _obj, _position, direction):
        """Update the map zoom based on the mousewheel movement.

        :param direction: the direction of the mousewheel movement (up or down)
        """
        self._update_zoom(direction)

    def _update_bitmap(self):
        """Generate and update the image with the map."""
        self._bitmap.bitmap = self._hut_map.get_map_image()

    def _update_gui_for_retrieve_enabled(self, is_enabled):
        """Update the frame based on the enabling status of the data retrieval.

        :param is_enabled: boolean defining if the data retrieval is enabled
        """
        self._retrieve_info_button.enable(is_enabled)
        super()._update_gui_for_retrieve_enabled(is_enabled)

    def _update_gui_for_language(self):
        """Update the frame using the current selected language."""
        self.title = i18n.all_strings['title']
        country_label = "{0} ({1})".format(self._hut_info['country'], i18n.regions_labels[self._hut_info['region']])
        self._country_text.label = country_label
        self._retrieve_info_button.label = i18n.all_strings['button retrieve info']
        self._open_web_button.label = i18n.all_strings['button open web']
        self._open_booking_button.label = i18n.all_strings['button open booking']
        self._mountain_text.label = i18n.mountain_ranges_labels[self._hut_info['mountain_range']]
        self._height_text.label = i18n.all_strings['height'] + ": {0} m".format(int(self._hut_info['height']))
        self._self_catering_text.label = i18n.all_strings['self catering']
        self._close_button.label = i18n.all_strings['button close']

    def _create_gui(self):
        """Build the view by creating all widgets, positioning them in a layout and setting this as frame layout."""
        self._create_widgets()
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

        self.set_layout(info_sizer)


class SelectedInfoView(_HutsInfoFrame):
    """Define the frame with information about the selected huts.

    Methods:
        From superclass:
        title: return the title of the frame
        icon: return the icon of the frame
        show: show the frame
        hide: hide the frame
        set_focus: set the focus of the frame
        set_cursor: set the cursor shape
        close: close the frame
        on_close: executed when the frame is closed
        update_gui: update the frame content
        on_update_gui: executed when updating the frame content
        set_layout: set the layout of the frame
        event_connect: connect an event to a function
        event_trigger: trigger the event
    """

    _STYLE = FrameStyle.FIXED_SIZE
    _SELECTED_DETAILED_GRID_HEIGHT = 400

    def __init__(self, **kwargs):
        """Initialise the frame.

        :param kwargs: additional parameters for superclass
        """
        self._room_selected = {r: True for r in ROOM_TYPES}
        self._selected = None
        super().__init__(title=i18n.all_strings['selected info'], **kwargs)
        self._create_gui()
        self._update_rooms()

    def on_update_gui(self, data):
        """Update the frame with the provided data.

        :param data: the data to use to update the frame
        """
        if 'dates' in data:
            self._update_dates(data['dates'])
        if 'selected' in data:
            self._update_selected(data['selected'])
        if 'rooms' in data:
            self._update_rooms()
        if 'huts_data' in data:
            self._update_huts_data(data['huts_data'])
        if 'retrieve_enabled' in data:
            self._update_gui_for_retrieve_enabled(data['retrieve_enabled'])
        if 'language' in data:
            self._update_gui_for_language()
        self._grid_selected_detailed.refresh()

    def _on_row_left_double_click(self, _obj, row, _col):
        """Deselect the hut which has been double left-clicked.

        :param row: the row of the double-clicked hut
        """
        self._deselect(row)

    def _on_row_right_click(self, _obj, row, _col):
        """Open the pop-up menu for the hut which has been right-clicked.

        :param row: the row of the clicked hut
        """
        self._hut_pop_up_menu(row)

    def _on_all_rooms(self, _obj):
        """Update the frame with the information about all rooms."""
        for room in ROOM_TYPES:
            self._room_selected[room] = True
            self._rooms_checkbox[room].value = self._room_selected[room]
        self.update_gui({'rooms': None})

    def _on_room_check(self, obj):
        """Update the frame based on the selected rooms.

        :param obj: the checkbox used to select the rooms
        """
        for room in ROOM_TYPES:
            if obj is self._rooms_checkbox[room]:
                self._room_selected[room] = self._rooms_checkbox[room].value
                break
        self.update_gui({'rooms': None})

    def _create_widgets(self):
        """Create all the widgets of the frame."""
        self._all_rooms_button = Button(parent=self,
                                        on_click=self._on_all_rooms)

        self._rooms_checkbox = {}

        for room in ROOM_TYPES:
            self._rooms_checkbox[room] = CheckBox(parent=self,
                                                  on_click=self._on_room_check,
                                                  value=self._room_selected[room])

        self._retrieve_info_button = Button(parent=self,
                                            on_click=self._on_get_huts_info_selected)

        self._close_button = Button(parent=self,
                                    on_click=self._on_button_close)

        self._grid_selected_detailed = self._create_grid()

    def _create_grid(self):
        """Create the grid for the information about the selected huts."""
        grid = SelectedDetailedGrid(self)
        grid.on_cell_left_double_click = self._on_row_left_double_click
        grid.on_cell_right_click = self._on_row_right_click
        return grid

    def _deselect(self, row):
        """Deselect a hut.

        :param row: the row of the hut to deselect
        """
        if len(self._selected) > 1:
            index = self._selected[row]
            self._controller.command_select({'which': index})

    def _on_button_close(self, _obj):
        """Close the frame."""
        self.close()

    def _on_get_huts_info_selected(self, _obj):
        """Command the retrieval of huts data for all selected huts."""
        data = {'which': 'selected'}
        self._controller.command_update_results(data)

    def _update_dates(self, request_dates):
        """Update the view based on the request dates.

        :param request_dates: the request dates
        """
        self._grid_selected_detailed.update_data(dates=request_dates)

    def _update_huts_data(self, huts_data):
        """Update the huts information with the provided data.

        :param huts_data: the data to use to update the huts information
        """
        self._grid_selected_detailed.update_data(data_dictionary=huts_data)

    def _update_selected(self, data):
        """Update the selected huts.

        :param data: tuple of indexes of the selected huts currently shown and of all the selected huts
        """
        selected, all_selected = data
        self._selected = selected
        self._grid_selected_detailed.update_data(indexes=selected)

    def _update_rooms(self):
        """Update the grid for the selected rooms."""
        self._grid_selected_detailed.update_data(room_selected=self._room_selected)

    def _hut_pop_up_menu(self, row):
        """Open the pop-up menu for a hut.

        :param row: the row of the hut
        """
        index = self._selected[row]

        menu_labels = []
        if len(self._selected) > 1:
            menu_labels.append(i18n.all_strings['deselect'])
        menu_labels.append(i18n.all_strings['show details'])
        if self._retrieve_enabled:
            menu_labels.append(i18n.all_strings['retrieve'])
        menu_labels.append(Menu.SEPARATOR)
        menu_labels.append(i18n.all_strings['set location'])
        menu_labels.append(i18n.all_strings['open web'])
        menu_labels.append(i18n.all_strings['open booking'])

        menu = Menu(parent=self, items=menu_labels, on_click=self._on_menu_item)
        menu.pop_up()

        if self._menu_chosen_item == i18n.all_strings['deselect']:
            self._controller.command_select({'which': index})
        elif self._menu_chosen_item == i18n.all_strings['show details']:
            self._controller.command_open_info_frame(index, self)
        elif self._menu_chosen_item == i18n.all_strings['retrieve']:
            self._controller.command_update_results({'which': 'huts', 'indexes': [index]})
        elif self._menu_chosen_item == i18n.all_strings['set location']:
            self._controller.command_update_reference_location({'which': 'hut', 'index': index})
        elif self._menu_chosen_item == i18n.all_strings['open web']:
            self._controller.command_open_hut_page({'which': index})
        elif self._menu_chosen_item == i18n.all_strings['open booking']:
            self._controller.command_open_book_page({'which': index})
        else:
            return

    def _on_menu_item(self, obj, choice_id):
        """Executed when a menu item is clicked.

        :param obj: the clicked menu
        :param choice_id: the index of the clicked item
        """
        self._menu_chosen_item = obj.get_item_label(choice_id)

    def _update_gui_for_language(self):
        """Update the frame using the current selected language."""
        self.title = i18n.all_strings['selected info']
        self._all_rooms_button.label = i18n.all_strings['all rooms']
        for room in ROOM_TYPES:
            self._rooms_checkbox[room].label = i18n.all_strings[room]
        self._retrieve_info_button.label = i18n.all_strings['retrieve selected detailed']
        self._close_button.label = i18n.all_strings['button close']

    def _update_gui_for_retrieve_enabled(self, is_enabled):
        """Update the frame based on the enabling status of the data retrieval.

        :param is_enabled: boolean defining if the data retrieval is enabled
        """
        self._retrieve_info_button.enable(is_enabled)
        super()._update_gui_for_retrieve_enabled(is_enabled)

    def _create_gui(self):
        """Build the view by creating all widgets, positioning them in a layout and setting this as frame layout."""
        self._create_widgets()
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
        self.set_layout(main_sizer)


class DeveloperInfoView(Frame):
    """Define the frame used to show information for the developer (warnings and errors)

    Methods:
        From superclass:
        title: return the title of the frame
        icon: return the icon of the frame
        show: show the frame
        hide: hide the frame
        set_focus: set the focus of the frame
        set_cursor: set the cursor shape
        close: close the frame
        on_close: executed when the frame is closed
        update_gui: update the frame content
        on_update_gui: executed when updating the frame content
        set_layout: set the layout of the frame
        event_connect: connect an event to a function
        event_trigger: trigger the event
    """

    _STYLE = FrameStyle.FIXED_SIZE
    _DEVELOPER_GRID_HEIGHT = 100

    def __init__(self, info_type, **kwargs):
        """Initialise the frame.

        :param info_type: the type of information to be shown (warnings or errors)
        :param kwargs: additional parameters for superclass
        """
        self._developer_info = None
        self._info_type = info_type
        super().__init__(title=i18n.all_strings['developer info'], icon=_APP_ICON_FILENAME, **kwargs)
        self._create_gui()

    def _create_widgets(self):
        """Create all the widgets of the frame."""
        self._main_label = Text(parent=self, font_size=11)

        self._no_info_label = Text(parent=self)

        self._grid_developer = DeveloperGrid(self)

        self._log_button = Button(parent=self,
                                  on_click=self._on_log)

        self._ok_button = Button(parent=self,
                                 on_click=self._on_ok)

    def on_update_gui(self, data):
        """Update the frame with the provided data.

        :param data: the data to use to update the frame
        """
        if 'developer_info' in data:
            self._update_gui_for_developer_info(data['developer_info'])
        if 'language' in data:
            self._update_gui_for_language()
        self._grid_developer.refresh()

    def _update_gui_for_developer_info(self, data):
        """Update the view with the information for the developer.

        :param data: the information for the developer
        """
        self._developer_info = data
        self._grid_developer.update_data(developer_info=self._developer_info)
        self._grid_developer.hide(not self._developer_info)
        self._log_button.hide(not self._developer_info)
        self._no_info_label.hide(self._developer_info)

    def _update_gui_for_language(self):
        """Update the frame using the current selected language."""
        self.title = i18n.all_strings['developer info']

        label_id = f'no {self._info_type}'
        self._no_info_label.label = i18n.all_strings[label_id]

        self._log_button.label = i18n.all_strings['log']

        self._ok_button.label = i18n.all_strings['ok']
        label_id = f'info {self._info_type}'
        self._main_label.label = i18n.all_strings[label_id]

    def _on_log(self, _obj):
        """Save a log file."""
        config.save_log(self._info_type, self._developer_info)
        self._log_button.enable(False)

    def _on_ok(self, _obj):
        """Close the frame."""
        self.close()

    def _create_gui(self):
        """Build the view by creating all widgets, positioning them in a layout and setting this as frame layout."""
        self._create_widgets()
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
        self._grid_developer._MINIMUM_HEIGHT = self._DEVELOPER_GRID_HEIGHT
        self.set_layout(info_sizer)


class FilterDialog(Dialog):
    """Define the dialog used to allow filtering of the table data.

    Methods:
        From superclass:
        title: return the title of the frame
        show_modal: show as a modal dialog
        set_layout: set the layout of the frame
        on_ok: executed if the dialog is closed by clicking on OK
        on_cancel: executed if the dialog is closed by clicking on Cancel
    """

    def __init__(self, **kwargs):
        """Initialise the dialog.

        :param kwargs: additional parameters for superclass
        """
        self.filter_values = None, None
        super().__init__(**kwargs)
        self._create_gui()

    def _create_widgets(self):
        """Create all the widgets of the dialog."""
        self._min_label = Text(parent=self, label=i18n.all_strings['min'])

        self._min_ctrl = TextControl(parent=self, label="")

        self._max_label = Text(parent=self, label=i18n.all_strings['max'])

        self._max_ctrl = TextControl(parent=self, label="")

        self._ok_button = self._create_ok_button(label=i18n.all_strings['ok'])
        self._cancel_button = self._create_cancel_button(label=i18n.all_strings['cancel'])

    def on_ok(self):
        """Store the values to be used for the filtering."""
        self.filter_values = self._min_value, self._max_value

    @property
    def _min_value(self):
        """Return the minimum value for filtering as read from the text control widget.

        :return: the minimum value for filtering
        """
        try:
            return int(self._min_ctrl.label)
        except ValueError:
            return None

    @property
    def _max_value(self):
        """Return the maximum value for filtering as read from the text control widget.

        :return: the maximum value for filtering
        """
        try:
            return int(self._max_ctrl.label)
        except ValueError:
            return None

    def _create_gui(self):
        """Build the view by creating all widgets, positioning them in a layout and setting this as dialog layout."""
        self._create_widgets()
        sizer = VBoxLayout()
        sizer.add(self._min_label, align=Align.EXPAND, border=(10, 10, 0, 10))
        sizer.add(self._min_ctrl, align=Align.EXPAND, border=(0, 10, 10, 10))
        sizer.add(self._max_label, align=Align.EXPAND, border=(10, 10, 0, 10))
        sizer.add(self._max_ctrl, align=Align.EXPAND, border=(0, 10, 10, 10))
        button_sizer = HBoxLayout()
        button_sizer.add(self._ok_button, border=(0, 10, 0, 0))
        button_sizer.add(self._cancel_button, border=(0, 0, 0, 10))
        sizer.add(button_sizer, align=Align.EXPAND, border=10)
        self.set_layout(sizer)


class AboutDialog(Dialog):
    """Define the dialog used to show the About information.

    Methods:
        From superclass:
        title: return the title of the frame
        show_modal: show as a modal dialog
        set_layout: set the layout of the frame
        on_ok: executed if the dialog is closed by clicking on OK
        on_cancel: executed if the dialog is closed by clicking on Cancel
    """

    def __init__(self, dialog_info, **kwargs):
        """Initialise the dialog.

        :param dialog_info: information to be shown in the dialog
        :param kwargs: additional parameters for superclass
        """
        self._dialog_info = dialog_info
        super().__init__(title=f"About {self._dialog_info['name']}", **kwargs)
        self._create_gui()

    def _create_widgets(self):
        """Create all the widgets of the dialog."""
        self._name_label = Text(parent=self, label=f"{self._dialog_info['name']} {self._dialog_info['version']}",
                                font_size=14)
        self._desc_label = Text(parent=self, label=self._dialog_info['description'][i18n.get_current_language_index()],
                                font_size=12)
        self._copyright_label = Text(parent=self, label=self._dialog_info['copyright'], font_size=10)
        self._website_label = Text(parent=self, label=self._dialog_info['website'], font_size=10)
        self._developer_label = Text(parent=self, label=f"Developer: {self._dialog_info['developer']}", font_size=10)

        self._ok_button = self._create_ok_button(label=i18n.all_strings['ok'])

    def _create_gui(self):
        """Build the view by creating all widgets, positioning them in a layout and setting this as dialog layout."""
        self._create_widgets()
        sizer = VBoxLayout()
        sizer.add(self._name_label, align=Align.EXPAND, border=(10, 10, 0, 10))
        sizer.add(self._desc_label, align=Align.EXPAND, border=(10, 10, 0, 10))
        sizer.add(self._copyright_label, align=Align.EXPAND, border=(10, 10, 10, 10))
        sizer.add(self._website_label, align=Align.EXPAND, border=(10, 10, 20, 10))
        sizer.add(self._developer_label, align=Align.EXPAND, border=(10, 10, 10, 10))
        sizer.add(self._ok_button, align=Align.RIGHT, border=(10, 10, 10, 10))
        self.set_layout(sizer)


class UpdateDialog(Dialog):
    """Define the dialog used to select the updates to the program to apply.

    Methods:
        From superclass:
        title: return the title of the frame
        show_modal: show as a modal dialog
        set_layout: set the layout of the frame
        on_ok: executed if the dialog is closed by clicking on OK
        on_cancel: executed if the dialog is closed by clicking on Cancel
    """

    def __init__(self, available_updates, **kwargs):
        """Initialise the dialog.

        :param available_updates: information about the available updates
        :param kwargs: additional parameters for superclass
        """
        self._available_updates = available_updates
        self.approved_updates = None
        super().__init__(title=i18n.all_strings['available updates'], **kwargs)
        self._create_gui()

    def _create_widgets(self):
        """Create all the widgets of the dialog."""
        self._labels = {}
        self._checkbox = {}
        for filename, (_, desc) in self._available_updates.items():
            label = Text(parent=self, label=i18n.all_strings[desc])
            label.on_left_down = self._on_label_click
            self._labels[filename] = label
            self._checkbox[filename] = CheckBox(parent=self, value=True)

        self._main_label = Text(parent=self, font_size=11)
        if self._available_updates:
            self._main_label.label = i18n.all_strings['choose updates']
        else:
            self._main_label.label = i18n.all_strings['no updates available']

        self._ok_button = self._create_ok_button(label=i18n.all_strings['ok'])
        self._cancel_button = self._create_cancel_button(label=i18n.all_strings['cancel'])

        if not self._available_updates:
            self._cancel_button.hide(True)

    def _on_label_click(self, obj, _position):
        """Executed when the label of an available update is clicked.

        :param obj: the clicked label
        """
        for filename, label in self._labels.items():
            if obj is label:
                self._checkbox[filename].value = not self._checkbox[filename].value

    def on_ok(self):
        """Store in the field the approved updates for further processing by the program."""
        self.approved_updates = {
            filename: path for filename, (path, _) in self._available_updates.items() if self._checkbox[filename].value
        }

    def _create_gui(self):
        """Build the view by creating all widgets, positioning them in a layout and setting this as dialog layout."""
        self._create_widgets()
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
        self.set_layout(sizer)


class WaitingMessage(Frame):
    """Define the frame (in dialog style) used to display a waiting message.

    Methods:
        From superclass:
        title: return the title of the frame
        icon: return the icon of the frame
        show: show the frame
        hide: hide the frame
        set_focus: set the focus of the frame
        set_cursor: set the cursor shape
        close: close the frame
        on_close: executed when the frame is closed
        update_gui: update the frame content
        on_update_gui: executed when updating the frame content
        set_layout: set the layout of the frame
        event_connect: connect an event to a function
        event_trigger: trigger the event
    """

    _STYLE = FrameStyle.DIALOG

    def __init__(self, *, cancel_function, **kwargs):
        """Initialise the frame.

        :param cancel_function: function to be executed if the cancel button is clicked
        :param kwargs: additional parameters for superclass
        """
        self._on_click = cancel_function
        super().__init__(icon=_APP_ICON_FILENAME, **kwargs)
        self._create_gui()

    def _create_widgets(self):
        """Create all the widgets of the frame."""
        self._message = Text(parent=self)
        self._stop_button = Button(parent=self,
                                   on_click=self._on_click,
                                   label=i18n.all_strings['cancel'])

    def on_update_gui(self, data):
        """Update the frame with the provided data.

        :param data: the data to use to update the frame
        """
        if 'message' in data:
            self._update_message(data['message'])

    def _update_message(self, label):
        """Update the displayed message.

        :param label: the message to display
        """
        self._message.label = label

    def _create_gui(self):
        """Build the view by creating all widgets, positioning them in a layout and setting this as frame layout."""
        self._create_widgets()
        info_sizer = VBoxLayout()
        info_sizer.add(self._message, align=Align.EXPAND, border=20)
        info_sizer.add(self._stop_button, align=Align.RIGHT, border=15)
        self.set_layout(info_sizer)
