from src.view.abstract_view.tables import AbstractHutsGrid, AbstractDetailedGrid, \
    AbstractDeveloperGrid, AbstractSelectedDetailedGrid

from src.gui_library.qt5.tables import QtAbstractGrid


class HutsGrid(QtAbstractGrid, AbstractHutsGrid):
    pass


class DetailedGrid(QtAbstractGrid, AbstractDetailedGrid):

    _FONT_SIZE = 9
    _FIXED_WIDTH_TABLE = True
    _FIXED_HEIGHT_TABLE = True


class SelectedDetailedGrid(QtAbstractGrid, AbstractSelectedDetailedGrid):

    _FONT_SIZE = 9
    _FIXED_WIDTH_TABLE = True
    _FIXED_HEIGHT_TABLE = True


class DeveloperGrid(QtAbstractGrid, AbstractDeveloperGrid):

    _FONT_SIZE = 9
    _FIXED_WIDTH_TABLE = True
