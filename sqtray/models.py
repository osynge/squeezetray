import UserDict

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

    def update(self, data):
        if self.data == data:
            return
        self.data = data
        self._docallbacks()

    def get(self):
        return self.data

    def unset(self):
        self.data = None


class ObservableDict( UserDict.DictMixin):
    def __init__(self):
        self._dict = {}
        self.callbacks = {}

    def __getitem__(self, item):

        if not item in self._dict.keys():
            raise KeyError("Item %s does not exist" % item)
        return self._dict[item]

    def addCallback(self, func):
        self.callbacks[func] = 1

    def delCallback(self, func):
        del self.callback[func]

    def _docallbacks(self, key):
        for func in self.callbacks:
            func(key)

    def __setitem__(self, item, value):
        if item in self:
            del self[item]
        self._dict[item] = value
        self._docallbacks(item)

    def __delitem__(self, item):
        if not item in self._dict:
            raise KeyError("File %s does not exist" % fn)
        self._docallbacks(item)

    def keys(self):
        return self._dict.keys()

    def count(self):
        return len(self._dict.keys())
