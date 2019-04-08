from models import Observable

import logging

from wxTaskBarIcon import TaskBarIconUpdateInteractor
from sqtray.wxTrayIconPopUpMenu import PopupMenuPresentor

class TaskBarIconPresentor(object):
    def __init__(self, Model, View, interactor):
        """Takes as a model a taskBarMdle"""
        self.log = logging.getLogger("TaskBarIconPresentor")
        self.Model = Model
        self.View = View
        interactor.install(self,self.View)
        #self.tbupdator =  TaskBarIconUpdateInteractor()
        #self.tbupdator.install(self.Model, self.View)
        self.currentPlayer = Observable(None)

        self.callbacks = {
            "on_settings" : {},
            "on_modelUpdate" : {},
            "on_popupMenu" : {},
            "on_left_up" : {},
        }

        self.TaskBarIconName = None
        self.Model.currentIconName.addCallback(self._OnIconChange)
        self.Model.tooltip.addCallback(self._OnToolTipChange)

    def doCbAbstract(self,indexer):

        results = {}
        if not indexer in self.callbacks.keys():
            return results
        for item in self.callbacks[indexer]:
            results[item] = item()
        return results

    def doCbModelUpdate(self):
        for item in self.callbacks["on_modelUpdate"]:
            item(self)

    def doCbPopupMenu(self):
        return self.doCbAbstract("on_popupMenu")


    def doCbExit(self):
        return self.doCbAbstract("on_exit")


    def _OnIconChange(self,IconName):
        self.View.set_icon(IconName,(16,16))
        #self.doCbModelUpdate()

    def _OnToolTipChange(self,ToolTip):
        self.log.debug("_OnToolTipChange")
        self.View.set_toolTip(ToolTip)

    def cbAddReqMdlUpdate(self,func):
        self.callbacks['on_modelUpdate'][func] = 1
    def cbAddRequestPopUpMenu(self,func):
        self.callbacks['on_popupMenu'][func] = 1



    def cbAddOnSettings(self,func):
        self.callbacks['on_settings'].append(func)
    def cbAddOnToolTipUpdate(self,func):
        self.callbacks['on_settings'].append(func)

    def cbAddOnExit(self,func):
        self.callbacks['on_exit'].append(func)
    def OnTrack(self):
        self.UpdateToolTip()
    def GetSqueezeServerPlayer(self):
        return self.currentPlayer.get()
    def UpdateToolTip(self):
        newToolTip = self.Model.tooltip.get()
        #self.View.set_toolTip(newToolTip)
        return newToolTip


    def OnPlayers(self):
        #print "OnPlayers(=%s)" % (Event)
        self.UpdateToolTip()
        #self.View.set_icon("ART_APPLICATION_STATUS_DISCONECTED",(16,16))
        self.View.set_icon("ART_APPLICATION_STATUS_CONNECTED",(16,16))
    def SelectPopupMenu(self):
        self.log.debug( "CreatePopupMenu")
        resultset = self.doCbPopupMenu()
        #print "resultset",len(resultset)
        for item in resultset:
            #self.log.debug( "CreatePopupMenu=%s" % (item))
            rc = item()
            if rc == None:
                continue
            return rc

        self.log.debug( "CreatePopupMenu=None")


        return None

    def on_move(self):
        #print 'on_move'
        pass
        self.UpdateToolTip()
    def on_settings(self):
        for item in self.callbacks["on_settings"]:
            item()


    def playerChanged1 (self,value):
        if value != self.Model.GuiPlayer.get():
            self.Model.GuiPlayer.set(value)
            #self.View.set_icon("ART_APPLICATION_STATUS_CONNECTED",(16,16))
    def on_exit(self):
        #self.on_settings_close(event)
        #wx.CallAfter(self.Destroy)
        #self.View.Exit()
        self.doCbExit()

    def on_left_up(self,):
        #self.log.debug( 'on_left_up=%s' % self.GetSqueezeServerPlayer())
        return self.doCbAbstract("on_left_up")

    def on_right_down(self):
        #print 'on_right_down'
        pass
    def on_right_up(self):
        self.log.debug( 'on_right_up')
        #menu = self.CreatePopupMenu()
        #print dir (menu)
    def on_right_dclick(self):
        self.log.debug( 'on_right_dclick')
        #self.CreatePopUp(  event.GetPoint() )
    def on_click(self):
        pass


    def on_left_down(self):
        #print 'Tray icon was left-clicked.'
        pass
    def on_left_dclick(self):
        #print 'Tray icon was on_left_dclick-clicked.'
        pass
    def setIcon(self,IconName):
        #self.View.set_icon("ART_APPLICATION_STATUS_CONNECTED",(16,16))
        self.View.set_icon(IconName,(16,16))
