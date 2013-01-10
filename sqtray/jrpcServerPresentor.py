



from sqtray.JrpcServer import squeezeConCtrl



class squeezeConPresentor:
    def __init__(self,model):
        self.Externalmodel = model
        self.callbacks = {'requestUpdateModel'}
        
        
    def cbAddRequestUpdateModel(self,functionRequestUpdateModel):
        # Note this calback may be called by any internal thread
        self.callbacks['requestUpdateModel'][functionRequestUpdateModel] = 1
    def cbDoRequestUpdateModel(self):
        # Note this may be called by any internal thread
        for func in self.callbacks:
            func(self)
    def requestUpdateModel(self):
        # This will empty the queue of messages to process
        pass
    
          
        
