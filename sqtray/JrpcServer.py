import socket
import httplib, urllib
import sys, traceback
from threading import *

from Queue import Queue
from threading import Thread
import datetime

from models import Observable

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
        self.SocketErrNo = Observable(0)
        self.SocketErrMsg = Observable("")
        
    def run(self):
        while True:
            func,params, args, kargs = self.tasks.get()
            if not hasattr(self,'conn'):
                #print "connectionString", self.connectionString 
                self.tasks.task_done()
                return
            if self.connectionString == None:
                self.tasks.task_done()
                return
            try:
                self.conn.request("POST", "/jsonrpc.js", params)
            except socket.error, E:
                #print "socket.error E.errno", E.errno
                
                #print "socket.error ", dir(E)
                errorNumber = int(E.errno)
                self.SocketErrNo.set(errorNumber)
                self.SocketErrMsg.set(unicode(E.strerror))
                    #print "socket.error E.strerror=%s", E.strerror
                self.tasks.task_done()
                return
            errorNoOld = self.SocketErrNo.get()
            self.SocketErrNo.set(0)
            self.SocketErrMsg.set(unicode(""))
            try:
                response = self.conn.getresponse()
            except httplib.BadStatusLine:
                self.conn = httplib.HTTPConnection(self.connectionString)
                self.conn.request("POST", "/jsonrpc.js", params)
                try:
                    response = self.conn.getresponse()
                except httplib.BadStatusLine:
                    self.tasks.task_done()
                    return
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
        #print "connectionStr", connectionStr
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
            #print connectionStr
            self.conn = httplib.HTTPConnection(connectionStr)
            
        
class SqueezeConnectionThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, squeezeConMdle,num_threads = 10):
        
        self.squeezeConMdle = squeezeConMdle
        connectionString = self.squeezeConMdle.connectionStr.get()
        self.tasks = Queue(num_threads)
        self.arrayOfSqueezeConnectionWorker = []
        for _ in range(num_threads): 
            new = SqueezeConnectionWorker(self.tasks)
            new.ConnectionSet(connectionString)
            new.SocketErrNo.addCallback(self.OnSocketErrNo)
            new.SocketErrMsg.addCallback(self.OnSocketErrMsg)
            self.arrayOfSqueezeConnectionWorker.append(new)
        self.squeezeConMdle.connectionStr.addCallback(self.OnConnectionStrChange)
        
    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()
    def sendMessage(self,func,message, *args, **kargs):
        #print "connectionString =" ,  self.squeezeConMdle.connectionStr.get()
        params = json.dumps(message, sort_keys=True, indent=4)
        self.tasks.put((func,params, args, kargs))
    
    def OnSocketErrNo(self,value):
        #print "OnSocketErrNo='%s'" % (value)
        SocketErrNo = self.squeezeConMdle.SocketErrNo.get()
        if SocketErrNo != value:
            #print "OnSocketErrNo from '%s' to '%s'" % (SocketErrNo,value)
            self.squeezeConMdle.SocketErrNo.set(value)        
    
    def OnSocketErrMsg(self,value):
        #print "OnSocketErrMsg='%s'" % (value)
        SocketErrMsg = self.squeezeConMdle.SocketErrMsg.get()
        if SocketErrMsg != value:
            #print "OnSocketErrMsg from '%s' to '%s'" % (SocketErrMsg,value)
            self.squeezeConMdle.SocketErrMsg.set(value)
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

    def OnPlayerIndex(self,responce):
        playerId = responce["result"]["_id"]
        playerIndex = int(responce['params'][1][2])
        OldPlayerId =  self.squeezeConMdle.playerList[playerIndex].identifier.get()
        if OldPlayerId != playerId:
            self.squeezeConMdle.playerList[playerIndex].identifier.set(playerId)
    def OnPlayerName(self,responce):
        #print "OnPlayerName",unicode(json.dumps(responce, sort_keys=True, indent=4))
        playerName = responce["result"]["_name"] 
        playerIndex = int(responce['params'][1][2])
        OldPlayerName = self.squeezeConMdle.playerList[playerIndex].name.get()
        if playerName != OldPlayerName:
            self.squeezeConMdle.playerList[playerIndex].name.set(playerName)
            
    def OnPlayerStatus(self,responce):
        now = datetime.datetime.now()
        #print "OnPlayerStatus:",datetime.datetime.now()
        #print  "OnPlayerStatus",responce
        #print "OnPlayerStatus",unicode(json.dumps(responce, indent=4))
        playerName = unicode(responce["result"]["player_name"])
        playerIndex = int(responce['id'])
        playlist_cur_index = int(responce["result"]["playlist_cur_index"])
        playlist_loop = responce["result"]["playlist_loop"]
        
        CurrentTrackTime = responce["result"]["time"]
        
        lsbsMode = unicode(responce["result"]["mode"])
        mappings = {"play" : "playing",
            "pause" : "paused",
            "off" : "Off"
        }
        OldplayerName = self.squeezeConMdle.playerList[playerIndex].name.get()
        if OldplayerName != playerName:
            self.squeezeConMdle.playerList[playerIndex].name.set(playerName)
        if lsbsMode in mappings:
            newOperationMode = mappings[lsbsMode]
            oldOperationMode = self.squeezeConMdle.playerList[playerIndex].operationMode.get()
            if newOperationMode != oldOperationMode:
                self.squeezeConMdle.playerList[playerIndex].operationMode.set(mappings[lsbsMode])
        CurrentTrackTitle = None
        for item in playlist_loop:
            playlistIndex = int(item["playlist index"])
            if playlistIndex == playlist_cur_index:
                CurrentTrackId = unicode(item["id"])
                CurrentTrackTitle = unicode(item["title"])
                OldCurrentTrackTitle = self.squeezeConMdle.playerList[playerIndex].CurrentTrackTitle.get()
                if CurrentTrackTitle  != OldCurrentTrackTitle:
                    self.squeezeConMdle.playerList[playerIndex].CurrentTrackTitle.set(CurrentTrackTitle)
                try:
                    CurrentTrackArtist = unicode(item["artist"])
                except KeyError:
                    CurrentTrackArtist = None
                OldCurrentTrackArtist = self.squeezeConMdle.playerList[playerIndex].CurrentTrackArtist.get()
                if CurrentTrackArtist  != OldCurrentTrackArtist:
                    self.squeezeConMdle.playerList[playerIndex].CurrentTrackArtist.set(CurrentTrackArtist)
                CurrentTrackDuration = None
                try:
                    CurrentTrackDuration = responce["result"]["duration"]
                except KeyError:
                    pass
                if (CurrentTrackDuration != None) and (self.squeezeConMdle.playerList[playerIndex].operationMode.get() == "playing"):
                    CurrentTrackRemaining = CurrentTrackDuration - CurrentTrackTime
                    CurrentTrackEnds = datetime.datetime.now() + datetime.timedelta(seconds=CurrentTrackRemaining)
                    OldCurrentTrackEnds = self.squeezeConMdle.playerList[playerIndex].CurrentTrackEnds.get()
                    if OldCurrentTrackEnds == None:
                        self.squeezeConMdle.playerList[playerIndex].CurrentTrackEnds.set(CurrentTrackEnds)
                    else:
                        timediff = abs(CurrentTrackEnds - OldCurrentTrackEnds)
                        if timediff.seconds > 0:
                            self.squeezeConMdle.playerList[playerIndex].CurrentTrackEnds.set(CurrentTrackEnds)
                else:
                    if None != self.squeezeConMdle.playerList[playerIndex].CurrentTrackEnds.get():
                        self.squeezeConMdle.playerList[playerIndex].CurrentTrackEnds.set(None)
                # Now Change the ID last so people shoudl call back on this.
                OldCurrentTrackId = self.squeezeConMdle.playerList[playerIndex].CurrentTrackId.get()
                if OldCurrentTrackId != CurrentTrackId:
                    self.squeezeConMdle.playerList[playerIndex].CurrentTrackId.set(CurrentTrackId)
       
class squeezeConCtrl:
    def __init__(self,model):  
        """Controler class for takes a model as a constructor (class squeezeConMdle)"""

        self.model = model
        self.view1 = SqueezeConnectionThreadPool(self.model)
        self.model.connectionStr.addCallback(self.view1.OnConnectionStrChange)
        self.model.CbPlayersAvailableAdd(self.OnPlayersAvailable)
        self.model.connected.addCallback(self.OnConnection)
        self.model.playersCount.addCallback(self.OnPlayersCount)
        self.CbConnection = []
        self.CbPlayersList = []
    def OnPlayersCount(self,value):
        #print "OnPlayersCount", value
        for index in range(len(self.model.playerList)):
            identifier = self.model.playerList[index].identifier.get()
            name = self.model.playerList[index].name.get()
            if identifier == None:
                #print "would make a name request"
                msg = { 
                    "method":"slim.request",
                    "params": [ '-', [ 'player', 'id', index ,"?"] ]
                }
                self.view1.sendMessage(self.view1.OnPlayerIndex,msg)
            if name == None:
                #print "would make a name request"
                msg = { 
                    "method":"slim.request",
                    "params": [ '-', [ 'player', 'name', index ,"?"] ]
                }
                self.view1.sendMessage(self.view1.OnPlayerName,msg)
            
    def  RecConnectionOnline(self):
        #print "sdfdsfsF"
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

    def OnPlayersAvailable(self):
        #print "OnPlayersAvailable",value,dfd
        #playersCount = self.model.playersCount.get()
        AllPlayers = list (self.model.Players)
        for player in AllPlayers:
            CurrentTrackId = self.model.Players[player].CurrentTrackId.get()
            if None == CurrentTrackId:
                self.RecPlayerStatus(player)
        
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
        for func, args, kargs in self.CbConnection:
            func(value,*args, **kargs)

    def OnPlayersList(self,value):
        #print "OnConnection(value)=%s" % value
        for func, args, kargs in self.CbConnection:
            func(value,*args, **kargs)

    def ConnectionOnline(self):
        return self.model.connected.get()
        
    def RecPlayerStatus(self,player):
        if not self.model.connected.get():
            return None
        if not player in self.model.Players:
            return None
        playerIndex = self.model.Players[player].index.get()
        playerId = self.model.Players[player].identifier.get()
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
        if not self.model.connected.get():
            print "connectionStr=",self.model.connectionStr.get()
            return None
        if not player in self.model.Players:
            return None
        playerIndex = self.model.Players[player].index.get()
        playerId = self.model.Players[player].identifier.get()
        reponce = self.view1.sendMessage(None,{ 
            "id":playerIndex,
            "method":"slim.request",
            "params":[ playerId, 
                    ["pause"]
                ]
        })
        #print " sent Pays",playerIndex,playerId

    def Play(self,player):
        if not self.model.connected.get():
            return None
        if not player in self.model.Players:
            return None
        playerIndex = self.model.Players[player].index.get()
        playerId = self.model.Players[player].identifier.get()
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
        prefix = ""
        if Count > 0:
            prefix = "+"
        if not player in self.model.Players:
            return None
        playerIndex = self.model.Players[player].index.get()
        playerId = self.model.Players[player].identifier.get()
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
        if not player in self.model.Players:
            return None
        playerIndex = self.model.Players[player].index.get()
        playerId = self.model.Players[player].identifier.get()
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
        if not player in self.model.Players:
            return None
        playerIndex = self.model.Players[player].index.get()
        playerId = self.model.Players[player].identifier.get()
        reponce = self.view1.sendMessage(self.view1.OnPlayerStatus,({ 
            "id":playerIndex,
            "method":"slim.request",
            "params":[ playerId, 
                    ["status",'-','2','tags']
                ]
            }))
        #print "PlayerStatus:",datetime.datetime.now()
