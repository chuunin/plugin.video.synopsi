import os, sys
import unittest
import logging
import json
from copy import copy

sys.path.insert(0, os.path.abspath('..'))
from apiclient import apiclient

def pprint(data):
	global logger

	if data and data.has_key('_db_queries'):
		del data['_db_queries']
	msg = json.dumps(data, indent=4)
	# print msg
	logger.debug(msg)


class ApiTest(unittest.TestCase):
	def test_auth(self):
		global connection

		c = connection		
		client = apiclient(c['base_url'], c['key'], c['secret'], c['username'], c['password'], c['device_id'], debugLvl = logging.WARNING)
		client.getAccessToken()
		self.assertIsInstance(client, apiclient)
		return client

	def test_auth_fail(self):
		global connection

		c = copy(connection)
		c['password'] = 'aax'		# bad password
		client = apiclient(c['base_url'], c['key'], c['secret'], c['username'], c['password'], c['device_id'], debugLvl = logging.WARNING)
		succ = client.getAccessToken()
		self.assertTrue(not succ)
		self.assertTrue(not client.isAuthenticated())

	def test_library_add(self):
		global connection

		c = connection		
		client = apiclient(c['base_url'], c['key'], c['secret'], c['username'], c['password'], c['device_id'], debugLvl = logging.WARNING)
		client.getAccessToken()

		# 60569 "Malcolm X"
		data = client.titleIdentify(imdb_id=60569, title_hash='', subtitle_hash='')

		stv_title_id = data['title_id']

		data = client.libraryTitleAdd(stv_title_id)

		watched_data =
		{
			'rating': 1, 
			'player_events': [
				{
				    "event": "start", 
				    "timestamp": 1348749184, 
				    "position": 1222.502
				}, 
				{
				    "event": "pause", 
				    "timestamp": 1348749320, 
				    "position": 1359.3679999999999
				}, 
				{
				    "event": "resume", 
				    "timestamp": 1348749321.69554, 
				    "position": 1359.3679999999999
				}, 
				{
				    "event": "stop", 
				    "timestamp": 1348751319.654, 
				    "position": 1460.3679999999999
				}
			]
		}

		data = client.titleWatched(stv_title_id, **watched_data)

		data = client.libraryTitleRemove(stv_title_id)

		# print 'profileRecco(movie)'
		# props = [ 'year','image' ]
		# data = client.profileRecco('movie', False, props)
		# pprint(data)



if __name__ == '__main__': 
	connection = {
		'base_url': 'http://neptune.local:8000/',
		#base_url: 'http://test.papi.synopsi.tv/',
		'key': '76ccb5ec8ecddf15c29c5decac35f9',
		'secret': '261029dbbdd5dd481da6564fa1054e',
		'username': 'martin.smid@gmail.com',
		'password': 'aaa'
		'device_id': '7caa970e-0e37-11e2-9462-7cc3a1719bfd'	
	}

	suite = unittest.TestLoader().loadTestsFromTestCase(ApiTest)
	unittest.TextTestRunner(verbosity=2).run(suite)

	#unittest.main()

