"""
Definition of different types of data tables for the GUI interface.
All table classes are derived from the PrettYSUsI Grid class.

Classes:
    HutsGrid: the table for the main view
    SelectedDetailedGrid: the table for the detailed information about selected huts
    DetailedGrid: the table for the detailed information about a hut
    DeveloperGrid: the table for developer information
"""
import datetime

from src.model import ROOM_TYPES, HutStatus
from src import i18n
from src.view import errors
from prettysusi.tables import Align, Renderer, TextStyle
from prettysusi.tables import Grid

# Definition of colors
_WHITE = (255, 255, 255)
_LIGHT_GRAY = (220, 220, 220)
_DARK_GRAY = (70, 70, 70)
_BLACK = (0, 0, 0)
_RED = (255, 0, 0)
_ORANGE = (224, 129, 25)
_GREEN = (0, 100, 0)

# Definition of colors for table rows: [foreground, background]
_NEUTRAL_COLOUR = [_BLACK, _WHITE]
_HUT_STATUS_COLOURS = {
    HutStatus.NO_REQUEST: [_DARK_GRAY, _WHITE],
    HutStatus.NO_RESPONSE: [_WHITE, _ORANGE],
    HutStatus.CLOSED: [_BLACK, _LIGHT_GRAY],
    HutStatus.NOT_AVAILABLE: [_BLACK, _RED],
    HutStatus.AVAILABLE: [_GREEN, _WHITE]
}

# Definition of symbols
_SORT_ASCENDING_SYMBOL = ' \u2191'
_SORT_DESCENDING_SYMBOL = " \u2193"
_FILTER_SYMBOL = " Y"


class HutsGrid(Grid):
    """Define the table for the main view.

    Methods:
        update_data: update the data of the table

        From superclass:
        on_cell_left_click: executed when a left click is performed on a cell
        on_cell_left_double_click: executed when a left double click is performed on a cell
        on_cell_right_click: executed when a right click is performed on a cell
        on_cell_right_double_click: executed when a right double click is performed on a cell
        on_label_left_click: executed when a left click is performed on a key label
        on_label_left_double_click: executed when a left double click is performed on a key label
        on_label_right_click: executed when a right click is performed on a key label
        on_label_right_double_click: executed when a right double click is performed on a key label
        freeze_cols_width: freeze the columns width
        set_cols_width_as: set the column width with the same size as another table
        unfreeze_cols_width: unfreeze the columns width
        refresh: redraw the table applying the updates
    """

    _hide_row_labels = True
    _auto_size_cols = True
    _FIXED_ROW_NUMBERS = True

    def __init__(self, parent):
        """Initialize all internal data.

        :param parent: the parent frame
        """
        self._indexes = None
        self._keys = None
        self._data_dictionary = None
        self._selected = ()
        self._sort_key = None
        self._sort_ascending = None
        self._filter_keys = {}
        super().__init__(parent=parent)

    def update_data(self, indexes=None, keys=None, data_dictionary=None, selected=None,
                    sort_key=None, sort_ascending=None, filter_keys=None):
        """Update the data of the table.

        :param indexes: the indexes of the huts to display in the table
        :param keys: the keys of the information to display in the table
        :param data_dictionary: the dictionary with the information about the huts
        :param selected: the indexes of the selected huts
        :param sort_key: the key used to sort the huts in the table
        :param sort_ascending: true for ascending order, false for descending order
        :param filter_keys: the keys for which a filter is applied
        """
        if indexes is not None:
            self._indexes = indexes
        if keys is not None:
            self._keys = keys
        if data_dictionary is not None:
            self._data_dictionary = data_dictionary
        if selected is not None:
            self._selected = selected
        if sort_key is not None:
            self._sort_key = sort_key
        if sort_ascending is not None:
            self._sort_ascending = sort_ascending
        if filter_keys is not None:
            self._filter_keys = filter_keys

    def _get_number_rows(self):
        """Return the number of rows of the table.

        :return: the number of rows of the table
        """
        return len(self._indexes)

    def _get_number_cols(self):
        """Return the number of columns of the table.

        :return: the number of columns of the table
        """
        return len(self._keys)

    def _get_value(self, row, col):
        """Return the value to be displayed in a cell.

        :param row: the row of the cell
        :param col: the column of the cell
        :return: the value to be displayed in the cell
        """
        index = self._indexes[row]
        key = self._keys[col]
        if key == 'height':
            return str(int(self._data_dictionary[index][key]))
        elif key == 'distance':
            return str(int(self._data_dictionary[index][key] / 1000.))
        elif key in ['available'] + ROOM_TYPES:
            if not self._data_dictionary[index]['data_requested'] or not self._data_dictionary[index]['response'] \
                    or not self._data_dictionary[index]['open']:
                return ""
            else:
                if self._data_dictionary[index][key] is not None:
                    return str(self._data_dictionary[index][key])
                else:
                    return ""
        elif key == 'region':
            return i18n.regions_labels[self._data_dictionary[index][key]]
        elif key == 'mountain_range':
            return i18n.mountain_ranges_labels[self._data_dictionary[index][key]]
        else:
            try:
                return str(self._data_dictionary[index][key])
            except Exception as e:
                errors.append({'type': type(e), 'message': str(e)})
                return i18n.all_strings('table error')

    def _get_col_label_value(self, col):
        """Return the value to be displayed as the label of a column.

        :param col: the column
        :return: the value to be displayed as the label of the column
        """
        key = self._keys[col]
        if key == self._sort_key:
            if self._sort_ascending:
                symbol = _SORT_ASCENDING_SYMBOL
            else:
                symbol = _SORT_DESCENDING_SYMBOL
        else:
            symbol = ""
        if key in self._filter_keys:
            symbol += _FILTER_SYMBOL
        if symbol == "":
            return "   " + i18n.all_strings[self._keys[col]] + symbol + "   "
        else:
            return i18n.all_strings[self._keys[col]] + symbol

    def _get_row_col_colour(self, row, _col):
        """Return the colour to be used for a cell.

        :param row: the row of the cell
        :return: the colour to be used for the cell
        """
        index = self._indexes[row]
        if not self._data_dictionary[index]['data_requested']:
            colour = _HUT_STATUS_COLOURS[HutStatus.NO_REQUEST]
        elif not self._data_dictionary[index]['response']:
            colour = _HUT_STATUS_COLOURS[HutStatus.NO_RESPONSE]
        elif not self._data_dictionary[index]['open']:
            colour = _HUT_STATUS_COLOURS[HutStatus.CLOSED]
        elif self._data_dictionary[index]['available'] == 0:
            colour = _HUT_STATUS_COLOURS[HutStatus.NOT_AVAILABLE]
        else:
            colour = _HUT_STATUS_COLOURS[HutStatus.AVAILABLE]
        return colour

    def _get_style(self, row, _col):
        """Return the style to be used for a cell.

        :param row: the row of the cell
        :return: the style to be used for the cell
        """
        index = self._indexes[row]
        if index in self._selected:
            return TextStyle.BOLD
        else:
            return TextStyle.NORMAL

    def _get_align(self, _row, col):
        """Return the alignment to be used for a cell.

        :param col: the column of the cell
        :return: the alignment to be used for the cell
        """
        key = self._keys[col]
        if key in ['height', 'distance', 'available'] + ROOM_TYPES:
            return Align.RIGHT
        else:
            return Align.LEFT

    def _get_renderer(self, _row, col):
        """Return the renderer to be used for a cell.

        :param col: the column of the cell
        :return: the renderer to be used for the cell
        """
        key = self._keys[col]
        if key in ['self_catering', 'data_requested', 'response', 'open']:
            return Renderer.BOOLEAN
        else:
            return Renderer.NORMAL

    def get_values_for_filter(self, key):
        """Return the values for a key, to be used in the filter.

        :param key: the key
        :return: a dictionary with the displayed table values as keys and the corresponding data as value
        """
        values_dict = {}
        col = self._keys.index(key)
        for row in range(self._get_number_rows()):
            index = self._indexes[row]
            values_dict[self._get_value(row, col)] = self._data_dictionary[index][key]
        return values_dict


class SelectedDetailedGrid(Grid):
    """Define the table for the detailed information about selected huts.

    Methods:
        update_data: update the data of the table

        From superclass:
        on_cell_left_click: executed when a left click is performed on a cell
        on_cell_left_double_click: executed when a left double click is performed on a cell
        on_cell_right_click: executed when a right click is performed on a cell
        on_cell_right_double_click: executed when a right double click is performed on a cell
        on_label_left_click: executed when a left click is performed on a key label
        on_label_left_double_click: executed when a left double click is performed on a key label
        on_label_right_click: executed when a right click is performed on a key label
        on_label_right_double_click: executed when a right double click is performed on a key label
        freeze_cols_width: freeze the columns width
        set_cols_width_as: set the column width with the same size as another table
        unfreeze_cols_width: unfreeze the columns width
        refresh: redraw the table applying the updates
    """

    _hide_row_labels = True
    _auto_size_cols = True
    _auto_size_col_labels = True
    _DATE_FORMAT = '%d\n%m\n%Y'
    _FONT_SIZE = 9
    _AVOID_HORIZONTAL_SCROLL = True
    _AVOID_VERTICAL_SCROLL = True
    _GRID_ROW_NUMBERS = 6
    _FIXED_ROW_NUMBERS = True

    def __init__(self, parent):
        """Initialize all internal data.

        :param parent: the parent frame
        """
        self._indexes = None
        self._keys = None
        self._data_dictionary = None
        self._room_selected = None
        super().__init__(parent=parent)

    def update_data(self, indexes=None, dates=None, data_dictionary=None, room_selected=None):
        """Update the data of the table.

        :param indexes: the indexes of the huts to display in the table
        :param dates: the dates for which the information have to be displayed
        :param data_dictionary: the dictionary with the information about the huts
        :param room_selected: the selected room for which the information have to be displayed
        """
        if indexes is not None:
            self._indexes = indexes
        if dates is not None:
            self._keys = ['name'] + dates
        if data_dictionary is not None:
            self._data_dictionary = data_dictionary
        if room_selected is not None:
            self._room_selected = room_selected

    def _get_number_rows(self):
        """Return the number of rows of the table.

        :return: the number of rows of the table
        """
        return len(self._indexes)

    def _get_number_cols(self):
        """Return the number of columns of the table.

        :return: the number of columns of the table
        """
        return len(self._keys)

    def _get_value(self, row, col):
        """Return the value to be displayed in a cell.

        :param row: the row of the cell
        :param col: the column of the cell
        :return: the value to be displayed in the cell
        """
        index = self._indexes[row]
        key = self._keys[col]
        if isinstance(key, datetime.date):
            return self._get_value_for_date(index, key)
        else:
            try:
                return str(self._data_dictionary[index][key])
            except Exception as e:
                errors.append({'type': type(e), 'message': str(e)})
                return i18n.all_strings('table error')

    def _get_col_label_value(self, col):
        """Return the value to be displayed as the label of a column.

        :param col: the column
        :return: the value to be displayed as the label of the column
        """
        key = self._keys[col]
        if isinstance(key, datetime.date):
            return key.strftime(self._DATE_FORMAT)
        else:
            return i18n.all_strings[key]

    def _get_row_col_colour(self, row, col):
        """Return the colour to be used for a cell.

        :param row: the row of the cell
        :param col: the column of the cell
        :return: the colour to be used for the cell
        """
        index = self._indexes[row]
        if not self._data_dictionary[index]['response']:
            colour = _HUT_STATUS_COLOURS[HutStatus.NO_RESPONSE]
        elif col == 0:
            colour = _NEUTRAL_COLOUR
        else:
            value = self._get_value(row, col)
            if value == i18n.all_strings['no information available']:
                colour = _HUT_STATUS_COLOURS[HutStatus.NO_REQUEST]
            elif value == i18n.all_strings['closed']:
                colour = _HUT_STATUS_COLOURS[HutStatus.CLOSED]
            elif value == 0:
                colour = _HUT_STATUS_COLOURS[HutStatus.NOT_AVAILABLE]
            else:
                colour = _HUT_STATUS_COLOURS[HutStatus.AVAILABLE]
        return colour

    def _get_align(self, _row, col):
        """Return the alignment to be used for a cell.

        :param col: the column of the cell
        :return: the alignment to be used for the cell
        """
        key = self._keys[col]
        if isinstance(key, datetime.date):
            return Align.RIGHT
        else:
            return Align.LEFT

    def _get_value_for_date(self, index, date):
        """Return the value to be displayed for a specific hut index and date.

        :param index: the hut index
        :param date: the date
        :return: the value to be displayed for the specific hut index and date
        """
        if date not in self._data_dictionary[index]['detailed_places']:
            return i18n.all_strings['no information available']
        detailed_places = self._data_dictionary[index]['detailed_places'][date]
        if not detailed_places:
            return i18n.all_strings['no information available']
        if 'closed' in detailed_places:
            return i18n.all_strings['closed']
        value = 0
        for room in ROOM_TYPES:
            if room in detailed_places and self._room_selected[room]:
                value += detailed_places[room]
        return value


class DetailedGrid(Grid):
    """Define the table for the detailed information about a hut.

    Methods:
        update_data: update the data of the table

        From superclass:
        on_cell_left_click: executed when a left click is performed on a cell
        on_cell_left_double_click: executed when a left double click is performed on a cell
        on_cell_right_click: executed when a right click is performed on a cell
        on_cell_right_double_click: executed when a right double click is performed on a cell
        on_label_left_click: executed when a left click is performed on a key label
        on_label_left_double_click: executed when a left double click is performed on a key label
        on_label_right_click: executed when a right click is performed on a key label
        on_label_right_double_click: executed when a right double click is performed on a key label
        freeze_cols_width: freeze the columns width
        set_cols_width_as: set the column width with the same size as another table
        unfreeze_cols_width: unfreeze the columns width
        refresh: redraw the table applying the updates
    """

    _auto_size_cols = True
    _auto_size_row_labels = True
    _FONT_SIZE = 9
    _AVOID_HORIZONTAL_SCROLL = True
    _AVOID_VERTICAL_SCROLL = True
    _GRID_ROW_NUMBERS = 15
    _FIXED_ROW_NUMBERS = False

    def __init__(self, parent):
        """Initialize all internal data.

        :param parent: the parent frame
        """
        self._indexes = None
        self._keys = None
        self._available_places = None
        self._available_places_for_room = None
        self._detailed_places = None
        self._hut_status = None
        super().__init__(parent=parent)

    def update_data(self, hut_info):
        """Update the data of the table.

        :param hut_info: the information about the hut
        """
        self._available_places = hut_info['available']
        self._available_places_for_room = {room: hut_info[room] for room in ROOM_TYPES if hut_info[room] is not None}
        self._detailed_places = hut_info['detailed_places']
        self._hut_status = hut_info['status']

        keys = set()
        for detailed_places_for_date in self._detailed_places.values():
            keys.update(detailed_places_for_date.keys())
        if 'closed' in keys:
            keys.remove('closed')
        self._indexes = []
        for date in self._detailed_places:
            self._indexes.append(date)
        self._indexes.sort()
        self._indexes.append('all_dates')
        self._keys = list(keys) + ['all rooms']

    def _get_number_rows(self):
        """Return the number of rows of the table.

        :return: the number of rows of the table
        """
        return len(self._indexes)

    def _get_number_cols(self):
        """Return the number of columns of the table.

        :return: the number of columns of the table
        """
        return len(self._keys)

    def _get_value(self, row, col):
        """Return the value to be displayed in a cell.

        :param row: the row of the cell
        :param col: the column of the cell
        :return: the value to be displayed in the cell
        """
        index = self._indexes[row]
        key = self._keys[col]
        if index == 'all_dates':
            return self._get_value_for_all_dates(key)
        else:
            return self._get_value_for_detailed_places(key, index)

    def _get_col_label_value(self, col):
        """Return the value to be displayed as the label of a column.

        :param col: the column
        :return: the value to be displayed as the label of the column
        """
        key = self._keys[col]
        return i18n.all_strings[key]

    def _get_row_label_value(self, row):
        """Return the value to be displayed as the label of a row.

        :param row: the row
        :return: the value to be displayed as the label of the row
        """
        index = self._indexes[row]
        if index == 'all_dates':
            return i18n.all_strings['all dates']
        else:
            return str(index)

    def _get_row_col_colour(self, row, col):
        """Return the colour to be used for a cell.

        :param row: the row of the cell
        :param col: the column of the cell
        :return: the colour to be used for the cell
        """
        if self._hut_status is HutStatus.NO_RESPONSE:
            return _HUT_STATUS_COLOURS[HutStatus.NO_RESPONSE]
        value = self._get_value(row, col)
        if value == i18n.all_strings['closed']:
            return _HUT_STATUS_COLOURS[HutStatus.CLOSED]
        elif value == i18n.all_strings['no information available']:
            return _HUT_STATUS_COLOURS[HutStatus.NO_REQUEST]
        elif int(value) == 0:
            return _HUT_STATUS_COLOURS[HutStatus.NOT_AVAILABLE]
        else:
            return _HUT_STATUS_COLOURS[HutStatus.AVAILABLE]

    def _get_row_colour(self, row):
        """
        Return the colour to be used for the cells of a row.
        For GUIs which don't support a different colour on cells in the same row.

        :param row: the row
        :return: the colour to be used for the cells of the row
        """
        if self._hut_status is HutStatus.NO_RESPONSE:
            return _HUT_STATUS_COLOURS[HutStatus.NO_RESPONSE]
        index = self._indexes[row]
        if index == 'all_dates':
            value = self._get_value_for_all_dates('all rooms')
        else:
            value = self._get_value_for_detailed_places('all rooms', index)
        if value == i18n.all_strings['closed']:
            return _HUT_STATUS_COLOURS[HutStatus.CLOSED]
        elif value == i18n.all_strings['no information available']:
            return _HUT_STATUS_COLOURS[HutStatus.NO_REQUEST]
        elif int(value) == 0:
            return _HUT_STATUS_COLOURS[HutStatus.NOT_AVAILABLE]
        else:
            return _HUT_STATUS_COLOURS[HutStatus.AVAILABLE]

    def _get_align(self, _row, _col):
        """Return the alignment to be used for a cell.

        :return: the alignment to be used for the cell
        """
        return Align.RIGHT

    def _get_value_for_all_dates(self, key):
        """Return the information about all dates for a room type.

        :param key: the room type
        :return: the value to be displayed
        """
        if self._hut_status is HutStatus.CLOSED:
            return i18n.all_strings['closed']
        elif self._hut_status is HutStatus.NO_RESPONSE:
            return i18n.all_strings['no information available']
        elif key in self._available_places_for_room:
            return str(self._available_places_for_room[key])
        elif key == 'all rooms':
            if self._available_places_for_room == {}:
                return i18n.all_strings['no information available']
            else:
                return str(self._available_places)
        else:
            return i18n.all_strings['no information available']

    def _get_value_for_detailed_places(self, key, index):
        """Return the information about a single date for a room type.

        :param key: the room type
        :param index: the index of the date
        :return: the value to be displayed
        """
        if key in self._detailed_places[index]:
            return str(self._detailed_places[index][key])
        elif 'closed' in self._detailed_places[index]:
            return i18n.all_strings['closed']
        elif key == 'all rooms':
            if self._detailed_places[index] == {}:
                return i18n.all_strings['no information available']
            else:
                return str(sum([self._detailed_places[index][key] for key in self._detailed_places[index]]))
        else:
            return i18n.all_strings['no information available']


class DeveloperGrid(Grid):
    """Define the table for developer information.

    Methods:
        update_data: update the data of the table

        From superclass:
        on_cell_left_click: executed when a left click is performed on a cell
        on_cell_left_double_click: executed when a left double click is performed on a cell
        on_cell_right_click: executed when a right click is performed on a cell
        on_cell_right_double_click: executed when a right double click is performed on a cell
        on_label_left_click: executed when a left click is performed on a key label
        on_label_left_double_click: executed when a left double click is performed on a key label
        on_label_right_click: executed when a right click is performed on a key label
        on_label_right_double_click: executed when a right double click is performed on a key label
        freeze_cols_width: freeze the columns width
        set_cols_width_as: set the column width with the same size as another table
        unfreeze_cols_width: unfreeze the columns width
        refresh: redraw the table applying the updates
    """

    _hide_row_labels = True
    _auto_size_rows = True
    _auto_size_cols = True
    _keys = ['name', 'type', 'message']
    _FONT_SIZE = 9
    _AVOID_HORIZONTAL_SCROLL = True
    _GRID_ROW_NUMBERS = 4
    _FIXED_ROW_NUMBERS = False

    def __init__(self, parent):
        """Initialize all internal data.

        :param parent: the parent frame
        """
        self._developer_info = None
        super().__init__(parent=parent)

    def update_data(self, developer_info=None):
        """Update the data of the table.

        :param developer_info: the information for developers
        """
        if developer_info is not None:
            self._developer_info = developer_info

    def _get_number_rows(self):
        """Return the number of rows of the table.

        :return: the number of rows of the table
        """
        return len(self._developer_info)

    def _get_number_cols(self):
        """Return the number of columns of the table.

        :return: the number of columns of the table
        """
        return len(self._keys)

    def _get_value(self, row, col):
        """Return the value to be displayed in a cell.

        :param row: the row of the cell
        :param col: the column of the cell
        :return: the value to be displayed in the cell
        """
        key = self._keys[col]
        return str(self._developer_info[row][key])

    def _get_col_label_value(self, col):
        """Return the value to be displayed as the label of a column.

        :param col: the column
        :return: the value to be displayed as the label of the column
        """
        key = self._keys[col]
        return i18n.all_strings[f'developer table {key}']

    def _get_renderer(self, _row, col):
        """Return the renderer to be used for a cell.

        :param col: the column of the cell
        :return: the renderer to be used for the cell
        """
        key = self._keys[col]
        if key == 'message':
            return Renderer.AUTO_WRAP
        else:
            return Renderer.NORMAL
