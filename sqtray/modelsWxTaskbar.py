from models import Observable, ObservableDict

class taskBarMdle:
    def __init__(self):
        self.tooltip = Observable("... initialising")
        self.currentIconName = Observable(None)

