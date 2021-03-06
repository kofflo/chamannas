from src.view.abstract.tables import AbstractHutsGrid, AbstractDetailedGrid, \
    AbstractDeveloperGrid, AbstractSelectedDetailedGrid

from src.gui_library.qt5.tables import QtAbstractGrid


class HutsGrid(QtAbstractGrid, AbstractHutsGrid):
    pass


class DetailedGrid(QtAbstractGrid, AbstractDetailedGrid):

    _FONT_SIZE = 9
    _AVOID_HORIZONTAL_SCROLL = True
    _AVOID_VERTICAL_SCROLL = True


class SelectedDetailedGrid(QtAbstractGrid, AbstractSelectedDetailedGrid):

    _FONT_SIZE = 9
    _AVOID_HORIZONTAL_SCROLL = True
    _AVOID_VERTICAL_SCROLL = True
    _MAXIMUM_HEIGHT = 300


class DeveloperGrid(QtAbstractGrid, AbstractDeveloperGrid):

    _FONT_SIZE = 9
    _AVOID_HORIZONTAL_SCROLL = True
