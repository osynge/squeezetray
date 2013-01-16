import wx
from wxFrmNowPlayingView import FrmNowPlaying
from models import Observable, ObservableDict

from wxFrmNowPlayingView import FrmNowPlaying
from modelsConnection import squeezePlayerMdl

from modelsWxFrmNowPlaying import mdlFrmNowPlaying
from interactorWxFrmNowPlayConnection import interactorNowPlaying
class mdlFrmInternalNowPlaying(mdlFrmNowPlaying):
    def __init__(self):
        self.__init__(mdlFrmNowPlaying)
        self.wxComboPlayerOptions = ObservableDict()
           
     

class frmPlayingPresentor:
    def __init__(self,model,interactor):
        
        self.GuiModel = model
        self.settingsOpen = False
        self.Example = None
        self.callbacks = {
            "on_exit" : {},
            "on_settings" : {},
            "on_play" : {},
            "on_pause" : {},
            "on_stop" : {},
            "on_seek_index" : {},
            "on_random_songs" : {}
        }
        self.interactor = interactor
        self.updateGuiInteractor = interactorNowPlaying()
        self.updateGuiInteractor.install(self.GuiModel,self.interactor)
    def ViewOpen(self):
        if self.settingsOpen == True:
            return
        self.Example = FrmNowPlaying(None, title='Now Playing')
        
        self.Example.Bind(wx.EVT_CLOSE, self.ViewClose)
        self.updateGuiInteractor.installGui(self.Example)
        
        self.Example.cbAddOnQuit(self.OnQuit)
        self.Example.cbAddOnPause(self.interactor.cbAddOnPause)
        
        
        self.Example.Show()
        
        self.settingsOpen = True
        
    def ViewClose(self,evnt = None):
        self.settingsOpen = False
        if self.Example != None:
            self.updateGuiInteractor.installGui(None)
            self.Example.Destroy()
        self.Example = None
        
    def OnQuit(self,iconName):
        self.ViewClose(None)
        self.interactor.doCbOnExit(None)
    
    def Update(self):
        self.updateGuiInteractor.updateTrackEnds()
        self.updateGuiInteractor.updatePlayerStatus()
