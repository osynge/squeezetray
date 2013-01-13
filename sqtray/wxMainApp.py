import wx
from sqtray.models import Observable
#, squeezeConMdle, squeezePlayerMdl
from sqtray.modelsConnection import squeezeConMdle, squeezePlayerMdl
from sqtray.modelsWxTaskbar import taskBarMdle


from sqtray.JrpcServer import squeezeConCtrl
from sqtray.wxTrayIconPopUpMenu import CreatePopupMenu,PopUpMenuInteractor, PopupMenuPresentor, TrayMenuInteractor, TrayMenuPresentor

from wxEvents import EVT_RESULT_CONNECTED_ID
from wxEvents import EVT_RESULT_PLAYERS_ID
from wxEvents import EVT_RESULT_CURRENT_TRACK_ID
from wxEvents import EVT_RESULT_CONNECTION_ID
from sqtray.wxEvents import ResultEvent2
import datetime

from sqtray.wxTaskBarIcon import TaskBarIcon, TaskBarIconInteractor, timedelta2str
from sqtray.wxTaskBarIconPresentor import TaskBarIconPresentor

from sqtray.wxArtPicker import MyArtProvider

from sqtray.wxConfig import ConfigPresentor

from sqtray.jrpcServerPresentor import squeezeConPresentor
from sqtray.wxFrmSettingsPresentor import frmSettingsPresentor
import logging

from modelsWxFrmSettings import mdlFrmSettings


from  modelActions import ConCtrlInteractor

def StoreConfig(FilePath,squeezeConMdle):
    cfg = wx.FileConfig(appName="ApplicationName", 
                                vendorName="VendorName", 
                                localFilename=FilePath, 
                                style=wx.CONFIG_USE_LOCAL_FILE)
    cfg.Write("squeezeServerHost", squeezeConMdle.host.get())

    cfg.WriteInt("squeezeServerPort", squeezeConMdle.port.get())
    cfg.Flush()



import  wx
import  wx.lib.newevent
from jrpcServerThreadPool  import sConTPool


SomeNewEvent, EVT_SOME_NEW_EVENT = wx.lib.newevent.NewEvent()
SomeNewCommandEvent, EVT_SOME_NEW_COMMAND_EVENT = wx.lib.newevent.NewCommandEvent()
           

class interactorWxUpdate():
    def install(self, src, wxObject):
        self.src = src
        self.wxObject = wxObject 
        self.wxObject.Bind(EVT_SOME_NEW_EVENT, self.wxObject.EventRevived)
        self.src.connected.addCallback(self.on_connected)
        self.src.CbPlayersAvailableAdd(self.on_players)
        self.messagesUnblock()
        
    def on_connected(self,value):
        if self.block:
            return
        evt = SomeNewEvent(attr1="on_connected")
        #post the event
        wx.PostEvent(self.wxObject, evt)
    
    def on_players(self):
        if self.block:
            return
        evt = SomeNewEvent(attr1="on_players")
        #post the event
        wx.PostEvent(self.wxObject, evt)
    def messagesBlock(self):
        self.block = True
    def messagesUnblock(self):
        self.block = False
    
        


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
        #self.src.Players.addCallback(self.on_connected)
        self.src.CbPlayersAvailableAdd(self.on_players)
        self.src.playersCount.addCallback(self.on_connected)
    
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
        if playerlistLen > 0:
            return self.updateToolTipManyPlayers()
           
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
        self.log.debug("on_players")
        self.updateNeeded = True
        #self.availablePlayers
        foundPlayers = set()
        for index in  range(len(self.src.playerList)):            
            playerName = self.src.playerList[index].name.get()
            
            self.src.playerList[index].name.addCallback(self.on_player_name)
            self.src.playerList[index].CurrentTrackTitle.addCallback(self.on_player_track)
            self.src.playerList[index].CurrentTrackArtist.addCallback(self.on_player_artist)
            
            
    def on_player_name(self,value):
        self.updateNeeded = True
    def on_player_track(self,value):
        self.log.debug('on_player_track')
        self.updateNeeded = True
    def on_player_artist(self,value):
        self.log.debug( 'on_player_artist')
        self.updateNeeded = True
    def gettoolTip(self):
        self.update()
        return self.toolTipCache.get()
    
    
    def getIconName(self):
        self.update()
        return self.iconNameCache.get()
        
    
class  Connection2SettingsInteractor():
    def install(self, connection, settings):
        self.connection = connection
        self.settings = settings
        self.connection.host.addCallback(self.OnHostChange)
        self.OnHostChange(None)
        self.connection.port.addCallback(self.OnPortChange)
        self.OnPortChange(None)
        self.connection.SocketErrNo.addCallback(self.OnConnectionError)

    def OnHostChange(self,value):
        self.settings.host.update(self.connection.host.get())
    def OnPortChange(self,value):
        self.settings.port.update(self.connection.port.get())
    def OnConnectionError(self,value):
        #self.settings.connectionMsg.update("SocketErrNo=%s" % (self.connection.SocketErrNo.get()))
        pass

           
class mainApp(wx.App):
    def __init__(self):
        super(mainApp, self).__init__()
        self.log = logging.getLogger("mainApp")
        # Used to decide the connection string  
        self.ModelConPool = squeezeConMdle()
        self.ModelGuiThread = taskBarMdle()
        self.ModelFrmSettings = mdlFrmSettings()
        
        
        self.ConCtrlInteractor = ConCtrlInteractor()
        self.ConCtrlInteractor.install(self.ModelFrmSettings,self.ModelConPool)
        
        #Now Load Config
        
        self.configPresentor = ConfigPresentor(self.ModelFrmSettings)
        self.configPresentor.load()
        
        self.ConCtrlInteractor.OnApply(None)
        
        # Now set model interactions
        self.Con2SettingsInteractor = Connection2SettingsInteractor()
        self.Con2SettingsInteractor.install(self.ModelConPool,self.ModelFrmSettings)
        
        
        
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
        
        
        
        
        self.timer.Start(9000)  # x100 milliseconds
        wx.EVT_TIMER(self, TIMER_ID, self.OnTimer)  # call the on_timer function
        self.taskbarInteractor = TaskBarIconInteractor()
        self.tbPresentor =  TaskBarIconPresentor(self.ModelGuiThread,self.tb,self.taskbarInteractor)
        
        self.tbPresentor.cbAddReqMdlUpdate(self.setUpdateModel)
        self.tbPresentor.cbAddRequestPopUpMenu(self.CreatePopUp)
        
        
        self.interactorWxUpdate = interactorWxUpdate()
        self.interactorWxUpdate.install(self.ModelConPool,self)
       
        # Now we hook up the view
        self.squeezeConCtrl = squeezeConCtrl(self.ModelConPool)
        #self.squeezeConCtrl.ConectionStringSet("mini:9000")
        self.count = 0
        self.viewWxToolBarSrc = viewWxToolBarSrc()
        self.viewWxToolBarSrc.install(self.ModelConPool)
        
        
        
        #Now we set up the Tray Pup Up menu
        self.tbPopUpMenuInteractor = TrayMenuInteractor()
        self.tbPopUpMenuPresentor = TrayMenuPresentor(self.ModelConPool,self.tbPopUpMenuInteractor)
        self.tbPopUpMenuInteractor.cbAddOnExit(self.Exit)
        self.tbPopUpMenuInteractor.cbAddOnSettings(self.SettingsOpen)
        
        self.tbPopUpMenuInteractor.cbAddOnPause(self.squeezeConCtrl.Pause)
        self.tbPopUpMenuInteractor.cbAddOnSeekIndex(self.squeezeConCtrl.Index)
        
        self.tbPopUpMenuInteractor.cbAddOnRandomSongs(self.squeezeConCtrl.PlayRandomSong)
        self.tbPopUpMenuInteractor.cbAddOnPlay(self.squeezeConCtrl.Play)
        self.tbPopUpMenuInteractor.cbAddOnStop(self.squeezeConCtrl.Stop)
        
        # Now we set up the jrpc server
        self.connectionPool = sConTPool(self.ModelConPool)
        self.jrpc = squeezeConPresentor(self.ModelConPool,self.connectionPool)
        self.connectionPool.cbAddOnMessagesToProcess(self.OnNewMessages)
        
        
        #Now load the settings presentor
        
        self.SettingsPresentor  = frmSettingsPresentor(self.ModelFrmSettings)
        self.SettingsPresentor.cbAddOnApply(self.ConCtrlInteractor.OnApply)
        self.SettingsPresentor.cbAddOnSave(self.OnSave)
        # Now apply the Settings
        #self.ConCtrlInteractor.OnApply(None)
        #print self.ModelFrmSettings.host.get()
        self.messagesUnblock()
        
    def OnNewMessages (self,details):
        self.log.debug('OnNewMessages')
        evt = SomeNewEvent(attr1="on_msg")
        #post the event
        wx.PostEvent(self, evt)
        
    def messagesBlock(self):
        self.block = True
    def messagesUnblock(self):
        self.block = False    
    def onTaskBarPopUpMenu(self,evt):
        self.log.debug("onTaskBarPopUpMenu=%s",(None))
        self.CreatePopUp()

    def EventRevived(self,evt):
        if self.block:
            return    
        
        self.log.debug("EventRevived=%s",(evt.attr1 ))
        if evt.attr1 == "on_connected":
            #self.ModelGuiThread.connected.update(self.ModelConPool.connected.get())
            pass
        if evt.attr1 == "on_players":
            pass
        if evt.attr1 == "on_msg":
            self.jrpc.requestUpdateModel()
        
            #print self.ModelConPool.Players
        self.setUpdateModel(evt)
            
    def OnSave(self,presentor):
        self.ConCtrlInteractor.OnApply(presentor)
        self.configPresentor.save()
    def OnTimer(self,event):
        
        if self.block:
            return
        self.jrpc.requestUpdateModel()
        connected = self.ModelConPool.connected.get()
        if False == connected: 
            self.squeezeConCtrl.RecConnectionOnline()
            return
        #self.log.debug("on timer")
        self.log.debug("on timer= %s" % (self.ModelConPool.port.get()))
        #self.timer.
        #print dir(self.timer)
        #self.interactorWxUpdate.on_connected()
        self.count+= 1
        #self.squeezeConCtrl.RecConnectionOnline()
        self.squeezeConCtrl.OnPlayersCount(None)
        if self.count > 2:
            self.count = 0
        
        if self.count > 0:
            self.squeezeConCtrl.RecPlayerStatus(self.count)
            self.squeezeConCtrl.PlayerStatus(self.count)
            self.viewWxToolBarSrc.update()
        else:
            self.log.debug("RecConnectionOnline")
        
        
        self.log.debug("on timer=cccccccccccc %s" % (self.ModelConPool.playerList))
        self.setUpdateModel(None)
    def on_event(self,event):
        self.log.debug("on_event")
        
    def Exit(self):
        self.SettingClose(None)
        self.messagesBlock()
        self.squeezeConCtrl.view1.wait_completion()
        self.tb.Destroy()
    def CreatePopUp(self):
        newMenu = self.tbPopUpMenuPresentor.getMenu()
        return newMenu
        
    def setUpdateModel(self,param):
        
        toolTip = self.viewWxToolBarSrc.gettoolTip()
        self.tbPresentor._OnToolTipChange(toolTip)
        currentIcon = self.viewWxToolBarSrc.getIconName()
        #self.log.debug("setUpdateModel")
        self.ModelGuiThread.currentIconName.update(currentIcon)
        #self.log.debug("setUpdateModel=%s" % (currentIcon))
    def SettingsOpen(self):
        self.SettingsPresentor.SettingsOpen()
    
        
    def SettingClose(self,evnt):
        self.SettingsPresentor.SettingClose(None)
    
    def doCbOnPlay(self,player):
        
        self.squeezeConCtrl.Play(player)
        
    def doCbOnPause(self,player):
        results = {}
        for item in self.callbacks["on_pause"]:
            results[item] = item()
        return results
    
    def doCbOnSeekForward(self,player):
        results = {}
        for item in self.callbacks["on_seek_forward"]:
            results[item] = item()
        return results
        
    def doCbOnSeekBackwards(self,player):
        results = {}
        for item in self.callbacks["on_seek_backwards"]:
            results[item] = item()
        return results

    def doCbOnRandomSongs(self,player):
        self.squeezeConCtrl.PlayRandomSong(player)
        
