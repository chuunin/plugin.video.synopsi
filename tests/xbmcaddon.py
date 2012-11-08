import xbmc
import os

class Addon(object):
    """
    docstring for Addon
    """
    def __init__(self):
        super(Addon, self).__init__()
        self.data = {}
        self.info = { 'path': os.path.realpath(__file__) }
    
    def getAddonInfo(self, key):
        return self.info.get(key, '')

    def setSetting(self, id="id", value="value"):
        self.data[id] = value

    def getSetting(self, id):
        return self.data.get(id, '')

    def openSettings(self):
        pass

    def getLocalizedString(self, *args, **kwargs):
        return "String"
