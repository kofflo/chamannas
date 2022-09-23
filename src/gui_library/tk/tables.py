import tkinter
import tkinter.ttk
import tkinter.font

from src.view.abstract.tables import Align, TextStyle, Renderer, AbstractGrid
from src.gui_library.tk.widgets import Widget
from src.gui_library.tk import ttk_style

_UNCHECKED_BOX_SYMBOL = '\u2610'
_CHECKED_BOX_SYMBOL = '\u2611'


def rgb2hex(r, g, b, *args):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def fixed_map(style, option):
    """

    Return the style map for 'option' with any styles starting with ("!disabled", "!selected", ...) filtered out.

    :param style:
    :param option:
    :return:
    """
    return [element for element in style.map("Treeview", query_opt=option) if element[:2] != ("!disabled", "!selected")]


class TkAbstractGrid(AbstractGrid, Widget):

    _FONT_SIZE = 10
    _FONT_FAMILY = 'Helvetica'
    _ROW_HEIGHT = 22
    _COL_WIDTH = 100
    _COL_LABEL_HEIGHT = 42
    _ROW_LABEL_WIDTH = 80
    _MAX_COL_WIDTH = 600
    _MAX_ROW_LABEL_WIDTH = 200
    _HEADER_FOREGROUND_COLOR = (0, 0, 0)
    _HEADER_BACKGROUND_COLOR = (220, 220, 220)
    _GRID_ROW_NUMBERS = 10
    _FIXED_ROW_NUMBERS = True
    SCROLLBAR_X = True
    SCROLLBAR_Y = True
    _row_colour = True

    ttk_style.map("Treeview",
                  foreground=fixed_map(ttk_style, "foreground"),
                  background=fixed_map(ttk_style, "background"),
                  rowheight=fixed_map(ttk_style, "rowheight"))

    def __init__(self, panel):
        super().__init__()
        self._row_ids = []

        self._tk_font = (self._FONT_FAMILY, self._FONT_SIZE)
        self._tk_font_bold = (self._FONT_FAMILY, self._FONT_SIZE, 'bold')
        self._tk_font_italic = (self._FONT_FAMILY, self._FONT_SIZE, 'italic')
        self._tk_font_bold_italic = (self._FONT_FAMILY, self._FONT_SIZE, 'bold italic')

        ttk_style.element_create(str(id(self)) + '.Treeheading.border', 'from', 'default')
        ttk_style.layout(
            str(id(self)) + '.Treeview.Heading', [
                (str(id(self)) + '.Treeheading.cell', {'sticky': 'nswe'}),
                (str(id(self)) + '.Treeheading.border', {
                    'sticky': 'nswe', 'children': [
                        (str(id(self)) + '.Treeheading.padding', {
                            'sticky': 'nswe', 'children': [
                                (str(id(self)) + '.Treeheading.image', {'side': 'right', 'sticky': ''}),
                                (str(id(self)) + '.Treeheading.text', {'sticky': 'we'})
                            ]
                        })
                    ]
                }),
            ]
        )
        ttk_style.configure(str(id(self)) + '.Treeview.Heading',
                            font=(self._FONT_FAMILY, self._FONT_SIZE, 'bold'),
                            padding=(self._COL_LABEL_HEIGHT - self._ROW_HEIGHT) // 2,
                            foreground=rgb2hex(*self._HEADER_FOREGROUND_COLOR),
                            background=rgb2hex(*self._HEADER_BACKGROUND_COLOR))
        self._current_xview = None
        self._current_yview = None
        self._frame = None

    def hide(self, is_hidden):
        super().hide(is_hidden)
        if self._widget is not None:
            if self._is_hidden:
                if self.SCROLLBAR_X:
                    self.xsb.grid_remove()
                if self.SCROLLBAR_Y:
                    self.ysb.grid_remove()
            else:
                if self.SCROLLBAR_X:
                    self.xsb.grid()
                if self.SCROLLBAR_Y:
                    self.ysb.grid()

    def _create_widget(self, row_numbers):
        self._widget = tkinter.ttk.Treeview(self._frame, height=row_numbers,
                                            selectmode="none", style=str(id(self)) + '.Treeview')
        self._widget.bind("<Button-1>", self._on_left_click)
        self._widget.bind("<ButtonRelease-1>", self._on_left_release)
        self._widget.bind("<Double-1>", self._on_left_double_click)
        self._widget.bind("<Button-3>", self._on_right_click)
        self._widget.bind("<Double-3>", self._on_right_double_click)
        self._widget.bind("<Motion>", self._on_motion)
        if self.SCROLLBAR_X:
            self.xsb = tkinter.ttk.Scrollbar(self._frame, orient='horizontal', command=self.xview)
            self.configure(xscrollcommand=self.xsb.set)
        if self.SCROLLBAR_Y:
            self.ysb = tkinter.ttk.Scrollbar(self._frame, orient='vertical', command=self.yview)
            self.configure(yscrollcommand=self.ysb.set)

    def set_frame(self, frame):
        self._frame = frame
        self._font_for_measure = tkinter.font.Font(family=self._FONT_FAMILY, size=self._FONT_SIZE, weight='bold')
        self._dummy_text = tkinter.Text(self._frame, font=self._font_for_measure)
        self._create_widget(self._GRID_ROW_NUMBERS)

    def _on_motion(self, event):
        if self._widget.identify_region(event.x, event.y) in ['separator', 'heading']:
            return "break"

    def _on_left_release(self, event):
        return "break"

    def _identify_click(self, event):
        if self._widget.identify_region(event.x, event.y) == 'separator':
            return None, None

        if self._widget.identify_region(event.x, event.y) == 'heading':
            row = -1
        else:
            row_id = self._widget.identify_row(event.y)
            if row_id == '':
                return None, None
            row = self._row_ids.index(row_id)
        col = int(self._widget.identify_column(event.x)[1:]) - 1
        return row, col

    def _on_left_click(self, event):
        row, col = self._identify_click(event)
        if row is not None:
            if row == -1 or col == -1:
                self.on_label_left_click(self, row, col)
            else:
                self.on_cell_left_click(self, row, col)
        return "break"

    def _on_left_double_click(self, event):
        row, col = self._identify_click(event)
        if row is not None:
            if row == -1 or col == -1:
                self.on_label_left_double_click(self, row, col)
            else:
                self.on_cell_left_double_click(self, row, col)
        return "break"

    def _on_right_click(self, event):
        row, col = self._identify_click(event)
        if row is not None:
            if row == -1 or col == -1:
                self.on_label_right_click(self, row, col)
            else:
                self.on_cell_right_click(self, row, col)
        return "break"

    def _on_right_double_click(self, event):
        row, col = self._identify_click(event)
        if row is not None:
            if row == -1 or col == -1:
                self.on_label_right_double_click(self, row, col)
            else:
                self.on_cell_right_double_click(self, row, col)
        return "break"

    def _restore_position(self, event):
        self._widget.xview('moveto', self._current_xview)
        self._widget.yview('moveto', self._current_yview)

    def _refresh_row_numbers(self):
        if not self._FIXED_ROW_NUMBERS:
            grid_params = self._widget.grid_info()
            self._widget.grid_forget()
            if self.SCROLLBAR_X:
                grid_params_xsb = self.xsb.grid_info()
                self.xsb.grid_forget()
            if self.SCROLLBAR_Y:
                grid_params_ysb = self.ysb.grid_info()
                self.ysb.grid_forget()
            row_numbers = min(self._get_number_rows(), self._GRID_ROW_NUMBERS)
            self._create_widget(row_numbers)
            if grid_params:
                self._widget.grid(**grid_params)
                if self.SCROLLBAR_X:
                    self.xsb.grid(**grid_params_xsb)
                if self.SCROLLBAR_Y:
                    self.ysb.grid(**grid_params_ysb)

    def _refresh_columns(self):
        columns = []
        for col in range(self._get_number_cols()):
            columns.append(f"#{col + 1}")
        self._widget['columns'] = columns
        for col in range(self._get_number_cols()):
            if self._get_number_rows() > 0:
                align = self._get_align(0, col)
                renderer = self._get_renderer(0, col)
                if align is Align.LEFT:
                    anchor = tkinter.W
                elif align is Align.RIGHT:
                    anchor = tkinter.E
                else:
                    anchor = tkinter.CENTER
                if renderer is Renderer.BOOLEAN:
                    anchor = tkinter.CENTER
            else:
                anchor = tkinter.W
            self._widget.column(f"#{col + 1}", anchor=anchor, stretch=False)

    def _refresh_col_labels(self, col_auto_width):
        if not self._hide_col_labels:
            max_label_height = 0
            for col in range(self._get_number_cols()):
                label = self._get_col_label_value(col)
                self._widget.heading(f"#{col + 1}", text=label)
                max_label_height = max(max_label_height, label.count('\n'))
                label_rows = label.split('\n')
                if self._auto_size_cols and not self._col_widths:
                    label_width = 0
                    for label_row in label_rows:
                        label_width = max(label_width, self._font_for_measure.measure(label_row))
                    col_auto_width[col + 1] = max(col_auto_width[col + 1], label_width + 20)
            if self._auto_size_col_labels:
                self._widget.heading("#0", text='\n' * max_label_height)
        else:
            self._widget.configure(show='tree')

    def _refresh_rows(self, col_auto_width):
        for child in self._widget.get_children():
            self._widget.delete(child)
        self._row_ids.clear()

        for row in range(self._get_number_rows()):
            row_values = []
            for col in range(self._get_number_cols()):
                value = self._get_value(row, col)
                renderer = self._get_renderer(row, col)
                if renderer is Renderer.BOOLEAN:
                    value = (_UNCHECKED_BOX_SYMBOL, _CHECKED_BOX_SYMBOL)[bool(int(value))]
                row_values.append(value)
                if self._auto_size_cols and not self._col_widths:
                    col_auto_width[col + 1] = max(col_auto_width[col + 1], self._font_for_measure.measure(value))

            foreground_color, background_color = self._get_colour(row, 0)
            fg_string = rgb2hex(*foreground_color)
            bg_string = rgb2hex(*background_color)

            text_style = self._get_style(row, 0)
            if text_style is TextStyle.BOLD:
                font = self._tk_font_bold
            elif text_style is TextStyle.ITALIC:
                font = self._tk_font_italic
            elif text_style is TextStyle.BOLD_ITALIC:
                font = self._tk_font_bold_italic
            else:
                font = self._tk_font

            tag = fg_string + bg_string + str(font)
            self._widget.tag_configure(tag, foreground=fg_string, background=bg_string, font=font)
            row_label = self._get_row_label_value(row)
            row_id = self._widget.insert('', 'end', text=row_label, values=row_values, tags=(tag,))
            if self._auto_size_row_labels:
                col_auto_width[0] = max(col_auto_width[0], self._font_for_measure.measure(row_label))
            self._row_ids.append(row_id)

    def refresh(self):
        self._refresh_row_numbers()

        self._refresh_columns()

        col_auto_width = [0] * (self._get_number_cols() + 1)

        self._refresh_col_labels(col_auto_width)

        self._refresh_rows(col_auto_width)

        if self._hide_row_labels:
            self._widget.column('#0', minwidth=0, width=0)
        elif self._auto_size_row_labels:
            self._widget.column('#0', width=min(col_auto_width[0] + 25, self._MAX_ROW_LABEL_WIDTH))
        else:
            self._widget.column('#0', width=self._ROW_LABEL_WIDTH)

        if self._col_widths is not None:
            self._set_frozen_cols_width()
        elif self._auto_size_cols:
            for col in range(self._get_number_cols()):
                self._set_col_size(col, min(col_auto_width[col + 1] + 10, self._MAX_COL_WIDTH))
        else:
            self._set_col_sizes(self._COL_WIDTH)

        # Treeview has no possibility to set the row height individually for each row
        # Therefore "_auto_size_rows" cannot be implemented
        # Similarly, there is no autowrap available and "Renderer.AUTO_WRAP" cannot be implemented
        ttk_style.configure(str(id(self)) + '.Treeview', rowheight=self._ROW_HEIGHT)

    def _get_row_size(self, row):
        return ttk_style.lookup('chamannas.Treeview', 'rowheight')

    def _get_col_size(self, col):
        return self._widget.column(f"#{col + 1}")['width']

    def _set_row_size(self, row, size):
        self._set_row_sizes(size)

    def _set_row_sizes(self, size):
        self._style.configure('chamannas.Treeview', rowheight=size)

    def _set_col_size(self, col, size):
        self._widget.column(f"#{col + 1}", width=size)

    def _set_col_sizes(self, size):
        for col in range(self._get_number_cols()):
            self._widget.column(f"#{col + 1}", width=size)
