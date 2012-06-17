
import wx
from wxEvents import EVT_RESULT_CONNECTED_ID
from wxEvents import EVT_RESULT_PLAYERS_ID
from wxEvents import EVT_RESULT_CURRENT_TRACK_ID
from sqtray.wxFrmSettings import FrmSettings
import datetime
import functools
import wxIcons
TRAY_TOOLTIP = 'SqueezeTray'
TRAY_ICON = 'icon.png'


def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item






class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self,model):
        super(TaskBarIcon, self).__init__()
        self.model = model
        #self.set_icon(TRAY_ICON)
        self.icon = wxIcons.trayDefault.getIcon()
        self.SetIcon(self.icon,"SqueezeTray")
        self.Bind(wx.EVT_TASKBAR_MOVE, self.on_move)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_TASKBAR_LEFT_UP, self.on_left_up )
        #self.Bind(wx.EVT_TASKBAR_RIGHT_DOWN, self.on_right_down )
        #self.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.on_right_up )
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.on_left_dclick)
        self.Bind(wx.EVT_TASKBAR_RIGHT_DCLICK, self.on_right_dclick)
        #self.Bind(wx.EVT_TASKBAR_CLICK, self.on_click )
        #self.squeezecmd = sc
        self.Example = None
        self.Connect(-1, -1, EVT_RESULT_PLAYERS_ID, self.OnPlayers)
        self.Connect(-1, -1, EVT_RESULT_CURRENT_TRACK_ID, self.OnTrack)
        #self.ToolTipText = TRAY_TOOLTIP
        
        
        TIMER_ID = wx.NewId()  # pick a number
        self.timer = wx.Timer(self, TIMER_ID)  # message will be sent to the panel
        self.timer.Start(9000)  # x100 milliseconds
        wx.EVT_TIMER(self, TIMER_ID, self.on_timer)  # call the on_timer function

    def Show(self):
        
        self.app.squeezeConCtrl.RecConnectionOnline()
        super(TaskBarIcon, self).Show()        
        
    def GetSqueezeServerPlayer(self):
        if not hasattr(self,'model'):
            return None
        return self.model.GuiPlayer.get()

    def OnPlayers(self, event):
        #print "OnPlayers(=%s)" % (Event)            
        self.UpdateToolTip()
        
    def OnTrack(self, event):
        self.UpdateToolTip()
    def UpdateToolTip(self):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            for index in  range(len(self.model.playerList)):
                playerName = self.model.playerList[index].name.get()
                if playerName == player:
                    newToolTip = unicode(player)
                    CurrentOperationMode = self.model.playerList[index].operationMode.get()
                    if CurrentOperationMode != None:
                        newToolTip += ":%s" % (CurrentOperationMode)
                    CurrentTrackTitle = self.model.playerList[index].CurrentTrackTitle.get()
                    if CurrentTrackTitle != None:
                        newToolTip += "\nTrack:%s" % (CurrentTrackTitle)
                    CurrentTrackArtist = self.model.playerList[index].CurrentTrackArtist.get()
                    if CurrentTrackArtist != None:
                        newToolTip += "\nArtist:%s" % (CurrentTrackArtist)
                    CurrentTrackEnds = self.model.playerList[index].CurrentTrackEnds.get()
                    #print "CurrentTrackEnds=%s" % (CurrentTrackEnds)
                    if CurrentTrackEnds != None:
                        seconds = (CurrentTrackEnds - datetime.datetime.now()).total_seconds()
                        newToolTip += "\nRemaining:%s" % (seconds)
                    self.set_toolTip(newToolTip)

    def OnShowPopup(self, event):
        pos = wx.GetMousePosition()
        #pos = event.GetPosition()
        
        
        
        #pos = self.panel.ScreenToClient(pos)

    def CreatePopupMenu(self):
        toolsMENU = wx.Menu()
        ConnectionStatus = self.model.connected.get()
        if ConnectionStatus:
            create_menu_item(toolsMENU, 'Play', self.onScPlay)
            create_menu_item(toolsMENU, 'Pause', self.onScPause)
            create_menu_item(toolsMENU, 'Next', self.onScNext)
            create_menu_item(toolsMENU, 'Previous', self.onScPrevious)
            create_menu_item(toolsMENU, 'Rnd', self.onScRandom)
            toolsMENU.AppendSeparator()
        playersLen = len(self.model.Players)
        #print "Players=\n%s\n%s" % (self.model.Players,self.model.playerList)
        if playersLen >1:
            playersMENU = wx.Menu()
            toolsMENU.AppendMenu(-1, "Change Player", playersMENU) 
            player = self.GetSqueezeServerPlayer()
            if player != None:
                MenuItem = wx.MenuItem(playersMENU, -1, player)
                # Bind event to self.ChangePlayer but add the parameter "player" to the call back, with the value "player"
                playersMENU.Bind(wx.EVT_MENU, functools.partial(self.ChangePlayer,player = player), id=MenuItem.GetId())
                playersMENU.AppendItem(MenuItem)
                playersMENU.AppendSeparator()
            for playerName in  self.model.Players:
                if playerName != player:
                    MenuItem = wx.MenuItem(playersMENU, -1, playerName)
                    playersMENU.Bind(wx.EVT_MENU, functools.partial(self.ChangePlayer,player = playerName), id=MenuItem.GetId())
                    playersMENU.AppendItem(MenuItem)
                    
            toolsMENU.AppendSeparator()
        create_menu_item(toolsMENU, 'Settings', self.on_settings)
        toolsMENU.AppendSeparator()
        create_menu_item(toolsMENU, 'Exit', self.on_exit)
        return toolsMENU
    def set_icon(self, path):
        self.icon = wx.IconFromBitmap(wx.Bitmap(path))
        CurrentToolTip = TRAY_TOOLTIP
        if hasattr(self,'ToolTipText'):
            CurrentToolTip = self.ToolTipText
        self.SetIcon(self.icon, CurrentToolTip)
    def set_toolTip(self, tooltip):
        if hasattr(self,'ToolTipText'):
            if self.ToolTipText == tooltip:
                return
        if hasattr(self,'icon'):
            self.SetIcon(self.icon, tooltip)
        self.ToolTipText = unicode(tooltip)
    def on_move(self, event):
        #print 'on_move'
        pass
        
        #print self.ScreenToClient(wx.GetMousePosition())
    def on_left_up(self, event):
        print 'on_left_up' , self.GetSqueezeServerPlayer()
        player = self.GetSqueezeServerPlayer()
        if player != None:
            self.app.squeezeConCtrl.RecPlayerStatus(player)
        else:
            self.on_settings(event)
    def on_right_down(self, event):
        #print 'on_right_down'
        pass
    def on_right_up(self, event):
        #print 'on_right_up'
        menu = self.CreatePopupMenu()
        #print dir (menu)
    def on_right_dclick(self, event):
        #print 'on_right_dclick'
        self.frame.PopupMenu( menu, event.GetPoint() )
    def on_click(self, event):
        #print 'on_click'
        pass
    
    def on_left_down(self, event):
        #print 'Tray icon was left-clicked.'
        pass
    def on_left_dclick(self, event):
        #print 'Tray icon was on_left_dclick-clicked.'
        self.set_icon('gnomedecor1.png')
        self.OnShowPopup( event)
    def on_hello(self, event):
        print 'Hello, world!'
    def on_exit(self, event):
        #self.on_settings_close(event)
        #wx.CallAfter(self.Destroy)
        self.app.Exit()
    def onScPlay(self, event):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            self.app.squeezeConCtrl.Play(player)
        else:
            self.on_settings(event)
    
    def onScPause(self, event):
        player = self.GetSqueezeServerPlayer()
        #print "player",player
        if player != None:
            self.app.squeezeConCtrl.Pause(player)
        else:
            self.on_settings(event)
    def onScNext(self, event):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            #self.squeezecmd.squeezecmd_Index(player,1)
            
            self.app.squeezeConCtrl.Index(player,1)
        else:
            self.on_settings(event)
    def onScPrevious(self, event):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            #self.squeezecmd.squeezecmd_Index(player,-1)
            self.app.squeezeConCtrl.Index(player,-1)
        else:
            self.on_settings(event)
    def onScRandom(self, event):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            #self.squeezecmd.squeezecmd_randomplay(player)
            self.app.squeezeConCtrl.PlayRandomSong(player)
        else:
            self.on_settings(event)


    def on_settings(self, event):
        self.FrmCtrl.showSettings()
        
    def ChangePlayer(self, event,player):
        oldPlayer = self.model.GuiPlayer.get()
        if oldPlayer != player:
            self.model.GuiPlayer.set(player)
        self.UpdateToolTip()
