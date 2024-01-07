import wx

from ..abstract.layouts import AbstractBoxLayout, AbstractGridLayout, Align


class Layout:
    _BORDER_FLAGS = [wx.TOP, wx.RIGHT, wx.BOTTOM, wx.LEFT]

    def create_layout(self, parent):
        raise NotImplementedError()

    def apply_align(self, align):
        if align & Align.EXPAND:
            flag = wx.EXPAND
        else:
            flag = 0
        return flag

    def _apply_border(self, widget, border_tuple, align):
        min_border = float('inf')
        flag = 0
        for index, b in enumerate(border_tuple):
            if b != 0:
                if b < min_border:
                    min_border = b
                flag |= self._BORDER_FLAGS[index]

        border_tuple = tuple(max(0, b - min_border) for b in border_tuple)

        if any(b != 0 for b in border_tuple):
            widget, widget_border, flag_border = self._apply_border(widget, border_tuple, align)
            box = wx.BoxSizer(wx.VERTICAL)
            if align & Align.EXPAND:
                flag_border |= wx.EXPAND
            box.Add(widget, border=widget_border, flag=flag_border)
            widget = box

        return widget, min_border, flag


class BoxLayout(AbstractBoxLayout, Layout):
    _DIRECTION = None

    def create_layout(self, parent):
        sizer = wx.BoxSizer(self._DIRECTION)
        for widget_dict in self._widgets:
            widget = widget_dict['type']
            if widget == 'space':
                sizer.AddSpacer(widget_dict['space'])
            elif widget == 'stretch':
                sizer.AddStretchSpacer(widget_dict['stretch'])
            else:
                widget_align = widget_dict['align']
                flag = self.apply_align(widget_align)

                if isinstance(widget, Layout):
                    widget = widget.create_layout(None)

                widget_border = widget_dict['border']
                if isinstance(widget_border, int):
                    flag |= wx.ALL
                elif any(b != 0 for b in widget_border):
                    widget, widget_border, flag_border = self._apply_border(widget, widget_border, widget_align)
                    flag |= flag_border
                else:
                    widget_border = 0

                sizer.Add(widget, proportion=widget_dict['stretch'], flag=flag, border=widget_border)

        if parent is not None:
            parent.SetSizer(sizer)
        return sizer


class VBoxLayout(BoxLayout):
    _DIRECTION = wx.VERTICAL

    def apply_align(self, align):
        flag = super().apply_align(align)
        if flag == 0:
            if align & Align.LEFT:
                flag = wx.ALIGN_LEFT
            elif align & Align.HCENTER:
                flag = wx.ALIGN_CENTER_HORIZONTAL
            elif align & Align.RIGHT:
                flag = wx.ALIGN_RIGHT
        return flag


class HBoxLayout(BoxLayout):
    _DIRECTION = wx.HORIZONTAL

    def apply_align(self, align):
        flag = super().apply_align(align)
        if flag == 0:
            if align & Align.TOP:
                flag = wx.ALIGN_TOP
            elif align & Align.VCENTER:
                flag = wx.ALIGN_CENTER_VERTICAL
            elif align & Align.BOTTOM:
                flag = wx.ALIGN_BOTTOM
        return flag


class GridLayout(AbstractGridLayout, Layout):

    def create_layout(self, parent):
        sizer = wx.FlexGridSizer(self._rows, self._cols, self._vgap, self._hgap)

        for row in range(self._rows):
            if self._row_stretch[row] is not None:
                sizer.AddGrowableRow(row, self._row_stretch[row])

        for col in range(self._cols):
            if self._row_stretch[col] is not None:
                sizer.AddGrowableCol(col, self._col_stretch[col])

        for widgets_row in self._widgets:
            for widget_dict in widgets_row:
                widget = widget_dict['type']
                if widget is None:
                    sizer.Add(0, 0)
                elif widget == 'space':
                    sizer.Add(widget_dict['width'], widget_dict['height'])
                else:
                    widget_align = widget_dict['align']
                    flag = self.apply_align(widget_align)

                    if isinstance(widget, Layout):
                        widget = widget.create_layout(None)

                    widget_border = widget_dict['border']
                    if isinstance(widget_border, int):
                        flag |= wx.ALL
                    elif any(b != 0 for b in widget_border):
                        widget, widget_border, flag_border = self._apply_border(widget, widget_border, widget_align)
                        flag |= flag_border
                    else:
                        widget_border = 0

                    sizer.Add(widget, flag=flag, border=widget_border)

        if parent is not None:
            parent.SetSizer(sizer)
        return sizer

    def apply_align(self, align):
        flag = super().apply_align(align)
        if flag == 0:
            if align & Align.TOP:
                flag = wx.ALIGN_TOP
            elif align & Align.VCENTER:
                flag = wx.ALIGN_CENTER_VERTICAL
            elif align & Align.BOTTOM:
                flag = wx.ALIGN_BOTTOM
            if align & Align.LEFT:
                flag |= wx.ALIGN_LEFT
            elif align & Align.HCENTER:
                flag |= wx.ALIGN_CENTER_HORIZONTAL
            elif align & Align.RIGHT:
                flag |= wx.ALIGN_RIGHT
        return flag
