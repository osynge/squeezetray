import logging
import datetime
from datetime import timedelta

from models import Observable
import sys
from jrpcServerView import SqueezeConnectionModelUpdator
from modelsConnection import squeezeSong,  squeezePlayerMdl, squeezeConMdle

if float(sys.version[:3]) >= 2.6:
    import json
else:
    # python 2.4 or 2.5 can also import simplejson
    # as working alternative to the json included.
    import simplejson as json



class poller:
    def __init__(self,model,view):
        self.log = logging.getLogger("poller")
        self.model = model
        self.Pollfrequancy = Observable(60)
        self.PollNext = Observable(datetime.datetime.now())
        self.view = view
    def isDue(self):
        lastPolled = self.PollNext.get()
        now = datetime.datetime.now()
        if now > lastPolled:
            return True
        return False
    def handleResponce(self,responce,ding,dong,foo):
        self.log.error('Programing error this methd shoudl be overridern')

    def wrapOutput(self,listcommands):
        now = datetime.datetime.now()
        pollfrequancy = self.Pollfrequancy.get()
        next = now + datetime.timedelta(seconds=pollfrequancy)
        self.PollNext.update(next)
        
        output = []
        for command in listcommands:
            seconds, message = command
            msg = json.dumps(message, sort_keys=True, indent=4)
            #print 'seconds, msg' ,seconds, msg 
            next = now + datetime.timedelta(seconds=seconds)
            diction = {
                'dueDate' : next,
                'msg' : msg
            } 
            output.append(diction)
        
        
        return output

class pollOnline(poller):
    def __init__(self,model,view):
        poller.__init__(self,model,view)
        self.Pollfrequancy.update(1)
    
    def GetNextDue(self):
        online = self.model.connected.get()
        msg = { 
            "method":"slim.request",
            "params": [ '-', [ 'player', 'count', '?' ] ]
        }
        if online == True:
            return self.wrapOutput([(500,msg)])
        else:
            return self.wrapOutput([(-10,msg)])

    def handleResponce(self,responce,ding,dong,foo):
        noPlayers = int(responce["result"]["_count"])
        self.noPlayers = noPlayers
        #print "self.noPlayers=%s" % ( noPlayers )
        self.model.connected.update(True)
        self.model.playersCount.update(noPlayers)
        



class pollPlayerName(poller):
    def __init__(self,model,view):
        poller.__init__(self,model,view)
        self.model.connected.addCallback(self.onConnected)
    
    def onConnected(self,event):
        self.log.error('sheduling update')
        now = datetime.datetime.now()
        self.PollNext.update(now)
    
    def GetNextDue(self):
        
        online = self.model.connected.get()
        if online != True:
            self.Pollfrequancy.update(60)
            return []
        
        secondDelay = 0
        secondInterval = 1
        commands = []
        for index in range(len(self.model.playerList)):
            identifier = self.model.playerList[index].identifier.get()
            name = self.model.playerList[index].name.get()
            if identifier == None:
                #print "would make a name request"
                msg = { 
                    "method":"slim.request",
                    "params": [ '-', [ 'player', 'id', index ,"?"] ]
                }
                secondDelay += secondInterval
                commands.append([secondDelay,msg])
                
                #self.view1.sendMessage([self.view1.OnPlayerIndex,msg])
            if name == None:
                #print "would make a name request"
                msg = { 
                    "method":"slim.request",
                    "params": [ '-', [ 'player', 'name', index ,"?"] ]
                }
                secondDelay += secondInterval
                commands.append([secondDelay,msg])
        if len(commands) > 0:
            
            self.Pollfrequancy.update(4)
            output = self.wrapOutput( commands)
            self.log.debug("msg=%s" % (output))
                
            
            return output
        secondDelay = 60
        secondInterval = 60
        for index in range(len(self.model.playerList)):
            msg = { 
                "method":"slim.request",
                "params": [ '-', [ 'player', 'id', index ,"?"] ]
            }
            
            secondDelay += secondInterval
            commands.append([secondDelay,msg])
            #print "would make a name request"
            msg = { 
                "method":"slim.request",
                "params": [ '-', [ 'player', 'name', index ,"?"] ]
            }
            secondDelay += secondInterval
            commands.append([secondDelay,msg])
        self.Pollfrequancy.update(60)
        output = self.wrapOutput( commands)
        self.log.debug("msg=%s" % (output))
        return output
    def handleResponce(self,responce,ding,dong,foo):
        playerIndex = int(responce['params'][1][2])
        if "_name" in responce["result"].keys():
            playerName = responce["result"]["_name"] 
            self.model.playerList[playerIndex].name.update(playerName)
        if "_id" in responce["result"].keys():
            playerId = responce["result"]["_id"] 
            self.model.playerList[playerIndex].identifier.set(playerId)

class pollPlayerStatus(poller):
    def __init__(self,model,view):
        poller.__init__(self,model,view)
    def GetNextDue(self):
        online = self.model.connected.get()
        if online != True:
            self.Pollfrequancy.update(6)
            return []
        secondDelay = 0
        secondInterval = 1
        commands = []
        for index in range(len(self.model.playerList)):
            identifier = self.model.playerList[index].identifier.get() 
            if identifier == None:
                continue
            msg = {"id":index,
                    "method":"slim.request",
                    "params":[identifier , 
                            ["status","-","4","tags:playlist_id"]
                        ]
                }
            secondDelay += secondInterval
            commands.append([secondDelay,msg])
        if len(commands) > 0:
            self.Pollfrequancy.update(1)
        output = self.wrapOutput( commands)
        self.log.debug("msg=%s" % (output))
        return output
    def handleResponce(self,responce,ding,dong,foo):
        print json.dumps(responce, sort_keys=True, indent=4)
        playerId = responce['params'][0]
        playerMode = responce['result']['mode']
        playerConnected = responce['result']["player_connected"]
        playerPower = responce['result']["power"]
        
        
        now = datetime.datetime.now()
        #print "OnPlayerStatus:",datetime.datetime.now()
        #print  "OnPlayerStatus",responce
        #print "OnPlayerStatus",unicode(json.dumps(responce, indent=4))
        playerName = unicode(responce["result"]["player_name"])
        playerIndex = int(responce['id'])
        if not( playerIndex < len(self.model.playerList)):
            self.log.error("Player not found")
            return
        self.model.playerList[playerIndex].name.update(playerName)
        lsbsMode = unicode(responce["result"]["mode"])
        mappings = {"play" : "playing",
            "pause" : "paused",
            "off" : "Off",
            "stop" : "stop"
        }
        if lsbsMode in mappings:
            newOperationMode = mappings[lsbsMode]
            self.model.playerList[playerIndex].operationMode.update(mappings[lsbsMode])
        else:
            self.log.error("Unknown player mode=%s" % (lsbsMode))
        playlist_cur_index = None
        if not "playlist_cur_index" in responce["result"].keys():
            self.log.debug("Message contained no playlist_cur_index")
            self.log.debug("Message=%s" % responce)
            self.model.playerList[playerIndex].CurrentTrackTitle.update(None)
            self.model.playerList[playerIndex].CurrentTrackId.update(None)
            self.model.playerList[playerIndex].CurrentTrackArtist.update(None)
            self.model.playerList[playerIndex].CurrentTrackEnds.update(None)
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
            CurrentTrackId = int(item["id"])
            CurrentTrackTitle = None
            if "title" in item.keys():
                CurrentTrackTitle = unicode(item["title"])
            CurrentTrackArtist = None
            if "artist" in item.keys():
                CurrentTrackArtist = unicode(item["artist"])            
            if playlistIndex == playlist_cur_index:
                self.model.playerList[playerIndex].CurrentTrackTitle.update(CurrentTrackTitle)
                
                self.model.playerList[playerIndex].CurrentTrackArtist.update(CurrentTrackArtist)
                CurrentTrackDuration = None
                try:
                    CurrentTrackDuration = responce["result"]["duration"]
                except KeyError:
                    pass
                if (CurrentTrackDuration != None) and (self.model.playerList[playerIndex].operationMode.get() == "playing"):
                    CurrentTrackRemaining = CurrentTrackDuration - CurrentTrackTime
                    CurrentTrackEnds = datetime.datetime.now() + datetime.timedelta(seconds=CurrentTrackRemaining)
                    OldCurrentTrackEnds = self.model.playerList[playerIndex].CurrentTrackEnds.get()
                    if OldCurrentTrackEnds == None:
                        self.model.playerList[playerIndex].CurrentTrackEnds.set(CurrentTrackEnds)
                    else:
                        timediff = abs(CurrentTrackEnds - OldCurrentTrackEnds)
                        if timediff.seconds > 0:
                            self.model.playerList[playerIndex].CurrentTrackEnds.update(CurrentTrackEnds)
                else:
                    self.model.playerList[playerIndex].CurrentTrackEnds.update(None)
                # Now Change the ID last so people shoudl call back on this.
                self.model.playerList[playerIndex].CurrentTrackId.update(CurrentTrackId)
            #Now we process each song
            if not CurrentTrackId in self.model.SongCache.keys():
                
                newSong = squeezeSong()
                newSong.id.update(CurrentTrackId)
                newSong.title.update(CurrentTrackTitle)
                newSong.artist.update(CurrentTrackArtist)
                self.model.SongCache[CurrentTrackId] = newSong
        print (self.model.SongCache.keys())
class pollholder:
    def __init__(self, model,view,updator):
        self.log = logging.getLogger("pollholder")
    
        self.model = model
        self.view = view
        self.updator = updator
        self.polls = []
        item = pollOnline(self.model,self.updator )
        self.polls.append(item)
        item = pollPlayerName(self.model,self.updator)
        self.polls.append(item)
        item = pollPlayerStatus(self.model,self.updator)
        self.polls.append(item)
    def check(self):
        for item in self.polls:
            isdue = item.isDue()
            if isdue != True:
                #self.log.debug('not due')
                continue
            duelist = item.GetNextDue()
            for ting in duelist:
                dueOn = ting['dueDate']
                msg = ting['msg']
                self.view.update(dueOn, msg,item)
        

        
        
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
            self.view1.queueMessage(self.view1.OnTrackInfo,{ 
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
        


class schedular:
    def __init__(self,threadpool):
        self.jobsById = {}
        self.log = logging.getLogger("schedular")
        self.threadpool = threadpool
    def update(self,duedate,message,poller):
        msghash = message.__hash__()
        if msghash in self.jobsById.keys():
            if duedate < self.jobsById[msghash]['duedate']:
                self.jobsById[msghash]['duedate'] = duedate
        else:
            details = {'uuid' : msghash,
                'duedate' : duedate,
                'msg' : message,
                'poller' : poller}
            self.jobsById[msghash] = details
    def Overdue(self):
        overduelist = []
        keys2check = self.jobsById.keys()
        now = datetime.datetime.now()
        results = {}
        for key in keys2check:
            metadata = self.jobsById[key]
            if now > metadata['duedate']:
                self.log.debug('overdue')
                del self.jobsById[key]
                #Make sure on next polling it responds
                metadata['poller'].PollNext.update(now)
                results[key] =  metadata
                #self.log.debug ('%s:%s:%s:%s' % (metadata['poller'].handleResponce,
                #    metadata['msg'],[],{}
                #    ))
                self.threadpool.QueueProcessAddMessage(metadata['poller'].handleResponce,
                    metadata['msg'],[],{}
                    )
            
        
        return results
class jrpcServerTaskQueuePresentor():
    
    def __init__(self,model, threadpool):
        self.log = logging.getLogger("jrpcServerTaskQueuePresentor")
        self.model = model
        self.threadpool = threadpool
        self.scheduler = schedular(self.threadpool)
        self.modelUpdator = SqueezeConnectionModelUpdator()
        self.modelUpdator.Install(self.model)
        self.pollholder = pollholder(self.model,self.scheduler,self.modelUpdator)
        
    
    def QueueProcess(self):
        self.pollholder.check()
        self.scheduler.Overdue()
        self.threadpool.QueueProcessPreTask()
        self.threadpool.QueueProcessResponces()
