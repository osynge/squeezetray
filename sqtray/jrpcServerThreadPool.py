import socket
import httplib, urllib
import sys, traceback
from threading import *

class SqueezeConnectionWorker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.callbacks = { 'task_done' : {}}
        self.daemon = True
        self.start()
        self.connectionString = None
        self.SocketErrNo = Observable(0)
        self.SocketErrMsg = Observable("")
        self.log = logging.getLogger("JrpcServer.SqueezeConnectionWorker")
    def cbAddTaskDone(self,funct):
        self.callbacks['task_done'][funct] = 1
    def taskDone(self):
        for func in self.callbacks['task_done']:
            func(self.request)    
        self.tasks.task_done()
        return
    def run(self):
        while True:
            self.request = self.tasks.get()
            
            func = self.request['function']
            params = self.request['params']
            args = self.request['args']
            kargs = self.request['kargs']
            if not hasattr(self,'conn'):
                #print "connectionString", self.connectionString 
                self.taskDone()
                continue
            if self.connectionString == None:
                self.taskDone()
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
                self.taskDone()
                continue
            except httplib.CannotSendRequest, E:
                self.conn = httplib.HTTPConnection(self.connectionString)
                self.log.error("Cannot Send Request, resetting connection.=%s" % (params))
                self.log.error(self.connectionString)
                self.taskDone()
                continue
            errorNoOld = self.SocketErrNo.get()
            self.SocketErrNo.set(0)
            self.SocketErrMsg.set(unicode(""))
            try:
                response = self.conn.getresponse()
            except exceptions.AttributeError, E:
                self.taskDone()
                continue
            except socket.error, E:
                errorNumber = int(E.errno)
                self.SocketErrNo.set(errorNumber)
                self.SocketErrMsg.set(unicode(E.strerror))
                self.taskDone()
                continue
            except httplib.BadStatusLine:
                self.conn = httplib.HTTPConnection(self.connectionString)
                try:
                    self.conn.request("POST", "/jsonrpc.js", params)
                except EnvironmentError as exc:
                    if exc.errno == errno.ECONNREFUSED:
                        self.log.info( "Connection refused")
                        self.taskDone()
                        continue
                    else:
                        raise exc
                except IOError as E:
                    self.log.info( "IOError error:%s" %(E))
                    self.taskDone()
                    continue
                try:
                    response = self.conn.getresponse()
                except httplib.BadStatusLine, E:
                    self.log.info( "httplib.BadStatusLine exception.message=%s,E=%s" % (E.message,E))
                    self.taskDone()
                    continue
            if response.status != 200:
                self.log.info( "httplib.BadResponceStatus %s:%s" % (response.status, response.reason))
                self.taskDone()
                return
            try:
                rep = json.loads(response.read())
            except ValueError as E:
                self.log.info( "Json decoding ValueError:%s" %(E))
                self.taskDone()
                continue
            if func != None:
                self.request['responce'] = rep
                #func(rep,*args, **kargs)
                #try: func(rep)
                #except Exception, e: 
                #    print e
                #    #traceback.print_tb(e, limit=1, file=sys.stdout)
            self.taskDone()
            
            
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


