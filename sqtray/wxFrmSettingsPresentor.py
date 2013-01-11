import wx
from sqtray.wxFrmSettings import FrmSettings

from modelsWxFrmSettings import mdlFrmSettings
from jrpcServerThreadPool import SqueezeConnectionWorker
import  wx
import  wx.lib.newevent
SomeNewEvent, EVT_SOME_NEW_EVENT = wx.lib.newevent.NewEvent()
SomeNewCommandEvent, EVT_SOME_NEW_COMMAND_EVENT = wx.lib.newevent.NewCommandEvent()


class frmSettingsModelWatcher():
    def install(self, src, wxObject):
        
        self.messagesBlock()
        self.model = src
        self.wxObject = wxObject 
        self.model.currentIconName.addCallback(self.onIconChange)
        self.model.tooltip.addCallback(self.onIconChange)
        self.model.host.addCallback(self.onIconChange)
        self.model.port.addCallback(self.onIconChange)
        self.model.connectionMsg.addCallback(self.onIconChange)
        self.model.statusText.addCallback(self.onIconChange)
        
        self.messagesUnblock()
        
    
    def onIconChange(self,value):
        if self.block:
            return
        evt = SomeNewEvent(attr1="on_connected")
        wx.PostEvent(self.wxObject, evt)
        
        
    def messagesBlock(self):
        self.block = True
    def messagesUnblock(self):
        self.block = False


class frmSettingsPresentor:
    def __init__(self,model):
        self.interactor = frmSettingsModelWatcher()
        self.callbacks = {
            "on_settings" : {},
            "on_modelUpdate" : {},
            "on_save" : {},
            "on_apply" : {},
            "on_cancel" : {},
        }
        self.GuiModel = model
        self.settingsOpen = False
        self.Example = None
        
    def SettingsOpen(self):
        if self.settingsOpen == True:
            return
        self.Example = FrmSettings(None, title='Settings')
        self.Example.ModelSet(self.GuiModel)
        self.Example.Bind(wx.EVT_CLOSE, self.SettingClose)
        self.Example.updateFromModel()
        self.Example.cbAddOnApply(self.OnApply)
        self.Example.cbAddOnSave(self.OnSave)
        self.Example.cbAddOnCancel(self.OnCancel)
        
        self.interactor.install(self.GuiModel,self.Example)
        self.Example.Show()
        
        self.settingsOpen = True
        
    def SettingClose(self,evnt):
        self.settingsOpen = False
        if self.Example != None:
            self.Example.Destroy()
        self.Example = None
        
    def OnCancel(self,iconName):
        self.SettingClose(None)
        
    def OnSave(self,iconName):
        self.cbDoOnSave()
        
    def OnApply(self,iconName):
        self.cbDoOnApply()
        
    
    def cbAddOnApply(self,func):
        self.callbacks['on_apply'][func] = 1
        
    def cbDoOnApply(self):
        for item in self.callbacks["on_apply"]:
            item(self)    
    def cbAddOnSave(self,func):
        self.callbacks['on_save'][func] = 1
        
    def cbDoOnSave(self):
        for item in self.callbacks["on_save"]:
            item(self)    
