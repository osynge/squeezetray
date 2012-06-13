

import wx


class Example(wx.Frame):
  
    def __init__(self, parent,  title):
        
        self.parent = parent
        self.title = title
        w, h = (250, 250)
        wx.Frame.__init__(self, self.parent, -1, self.title, wx.DefaultPosition, wx.Size(w, h))
        self.CreateStatusBar()
        
        self.SetStatusText("Demonstration of wxPython")
        self.sizer = wx.GridBagSizer(8, 3)
        
        
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
    
    def Show(self):
        self.UpdateCbPlayer()
        
        self.tcHost.SetValue(self.app.GetSqueezeServerHost())
        self.scPort.SetValue(self.app.GetSqueezeServerPort())
        
        self.Centre()
        #self.SetSize(wx.Size(w, h))
        super(Example, self).Show()
    def OnConnected(self,event):
        
        if True == self.app.squeezeConCtrl.ConnectionOnline():
            self.SetStatusText("Server Connected.")
        else:
            self.SetStatusText("Server not connected.")
        self.OnUpdate()
        print "self.app.squeezeConCtrl.PlayersList()=%s" % self.app.squeezeConCtrl.PlayersList()
    def UpdateCbPlayer(self):
        
        self.cbPlayer.Clear()
        
        #availablePlayers = self.app.ConMan.GetSqueezeServerPlayers()
        availablePlayers = self.app.squeezeConCtrl.PlayersList()
        #print "availablePlayers=%s" % (availablePlayers)
        
        
        for player in availablePlayers:
            self.cbPlayer.Append(player)
        if len(availablePlayers) > 0:
            CurrentPlayer = self.app.GetSqueezeServerPlayer()
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
        self.app.SetSqueezeServerHost(self.tcHost.GetValue())
        self.app.SqueezeServerPort.set((int(self.scPort.GetValue())))
        self.app.SetSqueezeServerPlayer(self.cbPlayer.GetValue())
        self.UpdateCbPlayer()
    def OnCancel(self, event):
        self.app.tb.on_settings_close(event)
        
