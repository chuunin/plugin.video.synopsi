import logging
import json
import sys
from base64 import b64encode
from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError


class BapiClient:
	def __init__(self, base_url, key, secret, username, password, originReqHost = None, debugLvl = logging.INFO):
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
		self.refreshToken = response_json['refresh_token']
		self._logger.debug('access token = ' + self.accessToken)

	def isAuthorized(self):
		return self.accessToken != None

	def execute(self, requestData):
		if not self.isAuthorized():
			raise Exception('Not Authorized')

		url = self.apiUrl + requestData['methodPath']

		method = requestData['method']
		
		if not requestData.has_key('data'):
			requestData['data'] = {}

		post = {}
		get = {}

		post = requestData['data']		

		# append data to post
		if method == 'post':
			post['client_id'] = self.key
			post['client_secret'] = self.secret
			post['bearer_token'] = self.accessToken
			data = urlencode(post)

		# append data to get
		if method == 'get':
			get['client_id'] = self.key
			get['client_secret'] = self.secret
			get['bearer_token'] = self.accessToken
			url += '?' + urlencode(get)
			self._logger.debug(url)

		self._logger.debug('post:' + str(post))
		self._logger.debug('get:' + str(get))		
		self._logger.debug('data:' + str(data))		
#		self._logger.debug(self.authHeaders)

		try:
			response = urlopen(Request(url,
				data = data,
				headers = self.authHeaders, 
				origin_req_host = self.originReqHost
			))
		except HTTPError as e:
			self._logger.error(str(e))
			self._logger.error(e.read())
		else:
			while True:
				l = response.readline()
				if not l:
					break
				print l



#class BapiMethods(BapiClient):
	def titleWatched(self, titleId, rating = None):
		req = {
			'methodPath': 'title/%d/watched/' % titleId,
			'method': 'post',
			'data': {
				'rating': rating
			}
		}

		self.execute(req)



