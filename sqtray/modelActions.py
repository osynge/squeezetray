class ConCtrlInteractor():

    def install(self,ModelFrmSettings,ModelConPool):
        self.ModelFrmSettings = ModelFrmSettings
        self.ModelConPool = ModelConPool
        
    def OnApply(self,presentor):
        self.ModelConPool.host.update(self.ModelFrmSettings.host.get())
        self.ModelConPool.port.update(self.ModelFrmSettings.port.get())
