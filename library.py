import xbmc, xbmcgui, xbmcaddon
from mythread import MyThread
import time
import socket
import json
import traceback
from app_apiclient import AppApiClient
from utilities import *
from cache import *


ABORT_REQUESTED = False


class RPCListener(MyThread):
    def __init__(self, cache):
        super(RPCListener, self).__init__()
        self.cache = cache
        self.apiclient = None

        self.sock = socket.socket()
        self.sock.settimeout(5)
        self.connected = False
        sleepTime = 100
        t = time.time()
        while sleepTime<500 and (not self.connected or ABORT_REQUESTED or xbmc.abortRequested):
            try:
                self.sock.connect(("localhost", 9090))  #   TODO: non default api port (get_api_port)
            except Exception, exc:
                self._log.debug('%0.2f %s' % (time.time() - t, str(exc)))
                xbmc.sleep(int(sleepTime))
                sleepTime *= 1.5
            else:
                self._log.debug('Connected to 9090')
                self.connected = True

        self.sock.setblocking(True)

    def process(self, data):
        pass

    def run(self):
        global ABORT_REQUESTED

        if not self.connected:
            return False

        self.apiclient = AppApiClient.getDefaultClient()

        while True:
            data = self.sock.recv(1024)
            # self._log.debug('SynopsiTV: {0}'.format(str(data)))
            try:
                data_json = json.loads(str(data))
                method = data_json.get("method")
            except ValueError, e:
                self._log.debug('RPC ERROR:' + str(e))
                continue

            if method == "System.OnQuit":
                ABORT_REQUESTED = True
                break
            else:
                self.process(data_json)

        self.sock.close()
        self._log.debug('Library thread end')

    def process(self, data):
        methodName = data['method'].replace('.', '_')
        method = getattr(self, methodName, None)
        if method == None:
            self._log.debug('Unknown method: ' + methodName)
            return

        self._log.debug('calling: ' + methodName)
        self._log.debug(str(data))
        
        #   Try to call that method
        try:
            method(data)
        except:
            self._log.debug('Error in method "' + methodName + '"')
            self._log.debug(traceback.format_exc())

        #   http://wiki.xbmc.org/index.php?title=JSON-RPC_API/v4


class RPCListenerHandler(RPCListener):
    """
    RPCListenerHandler defines event handler methods that are autotically called from parent class's RPCListener
    """
    def __init__(self, cache):
        super(RPCListenerHandler, self).__init__(cache)

    #   NOT USED NOW
    def playerEvent(self, data):
        self._log.debug(json.dumps(data, indent=4))

    def log(self, msg):
        self._log.debug('Library: ' + msg)

    def addorupdate(self, atype, aid):
        self.cache.addorupdate(atype, aid)

    def remove(self, atype, aid):
        self.cache.remove(atype, aid)

    def VideoLibrary_OnUpdate(self, data):
        self.addorupdate(data['params']['data']['item']['type'], data['params']['data']['item']['id'])

    def VideoLibrary_OnRemove(self, data):
        self.remove(data['params']['data']['type'], data['params']['data']['id'])

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

