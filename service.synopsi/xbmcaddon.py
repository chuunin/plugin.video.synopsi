import xbmc

class Addon(object):
    """docstring for Addon"""
    def __init__(self):
        super(Addon, self).__init__()
    
    def getAddonInfo(self, type):
        return ""

    def setSetting(self, id="id", value="value"):
        pass

    def getSetting(self, id):
        if id == "FIRSTRUN":
            return "true"
        else:
            return ""

    def openSettings(self):
        pass
