from enum import Enum, auto

from src.gui_library.abstract.widgets import AbstractWidget, TextStyle


class Align(Enum):
    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()


class Renderer(Enum):
    NORMAL = auto()
    BOOLEAN = auto()
    AUTO_WRAP = auto()


# COLOUR FOR TABLE ROWS: [foreground, background]
_NORMAL_COLOUR = [(0, 0, 0), (255, 255, 255)]


class AbstractGrid(AbstractWidget):

    _hide_row_labels = False
    _hide_col_labels = False
    _auto_size_rows = False
    _auto_size_cols = False
    _auto_size_row_labels = False
    _auto_size_col_labels = False
    _row_colour = False
    _MAXIMUM_HEIGHT = None
    _MAXIMUM_WIDTH = None
    _MINIMUM_HEIGHT = None
    _MINIMUM_WIDTH = None

    def __init__(self, **kwargs):
        self._col_widths = None
        super().__init__(**kwargs)

    def _get_number_rows(self):
        raise NotImplementedError

    def _get_number_cols(self):
        raise NotImplementedError

    def _get_value(self, row, col):
        raise NotImplementedError

    def _get_row_label_value(self, row):
        return ""

    def _get_col_label_value(self, col):
        return ""

    def _get_colour(self, row, col):
        if self._row_colour:
            return self._get_row_colour(row)
        else:
            return self._get_row_col_colour(row, col)

    def _get_row_col_colour(self, row, col):
        return _NORMAL_COLOUR

    def _get_row_colour(self, row):
        return self._get_row_col_colour(row, 0)

    def _get_style(self, row, col):
        return TextStyle.NORMAL

    def _get_align(self, row, col):
        return Align.LEFT

    def _get_renderer(self, row, col):
        return Renderer.NORMAL

    def _get_row_size(self, row):
        raise NotImplementedError

    def _get_col_size(self, col):
        raise NotImplementedError

    def _set_row_size(self, row, size):
        raise NotImplementedError

    def _set_col_size(self, col, size):
        raise NotImplementedError

    def _set_row_label_size(self, size):
        raise NotImplementedError

    def _set_col_label_size(self, size):
        raise NotImplementedError

    def update_data(self, **kwargs):
        raise NotImplementedError

    def on_cell_left_click(self, obj, row, col):
        #
        pass

    def on_cell_left_double_click(self, obj, row, col):
        #
        pass

    def on_cell_right_click(self, obj, row, col):
        #
        pass

    def on_cell_right_double_click(self, obj, row, col):
        #
        pass

    def on_label_left_click(self, obj, row, col):
        #
        pass

    def on_label_left_double_click(self, obj, row, col):
        #
        pass

    def on_label_right_click(self, obj, row, col):
        #
        pass

    def on_label_right_double_click(self, obj, row, col):
        #
        pass

    def freeze_cols_width(self):
        self._col_widths = []
        for col in range(self._get_number_cols()):
            self._col_widths.append(self._get_col_size(col))

    def set_cols_width_as(self, other_grid):
        self._col_widths = []
        for col in range(other_grid._get_number_cols()):
            self._col_widths.append(other_grid._get_col_size(col))

    def _set_frozen_cols_width(self):
        if self._col_widths is not None:
            for col in range(self._get_number_cols()):
                self._set_col_size(col, self._col_widths[col])

    def unfreeze_cols_width(self):
        self._col_widths = None

    def update_for_language(self):
        #
        pass

    def refresh(self):
        raise NotImplementedError
