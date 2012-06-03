import wx
import time

import httplib, urllib
import sys
import socket
# simplejson is included with Python 2.6 and above
# with the name json
if float(sys.version[:3]) >= 2.6:
    import json
else:
    # python 2.4 or 2.5 can also import simplejson
    # as working alternative to the json included.
    import simplejson as json
TRAY_TOOLTIP = 'System Tray Demo'
TRAY_ICON = 'icon.png'

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item




class squeezecmd:
    def __init__(self):
        self.conn = httplib.HTTPConnection("mini.yokel.org:9000")
        self.player = 1
        self.playerid = "00:04:20:23:52:7c"
        self.connected = False
    def SetSqueezeServerHost(self, Host):
        changed = False
        if not hasattr(self,'Host'):
            self.Host = Host
            changed = True
        else:
            if self.Host != Host:
                changed = True
                self.Host = Host
        if changed:
            self.OnHostChange()
    def GetSqueezeServerHost(self):
        if not hasattr(self,'Host'):
            return 'localhost'
        else:
            return self.Host
    def SetSqueezeServerPort(self, Port):
        changed = False
        if not hasattr(self,'Port'):
            self.Port = Port
            changed = True
        else:
            if self.Port != Port:
                changed = True
                self.Port = Port
        if changed:
            self.OnHostChange()

    def GetSqueezeServerPort(self):
        if not hasattr(self,'host'):
            return '9000'
        else:
            return self.Port
    def OnHostChange(self):
        Changed = False
        constr = "%s:%s" % (self.GetSqueezeServerHost(),self.GetSqueezeServerPort())
        #print constr
        if not hasattr(self,'_constr'):
            self._constr = constr
            Changed = True
        if self._constr != constr:
            Changed = True
            self._constr = constr
        if not Changed:
            return
        #print "here"
        if hasattr(self,'players'):
            del(self.players)
        self.conn = httplib.HTTPConnection(self._constr)
        reponce = self.sendmsg({ 
            "method":"slim.request",
            "params": [ '-', [ 'player', 'count', '?' ] ]
        })
        if reponce == None:
            return
        rep = json.loads(reponce)
        players = {}
        self.noPlayers = rep["result"]["_count"]
        for index in range(self.noPlayers):
            reponce = self.sendmsg({ 
                "method":"slim.request",
                "params": [ '-', [ 'player', 'id', index ,"?"] ]
            })
            rep = json.loads(reponce)
            playerId = rep["result"]["_id"]
            reponce = self.sendmsg({ 
                "method":"slim.request",
                "params": [ '-', [ 'player', 'name', index ,"?"] ]
            })
            rep = json.loads(reponce)
            playerName = rep["result"]["_name"]
            playerDetails = {"name" : playerName,
                "id" : playerId,
                "index" : index }
            players[playerName] = playerDetails
        self.players = players
        self.connected = True
        return
    def GetSqueezeServerPlayers(self):
        if  hasattr(self,'players'):
            return self.players.keys()
        return []
    def hasPlayer(self,player):
        if not player in self.GetSqueezeServerPlayers():
            return False
        return True
    
    def sendmsg(self,msg):
        params = json.dumps(msg, sort_keys=True, indent=4)
        try:
            self.conn.request("POST", "/jsonrpc.js", params)
        except socket.error:
            return
        try:
            response = self.conn.getresponse()
        except httplib.BadStatusLine:
            self.conn = httplib.HTTPConnection("mini.yokel.org:9000")
            self.conn.request("POST", "/jsonrpc.js", params)
            response = self.conn.getresponse()
        if response.status != 200:
            print response.status, response.reason
        return response.read()
    def squeezecmd_play(self):
        reponce = self.sendmsg({ 
            "id":self.player,
            "method":"slim.request",
            "params":[ self.playerid, 
                    ["play"]
                ]
        })
        
        
    def squeezecmd_pause(self,player):
        if not self.hasPlayer(player):
            return None
        playerIndex = self.players[player]["index"]
        playerId =self.players[player]["id"]
        reponce = self.sendmsg({ 
            "id":playerIndex,
            "method":"slim.request",
            "params":[ playerId, 
                    ["pause"]
                ]
        })
    def squeezecmd_randomplay(self,player):
        playerIndex = self.players[player]["index"]
        playerId =self.players[player]["id"]
        reponce = self.sendmsg({ 
            "id":self.player,
            "method":"slim.request",
            "params":[ self.playerid, 
                    ["randomplay",'tracks']
                ]
            })
    def squeezecmd_Index(self,player,Count):
        """Jumps player on currentplaylist"""
        prefix = ""
        if Count > 0:
            prefix = "+"
        reponce = self.sendmsg({ 
            "id":self.player,
            "method":"slim.request",
            "params":[ self.playerid, 
                    ["playlist","index",prefix + str(Count)]
                ]
        })

class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self,sc):
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        
        self.Bind(wx.EVT_TASKBAR_MOVE, self.on_move)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_TASKBAR_LEFT_UP, self.on_left_up )
        #self.Bind(wx.EVT_TASKBAR_RIGHT_DOWN, self.on_right_down )
        #self.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.on_right_up )
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.on_left_dclick)
        self.Bind(wx.EVT_TASKBAR_RIGHT_DCLICK, self.on_right_dclick)
        #self.Bind(wx.EVT_TASKBAR_CLICK, self.on_click )
        self.squeezecmd = sc
        self.Example = None
    def GetSqueezeServerPlayer(self):
        if not hasattr(self,'app'):
            return None
        return self.app.GetSqueezeServerPlayer()
    def OnShowPopup(self, event):
        pos = wx.GetMousePosition()
        #pos = event.GetPosition()
        
        
        
        #pos = self.panel.ScreenToClient(pos)

    
    def CreatePopupMenu(self):
        toolsMENU = wx.Menu()
        create_menu_item(toolsMENU, 'Pause', self.onScPause)
        create_menu_item(toolsMENU, 'Next', self.onScNext)
        create_menu_item(toolsMENU, 'Previous', self.onScPrevious)
        create_menu_item(toolsMENU, 'Rnd', self.onScRandom)
        #machinesMENU = wx.Menu() 
        
        #moldsMENU = wx.Menu() 
        #toolsMENU.AppendMenu(-1, "Command", machinesMENU) 
        
        
        #toolsMENU.AppendMenu(-1, "Molds", moldsMENU) 

        #create_menu_item(moldsMENU, 'Say Hello', self.on_hello)
        toolsMENU.AppendSeparator()
        create_menu_item(toolsMENU, 'Settings', self.on_settings)
        toolsMENU.AppendSeparator()
        create_menu_item(toolsMENU, 'Exit', self.on_exit)
        return toolsMENU
    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)
    def on_move(self, event):
        #print 'on_move'
        pass
        
        #print self.ScreenToClient(wx.GetMousePosition())
    def on_left_up(self, event):
        #print 'on_left_up'
        pass
    
    def on_right_down(self, event):
        #print 'on_right_down'
        pass
    def on_right_up(self, event):
        #print 'on_right_up'
        menu = self.CreatePopupMenu()
        #print dir (menu)
    def on_right_dclick(self, event):
        #print 'on_right_dclick'
        self.frame.PopupMenu( menu, event.GetPoint() )
    def on_click(self, event):
        #print 'on_click'
        pass
    
    def on_left_down(self, event):
        #print 'Tray icon was left-clicked.'
        pass
    def on_left_dclick(self, event):
        #print 'Tray icon was on_left_dclick-clicked.'
        self.set_icon('gnomedecor1.png')
        self.OnShowPopup( event)
    def on_hello(self, event):
        print 'Hello, world!'
    def on_exit(self, event):
        self.on_settings_close(event)
        wx.CallAfter(self.Destroy)
    def onScPause(self, event):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            self.squeezecmd.squeezecmd_pause(player)
        else:
            self.on_settings(event)
    def onScNext(self, event):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            self.squeezecmd.squeezecmd_Index(player,1)
        else:
            self.on_settings(event)
    def onScPrevious(self, event):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            self.squeezecmd.squeezecmd_Index(player,-1)
        else:
            self.on_settings(event)
    def onScRandom(self, event):
        player = self.GetSqueezeServerPlayer()
        if player != None:
            self.squeezecmd.squeezecmd_randomplay(player)
        else:
            self.on_settings(event)


    def on_settings(self, event):
        if (self.Example == None):
            self.Example = Example(None, title='Settings')
            self.Example.Bind(wx.EVT_CLOSE, self.on_settings_close)
            self.Example.cfg = self.cfg
            self.Example.app = self.app
            self.Example.Show()
    def on_settings_close(self, event):
        if (self.Example != None):
            self.Example.Destroy()
            self.Example = None
        
class Example(wx.Frame):
  
    def __init__(self, parent,  title):
        
        self.parent = parent
        self.title = title
        w, h = (250, 250)
        wx.Frame.__init__(self, self.parent, -1, self.title, wx.DefaultPosition, wx.Size(w, h))
        self.sizer = wx.GridBagSizer(8, 3)
        
        
        self.BtnApply = wx.Button(self,-1, "Apply")
        self.BtnCancel = wx.Button(self,-1, "Cancel")
        self.BtnSave = wx.Button(self,-1, "Save")
        
        self.Bind(wx.EVT_BUTTON, self.OnSave,id=self.BtnSave.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=self.BtnCancel.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnSave,id=self.BtnSave.GetId())
        
        
        
        
        self.sizer.Add(self.BtnApply, (8, 0), wx.DefaultSpan, wx.EXPAND)
        self.sizer.Add(self.BtnCancel, (8, 1), wx.DefaultSpan, wx.EXPAND)
        self.sizer.Add(self.BtnSave, (8, 2), wx.DefaultSpan, wx.EXPAND)
        
        label1 = wx.StaticText(self, -1, 'Host:')
        
        self.sizer.Add(label1, (0, 0), wx.DefaultSpan, wx.EXPAND)
        
        self.tcHost = wx.TextCtrl(self, -1 )
        self.sizer.Add(self.tcHost , (0, 1), (1,2), wx.EXPAND)
        label2 = wx.StaticText(self, -1, 'Port:')
        
        
        self.sizer.Add(label2, (1, 0), wx.DefaultSpan, wx.EXPAND)
        label3 = wx.StaticText(self, -1, 'Player:')
        
        self.sizer.Add(label3, (2, 0), wx.DefaultSpan, wx.EXPAND)
        
        self.scPort = wx.SpinCtrl(self, -1, str(9000),  min=1, max=99999)
        self.sizer.Add(self.scPort, (1, 1),wx.DefaultSpan, wx.EXPAND)
        #self.statusbar = self.CreateStatusBar()
        #self.sizer.Add(self.statusbar, (9, 0),(2,9), wx.EXPAND)
        
        self.cbPlayer = wx.ComboBox(self, -1, style=wx.CB_READONLY)
        self.sizer.Add(self.cbPlayer, (2, 1), (1,2), wx.EXPAND)
        
        
        self.sizer.AddGrowableRow(8)
        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableCol(1)
        self.sizer.AddGrowableCol(2)
        
        self.SetSizerAndFit(self.sizer)
    
    def Show(self):
        self.OnUpdate()
        
        self.tcHost.SetValue(self.app.GetSqueezeServerHost())
        self.scPort.SetValue(self.app.GetSqueezeServerPort())
        
        self.Centre()
        #self.SetSize(wx.Size(w, h))
        super(Example, self).Show()

    def OnUpdate(self):
        
        self.cbPlayer.Clear()
        
        availablePlayers = self.app.ConMan.GetSqueezeServerPlayers()
        
        for player in availablePlayers:
            self.cbPlayer.Append(player)
        if len(availablePlayers) > 0:
            CurrentPlayer = self.app.GetSqueezeServerPlayer()
            playerIndex = 0
            if CurrentPlayer != None:
                try:
                    playerIndex = availablePlayers.index(CurrentPlayer)
                except:
                    playerIndex = 0
            self.cbPlayer.SetSelection(playerIndex)
        
    def OnSave(self, event):
        self.OnApply(event)
        self.app.configSave()

    def OnApply(self, event):
        self.app.SetSqueezeServerHost(self.tcHost.GetValue())
        self.app.SetSqueezeServerPort(int(self.scPort.GetValue()))
        self.app.SetSqueezeServerPlayer(self.cbPlayer.GetValue())
        self.OnUpdate()
    def OnCancel(self, event):
        self.app.tb.on_settings_close(event)
        

class myapp(wx.App):
    def __init__(self):
        super(myapp, self).__init__()
        
        
        self.SqueezeServerPort = None
        self.cfg = wx.FileConfig(appName="ApplicationName", 
                                    vendorName="VendorName", 
                                    localFilename=".squeezetray.cfg", 
                                    style=wx.CONFIG_USE_LOCAL_FILE)
        self.configRead()
        self.ConMan = squeezecmd()
        self.ConMan.SetSqueezeServerHost(self.GetSqueezeServerHost())
        self.ConMan.SetSqueezeServerPort(self.GetSqueezeServerPort())
        
        
        self.tb = TaskBarIcon(self.ConMan)
        self.tb.app = self
         
        
        self.tb.cfg = self.cfg
    def configRead(self):
        squeezeServerHost = 'localhost'
        if self.cfg.Exists('squeezeServerHost'):
            squeezeServerHost = self.cfg.Read('squeezeServerHost')
        self.SetSqueezeServerHost(squeezeServerHost)
        squeezeServerPort = 9000
        if self.cfg.Exists('squeezeServerPort'):
            try:
                squeezeServerPortTmp = int(self.cfg.ReadInt('squeezeServerPort'))
            except ValueError:
                squeezeServerPort = 9000
        self.SetSqueezeServerPort(9000)
        SqueezeServerPlayer = None
        if self.cfg.Exists('SqueezeServerPlayer'):
            SqueezeServerPlayer = self.cfg.Read('SqueezeServerPlayer')
        self.SetSqueezeServerPlayer(SqueezeServerPlayer)
    def configSave(self):
        self.cfg.Write("squeezeServerHost", self.GetSqueezeServerHost())
        self.cfg.WriteInt("squeezeServerPort", self.GetSqueezeServerPort())
        self.cfg.Write("SqueezeServerPlayer", self.GetSqueezeServerPlayer())
        self.cfg.Flush()
    def SetSqueezeServerHost(self,host):
        Changed = False
        if not hasattr(self,'SqueezeServerHost'):
            Changed = True
            self.SqueezeServerHost = 'localhost'
        if self.SqueezeServerHost != host:
            Changed = True
        try:
            self.SqueezeServerHost = str(host)
        except TypeError:
            self.SqueezeServerHost = 'localhost'
        if hasattr(self,'ConMan'):
            self.ConMan.SetSqueezeServerHost(self.SqueezeServerHost)
    def GetSqueezeServerHost(self):
        if hasattr(self,'SqueezeServerHost'):
            return self.SqueezeServerHost
        return 'localhost'
        
        
    def SetSqueezeServerPort(self,port):
        Changed = False
        if not hasattr(self,'SqueezeServerPort'):
            Changed = True
            self.SqueezeServerPort = 9000
        if self.SqueezeServerPort != port:
            Changed = True
            try:
                self.SqueezeServerPort = int(port)
            except TypeError:
                squeezeServerPort = 9000
        if hasattr(self,'ConMan'):
            self.ConMan.SetSqueezeServerPort(self.SqueezeServerPort)
    def GetSqueezeServerPort(self):
        if hasattr(self,'SqueezeServerHost'):
            return self.SqueezeServerPort
        return 9000
    def SetSqueezeServerPlayer(self,player):
        self.SqueezeServerPlayer = player
        
    def GetSqueezeServerPlayer(self):
        if hasattr(self,'SqueezeServerPlayer'):
            return self.SqueezeServerPlayer
        return None
    
        
    
        
def main():
    app = myapp()
    app.MainLoop()

if __name__ == '__main__':
    main()
