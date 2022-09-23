import wx.grid

from src.view.abstract.tables import Align, TextStyle, Renderer, AbstractGrid
from src.gui_library.wx.widgets import Widget


class GridTable(wx.grid.GridTableBase):
    pass


class WxAbstractGrid(AbstractGrid, Widget, wx.grid.Grid):
    _FONT_SIZE = 10
    _ROW_HEIGHT = 22
    _COL_WIDTH = 80
    _MAX_COL_WIDTH = 400
    _COL_LABEL_HEIGHT = 32
    _ROW_LABEL_WIDTH = 80

    def __init__(self, panel):
        super().__init__()
        wx.grid.Grid.__init__(self, panel)

        self._wx_font = wx.Font(wx.FontInfo(self._FONT_SIZE))
        self._wx_font_bold = wx.Font(wx.FontInfo(self._FONT_SIZE).Bold())
        self._wx_font_italic = wx.Font(wx.FontInfo(self._FONT_SIZE).Italic())
        self._wx_font_bold_italic = wx.Font(wx.FontInfo(self._FONT_SIZE).Bold().Italic())

        self._grid_table = self._get_grid_table()

        self.EnableEditing(False)
        self.EnableDragRowSize(False)
        self.EnableDragColSize(False)
        self.SetCellHighlightPenWidth(0)
        self.SetCellHighlightROPenWidth(0)

        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self._on_cell_left_click)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self._on_cell_left_double_click)
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self._on_cell_right_click)
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_DCLICK, self._on_cell_right_double_click)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self._on_label_left_click)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self._on_label_left_double_click)
        self.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self._on_label_right_click)
        self.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_DCLICK, self._on_label_right_double_click)
        self.GetGridWindow().Bind(wx.EVT_MOTION, self._on_motion)

    def _get_grid_table(self):
        grid_table = GridTable()
        grid_table.GetNumberRows = self._get_number_rows
        grid_table.GetNumberCols = self._get_number_cols
        grid_table.GetValue = self._get_value
        grid_table.GetColLabelValue = self._get_col_label_value
        grid_table.GetRowLabelValue = self._get_row_label_value
        grid_table.GetAttr = self._get_attr
        return grid_table

    def _on_cell_left_click(self, event):
        row = event.GetRow()
        col = event.GetCol()
        self.on_cell_left_click(self, row, col)

    def _on_cell_left_double_click(self, event):
        row = event.GetRow()
        col = event.GetCol()
        self.on_cell_left_double_click(self, row, col)

    def _on_cell_right_click(self, event):
        row = event.GetRow()
        col = event.GetCol()
        self.on_cell_right_click(self, row, col)

    def _on_cell_right_double_click(self, event):
        row = event.GetRow()
        col = event.GetCol()
        self.on_cell_right_double_click(self, row, col)

    def _on_label_left_click(self, event):
        row = event.GetRow()
        col = event.GetCol()
        self.on_label_left_click(self, row, col)

    def _on_label_left_double_click(self, event):
        row = event.GetRow()
        col = event.GetCol()
        self.on_label_left_double_click(self, row, col)

    def _on_label_right_click(self, event):
        row = event.GetRow()
        col = event.GetCol()
        self.on_label_right_click(self, row, col)

    def _on_label_right_double_click(self, event):
        row = event.GetRow()
        col = event.GetCol()
        self.on_label_right_double_click(self, row, col)

    def _on_motion(self, event):
        # Traps the motion event
        pass

    def refresh(self):
        self._refresh_attributes()
        self.BeginBatch()
        self.SetTable(self._grid_table, False)
        if self._hide_row_labels:
            self.HideRowLabels()
        elif self._auto_size_row_labels:
            self.SetRowLabelSize(wx.grid.GRID_AUTOSIZE)
        else:
            self.SetRowLabelSize(self._ROW_LABEL_WIDTH)
        if self._hide_col_labels:
            self.HideColLabels()
        elif self._auto_size_col_labels:
            self.SetColLabelSize(wx.grid.GRID_AUTOSIZE)
        else:
            self.SetColLabelSize(self._COL_LABEL_HEIGHT)
        if self._auto_size_rows:
            self.AutoSizeRows()
        else:
            self._set_row_sizes(self._ROW_HEIGHT)
        if self._col_widths is not None:
            self._set_frozen_cols_width()
        elif self._auto_size_cols:
            self.AutoSizeColumns()
        else:
            self._set_col_sizes(self._COL_WIDTH)
        if self._MINIMUM_HEIGHT is not None:
            self.SetMinSize(wx.Size(width=-1, height=self._MINIMUM_HEIGHT))
        if self._MAXIMUM_HEIGHT is not None:
            self.SetMaxSize(wx.Size(width=-1, height=self._MAXIMUM_HEIGHT))
        if self._MINIMUM_WIDTH is not None:
            self.SetMinSize(wx.Size(width=-1, height=self._MINIMUM_WIDTH))
        if self._MAXIMUM_WIDTH is not None:
            self.SetMaxSize(wx.Size(width=-1, height=self._MAXIMUM_WIDTH))
        self.EndBatch()

    def _refresh_attributes(self):
        for row in range(self._get_number_rows()):
            for col in range(self._get_number_cols()):
                self.RefreshAttr(row, col)

    def _get_attr(self, row, col, kind):
        colour = self._get_colour(row, col)
        style = self._get_style(row, col)
        align = self._get_align(row, col)
        renderer = self._get_renderer(row, col)

        attr = wx.grid.GridCellAttr()
        attr.SetTextColour(wx.Colour(colour[0]))
        attr.SetBackgroundColour(wx.Colour(colour[1]))

        if style is TextStyle.BOLD:
            attr.SetFont(self._wx_font_bold)
        elif style is TextStyle.ITALIC:
            attr.SetFont(self._wx_font_italic)
        elif style is TextStyle.BOLD_ITALIC:
            attr.SetFont(self._wx_font_bold_italic)
        else:
            attr.SetFont(self._wx_font)

        if align is Align.RIGHT:
            attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        elif align is Align.LEFT:
            attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        else:
            attr.SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        if renderer is Renderer.BOOLEAN:
            attr.SetRenderer(wx.grid.GridCellBoolRenderer())
            attr.SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        elif renderer is Renderer.AUTO_WRAP:
            attr.SetRenderer(wx.grid.GridCellAutoWrapStringRenderer())
            self._set_col_size(col, self._MAX_COL_WIDTH)
        return attr

    def _get_row_size(self, row):
        return self.GetRowSize(row)

    def _get_col_size(self, col):
        return self.GetColSize(col)

    def _set_row_size(self, row, size):
        self.SetRowSize(row, size)

    def _set_row_sizes(self, size):
        row_sizes = wx.grid.GridSizesInfo()
        row_sizes.m_sizeDefault = size
        self.SetRowSizes(row_sizes)

    def _set_col_size(self, col, size):
        self.SetColSize(col, size)

    def _set_col_sizes(self, size):
        col_sizes = wx.grid.GridSizesInfo()
        col_sizes.m_sizeDefault = size
        self.SetColSizes(col_sizes)
