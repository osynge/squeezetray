

class SqueezeConnectionModelUpdator():

    def Install(self, model):
        self.squeezeConMdle = model
        
        
    def OnPlayerCount(self,responce):
        #sConTPool.__init__(self)
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
        
        
        
