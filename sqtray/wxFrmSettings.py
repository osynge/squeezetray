

import wx
from wxEvents import EVT_RESULT_CONNECTED_ID
from wxEvents import EVT_RESULT_PLAYERS_ID
from wxEvents import EVT_RESULT_CURRENT_TRACK_ID
from wxEvents import EVT_RESULT_CONNECTION_ID
class FrmSettings(wx.Frame):
  
    def __init__(self, parent,  title):
        self.parent = parent
        self.title = title
        w, h = (250, 250)
        wx.Frame.__init__(self, self.parent, -1, self.title, wx.DefaultPosition, wx.Size(w, h))
        self.CreateStatusBar()
        self.sizer = wx.GridBagSizer(8, 3)
        self.Connect(-1, -1, EVT_RESULT_CONNECTED_ID, self.OnConnected)
        self.Connect(-1, -1, EVT_RESULT_PLAYERS_ID, self.OnPlayersEvt)
        self.Connect(-1, -1, EVT_RESULT_CONNECTION_ID, self.OnPlayersEvt)
        self.BtnApply = wx.Button(self,-1, "Apply")
        self.BtnCancel = wx.Button(self,-1, "Cancel")
        self.BtnSave = wx.Button(self,-1, "Save")
        

        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=self.BtnCancel.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnSave,id=self.BtnSave.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnApply,id=self.BtnApply.GetId())

        
        
        
        self.sizer.Add(self.BtnApply, (8, 0), wx.DefaultSpan, wx.EXPAND)
        self.sizer.Add(self.BtnCancel, (8, 1), wx.DefaultSpan, wx.EXPAND)
        self.sizer.Add(self.BtnSave, (8, 2), wx.DefaultSpan, wx.EXPAND)
        
        label1 = wx.StaticText(self, -1, 'Host:')
        
        self.sizer.Add(label1, (0, 0), wx.DefaultSpan, wx.EXPAND)
        
        self.tcHost = wx.TextCtrl(self, -1 )
        self.sizer.Add(self.tcHost , (0, 1), (1,2), wx.EXPAND)
        label2 = wx.StaticText(self, -1, 'Port:')
        
        
        self.sizer.Add(label2, (1, 0), wx.DefaultSpan, wx.EXPAND)
        label3 = wx.StaticText(self, -1, 'Player:')
        
        self.sizer.Add(label3, (2, 0), wx.DefaultSpan, wx.EXPAND)
        
        self.scPort = wx.SpinCtrl(self, -1, unicode(9000),  min=1, max=99999)
        self.sizer.Add(self.scPort, (1, 1),wx.DefaultSpan, wx.EXPAND)
        #self.statusbar = self.CreateStatusBar()
        #self.sizer.Add(self.statusbar, (9, 0),(2,9), wx.EXPAND)
        
        self.cbPlayer = wx.ComboBox(self, -1, style=wx.CB_READONLY)
        self.sizer.Add(self.cbPlayer, (2, 1), (1,2), wx.EXPAND)
        
        
        self.sizer.AddGrowableRow(8)
        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableCol(1)
        self.sizer.AddGrowableCol(2)
        
        self.SetSizerAndFit(self.sizer)
    def UpdateStatusbar(self):
        if not hasattr(self,'model'):
            self.SetStatusText("")
            return
        if False == self.model.connected.get():
            self.SetStatusText("Server not connected.")
            return
        CurrentPlayer = self.model.GuiPlayer.get()
        if CurrentPlayer != None:
            host = self.model.host.get()
            port = self.model.port.get()
            self.SetStatusText("%s@%s:%s" % (CurrentPlayer,host,port))
            return
    def ModelSet(self,model):
        self.model = model
    
    def Show(self):
        self.UpdateStatusbar()
        self.UpdateCbPlayer()
        self.OnPlayers()
        self.Centre()
        #self.SetSize(wx.Size(w, h))
        
        super(FrmSettings, self).Show()
        
    def OnConnectionChange(self,event):
        host = self.model.host.get()
        #print 'host', host
        self.tcHost.SetValue(host)
        port = self.model.port.get()
        self.scPort.SetValue(port)
        self.UpdateCbPlayer()
        self.UpdateStatusbar()

    def OnConnected(self,event):
        self.UpdateStatusbar()
    
    def OnPlayers(self):
        host = self.model.host.get()
        #print 'host', host
        self.tcHost.SetValue(host)
        port = self.model.port.get()
        self.scPort.SetValue(port)
        self.UpdateCbPlayer()
    def OnPlayersEvt(self,event):
        self.OnPlayers()
        self.UpdateStatusbar()
    def UpdateCbPlayer(self):
        #print "here we go" , self.cbPlayer.GetStrings()
        currentOptions = self.cbPlayer.GetStrings()
        availablePlayers = self.app.squeezeConCtrl.PlayersList()
        if currentOptions != availablePlayers:
            self.cbPlayer.Clear()
            for player in availablePlayers:
                self.cbPlayer.Append(player)
        else:
            pass
        if len(availablePlayers) == 0:
            self.cbPlayer.Clear()
            self.cbPlayer.SetSelection(-1)
        else:
            CurrentPlayer = self.model.GuiPlayer.get()
            playerIndex = 0
            if CurrentPlayer != None:
                try:
                    playerIndex = availablePlayers.index(CurrentPlayer)
                except:
                    playerIndex = 0
            self.cbPlayer.SetSelection(playerIndex)
    def OnSave(self, event):
        self.OnApply(event)
        self.app.configSave()
        

    def OnApply(self, event):
        newHost = self.tcHost.GetValue()
        oldHost = self.model.host.get()
        if newHost != oldHost:
            #print 'hostchanged',newHost
            self.model.host.set(newHost)
            #print 'donehostchanged',newHost
        newPort = int(self.scPort.GetValue())
        oldPort = self.model.port.get()
        if newPort != oldPort:
            self.model.port.set(newPort)
        newDefaultPlayer = unicode(self.cbPlayer.GetValue())
        #print "newDefaultPlayer",newDefaultPlayer
        oldDefaultPlayer = self.model.GuiPlayerDefault.get()
        #print "oldDefaultPlayer",oldDefaultPlayer
        if oldDefaultPlayer != newDefaultPlayer:
            self.model.GuiPlayerDefault.set(newDefaultPlayer)
        self.UpdateCbPlayer()
        oldPlayer =  self.model.GuiPlayer.get()
        if oldPlayer != newDefaultPlayer:
            #print "oldPlayer",oldPlayer 
            self.model.GuiPlayer.set(newDefaultPlayer)
        #print 'dddd',self.model.host.get(),self.model.port.get(),self.model.GuiPlayer.get()
    def OnCancel(self, event):
        self.FrmCtrl.closeSettings(event)
        #self.app.tb.on_settings_close(event)
        #close = wx.PyEvent()
        #wx.EVT_CLOSE
        
