from models import Observable, ObservableDict
import wx
class mdlFrmNowPlaying:
    def __init__(self):
        self.frmTooltip = Observable("... initialising")
        self.frmCurrentIconName = Observable(None)
        self.frmPosition = Observable(wx.DefaultPosition)
        self.frmSize = wx.Size(250, 250)
        self.serverConnected = Observable(None)
        self.availablePlayer = ObservableDict()
        self.availableSong = ObservableDict()
        self.availableArtist = ObservableDict()
        self.CurrentPlayerIdDefault = Observable(None)
        self.nowPlayPlayerId = Observable(None)
        self.CurrentPlayerStatus = Observable(None)
        
        self.CurrentTrackId = Observable(None)
        self.CurrentTrackArtist = Observable(None)
        self.CurrentTrackName = Observable(None)
        self.CurrentTrackAlbum = Observable(None)
        
        self.CurrentTrackEnds = Observable(None)
        self.CurrentTrackDuration = Observable(None)
        self.showingPlayer = Observable(0)
        self.connectionMsg = Observable(None)
        self.statusText = Observable(None)
        
