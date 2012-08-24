import xbmc, xbmcgui, xbmcaddon
import threading
import time
import socket
import json

from utilities import *

ABORT_REQUESTED = False

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
        while True:
            data = self.sock.recv(1024)
            xbmc.log('At {0}: {1}'.format(time.time(), str(data)))
            try:
                data_json = json.loads(str(data))
                method = data_json.get("method")

                API_CACHE = data_json.copy()
            except ValueError:
                continue

            if method == "System.OnQuit":
                ABORT_REQUESTED = True
                break
            else:
                self.process(data_json)


class Cache(object):
    """
    Library cache.
    """
    def __init__(self):
        super(Cache, self).__init__()
        self.table = []
        self.hash_table = []

    def create(self, **kwargs):
        self.hash_table.append(kwargs)
    
    @staticmethod
    def dict_in_dict(d,c):
        try:    
            for i in d.keys():
                if not (d[i] == c[i]):
                    return False
        except KeyError, e:
            return False
        return True

    def get_from_dict(self, args):
        rtrn = []
        for row in self.hash_table:
            if self.dict_in_dict(args, row):
                rtrn.append(row)
        return rtrn
    
    def get(self, **kwargs):
        self.get_from_dict(kwargs)

    def get_index(self, **kwargs):
        pass

    def exists(self, **kwargs):
        if len(self.get_from_dict(kwargs)) > 0:
            return True
        else:
            return False

    def delete():
        pass


CACHE = Cache()


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
        print "{0}: {1}".format(_type, _id)
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
                self.addorupdate(data['params']['data']['id'], data['params']['data']['type'])
