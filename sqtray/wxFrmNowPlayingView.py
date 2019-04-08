

import wx
from wxEvents import EVT_RESULT_CONNECTED_ID
from wxEvents import EVT_RESULT_PLAYERS_ID
from wxEvents import EVT_RESULT_CURRENT_TRACK_ID
from wxEvents import EVT_RESULT_CONNECTION_ID
import wxIcons
import logging

class FrmNowPlaying(wx.Frame):

    def __init__(self, parent,  title):
        self.log = logging.getLogger("FrmNowPlaying")
        self.callbacks = {
            "on_pause" : {},
            "on_save" : {},
            "on_quit" : {},
        }
        self.parent = parent
        self.title = title
        w, h = (250, 250)
        wx.Frame.__init__(self, self.parent, -1, self.title, wx.DefaultPosition, wx.Size(w, h))
        self.menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.MenuItemSettings = self.fileMenu.Append(wx.NewId(), "Settings",
                                       "Configure the application")
        fitem = self.fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')

        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)
        self.menubar.Append(self.fileMenu, '&File')
        self.menuActions = wx.Menu()
        self.MenuItemPlay = self.menuActions.Append(wx.NewId(), "Play",
                                       "Start Playing")
        self.MenuItemStop = self.menuActions.Append(wx.NewId(), "Stop",
                                       "Stop Start")
        self.MenuItemPause = self.menuActions.Append(wx.NewId(), "Pause",
                                       "Pause, stop playing but keep place.")
        self.MenuItemNext = self.menuActions.Append(wx.NewId(), "Next",
                                       "Skip to next track in Playlist")
        self.MenuItemLast = self.menuActions.Append(wx.NewId(), "Last",
                                       "Play Previous Track on Playlist")
        self.MenuItemRndSong = self.menuActions.Append(wx.NewId(), "RndSong",
                                       "Randomise playlist and start playing")


        self.menubar.Append(self.menuActions, '&Actions')
        self.SetMenuBar(self.menubar)

        self.sizer = wx.GridBagSizer(8, 8)
        self.Connect(-1, -1, EVT_RESULT_CONNECTED_ID, self.OnConnected)
        self.Connect(-1, -1, EVT_RESULT_PLAYERS_ID, self.OnConnected)
        self.Connect(-1, -1, EVT_RESULT_CONNECTION_ID, self.OnConnected)


        play_ico = wx.ArtProvider.GetBitmap('ART_PLAYER_PLAY',wx.ART_BUTTON, (32,32))
        self.BtnPlay = wx.BitmapButton(self,id=-1,bitmap=play_ico,style=wx.BU_AUTODRAW)
        pause_ico = wx.ArtProvider.GetBitmap('ART_PLAYER_PAUSE',wx.ART_BUTTON, (32,32))

        self.BtnPause = wx.BitmapButton(self,id=-1,bitmap=pause_ico,style=wx.BU_AUTODRAW)
        stop_ico = wx.ArtProvider.GetBitmap('ART_PLAYER_STOP',wx.ART_BUTTON, (32,32))
        self.BtnStop = wx.BitmapButton(self,id=-1,bitmap=stop_ico,style=wx.BU_AUTODRAW)

        next_ico = wx.ArtProvider.GetBitmap('ART_PLAYER_SEEK_FORWARD',wx.ART_BUTTON, (32,32))
        self.BtnNext = wx.BitmapButton(self,id=-1,bitmap=next_ico,style=wx.BU_AUTODRAW)

        next_ico = wx.ArtProvider.GetBitmap('ART_PLAYER_SEEK_BACKWARD',wx.ART_BUTTON, (32,32))
        self.BtnLast = wx.BitmapButton(self,id=-1,bitmap=next_ico,style=wx.BU_AUTODRAW)


        self.sizer.Add(self.BtnLast, (7, 0), wx.DefaultSpan, wx.EXPAND)
        self.sizer.Add(self.BtnStop, (7, 1), wx.DefaultSpan, wx.EXPAND)
        self.sizer.Add(self.BtnPlay, (7, 2), wx.DefaultSpan, wx.EXPAND)
        self.sizer.Add(self.BtnPause, (7, 3), wx.DefaultSpan, wx.EXPAND)
        self.sizer.Add(self.BtnNext, (7, 4), wx.DefaultSpan, wx.EXPAND)

        label1 = wx.StaticText(self, -1, 'Player:')

        self.sizer.Add(label1, (0, 0), wx.DefaultSpan, wx.EXPAND)

        self.cbPlayer = wx.ComboBox(self, -1, style=wx.CB_READONLY)
        self.sizer.Add(self.cbPlayer, (0, 1), (1,7), wx.EXPAND)

        self.tcHost = wx.TextCtrl(self, -1 )
        self.sizer.Add(self.tcHost , (1, 1), (1,7), wx.EXPAND)
        label2 = wx.StaticText(self, -1, 'Title:')
        self.sizer.Add(label2, (1, 0), wx.DefaultSpan, wx.EXPAND)
        label3 = wx.StaticText(self, -1, 'Arist:')
        self.sizer.Add(label3, (2, 0), wx.DefaultSpan, wx.EXPAND)
        self.tbArtist = wx.TextCtrl(self, -1 )
        self.sizer.Add(self.tbArtist, (2, 1), (1,7), wx.EXPAND)
        label4 = wx.StaticText(self, -1, 'Album:')
        self.sizer.Add(label4, (3, 0), wx.DefaultSpan, wx.EXPAND)
        self.tbAlbum = wx.TextCtrl(self, -1 )
        self.sizer.Add(self.tbAlbum, (3, 1), (1,7), wx.EXPAND)

        self.statusbar = self.CreateStatusBar()
        #self.sizer.Add(self.statusbar, (9, 0),(2,9), wx.EXPAND)

        self.slider = wx.Slider(self, value=0, minValue=0, maxValue=10000,style=wx.SL_HORIZONTAL)
        self.sizer.Add(self.slider, (5, 0),(1,8), wx.EXPAND)
        self.Bind(wx.EVT_SCROLL, self.OnSliderScroll)


        self.sizer.AddGrowableRow(7)

        self.sizer.AddGrowableCol(7)

        self.SetSizerAndFit(self.sizer)


        self.icon = wxIcons.trayDefault.getIcon()
        self.SetIcon(self.icon)
        self.IconStatus = None
        self.IconSize = None
        self.model = None

        self.CurrentStatusText = None

    def ModelSet(self,model):
        self.model = model



    def cbAddOnPause(self,func):
        self.callbacks['on_pause'][func] = 1

    def cbDoOnPause(self):
        for item in self.callbacks["on_pause"]:
            item(self)
    def cbAddOnPause(self,func):
        self.callbacks['on_save'][func] = 1

    def cbDoOnPause(self):
        for item in self.callbacks["on_save"]:
            item(self)    
    def cbAddOnQuit(self,func):
        self.callbacks['on_quit'][func] = 1

    def cbDoOnQuit(self):
        for item in self.callbacks["on_quit"]:
            item(self)    

    def OnConnected(self,event):
        self.updateFromModel()

    def OnSliderScroll(self, event):
        pass
    def OnQuit(self, event):
        self.cbDoOnQuit()
