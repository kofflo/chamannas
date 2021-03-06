import wx.lib.newevent


def event_create():
    event_class, event_binder = wx.lib.newevent.NewEvent()
    return {'class': event_class, 'binder': event_binder}
