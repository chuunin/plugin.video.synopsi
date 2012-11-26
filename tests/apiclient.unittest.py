# python standart lib
import os, sys
from unittest import *
import logging
import json
from copy import copy

# test helper
from common import connection

# application
sys.path.insert(0, os.path.abspath('..'))
from utilities import *
from apiclient import *

def pprint(data):
	global logger

	if data is dict and data.has_key('_db_queries'):
		del data['_db_queries']

	msg = dump(data)
	# print msg
	logger.debug(msg)


class ApiTest(TestCase):
	def test_auth(self):		
		client.getAccessToken()
		self.assertIsInstance(client, ApiClient)
		return client

	def test_auth_fail(self):
		c = copy(connection)
		c['password'] = 'aax'		# bad password
		client = ApiClient(c['base_url'], c['key'], c['secret'], c['username'], c['password'], c['device_id'], debugLvl=logging.WARNING, rel_api_url=c['rel_api_url'])
		
		self.assertRaises(AuthenticationError, client.getAccessToken)
		self.assertTrue(client.isAuthenticated()==False)

	def test_unwatched_episodes(self):		
		data = client.unwatchedEpisodes()

		self.assertTrue(data.has_key('lineup'))
		self.assertTrue(data.has_key('new'))
		self.assertTrue(data.has_key('top'))
		self.assertTrue(data.has_key('upcoming'))

	def test_title_identify(self):	
		ident = {
			"file_name": "/Volumes/FLOAT/Film/_videne/Night_On_Earth/Night_On_Earth.avi", 
			"stv_title_hash": "1defa7f69476e9ffca7b8ceb8c251275afc31ade", 
			"os_title_hash": "486d1f7112f9749d", 
			"imdb_id": "0102536",
			'title_property[]': ','.join(['name', 'cover_medium'])
		}

		stv_title = client.titleIdentify(**ident)

		self.assertTrue(stv_title.has_key('type'))

		ident2 = {
			'file_name': '/Volumes/FLOAT/Film/_videne/Notorious/Notorious.[2009self.Eng].TELESYNC.DivX-LTT.avi', 
			'stv_title_hash': '8b05ff1ad4865480e4705a42b413115db2bf94db', 
			'os_title_hash': '484e59acbfaf64e5', 
			'imdb_id': ''		
		}

		stv_title = client.titleIdentify(**ident2)
		self.assertTrue(stv_title.has_key('type'))


	def test_library_add(self):		
		client.getAccessToken()

		ident = {
			'file_name': '/Volumes/FLOAT/Film/_videne/Notorious/Notorious.[2009self.Eng].TELESYNC.DivX-LTT.avi', 
			'stv_title_hash': '8b05ff1ad4865480e4705a42b413115db2bf94db', 
			'os_title_hash': '484e59acbfaf64e5', 
			'imdb_id': '0472198'		
		}

		data = client.titleIdentify(**ident)

		stv_title_id = data['id']

		data = client.libraryTitleAdd(stv_title_id)

		exampleEvents = [
			{
			    "event": "start", 
			    "timestamp": '2012-10-08 16:54:34', 
			    "position": 1222
			}, 
			{
			    "event": "pause", 
			    "timestamp": '2012-10-08 16:54:40', 
			    "position": 1359
			}, 
			{
			    "event": "resume", 
			    "timestamp": '2012-10-08 16:55:10', 
			    "position": 1359
			}, 
			{
			    "event": "stop", 
			    "timestamp": '2012-10-08 16:55:15', 
			    "position": 1460
			},
		]

		#exampleEvents = []

		watched_data = {
			'rating': 1, 
			'player_events': json.dumps(exampleEvents)
		}

		data = client.titleWatched(stv_title_id, **watched_data)

		data = client.libraryTitleRemove(stv_title_id)

	def test_profile_recco(self):
		

		props = [ 'year', 'cover_small' ]
		data = client.profileRecco('movie', False, 5, props)

		self.assertTrue(data.has_key('recco_id'))
		self.assertTrue(data.has_key('titles'))
		self.assertTrue(len(data['titles']) > 0)

	def test_profile_recco_local(self):
		

		props = [ 'year', 'cover_small' ]
		data = client.profileRecco('movie', True, 5, props)

		self.assertTrue(data.has_key('recco_id'))
		self.assertTrue(data.has_key('titles'))
		self.assertTrue(len(data['titles']) > 0)


	def test_title_similar(self):	
		# 1947362 "Ben-Hur (1959)"
		data_similar = client.titleSimilar(1947362)
		#print data_similar

	def test_title(self):		
		title = client.title(1947362, cast_props=['name'])
		
		self.assertTrue(title.has_key('cover_full'))
		self.assertTrue(title.has_key('cast'))
		self.assertTrue(title['cast'][0]['name']=='Charlton Heston')

	def test_tvshow(self):		
		title = client.tvshow(14335, cast_props=['name'], season_props=['id','season_number'], season_limit=3)
		
		# print dump(title)		

		self.assertTrue(title.has_key('cover_full'))
		self.assertTrue(title.get('type')=='tvshow')
		self.assertTrue(title.get('year')==2005)
		self.assertTrue(title['cast'][0]['name']=='Josh Radnor')

	def test_season(self):		
		title = client.season(14376)

		# print dump(title)

		self.assertTrue(title.has_key('cover_full'))
		self.assertTrue(title.get('type')=='tvshow')
		self.assertTrue(title.get('year')==2005)
		self.assertTrue(title['cast'][0]['name']=='Josh Radnor')

	def test_unicode_input(self):
		data = {
			'key-one': u'Alfa - \u03b1',
			'key-dict': {
				'key-nested': u'Gama - \u03b3'
			}
		}

		enc_data = client._unicode_input(data)
		self.assertEquals(str(enc_data), r"{'key-one': 'Alfa - \xce\xb1', 'key-dict': {'key-nested': 'Gama - \xce\xb3'}}")

	def test_search(self):
		result = client.search('Adams aebler')
		# print dump(result)
		self.assertTrue(result.has_key('search_result'))

	def test_identify_correct(self):
		result = client.title_identify_correct(1947362, '8b05ff1ad4865480e4705a42b413115db2bf94db')
		# print dump(result)
		self.assertTrue(result['status']=='ok')


if __name__ == '__main__': 
	c = connection
	client = ApiClient(c['base_url'], c['key'], c['secret'], c['username'], c['password'], c['device_id'], debugLvl = logging.WARNING, rel_api_url=c['rel_api_url'])

	logger = logging.getLogger()


	if len(sys.argv) < 2:
		suite = TestLoader().loadTestsFromTestCase(ApiTest)
	else:
		suite = TestLoader().loadTestsFromName('ApiTest.' + sys.argv[1], sys.modules[__name__])

	TextTestRunner(verbosity=2).run(suite)


