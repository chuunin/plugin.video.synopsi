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
        self.assertEqual(d.get(_id = 1)[0].get("_type"), "movie")

    def test_bencode(self):
        for i in range(1000):
            CACHE.create(_id = i, _type="movie")
        s = serialize(CACHE)
        d = deserialize(s)
        self.assertEqual(d.get(_id = 1)[0].get("_type"), "movie")

    def test_delete(self):
        CACHE.create(_id = 90909, _type="movie")
        before = len(CACHE.get(_type = "movie"))
        CACHE.delete(_id = 90909)
        after = len(CACHE.get(_type = "movie"))

        self.assertEqual(before -1 ,after)

        CACHE.delete()
        self.assertEqual(len(CACHE.get(_type = "movie")), 0)

        for i in range(1000):
            CACHE.create(_id = i, _type="movie")
        self.assertEqual(len(CACHE.get()), 1000)


if __name__ == "__main__":
    unittest.main()