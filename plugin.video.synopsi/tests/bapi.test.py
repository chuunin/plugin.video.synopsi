import json
import sys
from base64 import b64encode
from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError

base_url = 'http://neptune.local:8000/'
key = 'd5f5447375e3934cfaefee7b588884'
secret = 'd0b998a45ed65477f34e9f8942ddac'

print 'get access token'

data = {'grant_type': 'password', 'client_id': key, 'client_secret': secret, 'username': 'xbmc@synopsi', 'password': 'aaa'}
headers = {'AUTHORIZATION': 'BASIC %s' % b64encode("%s:%s" % (key, secret))}

# get token
try:
    response = urlopen(Request(base_url + 'oauth2/token/', data=urlencode(data), headers=headers, origin_req_host='dev.bapi.synopsi.tv'))
    response_json = json.loads(response.readline())
except HTTPError as e:
    print e
    print e.read()
    sys.exit()

access_token = response_json['access_token']
refresh_token = response_json['refresh_token']
print 'access token = ' + access_token

# post and get params
post = {}
get = {}
data = None

# create profile
# post = {
#     'client_id': key,
#     'client_secret': secret,
#     'bearer_token': access_token,
#     'id': '22',
#     'email': 'jurko@mrkvicka.com'
# }
# url = base_url + '/1.0/profile/create/'

# get user data
# get = {
#     'client_id': key,
#     'client_secret': secret,
#     'bearer_token': access_token,
# }
# url = base_url + '/1.0/profile/22/'

# add title
# post = {
#     'client_id': key,
#     'client_secret': secret,
#     'bearer_token': access_token,
#     'id': '2742562',
#     'imdb_id': '2742562'
# }
# url = base_url + '/1.0/movie/add/'

# get title
# get = {
#     'client_id': key,
#     'client_secret': secret,
#     'bearer_token': access_token,
# }

business_api_url = base_url + 'api/public/1.0/'
url = business_api_url + 'title/2848299/watched/'
#url = base_url + 'bapi/example/ping'
#url = business_api_url + 'example/ping'

method = 'post'

# append data

if method == 'post':
    post['client_id'] = key
    post['client_secret'] = secret
    post['bearer_token'] = access_token
    data = urlencode(post)
    print data

if method == 'get':
    get['client_id'] = key
    get['client_secret'] = secret
    get['bearer_token'] = access_token
    url += '?' + urlencode(get)
    print url

print 'call API'
try:
    response = urlopen(Request(url,
        data=data, headers=headers, origin_req_host='dev.bapi.synopsi.tv'
    ))
except HTTPError as e:
    print e
    print e.read()
else:
    while True:
        l = response.readline()
        if not l:
            break
        print l


