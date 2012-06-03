import wx
import time

import httplib, urllib
import sys
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
        self.parameters = {'randomplay' : ['tracks']}
        self.conn = httplib.HTTPConnection("mini.yokel.org:9000")
        self.player = 1
        self.playerid = "00:04:20:23:52:7c"
        
    def sendmsg(self,msg):
        params = json.dumps(msg, sort_keys=True, indent=4)
        print params
        self.conn.request("POST", "/jsonrpc.js", params)
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
        
        
    def squeezecmd_pause(self):
        
        reponce = self.sendmsg({ 
            "id":self.player,
            "method":"slim.request",
            "params":[ self.playerid, 
                    ["pause"]
                ]
        })
    def squeezecmd_randomplay(self):
        
        reponce = self.sendmsg({ 
            "id":self.player,
            "method":"slim.request",
            "params":[ self.playerid, 
                    ["randomplay",self.parameters['randomplay'][0]]
                ]
        })
    def squeezecmd_Next(self):
        
        reponce = self.sendmsg({ 
            "id":self.player,
            "method":"slim.request",
            "params":[ self.playerid, 
                    ["playlist","index","+1"]
                ]
        })
    def squeezecmd_Index(self,Count):
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

    def CreatePopupMenu_orig(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Say Hello', self.on_hello)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu
    
    def OnShowPopup(self, event):
        print dir(event)
        pos = wx.GetMousePosition()
        #pos = event.GetPosition()
        
        
        
        #pos = self.panel.ScreenToClient(pos)
        print dir (self)
    
    def CreatePopupMenu(self):
        toolsMENU = wx.Menu()
        create_menu_item(toolsMENU, 'Pause', self.onScPause)
        create_menu_item(toolsMENU, 'Next', self.onScNext)
        create_menu_item(toolsMENU, 'Previous', self.onScPrevious)
        create_menu_item(toolsMENU, 'Rnd', self.onScRandom)
        machinesMENU = wx.Menu() 
        materialsMENU = wx.Menu() 
        moldsMENU = wx.Menu() 
        toolsMENU.AppendMenu(-1, "Command", machinesMENU) 
        
        toolsMENU.AppendMenu(-1, "Setting", materialsMENU) 
        toolsMENU.AppendMenu(-1, "Molds", moldsMENU) 

        
        
        
        create_menu_item(moldsMENU, 'Say Hello', self.on_hello)
        moldsMENU.AppendSeparator()
        create_menu_item(moldsMENU, 'Exit', self.on_exit)
        return toolsMENU
    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)
    def on_move(self, event):
        #print 'on_move'
        pass
    def on_left_up(self, event):
        print 'on_left_up'
    
    def on_right_down(self, event):
        print 'on_right_down'
    
    def on_right_up(self, event):
        print 'on_right_up'
        menu = self.CreatePopupMenu()
        print dir (menu)
    def on_right_dclick(self, event):
        print 'on_right_dclick'
        self.frame.PopupMenu( menu, event.GetPoint() )
    def on_click(self, event):
        print 'on_click'
    
    def on_left_down(self, event):
        print 'Tray icon was left-clicked.'
    def on_left_dclick(self, event):
        print 'Tray icon was on_left_dclick-clicked.'
        self.set_icon('gnomedecor1.png')
        self.OnShowPopup( event)
    def on_hello(self, event):
        print 'Hello, world!'
    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
    def onScPause(self, event):
        self.squeezecmd.squeezecmd_pause()
    def onScNext(self, event):
        self.squeezecmd.squeezecmd_Index(1)
    def onScPrevious(self, event):
        self.squeezecmd.squeezecmd_Index(-1)
    def onScRandom(self, event):
        self.squeezecmd.squeezecmd_randomplay()
def main():
    app = wx.PySimpleApp()
    sc = squeezecmd()
    TaskBarIcon(sc)
    app.MainLoop()

if __name__ == '__main__':
    main()
