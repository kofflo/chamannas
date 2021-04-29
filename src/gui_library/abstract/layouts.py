from enum import Flag, auto


class Align(Flag):
    LEFT = auto()
    HCENTER = auto()
    RIGHT = auto()
    TOP = auto()
    VCENTER = auto()
    BOTTOM = auto()
    START = LEFT | TOP
    CENTER = HCENTER | VCENTER
    END = RIGHT | BOTTOM
    EXPAND = auto()


class AbstractLayout:

    def create_layout(self, parent):
        raise NotImplementedError()


class AbstractBoxLayout(AbstractLayout):
    def __init__(self):
        self._widgets = []

    def add(self, widget, align=Align.START, border=0, stretch=0):
        self._widgets.append({'type': widget, 'align': align, 'border': border, 'stretch': stretch})

    def add_space(self, space):
        self._widgets.append({'type': 'space', 'space': space})

    def add_stretch(self, stretch=1):
        self._widgets.append({'type': 'stretch', 'stretch': stretch})


class AbstractGridLayout(AbstractLayout):
    def __init__(self, rows, cols, vgap, hgap):
        self._rows = rows
        self._cols = cols
        self._widgets = [[None] * self._cols for _ in range(self._rows)]
        self._row_stretch = [None] * self._rows
        self._col_stretch = [None] * self._rows
        self._vgap = vgap
        self._hgap = hgap

    def add(self, row, col, widget, align=Align.CENTER, border=0):
        self._widgets[row][col] = {'type': widget, 'align': align, 'border': border}

    def add_space(self, row, col, width, height):
        self._widgets[row][col] = {'type': 'space', 'width': width, 'height': height}

    def create_sizer(self):
        raise NotImplementedError()

    def row_stretch(self, row, stretch):
        self._row_stretch[row] = stretch

    def col_stretch(self, col, stretch):
        self._col_stretch[col] = stretch
