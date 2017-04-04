import wx
from sqtray.models import Observable

import functools

import logging
from sqtray.wxArtSvg import MyArtProvider
from wxAppInteractor import GuiInteractor as TrayMenuInteractor
def create_menu_item(menu, label, art,func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    if art != None:
        save_ico = wx.ArtProvider.GetBitmap(art, wx.ART_TOOLBAR, (16,16))
        item.SetBitmap(save_ico)
    menu.AppendItem(item)
    return item







class PopupMenuPresentor(object):
    def __init__(self, Model, View,squeezecmd, interactor):
        self.Model = Model
        self.View = View
        self.squeezeConCtrl = squeezecmd
        interactor.install(self,self.View)
        self.player = Observable(None)
        self._cb_settings = []
        
        self.callbacks = {
            "on_exit" : {},
            "on_settings" : {},
            
        }
        
    def doCbExit(self):
        results = {}
        for item in self.callbacks["on_exit"]:
            results[item] = item()
        return results

    def doCbSettings(self):
        results = {}
        for item in self.callbacks["on_settings"]:
            results[item] = item()
        return results
    
    def cbAddOnExit(self,func):
        self.callbacks['on_exit'][func] = 1   
        
    def cbAddOnSettings(self,func):
        self.callbacks['on_settings'][func] = 1
        
        
        
    def GetSqueezeServerPlayer(self):
        return self.player.get()
    def onScPause(self):
        player = self.GetSqueezeServerPlayer()
        #print "player",player
        if player != None:
            self.squeezeConCtrl.Pause(player)
        else:
            self.on_settings()    
    def onScPlay(self):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            self.squeezeConCtrl.Play(player)
        else:
            self.on_settings()
    

    def onScNext(self):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            #self.squeezecmd.squeezecmd_Index(player,1)
            
            self.squeezeConCtrl.Index(player,1)
        else:
            self.on_settings()
    def onScPrevious(self):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            #self.squeezecmd.squeezecmd_Index(player,-1)
            self.squeezeConCtrl.Index(player,-1)
        else:
            self.on_settings()
    def onScRandom(self):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            #self.squeezecmd.squeezecmd_randomplay(player)
            self.squeezeConCtrl.PlayRandomSong(player)
        else:
            self.on_settings()


    def on_settings(self):
        self.doCbSettings()
    def ChangePlayer(self,player):
        oldPlayer = self.player.get()
        if oldPlayer != player:
            self.player.set(player)
    def on_exit(self):
        self.doCbExit()
        
###############################################################################






class TrayMenuPresentor(object):
    def __init__(self, model,interactor):
        self.model = model
        self.interactor = interactor
        self.log = logging.getLogger("TrayMenuPresentor")
        
    def getMenu(self):
        toolsMENU = wx.Menu()
        playersLen = len(self.model.playerList)
        self.log.debug('xxxxxxxxxxxxxxxxxxxxx=%s' % (playersLen))
        if playersLen >1:
            for i in range(playersLen):
                playerName = self.model.playerList[i].name.get()
                if playerName == None:
                    self.log.error("Player[%s] with no name" % (i))
                    continue
                playersMENU = wx.Menu()
                toolsMENU.AppendMenu(-1,playerName , playersMENU) 
                MenuItem = wx.MenuItem(playersMENU, -1, 'Play')
                save_ico = wx.ArtProvider.GetBitmap("ART_PLAYER_PLAY", wx.ART_TOOLBAR, (16,16))
                MenuItem.SetBitmap(save_ico)
                playersMENU.Bind(wx.EVT_MENU, functools.partial(self.interactor.doCbOnPlay,player = playerName), id=MenuItem.GetId())
                playersMENU.AppendItem(MenuItem)
                MenuItem = wx.MenuItem(playersMENU, -1, 'Stop')
                save_ico = wx.ArtProvider.GetBitmap("ART_PLAYER_STOP", wx.ART_TOOLBAR, (16,16))
                MenuItem.SetBitmap(save_ico)
                playersMENU.Bind(wx.EVT_MENU, functools.partial(self.interactor.doCbOnStop,player = playerName), id=MenuItem.GetId())
                playersMENU.AppendItem(MenuItem)
                
                MenuItem = wx.MenuItem(playersMENU, -1, 'Pause')
                save_ico = wx.ArtProvider.GetBitmap("ART_PLAYER_PAUSE", wx.ART_TOOLBAR, (16,16))
                MenuItem.SetBitmap(save_ico)
                playersMENU.Bind(wx.EVT_MENU, functools.partial(self.interactor.doCbOnPause,player = playerName), id=MenuItem.GetId())
                playersMENU.AppendItem(MenuItem)
                MenuItem = wx.MenuItem(playersMENU, -1, 'Next')
                save_ico = wx.ArtProvider.GetBitmap("ART_PLAYER_SEEK_FORWARD", wx.ART_TOOLBAR, (16,16))
                MenuItem.SetBitmap(save_ico)
                playersMENU.Bind(wx.EVT_MENU, functools.partial(self.interactor.doCbOnSeekForward,player = playerName), id=MenuItem.GetId())
                playersMENU.AppendItem(MenuItem)
                MenuItem = wx.MenuItem(playersMENU, -1, 'Previous')
                save_ico = wx.ArtProvider.GetBitmap("ART_PLAYER_SEEK_BACKWARD", wx.ART_TOOLBAR, (16,16))
                MenuItem.SetBitmap(save_ico)
                playersMENU.Bind(wx.EVT_MENU, functools.partial(self.interactor.doCbOnSeekBackwards,player = playerName), id=MenuItem.GetId())
                playersMENU.AppendItem(MenuItem)
                MenuItem = wx.MenuItem(playersMENU, -1, 'Rnd')
                playersMENU.Bind(wx.EVT_MENU, functools.partial(self.interactor.doCbOnRandomSongs,player = playerName), id=MenuItem.GetId())
                playersMENU.AppendItem(MenuItem)
                
            toolsMENU.AppendSeparator()
        create_menu_item(toolsMENU, 'Now Playing',None, self.interactor.doCbOnNowPlaying)
        create_menu_item(toolsMENU, 'Settings',None, self.interactor.doCbOnSettings)
        toolsMENU.AppendSeparator()
        create_menu_item(toolsMENU, 'Exit', wx.ART_QUIT,self.interactor.doCbOnExit)
        return toolsMENU
    
     

