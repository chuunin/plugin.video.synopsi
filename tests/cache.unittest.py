# python standart lib
import os, sys
from unittest import *
import logging
import json

# test helper
from common import connection

# application
sys.path.insert(0, os.path.abspath('..'))
from utilities import *
from apiclient import *
from cache import StvList

def pprint(data):
	global logger

	if data is dict and data.has_key('_db_queries'):
		del data['_db_queries']
	msg = dump(data)
	# print msg
	logger.debug(msg)


class CacheTest(TestCase):
	def test_save_load(self):

		cache.put(test_item1)
		cache.save()

		cache.load()

		self.assertEqual(cache.getByTypeId('movie', '10'), test_item1)

		# check if the items are correctly referenced
		self.assertEqual(id(cache.getByTypeId('movie', '10')), id(cache.getByFilename('/var/log/virtual.ext')))
		self.assertEqual(id(cache.getByTypeId('movie', '10')), id(cache.getByStvId(10009)))


	def test_addorupdate_stack(self):
		stack_ident = {
			"file_name": "stack:///Volumes/FLOAT/Film/cache ceske titulky/Cache - CD1.avi , /Volumes/FLOAT/Film/cache ceske titulky/Cache - CD2.avi",
			"stv_title_hash": 'FF00FF00',
			"os_title_hash": 'FF00FF00',
			"imdb_id": "0109362"
		}

	def test_put(self):
		movie1 = { 'type': u'movie', 'id': 1, 'file': 'xxx' }
		cache.put(movie1)

		episode1 = { 'type': u'episode', 'id': 2, 'file': 'episode.s02e22.avi' }
		cache.put(episode1)

		movie2 = { 'type': u'movie', 'id': 3, 'file': 'xxx', 'stvId': 9876543 }
		cache.put(movie2)

	def test_get_path(self):
		movie = {
			'file': "stack:///Volumes/FLOAT/Film/cache ceske titulky/Cache - CD1.avi , /Volumes/FLOAT/Film/cache ceske titulky/Cache - CD2.avi",
		}

		#print cache.get_path(movie)
		self.assertEqual(cache.get_path(movie), '/Volumes/FLOAT/Film/cache ceske titulky/Cache - CD1.avi')

	def test_correction(self):
		NEW_STV_ID = 1234567
		FILENAME = 'asodfhaoherfoahdfs.avi'

		movie2 = { 'type': u'movie', 'id': 3, 'file': FILENAME, 'stvId': 9876543 }
		cache.put(movie2)

		old_title = { 'type': 'movie', 'xbmc_id': 3 }
		new_title = { 'type': 'movie', 'id': NEW_STV_ID }

		new_item = cache.correct_title(old_title, new_title)

		self.assertEqual(cache.byTypeId['movie--3']['stvId'], NEW_STV_ID)
		self.assertEqual(cache.byStvId[NEW_STV_ID]['file'], FILENAME)
		self.assertEqual(cache.byFilename[FILENAME], new_item)

	def test_update_title(self):
		cache.put(test_item1)

		# title is a synopsi title, where title['id'] is a stvId
		title_01 = { 'id': test_item1['stvId'], 'stv_title_hash': 'should be overwritten', 'type': 'TODO: should stay?',  }

		cache.updateTitle(title_01)

		self.assertEquals(title_01['file'], test_item1['file'])
		self.assertEquals(title_01['stv_title_hash'], test_item1['stv_title_hash'])
		self.assertEquals(title_01['id'], test_item1['stvId'])


if __name__ == '__main__':
	test_item1 = {
		'type': 'movie',
		'id': 10,
		'file': '/var/log/virtual.ext',
		'stvId': 10009,
		'stv_title_hash': 'ba7c6a7bc6a7b6c',
	}

	c = connection
	apiClient = ApiClient(c['base_url'], c['key'], c['secret'], c['username'], c['password'], c['device_id'], debugLvl=logging.ERROR, rel_api_url=c['rel_api_url'])
	cwd = os.path.join(os.getcwd(), 'cache.dat')

	cache = StvList(c['device_id'], apiClient, cwd)

	logger = logging.getLogger()

	if len(sys.argv) < 2:
		suite = TestLoader().loadTestsFromTestCase(CacheTest)
	else:
		suite = TestLoader().loadTestsFromName('CacheTest.' + sys.argv[1], sys.modules[__name__])

	TextTestRunner(verbosity=2).run(suite)


