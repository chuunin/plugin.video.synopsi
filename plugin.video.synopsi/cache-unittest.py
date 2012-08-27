import base64
import pickle
import unittest

from cache import *

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
        self.assertTrue(CACHE.dict_in_dict(
            {'_id': 1}, {'_type': 'movie', '_id': 1}))

    def test_set(self):
        CACHE.create(_id = 1, _type="movie")
        self.assertEqual(CACHE.get(_id = 1)[0].get("_type"), "movie")

    def test_serialize(self):
        CACHE.create(_id = 1, _type="movie")
        s = serialize(CACHE)
        d = deserialize(s)
        self.assertEqual(CACHE.get(_id = 1)[0].get("_type"), "movie")

if __name__ == "__main__":
    unittest.main()