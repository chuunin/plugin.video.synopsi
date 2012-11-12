import xbmc, xbmcgui, xbmcaddon
import logging
import json
import sys
import datetime
from base64 import b64encode
from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError, URLError
from utilities import *
import httplib

RATING_CODE = {
	1: 'like',
	2: 'neutral',
	3: 'dislike'
}

defaultTitleProps = [ 'id', 'cover_full', 'cover_large', 'cover_medium', 'cover_small', 'cover_thumbnail', 'date', 'genres', 'name', 'plot', 'released', 'trailer', 'type', 'year', 'url', 'directors', 'writers', 'runtime' ]

class CacheType:
	No = 1
	Write = 2
	Read = 4
						

class AuthenticationError(Exception):
	pass

class ApiClient(object):
	_instance = None
	def __init__(self, base_url, key, secret, username, password, device_id, originReqHost=None, debugLvl=logging.INFO, accessTokenTimeout=10, rel_api_url='api/public/1.0/'):
		self.baseUrl = base_url
		self.key = key
		self.secret = secret
		self.username = username
		self.password = password
		self.invalidateAccessToken()
		self.accessTokenTimeout = accessTokenTimeout		# [minutes] how long is stv accessToken valid ?
		self.apiUrl = self.baseUrl + rel_api_url
		self.originReqHost = originReqHost or 'test.papi.synopsi.tv'		# TODO: what is this
		self.authHeaders = None
		self.device_id = device_id  
		self._log = logging.getLogger()
		
		if len(self._log.handlers)==0:
			self._log.addHandler(logging.StreamHandler(sys.stdout))

		self._log.setLevel(debugLvl)
		self._log.debug('apiclient __init__ (%s, %s)' % (self.username, self.password))
		self.failedRequest = []
		# self._log.error('APIURL:' + self.apiUrl)
		# self._log.error('BASEURL:' + self.baseUrl)		
		

	@classmethod
	def getDefaultClient(cls):
		if ApiClient._instance:
			return ApiClient._instance

		__addon__  = get_current_addon()

		iuid = get_install_id()
		
		# get or generate install-unique ID
		ApiClient._instance = cls(
			__addon__.getSetting('BASE_URL'),
			__addon__.getSetting('KEY'),
			__addon__.getSetting('SECRET'),
			__addon__.getSetting('USER'),
			__addon__.getSetting('PASS'),
			iuid,
			debugLvl=logging.ERROR,
			rel_api_url=__addon__.getSetting('REL_API_URL'),
		)

		return ApiClient._instance

	def setUserPass(self, username, password):
		self.username = username
		self.password = password

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
			req = Request(
					self.baseUrl + 'oauth2/token/', 
					data=urlencode(data), 
					headers=self.authHeaders, 
					origin_req_host=self.originReqHost)
						
			# self._log.debug('request REQ HOST:' + str(req.get_origin_req_host()))
			# self._log.debug('request URL:' + str(req.get_full_url()))
			# self._log.debug('request HEADERS:' + str(req.headers.items()))
			# self._log.debug('request DATA:' + str(req.get_data()))

			response = urlopen(req)

			# self._log.debug('request RESPONSE:' + str(response))
			response_json = json.loads(response.readline())

		except HTTPError as e:
			self._log.error('APICLIENT HTTPERROR %d %s' % (e.code, e))
			self._log.error('APICLIENT HTTPERROR ' + str(e.read()))
			raise AuthenticationError()

		except URLError as e:
			self._log.error('APICLIENT URLERROR ' + str(e))
			self._log.error('APICLIENT URLERROR ' + e.reason)
			raise AuthenticationError()

		except Exception as e:
		 	self._log.error('ANOTHER EXCEPTION:' + str(e))
			raise AuthenticationError()


		self.accessToken = response_json['access_token']
		self.accessTokenSessionStart = datetime.datetime.now()
		self.refreshToken = response_json['refresh_token']
		self._log.debug('new access token: ' + self.accessToken)

	def invalidateAccessToken(self):
		self.accessToken = None
		self.accessTokenSessionStart = None
		self.refreshToken = None


	def isAuthenticated(self):
		# if we have some acess token and if access token session didn't timeout
		return self.accessToken != None and self.accessTokenSessionStart + datetime.timedelta(minutes=self.accessTokenTimeout) > datetime.datetime.now()

	def prepareRequest(self, requestData):
		url = self.apiUrl + requestData['methodPath']
		method = requestData['method']
		data = None

		if not requestData.has_key('data'):
			requestData['data'] = {}

		# append data to post
		if method == 'post':
			post = requestData['data']		
			post['bearer_token'] = self.accessToken
			data = urlencode(post)

		# append data to get
		if method == 'get':
			get = requestData['data']
			get['bearer_token'] = self.accessToken
			url += '?' + urlencode(get)
			data = None

		self._log.debug('URL:' + url)
		if 'post' in locals():
			self._log.debug('POST:' + str(post))
		if 'get' in locals():
			self._log.debug('GET:' + str(get))		
		if data:
			self._log.debug('DATA:' + str(data))	
			
		req = Request(
					url,
					data = data,
					origin_req_host = self.originReqHost
				)		

		return req

	def execute(self, requestData, cache_type=CacheType.No):
		if not self.isAuthenticated():
			self.getAccessToken()

		req = self.prepareRequest(requestData)
		response = urlopen(req)
		response_json = json.loads(response.readline())

		return response_json


#	api methods
#	list independent
	def titleWatched(self, titleId, **data):
		# normalize ratings
		if data.has_key('rating') and isinstance(data['rating'], (int, long)):
			data['rating'] = RATING_CODE[data['rating']]

		data['device_id'] = self.device_id
		req = {
			'methodPath': 'title/%d/watched/' % titleId,
			'method': 'post',
			'data': data
		}

		self.execute(req, CacheType.Write)

	def titleIdentify(self, **data):
		""" Try to match synopsi title by various data """
		data['device_id'] = self.device_id
		req = {
			'methodPath': 'title/identify/',
			'method': 'get',
			'data': data
		}

		return self.execute(req, CacheType.Read)

	def titleSimilar(self, titleId, props=defaultTitleProps):
		req = {
			'methodPath': 'title/%d/similar/' % titleId,
			'method': 'get',
			'data': {
				'title_property[]': ','.join(props)
			}
		}

		return self.execute(req, CacheType.Read)

# conditionally dependent
	def profileRecco(self, atype, local=False, props=defaultTitleProps):
		req = {
			'methodPath': 'profile/recco/',
			'method': 'get',
			'data': {
				'type': atype,
				'title_property[]': ','.join(props)
			}
		}

		if local:
			req['data']['device_id'] = self.device_id

		return self.execute(req, CacheType.Read)

# list dependent
	def libraryTitleAdd(self, titleId):
		req = {
			'methodPath': 'library/title/%d/add/' % titleId,
			'method': 'post',
			'data':
			{
				'device_id': self.device_id
			}
		}	

		return self.execute(req, CacheType.Write)

	def libraryTitleRemove(self, titleId):
		req = {
			'methodPath': 'library/title/%d/' % titleId,
			'method': 'get',
			'data': {
				'_method': 'delete',
				'device_id': self.device_id
			}
		}

		return self.execute(req, CacheType.Write)

	def title(self, titleId, props=defaultTitleProps):
		" Get title from library "
		req = {
			'methodPath': '/title/%d/' % titleId,
			'method': 'get',
			'data': {
				'title_property[]': ','.join(props)
			}
		}

		return self.execute(req, CacheType.Read)

	def unwatchedEpisodes(self, props=defaultTitleProps):
		req = {
			'methodPath': 'profile/unwatched_episodes/',
			'method': 'get',
			'data': {
				'title_property[]': ','.join(props)
			}
		}

		return self.execute(req, CacheType.Read)


