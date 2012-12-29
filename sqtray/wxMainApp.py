import wx
from sqtray.models import Observable, squeezeConMdle, squeezePlayerMdl
from sqtray.JrpcServer import squeezeConCtrl
from sqtray.wxTrayIconPopUpMenu import CreatePopupMenu,PopUpMenuInteractor, PopupMenuPresentor

from wxEvents import EVT_RESULT_CONNECTED_ID
from wxEvents import EVT_RESULT_PLAYERS_ID
from wxEvents import EVT_RESULT_CURRENT_TRACK_ID
from wxEvents import EVT_RESULT_CONNECTION_ID
from sqtray.wxEvents import ResultEvent2
import datetime

from sqtray.wxTaskBarIcon import TaskBarIcon, TaskBarIconInteractor,TaskBarIconPresentor
from sqtray.wxFrmSettings import FrmSettings

from sqtray.wxArtPicker import MyArtProvider
import logging

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
        self.log = logging.getLogger("FrmCtrl")
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
            IconName = "ART_APPLICATION_STATUS_DISCONECTED"
            self.Example.set_icon(IconName,(16,16))
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
        #print param
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
        
    def setIcon(self,IconName):
        self.log.debug("setIcon=%s"% (IconName))
        #self.View.set_icon("ART_APPLICATION_STATUS_CONNECTED",(16,16))
        testIcon = wx.ArtProvider.GetIcon(IconName,"FrmCtrl" ,(16,16))
        if not testIcon.Ok():
            self.log.debug("Icon not OK")
            return
        self.tb.SetIcon(testIcon)    

class myapp(wx.App):
    def __init__(self):
        super(myapp, self).__init__()
        
        self.log = logging.getLogger("myapp")
        # Used to decide the connection string
        self.iconFacts = set([])
        # Setup global art provider
        
        self.ApplicationIconName = Observable(None)
        self.ApplicationIconName.addCallback(self.OnApplicationIconNameChange)
        
        self.model = squeezeConMdle()
        self.model.GuiPlayer = Observable(None)
        self.model.GuiPlayerDefault = Observable(None)
        self.model.connected.addCallback(self.OnConection)
        self.SqueezeServerPort = Observable(9000)
        self.SqueezeServerPort.addCallback(self.OnSqueezeServerPort)
        self.cfg = wx.FileConfig(appName="ApplicationName", 
                                    vendorName="VendorName", 
                                    localFilename=".squeezetray.cfg", 
                                    style=wx.CONFIG_USE_LOCAL_FILE)
        self.squeezeConCtrl = squeezeConCtrl(self.model)
        
        
        
        # Now we can set up forms using the art provider     
        self.frmCtrl = FrmCtrl(self.model )
        self.frmCtrl.setApp(self)
        self.frmCtrl.setCfg(self.cfg)
        self.tb = self.frmCtrl.tb
        
        #print "tb=%s" %self.tb
        self.tb.cfg = self.cfg
        self.model.GuiPlayer.addCallback(self.frmCtrl.handleConnectionStrChange)
        
        self.model.GuiPlayer.addCallback(self.OnGuiPlayer)
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



        self.interactor = TaskBarIconInteractor()
        self.tbPresentor =  TaskBarIconPresentor(self.model,self.tb,self.interactor)
        self.tbPresentor.squeezeConCtrl = self.squeezeConCtrl
        self.tbPresentor.cbAddOnSettings(self.on_settings)
        # Next tick will update the UpdateApplicationIconName
        self.UpdateApplicationIconNameRequestFlag = True
    
        
    def UpdateApplicationIconNameRequest(self):
        
        self.UpdateApplicationIconNameRequestFlag = True
        
    def UpdateApplicationIconName(self):
        if not "conected" in self.iconFacts:
            #self.View.set_icon("ART_APPLICATION_STATUS_DISCONECTED",(16,16))
            #self.View.set_icon("ART_APPLICATION_STATUS_CONNECTED",(16,16))
            self.ApplicationIconName.update("ART_APPLICATION_STATUS_DISCONECTED")
            return
        if "players" in self.iconFacts:
            self.ApplicationIconName.update("ART_APPLICATION_STATUS_CONNECTED")
            return
        
    def OnTimer(self,event):
        self.tbPresentor.UpdateToolTip()
        if self.UpdateApplicationIconNameRequestFlag:
            self.UpdateApplicationIconNameRequestFlag = False
            self.UpdateApplicationIconName()
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
    
    def OnApplicationIconNameChange(self, mstuff):
        NewName = self.ApplicationIconName.get()
        if NewName == None:
            return
        self.tbPresentor.setIcon(NewName)
        if self.frmCtrl.Example != None:
            self.frmCtrl.Example.set_icon(NewName,(16,16))
        
    def OnConection(self,stuff):
        print "OnConection=%s"  % (stuff)
        isConnected = self.model.connected.get()
        OldLenIf = len(self.iconFacts)
        if isConnected:
            self.iconFacts.add("conected")
        else:
            if "conected" in self.iconFacts:
                self.iconFacts.remove("conected")
        NewLenIf = len(self.iconFacts)
        if OldLenIf != NewLenIf:
            self.UpdateApplicationIconNameRequest()
            self.log.debug("Updated Icon")
            self.log.debug("self.iconFact=%s" % (self.iconFacts))

    def OnPlayerAvailable(self):
        # If Not connected set None
        if not self.model.connected:
            if None != self.model.GuiPlayer.get():
                self.model.GuiPlayer.set(None)
            return
        # If no players Available:
        AvailableArray = self.model.Players.keys()
        AvailableArrayLen = len(AvailableArray)
        OldLenIf = len(self.iconFacts)
        if AvailableArrayLen == 0:
            if  "players" in self.iconFacts:
                self.iconFacts.remove("players")
        else:
            self.iconFacts.add("players")
        NewLenIf = len(self.iconFacts)
        if OldLenIf != NewLenIf:
            self.UpdateApplicationIconNameRequest()
            self.log.debug("Updated Icon")
            self.log.debug("self.iconFact=%s" % (self.iconFacts))
        
        if AvailableArrayLen == 0:
            if None != self.model.GuiPlayer.get():
                self.model.GuiPlayer.set(None)
            if  "players" in self.iconFacts:
                self.iconFacts.remove("players")
            return
        self.iconFacts.add("players")
        # Try to Apply Current Player
        
        # If the GuiPlayer is still set to right thing
        GuiPlayer = self.model.GuiPlayer.get()
        if GuiPlayer in AvailableArray:
            
            return
        # Try to Apply Default Player
        
        DefaultPlayer = self.model.GuiPlayerDefault.get()
        if DefaultPlayer in AvailableArray:
            OldDefaultPlayer = self.model.GuiPlayer.get()
            if OldDefaultPlayer != DefaultPlayer:
                self.model.GuiPlayer.set(DefaultPlayer)
                
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
        
    def configSave(self):
        #print 'saving'
        self.cfg.Write("squeezeServerHost", self.model.host.get())
        self.cfg.WriteInt("squeezeServerPort", self.model.port.get())
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
    
        

        
        #print self.ScreenToClient(wx.GetMousePosition())

    def on_hello(self, event):
        print 'Hello, world!'

    def on_settings(self):
        
        self.frmCtrl.showSettings()
        self.OnApplicationIconNameChange(None)
        
    def OnGuiPlayer(self,player):
        
        self.tbPresentor.currentPlayer.set(self.model.GuiPlayer.get())
        
    
