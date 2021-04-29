from src.view.abstract.tables import AbstractHutsGrid, AbstractDetailedGrid, \
    AbstractDeveloperGrid, AbstractSelectedDetailedGrid

from src.gui_library.tk.tables import TkAbstractGrid


class HutsGrid(TkAbstractGrid, AbstractHutsGrid):
    pass


class DetailedGrid(TkAbstractGrid, AbstractDetailedGrid):

    _FONT_SIZE = 9
    _GRID_ROW_NUMBERS = 15
    _FIXED_ROW_NUMBERS = False
    SCROLLBAR_X = False
    SCROLLBAR_Y = False


class SelectedDetailedGrid(TkAbstractGrid, AbstractSelectedDetailedGrid):

    _FONT_SIZE = 9
    _GRID_ROW_NUMBERS = 6
    _FIXED_ROW_NUMBERS = False
    SCROLLBAR_X = False


class DeveloperGrid(TkAbstractGrid, AbstractDeveloperGrid):

    _FONT_SIZE = 9
    _GRID_ROW_NUMBERS = 4
    _FIXED_ROW_NUMBERS = False
    _auto_size_cols = True
