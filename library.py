try:
    import xbmc, xbmcgui, xbmcaddon
except ImportError:
    from tests import xbmc, xbmcgui, xbmcaddon
import threading
import time
import socket
import json
import traceback
import apiclient
from utilities import *
from cache import *


ABORT_REQUESTED = False

__addon__  = xbmcaddon.Addon()

class RPCListener(threading.Thread):
    def __init__(self, cache):
        super(RPCListener, self).__init__()
        self.sock = socket.socket()
        self.sock.settimeout(10)
        conned = False
        sleepTime = 100
        t = time.time()
        while not conned or ABORT_REQUESTED:
            try:
                self.sock.connect(("localhost", 9090))  #   TODO: non default api port (get_api_port)
            except Exception, exc:
                xbmc.log('%0.2f %s' % (time.time() - t, str(exc)))
                xbmc.sleep(int(sleepTime))
                sleepTime *= 1.5
            else:
                xbmc.log('Connected to 9090')
                conned = True

        self.sock.setblocking(True)
        self.cache = cache
        self.apiclient = None


    def process(self, data):
        pass

    def run(self):
        global ABORT_REQUESTED
        # raise Exception(__addon__.getSetting('BASE_URL'))
        self.apiclient = apiclient.apiclient(
            __addon__.getSetting('BASE_URL'),
            __addon__.getSetting('KEY'),
            __addon__.getSetting('SECRET'),
            __addon__.getSetting('USER'),
            __addon__.getSetting('PASS'),
            get_install_id(),
            rel_api_url=__addon__.getSetting('REL_API_URL'),
        )

        while True:
            data = self.sock.recv(1024)
            # xbmc.log('SynopsiTV: {0}'.format(str(data)))
            try:
                data_json = json.loads(str(data))
                method = data_json.get("method")
            except ValueError, e:
                xbmc.log(str(e))
                continue

            if method == "System.OnQuit":
                ABORT_REQUESTED = True
                break
            else:
                self.process(data_json)

        xbmc.log('Library thread end')

    def process(self, data):
        methodName = data['method'].replace('.', '_')
        method = getattr(self, methodName, None)
        if method == None:
            xbmc.log('Unknown method: ' + methodName)
            return

        xbmc.log('calling: ' + methodName)
        xbmc.log(str(data))
        
        #   Try to call that method
        try:
            method(data)
        except:
            xbmc.log('Error in method "' + methodName + '"')
            xbmc.log(traceback.format_exc())

        #   http://wiki.xbmc.org/index.php?title=JSON-RPC_API/v4


class RPCListenerHandler(RPCListener):
    """
    RPCListenerHandler defines event handler methods that are autotically called from parent class's RPCListener
    """
    def __init__(self, cache):
        super(RPCListenerHandler, self).__init__(cache)
        self.playerEvents = []

    #   NOT USED NOW
    def playerEvent(self, data):
        self.log(json.dumps(data, indent=4))

    def log(self, msg):
        xbmc.log('Library: ' + msg)

    def addorupdate(self, aid, atype):
        self.cache.addorupdate(aid, atype)

    def remove(self, aid, atype):
        self.cache.remove(atype, aid)

    def VideoLibrary_OnUpdate(self, data):
        self.addorupdate(data['params']['data']['item']['id'], data['params']['data']['item']['type'])

    def VideoLibrary_OnRemove(self, data):
        self.remove(data['params']['data']['id'], data['params']['data']['type'])

    def Player_OnPlay(self, data):
        self.playerEvent(data)

    def Player_OnStop(self, data):
        self.playerEvent(data)

    def Player_OnSeek(self, data):
        self.playerEvent(data)
        pass

    def Player_OnPause(self, data):
        self.playerEvent(data)
        pass

    def Player_OnResume(self, data):
        self.playerEvent(data)
        pass

    def GUI_OnScreenSaverActivated(self, data):
        self.playerEvent(data)
        pass

    def GUI_OnScreenSaverDeactivated(self, data):
        self.playerEvent(data)
        pass

