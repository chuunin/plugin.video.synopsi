import logging
import json
import sys
import datetime
from base64 import b64encode
from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError

RATING_CODE = {
	1: 'like',
	2: 'neutral',
	3: 'dislike'
}

class apiclient:
	def __init__(self, base_url, key, secret, username, password, originReqHost = None, debugLvl = logging.INFO, accessTokenTimeout = 10):
		self.baseUrl = base_url
		self.key = key
		self.secret = secret
		self.username = username
		self.password = password
		self.accessToken = None
		self.refreshToken = None
		self.apiUrl = self.baseUrl + 'api/public/1.0/'
		self.originReqHost = originReqHost or 'dev.bapi.synopsi.tv'
		self.authHeaders = None
		self._logger = logging.getLogger()
		self._logger.addHandler(logging.StreamHandler(sys.stdout))
		self._logger.setLevel(debugLvl)
		self._logger.debug('apiclient __init__')
		self.accessTokenTimeout = accessTokenTimeout		# [minutes] how long is stv accessToken valid ?
		self.accessTokenSessionStart = None

	def getAccessToken(self):
		data = {
			'grant_type': 'password',
			'client_id': self.key,
			'client_secret': self.secret,
			'username': self.username,
			'password': self.password
		}

		self.authHeaders = {'AUTHORIZATION': 'BASIC %s' % b64encode("%s:%s" % (self.key, self.secret))}

		# get token
		try:
			response = urlopen(Request(
					self.baseUrl + 'oauth2/token/', 
					data=urlencode(data), 
					headers=self.authHeaders, 
					origin_req_host=self.originReqHost))

			response_json = json.loads(response.readline())

		except HTTPError as e:
			self._logger.error(str(e))
			self._logger.error(e.read())
			return False

		self.accessToken = response_json['access_token']
		self.accessTokenSessionStart = datetime.datetime.now()
		self.refreshToken = response_json['refresh_token']
		self._logger.debug('access token = ' + self.accessToken)
		return True

	def isAuthorized(self):
		# if we have some acess token and if access token session didn't timeout
		return self.accessToken != None and self.accessTokenSessionStart + datetime.timedelta(minutes=self.accessTokenTimeout) > datetime.datetime.now()

	def execute(self, requestData):
		if not self.isAuthorized():
			access = self.getAccessToken()
			if not access:
				self._logger.debug('Could not get the auth token')
				return False

		url = self.apiUrl + requestData['methodPath']

		method = requestData['method']
		data = None

		if not requestData.has_key('data'):
			requestData['data'] = {}

		# append data to post
		if method == 'post':
			post = requestData['data']		
			# post['client_id'] = self.key
			# post['client_secret'] = self.secret
			post['bearer_token'] = self.accessToken
			data = urlencode(post)

		# append data to get
		if method == 'get':
			get = requestData['data']
			# get['client_id'] = self.key
			# get['client_secret'] = self.secret
			get['bearer_token'] = self.accessToken
			url += '?' + urlencode(get)
			data = None
			self._logger.debug(url)

		if 'post' in locals():
			self._logger.debug('post:' + str(post))
		if 'get' in locals():
			self._logger.debug('get:' + str(get))		

		self._logger.debug('data:' + str(data))	

		try:
			response = urlopen(
				Request(
					url,
					data = data,
					headers = self.authHeaders, 
					origin_req_host = self.originReqHost
				)
			)

			response_json = json.loads(response.readline())

		except HTTPError as e:
			self._logger.error('APICLIENT:' + str(e))
			self._logger.error('APICLIENT:' + e.read())
			response_json = {}

		except URLError as e:
			self._logger.error('APICLIENT:' + str(e))
			self._logger.error('APICLIENT:' + e.read())
			response_json = {}

		return response_json


#	api methods

	def titleWatched(self, titleId, rating = None, playerEvents = None):
		if isinstance(rating, (int, long)):
			rating = RATING_CODE[rating]

		req = {
			'methodPath': 'title/%d/watched/' % titleId,
			'method': 'post',
			'data': {
				'rating': rating,
				'player_events': json.dumps(playerEvents)
			}
		}

		self.execute(req)

	def titleIdentify(self, **data):
		"""
			stv_title_hash - hash of the movie file
			stv_subtitle_hash - hash of the subtitle file
			imdb_id - IMDb ID
			total_time - total time of the movie
			file_name - name fo the file
			label - label of the movie
		"""
		req = {
			'methodPath': 'title/identify/',
			'method': 'post',
			'data': data
		}

		return self.execute(req)

	def libraryTitleAdd(self, titleId):
		req = {
			'methodPath': 'library/title/%d/add/' % titleId,
			'method': 'post'
		}

		return self.execute(req)

	def libraryTitleRemove(self, titleId):
		req = {
			'methodPath': 'library/title/%d/' % titleId,
			'method': 'delete'
		}

		return self.execute(req)

	def libraryTitle(self, titleId):
		req = {
			'methodPath': 'library/title/%d/' % titleId,
			'method': 'post'
		}

		return self.execute(req)

	def titleSimilar(self, titleId):
		req = {
			'methodPath': 'title/%d/similar/' % titleId,
			'method': 'post'
		}

		return self.execute(req)

	def profileRecco(self, atype, props = [ 'id', 'cover_full', 'cover_large', 'cover_medium', 'cover_small', 'cover_thumbnail', 'date', 'genres', 'image', 'link', 'name', 'plot', 'released', 'trailer', 'type', 'year' ]):
		req = {
			'methodPath': 'profile/recco/',
			'method': 'get',
			'data': {
				'type': atype,
				'title_property[]': ','.join(props)
			}
		}

		return self.execute(req)

	def libraryListCreate(self, list_uid):
		req = {
			'methodPath': 'library/list/%s/create/' % list_uid,
			'method': 'get',
		}

		return self.execute(req)


