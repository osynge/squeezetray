class GuiInteractor(object):
    def __init__(self):
        self.callbacks = {
            "on_exit" : {},
            "on_settings" : {},
            "on_nowPlaying" : {},
            "on_play" : {},
            "on_pause" : {},
            "on_stop" : {},
            "on_seek_index" : {},
            "on_random_songs" : {}
        }

    def cbAddOnExit(self, func):
        self.callbacks['on_exit'][func] = 1

    def cbAddOnSettings(self, func):
        self.callbacks['on_settings'][func] = 1

    def cbAddOnNowPlaying(self, func):
        self.callbacks['on_nowPlaying'][func] = 1

    def cbAddOnPlay(self, func):
        self.callbacks['on_play'][func] = 1

    def cbAddOnPause(self, func):
        self.callbacks['on_pause'][func] = 1
    def cbAddOnStop(self, func):
        self.callbacks['on_stop'][func] = 1



    def cbAddOnSeekIndex(self, func):
        self.callbacks['on_seek_index'][func] = 1

    def cbAddOnRandomSongs(self, func):
        self.callbacks['on_random_songs'][func] = 1


    def doCbOnExit(self, evt):
        results = {}
        for item in self.callbacks["on_exit"]:
            results[item] = item()
        return results

    def doCbOnSettings(self, evt):
        results = {}
        for item in self.callbacks["on_settings"]:
            results[item] = item()
        return results
    def doCbOnNowPlaying(self, evt):
        results = {}
        for item in self.callbacks["on_nowPlaying"]:
            results[item] = item()
        return results
    def doCbOnPlay(self, evt, player):
        results = {}
        for item in self.callbacks["on_play"]:
            results[item] = item(player)
        return results
    def doCbOnStop(self, evt, player):
        results = {}
        for item in self.callbacks["on_stop"]:
            results[item] = item(player)
        return results
    def doCbOnPause(self, evt, player):
        results = {}
        for item in self.callbacks["on_pause"]:
            results[item] = item(player)
        return results

    def doCbOnSeekForward(self, evt, player):
        results = {}
        for item in self.callbacks["on_seek_index"]:
            results[item] = item(player, 1)
        return results

    def doCbOnSeekBackwards(self, evt, player):
        results = {}
        for item in self.callbacks["on_seek_index"]:
            results[item] = item(player, -1)
        return results

    def doCbOnRandomSongs(self, evt, player):
        results = {}
        for item in self.callbacks["on_random_songs"]:
            results[item] = item(player)
        return results
