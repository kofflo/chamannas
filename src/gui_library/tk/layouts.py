import tkinter

from src.gui_library.abstract.layouts import AbstractBoxLayout, AbstractGridLayout, Align
from src.gui_library.tk.tables import TkAbstractGrid


class TkLayout:

    def create_layout(self, parent):
        raise NotImplementedError()

    def apply_border(self, border_tuple):
        return [border_tuple[3], border_tuple[1]], [border_tuple[0], border_tuple[2]]

    def apply_align(self, align):
        raise NotImplementedError()


class BoxLayout(AbstractBoxLayout, TkLayout):
    _DIRECTION = None
    i = 0
    colors = ['red', 'blue', 'green', 'yellow']

    def __init__(self):
        self._delta_row = 0
        self._delta_col = 0
        super().__init__()

    def create_layout(self, parent):
        frame = tkinter.Frame(parent, bg=self.colors[BoxLayout.i])
        print("creo frame", self.colors[BoxLayout.i])
        BoxLayout.i += 1
        if BoxLayout.i > 3:
            BoxLayout.i = 0
        for index, widget_dict in enumerate(self._widgets):
            widget = widget_dict['type']

            if widget == 'space':
                self.create_space(frame, index, widget_dict['space'])
            elif widget == 'stretch':
                self.create_stretch(frame, index, widget_dict['stretch'])
            else:
                row, col = self._get_row_col(index)

                widget_align = widget_dict['align']
                sticky = self.apply_align(widget_align)

                widget_border = widget_dict['border']
                if isinstance(widget_border, int):
                    widget_border = [widget_border] * 4
                padx, pady = self.apply_border(widget_border)
                if isinstance(widget, TkLayout):
                    widget = widget.create_layout(frame)
                    widget.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)
                elif isinstance(widget, TkAbstractGrid):
                    frame_grid = tkinter.Frame(frame)
                    widget.set_frame(frame_grid)
                    if widget.SCROLLBAR_X:
                        pady_grid = 0
                    else:
                        pady_grid = pady[1]
                    if widget.SCROLLBAR_Y:
                        padx_grid = 0
                    else:
                        padx_grid = padx[1]
                    pippo_row = row
                    pippo_col = col
                    row = 0
                    col = 0
                    if widget.SCROLLBAR_X:
                        widget.xsb.grid(row=row+1, column=col, padx=(padx[0], padx_grid), pady=(5, pady[1]), sticky='new')
#                        self._delta_row += 1
                    if widget.SCROLLBAR_Y:
                        widget.ysb.grid(row=row, column=col+1, padx=(5, padx[1]), pady=(pady[0], pady_grid), sticky='nsw')
#                        self._delta_col += 1
                    widget.grid(row=row, column=col, padx=(padx[0], padx_grid), pady=(pady[0], pady_grid), sticky=sticky)
                    frame_grid.columnconfigure(0, weight=1)
                    frame_grid.rowconfigure(0, weight=1)
                    frame_grid.grid(row=pippo_row, column=pippo_col, sticky=sticky)
                else:
                    widget.set_frame(frame)
                    widget.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)

                widget_stretch = widget_dict['stretch']
                self.create_stretch(frame, index, widget_stretch)

        return frame

    def _get_row_col(self, index):
        raise NotImplementedError()

    def create_space(self, frame, index, space):
        raise NotImplementedError()

    def create_stretch(self, frame, index, space):
        raise NotImplementedError()


class VBoxLayout(BoxLayout):
    def create_space(self, frame, index, space):
        frame.grid_rowconfigure(index, minsize=space)

    def create_stretch(self, frame, index, stretch):
        frame.grid_rowconfigure(index, weight=stretch)

    def _get_row_col(self, index):
        return index + self._delta_row, 0

    def apply_align(self, align):
        if align & Align.EXPAND:
            return "ew"
        elif align & Align.LEFT:
            return "w"
        elif align & Align.HCENTER:
            return ""
        elif align & Align.RIGHT:
            return "e"
        return ""


class HBoxLayout(BoxLayout):

    def create_space(self, frame, index, space):
        frame.grid_columnconfigure(index, minsize=space)

    def create_stretch(self, frame, index, stretch):
        frame.grid_columnconfigure(index, weight=stretch)

    def _get_row_col(self, index):
        return 0, index + self._delta_col

    def apply_align(self, align):
        if align & Align.EXPAND:
            return "ns"
        elif align & Align.TOP:
            return "n"
        elif align & Align.VCENTER:
            return ""
        elif align & Align.BOTTOM:
            return "s"
        return ""


class GridLayout(AbstractGridLayout, TkLayout):

    def create_layout(self, parent):
        frame = tkinter.Frame(parent)

        for row in range(self._rows):
            if self._row_stretch[row] is not None:
                frame.grid_rowconfigure(row, weight=self._row_stretch[row])

        for col in range(self._cols):
            if self._row_stretch[col] is not None:
                frame.grid_columnconfigure(col, weight=self._col_stretch[col])

        for row, widgets_row in enumerate(self._widgets):
            for col, widget_dict in enumerate(widgets_row):
                widget = widget_dict['type']
                if widget == 'space':
                    frame.grid_rowconfigure(row, minsize=widget_dict['height'])
                    frame.grid_columnconfigure(col, minsize=widget_dict['width'])
                else:
                    widget_align = widget_dict['align']
                    sticky = self.apply_align(widget_align)

                    if isinstance(widget, TkLayout):
                        widget = widget.create_layout(frame)
                    else:
                        widget.set_frame(frame)

                    widget_border = widget_dict['border']
                    if isinstance(widget_border, int):
                        widget_border = [widget_border] * 4
                    padx, pady = self.apply_border(widget_border)

                    if row != 0:
                        pady[0] += self._vgap / 2
                    if row != self._rows - 1:
                        pady[1] += self._vgap / 2
                    if col != 0:
                        padx[0] += self._hgap / 2
                    if col != self._cols - 1:
                        padx[1] += self._hgap / 2

                    widget.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)
        return frame

    def apply_align(self, align):
        if align & Align.EXPAND:
            return "nsew"
        else:
            sticky=""
            if align & Align.TOP:
                sticky += "n"
            elif align & Align.BOTTOM:
                sticky += "s"
            if align & Align.LEFT:
                sticky += "w"
            elif align & Align.RIGHT:
                sticky += "e"
            return sticky
