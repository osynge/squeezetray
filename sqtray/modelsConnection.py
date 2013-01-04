from models import Observable, ObservableDict
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
        self.CurrentTrackArtist = Observable(None)
        self.CurrentTrackEnds = Observable(None)
        self.CurrentTrackId = Observable(None)
    def OnAtribChange(self,value):
        
        discovered = True
        if  (self.name.get() == None):
            discovered = False
        if  (self.identifier.get() == None):
            discovered = False
        previously = self.discovered.get()
        if not previously == discovered:
            self.discovered.set(discovered)

class squeezeConMdle:
    def __init__(self):
        self.host = Observable("localhost")
        self.port = Observable(9000)
        # connectionStr : a simple to observe break of connection settings obj
        self.connectionStr = Observable("localhost:9000")
        self.connected = Observable(False)
        # Number of players on the server that can be used
        self.playersCount = Observable(0)
        # Socket Computer diagnostic error. Will be 0 when no error
        self.SocketErrNo = Observable(0)
        # Socket Human diagnostic error. Will be "" with no error, 
        self.SocketErrMsg = Observable("")
        
        self.playerList = []
        self.Players = ObservableDict()
        self.CbPlayersAvailable= []
        self.CbChurrentTrack = []
        self.host.addCallback(self.OnHostChange)
        self.port.addCallback(self.OnPortChange)
        
        self.connectionStr.addCallback(self.OnConnectedChange)
        self.connected.addCallback(self.OnConnectedChange)
        self.playersCount.addCallback(self.OnPlayersCountChange)
    
    
    
    def OnHostChange(self,value):
        newHost = self.host.get()
        newPort = self.port.get()
        newConnectionStr = "%s:%s" % (self.host.get(),self.port.get())
        if newConnectionStr != self.connectionStr.get():
            self.connectionStr.set(newConnectionStr)
    def OnPortChange(self,value):
        newHost = self.host.get()
        newPort = self.port.get()
        newConnectionStr = "%s:%s" % (self.host.get(),self.port.get())
        if newConnectionStr != self.connectionStr.get():
            self.connectionStr.set(newConnectionStr)

            
    def OnConnectedChange(self,value):
        if not self.connected.get():
            if 0 != self.playersCount.get():
                self.playersCount.set(0)
    def OnPlayersCountChange(self,value):
        self.playerList = []
        for index in range(value):
            self.playerList.append(squeezePlayerMdl(index))
            self.playerList[index].discovered.addCallback(self.OnPlayersAvailableChange)
            self.playerList[index].CurrentTrackId.addCallback(self.OnCurrentTrack)
        self.OnPlayersAvailableChange(value)
        
    
    
    def OnPlayersAvailableChange(self,value):
        #print "OnPlayersAvailableChange"
        AvailablePlayersList = []
        for index in range(len(self.playerList)):
            if True != self.playerList[index].discovered.get():
                continue
            PlayerName = self.playerList[index].name.get()
            AvailablePlayersList.append(PlayerName)
            if PlayerName in self.Players:
                continue
            self.Players[PlayerName] = self.playerList[index]
        AvailablePlayersSet = set(AvailablePlayersList)
        for item in AvailablePlayersSet.symmetric_difference(self.Players):
            del self.Players[item]
        
        for func, args, kargs in self.CbPlayersAvailable:
            func(*args, **kargs)
    
    def CbPlayersAvailableAdd(self,func, *args, **kargs):
        self.CbPlayersAvailable.append((func, args, kargs))
    def CbChurrentTrackAdd(self,func, *args, **kargs):
        self.CbChurrentTrack.append((func, args, kargs))
    def OnCurrentTrack(self,value):
        #print "OnCurrentTrack (%s)" % value
        for func, args, kargs in self.CbChurrentTrack:
            func(*args, **kargs)
    
    
    
    def playerListClear(self):
        self.playerList = []
        if 0 != self.playersCount.get():
            self.playersCount.set(0)
