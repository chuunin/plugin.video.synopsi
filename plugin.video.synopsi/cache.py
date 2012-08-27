import base64
import pickle


def serialize(cache):
    return base64.b64encode(pickle.dumps(cache))


def deserialize(_string):
    return pickle.loads(base64.b64decode(_string))


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

    def get_from_dict(self, arg):
        rtrn = []
        for row in self.hash_table:
            if self.dict_in_dict(arg, row):
                rtrn.append(row)
        return rtrn
    
    def get(self, **kwargs):
        return self.get_from_dict(kwargs)

    def get_index(self, **kwargs):
        pass

    def exists(self, **kwargs):
        if len(self.get(kwargs)) > 0:
            return True
        else:
            return False

    def delete(self, **kwargs):
        for item in self.get_from_dict(kwargs):
            self.hash_table.remove(item)

