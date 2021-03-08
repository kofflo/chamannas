import wx
import wx.adv
import wx.lib.newevent

from src.view.abstract.frames import AbstractIconFrame, FrameStyle, CursorStyle, AbstractDialog


class WxFrame(AbstractIconFrame, wx.Frame):

    _NEW_VERSION = False
    def __init__(self, *, parent, pos=None, size=None, **kwargs):

        if self._STYLE is FrameStyle.FIXED_SIZE:
            style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        elif self._STYLE is FrameStyle.DIALOG:
            style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX)
        else:
            style = wx.DEFAULT_FRAME_STYLE
        if pos is None:
            wx_pos = wx.DefaultPosition
        else:
            wx_pos = wx.Point(*pos)
        if size is None:
            wx_size = wx.DefaultSize
        else:
            wx_size = wx.Size(*size)
        wx.Frame.__init__(self, parent, style=style, pos=wx_pos, size=wx_size)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self._panel = wx.Panel(self)
        self._frame_sizer = wx.BoxSizer(wx.VERTICAL)
        self._frame_sizer.Add(self._panel)
        super().__init__(parent=parent, **kwargs)
        self._create_widgets(self._panel)
        if self._NEW_VERSION is True:
            print('NEW VERSION')
            self._create_gui().create_layout(self._panel)
        else:
            self._create_gui()
        self._create_menu()

    def event_connect(self, event, on_event):
        self.Bind(event['binder'], lambda e: on_event(**e._getAttrDict()))

    def event_trigger(self, event, **kwargs):
        event = event['class'](**kwargs)
        wx.CallAfter(wx.PostEvent, self, event)

    def _create_menu(self):
        #
        pass

    def _create_gui(self):
        raise NotImplementedError

    @property
    def title(self):
        return super(WxFrame, WxFrame).title.__get__(self)

    @title.setter
    def title(self, title):
        super(WxFrame, WxFrame).title.__set__(self, title)
        self.SetTitle(title)

    @property
    def icon(self):
        return super(WxFrame, WxFrame).icon.__get__(self)

    @icon.setter
    def icon(self, icon):
        super(WxFrame, WxFrame).icon.__set__(self, icon)
        self.SetIcon(wx.Icon(self.icon))

    def show(self):
        self.Show()

    def close(self):
        self.Close()

    def _on_close(self, event):
        self.detach()
        self.on_close(self)
        event.Skip()

    def _set_menubar(self, menu):
        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)
        menu.build_menu(menubar=menubar)

    def _fit_frame(self):
        self.Layout()
        self.SetSizerAndFit(self._frame_sizer)

    def _set_cursor(self, cursor):
        if cursor is CursorStyle.SIZING:
            self.SetCursor(wx.Cursor(wx.CURSOR_SIZING))
        elif cursor is CursorStyle.ARROW:
            self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

    def set_focus(self):
        self.SetFocus()


class WxDialog(AbstractDialog, wx.Dialog):

    _NEW_VERSION = False

    def __init__(self, parent, **kwargs):
        wx.Dialog.__init__(self, parent)
        super().__init__(**kwargs)
        self._create_widgets(self)
        if self._NEW_VERSION is True:
            print('NEW VERSION')
            self._create_gui().create_layout(self)
            self.Fit()
            self.SetSizeHints(self.GetSize().x, self.GetSize().y, self.GetMaxWidth(), self.GetMaxHeight())
        else:
            self._create_gui()
        self.SetIcon(wx.Icon(parent.icon))

    def _create_gui(self):
        raise NotImplementedError

    @property
    def title(self):
        return super(WxDialog, WxDialog).title.__get__(self)

    @title.setter
    def title(self, title):
        super(WxDialog, WxDialog).title.__set__(self, title)
        self.SetTitle(title)

    def show_modal(self):
        self.update_gui({})
        return self.ShowModal() == 1

    def _on_ok(self, obj):
        super()._on_ok(obj)
        self.EndModal(self._return_value)

    def _on_cancel(self, obj):
        super()._on_cancel(obj)
        self.EndModal(self._return_value)
