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
from jrpcServerThreadPool  import sConTPool


if float(sys.version[:3]) >= 2.6:
    import json
else:
    # python 2.4 or 2.5 can also import simplejson
    # as working alternative to the json included.
    import simplejson as json


import errno
from jrpcServerTaskQueuePresentor import jrpcServerTaskQueuePresentor

from  modelActions import ConCtrlInteractor

class squeezeConPresentor:
    def __init__(self, model, connectionPool):
        self.model = model
        #self.internalModel = squeezeConMdle()
        #self.internalModel.host.update('mini')
        #self.connectionCopyer = ConCtrlInteractor()
        #self.connectionCopyer.install(self.model,self.internalModel)
        #self.internalUpdator.Install(self.internalModel)
        self.connectionPool = connectionPool
        self.threadpoolPresentor = jrpcServerTaskQueuePresentor(self.model,
                                                                self.connectionPool)


    def requestUpdateModel(self):
        # This will empty the queue of messages to process
        self.threadpoolPresentor.QueueProcess()



    def Pause(self, player):
        if not self.model.connected.get():
            return None
        if not player in self.model.Players:
            return None
        playerIndex = self.model.Players[player].index.get()
        playerId = self.model.Players[player].identifier.get()
        msg = {
            "id": playerIndex,
            "method": "slim.request",
            "params": [ playerId, ["pause"]]
        }
        msg = json.dumps(msg, sort_keys=True, indent=4)
        reponce = self.connectionPool.SendMessage(None, msg)

    def Play(self, player):
        if not self.model.connected.get():
            return None
        if not player in self.model.Players:
            return None
        playerIndex = self.model.Players[player].index.get()
        playerId = self.model.Players[player].identifier.get()
        msg = {
            "id" : playerIndex,
            "method": "slim.request",
            "params": [ playerId, ["play"]]
        }
        msg = json.dumps(msg, sort_keys=True, indent=4)
        reponce = self.connectionPool.SendMessage(None, msg)

    def Stop(self, player):
        if not self.model.connected.get():
            return None
        if not player in self.model.Players:
            return None
        playerIndex = self.model.Players[player].index.get()
        playerId = self.model.Players[player].identifier.get()
        msg = {
            "id" : playerIndex,
            "method": "slim.request",
            "params": [ playerId, ["stop"]]
        }
        msg = json.dumps(msg, sort_keys=True, indent=4)
        reponce = self.connectionPool.SendMessage(None, msg)

    def Index(self, player, Count):
        if not self.model.connected.get():
            return None
        prefix = ""
        if Count > 0:
            prefix = "+"
        if not player in self.model.Players:
            return None
        playerIndex = self.model.Players[player].index.get()
        playerId = self.model.Players[player].identifier.get()
        msg = {
            "id": playerIndex,
            "method": "slim.request",
            "params": [ playerId, ["playlist", "index", prefix + unicode(Count)]]
        }
        msg = json.dumps(msg, sort_keys=True, indent=4)
        reponce = self.connectionPool.SendMessage(None, msg)

    def PlayRandomSong(self, player):
        if not self.model.connected.get():
            return None
        if not player in self.model.Players:
            return None
        playerIndex = self.model.Players[player].index.get()
        playerId = self.model.Players[player].identifier.get()
        msg = {
            "id": playerIndex,
            "method": "slim.request",
            "params": [ playerId, ["randomplay", 'tracks']]
            }
        msg = json.dumps(msg, sort_keys=True, indent=4)
        reponce = self.connectionPool.SendMessage(None, msg)

