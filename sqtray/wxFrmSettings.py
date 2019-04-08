import wx
from wxEvents import EVT_RESULT_CONNECTED_ID
from wxEvents import EVT_RESULT_PLAYERS_ID
from wxEvents import EVT_RESULT_CURRENT_TRACK_ID
from wxEvents import EVT_RESULT_CONNECTION_ID
import wxIcons
import logging

from modelsWxFrmSettings import mdlFrmSettings

class FrmSettings(wx.Frame):

    def __init__(self, parent,  title):
        self.log = logging.getLogger("FrmSettings")
        self.callbacks = {
            "on_apply" : {},
            "on_save" : {},
            "on_cancel" : {},
        }
        self.parent = parent
        self.title = title
        w, h = (250, 250)
        wx.Frame.__init__(self, self.parent, -1, self.title, wx.DefaultPosition, wx.Size(w, h))
        self.CreateStatusBar()
        self.sizer = wx.GridBagSizer(8, 3)
        self.Connect(-1, -1, EVT_RESULT_CONNECTED_ID, self.OnConnected)
        self.Connect(-1, -1, EVT_RESULT_PLAYERS_ID, self.OnConnected)
        self.Connect(-1, -1, EVT_RESULT_CONNECTION_ID, self.OnConnected)
        self.BtnApply = wx.Button(self, -1, "Apply")
        self.BtnCancel = wx.Button(self, -1, "Cancel")
        self.BtnSave = wx.Button(self, -1, "Save")
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=self.BtnCancel.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnSave, id=self.BtnSave.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnApply, id=self.BtnApply.GetId())
        self.sizer.Add(self.BtnApply, (8, 0), wx.DefaultSpan, wx.EXPAND)
        self.sizer.Add(self.BtnCancel, (8, 1), wx.DefaultSpan, wx.EXPAND)
        self.sizer.Add(self.BtnSave, (8, 2), wx.DefaultSpan, wx.EXPAND)
        label1 = wx.StaticText(self, -1, 'Host:')
        self.sizer.Add(label1, (0, 0), wx.DefaultSpan, wx.EXPAND)
        self.tcHost = wx.TextCtrl(self, -1 )
        self.sizer.Add(self.tcHost , (0, 1), (1, 2), wx.EXPAND)
        label2 = wx.StaticText(self, -1, 'Port:')
        self.sizer.Add(label2, (1, 0), wx.DefaultSpan, wx.EXPAND)
        label3 = wx.StaticText(self, -1, 'Player:')
        self.sizer.Add(label3, (2, 0), wx.DefaultSpan, wx.EXPAND)
        self.scPort = wx.SpinCtrl(self, -1, unicode(9000),  min=1, max=99999)
        self.sizer.Add(self.scPort, (1, 1), wx.DefaultSpan, wx.EXPAND)
        #self.statusbar = self.CreateStatusBar()
        #self.sizer.Add(self.statusbar, (9, 0),(2,9), wx.EXPAND)
        self.cbPlayer = wx.ComboBox(self, -1, style=wx.CB_READONLY)
        self.sizer.Add(self.cbPlayer, (2, 1), (1, 2), wx.EXPAND)
        self.sizer.AddGrowableRow(8)
        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableCol(1)
        self.sizer.AddGrowableCol(2)
        self.SetSizerAndFit(self.sizer)
        self.icon = wxIcons.trayDefault.getIcon()
        self.SetIcon(self.icon)
        self.IconStatus = None
        self.IconSize = None
        self.model = None
        self.GuiModel = mdlFrmSettings()
        self.GuiModel.statusText.addCallback(self.onStatusText)
        self.GuiModel.host.addCallback(self.onHost)
        self.GuiModel.port.addCallback(self.onPort)
        self.CurrentStatusText = None

    def ModelSet(self, model):
        self.model = model

    def cbAddOnApply(self, func):
        self.callbacks['on_apply'][func] = 1

    def cbDoOnApply(self):
        for item in self.callbacks["on_apply"]:
            item(self)
    def cbAddOnSave(self, func):
        self.callbacks['on_save'][func] = 1

    def cbDoOnSave(self):
        for item in self.callbacks["on_save"]:
            item(self)
    def cbAddOnCancel(self, func):
        self.callbacks['on_cancel'][func] = 1

    def cbDoOnCancel(self):
        for item in self.callbacks["on_cancel"]:
            item(self)

    def OnConnected(self, event):
        self.updateFromModel()

    def updateFromModel(self):
        if self.model  == None:
            return
        self.GuiModel.statusText.update(self.model.statusText.get())
        self.GuiModel.host.update(self.model.host.get())
        self.GuiModel.port.update(self.model.port.get())

    def onStatusText(self, value):
        self.SetStatusText(self.model.statusText.get())

    def onHost(self, value):
        self.tcHost.SetValue(self.GuiModel.host.get())

    def onPort(self, value):
        self.scPort.SetValue(self.GuiModel.port.get())

    def OnSave(self, event):
        self.OnApply(event)
        #self.app.configSave()
        #self.log.error('should call call back here')
        self.cbDoOnSave()
#
    def OnApply(self, event):
        newHost = self.tcHost.GetValue()
        self.model.host.update(newHost)
        newPort = int(self.scPort.GetValue())
        oldPort = self.model.port.get()
        self.model.port.update(newPort)
        self.cbDoOnApply()

    def OnCancel(self, event):
        #self.FrmCtrl.closeSettings(event)
        #self.app.tb.on_settings_close(event)
        #close = wx.PyEvent()
        #wx.EVT_CLOSE
        self.cbDoOnCancel ()
