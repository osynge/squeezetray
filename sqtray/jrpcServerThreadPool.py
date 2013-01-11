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



        
class sConTPool:
    """Pool of threads consuming tasks from a queue"""
    
    def __init__(self, squeezeConMdle,num_threads = 10):
        self.log = logging.getLogger("JrpcServer.SqueezeConnectionThreadPool")
        self.squeezeConMdle = squeezeConMdle
        connectionString = self.squeezeConMdle.connectionStr.get()
        self.tasks = Queue(num_threads)
        self.preTasks = Queue()
        self.arrayOfSqueezeConnectionWorker = []
        self.taskCache = {}
        self.postTasks = Queue()
        for _ in range(num_threads): 
            new = SqueezeConnectionWorker(self.tasks)
            new.ConnectionSet(connectionString)
            new.SocketErrNo.addCallback(self.OnSocketErrNo)
            new.SocketErrMsg.addCallback(self.OnSocketErrMsg)
            new.cbAddTaskDone(self.handleTaskDoneByThread)
            self.arrayOfSqueezeConnectionWorker.append(new)
        self.squeezeConMdle.connectionStr.addCallback(self.OnConnectionStrChange)
    
    def handleTaskDoneByThread(self,request):
        msgHash = request['params']
        if msgHash in self.taskCache.keys():
            del(self.taskCache[msgHash])
        if not 'responce' in request.keys():
            return
        self.postTasks.put(msgHash)
        
    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.log.error("Wait for completion of all the tasks in the queue")
        self.tasks.join()
        
    def SendMessage(self,func,message, *args, **kargs):
        #Sends a message now without Queuing 
        #for a aproved thread
        params = json.dumps(message, sort_keys=True, indent=4)
        request = {
            'function' : func,
            'params' : params,
            'args' : args,
            'kargs' : kargs,
        }
        self.tasks.put(request)
        self.QueueProcessPreTask()
        
    def QueueProcessPreTask(self):
        # For calling to place messages on 
        while True:
            try:
                request = self.preTasks.get_nowait()
            except Empty:
                break
            msgHash = request['params']
            if msgHash in self.taskCache.keys():
                self.taskCache[msgHash]["state"] = 'Qued'
            self.tasks.put(request)
            self.preTasks.task_done()
    def QueueProcessResponces(self):
        # To be processed by external thead
        while True:
            try:
                request = self.postTasks.get_nowait()
            except Empty:
                break
            msgHash = request['params']
            if msgHash in self.taskCache.keys():
                func = self.taskCache[msgHash]['function']
                params = self.taskCache[msgHash]['params']
                args = self.taskCache[msgHash]['args']
                kargs = self.taskCache[msgHash]['kargs']
                rep = self.taskCache[msgHash]['responce']
                
                
                func(rep,params,*args, **kargs)
                #try: func(rep)
                #except Exception, e: 
                #    print e
                #    #traceback.print_tb(e, limit=1, file=sys.stdout)
                
                del(self.taskCache[msgHash])
            self.postTasks.task_done()
            
    def QueueProcessAddMessage(self,func,message, *args, **kargs):
        messageDict = {}
        params = json.dumps(message, sort_keys=True, indent=4)
        if params in self.taskCache.keys():
            #self.log.debug('dedupe is working')
            return
        request = {
            'function' : func,
            'params' : params,
            'args' : args,
            'kargs' : kargs,
        }
        self.taskCache[params] = request
        self.preTasks.put(request)
        
        
        
    
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

        
