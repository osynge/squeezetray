import socket
import httplib, urllib
import sys, traceback
from threading import *
from modelsConnection import squeezeSong,  squeezePlayerMdl, squeezeConMdle
import logging
from Queue import Queue, Empty
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


from jrpcServerView import SqueezeConnectionModelUpdator
        
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
            self.view1.queueMessage(item[0],item[1])
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
        



from jrpcServerTaskQueuePresentor import jrpcServerTaskQueuePresentor

class squeezeConPresentor:
    def __init__(self,model):
        self.externalModel = model
        self.callbacks = {'requestUpdateModel'}
        self.internalModel = squeezeConMdle()
        self.internalUpdator = SqueezeConnectionModelUpdator()
        self.internalUpdator.Install(self.internalModel)
        self.thradpool = jrpcServerTaskQueuePresentor
        #print 'ssssssssssssssss'
        #self.ConCtrlView = squeezeConCtrl(self.internalModel)
        
    def cbAddRequestUpdateModel(self,functionRequestUpdateModel):
        # Note this calback may be called by any internal thread
        self.callbacks['requestUpdateModel'][functionRequestUpdateModel] = 1
    def cbDelRequestUpdateModel(self,functionRequestUpdateModel):
        # Note this calback may be called by any internal thread
        del(self.callbacks['requestUpdateModel'][functionRequestUpdateModel])
    def cbDoRequestUpdateModel(self):
        # Note this may be called by any internal thread
        for func in self.callbacks:
            func(self)
    def requestUpdateModel(self):
        # This will empty the queue of messages to process
        pass
    
    
          
        
