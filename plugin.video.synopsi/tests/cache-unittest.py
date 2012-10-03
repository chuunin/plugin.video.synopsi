# -*- coding: utf-8 -*-
import base64
import pickle
import unittest
import random
import sys

sys.path.append('..')
cache = __import__('cache')

CACHE = cache.StvList()

class StvListTest(unittest.TestCase):
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
        s = cache.serialize(CACHE)
        d = cache.deserialize(s)
        self.assertEqual(d.get(_id = 1)[0].get("_type"), "movie")

    def test_bencode(self):
        for i in range(1000):
            CACHE.create(_id = i, _type="movie")
        s = cache.serialize(CACHE)
        d = cache.deserialize(s)
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

TVShows = [ 
            # Filename , Serie, #Season, #Episode(s) 
             ("Dexter - 6x09.mkv","Dexter",6,[9])
            ,("Terra Nova - 1x11x12 - Occupation & Resistance.mkv","Terra Nova",1,[11,12])
            ,("Dexter - S06E09.mkv","Dexter",6,[9])
            ,("Terra Nova - S01E11-12 - Occupation & Resistance.mkv","Terra Nova",1,[11,12])
            ,("Dexter.6x09.mkv","Dexter",6,[9])
            ,("Terra.Nova.1x11x12.Occupation.&.Resistance.mkv","Terra Nova",1,[11,12])
            ,("Breaking.Bad.S02E03.Bit.by.a.Dead.Bee.mkv","Breaking Bad",2,[3])
            ,("Dexter.S06E09.mkv","Dexter",6,[9])
            ,("Terra.Nova.S01E11-12.Occupation.&.Resistance.mkv","Terra Nova",1,[11,12])
            ,("Terra.Nova.S1E11-12.Occupation.&.Resistance.mkv","Terra Nova",1,[11,12])
            ,("Dexter.S6E9.mkv","Dexter",6,[9])
            ,("The Cleveland Show - S03E01 - BFFs.HDTV.mkv","The Cleveland Show",3,[1])
        ]

Movies = [
            # Filename [I should inform the majors that theses files are some examples taken from the net ! ;-)]
             ("Home.(2009).1080p") 
            ,("Home (2009) 1080p")
            ,("Home_(2009)_1080p")    
            ,("Inception.BDRip.1080p.mkv")
            ,("indiana jones and the last crusade 1989 1080p x264 dd5.1-m794.mkv")
            ,("Indiana.Jones.and.the.Temple.of.Doom.[1984].HDTV.1080p.mkv")
            ,("Inglourious.Basterds.(2009).BDRip.1080p.mkv")        
            ,("James.Bond.04.Thunderball.1965.Bluray.1080p.DTSMA.x264.dxva-FraMeSToR.mkv")
            ,("James.Bond.08.Live.and.Let.Die.1973.Bluray.1080p.DTSMA.x264.dxva-FraMeSToR.mkv")
            ,("The.Godfather.Part.III.(1990).BDRip.1080p.[SET Godfather].mkv")
            ,("Underworld.Rise.Of.The.Lycans.(2008).BDRip.1080p.[SET Underworld].mkv")
            ,("unstoppable.2010.bluray.1080p.dts.x264-chd.mkv")
            ,("UP.(2009).BDRip.720p.mkv") # epic !
            ,("127.Hours.2010.1080p.BluRay.x264-SECTOR7.mkv")
            ,("13.Assassins.2010.LIMITED.1080p.BluRay.x264-WEST.mkv")
            ,("2012.(2009).BDRip.1080p.mkv")
            ,("300.(2006).BDRip.1080p.mkv")
            ,("Big.Fish.2003.1080p.BluRay.DTS.x264-DON")
            ,("inf-fast5-1080p[ID tt1596343].mkv") # Who are looking this shit ?
            ,("Le.Fabuleux.Destin.d'Amélie.Poulain.2001.1080p.BluRay.DTS.x264-CtrlHD")
            ,("avchd-paul.2011.extended.1080p.x264")
            ,("twiz-unknown-1080p")
        ]

class ScenarioTest(unittest.TestCase):
    c = cache.StvList()
    def test_initial_import(self):
        self.c.delete()
        if len(Movies) > len(self.c.get(_type = "movie")):
            pass
        elif len(Movies) < len(self.c.get(_type = "movie")):
            pass

    def test_rebuild(self):
        self.c.delete()
        for i in Movies:
            self.c.create(_id = random.randint(1,1000), _type= "movie", _file = i )

        self.assertEqual(len(Movies), len(self.c.get(_type = "movie")))

        # print [x for x in self.c.get()]

        # for i in TVShows:
        #     self.c.create(_id = random.randint(1,1000), _type= "episode", _file = i[0],  )

    def test_reparse(self):
        
        def api_parse(somedata):
            return random.randint(1000000,2891720)
        # for i in self.c.get_has_not("stv_id"):
        #     self.c.update(i, stv_id=api_parse(i))
        # self.assertEqual(0, len(self.c.get_has_not("stv_id")))
        pass

if __name__ == "__main__":
    unittest.main()


