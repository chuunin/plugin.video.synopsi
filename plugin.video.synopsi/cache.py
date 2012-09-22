import base64
import pickle
import xbmc

def serialize(cache):
    return base64.b64encode(pickle.dumps(cache))


def deserialize(_string):
    return pickle.loads(base64.b64decode(_string))


class Cache(object):
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
    def __init__(self):
        super(Cache, self).__init__()
        self.byTypeId = {}
        self.byFilename = {}

        self.hash_table = []

    def log(self, msg):
        xbmc.log('CACHE: ' + str(msg))

    def put(self, item):
        type = item['type']
        id = item['id']
        self.byTypeId[self._getKey(type, id)] = item
        self.byFilename[item['file']] = item
        stvIdStr = ' | stvId ' + str(item['stvId']) if item.has_key('stvId') else ''
        logstr = 'PUT:' + self._getKey(type, id) + stvIdStr + ' | ' + item['file']
        self.log(logstr)

    def hasTypeId(self, type, id):
        return self.byTypeId.has_key(self._getKey(type, id))

    def getByTypeId(self, type, id):
        return self.byTypeId[self._getKey(type, id)]

    def getByFilename(self, name):
        return self.byFilename[name]

    def remove(self, type, id):
        item = self.getByTypeId(type, id)
        del self.byFilename[item['file']]
        del self.byTypeId[self._getKey(type, id)]

    def _getKey(self, type, id):
        return str('type') + '--' + str('id')
