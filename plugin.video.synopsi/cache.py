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
        self.byTypeId[str(item['type']) + '--' + str(item['id'])] = item
        self.byFilename[item['file']] = item
        stvIdStr = ' | stvId ' + str(item['stvId']) if item.has_key('stvId') else ''
        logstr = 'PUT:' + str(item['type']) + '--' + str(item['id']) + stvIdStr + ' | ' + item['file']
        self.log(logstr)

    def hasTypeId(self, type, id):
        return self.byTypeId.has_key(type + '--' + str(id))

    def getByTypeId(self, type, id):
        return self.byTypeId[type + '--' + str(id)]

    def getByFilename(self, name):
        return self.byFilename[name]

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

    def get_from_dict(self, arg):
        rtrn = []
        for row in self.hash_table:
            if self.dict_in_dict(arg, row):
                rtrn.append(row)
        return rtrn

    def get(self, **kwargs):
        return self.get_from_dict(kwargs)

    def get_index(self, **kwargs):
        raise NotImplementedError

    def get_has_not(self, *args):
        rtrn = []
        broken = False
        for row in self.hash_table:
            for arg in args:
                if row.has_key(arg):
                    if row[arg] is None:
                        broken = True
                        break
                else:
                    broken = True
                    break
            if broken:
                rtrn.append(row)
                broken = False
        return rtrn

    def exists(self, **kwargs):
        if len(self.get_from_dict(kwargs)) > 0:
            return True
        else:
            return False

    def update(self, item, **kwargs):
        raise NotImplementedError
        for _item in self.get_from_dict(item):
            pass
            # cache.update({"_id": 99, "_type": "movie"}, stv_id = 92384924)
            # self.hash_table.
            # for key in kwargs.keys():


    def delete(self, **kwargs):
        for item in self.get_from_dict(kwargs):
            self.hash_table.remove(item)

