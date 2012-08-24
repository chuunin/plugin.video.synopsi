import unittest
# from library import Cache

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
        if len(self.get(kwargs)) > 0:
            return True
        else:
            return False

    def delete():
        pass

CACHE = Cache()

class DeviceIDTest(unittest.TestCase):
    def test_dict(self):
        self.assertTrue(CACHE.dict_in_dict(
            {},{}
            ))

        a = {}
        b = {}
        for i in range(20):
            a[str(i)] = i
        for i in range(25):
            b[str(i)] = i

        self.assertTrue(CACHE.dict_in_dict(a,b))
        self.assertFalse(CACHE.dict_in_dict(b,a))

    def test_set(self):
        CACHE.create(_id = 1, _type="movie")
        self.assertEqual(CACHE.get(_id = 1)[0].get("_type"), "movie")

    def test_error(self):
        # self.assertRaises(KeyError, CACHE.get)
        print CACHE.get(_id=3)

    def test_get(self):
        pass

        # print CACHE.get(_id=1)
        # dev_id = default.generate_deviceid()
        # for i in xrange(1,10):
        #   self.assertEqual(dev_id, default.generate_deviceid())

if __name__ == "__main__":
    unittest.main()