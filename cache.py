import base64
import pickle
import xbmc
import json
from utilities import *
from app_apiclient import ApiClient


xbmc2stv_key_translation = {
    'file_name': 'file', 
    'stv_title_hash': 'stv_hash', 
    'os_title_hash': 'os_title_hash', 
    'total_time': 'runtime', 
    'label': 'originaltitle', 
    'imdb_id': 'imdbnumber'
}

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
    def __init__(self, uuid, apiclient):
        super(StvList, self).__init__()
        self.apiclient = apiclient

        self.byTypeId = {}
        self.byFilename = {}
        self.byStvId = {}

        self.uuid = uuid


    @classmethod
    def getDefaultList(cls, apiClient=None):
        addon  = get_current_addon()
        if not apiClient:
            apiClient = AppApiClient.getDefaultClient()

        iuid = get_install_id()    
        cache = StvList(iuid, apiClient) 
        try:
            cwd = addon.getAddonInfo('path')
            cache.load(os.path.join(cwd, 'resources', 'cache.dat'))
        except:
            # first time
            self.log('restore failed. If this is your first run, its ok')

        return cache

    def serialize(self):
        pickled_base64_cache = base64.b64encode(pickle.dumps([self.byTypeId, self.byFilename, self.byStvId]))
        return pickled_base64_cache

    def deserialize(self, _string):
        unpickled_list = pickle.loads(base64.b64decode(_string))
        self.byTypeId = unpickled_list[0]
        self.byFilename = unpickled_list[1]
        self.byStvId = unpickled_list[2]

    def log(self, msg):
        xbmc.log('CACHE / ' + str(msg))

    def _translate_xbmc2stv_keys(self, a, b):
        for (dst_key, src_key) in xbmc2stv_key_translation.iteritems():
            if b.has_key(src_key):
                a[dst_key] = b[src_key]

    def addorupdate(self, atype, aid):
        # find out actual data about movie
        movie = get_details(atype, aid)
        movie['type'] = atype
        movie['id'] = aid

        # if not in cache, it's been probably added
        if not self.hasTypeId(movie['type'], movie['id']):
            # get stv hash
            movie['stv_hash'] = stv_hash(movie['file'])
            movie['os_title_hash'] = hash_opensubtitle(movie['file'])
            # try to get synopsi id
            # for now, try only if there is 'imdbnumber'

            # TODO: stv_subtitle_hash - hash of the subtitle file if presented
            ident = {}
            self._translate_xbmc2stv_keys(ident, movie)
            # correct exceptions
            if ident.get('imdb_id'):
                ident['imdb_id'] = ident['imdb_id'][2:]

            # self.log('ident:' + json.dumps(ident, indent=4))    

            title = self.apiclient.titleIdentify(**ident)
            if title.has_key('title_id'):
                movie['stvId'] = title['title_id']

            self.put(movie)

        # it is already in cache, some property has changed (e.g. lastplayed time)
        else:
            self.update(movie)


    def put(self, item):
        " Put a new record in the list "
        typeIdStr = self._getKey(item['type'], item['id'])
        
        self.byTypeId[typeIdStr] = item
        self.byFilename[item['file']] = item
        if item.has_key('stvId'):
            self.byStvId[item['stvId']] = item

        stvIdStr = ' | stvId ' + str(item['stvId']) if item.has_key('stvId') else ''
        logstr = 'PUT / ' + typeIdStr + stvIdStr + ' | ' + item['file']
        
        # if known by synopsi, add to list
        if item.has_key('stvId'):
            self.apiclient.libraryTitleAdd(item['stvId'])

        self.log(logstr)

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

    def remove(self, type, id):
        typeIdStr = self._getKey(type, id)
        try:
            item = self.getByTypeId(type, id)
            del self.byFilename[item['file']]
            del self.byTypeId[typeIdStr]

            if item.has_key('stvId'):
                self.apiclient.libraryTitleRemove(item['stvId'])
                del self.byStvId[item['stvId']]
        except Exception as e:
            self.log(e)
            self.log('REMOVE FAILED / ' + typeIdStr)    

        self.log('REMOVE / ' + typeIdStr)

    def hasTypeId(self, type, id):
        return self.byTypeId.has_key(self._getKey(type, id))

    def getByTypeId(self, type, id):
        return self.byTypeId[self._getKey(type, id)]

    def hasFilename(self, name):
        return self.byFilename.has_key(name)
        
    def getByFilename(self, name):
        return self.byFilename[name]

    def hasStvId(self, stv_id):
        return self.byStvId.has_key(stv_id)

    def getByStvId(self, stv_id):
        if self.byStvId.has_key(stv_id):
            return self.byStvId[stv_id]

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

    def save(self, path):
        f = open(path, 'w')
        f.write(self.serialize())
        f.close()

    def load(self, path):
        f = open(path, 'r')
        self.deserialize(f.read())
        f.close()

    def _getKey(self, type, id):
        return str(type) + '--' + str(id)

