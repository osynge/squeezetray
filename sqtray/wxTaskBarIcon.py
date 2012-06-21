
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






class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self,model):
        super(TaskBarIcon, self).__init__()
        self.model = model
        #self.set_icon(TRAY_ICON)
        self.icon = wxIcons.trayDefault.getIcon()
        self.SetIcon(self.icon,"SqueezeTray")
        
        #self.squeezecmd = sc
        self.Example = None
        self.CallBacks = { 'CreatePopupMenu' : []}
  
    def CbAddCreatePopupMenu(self,funct):
        if 'CreatePopupMenu' in self.CallBacks:
            self.CallBacks['CreatePopupMenu'].append(funct)
        
    def Show(self):
        
        self.app.squeezeConCtrl.RecConnectionOnline()
        super(TaskBarIcon, self).Show()        
        
    def GetSqueezeServerPlayer(self):
        if not hasattr(self,'model'):
            return None
        return self.model.GuiPlayer.get()



    def OnShowPopup(self, event):
        pos = wx.GetMousePosition()
        #pos = event.GetPosition()
        
        
        
        #pos = self.panel.ScreenToClient(pos)


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
    def CreatePopupMenu(self):
        #print "here"
        result = None
        if "CreatePopupMenu" in self.CallBacks:
            for item in self.CallBacks["CreatePopupMenu"]:
                #print "called"
                rc = item(self)
                #print "rc=%s" % (rc)
                if rc != None:
                    result = rc
        return result
        
