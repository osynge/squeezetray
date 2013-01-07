import socket
import httplib, urllib
import sys, traceback
from threading import *
from modelsConnection import squeezeSong
import logging
from Queue import Queue
from threading import Thread
import datetime
import time
from models import Observable
import exceptions
if float(sys.version[:3]) >= 2.6:
    import json
else:
    # python 2.4 or 2.5 can also import simplejson
    # as working alternative to the json included.
    import simplejson as json


import errno

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
        self.log = logging.getLogger("JrpcServer.SqueezeConnectionWorker")
        
    def run(self):
        while True:
            func,params, args, kargs = self.tasks.get()
            if not hasattr(self,'conn'):
                #print "connectionString", self.connectionString 
                self.tasks.task_done()
                continue
            if self.connectionString == None:
                self.tasks.task_done()
                continue
            if self.conn == None:
                self.conn = httplib.HTTPConnection(self.connectionString)
            try:
                self.conn.request("POST", "/jsonrpc.js", params)
            except socket.error, E:
                if hasattr(E,'errno'):
                    errorNumber = int(E.errno)
                self.SocketErrNo.set(errorNumber)
                self.SocketErrMsg.set(unicode(E.strerror))
                self.tasks.task_done()
                continue
            except httplib.CannotSendRequest, E:
                self.conn = httplib.HTTPConnection(self.connectionString)
                self.log.error("Cannot Send Request, resetting connection.=%s" % (params))
                self.log.error(self.connectionString)
                self.tasks.task_done()
                continue
            errorNoOld = self.SocketErrNo.get()
            self.SocketErrNo.set(0)
            self.SocketErrMsg.set(unicode(""))
            try:
                response = self.conn.getresponse()
            except exceptions.AttributeError, E:
                self.tasks.task_done()
                continue
            except socket.error, E:
                errorNumber = int(E.errno)
                self.SocketErrNo.set(errorNumber)
                self.SocketErrMsg.set(unicode(E.strerror))
                self.tasks.task_done()
                continue
            except httplib.BadStatusLine:
                self.conn = httplib.HTTPConnection(self.connectionString)
                try:
                    self.conn.request("POST", "/jsonrpc.js", params)
                except EnvironmentError as exc:
                    if exc.errno == errno.ECONNREFUSED:
                        self.log.info( "Connection refused")
                        self.tasks.task_done()
                        continue
                    else:
                        raise exc
                except IOError as E:
                    self.log.info( "IOError error:%s" %(E))
                    self.tasks.task_done()
                    continue
                try:
                    response = self.conn.getresponse()
                except httplib.BadStatusLine, E:
                    self.log.info( "httplib.BadStatusLine exception.message=%s,E=%s" % (E.message,E))
                    self.tasks.task_done()
                    continue
            if response.status != 200:
                self.log.info( "httplib.BadResponceStatus %s:%s" % (response.status, response.reason))
                self.tasks.task_done()
                return
            try:
                rep = json.loads(response.read())
            except ValueError as E:
                self.log.info( "Json decoding ValueError:%s" %(E))
                self.tasks.task_done()
                continue
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
        elif self.conn == None:
            Changed =  True
        if Changed:
            #print connectionStr
            self.conn = httplib.HTTPConnection(connectionStr)
        self.conn == None   
        
class SqueezeConnectionThreadPool:
    """Pool of threads consuming tasks from a queue"""
    
    def __init__(self, squeezeConMdle,num_threads = 10):
        self.log = logging.getLogger("JrpcServer.SqueezeConnectionThreadPool")
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
        self.log.error("Wait for completion of all the tasks in the queue")
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
        self.squeezeConMdle.connected.update(True)
        oldValue = self.squeezeConMdle.connected.get()
        if oldValue == noPlayers:
            return
        self.squeezeConMdle.playersCount.update(noPlayers)
        self.squeezeConMdle.connected.update(True)

    def OnPlayerIndex(self,responce):
        playerId = responce["result"]["_id"]
        playerIndex = int(responce['params'][1][2])
        if len(self.squeezeConMdle.playerList) <= playerIndex:
            self.log.error("Bad message.")
            return
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
        if not( playerIndex < len(self.squeezeConMdle.playerList)):
            self.log.error("Player not found")
            return
        OldplayerName = self.squeezeConMdle.playerList[playerIndex].name.get()
        if OldplayerName != playerName:
            self.squeezeConMdle.playerList[playerIndex].name.set(playerName)
        lsbsMode = unicode(responce["result"]["mode"])
        mappings = {"play" : "playing",
            "pause" : "paused",
            "off" : "Off",
            "stop" : "stop"
        }
        if lsbsMode in mappings:
            newOperationMode = mappings[lsbsMode]
            oldOperationMode = self.squeezeConMdle.playerList[playerIndex].operationMode.get()
            if newOperationMode != oldOperationMode:
                self.squeezeConMdle.playerList[playerIndex].operationMode.set(mappings[lsbsMode])
        else:
            self.log.error("Unknown player mode=%s" % (lsbsMode))
        playlist_cur_index = None
        if not "playlist_cur_index" in responce["result"].keys():
            self.log.debug("Message contained no playlist_cur_index")
            self.log.debug("Message=%s" % responce)
        else:
            playlist_cur_index = int(responce["result"]["playlist_cur_index"])
        playlist_loop = []
        if "playlist_loop" in responce["result"]:
            playlist_loop = responce["result"]["playlist_loop"]
        CurrentTrackTime = None
        if "time" in responce["result"].keys():
            CurrentTrackTime = responce["result"]["time"]
        CurrentTrackTitle = None
        for item in playlist_loop:
            playlistIndex = int(item["playlist index"])
            if playlistIndex == playlist_cur_index:
                CurrentTrackId = int(item["id"])
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
    def OnTrackInfo(self,responce):
        now = datetime.datetime.now()
        #print "OnPlayerStatus:",datetime.datetime.now()
        #print  "OnTrackInfo",responce
        #print "OnTrackInfo",unicode(json.dumps(responce, indent=4))
        
        def cleanList(inputStr):
            inputList = inputStr.split(",")
            outputList = []
            for item in inputList:
                cleanItem = item.strip()
                if len(cleanItem) > 0:
                    outputList.append(cleanItem)
            return outputList
        
        
        identifier = responce["result"]["songinfo_loop"][0][u'id']
        if identifier == 0:
            self.log.error("Invalid song ID")
            return
        newSongInfo = None
        if identifier in self.squeezeConMdle.SongCache.keys():
            newSongInfo = self.squeezeConMdle.SongCache[identifier]
        else:
            newSongInfo = squeezeSong()
        for metadata in  responce["result"]["songinfo_loop"]:
            #print metadata
            for key in metadata:
                #print key
                if key == u'id':
                    newSongInfo.id.update( int(metadata[key]))
                if key == u'title':
                    newSongInfo.title.update(cleanList(metadata[key]))
                if key == u'genres':
                    newSongInfo.genres.update(cleanList(metadata[key]))
                if key == u'artist':
                    newSongInfo.artist.update(cleanList(metadata[key]))
                if key == u'artist_ids':
                    newSongInfo.artist_ids.update(cleanList(metadata[key]))
                    
                if key == u'samplesize':
                    newSongInfo.samplesize.update(cleanList(metadata[key]))
                if key == u'duration':
                    newSongInfo.duration.update(cleanList(metadata[key]))
                if key == u'tracknum':
                    newSongInfo.tracknum.update(cleanList(metadata[key]))
                if key == u'year':
                    newSongInfo.year.update(cleanList(metadata[key]))      
                if key == u'album':
                    newSongInfo.album.update(cleanList(metadata[key]))
                if key == u'album_id':
                    newSongInfo.album_id.update(cleanList(metadata[key]))
                if key == u'duration':
                    newSongInfo.duration.update(cleanList(metadata[key]))   
                if key == u'type':
                    newSongInfo.type.update(cleanList(metadata[key]))
                if key == u'tagversion':
                    newSongInfo.tagversion.update(cleanList(metadata[key]))
                if key == u'bitrate':
                    newSongInfo.bitrate.update(cleanList(metadata[key]))
                if key == u'filesize':
                    newSongInfo.filesize.update(cleanList(metadata[key]))    
                if key == u'coverart':
                    newSongInfo.coverart.update(cleanList(metadata[key]))
                if key == u'modificationTime':
                    newSongInfo.modificationTime.update(cleanList(metadata[key]))
                if key == u'compilation':
                    newSongInfo.compilation.update(cleanList(metadata[key]))
                if key == u'samplerate':
                    newSongInfo.samplerate.update(cleanList(metadata[key])) 
                if key == u'url':
                    newSongInfo.url.update(cleanList(metadata[key]))
        newSongInfo.updated.update(datetime.datetime.now())
        if not identifier in self.squeezeConMdle.SongCache.keys():
            self.squeezeConMdle.SongCache[identifier] = newSongInfo
        
        
        
        
class squeezeConCtrl:
    def __init__(self,model):  
        
        """Controler class for takes a model as a constructor (class squeezeConMdle)"""
        self.log = logging.getLogger("squeezeConCtrl")
        self.model = model
        self.view1 = SqueezeConnectionThreadPool(self.model)
        self.model.connectionStr.addCallback(self.view1.OnConnectionStrChange)
        self.model.CbPlayersAvailableAdd(self.OnPlayersAvailable)
        self.model.connected.addCallback(self.OnConnection)
        self.model.playersCount.addCallback(self.OnPlayersCount)
        self.CbConnection = []
        self.CbPlayersList = []
        self.model.CbChurrentTrackAdd(self.OnTrackChange)
    
    
    def OnPlayersCount(self,value):
        #print "OnPlayersCount", value
        comands = []
        for index in range(len(self.model.playerList)):
            identifier = self.model.playerList[index].identifier.get()
            name = self.model.playerList[index].name.get()
            
            if identifier == None:
                #print "would make a name request"
                msg = { 
                    "method":"slim.request",
                    "params": [ '-', [ 'player', 'id', index ,"?"] ]
                }
                self.log.debug("msg=%s" % (msg))
                comands.append([self.view1.OnPlayerIndex,msg])
                
                #self.view1.sendMessage([self.view1.OnPlayerIndex,msg])
            if name == None:
                #print "would make a name request"
                msg = { 
                    "method":"slim.request",
                    "params": [ '-', [ 'player', 'name', index ,"?"] ]
                }
                comands.append([self.view1.OnPlayerName,msg])
                #self.view1.sendMessage([self.view1.OnPlayerName,msg])
        for item in comands:
            time.sleep(1)
            self.view1.sendMessage(item[0],item[1])
    def RecConnectionOnline(self):
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

    def OnTrackChange(self):
        #print "OnTrackChange"
        
        for player in self.model.Players:
            trackId = self.model.Players[player].CurrentTrackId.get()
            if trackId == None:
                continue
            trackId = int(trackId)
            if trackId <= 0:
                continue
            self.view1.sendMessage(self.view1.OnTrackInfo,{ 
                        "method":"slim.request",
                        "params": ["-",
                            ['songinfo', '0', '100', 'track_id:%s'  % (trackId),"tags:GPlASIediqtymkovrfijnCcYXRTIuwxN"] ]     
                    })
        
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
    
    def Pause(self,player):
        if not self.model.connected.get():
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
    def Stop(self,player):
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
                    ["stop"]
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
            self.log.debug("PlayerStatus")
            return None
        playerlistLen = len(self.model.playerList)
        if not player in range(playerlistLen):
            self.log.debug("PlayerStatus-------------%s" % (self.model.Players))
            return None
        playerIndex = self.model.playerList[player].index.get()
        playerId = self.model.playerList[player].identifier.get()
        reponce = self.view1.sendMessage(self.view1.OnPlayerStatus,({ 
            "id":playerIndex,
            "method":"slim.request",
            "params":[ playerId, 
                    ["status",'-','2','tags']
                ]
            }))
        
