import wx
from sqtray.models import Observable, squeezeConMdle, squeezePlayerMdl
from sqtray.JrpcServer import squeezeConCtrl
from sqtray.wxTrayIconPopUpMenu import CreatePopupMenu

from wxEvents import EVT_RESULT_CONNECTED_ID
from wxEvents import EVT_RESULT_PLAYERS_ID
from wxEvents import EVT_RESULT_CURRENT_TRACK_ID
from wxEvents import EVT_RESULT_CONNECTION_ID
from sqtray.wxEvents import ResultEvent2
import datetime

from sqtray.wxTaskBarIcon import TaskBarIcon
from sqtray.wxFrmSettings import FrmSettings

def StoreConfig(FilePath,squeezeConMdle):
    cfg = wx.FileConfig(appName="ApplicationName", 
                                vendorName="VendorName", 
                                localFilename=FilePath, 
                                style=wx.CONFIG_USE_LOCAL_FILE)
    cfg.Write("squeezeServerHost", squeezeConMdle.host.get())

    cfg.WriteInt("squeezeServerPort", squeezeConMdle.port.get())
    cfg.Flush()


class FrmCtrl:
    def  __init__(self,model):
        self.model = model
        self.tb = TaskBarIcon(model)
        self.tb.FrmCtrl = self
        self.tb.Bind(wx.EVT_CLOSE, self.Exit)
        self.Example = None
    def setApp(self,app):
        self.app = app
        self.tb.app = app
    def setCfg(self,cfg):
        self.cfg = cfg
    def showSettings(self):
        if (self.Example == None):
            self.Example = FrmSettings(None, title='Settings')
            self.Example.Bind(wx.EVT_CLOSE, self.closeSettings)
            self.Example.FrmCtrl = self
            self.Example.cfg = self.cfg
            self.Example.app = self.app
            self.Example.ModelSet(self.model)
            self.Example.Show()
    def closeSettings(self,wxExvent):
        if (self.Example != None):
            self.Example.Destroy()
            self.Example = None    
    def Exit(self):
        self.closeSettings(None)
        self.tb.Destroy()

    def CreatePopUp(self,param):
        ################################################################
        print param
        CreatePopupMenu()
    def handleConnectionStrChange(self,value):
        if (self.Example != None):
            wx.PostEvent(self.Example, ResultEvent2(EVT_RESULT_CONNECTION_ID,value))
            
    def handleConnectionChange(self,value):
        wx.PostEvent(self.tb, ResultEvent2(EVT_RESULT_CONNECTED_ID,value))
        if (self.Example != None):
            wx.PostEvent(self.Example, ResultEvent2(EVT_RESULT_CONNECTED_ID,value))
    
    def handlePlayersChange(self,value):
        wx.PostEvent(self.tb, ResultEvent2(EVT_RESULT_PLAYERS_ID,None))
        if (self.Example != None):
            wx.PostEvent(self.Example, ResultEvent2(EVT_RESULT_PLAYERS_ID,None))
        
    def handleCurrentTrackChange(self):
        wx.PostEvent(self.tb, ResultEvent2(EVT_RESULT_CURRENT_TRACK_ID,None))

class myapp(wx.App):
    def __init__(self):
        super(myapp, self).__init__()
        
        self.model = squeezeConMdle()
        self.model.GuiPlayer = Observable(None)
        self.model.GuiPlayerDefault = Observable(None)
        
        self.SqueezeServerPort = Observable(9000)
        self.SqueezeServerPort.addCallback(self.OnSqueezeServerPort)
        self.cfg = wx.FileConfig(appName="ApplicationName", 
                                    vendorName="VendorName", 
                                    localFilename=".squeezetray.cfg", 
                                    style=wx.CONFIG_USE_LOCAL_FILE)
        self.squeezeConCtrl = squeezeConCtrl(self.model)
             
        self.frmCtrl = FrmCtrl(self.model )
        self.frmCtrl.setApp(self)
        self.frmCtrl.setCfg(self.cfg)
        self.tb = self.frmCtrl.tb
        
        #print "tb=%s" %self.tb
        self.tb.cfg = self.cfg
        self.model.GuiPlayer.addCallback(self.frmCtrl.handleConnectionStrChange)
        self.squeezeConCtrl.CbConnectionAdd(self.frmCtrl.handleConnectionChange)
        
        self.model.CbPlayersAvailableAdd(self.frmCtrl.handlePlayersChange,None)

        self.model.CbPlayersAvailableAdd(self.OnPlayerAvailable)
        
        self.model.CbChurrentTrackAdd(self.frmCtrl.handleCurrentTrackChange)
        self.model.connectionStr.addCallback(self.frmCtrl.handlePlayersChange)
        self.model.SocketErrNo.addCallback(self.frmCtrl.handlePlayersChange)
        self.configRead()
        TIMER_ID = wx.NewId()  # pick a number
        self.timer = wx.Timer(self, TIMER_ID)  # message will be sent to the panel
        self.timer.Start(9000)  # x100 milliseconds
        wx.EVT_TIMER(self, TIMER_ID, self.OnTimer)  # call the on_timer function
        self.BindApp()
        
    def BindApp(self):
        self.frmCtrl.tb.Bind(wx.EVT_TASKBAR_MOVE, self.on_move)
        self.frmCtrl.tb.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.frmCtrl.tb.Bind(wx.EVT_TASKBAR_LEFT_UP, self.on_left_up )
        #self.frmCtrl.tb.Bind(wx.EVT_TASKBAR_RIGHT_DOWN, self.on_right_down )
        #self.frmCtrl.tb.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.on_right_up )
        self.frmCtrl.tb.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.on_left_dclick)
        self.frmCtrl.tb.Bind(wx.EVT_TASKBAR_RIGHT_DCLICK, self.on_right_dclick)
        
        #self.Bind(wx.EVT_TASKBAR_CLICK, self.frmCtrl.tb.on_click )
        
        
        self.frmCtrl.tb.Connect(-1, -1, EVT_RESULT_PLAYERS_ID, self.OnPlayers)
        self.frmCtrl.tb.Connect(-1, -1, EVT_RESULT_CURRENT_TRACK_ID, self.OnTrack)
        
        
        self.frmCtrl.tb.CbAddCreatePopupMenu(self.CreatePopupMenu)
    def OnTimer(self,event):
        self.UpdateToolTip()
        ConnectionStatus = self.model.connected.get()
        if not ConnectionStatus:
            #print "not on line"
            self.squeezeConCtrl.RecConnectionOnline()
            return
        player = self.model.GuiPlayer.get()
        #print "on_timer.player",player
        if player != None:
            self.squeezeConCtrl.PlayerStatus(player)
            return
        self.squeezeConCtrl.RecConnectionOnline()
    
    
    def CreatePopupMenu(self,context):
        #print "asdasddddddddddddddddddddddads"
        return CreatePopupMenu(self.model,self)
        
    def OnPlayerAvailable(self):
        # If Not connected set None
        if not self.model.connected:
            if None != self.model.GuiPlayer.get():
                self.model.GuiPlayer.set(None)
            return
        # If no players Available:
        AvailableArray = self.model.Players.keys()
        if len(AvailableArray) == 0:
            if None != self.model.GuiPlayer.get():
                self.model.GuiPlayer.set(None)
            return
        # Try to Apply Default Player
        DefaultPlayer = self.model.GuiPlayerDefault.get()
        if DefaultPlayer in AvailableArray:
            OldDefaultPlayer = self.model.GuiPlayer.get()
            if OldDefaultPlayer != DefaultPlayer:
                self.model.GuiPlayer.set(DefaultPlayer)
            return
        # If the GuiPlayer is still set to right thing
        GuiPlayer = self.model.GuiPlayer.get()
        if GuiPlayer in AvailableArray:
            return
        # Try to find any player
        for PlayerName in self.model.Players:
            self.model.GuiPlayer.set(unicode(PlayerName))
            return
            
    def configRead(self):
        # Set Host
        squeezeServerHost = 'localhost'
        if self.cfg.Exists('squeezeServerHost'):
            squeezeServerHost = self.cfg.Read('squeezeServerHost')
        OldSqueezeServerHost = self.model.host.get()
        if squeezeServerHost != OldSqueezeServerHost:
            self.model.host.set(squeezeServerHost)
        self.SetSqueezeServerHost(squeezeServerHost)
        # Set Port
        squeezeServerPort = 9000
        if self.cfg.Exists('squeezeServerPort'):
            try:
                squeezeServerPortTmp = int(self.cfg.ReadInt('squeezeServerPort'))
            except ValueError:
                squeezeServerPort = 9000
        OldSqueezeServerPort = self.SqueezeServerPort.get()
        if squeezeServerPort != OldSqueezeServerPort:
            self.SqueezeServerPort.set(squeezeServerPort)
        OldSqueezeServerPort = self.model.port.get()
        if squeezeServerPort != OldSqueezeServerPort:
            self.model.port.set(squeezeServerPort)
        
        # Set Player
        SqueezeServerPlayer = None
        if self.cfg.Exists('SqueezeServerPlayer'):
            SqueezeServerPlayer = self.cfg.Read('SqueezeServerPlayer')
        self.SetSqueezeServerPlayer(SqueezeServerPlayer)
        self.model.GuiPlayerDefault.set(SqueezeServerPlayer)
        self.squeezeConCtrl.RecConnectionOnline()
        #print "self.model.GuiPlayerDefault", self.model.GuiPlayerDefault.get()
    def configSave(self):
        #print 'saving'
        self.cfg.Write("squeezeServerHost", self.model.host.get())
        self.cfg.WriteInt("squeezeServerPort", self.model.port.get())
        SqueezeServerPlayer = self.GetSqueezeServerPlayer()
        self.cfg.Write("SqueezeServerPlayer", self.model.GuiPlayerDefault.get())
        self.cfg.Flush()

    def SetSqueezeServerHost(self,host):
        OldHost = self.model.host.get()
        if OldHost != host:
            self.model.host.set(host)
            #print "set" ,self.model.host.get()
            self.squeezeConCtrl.RecConnectionOnline()
            
        
    def GetSqueezeServerHost(self):
        if hasattr(self,'SqueezeServerHost'):
            return self.SqueezeServerHost
        return 'localhost'
        
    def OnSqueezeServerPort(self,value):
        self.squeezeConCtrl.ServerPortSet(self.SqueezeServerPort.get())
        self.squeezeConCtrl.RecConnectionOnline()

    def GetSqueezeServerPort(self):
        if hasattr(self,'SqueezeServerHost'):
            return self.SqueezeServerPort.get()
        return 9000
    def SetSqueezeServerPlayer(self,player):
        self.SqueezeServerPlayer = player
        #print "player=%s" % player
        self.squeezeConCtrl.RecPlayerStatus(player)
        
    def GetSqueezeServerPlayer(self):        
        if hasattr(self,'SqueezeServerPlayer'):
            return self.SqueezeServerPlayer
        if self.model.playersCount.get() > 0:
            return unicode(self.model.playerList[0].name.get())
        return None
    
        
    def on_move(self, event):
        #print 'on_move'
        pass
        
        #print self.ScreenToClient(wx.GetMousePosition())
    def on_left_up(self, event):
        print 'on_left_up' , self.GetSqueezeServerPlayer()
        player = self.GetSqueezeServerPlayer()
        if player != None:
            self.squeezeConCtrl.RecPlayerStatus(player)
        else:
            self.on_settings(event)
    def on_right_down(self, event):
        #print 'on_right_down'
        pass
    def on_right_up(self, event):
        print 'on_right_up'
        #menu = self.CreatePopupMenu()
        #print dir (menu)
    def on_right_dclick(self, event):
        print 'on_right_dclick'
        self.CreatePopUp(  event.GetPoint() )
    def on_click(self, event):
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
        self.Exit()
    def onScPlay(self, event):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            self.squeezeConCtrl.Play(player)
        else:
            self.on_settings(event)
    
    def onScPause(self, event):
        player = self.GetSqueezeServerPlayer()
        #print "player",player
        if player != None:
            self.squeezeConCtrl.Pause(player)
        else:
            self.on_settings(event)
    def onScNext(self, event):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            #self.squeezecmd.squeezecmd_Index(player,1)
            
            self.squeezeConCtrl.Index(player,1)
        else:
            self.on_settings(event)
    def onScPrevious(self, event):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            #self.squeezecmd.squeezecmd_Index(player,-1)
            self.squeezeConCtrl.Index(player,-1)
        else:
            self.on_settings(event)
    def onScRandom(self, event):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            #self.squeezecmd.squeezecmd_randomplay(player)
            self.squeezeConCtrl.PlayRandomSong(player)
        else:
            self.on_settings(event)


    def on_settings(self, event):
        self.frmCtrl.showSettings()
        
    def ChangePlayer(self, event,player):
        oldPlayer = self.model.GuiPlayer.get()
        if oldPlayer != player:
            self.model.GuiPlayer.set(player)
        self.UpdateToolTip()
    
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
                    self.frmCtrl.tb.set_toolTip(newToolTip)
