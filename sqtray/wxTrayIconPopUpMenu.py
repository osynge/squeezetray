import wx
from sqtray.models import Observable

import functools

import logging
from sqtray.wxArtPicker import MyArtProvider

def create_menu_item(menu, label, art,func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    if art != None:
        save_ico = wx.ArtProvider.GetBitmap(art, wx.ART_TOOLBAR, (16,16))
        item.SetBitmap(save_ico)
    menu.AppendItem(item)
    return item



def CreatePopupMenu(model,interactor):
    toolsMENU = wx.Menu()
    ConnectionStatus = model.connected.get()
    #ConnectionStatus = False
    if ConnectionStatus:
        
        create_menu_item(toolsMENU, 'Play',"ART_PLAYER_PLAY", interactor.onScPlay)
        create_menu_item(toolsMENU, 'Pause', "ART_PLAYER_PAUSE",interactor.onScPause)
        create_menu_item(toolsMENU, 'Next', "ART_PLAYER_SEEK_FORWARD",interactor.onScNext)
        create_menu_item(toolsMENU, 'Previous', 'ART_PLAYER_SEEK_BACKWARD',interactor.onScPrevious)
        create_menu_item(toolsMENU, 'Rnd', None,interactor.onScRandom)
        toolsMENU.AppendSeparator()
    playersLen = len(model.Players)
    #print "Players=\n%s\n%s" % (model.Players,model.playerList)
    #playersLen = 0
    if playersLen >1:
        playersMENU = wx.Menu()
        toolsMENU.AppendMenu(-1, "Change Player", playersMENU) 
        #player = model.GuiPlayer.get()
        player = None
        if player != None:
            MenuItem = wx.MenuItem(playersMENU, -1, player)
            # Bind event to self.ChangePlayer but add the parameter "player" to the call back, with the value "player"
            playersMENU.Bind(wx.EVT_MENU, functools.partial(interactor.ChangePlayer,player = player), id=MenuItem.GetId())
            playersMENU.AppendItem(MenuItem)
            playersMENU.AppendSeparator()
        for playerName in  model.Players:
            if playerName != player:
                MenuItem = wx.MenuItem(playersMENU, -1, playerName)
                playersMENU.Bind(wx.EVT_MENU, functools.partial(interactor.ChangePlayer,player = playerName), id=MenuItem.GetId())
                playersMENU.AppendItem(MenuItem)

        toolsMENU.AppendSeparator()
    create_menu_item(toolsMENU, 'Settings',None, interactor.on_settings)
    toolsMENU.AppendSeparator()
    create_menu_item(toolsMENU, 'Exit', wx.ART_QUIT,interactor.on_exit)
    return toolsMENU




class PopUpMenuInteractor(object):
    """ http://wiki.wxpython.org/ModelViewPresenter inspired """
    def install(self, presenter, view):
        self.presenter = presenter
        self.view = view
    def onScPlay(self,event):
        self.presenter.onScPlay()
    def onScPause(self,event):
        self.presenter.onScPause()
    def onScNext(self,event):
        self.presenter.onScNext()
    def onScPrevious(self,event):
        self.presenter.onScPrevious()
    def onScRandom(self,event):
        self.presenter.onScRandom()
    def ChangePlayer(self,event,player):
        playerStr = unicode(player)
        self.presenter.ChangePlayer(playerStr)
    def on_settings(self,event):
        self.presenter.on_settings()
    def on_exit(self,event):
        self.presenter.on_exit()




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

class TrayMenuInteractor(object):
    def __init__(self):
        self.callbacks = {
            "on_exit" : {},
            "on_settings" : {},
            "on_play" : {},
            "on_pause" : {},
            "on_stop" : {},
            "on_seek_index" : {},
            "on_random_songs" : {}
        }

    def cbAddOnExit(self,func):
        self.callbacks['on_exit'][func] = 1   
        
    def cbAddOnSettings(self,func):
        self.callbacks['on_settings'][func] = 1
    
    def cbAddOnPlay(self,func):
        self.callbacks['on_play'][func] = 1
    
    def cbAddOnPause(self,func):
        self.callbacks['on_pause'][func] = 1
    def cbAddOnStop(self,func):
        self.callbacks['on_stop'][func] = 1
    
    
    
    def cbAddOnSeekIndex(self,func):
        self.callbacks['on_seek_index'][func] = 1
    
    def cbAddOnRandomSongs(self,func):
        self.callbacks['on_random_songs'][func] = 1
    
    
    def doCbOnExit(self,evt):
        results = {}
        for item in self.callbacks["on_exit"]:
            results[item] = item()
        return results
        
    def doCbOnSettings(self,evt):
        results = {}
        for item in self.callbacks["on_settings"]:
            results[item] = item()
        return results
    
    def doCbOnPlay(self,evt,player):
        results = {}
        for item in self.callbacks["on_play"]:
            results[item] = item(player)
        return results
    def doCbOnStop(self,evt,player):
        results = {}
        for item in self.callbacks["on_stop"]:
            results[item] = item(player)
        return results
    def doCbOnPause(self,evt,player):
        results = {}
        for item in self.callbacks["on_pause"]:
            results[item] = item(player)
        return results
    
    def doCbOnSeekForward(self,evt,player):
        results = {}
        for item in self.callbacks["on_seek_index"]:
            results[item] = item(player,1)
        return results
        
    def doCbOnSeekBackwards(self,evt,player):
        results = {}
        for item in self.callbacks["on_seek_index"]:
            results[item] = item(player,-1)
        return results

    def doCbOnRandomSongs(self,evt,player):
        results = {}
        for item in self.callbacks["on_random_songs"]:
            results[item] = item(player)
        return results




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
        create_menu_item(toolsMENU, 'Settings',None, self.interactor.doCbOnSettings)
        toolsMENU.AppendSeparator()
        create_menu_item(toolsMENU, 'Exit', wx.ART_QUIT,self.interactor.doCbOnExit)
        return toolsMENU
    
     

