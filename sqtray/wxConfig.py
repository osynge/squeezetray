
import wx


import logging

    
class ConfigView():
    def __init__(self,model):
        self.model = model
        self.log = logging.getLogger("ConfigView")
        self.cfg = wx.FileConfig(appName="ApplicationName", 
                                    vendorName="VendorName", 
                                    localFilename=".squeezetray.cfg", 
                                    style=wx.CONFIG_USE_LOCAL_FILE)
    def configRead(self):
        self.log.debug("configRead")
        # Set Host
        squeezeServerHost = 'localhost'
        if self.cfg.Exists('squeezeServerHost'):
            #self.log.info("found")
            squeezeServerHost = self.cfg.Read('squeezeServerHost')
        
        
        
        OldSqueezeServerHost = self.model.host.get()
        
        if squeezeServerHost != OldSqueezeServerHost:
            self.model.host.set(squeezeServerHost)
            
        # Set Port
        squeezeServerPort = 9000
        if self.cfg.Exists('squeezeServerPort'):
            try:
                squeezeServerPortTmp = int(self.cfg.ReadInt('squeezeServerPort'))
            except ValueError:
                squeezeServerPort = 9000
                    
                
        OldSqueezeServerPort = self.model.port.get()
        if squeezeServerPort != OldSqueezeServerPort:
            self.model.port.set(squeezeServerPort)
        
        
        # Set Player
        #SqueezeServerPlayer = None
        #if self.cfg.Exists('SqueezeServerPlayer'):
        #    SqueezeServerPlayer = self.cfg.Read('SqueezeServerPlayer')
        #self.SetSqueezeServerPlayer(SqueezeServerPlayer)
        #self.model.GuiPlayerDefault.set(SqueezeServerPlayer)
        #self.squeezeConCtrl.RecConnectionOnline()
        return
    
    
    
class ConfigPresentor():
    def __init__(self,model):
        
        
        self.ExternalModel = model
        self.view = ConfigView(self.ExternalModel)
        
    def load(self):
        self.view.configRead()
    
    def save(self):
        self.view.configSave()
        
        
           
    
