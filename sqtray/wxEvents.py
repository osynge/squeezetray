
import wx
# Define notification event for thread completion
EVT_RESULT_CONNECTION_ID = wx.NewId()
EVT_RESULT_CONNECTED_ID = wx.NewId()
EVT_RESULT_PLAYERS_ID = wx.NewId()
EVT_RESULT_CURRENT_TRACK_ID = wx.NewId()



class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class ResultEvent2(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, wxTypeId, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(wxTypeId)
        self.data = data
