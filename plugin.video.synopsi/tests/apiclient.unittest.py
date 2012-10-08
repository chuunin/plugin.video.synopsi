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
		client = apiclient(c['base_url'], c['key'], c['secret'], c['username'], c['password'], debugLvl = logging.WARNING)
		client.getAccessToken()
		self.assertIsInstance(client, apiclient)
		return client

	def test_auth_fail(self):
		global connection

		c = copy(connection)
		c['password'] = 'aax'		# bad password
		client = apiclient(c['base_url'], c['key'], c['secret'], c['username'], c['password'], debugLvl = logging.WARNING)
		succ = client.getAccessToken()
		self.assertTrue(not succ)
		self.assertTrue(not client.isAuthenticated())

	def test_library_add(self):
		global connection

		c = connection		
		client = apiclient(c['base_url'], c['key'], c['secret'], c['username'], c['password'], debugLvl = logging.WARNING)
		client.getAccessToken()

		# 60569 "Malcolm X"
		data = client.titleIdentify(imdb_id = 60569)

		stv_title_id = data['title_id']

		data = client.libraryTitleAdd(stv_title_id)

		watched_data =
		{
			'rating': 1, 
			'playerEvents': [
				{
				    "event_name": "start", 
				    "event_time": 1348749184, 
				    "movie_time": 1222.502
				}, 
				{
				    "event_name": "pause", 
				    "event_time": 1348749320, 
				    "movie_time": 1359.3679999999999
				}, 
				{
				    "event_name": "resume", 
				    "event_time": 1348749321.69554, 
				    "movie_time": 1359.3679999999999
				}, 
				{
				    "event_name": "stop", 
				    "event_time": 1348751319.654, 
				    "movie_time": 1460.3679999999999
				}
			]
		}

		data = client.titleWatched(stv_title_id, **watched_data)

		data = client.libraryTitleRemove(stv_title_id)

		# print 'profileRecco(movie)'
		# props = [ 'year','image' ]
		# data = client.profileRecco('movie', props)
		# pprint(data)



if __name__ == '__main__': 
	connection = {
		'base_url': 'http://neptune.local:8000/',
		#base_url: 'http://test.papi.synopsi.tv/',
		'key': '76ccb5ec8ecddf15c29c5decac35f9',
		'secret': '261029dbbdd5dd481da6564fa1054e',
		'username': 'martin.smid@gmail.com',
		'password': 'aaa'
		'device_id': ''	
	}

	suite = unittest.TestLoader().loadTestsFromTestCase(ApiTest)
	unittest.TextTestRunner(verbosity=2).run(suite)

	#unittest.main()

