import os, sys
import logging
import json

sys.path.insert(0, os.path.abspath('..'))
from apiclient import apiclient


def pprint(data):
	if data.has_key('_db_queries'):
		del data['_db_queries']
	print json.dumps(data, indent=4)


base_url = 'http://neptune.local:8000/'
key = '76ccb5ec8ecddf15c29c5decac35f9'
secret = '261029dbbdd5dd481da6564fa1054e'
username = 'martin.smid@gmail.com'
password = 'aaa'

client = apiclient(base_url, key, secret, username, password, debugLvl = logging.DEBUG)
#client.titleWatched(2848299, 'like')
#client.titleIdentify('1268799')
#client.titleIdentify('1770488')

# 60569 "Malcolm X"

print 'titleIdentify(60569)'
data = client.titleIdentify(60569)
pprint(data)

print 'libraryTitleAdd(60569)'
data = client.libraryTitleAdd(60569)
pprint(data)

print 'profileRecco(movie)'
data = client.profileRecco('movie')
pprint(data)

