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

from jrpcServerView import SqueezeConnectionModelUpdator
        
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
    def __init__(self,model,connectionPool):
        self.externalModel = model
        self.callbacks = {'requestUpdateModel'}
        #self.internalModel = squeezeConMdle()
        #self.internalModel.host.update('mini')
        #self.connectionCopyer = ConCtrlInteractor()
        #self.connectionCopyer.install(self.externalModel,self.internalModel)
        #self.internalUpdator = SqueezeConnectionModelUpdator()
        #self.internalUpdator.Install(self.internalModel)
        self.connectionPool = connectionPool
        self.threadpoolPresentor = jrpcServerTaskQueuePresentor(self.externalModel,
            self.connectionPool)
        
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
        self.threadpoolPresentor.QueueProcess()
        
        
            
