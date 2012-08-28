import xbmc, xbmcgui, xbmcaddon
import threading
import time
import socket
import json

from utilities import *
from cache import *

ABORT_REQUESTED = False
# CACHE = Cache()
CACHE = None

__addon__  = xbmcaddon.Addon()

def rebuild(cache):
    """
    Rebuild whole cache in case it is broken.
    """
    pass

class ApiThread(threading.Thread):
    def __init__(self):
        super(ApiThread, self).__init__()
        self.sock = socket.socket()
        self.sock.settimeout(None)
        self.sock.connect(("localhost", 9090))
        # self.sock.connect(("localhost", get_api_port()))

    def process(self, data):
        pass

    def run(self):
        global ABORT_REQUESTED
        global CACHE

        try:
            CACHE = deserialize(__addon__.getSetting("CACHE"))
        except Exception, e:
            print e
            CACHE = Cache()

        while True:
            data = self.sock.recv(1024)
            xbmc.log('At {0}: {1}'.format(time.time(), str(data)))
            try:
                data_json = json.loads(str(data))
                method = data_json.get("method")
            except ValueError, e:
                xbmc.log(e)
                continue

            if method == "System.OnQuit":
                ABORT_REQUESTED = True
                break
            else:
                self.process(data_json)

        __addon__.setSetting(id='CACHE', value=serialize(CACHE))


class Library(ApiThread):
    """
    Just a Library.
    """
    def __init__(self):
        super(Library, self).__init__()

    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    def addorupdate(self, _id, _type):
        if CACHE.exists( _id = _id, _type = _type):
            if _type == "movie":
                print get_movie_details(_id)
            elif _type == "episode":
                print get_episode_details(_id)
        else:
            if _type == "movie":
                movie = get_movie_details(_id)
                print movie
            elif _type == "episode":
                print get_episode_details(_id)

    def remove(self, _id, _type):
        pass

    def process(self, data):
        if "VideoLibrary" in data['method']:
            print data
            if data['method'] == 'VideoLibrary.OnUpdate':
                self.addorupdate(data['params']['data']['item']['id'], data['params']['data']['item']['type'])
            elif data['method'] == 'VideoLibrary.OnRemove':
                self.remove(data['params']['data']['id'], data['params']['data']['type'])
            # http://wiki.xbmc.org/index.php?title=JSON-RPC_API/v4
