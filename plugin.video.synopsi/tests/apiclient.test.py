import os, sys
import logging
import json

sys.path.insert(0, os.path.abspath('..'))
from apiclient import apiclient


def pprint(data):
	if data and data.has_key('_db_queries'):
		del data['_db_queries']
	print json.dumps(data, indent=4)


base_url = 'http://neptune.local:8000/'
#base_url = 'http://test.papi.synopsi.tv/'
key = '76ccb5ec8ecddf15c29c5decac35f9'
secret = '261029dbbdd5dd481da6564fa1054e'
username = 'martin.smid@gmail.com'
password = 'aaa'
iuid = '7caa970e-0e37-11e2-9462-7cc3a1719bfd'

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

exampleEvents = []

#	TEST START	
client = apiclient(base_url, key, secret, username, password, iuid, debugLvl=logging.DEBUG)
# data = { 'rating': 'like' }
#client.titleWatched(2848299, data)

# 60569 "Malcolm X"

print 'titleIdentify(imdb_id = 60569)'
data = client.titleIdentify(imdb_id=60569, title_hash='', subtitle_hash='')
pprint(data)

stv_title_id = data['title_id']

print 'libraryTitleAdd(%s)' % stv_title_id
data = client.libraryTitleAdd(stv_title_id)
pprint(data)

watched_data = {
	'rating': 1, 
	'player_events': exampleEvents 
}

print 'titleWatched(%s)' % stv_title_id
data = client.titleWatched(stv_title_id, **watched_data)

pprint(data)

print 'libraryTitleRemove(%s)' % stv_title_id
data = client.libraryTitleRemove(stv_title_id)
pprint(data)


# print 'profileRecco(movie)'
# props = [ 'year','image' ]
# data = client.profileRecco('movie', True, props)
# pprint(data)

# print 'profileRecco(movie)'
# props = [ 'year','image' ]
# data = client.profileRecco('movie', False, props)
# pprint(data)


