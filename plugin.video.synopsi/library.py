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

def rebuild(cache):
    """
    Rebuild whole cache in case it is broken.
    """
    pass
    # print json.dumps(get_all_movies())
    cache.delete()
    movies = get_all_movies()["result"]["movies"]
    for movie in movies:
        cache.create(_id = movie["movieid"], _type = "movie", imdb = movie["imdbnumber"], filepath = movie["file"])
        print movie["imdbnumber"]

    tv_shows = get_all_tvshows()["result"]["tvshows"]
    # print tv_shows
    for show in tv_shows:
        for episode in get_episodes(show["tvshowid"])["result"]["episodes"]:
            cache.create(_id = episode["episodeid"], _type = "episode", filepath = episode["file"])


    for u in cache.get():
        print u
        # print get_episode_details(u)


class ApiThread(threading.Thread):
    def __init__(self, cache):
        super(ApiThread, self).__init__()
        self.sock = socket.socket()
        self.sock.settimeout(None)
        self.sock.connect(("localhost", 9090))
        # self.sock.connect(("localhost", get_api_port()))
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

        self.apiclient.getAccessToken()

        while True:
            data = self.sock.recv(1024)
            # xbmc.log('At {0}: {1}'.format(time.time(), str(data)))
            xbmc.log('SynopsiTV: {0}'.format(str(data)))
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

        # __addon__.setSetting(id='CACHE', value=serialize(CACHE))


class Library(ApiThread):
    """
    Just a Library.
    """
    def __init__(self, cache):
        super(Library, self).__init__(cache)

    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    def addorupdate(self, aid, atype):
        movie = get_details(atype, aid)
        movie['type'] = atype
        movie['id'] = aid
        # if not in cache, it's been probably added
        if not self.cache.hasTypeId(atype, aid):
            # try to get synopsi id
            title = self.apiclient.titleIdentify(movie['imdbnumber'][2:])
            if title.has_key('title_id'):
                movie['stvId'] = title['title_id']
            self.cache.put(movie)

        # it is already in cache, some property has changed (e.g. lastplayed time)
        else:
            movie = get_details(atype, aid)
            xbmc.log(str(movie))

    def remove(self, aid, atype):
        self.cache.remove(aid, atype)

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
