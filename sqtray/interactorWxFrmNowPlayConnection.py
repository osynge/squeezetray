from models import Observable, ObservableDict
import datetime
import wx
class watcherPlayer:
    def enable(self):
        self._enabled = True
        self.update()
    def disable(self):
        self._enabled = False
    def autoEnable(self,value=None):
        activePlayer = self.NowPlayingMdl.nowPlayPlayerId.get()
        if activePlayer == self.player.name.get():
            self.enable()
        else:
            self.disable()
    def install(self,Player,NowPlayingMdl):

        self.disable()
        self.player = Player
        self.NowPlayingMdl = NowPlayingMdl

        self.player.operationMode.addCallback(self.onOperatingMode)
        self.player.CurrentTrackEnds.addCallback(self.onCurrentTrackEnds)
        self.player.CurrentTrackId.addCallback(self.onTrackId)
        self.NowPlayingMdl.nowPlayPlayerId.addCallback(self.autoEnable)
        self.autoEnable()



    def update(self):
        self.onOperatingMode()
        self.onTrackId()
        self.onCurrentTrackEnds()


    def onTrackId(self,value = None):
        if not self._enabled:
            return
        newCurrentTrackId = self.player.CurrentTrackId.get()
        self.NowPlayingMdl.CurrentTrackId.update(newCurrentTrackId)

    def onOperatingMode(self,value = None):
        if not self._enabled:
            return
        newOperatinMode = self.player.operationMode.get()
        self.NowPlayingMdl.CurrentPlayerStatus.update(newOperatinMode)

    def onCurrentTrackEnds(self,value = None):
        if not self._enabled:
            return
        newCurrentTrackEnds = self.player.CurrentTrackEnds.get()
        self.NowPlayingMdl.CurrentTrackEnds.update(newCurrentTrackEnds)


class SongWatcher:
    def enable(self):
        self._enabled = True
        self.update()
    def disable(self):
        self._enabled = False
    def install(self,Song,NowPlayingMdl):
        self.disable()
        self.song = Song
        self.NowPlayingMdl = NowPlayingMdl
        self.song.id = Observable(None)
        self.song.updated = Observable(None)
        self.song.title.addCallback(self.onTitle)
        self.song.genres.addCallback(self.onTitle)
        self.song.genre_ids.addCallback(self.onTitle)
        self.song.album.addCallback(self.onTitle)
        self.song.artist.addCallback(self.onArtist)
        self.song.artist_ids.addCallback(self.onTitle)
        self.song.album_id.addCallback(self.onTitle)
        self.song.duration.addCallback(self.onTitle)
        self.song.tracknum.addCallback(self.onTitle)
        self.song.year.addCallback(self.onTitle)
        self.song.comment.addCallback(self.onTitle)
        self.song.type.addCallback(self.onTitle)
        self.song.tagversion.addCallback(self.onTitle)
        self.song.bitrate.addCallback(self.onTitle)
        self.song.samplesize.addCallback(self.onTitle)
        self.song.filesize.addCallback(self.onTitle)
        self.song.coverart.addCallback(self.onTitle)
        self.song.modificationTime.addCallback(self.onTitle)
        self.song.compilation.addCallback(self.onTitle)
        self.song.samplerate.addCallback(self.onTitle)
        self.song.url.addCallback(self.onTitle)
        self.update()
    def update(self):
        self.onTitle()
        self.onArtist()
        self.onAlbum()
        self.onDuration()
    def onTitle(self,value=None):
        newCurrentTrackId = self.song.title.get()
        self.NowPlayingMdl.CurrentTrackName.update(newCurrentTrackId)

    def onArtist(self,value=None):
        newCurrentTrackId = self.song.artist.get()
        self.NowPlayingMdl.CurrentTrackArtist.update(newCurrentTrackId)
    def onAlbum(self,value=None):
        newCurrentTrackId = self.song.album.get()
        self.NowPlayingMdl.CurrentTrackAlbum.update(newCurrentTrackId)
    def onDuration(self,value=None):
        newCurrentTrackId = self.song.duration.get()
        self.NowPlayingMdl.CurrentTrackDuration.update(newCurrentTrackId)
class interactorNowPlaying:
    def __init__(self):
        self.installGui(None)
    def installGui(self,gui):
        self.view = gui
        if self.view == None:
            return
        self.view.cbPlayer.Bind(wx.EVT_COMBOBOX, self.OnCbSelect)
        self.view.BtnPause.Bind(wx.EVT_BUTTON, self.OnCbPause)
        self.view.BtnNext.Bind(wx.EVT_BUTTON, self.OnCbTrackSeekForward)
        self.view.BtnLast.Bind(wx.EVT_BUTTON, self.OnCbTrackSeekBackward)
        self.view.BtnPlay.Bind(wx.EVT_BUTTON, self.OnCbPlay)
        self.view.BtnStop.Bind(wx.EVT_BUTTON, self.OnCbStop)

        self.view.Bind(wx.EVT_MENU, self.OnShowSettings,id=self.view.MenuItemSettings.GetId() )

        self.view.Bind(wx.EVT_MENU, self.OnCbPause,id=self.view.MenuItemPause.GetId() )
        self.view.Bind(wx.EVT_MENU, self.OnCbTrackSeekForward,id=self.view.MenuItemNext.GetId() )
        self.view.Bind(wx.EVT_MENU, self.OnCbTrackSeekBackward,id=self.view.MenuItemLast.GetId() )
        self.view.Bind(wx.EVT_MENU, self.OnCbPlay,id=self.view.MenuItemPlay.GetId() )
        self.view.Bind(wx.EVT_MENU, self.OnCbStop,id=self.view.MenuItemStop.GetId() )
        self.view.Bind(wx.EVT_MENU, self.OnCbRandomSong,id=self.view.MenuItemRndSong.GetId() )


        self.updateView()
        self.OnUpdateFrmIcon()
    def install(self,mdlNowPlaying,mainInteractor):
        self.mdlNowPlaying = mdlNowPlaying
        self.watchers = {}
        self.watchersSong = {}
        self.mainInteractor = mainInteractor
        self.mdlNowPlaying.availablePlayer.addCallback(self.onAvailablePlayer)
        self.mdlNowPlaying.nowPlayPlayerId.addCallback(self.updatePlayerId)
        self.mdlNowPlaying.CurrentTrackId.addCallback(self.updateTrackId)
        self.mdlNowPlaying.CurrentTrackName.addCallback(self.updateTrackName)
        self.mdlNowPlaying.CurrentTrackArtist.addCallback(self.updateTrackArtist)
        self.mdlNowPlaying.CurrentTrackAlbum.addCallback(self.updateTrackAlbum)
        self.mdlNowPlaying.CurrentTrackEnds.addCallback(self.updateTrackEnds)
        self.mdlNowPlaying.CurrentTrackDuration.addCallback(self.updateTrackEnds)
        self.mdlNowPlaying.CurrentPlayerStatus.addCallback(self.updatePlayerStatus)
        self.mdlNowPlaying.frmCurrentIconName.addCallback(self.OnUpdateFrmIcon)
        self.mdlNowPlaying.serverConnected.addCallback(self.OnConnected)

        self.watchingPlayer = Observable(None)
        self.watchingSong = Observable(None)

        for player in self.mdlNowPlaying.availablePlayer.keys():
            self.onAvailablePlayer(player)
        self.updateView()

    def UpdateIcon(self,event = None):
        if self.view == None:
            return
        connected = self.mdlNowPlaying.serverConnected.get()
        playerId = self.mdlNowPlaying.CurrentTrackId.get()
        playerStatus = self.mdlNowPlaying.CurrentPlayerStatus.get()
        iconName = 'ART_APPLICATION_STATUS_DISCONECTED'
        if connected:
            iconName = 'ART_APPLICATION_STATUS_CONNECTED'
        if playerId != None:

            iconName = 'ART_PLAYER_PLAY'
        if playerStatus != None:
            mapping = {'playing' :'ART_PLAYER_PLAY',
                        'paused' : 'ART_PLAYER_PAUSE',
                        'stop' : 'ART_PLAYER_STOP' }
            if playerStatus in mapping.keys():
                iconName = mapping[playerStatus]
        self.mdlNowPlaying.frmCurrentIconName.update(iconName)

    def OnConnected(self,event = None):
        self.UpdateIcon()


    def OnUpdateFrmIcon(self,event = None):
        if self.view == None:
            return
        iconName = self.mdlNowPlaying.frmCurrentIconName.get()
        if iconName == None:
            return
        icon = wx.ArtProvider.GetIcon(iconName, wx.ART_TOOLBAR, (16,16))
        self.view.SetIcon(icon)


    def OnShowSettings(self,event):
        self.mainInteractor.doCbOnSettings(event)
    def OnCbPlay(self,event):
        currentPlayer = self.mdlNowPlaying.nowPlayPlayerId.get()
        if currentPlayer != None:
            self.mainInteractor.doCbOnPlay(event,currentPlayer)
    def OnCbStop(self,event):
        currentPlayer = self.mdlNowPlaying.nowPlayPlayerId.get()
        if currentPlayer != None:
            self.mainInteractor.doCbOnStop(event,currentPlayer)

    def OnCbSelect(self,event):
        value = event.GetString()
        if not value in self.mdlNowPlaying.availablePlayer.keys():
            return

        self.mdlNowPlaying.nowPlayPlayerId.update(value)

        self.updatePlayerStatus()
    def OnCbPause(self,event):
        currentPlayer = self.mdlNowPlaying.nowPlayPlayerId.get()
        if currentPlayer != None:
            self.mainInteractor.doCbOnPause(event,currentPlayer)
    def OnCbTrackSeekForward(self,event):
        currentPlayer = self.mdlNowPlaying.nowPlayPlayerId.get()
        if currentPlayer != None:
            self.mainInteractor.doCbOnSeekForward(event,currentPlayer)

    def OnCbTrackSeekBackward(self,event):
        currentPlayer = self.mdlNowPlaying.nowPlayPlayerId.get()
        if currentPlayer != None:
            self.mainInteractor.doCbOnSeekBackwards(event,currentPlayer)


    def OnCbRandomSong (self,event):
        currentPlayer = self.mdlNowPlaying.nowPlayPlayerId.get()
        if currentPlayer != None:
            self.mainInteractor.doCbOnRandomSongs(event,currentPlayer)


    def updateView(self):
        availablePlayers = set(self.mdlNowPlaying.availablePlayer.keys())
        #playerslist = set(self.view.Players.keys())
        watcherlist = set(self.watchers.keys())

        watchers2delnew = watcherlist.difference(availablePlayers)
        watchers2new = availablePlayers.difference(watcherlist)

        for watch in watchers2new:
            newWatcher = watcherPlayer()
            self.watchers[watch] = watcherPlayer()
            self.watchers[watch].install(
                self.mdlNowPlaying.availablePlayer[watch],
                self.mdlNowPlaying)
        for watch in watchers2delnew:
            del self.watchers[watch]

        self.updateCombo()
        self.updateTrackName()
        self.updateTrackArtist()
        self.updateTrackAlbum()
        self.updateTrackEnds()
        #self.OnConnected()


    def onOperatingMode(self,key):
        self.log.error("onOperatingMode=" % (self.watchingPlayer.get()))

    def onCurrentTrackEnds(self,key):
        self.log.error("onCurrentTrackEnds=" % (self.watchingPlayer.get()))

    def onOperatingMode(self,operationMode):
        self.log.error("onTrackId=" % (self.watchingPlayer.get()))
        playerId = self.mdlNowPlaying.nowPlayPlayerId.get()
        self.mdlNowPlaying.operationMode.update(operationMode)


    def onAvailablePlayer(self,key):
        added = False
        if not key in self.mdlNowPlaying.availablePlayer.keys():
            added = True
        self.updateView()



        currentKey = self.mdlNowPlaying.nowPlayPlayerId.get()

        if None == currentKey:
            defaultPlayer = self.mdlNowPlaying.CurrentPlayerIdDefault.get()
            if None == defaultPlayer:
                defaultPlayer = key

            self.mdlNowPlaying.nowPlayPlayerId.update(defaultPlayer)
        self.updateCombo()


    def updateCombo(self,key = None):
        if self.view == None:
            return
        availableKeys = self.mdlNowPlaying.availablePlayer.keys()
        availableKeysLen = len(availableKeys)
        combokeysDesitered = set([''])
        if availableKeysLen > 0:
            combokeysDesitered = set(availableKeys)
        combokeysFound = set(self.view.cbPlayer.Items)
        todelete = combokeysFound.difference(combokeysDesitered)
        newkeys = combokeysDesitered.difference(combokeysFound)

        # No delete option in wxpython so this work around
        if len(todelete) > 0:
            self.view.cbPlayer.Clear()
            newkeys = availableKeys
        for thiskey in newkeys:
            self.view.cbPlayer.Append(thiskey)

        selectedplayer = self.mdlNowPlaying.nowPlayPlayerId.get()
        if selectedplayer != None:
            if selectedplayer in self.view.cbPlayer.Items:
                self.view.cbPlayer.SetValue(selectedplayer)
    def updatePlayerId(self,value):
        self.UpdateIcon()
        self.updateView()
        currentKey = self.mdlNowPlaying.nowPlayPlayerId.get()
        if None == currentKey:
            return
        watcherlist = set(self.watchers.keys())
        if value == None:
            availableKeys = self.mdlNowPlaying.availablePlayer.keys()
            availableKeysLen = len (availableKeys)
            if availableKeysLen > 0:
                value = availableKeys[0]
                self.mdlNowPlaying.nowPlayPlayerId.update(availableKeys[0])
                self.view.cbPlayer.SetValue(availableKeys[0])

        for player in watcherlist:
            if currentKey == player:
                self.watchers[player].enable()
                self.watchers[player].update()
            else:
                self.watchers[player].disable()


        #self.watchPlayer(value)  
        playerId = self.mdlNowPlaying.nowPlayPlayerId.get()
        if playerId == None:
            return
        if not playerId in self.mdlNowPlaying.availablePlayer.keys() :
            return


    def updateTrackId(self,TrackId):

        currentWatching = self.mdlNowPlaying.CurrentTrackId.get()

        if not currentWatching in self.mdlNowPlaying.availableSong.keys():
            return

        self.songWatch = SongWatcher()
        self.songWatch.install(self.mdlNowPlaying.availableSong[TrackId],self.mdlNowPlaying)

    def updateTrackName(self,event = None):
        if self.view == None:
            return
        displayText = ''
        TrackName = self.mdlNowPlaying.CurrentTrackName.get()
        if TrackName == None:
            self.view.tcHost.SetValue('')
            return
        for track in TrackName:
            displayText += track
        self.view.tcHost.SetValue(displayText)
    def updateTrackArtist(self,event= None):
        if self.view == None:
            return
        displayText = ''
        TrackArtist = self.mdlNowPlaying.CurrentTrackArtist.get()
        if TrackArtist == None:
            self.view.tbArtist.SetValue('')
            return
        for track in TrackArtist:
            displayText += track
        oldValue = self.view.tbArtist.GetValue()
        if oldValue != displayText:
            self.view.tbArtist.SetValue(displayText)
    def updateTrackAlbum(self,event= None):
        if self.view == None:
            return
        displayText = ''
        TrackAlbum = self.mdlNowPlaying.CurrentTrackAlbum.get()
        if TrackAlbum == None:
            self.view.tbArtist.SetValue('')
            return
        for track in TrackAlbum:
            displayText += track
        self.view.tbAlbum.SetValue(displayText)
    def updateTrackEnds(self,event= None):
        if self.view == None:
            return
        displayText = ''
        TrackEnds = self.mdlNowPlaying.CurrentTrackEnds.get()
        if TrackEnds == None:
            self.view.slider.SetValue(10000)
            return
        Tracklength = self.mdlNowPlaying.CurrentTrackDuration.get()
        if Tracklength == None:
            self.view.slider.SetValue(10000)
            return
        now = datetime.datetime.now()
        timediff = TrackEnds - now
        length = Tracklength[0]
        remaining = Tracklength[0] - timediff.seconds
        sliderpos = remaining * 10000 / Tracklength[0]
        if sliderpos > 10000:
            sliderpos = 10000
        self.view.slider.SetValue(sliderpos)
    def updatePlayerStatus(self,event= None):
        self.UpdateIcon()
        if self.view == None:
            return

        status = self.mdlNowPlaying.CurrentPlayerStatus.get()
        disablePause = False
        disableplay = False
        disableStop = False
        if status == None:
            disablePause = True
            disableplay = True
            disableStop = True
        if status == 'paused':
            disablePause = True
        if status == 'playing':
            disableplay = True
        if status == 'stop':
            disablePause = True
            disableStop = True
        if disableplay == self.view.BtnPlay.Enabled:
            if disableplay:
                self.view.BtnPlay.Disable()
            else:
                self.view.BtnPlay.Enable()
        if disablePause == self.view.BtnPause.Enabled:
            if disablePause:
                self.view.BtnPause.Disable()
            else:
                self.view.BtnPause.Enable()
        if disableStop == self.view.BtnStop.Enabled:
            if disableStop:
                self.view.BtnStop.Disable()
            else:
                self.view.BtnStop.Enable()
