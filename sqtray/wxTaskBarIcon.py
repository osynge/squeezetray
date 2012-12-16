
import wx
from wxEvents import EVT_RESULT_CONNECTED_ID
from wxEvents import EVT_RESULT_PLAYERS_ID
from wxEvents import EVT_RESULT_CURRENT_TRACK_ID
from sqtray.wxFrmSettings import FrmSettings
import datetime
import functools
import wxIcons
import logging

TRAY_TOOLTIP = 'SqueezeTray'

from sqtray.models import Observable

from sqtray.wxTrayIconPopUpMenu import CreatePopupMenu,PopUpMenuInteractor, PopupMenuPresentor
class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self,model):
        super(TaskBarIcon, self).__init__()
        self.model = model
        #self.icon = wxIcons.trayDefault.getIcon()
        self.icon = wx.ArtProvider.GetIcon("ART_APPLICATION_STATUS_DISCONECTED", "ART_APPLICATION_STATUS_DISCONECTED", (16,16))
        self.SetIcon(self.icon,"SqueezeTray")
        self.Example = None
        self.CallBacks = { 'CreatePopupMenu' : []}
        self.IconStatus = None
        self.IconSize = None
        self.log = logging.getLogger("TaskBarIcon")
    def CbAddCreatePopupMenu(self,funct):
        """Callback items shoudl return Menu objects"""
        if 'CreatePopupMenu' in self.CallBacks:
            self.CallBacks['CreatePopupMenu'].append(funct)
        
    def Show(self):
        
        self.app.squeezeConCtrl.RecConnectionOnline()
        super(TaskBarIcon, self).Show()        
        
    def GetSqueezeServerPlayer(self):
        if not hasattr(self,'model'):
            return None
        return self.model.GuiPlayer.get()



    def set_icon(self, status,size):
        if (self.IconStatus == status) and (self.IconSize == size):
            self.log.debug("Icon unchanged")
            return
        self.IconStatus = status
        self.IconSize = size
        self.log.debug("Icon changed '%s:%s'" % (self.IconStatus,str(self.IconSize).strip()))
        
        
        #self.icon = wxIcons.trayDefault.getIcon()
        if status == None:
            self.log.error("status == None")
            return
        self.icon = wx.ArtProvider.GetIcon(status, "WIBBLE",size)
        testIcon = wx.ArtProvider.GetIcon(self.IconStatus,"WIBBLE" ,size)
        if not testIcon.Ok():
            self.log.debug("Icon not OK")
            return
        self.icon = testIcon
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
    def CreatePopupMenu(self):
        result = None
        if "CreatePopupMenu" in self.CallBacks:
            for item in self.CallBacks["CreatePopupMenu"]:
                #print "called"
                rc = item()
                #print "rc=%s" % (rc)
                if rc != None:
                    result = rc
        return result
        

class TaskBarIconInteractor(object):
    """ http://wiki.wxpython.org/ModelViewPresenter inspired """

    def install(self, presenter, view):
        self.presenter = presenter
        self.view = view
        self.view.Bind(wx.EVT_TASKBAR_MOVE, self.on_move)
        self.view.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.view.Bind(wx.EVT_TASKBAR_LEFT_UP, self.on_left_up )
        #self.view.Bind(wx.EVT_TASKBAR_RIGHT_DOWN, self.on_right_down )
        #self.view.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.on_right_up )
        self.view.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.on_left_dclick)
        self.view.Bind(wx.EVT_TASKBAR_RIGHT_DCLICK, self.on_right_dclick)
        #self.Bind(wx.EVT_TASKBAR_CLICK, self.view.on_click )
        self.view.Connect(-1, -1, EVT_RESULT_PLAYERS_ID, self.OnPlayers)
        self.view.Connect(-1, -1, EVT_RESULT_CURRENT_TRACK_ID, self.OnTrack)
        self.view.CbAddCreatePopupMenu(self.CreatePopupMenu)
    def on_move(self, evt):
        self.presenter.on_move()
    def on_left_down(self, evt):
        self.presenter.on_left_down()
    def on_left_up(self, evt):
        self.presenter.on_left_up()
    def on_right_down(self, evt):
        self.presenter.on_right_down()
    def on_right_up(self, evt):
        self.presenter.on_right_up()
    def on_left_dclick(self, evt):
        self.presenter.on_left_dclick()
    def on_right_dclick(self, evt):
        self.presenter.on_right_dclick()
    def on_click(self, evt):
        self.presenter.on_click()
    def OnPlayers(self, evt):
        self.presenter.OnPlayers()
    def OnTrack(self, evt):
        self.presenter.OnTrack()
    def CreatePopupMenu(self):
        return self.presenter.CreatePopupMenu()
        
    def on_settings(self, evt):
        #print "asdasdaSD"
        self.presenter.on_settings()


def timedelta2str(timedeltainst):
    delta = abs(timedeltainst)
    totalseconds = delta.seconds + delta.days * 24 * 3600
    output = "%s:%s" % (totalseconds / 60, totalseconds % 60)
    return output
class TaskBarIconPresentor(object):
    def __init__(self, Model, View, interactor):
        self.Model = Model
        self.View = View
        interactor.install(self,self.View)
        self.currentPlayer = Observable(None)
        
        self.callbacks = {
            "on_settings" : [],
        }
        self.TaskBarIconName = None
    def cbAddOnSettings(self,func):
        self.callbacks['on_settings'].append(func)
    def OnTrack(self):
        self.UpdateToolTip()
    def GetSqueezeServerPlayer(self):
        return self.currentPlayer.get()
    def UpdateToolTip(self):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            for index in  range(len(self.Model.playerList)):
                playerName = self.Model.playerList[index].name.get()
                if playerName == player:
                    newToolTip = unicode(player)
                    CurrentOperationMode = self.Model.playerList[index].operationMode.get()
                    if CurrentOperationMode != None:
                        newToolTip += ":%s" % (CurrentOperationMode)
                    CurrentTrackTitle = self.Model.playerList[index].CurrentTrackTitle.get()
                    if CurrentTrackTitle != None:
                        newToolTip += "\nTrack:%s" % (CurrentTrackTitle)
                    CurrentTrackArtist = self.Model.playerList[index].CurrentTrackArtist.get()
                    if CurrentTrackArtist != None:
                        newToolTip += "\nArtist:%s" % (CurrentTrackArtist)
                    CurrentTrackEnds = self.Model.playerList[index].CurrentTrackEnds.get()
                    #print "CurrentTrackEnds=%s" % (CurrentTrackEnds)
                    if CurrentTrackEnds != None:
                        seconds = timedelta2str(CurrentTrackEnds - datetime.datetime.now())
                        newToolTip += "\nRemaining:%s" % (seconds)
                    self.View.set_toolTip(newToolTip)
                    
                    
    def OnPlayers(self):
        #print "OnPlayers(=%s)" % (Event)            
        self.UpdateToolTip()
        #self.View.set_icon("ART_APPLICATION_STATUS_DISCONECTED",(16,16))
        #self.View.set_icon("ART_APPLICATION_STATUS_CONNECTED",(16,16))
    def CreatePopupMenu(self):
        interactor =PopUpMenuInteractor ()
        newMenu = CreatePopupMenu(self.Model,interactor)
        self.PopupMenu  = PopupMenuPresentor(self.Model,newMenu, self.squeezeConCtrl, interactor)
        self.Model.GuiPlayer.addCallback(self.PopupMenu.player.set)
        self.PopupMenu.player.set(self.Model.GuiPlayer.get())
        self.PopupMenu.AddCallbackSettings(self.on_settings)
        self.PopupMenu.player.addCallback(self.playerChanged1)
        return newMenu
    def on_move(self):
        #print 'on_move'
        self.UpdateToolTip()
    def on_settings(self):
        for item in self.callbacks["on_settings"]:
            item()

    def playerChanged1 (self,value):
        if value != self.Model.GuiPlayer.get():
            self.Model.GuiPlayer.set(value)
            #self.View.set_icon("ART_APPLICATION_STATUS_CONNECTED",(16,16))
    def on_exit(self):
        #self.on_settings_close(event)
        #wx.CallAfter(self.Destroy)
        self.View.Exit()


    def on_left_up(self,):
        print 'on_left_up' , self.GetSqueezeServerPlayer()
        player = self.GetSqueezeServerPlayer()
        if player != None:
            self.squeezeConCtrl.RecPlayerStatus(player)
        else:
            self.on_settings()
    def on_right_down(self):
        #print 'on_right_down'
        pass
    def on_right_up(self):
        print 'on_right_up'
        #menu = self.CreatePopupMenu()
        #print dir (menu)
    def on_right_dclick(self):
        print 'on_right_dclick'
        self.CreatePopUp(  event.GetPoint() )
    def on_click(self):
        pass
    
    def on_left_down(self):
        #print 'Tray icon was left-clicked.'
        pass
    def on_left_dclick(self):
        #print 'Tray icon was on_left_dclick-clicked.'
        pass
    def setIcon(self,IconName):
        #self.View.set_icon("ART_APPLICATION_STATUS_CONNECTED",(16,16))
        self.View.set_icon(IconName,(16,16))
