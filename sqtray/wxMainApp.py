import wx
from sqtray.models import Observable, squeezeConMdle, squeezePlayerMdl
from sqtray.JrpcServer import squeezeConCtrl


from wxEvents import EVT_RESULT_CONNECTED_ID
from wxEvents import EVT_RESULT_PLAYERS_ID
from wxEvents import EVT_RESULT_CURRENT_TRACK_ID
from wxEvents import EVT_RESULT_CONNECTION_ID
from sqtray.wxEvents import ResultEvent2


from sqtray.wxTaskBarIcon import TaskBarIcon
from sqtray.wxFrmSettings import FrmSettings


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


    def handleConnectionStrChange(self,value):
        if (self.Example != None):
            wx.PostEvent(self.Example, ResultEvent2(EVT_RESULT_CONNECTION_ID,value))
            
    def handleConnectionChange(self,value, window):
        wx.PostEvent(self.tb, ResultEvent2(EVT_RESULT_CONNECTED_ID,value))
        if (self.Example != None):
            wx.PostEvent(self.Example, ResultEvent2(EVT_RESULT_PLAYERS_ID,value))
    
    def handlePlayersChange(self,value,window = None,asda= None):
        wx.PostEvent(self.tb, ResultEvent2(EVT_RESULT_PLAYERS_ID,value))
        if (self.Example != None):
            wx.PostEvent(self.Example, ResultEvent2(EVT_RESULT_PLAYERS_ID,value))
        
    def handleTrackChange(self,value,other):
        wx.PostEvent(self.tb, ResultEvent2(EVT_RESULT_CURRENT_TRACK_ID,value))

class myapp(wx.App):
    def __init__(self):
        super(myapp, self).__init__()
        
        self.model = squeezeConMdle()
        self.model.GuiPlayer = Observable(None)
        self.model.GuiPlayerDefault = Observable(None)
        self.model.CbPlayersAvailableAdd(self.OnPlayerAvailable)
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
        self.squeezeConCtrl.CbConnectionAdd(self.frmCtrl.handleConnectionChange,None)
        self.model.CbPlayersAvailableAdd(self.frmCtrl.handlePlayersChange,None)
        self.model.CbPlayersAvailableAdd(self.OnPlayers)
        self.model.CbChurrentTrackAdd(self.frmCtrl.handleTrackChange,None)
        self.model.connectionStr.addCallback(self.frmCtrl.handlePlayersChange)
        self.configRead()
    def OnPlayers(self,connected,playerlist):
        # If Not connected set None
        if not connected:
            if None != self.model.GuiPlayer.get():
                self.model.GuiPlayer.set(None)
            return
        # Try to Apply Default Player
        DefaultPlayer = self.model.GuiPlayerDefault.get()
        if DefaultPlayer in playerlist:
            OldDefaultPlayer = self.model.GuiPlayer.get()
            if OldDefaultPlayer != DefaultPlayer:
                self.model.GuiPlayer.set(DefaultPlayer)
            return
        # Try to find any player
        for index in range(len(self.model.playerList)):
            Name = self.model.playerList[index].name.get()
            if Name != None:
                self.model.GuiPlayer.set(unicode(Name))
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
        print 'saving'
        self.cfg.Write("squeezeServerHost", self.model.host.get())
        self.cfg.WriteInt("squeezeServerPort", self.model.port.get())
        SqueezeServerPlayer = self.GetSqueezeServerPlayer()
        self.cfg.Write("SqueezeServerPlayer", self.model.GuiPlayerDefault.get())
        self.cfg.Flush()
        
    def OnPlayerAvailable(self,AvailablePlayers,extra):
        print "AvailablePlayers",AvailablePlayers,extra
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
    
        
    
