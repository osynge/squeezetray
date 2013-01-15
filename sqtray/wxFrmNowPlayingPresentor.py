import wx
from wxFrmNowPlayingView import FrmNowPlaying
from models import Observable, ObservableDict

from wxFrmNowPlayingView import FrmNowPlaying


class mdlFrmNowPlaying:
    def __init__(self):
        self.frmTooltip = Observable("... initialising")
        self.frmCurrentIconName = Observable(None)
        self.frmPosition = Observable(wx.DefaultPosition)
        self.frmSize = wx.Size(250, 250)
        
        self.availablePlayer = ObservableDict()
        self.availableSong = ObservableDict()
        self.availableArtist = ObservableDict()
        
        self.nowPlayPlayerId = Observable(None)
        
        self.nowPlayTrackId = Observable(None)
        
        self.showingPlayer = Observable(0)
        self.connectionMsg = Observable(None)
        self.statusText = Observable(None)




        
        

class frmPlayingPresentor:
    def __init__(self,model):
        
        self.GuiModel = model
        self.settingsOpen = False
        self.Example = None
        
    def SettingsOpen(self):
        if self.settingsOpen == True:
            return
        self.Example = FrmNowPlaying(None, title='Now Playing')
        self.Example.ModelSet(self.GuiModel)
        self.Example.Bind(wx.EVT_CLOSE, self.SettingClose)
        self.Example.updateFromModel()
        self.Example.cbAddOnApply(self.OnApply)
        self.Example.cbAddOnSave(self.OnSave)
        self.Example.cbAddOnCancel(self.OnCancel)
        
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
