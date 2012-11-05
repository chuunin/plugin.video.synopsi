import os, sys
import unittest
import logging
import json

sys.path.insert(0, os.path.abspath('..'))
from apiclient import *
from cache import StvList

def pprint(data):
	global logger

	if data is dict and data.has_key('_db_queries'):
		del data['_db_queries']
	msg = json.dumps(data, indent=4)
	# print msg
	logger.debug(msg)


class CacheTest(unittest.TestCase):
	connection = None
	apiClient = None
	_library = None
		
	def test_save(self):
		c = connection
		client = ApiClient(c['base_url'], c['key'], c['secret'], c['username'], c['password'], c['device_id'], debugLvl=logging.WARNING, rel_api_url=c['rel_api_url'])

		self._library = StvList(c['device_id'], client)
		self._library.put(test_item1)

		str_cache_ser = self._library.serialize()				
		self._library.save('cache.test.dat')
		
	def test_load(self):
		c = connection
		client = ApiClient(c['base_url'], c['key'], c['secret'], c['username'], c['password'], c['device_id'], debugLvl=logging.WARNING, rel_api_url=c['rel_api_url'])

		self._library = StvList(c['device_id'], client)		
		self._library.load('cache.test.dat')
		self._library.list()
		

if __name__ == '__main__':
	test_item1 = {
		'type': 'movie',
		'id': 1,
		'file': '/var/log/virtual.ext',
		'stvId': 10009
	}		

	connection = {
		'base_url': 'http://test.papi.synopsi.tv/',
		'key': 'e20e8f465f42e96d8340e81bfc48c757',
		'secret': '72ab379c50650f7aec044b14db306430a55f09a2da1eb8e40b297a54b30e4b4f',
		'rel_api_url': '1.0/',
		# 'base_url': 'http://neptune.local:8000/',
		# 'key': '76ccb5ec8ecddf15c29c5decac35f9',
		# 'secret': '261029dbbdd5dd481da6564fa1054e',
		# 'rel_api_url': 'api/public/1.0/',
		'username': 'martin.smid@gmail.com',
		'password': 'aaa',
		'device_id': '7caa970e-0e37-11e2-9462-7cc3a1719bfd',
	}
	
	logger = logging.getLogger()

	suite = unittest.TestLoader().loadTestsFromTestCase(CacheTest)
	unittest.TextTestRunner(verbosity=2).run(suite)


