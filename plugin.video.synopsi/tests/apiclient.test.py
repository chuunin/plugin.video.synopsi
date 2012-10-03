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

client = apiclient(base_url, key, secret, username, password, debugLvl = logging.DEBUG)
#client.titleWatched(2848299, 'like')

# 60569 "Malcolm X"

print 'titleIdentify(imdb_id = 60569)'
data = client.titleIdentify(imdb_id = 60569)
pprint(data)

stv_title_id = data['title_id']

print 'libraryTitleAdd(%s)' % stv_title_id
data = client.libraryTitleAdd(stv_title_id)
pprint(data)

print 'titleWatched(%s)' % stv_title_id
data = client.titleWatched(stv_title_id, 
	rating = 1, 
	playerEvents = [
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
		}, 

	]
)

pprint(data)

print 'libraryTitleRemove(%s)' % stv_title_id
data = client.libraryTitleRemove(stv_title_id)
pprint(data)


# print 'profileRecco(movie)'
# props = [ 'year','image' ]
# data = client.profileRecco('movie', props)
# pprint(data)


