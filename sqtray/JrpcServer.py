
import httplib, urllib
import sys, traceback
from threading import *

from Queue import Queue
from threading import Thread

if float(sys.version[:3]) >= 2.6:
    import json
else:
    # python 2.4 or 2.5 can also import simplejson
    # as working alternative to the json included.
    import simplejson as json

class SqueezeConnectionWorker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()
        self.connectionString = None
    def run(self):
        while True:
            func,params, args, kargs = self.tasks.get()
            if not hasattr(self,'conn'):
                self.tasks.task_done()
                return
            if self.connectionString == None:
                self.tasks.task_done()
                return
            try:
                self.conn.request("POST", "/jsonrpc.js", params)
            except socket.error:
                self.tasks.task_done()
                return
            try:
                response = self.conn.getresponse()
            except httplib.BadStatusLine:
                self.conn = httplib.HTTPConnection(self.connectionString)
                self.conn.request("POST", "/jsonrpc.js", params)
                response = self.conn.getresponse()

            if response.status != 200:
                print response.status, response.reason
            #return response.read()
            rep = json.loads(response.read())
            if func != None:
                func(rep,*args, **kargs)
                #try: func(rep)
                #except Exception, e: 
                #    print e
                #    #traceback.print_tb(e, limit=1, file=sys.stdout)
            self.tasks.task_done()
            
            
    def ConnectionSet(self,connectionStr):
        Changed =  False
        if not hasattr(self,'connectionString'):
            Changed =  True
            self.connectionString = connectionStr
        if self.connectionString != connectionStr:
            Changed =  True
            self.connectionString = connectionStr
        if not hasattr(self,'conn'):
            Changed =  True
        if Changed:
            self.conn = httplib.HTTPConnection(connectionStr)
            
        
class SqueezeConnectionThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, squeezeConMdle,num_threads = 10):
        
        self.squeezeConMdle = squeezeConMdle
        
        self.tasks = Queue(num_threads)
        self.arrayOfSqueezeConnectionWorker = []
        for _ in range(num_threads): 
            new = SqueezeConnectionWorker(self.tasks)
            self.arrayOfSqueezeConnectionWorker.append(new)

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()
    def sendMessage(self,func,message, *args, **kargs):
        params = json.dumps(message, sort_keys=True, indent=4)
        self.tasks.put((func,params, args, kargs))
  
        
    def OnConnectionStrChange(self,value):
        oldvalue = self.squeezeConMdle.connectionStr.get()
        for player in range(len(self.arrayOfSqueezeConnectionWorker)):
            self.arrayOfSqueezeConnectionWorker[player].ConnectionSet(oldvalue)
        oldValue = self.squeezeConMdle.connected.get()
        self.squeezeConMdle.connected.set(False)
        
        
    def OnPlayerCount(self,responce):
        noPlayers = int(responce["result"]["_count"])
        self.noPlayers = noPlayers
        #print "self.noPlayers=%s" % ( noPlayers )
        self.squeezeConMdle.connected.set(True)
        oldValue = self.squeezeConMdle.connected.get()
        if oldValue == noPlayers:
            return
        self.squeezeConMdle.playersCount.set(noPlayers)
        oldValue = self.squeezeConMdle.connected.get()
        if oldValue != True:
            self.squeezeConMdle.connected.set(True)
        for index in range(self.noPlayers):            
            msg = { 
                "method":"slim.request",
                "params": [ '-', [ 'player', 'id', index ,"?"] ]
            }
            self.sendMessage(self.OnPlayerIndex,msg)
            msg = { 
                "method":"slim.request",
                "params": [ '-', [ 'player', 'name', index ,"?"] ]
            }
            self.sendMessage(self.OnPlayerName,msg)

    def OnPlayerIndex(self,responce):
        playerId = responce["result"]["_id"]
        playerIndex = int(responce['params'][1][2])
        self.squeezeConMdle.playerList[playerIndex].identifier.set(playerId)
    def OnPlayerName(self,responce):
        playerName = responce["result"]["_name"] 
        playerIndex = int(responce['params'][1][2])
        self.squeezeConMdle.playerList[playerIndex].name.set(playerName)
    def OnPlayerStatus(self,responce):
        #print "OnPlayerStatus:",datetime.datetime.now()
        #print unicode(json.dumps(responce, sort_keys=True, indent=4))
        playerName = unicode(responce["result"]["player_name"])
        playerIndex = int(responce['id'])
        playlist_cur_index = int(responce["result"]["playlist_cur_index"])
        playlist_loop = responce["result"]["playlist_loop"]
        
        lsbsMode = unicode(responce["result"]["mode"])
        mappings = {"play" : "playing",
            "pause" : "paused",
            "off" : "Off"
        }
        OldplayerName = self.squeezeConMdle.playerList[playerIndex].name.get()
        if OldplayerName != playerName:
            self.squeezeConMdle.playerList[playerIndex].name.set(playerName)
        if lsbsMode in mappings:
            self.squeezeConMdle.playerList[playerIndex].operationMode.set(mappings[lsbsMode])
        CurrentTrackTitle = None
        for item in playlist_loop:
            playlistIndex = int(item["playlist index"])
            if playlistIndex == playlist_cur_index:
                CurrentTrackTitle = unicode(item["title"])
                OldCurrentTrackTitle = self.squeezeConMdle.playerList[playerIndex].CurrentTrackTitle.get()
                if CurrentTrackTitle  != OldCurrentTrackTitle:
                    self.squeezeConMdle.playerList[playerIndex].CurrentTrackTitle.set(CurrentTrackTitle)
                    
            
       
class squeezeConCtrl:
    def __init__(self,model):  
        """Controler class for takes a model as a constructor (class squeezeConMdle)"""

        self.model = model
        self.view1 = SqueezeConnectionThreadPool(self.model)
        self.model.connectionStr.addCallback(self.view1.OnConnectionStrChange)
        self.model.CbPlayersAvailableAdd(self._OnPlayersNameChange)
        self.model.connected.addCallback(self.OnConnection)
        self.model.playersCount.addCallback(self.OnPlayersCount)
        self.mapping = {}
        self.CbConnection = []
        self.CbPlayersList = []
    def OnPlayersCount(self,value):
        for i in range(len(self.model.playerList)):
            identifier = self.model.playerList[i].identifier.get()
            name = self.model.playerList[i].name.get()
            if identifier == None:
                print "would make a name request"
    def  RecConnectionOnline(self):
        #self.view1.RecConnectionOnline()
        self.view1.sendMessage(self.view1.OnPlayerCount,{ 
            "method":"slim.request",
            "params": [ '-', [ 'player', 'count', '?' ] ]
        })
    
    def ConectionStringSet(self,Conecxtionstring):
        oldConecxtionstring = self.model.connectionStr.get()
        if oldConecxtionstring != Conecxtionstring:
            self.model.connectionStr.set(Conecxtionstring)
            self.RecConnectionOnline()
            
    def ServerHostSet(self,hostname):
        oldHost = self.model.port.get()
        if oldHost != hostname:
            self.model.host.set(hostname)
            self.RecConnectionOnline()
    def ServerPortSet(self,port):
        oldPort = self.model.port.get()
        if oldPort != port:
            self.model.port.set(port)
            self.RecConnectionOnline()

    def _OnPlayersNameChange(self,value,dfd):
        #print (self,value,dfd)
        playersCount = self.model.playersCount.get()
        for index in range(playersCount):
            #print index
            name = self.model.playerList[index].name.get()
            if None != name:
                self.mapping[ name] =index

    def PlayersList(self):
        self.mapping = {}
        playerList = []
        playersCount = self.model.playersCount.get()
        for index in range(playersCount):
            player = self.model.playerList[index].name.get()
            if player != None:
                playerList.append(player)
                self.mapping[player] = index
        return playerList

    def CbPlayersListAdd(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.CbPlayersList.append((func, args, kargs))

    def CbPlayersLisCbPlayersAvailableAdd(self, func, *args, **kargs):    
        self.model.CbPlayersAvailableAdd(func, args, kargs)

    def CbConnectionAdd(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.CbConnection.append((func, args, kargs))
    def OnConnection(self,value):
        #print "OnConnection(value)=%s" % value
        self.mapping = {}
        for func, args, kargs in self.CbConnection:
            func(value,*args, **kargs)

    def OnPlayersList(self,value):
        #print "OnConnection(value)=%s" % value
        for func, args, kargs in self.CbConnection:
            func(value,*args, **kargs)

    def ConnectionOnline(self):
        return self.model.connected.get()
        
    def RecPlayerStatus(self,player):
        #print "self.mapping,player1"
        if not self.model.connected.get():
            return None
        if not player in self.mapping:
            return None
        #print "self.mapping,player2"
        playerIndex = self.mapping[player]
        playerId = self.model.playerList[playerIndex].identifier.get()
        reponce = self.view1.sendMessage(self.view1.OnPlayerStatus,{ 
            "id":playerIndex,
            "method":"slim.request",
            "params":[ playerId, 
                    ["status","-","4","tags:playlist_id"]
                ]
        })
        
        
        #Eself.view1.sendMessage(self.view1.OnPlayerCount,{ 
        #    "method":"slim.request",
        #    "params": [ '-', [ 'player', 'count', '?' ] ]
        #})
        #self.view1.RecPlayerStatus()        
    def Pause(self,player):
        #print self.mapping,player
        if not self.model.connected.get():
            return None
        if not player in self.mapping:
            return None
        playerIndex = self.mapping[player]
        playerId = self.model.playerList[playerIndex].identifier.get()
        reponce = self.view1.sendMessage(None,{ 
            "id":playerIndex,
            "method":"slim.request",
            "params":[ playerId, 
                    ["pause"]
                ]
        })
    def Play(self,player):
        if not self.model.connected.get():
            return None
        if not player in self.mapping:
            return None
        playerIndex = self.mapping[player]
        playerId = self.model.playerList[playerIndex].identifier.get()
        reponce = self.view1.sendMessage(None,({ 
            "id" : playerIndex,
            "method":"slim.request",
            "params":[ playerId, 
                    ["play"]
                ]
        }))
    def Index(self,player,Count):
        if not self.model.connected.get():
            return None
        if not player in self.mapping:
            return None
        prefix = ""
        if Count > 0:
            prefix = "+"
        playerIndex = self.mapping[player]
        playerId = self.model.playerList[playerIndex].identifier.get()
        reponce = self.view1.sendMessage(None,({ 
            "id":playerIndex,
            "method":"slim.request",
            "params":[ playerId, 
                    ["playlist","index",prefix + unicode(Count)]
                ]
        }))


    def PlayRandomSong(self,player):
        if not self.model.connected.get():
            return None
        if not player in self.mapping:
            return None
        playerIndex = self.mapping[player]
        playerId = self.model.playerList[playerIndex].identifier.get()
        reponce = self.view1.sendMessage(None,({ 
            "id":playerIndex,
            "method":"slim.request",
            "params":[ playerId, 
                    ["randomplay",'tracks']
                ]
            }))
    
    def PlayerStatus(self,player):
        
        if not self.model.connected.get():
            return None
        if not player in self.mapping:
            return None
        playerIndex = self.mapping[player]
        playerId = self.model.playerList[playerIndex].identifier.get()
        reponce = self.view1.sendMessage(self.view1.OnPlayerStatus,({ 
            "id":playerIndex,
            "method":"slim.request",
            "params":[ playerId, 
                    ["status",'-','2','tags']
                ]
            }))
        #print "PlayerStatus:",datetime.datetime.now()
