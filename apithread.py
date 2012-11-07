import apiclient
import threading

class

class NotConnectedException(Exception):
	pass

class RequestDataCache():

	def __init__(self, path):
		self._storage = {}
		self._logger = logging.getLogger()
		self._path = path

	def put(self, reqData, response):
		self._logger.debug('DataCache PUT /' + json.dumps(reqData))
		self._storage[reqData] = response

	def get(self, reqData):
		return self._storage[reqData]

	def save(self):
		self.save_to(self.path)
	
	def load(self):
		return self.load_from(self.path)

    def save_to(self, path):
        f = open(path, 'w')
        f.write(self.serialize())
        f.close()

    def load_from(self, path):
        f = open(path, 'r')
        self.deserialize(f.read())
        f.close()

    def serialize(self):        
        pickled_base64_cache = base64.b64encode(pickle.dumps(self._storage))
        return pickled_base64_cache

    def deserialize(self, _string):
        self._storage = pickle.loads(base64.b64decode(_string))


class CachedApiClient(apiclient.ApiClient):
	_instance = None
	def __init__(self, base_url, key, secret, username, password, device_id, originReqHost=None, debugLvl=logging.INFO, accessTokenTimeout=10, rel_api_url='api/public/1.0/'):
		super(CachedApiClient, self).__init__()

		addon = get_current_addon()
		cwd    = addon.getAddonInfo('path')

		# try to load cache
		self._cache = RequestDataCache(os.path.join(cwd, 'read_request_cache.dat')
		try:
			self._cache.load()
		except:
			pass

		self.baseUrl = base_url
		self.key = key
		self.secret = secret
		self.username = username
		self.password = password
		self.accessToken = None
		self.refreshToken = None
		self.apiUrl = self.baseUrl + rel_api_url
		self.originReqHost = originReqHost or 'test.papi.synopsi.tv'		# TODO: what is this
		self.authHeaders = None
		self.device_id = device_id  
		self._logger = logging.getLogger()
		
		# xbmc.log('Log handler count %d ' % len(self._logger.handlers))

		if len(self._logger.handlers)==0:
			self._logger.addHandler(logging.StreamHandler(sys.stdout))

		self._logger.setLevel(debugLvl)
		self._logger.debug('apiclient __init__ (%s, %s)' % (self.username, self.password))
		self.accessTokenTimeout = accessTokenTimeout		# [minutes] how long is stv accessToken valid ?
		self.accessTokenSessionStart = None
		self.failedRequest = []
		# self._logger.error('APIURL:' + self.apiUrl)
		# self._logger.error('BASEURL:' + self.baseUrl)		
	
	def __del__(self):
		self._cache.save()

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

	def queueRequest(self, requestData):
		self.failedRequest.append(requestData)

	def tryEmptyQueue(self):
		# assume connected
		connected = True
		while connected and len(self.failedRequest) > 0:
			try:
				response = self.doRequest(self.failedRequest[0], False)
				# on success, pop the request out of queue
				self.pop(0)
			except:
				# if network failure
				connected = False
				
		return connected

	def doRequest(self, req, cacheable=True):
		if not self.isAuthenticated():
			access = self.getAccessToken()
			if not access:
				self._logger.error('Could not get the auth token')
				return False

		# put the cacheable request into queue
		if cacheable:
			self.queueRequest(req)
			# try to empty queue, if not success, return back
			if not self.tryEmptyQueue():
				raise NotConnectedException()
		else:
			response = urlopen(req)
			response_json = json.loads(response.readline())
			return response_json

	def getAccessToken(self):
		data = {
			'grant_type': 'password',
			'client_id': self.key,
			'client_secret': self.secret,
			'username': self.username,
			'password': self.password
		}

		self.authHeaders = {'AUTHORIZATION': 'BASIC %s' % b64encode("%s:%s" % (self.key, self.secret))}

		# self._logger.debug('apiclient getaccesstoken u:%s p:%s' % (self.username, self.password))
		# self._logger.debug('apiclient getaccesstoken %s' % str(data))

		# get token
		try:

			req = Request(
					self.baseUrl + 'oauth2/token/', 
					data=urlencode(data), 
					headers=self.authHeaders, 
					origin_req_host=self.originReqHost)
						
			# self._logger.debug('request REQ HOST:' + str(req.get_origin_req_host()))
			# self._logger.debug('request URL:' + str(req.get_full_url()))
			# self._logger.debug('request HEADERS:' + str(req.headers.items()))
			# self._logger.debug('request DATA:' + str(req.get_data()))

			response = urlopen(req)

			# self._logger.debug('request RESPONSE:' + str(response))
			response_json = json.loads(response.readline())

		except HTTPError as e:
			self._logger.error('%d %s' % (e.code, e))
			self._logger.error(e.read())
			raise AuthenticationError()

		except URLError as e:
			self._logger.error(str(e))
			self._logger.error(e.reason)
			raise AuthenticationError()

		except Exception as e:
		 	self._logger.error('ANOTHER EXCEPTION:' + str(e))
			raise AuthenticationError()


		self.accessToken = response_json['access_token']
		self.accessTokenSessionStart = datetime.datetime.now()
		self.refreshToken = response_json['refresh_token']
		self._logger.debug('new access token: ' + self.accessToken)

	def isAuthenticated(self):
		# if we have some acess token and if access token session didn't timeout
		return self.accessToken != None and self.accessTokenSessionStart + datetime.timedelta(minutes=self.accessTokenTimeout) > datetime.datetime.now()


	def execute(self, requestData, cache_type=CacheType.No):
		try:
			response = self.execute(requestData)			
			response_json = json.loads(response.readline())
			self._cache.put(requestData, response_json)
		except Exception as e:
			self._logger.error('APICLIENT:' + url)
			self._logger.error('APICLIENT:' + str(e))
			self._logger.error('APICLIENT:' + e.read())
			# handle accordingly to cache_type or re-raise the exception
			if cache_type==CacheType.Write:
				self.queueRequest(requestData)
				response_json = None
			elif cache_type==CacheType.Read:
				response_json = self._cache.get(requestData)				
			else:
				raise	

		return response_json


