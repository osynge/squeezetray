
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

from sqtray.wxTrayIconPopUpMenu import  PopupMenuPresentor
class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self,model):
        super(TaskBarIcon, self).__init__()
        self.model = model
        self.icon = wx.ArtProvider.GetIcon(
            "ART_APPLICATION_STATUS_DISCONECTED", 
            wx.ART_OTHER,
            (16,16))
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
        
        self.log.debug("Icon changed from '%s:%s'" % (self.IconStatus,str(self.IconSize).strip()))
        self.log.debug("Icon changed to '%s:%s'" % (status,size))
        self.IconStatus = status
        self.IconSize = size
        
        #self.icon = wxIcons.trayDefault.getIcon()
        if status == None:
            self.log.error("status == None")
            return
        #self.icon = wx.ArtProvider.GetIcon(status, "WIBBLE",size)
        testIcon = wx.ArtProvider.GetIcon(self.IconStatus,wx.ART_OTHER ,size)
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
                self.log.debug("Icon changed '%s:%s'" % (self.IconStatus,str(self.IconSize).strip()))        
                return
        if hasattr(self,'icon'):
            self.SetIcon(self.icon, tooltip)
        self.ToolTipText = unicode(tooltip)
    def CreatePopupMenu(self):
        result = None
        
        if "CreatePopupMenu" in self.CallBacks:
            resultSet = {}
            for item in self.CallBacks["CreatePopupMenu"]:
                #print "called"
                
                rc = item()
                if rc == None:
                    continue
                return rc
                #print "rc=%s" % (rc)
                if rc != None:
                    result = rc
            
            
        self.log.debug('No menu? result = %s' % (result))
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
        return self.presenter.SelectPopupMenu()
        
    def on_settings(self, evt):
        #print "asdasdaSD"
        self.presenter.on_settings()

class TaskBarIconUpdateInteractor(object):
    """ http://wiki.wxpython.org/ModelViewPresenter inspired """

    def install(self, model, view):
        self.model = model
        self.view = view
        self.model.tooltip.addCallback(self._OnToolTipChange)
        
    def _OnToolTipChange(self,event):
        self.view.set_toolTip(ToolTip)
        
        self.log.warn("dsfsf")
    
        

def timedelta2str(timedeltainst):
    delta = abs(timedeltainst)
    totalseconds = delta.seconds + delta.days * 24 * 3600
    output = "%s:%02d" % (totalseconds / 60, totalseconds % 60)
    return output

