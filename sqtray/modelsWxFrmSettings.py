from models import Observable, ObservableDict

class mdlFrmSettings:
    def __init__(self):
        self.tooltip = Observable("... initialising")
        self.currentIconName = Observable(None)
        self.host = Observable(None)
        self.port = Observable(None)
        self.connectionMsg = Observable(None)
        self.statusText = Observable(None)


