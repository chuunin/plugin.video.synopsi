import json
import sys
from base64 import b64encode
from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError

# definitions of properties
key = 'a050ae580751249c462e7e4489d414'
secret = '75dd95a845e8bcf5da23037b8ec014'

data = {'grant_type': 'password', 'client_id': key, 'username': 'NAME', 'password': 'PASSWORD'}
headers = {'AUTHORIZATION': 'BASIC %s' % b64encode("%s:%s" % (key, secret))}


#get token
try:
    response = urlopen(Request('http://synopsi.icepol.net:8000/oauth2/token/', data=urlencode(data), headers=headers, origin_req_host='synopsi.icepol.net'))
    response_json = json.loads(response.readline())
except HTTPError as e:
    print e
    print e.read()
    sys.exit()

print response_json
access_token = response_json['access_token']
refresh_token = response_json['refresh_token']

print 'get data'
post = None
get = None

if 0:
    # add title in to library
    post = {
        'client_id': key,
        'bearer_token': access_token,
    }
    url = 'http://synopsi.icepol.net:8000/bapi/public/1.0/library/title/100/add/'

if 0:
    # get title from library
    get = {
        'client_id': key,
        'bearer_token': access_token,
    }
    url = 'http://synopsi.icepol.net:8000/bapi/public/1.0/library/title/100/'

if 0:
    # recco for user
    get = {
        'client_id': key,
        'bearer_token': access_token,
        'type': 'movie'
    }
    url = 'http://synopsi.icepol.net:8000/bapi/public/1.0/profile/recco/'

if 0:
    # similar title
    get = {
        'client_id': key,
        'bearer_token': access_token,
    }
    url = 'http://synopsi.icepol.net:8000/bapi/public/1.0/title/100/similar/'

if 0:
    # get synopsi title ID
    post = {
        'client_id': key,
        'bearer_token': access_token,
        'imdb_id': 1234
    }
    url = 'http://synopsi.icepol.net:8000/bapi/public/1.0/title/identify/'

if 1:
    # similar title
    post = {
        'client_id': key,
        'bearer_token': access_token
    }
    url = 'http://synopsi.icepol.net:8000/bapi/public/1.0/title/100/watched/'

data = None
if post:
    data = urlencode(post)
if get:
    url += '?' + urlencode(get)

try:
    response = urlopen(Request(url,
        data=data, headers=headers, origin_req_host='synopsi.icepol.net'
    ))
except HTTPError as e:
    print e
    print e.read()
else:
    print 'read data'
    while True:
        l = response.readline()
        if not l:
            break
        print l