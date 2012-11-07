from apiclient import *
import threading
import logging
import base64
import pickle

class NotConnectedException(Exception):
	pass

class RequestDataCache():

	def __init__(self, path):
		self._storage = {}
		self._logger = logging.getLogger()
		self._path = path

	def put(self, reqData, response):
		self._logger.debug('DataCache PUT /' + json.dumps(reqData))
		self._storage[json.dumps(reqData)] = response

	def get(self, reqData, default=None):
		return self._storage.get(json.dumps(reqData), default)

	def save(self):
		self.save_to(self._path)
	
	def load(self):
		return self.load_from(self._path)

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

	def dump(self):
		print 'DataCache: ' + str(self._storage)

class CachedApiClient(ApiClient):
	_instance = None
	def __init__(self, base_url, key, secret, username, password, device_id, originReqHost=None, debugLvl=logging.INFO, accessTokenTimeout=10, rel_api_url='api/public/1.0/'):
		super(CachedApiClient, self).__init__(base_url, key, secret, username, password, device_id, originReqHost, debugLvl, accessTokenTimeout, rel_api_url)

		addon = get_current_addon()
		cwd    = addon.getAddonInfo('path')

		# try to load cache
		self._cache = RequestDataCache(os.path.join(cwd, 'read_request_cache.dat'))
		try:
			self._cache.load()
		except:
			pass

		self._cache.dump()
	
	def __del__(self):
		self._cache.save()

	def queueRequest(self, requestData):
		self.failedRequest.append(requestData)

	def tryEmptyQueue(self):
		" Tries to empty queue by sending all requests. Returns true, if queue was successfully emptied."
		# assume connected
		connected = True
		while connected and len(self.failedRequest) > 0:
			try:
				response_json = ApiClient.execute(self, requestData)
				self._cache.put(requestData, response_json)
				# on success, pop the request out of queue
				self.pop(0)
			except Exception as e:
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

	def execute(self, requestData, cache_type=CacheType.No):
		try:
			response_json = ApiClient.execute(self, requestData)
			self._cache.put(requestData, response_json)
		except Exception as e:
			self._logger.error('APICLIENT:' + requestData['methodPath'])
			self._logger.error('APICLIENT:' + str(e))
			# handle accordingly to cache_type or re-raise the exception
			if cache_type==CacheType.Write:
				self.queueRequest(requestData)
				response_json = None
			elif cache_type==CacheType.Read:
				response_json = self._cache.get(requestData)				
			else:
				raise	

		return response_json


