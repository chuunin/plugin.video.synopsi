import base64
import pickle
import xbmc
import json
from utilities import *

def serialize(cache):
    return base64.b64encode(pickle.dumps(cache))


def deserialize(_string):
    return pickle.loads(base64.b64decode(_string))


class StvList(object):
    """
    Library cache.
    Storing:
    {
        "_id" : xbmcid, # not unique
        "_type": xbmctype, # "movie" or "episode"
        "_hash": stvhash, # synopsi hash
        "_file": file, # unique path to ONE file
        "filepath": filepath, # path recieved from xbmc
        # could be stack:// or stream etc.
        "imdb": imdb,
        "stv_id": synopsi_id_library
    }
    """
    def __init__(self, uuid):
        super(StvList, self).__init__()
        self.byTypeId = {}
        self.byFilename = {}
        self.byStvId = {}

        self.uuid = uuid
        self.list()

    def log(self, msg):
        xbmc.log('CACHE / ' + str(msg))

    def put(self, item):
        " Put a new record in the list "
        typeIdStr = self._getKey(item['type'], item['id'])
        self.byTypeId[typeIdStr] = item
        self.byFilename[item['file']] = item
        stvIdStr = ' | stvId ' + str(item['stvId']) if item.has_key('stvId') else ''
        logstr = 'PUT / ' + typeIdStr + stvIdStr + ' | ' + item['file']
        self.log(logstr)
        self.list()

    def update(self, item):
        typeIdStr = self._getKey(item['type'], item['id'])
        cacheItem = self.byTypeId[typeIdStr]

        updateStr = ''

        # update items
        for key in item:
            if not cacheItem.has_key(key) or not item[key] == cacheItem[key]:
                updateStr += key + ': ' + str(getattr(cacheItem, key, None)) + ' -> ' + str(item[key]) + ' | '
                cacheItem[key] = item[key]

        self.log('UPDATE / ' + typeIdStr + ' / ' + updateStr)


    def hasTypeId(self, type, id):
        return self.byTypeId.has_key(self._getKey(type, id))

    def getByTypeId(self, type, id):
        return self.byTypeId[self._getKey(type, id)]

    def hasFilename(self, name):
        return self.byFilename.has_key(name)
        
    def getByFilename(self, name):
        return self.byFilename[name]

    def remove(self, type, id):
        item = self.getByTypeId(type, id)
        del self.byFilename[item['file']]
        del self.byTypeId[self._getKey(type, id)]
        self.list()

    def list(self):
        self.log('ID / ' +  self.uuid)
        if len(self.byTypeId) == 0:
            self.log('EMPTY')
            return

        self.log('LIST /')
        for rec in self.byTypeId.values():
            self.log(self._getKey(rec['type'], rec['id']) + '\t| ' + json.dumps(rec))

    def listByFilename(self):
        if len(self.byFilename) == 0:
            self.log('EMPTY')
            return

        self.log('LIST /')
        for rec in self.byFilename.items():
            self.log(rec[0] + '\t| ' + json.dumps(rec[1]))

    def clear(self):
        self.byFilename = {}
        self.byTypeId = {}

    def rebuild(self):
        """
        Rebuild whole cache in case it is broken.
        """
        
        self.clear()
        movies = get_all_movies()["movies"]
        for movie in movies:
            movie['id'] = movie["movieid"]
            movie['type'] = "movie"
            self.put(movie)

        resTvShows = get_all_tvshows()
        if resTvShows.has_key("tvshows") > 0:
            tv_shows = resTvShows
            self.log(json.dumps(tv_shows))
            # print tv_shows
            for show in tv_shows:
                for episode in get_episodes(show["tvshowid"])["result"]["episodes"]:
                    self.create(_id = episode["episodeid"], _type = "episode", filepath = episode["file"])
                    episode['id'] = episode["episodeid"]
                    episode['type'] = "episode"
                    self.put(episode)

    def _getKey(self, type, id):
        return str(type) + '--' + str(id)

