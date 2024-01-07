import ast
import datetime

from src.map_tools import NavigableMap, HutMap
from src import i18n
from src import config
from src.model import ROOM_TYPES
from src.gui_library import Button, CheckBox, RadioBox, Bitmap, Text, Calendar, SpinControl, Menu, TextControl, \
    TextTimedMenu
from build.tables import HutsGrid, DetailedGrid, DeveloperGrid, SelectedDetailedGrid
from src.gui_library import event_create
from src.gui_library.abstract.frames import AbstractFrame, AbstractDialog, FrameStyle, CursorStyle
from src.gui_library.abstract.widgets import TextStyle
from src.config import ASSETS_PATH_ICONS

_APP_ICON_FILENAME = str(ASSETS_PATH_ICONS / "app_icon.png")

_CHECKED_SYMBOL = '  \u2713'

WaitingMessage = None
FilterDialog = None
MessageDialog = None


class AbstractIconFrame(AbstractFrame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, icon=_APP_ICON_FILENAME)


class AbstractWaitingMessage(AbstractIconFrame):

    _STYLE = FrameStyle.DIALOG

    def __init__(self, *, cancel_function, **kwargs):
        self._on_click = cancel_function
        super().__init__(**kwargs)

    def _create_widgets(self, panel):
        self._message = Text(panel)
        self._stop_button = Button(panel,
                                   on_click=self._on_click,
                                   label=i18n.all_strings['cancel'])

    def update_gui(self, data):
        if 'message' in data:
            self._update_message(data['message'])
        super().update_gui(data)

    def _update_message(self, label):
        self._message.label = label


class AbstractHutsInfoFrame(AbstractIconFrame):

    def __init__(self, *, controller, **kwargs):
        self._controller = controller
        self._menu_chosen_item = None
        self._retrieve_enabled = True
        super().__init__(**kwargs)

    def _update_gui_for_retrieve_enabled(self, is_enabled):
        self._retrieve_enabled = is_enabled


class AbstractHutsView(AbstractHutsInfoFrame):

    _after_update_event = event_create()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_connect(self._after_update_event, self._on_after_update)
        self._waiting_message = None
        self._all_updates = {}
        self._update_cancelled = False

    def show_waiting_message_huts(self, cancel_function, outstanding):
        if self._waiting_message is not None:
            self.close_waiting_message()
        title = i18n.all_strings['waiting caption huts']
        self._waiting_message = WaitingMessage(cancel_function=cancel_function, parent=self, title=title)
        label = i18n.all_strings['waiting message huts'].format(outstanding)
        self._waiting_message.update_gui({'message': label})
        self._waiting_message.show()

    def update_waiting_message_huts(self, outstanding):
        label = i18n.all_strings['waiting message huts'].format(outstanding)
        self._waiting_message.update_gui_from_thread({'message': label})

    def show_waiting_message_updates(self, cancel_function, message):
        if self._waiting_message is not None:
            self.close_waiting_message()
        title = i18n.all_strings['waiting caption updates']
        self._waiting_message = WaitingMessage(cancel_function=cancel_function, parent=self, title=title)
        label = i18n.all_strings['waiting message updates'].format(i18n.all_strings[message])
        self._waiting_message.update_gui({'message': label})
        self._waiting_message.show()

    def update_waiting_message_updates(self, message):
        label = i18n.all_strings['waiting message updates'].format(i18n.all_strings[message])
        self._waiting_message.update_gui_from_thread({'message': label})

    def close_waiting_message(self):
        self._waiting_message.close_from_thread()
        self._waiting_message = None

    def _update_gui_for_retrieve_enabled(self, is_enabled):
        super()._update_gui_for_retrieve_enabled(is_enabled)
        self._create_menu()

    def _create_date_widgets(self, panel):
        self._request_date_label = Text(panel, label=i18n.all_strings['request date'])

        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        self._date_widget = Calendar(panel, lower_date=tomorrow, selected_date=tomorrow)
        self._date_widget.on_date_changed = self._on_dates_selected

        self._number_days_label = Text(panel, label=i18n.all_strings['number of days'])

        self._number_days_widget = SpinControl(panel, min_value=1, max_value=1)
        self._number_days_widget.on_click = self._on_dates_selected

    def _create_menu(self):
        menubar = Menu(self)

        label = ast.literal_eval(i18n.all_strings['menu main'])[0]
        menu_main = Menu(self, label=label)

        self._other_view_menu(menu_main)

        if self.parent is not None:
            menubar.append(menu_main)
            self._set_menubar(menubar)
            return

        label = ast.literal_eval(i18n.all_strings['menu language'])[0]
        menu_language = Menu(self, label=label)
        languages = i18n.get_languages_list()
        if languages:
            menu_main.append(menu_language)
            for lang_index, lang_string in enumerate(languages):
                menu_string = '&' + lang_string
                if lang_index == i18n.get_current_language():
                    menu_string += _CHECKED_SYMBOL
                menu_string += '\tAlt-' + lang_string[0]
                menu_language.append(menu_string, on_item_click=lambda lang=lang_index: self._on_language(lang))

        label = ast.literal_eval(i18n.all_strings['menu preferences'])[0]
        menu_preferences = Menu(self, label=label)
        menu_main.append(menu_preferences)

        if config.SUPPORTED_GUIS is not None:
            label = ast.literal_eval(i18n.all_strings['menu gui'])[0]
            menu_gui = Menu(self, label=label)
            menu_preferences.append(menu_gui)
            for gui_type in config.SUPPORTED_GUIS:
                menu_string = i18n.all_strings[gui_type]
                if gui_type == config.GUI:
                    menu_string += _CHECKED_SYMBOL
                menu_gui.append(menu_string, on_item_click=lambda gt=gui_type: self._on_menu_gui(gt))

        label = ast.literal_eval(i18n.all_strings['menu view'])[0]
        menu_view = Menu(self, label=label)
        menu_preferences.append(menu_view)
        for view_type in ['table', 'map']:
            menu_string = i18n.all_strings[view_type]
            if view_type == config.VIEW:
                menu_string += _CHECKED_SYMBOL
            menu_view.append(menu_string, on_item_click=lambda vt=view_type: self._on_menu_view(vt))

        label = ast.literal_eval(i18n.all_strings['menu exit'])[0]
        menu_main.append(label, on_item_click=self._on_menu_command_close)

        label = ast.literal_eval(i18n.all_strings['menu help'])[0]
        menu_help = Menu(self, label=label)

        if self._retrieve_enabled:
            label = ast.literal_eval(i18n.all_strings['menu updates'])[0]
            menu_help.append(label, on_item_click=self._on_updates)

        label = ast.literal_eval(i18n.all_strings['menu about'])[0]
        menu_help.append(label, on_item_click=self._on_about)

        label = ast.literal_eval(i18n.all_strings['menu developer'])[0]
        menu_develop = Menu(self, label=label)

        label = ast.literal_eval(i18n.all_strings['menu warnings'])[0]
        menu_develop.append(label, on_item_click=self._on_show_warnings)
        label = ast.literal_eval(i18n.all_strings['menu errors'])[0]
        menu_develop.append(label, on_item_click=self._on_show_errors)

        menubar.append(menu_main)
        menubar.append(menu_develop)
        menubar.append(menu_help)

        self._set_menubar(menubar)

    def _on_about(self):
        self._controller.command_open_about_dialog(self)

    def _on_updates(self):
        self._controller.command_search_for_updates()

    def _on_language(self, lang):
        self._controller.command_language(lang)

    def _on_menu_gui(self, gui_type):
        self._controller.command_preference_gui(gui_type)
        self._create_menu()

    def _on_menu_view(self, view_type):
        self._controller.command_preference_view(view_type)
        self._create_menu()

    def _on_show_warnings(self):
        self._controller.command_open_warnings_frame(self)

    def _on_show_errors(self):
        self._controller.command_open_errors_frame(self)

    def _on_menu_command_close(self):
        self.close()

    def _on_command_close(self, obj):
        self.close()

    def update_gui(self, data):
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
        super().update_gui(data)

    def _update_displayed(self, data):
        raise NotImplementedError

    def _update_selected(self, data):
        raise NotImplementedError

    def _update_huts_data(self, data):
        raise NotImplementedError

    def _update_reference_location(self, location):
        raise NotImplementedError

    def _update_filter_displayed_keys(self, filter_displayed_keys):
        raise NotImplementedError

    def _update_dates(self, request_dates):
        self._date_widget.selected_date = request_dates[0]
        self._number_days_widget.value = len(request_dates)

    def _update_gui_for_language(self):
        self._date_widget.set_language(i18n.get_current_language_string())

    def _update_gui_for_config(self):
        self._number_days_widget.max_value = config.MAX_NIGHTS

    def _on_dates_selected(self, obj):
        date = self._date_widget.selected_date
        data = {'request_date': date,
                'number_days': self._number_days_widget.value}
        self._controller.command_update_dates(data)

    def _other_view_menu(self, menu_main):
        raise NotImplementedError()

    def post_after_updates_event(self, all_updates, update_cancelled):
        self.event_trigger(self._after_update_event, all_updates=all_updates, update_cancelled=update_cancelled)

    def _on_after_update(self, all_updates, update_cancelled):
        self._controller.command_open_update_dialog(self, all_updates, update_cancelled)


class AbstractHutsTableView(AbstractHutsView):

    _TABLE_VIEW_SIZE = (1000, 600)

    def __init__(self, *, parent=None, **kwargs):

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
        self._grid_displayed.update_data(keys=self._keys)
        self._grid_selected.update_data(keys=self._keys)

    def update_gui(self, data):
        if 'filter_selected_keys' in data:
            self._update_filter_selected_keys(data['filter_selected_keys'])
        if 'sort_displayed_key' in data:
            self._update_sort_displayed_key(data['sort_displayed_key'])
        if 'sort_selected_key' in data:
            self._update_sort_selected_key(data['sort_selected_key'])
        if 'columns_width' in data:
            self._columns_width_to_reset = True
        super().update_gui(data)

    def _reset_columns_width(self):
        self._grid_displayed.unfreeze_cols_width()
        self._grid_displayed.refresh()
        self._grid_displayed.freeze_cols_width()
        self._grid_selected.set_cols_width_as(self._grid_displayed)

    def _refresh_widgets(self):
        if self._columns_width_to_reset:
            self._reset_columns_width()
            self._columns_width_to_reset = False
        self._grid_displayed.refresh()
        self._grid_selected.refresh()

    def _other_view_menu(self, menu_main):
        label = ast.literal_eval(i18n.all_strings['menu map view'])[0]
        menu_main.append(label, on_item_click=self._on_map_view)

    def _on_map_view(self):
        self._show_map_view()

    def _show_map_view(self):
        if self.parent is not None and isinstance(self.parent, AbstractHutsMapView):
            self.parent.set_focus()
            return
        for child_view in self.child_views:
            if isinstance(child_view, AbstractHutsMapView):
                child_view.set_focus()
                return
        self._controller.command_open_map_view(parent=self)

    def _create_grid(self, grid_id, panel):
        grid = HutsGrid(panel)
        grid.grid_id = grid_id

        grid.on_cell_left_double_click = self._command_select
        grid.on_cell_right_click = self._hut_pop_up_menu
        grid.on_label_left_click = self._command_sort
        grid.on_label_right_click = self._command_filter

        return grid

    def _create_widgets(self, panel):
        self._create_date_widgets(panel)

        self._checkbox_no_response = CheckBox(panel,
                                              on_click=self._on_response_check)

        self._checkbox_closed = CheckBox(panel,
                                         on_click=self._on_closed_check)

        self._grid_displayed = self._create_grid('displayed', panel)

        self._selected_huts_label = Text(panel)

        self._grid_selected = self._create_grid('selected', panel)

        self._retrieve_info_label = Text(panel)

        self._get_displayed_results_button = Button(panel,
                                                    on_click=self._on_get_huts_info_displayed)

        self._get_selected_results_button = Button(panel,
                                                   on_click=self._on_get_huts_info_selected)

        self._reference_label = Text(panel)

        self._latitude_label = Text(panel)

        self._latitude_widget = TextControl(panel)

        self._longitude_label = Text(panel)

        self._longitude_widget = TextControl(panel)

        self._set_location_button = Button(panel,
                                           on_click=self._on_update_location_button)

        self._close_button = Button(panel,
                                    on_click=self._on_command_close)

    def _update_gui_for_retrieve_enabled(self, is_enabled):
        self._get_displayed_results_button.enable(is_enabled)
        self._get_selected_results_button.enable(is_enabled)
        super()._update_gui_for_retrieve_enabled(is_enabled)

    def _update_gui_for_language(self):
        super()._update_gui_for_language()
        self._create_menu()
        self.title = i18n.all_strings['title']
        self._grid_displayed.update_for_language()
        self._grid_selected.update_for_language()
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
        self._filter_keys['displayed'] = filter_displayed_keys
        self._checkbox_closed.value = 'open' in filter_displayed_keys
        self._checkbox_no_response.value = 'response' in filter_displayed_keys
        self._grid_displayed.update_data(filter_keys=filter_displayed_keys)

    def _update_filter_selected_keys(self, filter_selected_keys):
        self._filter_keys['selected'] = filter_selected_keys
        self._grid_selected.update_data(filter_keys=filter_selected_keys)

    def _update_sort_displayed_key(self, sort_displayed_params):
        self._grid_displayed.update_data(sort_key=sort_displayed_params[0], sort_ascending=sort_displayed_params[1])

    def _update_sort_selected_key(self, sort_selected_params):
        self._grid_selected.update_data(sort_key=sort_selected_params[0], sort_ascending=sort_selected_params[1])

    def _update_huts_data(self, huts_data):
        self._grid_displayed.update_data(data_dictionary=huts_data)
        self._grid_selected.update_data(data_dictionary=huts_data)

    def _update_displayed(self, displayed):
        self._displayed = displayed
        self._grid_displayed.update_data(indexes=displayed)

    def _update_selected(self, data):
        selected, all_selected = data
        self._selected = selected
        self._grid_displayed.update_data(selected=all_selected)
        self._grid_selected.update_data(selected)

    def _update_reference_location(self, location):
        self._latitude_widget.label = '{0:.5f}'.format(location['lat'])
        self._longitude_widget.label = '{0:.5f}'.format(location['lon'])

    def _on_response_check(self, obj):
        data = {'which': 'displayed', 'key': 'response', 'parameters': None}
        self._controller.command_filter(data)
        data = {'which': 'selected', 'key': 'response', 'parameters': None}
        self._controller.command_filter(data)

    def _on_closed_check(self, obj):
        data = {'which': 'displayed', 'key': 'open', 'parameters': None}
        self._controller.command_filter(data)
        data = {'which': 'selected', 'key': 'open', 'parameters': None}
        self._controller.command_filter(data)

    def _on_get_huts_info_displayed(self, obj):
        data = {'which': 'displayed'}
        self._controller.command_update_results(data)

    def _on_get_huts_info_selected(self, obj):
        data = {'which': 'selected'}
        self._controller.command_update_results(data)

    def _on_update_location_button(self, obj):
        try:
            lat = float(self._latitude_widget.label)
            lon = float(self._longitude_widget.label)
            if -90. < lat < 90. and -180. < lon < 180.:
                data = {'which': 'latlon', 'lat': lat, 'lon': lon}
                self._controller.command_update_reference_location(data)
            else:
                raise ValueError()
        except ValueError:
            with MessageDialog(self, i18n.all_strings['invalid location'], i18n.all_strings['error']) as dialog:
                dialog.show_modal()

    def _command_select(self, obj, row, col):
        if obj.grid_id == 'displayed':
            index = self._displayed[row]
        else:
            index = self._selected[row]
        data = {'which': index}
        self._controller.command_select(data)

    def _command_sort(self, obj, row, col):
        key = self._keys[col]
        data = {'which': obj.grid_id, 'key': key}
        self._controller.command_sort(data)

    def _command_filter(self, obj, row, col):
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
        menu_labels = sorted(list(filter_dict))

        self._menu_chosen_item = None
        menu = Menu(self, items=menu_labels, on_click=self._on_menu_item)
        menu.pop_up()

        if self._menu_chosen_item is not None:
            return {'value': filter_dict[self._menu_chosen_item]}
        else:
            return None

    def _value_entry(self, key):
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

    def _hut_pop_up_menu(self, obj, row, col):
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
        menu = Menu(self, items=menu_labels, on_click=self._on_menu_item)
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
        self._menu_chosen_item = obj.get_item_label(choice_id)


class AbstractHutsMapView(AbstractHutsView):

    _STYLE = FrameStyle.FIXED_SIZE

    _DEFAULT_MAP_WINDOW = [46.0, 52.0, 4.5, 16.5]  # [degrees]
    _MAP_X_PIXEL_DIMENSION = 550
    _MAP_Y_PIXEL_DIMENSION = 550
    _DEFAULT_MAP_ZOOM = 6
    _MAP_MIN_ZOOM = 6
    _MAP_MAX_ZOOM = 13

    def __init__(self, *, parent=None, **kwargs):
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

    def _create_widgets(self, panel):
        self._hut_map = NavigableMap(self._MAP_X_PIXEL_DIMENSION, self._MAP_Y_PIXEL_DIMENSION,
                                     self._DEFAULT_MAP_ZOOM, self._MAP_MIN_ZOOM, self._MAP_MAX_ZOOM,
                                     self._DEFAULT_MAP_WINDOW)

        self._bitmap = Bitmap(panel, bitmap=self._hut_map.get_map_image())
        self._bitmap.on_left_down = self._on_left_down
        self._bitmap.on_left_up = self._on_left_up
        self._bitmap.on_right_down = self._on_right_down
        self._bitmap.on_right_up = self._on_right_up
        self._bitmap.on_mouse_motion = self._on_mouse_motion
        self._bitmap.on_mouse_leave = self._on_mouse_leave
        self._bitmap.on_wheel = self._on_mouse_wheel

        self._create_date_widgets(panel)

        self._get_results_button = Button(panel,
                                          on_click=self._on_get_huts_info)

        self._checkbox_no_response = CheckBox(panel,
                                              on_click=self._on_response_check)

        self._checkbox_closed = CheckBox(panel,
                                         on_click=self._on_closed_check)

        self._checkbox_reference = CheckBox(panel,
                                            on_click=self._on_reference_check)

        self._huts_choice = RadioBox(panel,
                                     num_choices=2,
                                     on_click=self._on_huts_choice)

        self._fit_button = Button(panel,
                                  on_click=self._on_fit_button)

        self._close_button = Button(panel,
                                    on_click=self._on_command_close)

    def _other_view_menu(self, menu_main):
        label = ast.literal_eval(i18n.all_strings['menu table view'])[0]
        menu_main.append(label, on_item_click=self._on_table_view)

    def _on_table_view(self):
        self._show_table_view()

    def _show_table_view(self):
        if self.parent is not None and isinstance(self.parent, AbstractHutsTableView):
            self.parent.set_focus()
            return
        for child_view in self.child_views:
            if isinstance(child_view, AbstractHutsTableView):
                child_view.set_focus()
                return
        self._controller.command_open_table_view(parent=self)

    def _on_response_check(self, obj):
        data = {'which': 'displayed', 'key': 'response', 'parameters': None}
        self._controller.command_filter(data)
        data = {'which': 'selected', 'key': 'response', 'parameters': None}
        self._controller.command_filter(data)

    def _on_reference_check(self, obj):
        self._show_reference_location()

    def _on_closed_check(self, obj):
        data = {'which': 'displayed', 'key': 'open', 'parameters': None}
        self._controller.command_filter(data)
        data = {'which': 'selected', 'key': 'open', 'parameters': None}
        self._controller.command_filter(data)

    def _on_get_huts_info(self, obj):
        data = {'which': 'displayed' if self._huts_choice.selection == 0 else 'selected'}
        self._controller.command_update_results(data)

    def _refresh_widgets(self):
        self._update_shown_huts()

    def _update_huts_data(self, huts_data):
        self._huts_data = huts_data

    def _on_huts_choice(self, obj):
        self._update_shown_huts()

    def _update_shown_huts(self):
        if self._huts_choice.selection == 0:
            huts_data = {index: self._huts_data[index] for index in self._displayed}
        else:
            huts_data = {index: self._huts_data[index] for index in self._selected}
        self._hut_map.update_huts_data(huts_data)
        self._update_map()

    def _update_filter_displayed_keys(self, filter_displayed_keys):
        self._checkbox_closed.value = 'open' in filter_displayed_keys
        self._checkbox_no_response.value = 'response' in filter_displayed_keys

    def _update_map(self):
        self._bitmap.bitmap = self._hut_map.get_map_image()

    def _update_selected(self, data):
        selected, all_selected = data
        self._selected = selected

    def _update_displayed(self, displayed):
        self._displayed = displayed

    def _update_reference_location(self, location):
        self._reference_location = location
        self._show_reference_location()

    def _show_reference_location(self):
        if self._checkbox_reference.value:
            self._hut_map.show_reference_location(self._reference_location['lat'],
                                                  self._reference_location['lon'])
        else:
            self._hut_map.hide_reference_location()
        self._update_map()

    def _on_fit_button(self, obj):
        if self._huts_choice.selection == 0:
            self.update_zoom_from_huts({index: self._huts_data[index] for index in self._displayed})
        else:
            self.update_zoom_from_huts({index: self._huts_data[index] for index in self._selected})
        self._update_map()

    def _on_left_down(self, obj, position):
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
                self.hut_menu(huts[0])
            else:
                self._multi_hut_menu(huts)
        else:
            self._left_drag_start = position
            self.map_center = self._hut_map.get_lat_lon_map_center()
            self._set_cursor(CursorStyle.SIZING)

    def _on_left_up(self, obj, position):
        self._left_drag_start = None
        self._set_cursor(CursorStyle.ARROW)

    def _on_right_down(self, obj, position):
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
                self.hut_menu(huts[0])
            else:
                self._multi_hut_menu(huts)
        else:
            self._right_drag_start = position

    def _get_window_boundaries(self, position):
        start_lat, start_lon = self._hut_map.get_lat_lon_from_pixel(*self._right_drag_start)
        end_lat, end_lon = self._hut_map.get_lat_lon_from_pixel(*position)
        lat_min = min(start_lat, end_lat)
        lat_max = max(start_lat, end_lat)
        lon_min = min(start_lon, end_lon)
        lon_max = max(start_lon, end_lon)
        return lat_min, lat_max, lon_min, lon_max

    def _on_right_up(self, obj, position):
        if self._right_drag_start is not None:
            if position == self._right_drag_start:
                self._point_menu(*self._hut_map.get_lat_lon_from_pixel(*position))
            else:
                self._keep_window = True
                self._window_menu(*self._get_window_boundaries(position))
                self._keep_window = False
        self._right_drag_start = None

    def _on_mouse_motion(self, obj, position):
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
                    self._get_info_pop_up(huts)
                    self._info_pop_up.pop_up()
                elif huts[0] == self._pop_up_group:
                    self._info_pop_up.prevent_close()
                else:
                    self._info_pop_up.force_close()
                    self._get_info_pop_up(huts)
                    self._info_pop_up.pop_up()
            else:
                if self._info_pop_up is not None:
                    self._info_pop_up.command_close()

    def _on_mouse_leave(self, obj):
        if self._info_pop_up is not None:
            self._info_pop_up.command_close()
        self._left_drag_start = None
        self._set_cursor(CursorStyle.ARROW)
        self._right_drag_start = None
        if not self._keep_window:
            self._hut_map.hide_window()
        self._measure_distance_start = None
        self._hut_map.hide_ruler()
        self._update_map()

    def _get_info_pop_up(self, huts):
        menu_items = []
        for i, hut in enumerate(huts):
            menu_items.append((self._huts_data[hut]['name'] + " (" + str(int(self._huts_data[hut]['height'])) + " m)",
                               True, lambda h=hut: self.hut_menu(h)))
        self._pop_up_group = huts[0]
        self._info_pop_up = TextTimedMenu(self, items=menu_items)
        self._info_pop_up.on_close = self.on_close_pop_up

    def on_info_pop_up_item(self, obj, choice_id):
        obj.get_on_item_click(choice_id)()

    def on_close_pop_up(self, obj):
        self._info_pop_up = None
        self._pop_up_group = None

    def _window_menu(self, lat_min, lat_max, lon_min, lon_max):
        menu_labels = []
        menu_labels.append(i18n.all_strings['zoom to window'])
        select_label = i18n.all_strings['select in window'] \
            if self._huts_choice.selection == 0 else i18n.all_strings['deselect in window']
        menu_labels.append(select_label)
        if self._huts_choice.selection == 1:
            menu_labels.append(i18n.all_strings['select only in window'])

        self._menu_chosen_item = None
        menu = Menu(self, items=menu_labels, on_click=self._on_menu_item)
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

    def hut_menu(self, index):
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
        menu = Menu(self, items=menu_labels, on_click=self._on_menu_item)
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
            self.update_zoom_from_huts(huts_data)
            self._update_map()
        elif self._menu_chosen_item == i18n.all_strings['measure distance']:
            self._measure_distance_start = hut_info['lat'], hut_info['lon']
        else:
            return

    def update_zoom_from_huts(self, huts_data):
        lat_min = min(hut_data['lat'] for hut_data in huts_data.values())
        lat_max = max(hut_data['lat'] for hut_data in huts_data.values())
        lon_min = min(hut_data['lon'] for hut_data in huts_data.values())
        lon_max = max(hut_data['lon'] for hut_data in huts_data.values())

        self._hut_map.update_zoom_from_window(lat_min, lat_max, lon_min, lon_max)

    def _multi_hut_menu(self, indexes):
        menu_labels = []
        select_all_label = i18n.all_strings['select all group'] \
            if self._huts_choice.selection == 0 else i18n.all_strings['deselect all group']
        menu_labels.append(select_all_label)
        menu_labels.append(i18n.all_strings['zoom on group'])
        if self._retrieve_enabled:
            menu_labels.append(i18n.all_strings['retrieve group'])

        self._menu_chosen_item = None
        menu = Menu(self, items=menu_labels, on_click=self._on_menu_item)
        menu.pop_up()

        if self._menu_chosen_item == select_all_label:
            data = {
                'which': indexes,
                'type': 'select' if self._huts_choice.selection == 0 else 'deselect'
            }
            self._controller.command_select_multi(data)
        elif self._menu_chosen_item == i18n.all_strings['zoom on group']:
            huts_data = {index: self._huts_data[index] for index in indexes}
            self.update_zoom_from_huts(huts_data)
            self._update_map()
        elif self._menu_chosen_item == i18n.all_strings['retrieve group']:
            self._controller.command_update_results({'which': 'huts', 'indexes': indexes})
        else:
            return

    def _point_menu(self, lat, lon):
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
        menu = Menu(self, items=menu_labels, on_click=self._on_menu_item)
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
        self._menu_chosen_item = obj.get_item_label(choice_id)

    def _on_mouse_wheel(self, obj, position, direction):
        if self._info_pop_up is not None:
            self._info_pop_up.force_close()
        self._measure_distance_start = None
        self._hut_map.hide_ruler()
        self._left_drag_start = None
        self._set_cursor(CursorStyle.ARROW)
        self._right_drag_start = None
        self._hut_map.hide_window()
        self._hut_map.update_zoom_from_point(*self._hut_map.get_lat_lon_from_pixel(*position), direction)
        self._update_map()

    def _update_gui_for_retrieve_enabled(self, is_enabled):
        self._get_results_button.enable(is_enabled)
        super()._update_gui_for_retrieve_enabled(is_enabled)

    def _update_gui_for_language(self):
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


class AbstractDetailedInfoView(AbstractHutsInfoFrame):

    _DETAILED_MAP_WIDTH = 60000  # [meters]
    _DETAILED_MAP_HEIGHT = 60000  # [meters]
    _DETAILED_MAP_REF_ZOOM = 9
    _DETAILED_MAP_MIN_ZOOM = 6
    _DETAILED_MAP_MAX_ZOOM = 13
    _STYLE = FrameStyle.FIXED_SIZE

    def __init__(self, *, index, hut_info, **kwargs):
        self._index = index
        self._hut_info = hut_info
        self._hut_map = HutMap(self._hut_info['lat'], self._hut_info['lon'],
                               self._DETAILED_MAP_WIDTH, self._DETAILED_MAP_HEIGHT,
                               self._DETAILED_MAP_REF_ZOOM, self._DETAILED_MAP_MIN_ZOOM, self._DETAILED_MAP_MAX_ZOOM)
        super().__init__(title=i18n.all_strings['detailed info'], **kwargs)
        self._self_catering_text.hide(not self._hut_info['self_catering'])
        self._hut_text.label = self._hut_info['name']

    def _create_widgets(self, panel):
        self._hut_text = Text(panel, font_size=11, font_style=TextStyle.BOLD)

        self._country_text = Text(panel, font_size=10)

        self._mountain_text = Text(panel, font_size=10)

        self._height_text = Text(panel, font_size=10)

        self._self_catering_text = Text(panel, font_size=10)

        self._bitmap = Bitmap(panel)
        self._bitmap.on_wheel = self._on_wheel
        self._bitmap.on_left_down = self._on_click

        self._retrieve_info_button = Button(panel,
                                            on_click=self._on_retrieve_info)

        self._open_web_button = Button(panel,
                                       on_click=self._on_open_web)

        self._open_booking_button = Button(panel,
                                           on_click=self._on_open_booking)

        self._grid_detailed = DetailedGrid(panel)

        self._close_button = Button(panel,
                                    on_click=self._on_button_close)

    def update_gui(self, data):
        if 'huts_data' in data:
            self._update_huts_data(data['huts_data'])
        if 'retrieve_enabled' in data:
            self._update_gui_for_retrieve_enabled(data['retrieve_enabled'])
        if 'language' in data:
            self._update_gui_for_language()

        super().update_gui(data)

    def _update_huts_data(self, huts_data):
        self._hut_info = huts_data[self._index]
        self._hut_map.set_status(self._hut_info['status'])
        self._grid_detailed.update_data(self._hut_info)
        self._update_bitmap()

    def _refresh_widgets(self):
        self._grid_detailed.refresh()

    def _on_button_close(self, obj):
        self.close()

    def _update_zoom(self, direction):
        self._hut_map.update_zoom(direction)
        self._update_bitmap()

    def _on_retrieve_info(self, obj):
        self._controller.command_update_results({'which': 'huts', 'indexes': [self._index]})

    def _on_open_web(self, obj):
        self._controller.command_open_hut_page({'which': self._index})

    def _on_open_booking(self, obj):
        self._controller.command_open_book_page({'which': self._index})

    def _on_click(self, obj, position):
        delta_zoom = self._hut_map.check_zoom(*position)
        if delta_zoom != 0:
            self._update_zoom(delta_zoom)

    def _on_wheel(self, obj, position, direction):
        self._update_zoom(direction)

    def _update_bitmap(self):
        self._bitmap.bitmap = self._hut_map.get_map_image()

    def _update_gui_for_retrieve_enabled(self, is_enabled):
        self._retrieve_info_button.enable(is_enabled)
        super()._update_gui_for_retrieve_enabled(is_enabled)

    def _update_gui_for_language(self):
        self.title = i18n.all_strings['title']
        country_label = "{0} ({1})".format(self._hut_info['country'], i18n.regions_labels[self._hut_info['region']])
        self._country_text.label = country_label
        self._retrieve_info_button.label = i18n.all_strings['button retrieve info']
        self._open_web_button.label = i18n.all_strings['button open web']
        self._open_booking_button.label = i18n.all_strings['button open booking']
        self._mountain_text.label = i18n.mountain_ranges_labels[self._hut_info['mountain_range']]
        self._height_text.label = i18n.all_strings['height'] + ": {0} m".format(int(self._hut_info['height']))
        self._self_catering_text.label = i18n.all_strings['self catering']
        self._grid_detailed.update_for_language()
        self._close_button.label = i18n.all_strings['button close']


class AbstractSelectedInfoView(AbstractHutsInfoFrame):

    _STYLE = FrameStyle.FIXED_SIZE

    def __init__(self, **kwargs):
        self._room_selected = {r: True for r in ROOM_TYPES}
        self._selected = None
        super().__init__(title=i18n.all_strings['selected info'], **kwargs)
        self._update_rooms()

    def update_gui(self, data):
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
        super().update_gui(data)

    def _refresh_widgets(self):
        self._grid_selected_detailed.refresh()

    def _on_row_left_double_click(self, obj, row, col):
        self._deselect(row)

    def _on_row_right_click(self, obj, row, col):
        self._hut_pop_up_menu(row)

    def _on_all_rooms(self, obj):
        for room in ROOM_TYPES:
            self._room_selected[room] = True
            self._rooms_checkbox[room].value = self._room_selected[room]
        self.update_gui({'rooms': None})

    def _on_room_check(self, obj):
        for room in ROOM_TYPES:
            if obj is self._rooms_checkbox[room]:
                self._room_selected[room] = self._rooms_checkbox[room].value
                break
        self.update_gui({'rooms': None})

    def _create_widgets(self, panel):

        self._all_rooms_button = Button(panel,
                                        on_click=self._on_all_rooms)

        self._rooms_checkbox = {}

        for room in ROOM_TYPES:
            self._rooms_checkbox[room] = CheckBox(panel,
                                                  on_click=self._on_room_check,
                                                  value=self._room_selected[room])

        self._retrieve_info_button = Button(panel,
                                            on_click=self._on_get_huts_info_selected)

        self._close_button = Button(panel,
                                    on_click=self._on_button_close)

        self._grid_selected_detailed = self._create_grid(panel)

    def _create_grid(self, panel):
        grid = SelectedDetailedGrid(panel)
        grid.on_cell_left_double_click = self._on_row_left_double_click
        grid.on_cell_right_click = self._on_row_right_click
        return grid

    def _deselect(self, row):
        if len(self._selected) > 1:
            index = self._selected[row]
            self._controller.command_select({'which': index})

    def _on_button_close(self, obj):
        self.close()

    def _on_get_huts_info_selected(self, obj):
        data = {'which': 'selected'}
        self._controller.command_update_results(data)

    def _update_dates(self, request_dates):
        self._grid_selected_detailed.update_data(dates=request_dates)

    def _update_huts_data(self, huts_data):
        self._grid_selected_detailed.update_data(data_dictionary=huts_data)

    def _update_selected(self, data):
        selected, all_selected = data
        self._selected = selected
        self._grid_selected_detailed.update_data(indexes=selected)

    def _update_rooms(self):
        self._grid_selected_detailed.update_data(room_selected=self._room_selected)

    def _hut_pop_up_menu(self, row):
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

        menu = Menu(self, items=menu_labels, on_click=self._on_menu_item)
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
        self._menu_chosen_item = obj.get_item_label(choice_id)

    def _update_gui_for_language(self):
        self.title = i18n.all_strings['selected info']
        self._all_rooms_button.label = i18n.all_strings['all rooms']
        for room in ROOM_TYPES:
            self._rooms_checkbox[room].label = i18n.all_strings[room]
        self._grid_selected_detailed.update_for_language()
        self._retrieve_info_button.label = i18n.all_strings['retrieve selected detailed']
        self._close_button.label = i18n.all_strings['button close']

    def _update_gui_for_retrieve_enabled(self, is_enabled):
        self._retrieve_info_button.enable(is_enabled)
        super()._update_gui_for_retrieve_enabled(is_enabled)


class AbstractDeveloperInfoView(AbstractIconFrame):

    _STYLE = FrameStyle.FIXED_SIZE

    def __init__(self, info_type, **kwargs):
        self._developer_info = None
        self._info_type = info_type
        super().__init__(title=i18n.all_strings['developer info'], **kwargs)

    def _create_widgets(self, panel):
        self._main_label = Text(panel, font_size=11)

        self._no_info_label = Text(panel)

        self._grid_developer = DeveloperGrid(panel)

        self._log_button = Button(panel,
                                  on_click=self._on_log)

        self._ok_button = Button(panel,
                                 on_click=self._on_ok)

    def _save_log(self):
        config.save_log(self._info_type, self._developer_info)

    def update_gui(self, data):
        if 'developer_info' in data:
            self._update_gui_for_developer_info(data['developer_info'])
        if 'language' in data:
            self._update_gui_for_language()
        super().update_gui(data)

    def _refresh_widgets(self):
        self._grid_developer.refresh()

    def _update_gui_for_developer_info(self, data):
        self._developer_info = data
        self._grid_developer.update_data(developer_info=self._developer_info)
        self._grid_developer.hide(not self._developer_info)
        self._log_button.hide(not self._developer_info)
        self._no_info_label.hide(self._developer_info)

    def _update_gui_for_language(self):
        self.title = i18n.all_strings['developer info']

        label_id = f'no {self._info_type}'
        self._no_info_label.label = i18n.all_strings[label_id]

        self._grid_developer.update_for_language()
        self._log_button.label = i18n.all_strings['log']

        self._ok_button.label = i18n.all_strings['ok']
        label_id = f'info {self._info_type}'
        self._main_label.label = i18n.all_strings[label_id]

    def _on_log(self, obj):
        self._save_log()
        self._log_button.enable(False)

    def _on_ok(self, obj):
        self.close()


class AbstractFilterDialog(AbstractDialog):

    def __init__(self, **kwargs):
        self.filter_values = None, None
        super().__init__(**kwargs)

    def _create_widgets(self, panel):

        self._min_label = Text(panel, label=i18n.all_strings['min'])

        self._min_ctrl = TextControl(panel, label="")

        self._max_label = Text(panel, label=i18n.all_strings['max'])

        self._max_ctrl = TextControl(panel, label="")

        self._ok_button = Button(panel, label=i18n.all_strings['ok'], on_click=self._on_ok)

        self._cancel_button = Button(panel, label=i18n.all_strings['cancel'], on_click=self._on_cancel)

    def _on_ok(self, obj):
        self.filter_values = self._min_value, self._max_value
        super()._on_ok(obj)

    @property
    def _min_value(self):
        try:
            return int(self._min_ctrl.label)
        except ValueError:
            return None

    @property
    def _max_value(self):
        try:
            return int(self._max_ctrl.label)
        except ValueError:
            return None


class AbstractAboutDialog(AbstractDialog):

    def __init__(self, dialog_infos, **kwargs):
        self._dialog_infos = dialog_infos
        super().__init__(title=f"About {self._dialog_infos['name']}", **kwargs)

    def _create_widgets(self, panel):
        self._name_label = Text(panel, font_size=14)
        self._desc_label = Text(panel, font_size=12)
        self._copyright_label = Text(panel, font_size=10)
        self._website_label = Text(panel, font_size=10)
        self._developer_label = Text(panel, font_size=10)
        self._ok_button = Button(panel, on_click=self._on_ok)

    def update_gui(self, data):
        self._name_label.label = f"{self._dialog_infos['name']} {self._dialog_infos['version']}"
        self._desc_label.label = self._dialog_infos['description'][i18n.get_current_language()]
        self._copyright_label.label = self._dialog_infos['copyright']
        self._website_label.label = self._dialog_infos['website']
        self._developer_label.label = f"Developer: {self._dialog_infos['developer']}"
        self._ok_button.label = i18n.all_strings['ok']


class AbstractUpdateDialog(AbstractDialog):

    def __init__(self, available_updates, **kwargs):
        self._available_updates = available_updates
        self.approved_updates = None
        super().__init__(title=i18n.all_strings['available updates'], **kwargs)

    def _create_widgets(self, panel):

        self._labels = {}
        self._checkbox = {}
        for filename, (_, desc) in self._available_updates.items():
            label = Text(panel, label=i18n.all_strings[desc])
            label.on_left_down = self._on_label_click
            self._labels[filename] = label
            self._checkbox[filename] = CheckBox(panel, value=True)

        self._main_label = Text(panel, font_size=11)
        if self._available_updates:
            self._main_label.label = i18n.all_strings['choose updates']
        else:
            self._main_label.label = i18n.all_strings['no updates available']

        self._ok_button = Button(panel, label=i18n.all_strings['ok'], on_click=self._on_ok)

        self._cancel_button = Button(panel, label=i18n.all_strings['cancel'], on_click=self._on_cancel)

        if not self._available_updates:
            self._cancel_button.hide(True)

    def _on_label_click(self, obj, position):
        for filename, label in self._labels.items():
            if obj is label:
                self._checkbox[filename].value = not self._checkbox[filename].value

    def _on_ok(self, obj):
        self.approved_updates = {
            filename: path for filename, (path, _) in self._available_updates.items() if self._checkbox[filename].value
        }
        super()._on_ok(obj)
