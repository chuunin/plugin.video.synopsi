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
		
	def test_addorupdate_stack(self):
		stack_ident = {
			"file_name": "stack:///Volumes/FLOAT/Film/cache ceske titulky/Cache - CD1.avi , /Volumes/FLOAT/Film/cache ceske titulky/Cache - CD2.avi", 
			"stv_title_hash": 'FF00FF00', 
			"os_title_hash": 'FF00FF00', 
			"imdb_id": "0109362"
		}

	def test_put(self):
		item = { 'type': u'movie', 'id': 1, 'file': 'xxx' }
		cache.put(item)
		
	def test_get_path(self):
		movie = {
			'file': "stack:///Volumes/FLOAT/Film/cache ceske titulky/Cache - CD1.avi , /Volumes/FLOAT/Film/cache ceske titulky/Cache - CD2.avi", 
		}

		#print cache.get_path(movie)
		self.assertEqual(cache.get_path(movie), '/Volumes/FLOAT/Film/cache ceske titulky/Cache - CD1.avi')


if __name__ == '__main__':
	test_item1 = {
		'type': 'movie',
		'id': 10,
		'file': '/var/log/virtual.ext',
		'stvId': 10009
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


