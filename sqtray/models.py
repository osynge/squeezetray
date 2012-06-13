

class Observable:
    def __init__(self, initialValue=None):
        self.data = initialValue
        self.callbacks = {}

    def addCallback(self, func):
        self.callbacks[func] = 1

    def delCallback(self, func):
        del self.callback[func]

    def _docallbacks(self):
        for func in self.callbacks:
            func(self.data)

    def set(self, data):
        self.data = data
        self._docallbacks()

    def get(self):
        return self.data

    def unset(self):
        self.data = None

class squeezePlayerMdl:
    def __init__(self,index,identifier = None, Name = None):
        self.index = Observable(index)
        self.identifier = Observable(identifier)
        self.name = Observable(Name)
        self.discovered = Observable(False)
        self.index.addCallback(self.OnAtribChange)
        self.identifier.addCallback(self.OnAtribChange)
        self.name.addCallback(self.OnAtribChange)
        self.operationMode = Observable(None)
        self.CurrentTrackTitle = Observable(None)
        self.CurrentTrackEnds = Observable(None)
        
    def OnAtribChange(self,value):
        discovered = False
        if  (self.identifier != None) and (self.name != None):
            discovered = True
        previously = self.discovered.get()
        if not previously == discovered:
            previously = discovered
            self.discovered.set(discovered)

class squeezeConMdle:
    def __init__(self):
        self.host = Observable("localhost")
        
        self.port = Observable("9000")
        self.connectionStr = Observable("localhost:9000")
        self.connected = Observable(False)
        # Number of players on the server that can be used
        self.playersCount = Observable(0)
        self.playerList = []
        self.connected.addCallback(self.OnConnectedChange)
        self.playersCount.addCallback(self.OnPlayersCountChange)
        self.CbPlayersAvailable= []
        self.CbChurrentTrack = []
        self.connectionStr.addCallback(self.OnConnectedChange)
        
    def OnConnectionStrChange(self,value):
        """ Note ignores parmewters"""
        print "OnConnectionStrChange='%s'" % value
        NewConstr = "%s:%s" % (self.host.get(),self.port.get())
        OldConstr = self.connectionStr.get()
        if NewConstr != OldConstr:
            print "OnConnectionStrChange checnged=%s" % (NewConstr)
            #self.connectionStr.set(NewConstr)
            #self.ConectionStringSet(NewConstr)
            self.playersCount.set(0)
            
    def OnConnectedChange(self,value):
        if not self.connected.get():
            self.playersCount.set(0)
    def OnPlayersCountChange(self,value):
        self.playerList = []
        for index in range(value):
            self.playerList.append(squeezePlayerMdl(index))
            self.playerList[index].discovered.addCallback(self.OnPlayersAvailableChange)
            self.playerList[index].CurrentTrackTitle.addCallback(self.OnCurrentTrack)
    
    def OnPlayersAvailableChange(self,value):
        #print 'dsdsd',value
        availablePlayewrs = []
        for index in range(len(self.playerList)):
            #print index
            if self.playerList[index].discovered.get():
                availablePlayewrs.append(unicode(self.playerList[index].name.get()))
        for func, args, kargs in self.CbPlayersAvailable:
            func(value,availablePlayewrs,*args, **kargs)
    
    def CbPlayersAvailableAdd(self,func, *args, **kargs):
        self.CbPlayersAvailable.append((func, args, kargs))
    def CbChurrentTrackAdd(self,func, *args, **kargs):
        self.CbChurrentTrack.append((func, args, kargs))
    def OnCurrentTrack(self,value):
        #print "OnCurrentTrack (%s)" % value
        for func, args, kargs in self.CbChurrentTrack:
            func(value,*args, **kargs)
    
    
    
    def playerListClear(self):
        self.playerList = []
        self.playersCount.set(0)
