# xbmc
import xbmc

# python standart lib
import base64
import pickle
import json
import traceback

# application
from utilities import *
from app_apiclient import ApiClient
from apiclient import commonTitleProps
from xbmcrpc import xbmc_rpc

xbmc2stv_key_translation = {
	'file_name': 'file', 
	'os_title_hash': 'os_title_hash', 
	'stv_title_hash': 'stv_title_hash', 
	'total_time': 'runtime', 
	'label': 'originaltitle', 
	'imdb_id': 'imdbnumber'
}

playable_types = ['movie', 'episode']

class StvList(object):
	"""
	Library cache.
	Storing:
	{
		"_id" : xbmcid, # not unique
		"_type": xbmctype, # "movie" or "episode"
		"_hash": stvhash, # synopsi hash
		"_file": file, # unique path to ONE file
		"filepath": filepath, # path recieved from xbmc
		# could be stack:// or stream etc.
		"imdb": imdb,
		"stv_id": synopsi_id_library
	}
	"""
	def __init__(self, uuid, apiclient, filePath=None):
		super(StvList, self).__init__()
		self.apiclient = apiclient
		self.filePath = filePath or self.__class__.getDefaultFilePath()
		self.clear()
		
		self.uuid = uuid
		#~ self.list()
		
	@classmethod
	def getDefaultFilePath(cls):
		addon  = get_current_addon()
		addon_id = addon.getAddonInfo('id')
		data_path = xbmc.translatePath('special://masterprofile/addon_data/')
		return os.path.join(data_path, addon_id, 'cache.dat')
			

	@classmethod
	def getDefaultList(cls, apiClient=None):
		if not apiClient:
			apiClient = AppApiClient.getDefaultClient()

		iuid = get_install_id()	
		cache = StvList(iuid, apiClient) 
		try:
			cache.load()
		except:
			# first time
			log('CACHE restore failed. If this is your first run, its ok')

		return cache

	def serialize(self):
		#~ self.log(dump([self.byType, self.byTypeId, self.byFilename, self.byStvId]))
		pickled_base64_cache = base64.b64encode(pickle.dumps([self.byType, self.byTypeId, self.byFilename, self.byStvId]))
		return pickled_base64_cache

	def deserialize(self, _string):
		unpickled_list = pickle.loads(base64.b64decode(_string))
		# self.log('UNPICKLED:' + str(unpickled_list))
		self.byType = unpickled_list[0]
		self.byTypeId = unpickled_list[1]
		self.byFilename = unpickled_list[2]
		self.byStvId = unpickled_list[3]

	def log(self, msg):
		log('CACHE / ' + msg)

	def _translate_xbmc2stv_keys(self, a, b):
		for (dst_key, src_key) in xbmc2stv_key_translation.iteritems():
			if b.has_key(src_key):
				a[dst_key] = b[src_key]

	def get_path(self, movie):
		if 'stack://' in movie['file']:
			parts = movie['file'][8:].split(" , ")
			return parts[0]
		else:
			return movie['file']

	def addorupdate(self, atype, aid):
		if not atype in playable_types:
			return
			
		# find out actual data about movie
		movie = xbmc_rpc.get_details(atype, aid)
		movie['type'] = atype
		movie['id'] = aid
		
		# if not in cache, it's been probably added
		if not self.hasTypeId(movie['type'], movie['id']):
			# get stv hash
			path = self.get_path(movie)
			movie['stv_title_hash'] = stv_hash(path)
			movie['os_title_hash'] = hash_opensubtitle(path)

			# try to get synopsi id
			# TODO: stv_subtitle_hash - hash of the subtitle file if present
			ident = {}
			self._translate_xbmc2stv_keys(ident, movie)

			# correct input
			if ident.get('imdb_id'):
				ident['imdb_id'] = ident['imdb_id'][2:]

			#~ self.log('to identify: ' + dump(ident))	
			self.log('to identify: ' + ident['file_name'])	

			title = self.apiclient.titleIdentify(**ident)
						
			if title.has_key('id'):
				movie['stvId'] = title['id']
				self.log('identified: ' + title['name'])
			else:
				self.log('File NOT identified %s' % movie['file'])


			self.put(movie)

			# debug warning on movie type mismatch
			if movie['type'] != title.get('type'):
				self.log('Xbmc/Synopsi identification type mismatch: %s / %s in [%s]' % (movie['type'], title.get('type'), movie.get('file')))

			# for episode, add tvshow
			if movie['type'] == 'episode' and title.get('type') == 'episode':
				self.log('episode:'+dump(title))
				self.add_tvshow(movie['id'], title['tvshow_id'])

		# it is already in cache, some property has changed (e.g. lastplayed time)
		else:
			self.update(movie)

	def add_tvshow(self, xbmc_id, stvId):
		stv_title = self.apiclient.tvshow(stvId, commonTitleProps)
		stv_title['id'] = xbmc_id
		self.put(stv_title)

	def put(self, item):
		" Put a new record in the list "
		typeIdStr = self._getKey(item['type'], item['id'])
				
		self.byType[item['type']][item['id']] = item
		self.byTypeId[typeIdStr] = item
		if item['type'] in playable_types:
			self.byFilename[item['file']] = item
			
		if item.has_key('stvId'):
			self.byStvId[item['stvId']] = item
			typeIdStr += ' | stvId ' + str(item['stvId'])
		
		logstr = 'PUT / ' + typeIdStr + ' | ' + item['file']
		
		# if known by synopsi, add to list
		if item.has_key('stvId'):
			self.apiclient.libraryTitleAdd(item['stvId'])

		self.log(logstr)

	def update(self, item):
		typeIdStr = self._getKey(item['type'], item['id'])
		cacheItem = self.byTypeId[typeIdStr]

		updateStr = ''

		# update items
		for key in item:
			if not cacheItem.has_key(key) or not item[key] == cacheItem[key]:
				updateStr += key + ': ' + str(getattr(cacheItem, key, None)) + ' -> ' + str(item[key]) + ' | '
				cacheItem[key] = item[key]

		self.log('UPDATE / ' + typeIdStr + ' / ' + updateStr)

	def remove(self, atype, aid):
		typeIdStr = self._getKey(atype, aid)
		self.log('REMOVE / ' + typeIdStr)
		try:
			item = self.getByTypeId(atype, aid)

			if item.has_key('stvId'):
				self.apiclient.libraryTitleRemove(item['stvId'])
				del self.byStvId[item['stvId']]

			# suppose cache is consistent and remove only if one of indexes is available			
			if self.byTypeId.has_key(typeIdStr):
				if self.byFilename.has_key(item['file']):
					del self.byFilename[item['file']]			
					del self.byTypeId[typeIdStr]
					del self.byType[atype][aid]

				if item.has_key('stvId'):
					self.apiclient.libraryTitleRemove(item['stvId'])
					del self.byStvId[item['stvId']]

		except Exception as e:
			self.log('REMOVE FAILED / ' + typeIdStr)	


	def hasTypeId(self, type, id):
		return self.byTypeId.has_key(self._getKey(type, id))

	def getByTypeId(self, type, id):
		return self.byTypeId[self._getKey(type, id)]

	def hasFilename(self, name):
		return self.byFilename.has_key(name)
		
	def getByFilename(self, name):
		return self.byFilename[name]

	def hasStvId(self, stv_id):
		return self.byStvId.has_key(stv_id)

	def getByStvId(self, stv_id):
		if self.byStvId.has_key(stv_id):
			return self.byStvId[stv_id]

	def getAllByType(self, atype):
		return self.byType[atype]

	def list(self):
		self.log('ID / ' +  self.uuid)
		if len(self.byTypeId) == 0:
			self.log('EMPTY')
			return

		self.log('LIST /')
		for rec in self.byTypeId.values():
			self.log(self._getKey(rec['type'], rec['id']) + '\t| ' + dump(rec))

	def listByFilename(self):
		if len(self.byFilename) == 0:
			self.log('EMPTY')
			return

		self.log('LIST /')
		for rec in self.byFilename.items():
			self.log(rec[0] + '\t| ' + dump(rec[1]))

	def clear(self):
		self.byType = { 'movie': {}, 'tvshow': {}, 'episode': {}, 'season': {}}
		self.byTypeId = {}
		self.byFilename = {}
		self.byStvId = {}

	def rebuild(self):
		"""
		Rebuild whole cache in case it is broken.
		"""
		
		self.clear()
		movies = xbmc_rpc.get_movies()
		#~ movies = { 'movies': [] }
		
		for movie in movies.get('movies', []):
			try:
				self.addorupdate('movie', movie['movieid'])
			except Exception as e:
				self.log(unicode(e))
		
		tvshows = xbmc_rpc.get_all_tvshows()
				
		self.log('get_all_tvshows ' + dump(tvshows))
		
		if tvshows['limits']['total'] > 0:
			for show in tvshows['tvshows']:
				episodes = xbmc_rpc.get_episodes(show["tvshowid"])				
				self.log('episodes: ' + dump(episodes))
				
				if episodes['limits']['total'] > 0:
					for episode in episodes["episodes"]:
						try:
							self.addorupdate('episode', episode['episodeid'])
						except Exception as e:
							self.log(unicode(e))


	def rebuild_light(self):
		"""
		Rebuild whole cache in case it is broken.
		"""
		#~ addon = get_current_addon()
		#~ addonpath = 	addon.getAddonInfo('path')
		#~ path = os.path.join(addonpath, 'tests')
		
		self.clear()
		movies = xbmc_rpc.get_movies()
		
		# generate testing json
		#~ f = open(os.path.join(path, 'get_movies.json'), 'w')
		#~ f.write(dump(movies))
		#~ f.close()
		
		for movie in movies['movies']:
			movie['id'] = movie["movieid"]
			movie['type'] = "movie"
			self.put(movie)

		
		tvshows = xbmc_rpc.get_all_tvshows()
		
		# generate testing json
		#~ f = open(os.path.join(path, 'get_all_tvshows.json'), 'w')
		#~ f.write(dump(tvshows))
		#~ f.close()
		
		self.log('get_all_tvshows ' + dump(tvshows))
		
		if tvshows['limits']['total'] > 0:
			for show in tvshows['tvshows']:
				episodes = xbmc_rpc.get_episodes(show["tvshowid"])				
				self.log('episodes: ' + dump(episodes))
				
				if episodes['limits']['total'] > 0:
					for episode in episodes["episodes"]:
						episode['id'] = episode["episodeid"]
						episode['type'] = "episode"
						self.put(episode)

	def save(self):
		self.log('SAVING / ' + self.filePath)
		f = open(self.filePath, 'w')
		f.write(self.serialize())
		f.close()

	def load(self):
		f = open(self.filePath, 'r')
		self.deserialize(f.read())
		f.close()

	def _getKey(self, type, id):
		return str(type) + '--' + str(id)

