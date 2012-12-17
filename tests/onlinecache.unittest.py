# -*- coding: utf-8 -*-
# python standart lib
import os, sys
from unittest import *
import logging
import json
import string
import random
import time

# test helper
from common import connection

# application
sys.path.insert(0, os.path.abspath('..'))
from utilities import *
from apiclient import *
from cache import OnlineStvList, DuplicateStvIdException

def pprint(data):
	global logger

	if data is dict and data.has_key('_db_queries'):
		del data['_db_queries']
	msg = dump(data)
	# print msg
	logger.debug(msg)


class OnlineCacheTest(TestCase):
	def setUp(self):
		cache.clear()

	def test_save_load(self):

		cache.put(test_item1)
		cache.put(test_item3)
		cache.save()

		cache.load()

		self.assertEqual(cache.getByTypeId('movie', '10'), test_item1)

		# check if the items are correctly referenced
		self.assertEqual(id(cache.getByTypeId('movie', '10')), id(cache.getByFilename('/var/log/virtual.ext')))
		self.assertEqual(id(cache.getByTypeId('movie', '10')), id(cache.getByStvId(10009)))

		# check the items encoding
		self.assertEqual(cache.getByTypeId('episode', '10')['file'], u'/var/log/tvshow/Čučoriedky žužlavé.avi')

	def test_put(self):
		movie1 = { 'type': u'movie', 'id': 1, 'file': 'xxx' }
		cache.put(movie1)

		episode1 = { 'type': u'episode', 'id': 2, 'file': 'episode.s02e22.avi' }
		cache.put(episode1)

		movie2 = { 'type': u'movie', 'id': 3, 'file': 'xxx', 'stvId': 9876543 }
		cache.put(movie2)

	def test_correction(self):

		CORRECTION_FILE_HASH = 'abcdefgh1234567890'

		# prepare apiClient with new library

		c = dict(connection)
		c['device_id'] = ''.join(random.choice(string.ascii_lowercase) for x in range(10))

		apiClient = ApiClient(c['base_url'], c['key'], c['secret'], c['username'], c['password'], c['device_id'], debugLvl=logging.ERROR, rel_api_url=c['rel_api_url'])
		cache = OnlineStvList(c['device_id'], apiClient, cwd)


		NEW_STV_ID = 654591
		OLD_STV_ID = 16813

		FILENAME = 'asodfhaoherfoahdfs.avi'

		test_item = { 'type': u'movie', 'id': 3, 'file': FILENAME, 'stvId': OLD_STV_ID }

		movies = [
			{ 'type': u'movie', 'id': 1, 'file': 'movie1.avi', 'stvId': 1483669 }	,
			{ 'type': u'movie', 'id': 2, 'file': 'movie2.avi', 'stvId': 45, 'name': 'The Lord of the Rings: The Two Towers' },
			test_item,
			{ 'type': u'movie', 'id': 4, 'file': 'movie4.avi', 'stvId': 408316, 'name': 'Out of Africa' },
			{ 'type': u'episode', 'id': 1, 'file': 'episode1.avi', 'stvId': 602923, 'name': 'I.F.T.' }  ,
			{ 'type': u'episode', 'id': 2, 'file': 'episode2.avi', 'stvId': 1812663, 'name': 'Cat\'s in the Bag...'} ,
			{ 'type': u'episode', 'id': 3, 'file': 'episode3.avi', 'stvId': 2069156, 'name': 'Founder\'s Day' } ]


		# prepare the library
		# do the identification to put the hash into api
		ident = {
			"file_name": "three times.avi",
			"stv_title_hash": CORRECTION_FILE_HASH,
			"os_title_hash": "486d1f7112f9749d",
			"imdb_id": "0102536",
			'title_property[]': ','.join(['name', 'cover_medium']),
			'type': 'movie'
		}

		# let the service know about our hash. withou this it would not be possible to do correction
		identified_title = apiClient.titleIdentify(**ident)

		print dump(identified_title)
		movies[0]['stvId'] = identified_title['id']

		for movie in movies:
			cache.put(movie)

		time.sleep(2)

		# make sure the old id is in the library
		apiClient.title_identify_correct(OLD_STV_ID, CORRECTION_FILE_HASH)

		cache.list()

		old_title = { 'type': 'movie', 'xbmc_id': 3, 'stv_title_hash': CORRECTION_FILE_HASH }
		new_title = { 'type': 'movie', 'id': NEW_STV_ID }

		new_item = cache.correct_title(old_title, new_title)

		# check if old item is removed
		self.assertTrue(not cache.hasStvId(OLD_STV_ID))
		self.assertTrue(not cache.hasItem(test_item))

		# check if new item is in the right place
		self.assertEqual(cache.byTypeId['movie--3']['stvId'], NEW_STV_ID)
		self.assertEqual(cache.byStvId[NEW_STV_ID]['file'], FILENAME)
		self.assertEqual(cache.byFilename[FILENAME], new_item)

		cache.list()

	def test_disallow_duplicate_stvid(self):
		with self.assertRaises(DuplicateStvIdException):
			cache.put(test_item1)
			cache.put(test_item2)

	def test_get_items(self):
		cache.clear()
		cache.put(test_item1)
		cache.put(test_item3)
		i = cache.getItems()
		self.assertEquals(i[0]['stv_title_hash'], 'ba7c6a7bc6a7b6c')
		self.assertEquals(i[0]['file'], '/var/log/virtual.ext')

if __name__ == '__main__':
	test_item1 = {
		'type': 'movie',
		'id': 10,
		'file': '/var/log/virtual.ext',
		'stvId': 80962,
		'name': 'District 9',
		'stv_title_hash': 'ba7c6a7bc6a7b6c',
	}

	test_item2 = {
		'type': 'movie',
		'id': 11,
		'file': '/var/log/002.avi',
		'stvId': 612160,
		'name': 'Stander',
		'stv_title_hash': 'ba7c6a7bc6a7b6cb8ac8bc',
	}

	test_item3 = {
		'type': 'episode',
		'id': 10,
		'file': u'/var/log/tvshow/Čučoriedky žužlavé.avi',
		'stvId': 3538511,
		'name': 'The Santa Simulation',
		'stv_title_hash': 'c34t66627bc6a7b6cb8ac8bc',
	}

	c = connection
	apiClient = ApiClient(c['base_url'], c['key'], c['secret'], c['username'], c['password'], c['device_id'], debugLvl=logging.ERROR, rel_api_url=c['rel_api_url'])
	cwd = os.path.join(os.getcwd(), 'data', 'cache.dat')

	cache = OnlineStvList(c['device_id'], apiClient, cwd)

	logger = logging.getLogger()

	if len(sys.argv) < 2:
		suite = TestLoader().loadTestsFromTestCase(OnlineCacheTest)
	else:
		suite = TestLoader().loadTestsFromName('OnlineCacheTest.' + sys.argv[1], sys.modules[__name__])

	TextTestRunner(verbosity=2).run(suite)


