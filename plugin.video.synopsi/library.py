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

class ApiThread(threading.Thread):
    def __init__(self, cache):
        super(ApiThread, self).__init__()
        self.sock = socket.socket()
        self.sock.settimeout(10)
        conned = False
        while not conned:
            try:
                self.sock.connect(("localhost", 9090))  #   TODO: non default api port (get_api_port)
            except Exception, exc:
                xbmc.log(str(exc))
                xbmc.sleep(1)
            else:
                xbmc.log('Connected to 9090')
                conned = True

        xbmc.log('timeout:' + str(self.sock.gettimeout()))
        self.sock.setblocking(True)
        self.cache = cache
        self.apiclient = None


    def process(self, data):
        pass

    def run(self):
        global ABORT_REQUESTED

        self.apiclient = apiclient.apiclient(
            __addon__.getSetting('BASE_URL'),
            __addon__.getSetting('KEY'),
            __addon__.getSetting('SECRET'),
            __addon__.getSetting('USER'),
            __addon__.getSetting('PASS'),
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


class Library(ApiThread):
    """
    Just a Library.
    """
    def __init__(self, cache):
        super(Library, self).__init__(cache)
        self.playerEvents = []

    def playerEvent(self, data):
        self.log(json.dumps(data, indent=4))

    def log(self, msg):
        xbmc.log('Library: ' + msg)

    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    def addorupdate(self, aid, atype):
        # find out new data about movie
        movie = get_details(atype, aid)
        movie['type'] = atype
        movie['id'] = aid
        # if not in cache, it's been probably added
        if not self.cache.hasTypeId(atype, aid):
            # get stv hash
            movie_hash = stv_hash(movie['file'])
            movie['stv_hash'] = movie_hash
            # try to get synopsi id
            # for now, try only if there is 'imdbnumber'
            if movie.has_key('imdbnumber'):
                title = self.apiclient.titleIdentify(movie['imdbnumber'][2:])
                if title.has_key('title_id'):
                    movie['stvId'] = title['title_id']
            self.cache.put(movie)

        # it is already in cache, some property has changed (e.g. lastplayed time)
        else:
            self.cache.update(movie)

    def remove(self, aid, atype):
        self.cache.remove(atype, aid)

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

    def VideoLibrary_OnUpdate(self, data):
        self.addorupdate(data['params']['data']['item']['id'], data['params']['data']['item']['type'])

    def VideoLibrary_OnRemove(self, data):
        self.remove(data['params']['data']['id'], data['params']['data']['type'])

    def Player_OnPlay(self, data):
        self.playerEvent(data)
        aid = data['params']['data']['item']['id']
        atype = data['params']['data']['item']['type']

    def Player_OnStop(self, data):
        self.playerEvent(data)
        if data == None:
            return

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




