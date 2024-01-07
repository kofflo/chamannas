import PySide6.QtWidgets
import PySide6.QtCore
import PySide6.QtGui

from ..abstract.tables import Align, TextStyle, Renderer, AbstractGrid
from .widgets import Widget, rgb2hex

_UNCHECKED_BOX_SYMBOL = '\u2610'
_CHECKED_BOX_SYMBOL = '\u2611'


class GridTable(PySide6.QtCore.QAbstractTableModel):
    pass


class TableHeader(PySide6.QtWidgets.QHeaderView):

    def mousePressEvent(self, event):
        button = event.button()
        index = self.logicalIndexAt(event.pos())
        if self.orientation() is PySide6.QtGui.Qt.Horizontal:
            row = -1
            col = index
        else:
            row = index
            col = -1
        if button is PySide6.QtCore.Qt.LeftButton:
            self.parent().on_label_left_click(self.parent(), row, col)
        elif button is PySide6.QtCore.Qt.RightButton:
            self.parent().on_label_right_click(self.parent(), row, col)

    def mouseDoubleClickEvent(self, event):
        button = event.button()
        index = self.indexAt(event.pos())
        row = index.row()
        col = index.column()
        if button is PySide6.QtCore.Qt.LeftButton:
            self.parent().on_label_left_double_click(self.parent(), row, col)
        elif button is PySide6.QtCore.Qt.RightButton:
            self.parent().on_label_right_double_click(self.parent(), row, col)


class Grid(AbstractGrid, Widget, PySide6.QtWidgets.QTableView):

    def __init__(self, panel):
        PySide6.QtWidgets.QTableView.__init__(self, panel)
        super().__init__()
        self.setHorizontalHeader(TableHeader(PySide6.QtGui.Qt.Horizontal, self))
        self.setVerticalHeader(TableHeader(PySide6.QtGui.Qt.Vertical, self))

        self._qt_font = PySide6.QtGui.QFont('Helvetica', self._FONT_SIZE)
        self._qt_font_bold = PySide6.QtGui.QFont('Helvetica', self._FONT_SIZE)
        self._qt_font_bold.setBold(True)
        self._qt_font_italic = PySide6.QtGui.QFont('Helvetica', self._FONT_SIZE)
        self._qt_font_italic.setItalic(True)
        self._qt_font_bold_italic = PySide6.QtGui.QFont('Helvetica', self._FONT_SIZE)
        self._qt_font_bold_italic.setBold(True)
        self._qt_font_bold_italic.setItalic(True)

        self._font_dict = {
            TextStyle.NORMAL: self._qt_font,
            TextStyle.BOLD: self._qt_font_bold,
            TextStyle.ITALIC: self._qt_font_italic,
            TextStyle.BOLD_ITALIC: self._qt_font_bold_italic
        }

        self._align_dict = {
            Align.LEFT: int(PySide6.QtCore.Qt.AlignLeft | PySide6.QtCore.Qt.AlignVCenter),
            Align.CENTER: int(PySide6.QtCore.Qt.AlignCenter),
            Align.RIGHT: int(PySide6.QtCore.Qt.AlignRight | PySide6.QtCore.Qt.AlignVCenter),
        }
        self._grid_table = self._get_grid_table()

        color_string = rgb2hex(*self._get_header_colour()[1])
        header_stylesheet = "::section{Background-color : %s}" % color_string
        self.horizontalHeader().setStyleSheet(header_stylesheet)
        self.verticalHeader().setStyleSheet(header_stylesheet)
        corner_stylesheet = "QTableCornerButton::section{Background-color : %s}" % color_string
        self.setStyleSheet(corner_stylesheet)
        self.setCornerButtonEnabled(False)

        self.horizontalHeader().setSectionResizeMode(PySide6.QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setSectionResizeMode(PySide6.QtWidgets.QHeaderView.Fixed)
        self.setSelectionMode(self.SelectionMode.NoSelection)
        self.setEditTriggers(self.EditTrigger.NoEditTriggers)
        self.setFocusPolicy(PySide6.QtCore.Qt.NoFocus)
        self.setSizePolicy(PySide6.QtWidgets.QSizePolicy.Minimum, PySide6.QtWidgets.QSizePolicy.Minimum)

    def _get_grid_table(self):
        grid_table = GridTable()
        grid_table.rowCount = self._get_row_count
        grid_table.columnCount = self._get_column_count
        grid_table.data = self._get_data
        grid_table.headerData = self._get_header_data
        return grid_table

    def _get_row_count(self, index):
        return self._get_number_rows()

    def _get_column_count(self, index):
        return self._get_number_cols()

    def _get_data(self, index, role):
        row = index.row()
        column = index.column()
        renderer = self._get_renderer(row, column)
        if role == PySide6.QtCore.Qt.DisplayRole:
            value = self._get_value(row, column)
            if renderer is Renderer.BOOLEAN:
                return (_UNCHECKED_BOX_SYMBOL, _CHECKED_BOX_SYMBOL)[bool(int(value))]
            else:
                return value
        elif role == PySide6.QtCore.Qt.FontRole:
            return self._font_dict[self._get_style(row, column)]
        elif role == PySide6.QtCore.Qt.ForegroundRole:
            return PySide6.QtGui.QColor.fromRgb(*self._get_colour(row, column)[0])
        elif role == PySide6.QtCore.Qt.BackgroundRole:
            return PySide6.QtGui.QColor.fromRgb(*self._get_colour(row, column)[1])
        elif role == PySide6.QtCore.Qt.TextAlignmentRole:
            if renderer is Renderer.BOOLEAN:
                return self._align_dict[Align.CENTER]
            else:
                return self._align_dict[self._get_align(row, column)]
        if renderer is Renderer.AUTO_WRAP:
            self._set_col_size(column, self._MAX_COL_WIDTH)

    def _get_header_data(self, index, orientation, role):
        if role == PySide6.QtCore.Qt.DisplayRole:
            if orientation == PySide6.QtCore.Qt.Horizontal:
                return self._get_col_label_value(index)
            elif orientation == PySide6.QtCore.Qt.Vertical:
                return self._get_row_label_value(index)
        elif role == PySide6.QtCore.Qt.FontRole:
            return self._qt_font_bold
        elif role == PySide6.QtCore.Qt.ForegroundRole:
            return PySide6.QtGui.QColor.fromRgb(*self._get_header_colour()[0])

    def mousePressEvent(self, event):
        button = event.button()
        index = self.indexAt(event.pos())
        row = index.row()
        col = index.column()
        if row == -1 or col == -1:
            return
        if button is PySide6.QtCore.Qt.LeftButton:
            self.on_cell_left_click(self, row, col)
        elif button is PySide6.QtCore.Qt.RightButton:
            self.on_cell_right_click(self, row, col)

    def mouseDoubleClickEvent(self, event):
        button = event.button()
        index = self.indexAt(event.pos())
        row = index.row()
        col = index.column()
        if row == -1 or col == -1:
            return
        if button is PySide6.QtCore.Qt.LeftButton:
            self.on_cell_left_double_click(self, row, col)
        elif button is PySide6.QtCore.Qt.RightButton:
            self.on_cell_right_double_click(self, row, col)

    def refresh(self):
        self.setModel(self._grid_table)
        self._grid_table.layoutChanged.emit()

        if self._hide_row_labels:
            self.verticalHeader().hide()
        elif not self._auto_size_row_labels:
            self.verticalHeader().setFixedWidth(self._ROW_LABEL_WIDTH)
        if self._hide_col_labels:
            self.horizontalHeader().hide()
        elif not self._auto_size_col_labels:
            self.horizontalHeader().setFixedHeight(self._COL_LABEL_HEIGHT)
        if self._auto_size_rows:
            self.resizeRowsToContents()
        else:
            self._set_row_sizes(self._ROW_HEIGHT)
        if self._col_widths is not None:
            self._set_frozen_cols_width()
        elif self._auto_size_cols:
            self.resizeColumnsToContents()
        else:
            self._set_row_sizes(self._COL_WIDTH)

        height = 0
        width = 0

        if self._AVOID_HORIZONTAL_SCROLL:
            self.setHorizontalScrollBarPolicy(PySide6.QtGui.Qt.ScrollBarAlwaysOff)
            width = self.horizontalHeader().length()
            if not self.verticalHeader().isHidden():
                width += self.verticalHeader().width()
            if self._MAXIMUM_WIDTH is not None and width > self._MAXIMUM_WIDTH:
                width = self._MAXIMUM_WIDTH
                self.setHorizontalScrollBarPolicy(PySide6.QtGui.Qt.ScrollBarAsNeeded)
                height += self.horizontalScrollBar().height()

        if self._AVOID_VERTICAL_SCROLL:
            self.setVerticalScrollBarPolicy(PySide6.QtGui.Qt.ScrollBarAlwaysOff)
            height = self.verticalHeader().length()
            if not self.horizontalHeader().isHidden():
                height += self.horizontalHeader().height()
            if self._MAXIMUM_HEIGHT is not None and height > self._MAXIMUM_HEIGHT:
                height = self._MAXIMUM_HEIGHT
                self.setVerticalScrollBarPolicy(PySide6.QtGui.Qt.ScrollBarAsNeeded)
                width += self.verticalScrollBar().width()

        if self._AVOID_HORIZONTAL_SCROLL:
            self.setFixedWidth(width)
        elif self._MAXIMUM_WIDTH is not None:
            self.setMaximumWidth(self._MAXIMUM_WIDTH)
        if self._MINIMUM_WIDTH is not None:
            self.setMinimumWidth(self._MAXIMUM_WIDTH)
        if self._AVOID_VERTICAL_SCROLL:
            self.setFixedHeight(height)
        elif self._MAXIMUM_HEIGHT is not None:
            self.setMaximumHeight(self._MAXIMUM_HEIGHT)
        if self._MINIMUM_HEIGHT is not None:
            self.setMinimumHeight(self._MINIMUM_HEIGHT)

    def _get_row_size(self, row):
        return self.rowHeight(row)

    def _get_col_size(self, col):
        return self.columnWidth(col)

    def _set_row_size(self, row, size):
        self.setRowHeight(row, size)

    def _set_row_sizes(self, size):
        self.verticalHeader().setSectionResizeMode(self.verticalHeader().ResizeMode.Fixed)
        self.verticalHeader().setDefaultSectionSize(size)

    def _set_col_size(self, col, size):
        self.setColumnWidth(col, size)

    def _set_col_sizes(self, size):
        self.horizontalHeader().setSectionResizeMode(self.horizontalHeader().ResizeMode.Fixed)
        self.horizontalHeader().setDefaultSectionSize(size)
