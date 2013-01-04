import wx
from sqtray.models import Observable
#, squeezeConMdle, squeezePlayerMdl
from sqtray.modelsConnection import squeezeConMdle, squeezePlayerMdl
from sqtray.modelsWxTaskbar import taskBarMdle


from sqtray.JrpcServer import squeezeConCtrl
from sqtray.wxTrayIconPopUpMenu import CreatePopupMenu,PopUpMenuInteractor, PopupMenuPresentor

from wxEvents import EVT_RESULT_CONNECTED_ID
from wxEvents import EVT_RESULT_PLAYERS_ID
from wxEvents import EVT_RESULT_CURRENT_TRACK_ID
from wxEvents import EVT_RESULT_CONNECTION_ID
from sqtray.wxEvents import ResultEvent2
import datetime

from sqtray.wxTaskBarIcon import TaskBarIcon, TaskBarIconInteractor, timedelta2str
from sqtray.wxTaskBarIconPresentor import TaskBarIconPresentor
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
        self.log.debug("CreatePopUp=%s" % (param))
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


import  wx
import  wx.lib.newevent

SomeNewEvent, EVT_SOME_NEW_EVENT = wx.lib.newevent.NewEvent()
SomeNewCommandEvent, EVT_SOME_NEW_COMMAND_EVENT = wx.lib.newevent.NewCommandEvent()
           

class interactorWxUpdate():
    def install(self, src, wxObject):
        self.src = src
        self.wxObject = wxObject 
        self.wxObject.Bind(EVT_SOME_NEW_EVENT, self.wxObject.EventRevived)
        self.src.connected.addCallback(self.on_connected)
        self.src.CbPlayersAvailableAdd(self.on_players)
        #self.wxObject.setUpdateModel(self.updateWx)
         
        
    def on_connected(self,value):
        #print self.src.connected
        #print dir(self.wxObject)
        #create the event
        evt = SomeNewEvent(attr1="on_connected")
        #post the event
        wx.PostEvent(self.wxObject, evt)
    
    def on_players(self):
        evt = SomeNewEvent(attr1="on_players")
        #post the event
        wx.PostEvent(self.wxObject, evt)

        #newIconName = "ART_APPLICATION_STATUS_CONNECTED"
        #self.wxObject.setIcon.update(newIconName)
        


class viewWxToolBarSrc():
    def __init__(self):
        self.updateNeeded = True
        self.toolTipCache = Observable(None)
        self.iconNameCache = Observable(None)
        self.knowledge = {}
        self.log = logging.getLogger("viewWxToolBarSrc")
    def install(self, src):        
        self.src = src
        self.src.connected.addCallback(self.on_connected)
        self.src.CbPlayersAvailableAdd(self.on_players)
    
    
    def updateToolTipManyPlayers(self):
        newToolTip = unicode()
        for index in  range(len(self.src.playerList)):
            playerName = self.src.playerList[index].name.get()
            if playerName == None:
                continue
            newToolTip += unicode(playerName)
            
            CurrentOperationMode = self.src.playerList[index].operationMode.get()
            if CurrentOperationMode != None:
                newToolTip += ":%s" % (CurrentOperationMode)
            CurrentTrackTitle = self.src.playerList[index].CurrentTrackTitle.get()
            if CurrentTrackTitle != None:
                newToolTip += "\nTrack:%s" % (CurrentTrackTitle)
            CurrentTrackArtist = self.src.playerList[index].CurrentTrackArtist.get()
            if CurrentTrackArtist != None:
                newToolTip += "\nArtist:%s" % (CurrentTrackArtist)
            CurrentTrackEnds = self.src.playerList[index].CurrentTrackEnds.get()
            #print "CurrentTrackEnds=%s" % (CurrentTrackEnds)
            if CurrentTrackEnds != None:
                seconds = timedelta2str(CurrentTrackEnds - datetime.datetime.now())
                newToolTip += "\nRemaining:%s" % (seconds)
            newToolTip += '\n'
        #print newToolTip
        #self.log.warn("ffoo%sooff" % ( newToolTip.strip())            )
        self.toolTipCache.update(newToolTip)
        #self.log.warn("xxx%sxxx" % (self.toolTipCache.get() ) )
        return self.toolTipCache.get()
    def updateToolTip(self):
        self.log.debug("updateToolTip")
        newToolTip = unicode()
        playerlistLen = len(self.src.playerList)
        #print "playerlistLen" , playerlistLen
        if playerlistLen > 0:
            return self.updateToolTipManyPlayers()
        #print "dfsfsdf" ,  self.src.playerList
            
        if self.src.connected:
            self.toolTipCache.update("Connected")
    
        return self.toolTipCache.get()
    
    def update(self):
        
        if not self.updateNeeded:
            pass
            #return
        else:
            self.updateNeeded = False
        self.updateToolTip()
        connected = self.src.connected.get()
        #print "connected", self.toolTipCache.get()
        self.knowledge['connected'] = connected
        if self.knowledge['connected'] == True:
            self.iconNameCache.update("ART_APPLICATION_STATUS_CONNECTED")
            
    def on_connected(self,value):
        self.updateNeeded = True
        
        
        if value != True:
            self.iconNameCache.update("ART_APPLICATION_STATUS_DISCONECTED")
        
    def on_players(self):
        self.updateNeeded = True
        
    
    
    def gettoolTip(self):
        self.update()
        return self.toolTipCache.get()
    
    
    def getIconName(self):
        self.update()
        return self.iconNameCache.get()
        
    
    
class mainApp(wx.App):
    def __init__(self):
        super(mainApp, self).__init__()
        self.log = logging.getLogger("mainApp")
        # Used to decide the connection string  
        self.ModelConPool = squeezeConMdle()
        self.ModelGuiThread = taskBarMdle()
        
        #self.tb = TaskBarPresntor(self.ModelGuiThread)
        self.cfg = wx.FileConfig(appName="ApplicationName", 
                                    vendorName="VendorName", 
                                    localFilename=".squeezetray.cfg", 
                                    style=wx.CONFIG_USE_LOCAL_FILE)
        # Now we can set up forms using the art provider     
        self.tb = TaskBarIcon(self.ModelGuiThread)
        self.tb.Bind(wx.EVT_CLOSE, self.Exit)
        
        TIMER_ID = wx.NewId()  # pick a number
        
        self.CUSTOM_ID = wx.NewId()
        
        self.timer = wx.Timer(self, TIMER_ID)  # message will be sent to the panel
        
        
        
        
        self.timer.Start(900)  # x100 milliseconds
        wx.EVT_TIMER(self, TIMER_ID, self.OnTimer)  # call the on_timer function
        self.taskbarInteractor = TaskBarIconInteractor()
        self.tbPresentor =  TaskBarIconPresentor(self.ModelGuiThread,self.tb,self.taskbarInteractor)
        self.tbPresentor.cbAddReqMdlUpdate(self.setUpdateModel)
        self.tbPresentor.cbAddRequestPopUpMenu(self.CreatePopUp)
        
        
        self.interactorWxUpdate = interactorWxUpdate()
        self.interactorWxUpdate.install(self.ModelConPool,self)
        
        # Now we hook up the view
        self.squeezeConCtrl = squeezeConCtrl(self.ModelConPool)
        self.squeezeConCtrl.ConectionStringSet("mini:9000")
        self.count = 0
        self.viewWxToolBarSrc = viewWxToolBarSrc()
        self.viewWxToolBarSrc.install(self.ModelConPool)
    def onTaskBarPopUpMenu(self,evt):
        self.log.debug("onTaskBarPopUpMenu=%s",(None))
        self.CreatePopUp()

    def EventRevived(self,evt):
        self.log.debug("EventRevived=%s",(evt.attr1 ))
        if evt.attr1 == "on_connected":
            #self.ModelGuiThread.connected.update(self.ModelConPool.connected.get())
            pass
        if evt.attr1 == "on_players":
            pass
            #print self.ModelConPool.Players
        self.setUpdateModel(evt)
            
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
        
    def OnTimer(self,event):
        #self.log.debug("on timer")
        #self.log.debug("on timer= %s" % (self.viewWxToolBarSrc.gettoolTip()))
        #self.timer.
        #print dir(self.timer)
        #self.interactorWxUpdate.on_connected()
        if self.count > 100:
            self.Exit()
        self.count += 1
    def on_event(self,event):
        self.log.debug("on_event")
        
    def Exit(self):
        self.squeezeConCtrl.view1.wait_completion()
        self.tb.Destroy()
    def CreatePopUp(self):
        self.log.debug("CreatePopUpp")
        
        interactor = PopUpMenuInteractor ()
        newMenu = CreatePopupMenu(self.ModelConPool,interactor)
        #print newMenu
        self.PopupMenu  = PopupMenuPresentor(self.ModelConPool,newMenu, self.squeezeConCtrl, interactor)
        self.PopupMenu.cbAddOnExit(self.Exit)
        self.PopupMenu.cbAddOnSettings(self.SettingsOpen)
        
        #self.PopupMenu.player.set(self.Model.GuiPlayer.get())
        #self.PopupMenu.AddCallbackSettings(self.on_settings)
        #self.PopupMenu.player.addCallback(self.playerChanged1)
        return newMenu
    def setUpdateModel(self,param):
        connected = self.ModelConPool.connected.get()
        if connected == False:
            self.ModelGuiThread.currentIconName.update("ART_APPLICATION_STATUS_DISCONECTED")
            return
        if connected == True:
            self.ModelGuiThread.currentIconName.update("ART_APPLICATION_STATUS_CONNECTED")
        #if connected:
        #    self.ModelGuiThread.currentIconName.update("ART_APPLICATION_STATUS_CONNECTED")
        #    return
        toolTip = self.viewWxToolBarSrc.gettoolTip()
        #self.ModelGuiThread.set_toolTip(toolTip)
        self.tbPresentor._OnToolTipChange(toolTip)
        currentIcon = self.viewWxToolBarSrc.getIconName()
        self.log.debug("setUpdateModel")
        
        
        self.log.debug("setUpdateModel=%s" % (connected))
    def SettingsOpen(self):
        self.Example = FrmSettings(None, title='Settings')
        self.Example.Bind(wx.EVT_CLOSE, self.SettingClose)
        self.Example.ModelSet(self.ModelConPool)
        self.Example.Show()
    def SettingClose(self,evnt):
        self.Example.Destroy()
        self.Example = None
