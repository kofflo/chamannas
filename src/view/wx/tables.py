from src.view.abstract_view.tables import AbstractHutsGrid, AbstractDetailedGrid, \
    AbstractDeveloperGrid, AbstractSelectedDetailedGrid

from src.gui_library.wx.tables import WxAbstractGrid


class HutsGrid(WxAbstractGrid, AbstractHutsGrid):
    pass


class DetailedGrid(WxAbstractGrid, AbstractDetailedGrid):

    _FONT_SIZE = 9


class SelectedDetailedGrid(WxAbstractGrid, AbstractSelectedDetailedGrid):

    _FONT_SIZE = 9


class DeveloperGrid(WxAbstractGrid, AbstractDeveloperGrid):

    _FONT_SIZE = 9
