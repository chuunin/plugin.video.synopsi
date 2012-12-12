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

class DuplicateStvIdException(Exception):
	pass

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
		json_str = json.dumps(self.getItems())

		return json_str

	def deserialize(self, _string):
		json_obj = json.loads(_string)
		return json_obj

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


			# TODO: stv_subtitle_hash - hash of the subtitle file if present
			ident = {}
			self._translate_xbmc2stv_keys(ident, movie)

			# give api a hint about type if possible
			if movie['type'] in playable_types:
				ident['type'] = movie['type']

			# correct input
			if ident.get('imdb_id'):
				ident['imdb_id'] = ident['imdb_id'][2:]

			# try to get synopsi id
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
			if title.has_key('id') and movie['type'] == 'episode' and title.get('type') == 'episode':
				self.log('xbmc episode:'+dump(filtertitles(movie)))
				self.add_tvshow(title['tvshow_id'], movie['tvshowid'])

		# it is already in cache, some property has changed (e.g. lastplayed time)
		else:
			self.update(movie)

	def add_tvshow(self, stvId, xbmc_id):
		" Adds a tvshow with stvId into cache, if it's not already there "
		if not self.byStvId.has_key(stvId):
			stv_title = self.apiclient.tvshow(stvId, commonTitleProps)

			stv_title['xbmc_id'] = xbmc_id

			# if tvshow not in cache yet
			if not self.hasStvId(stv_title['id']):
				self.log('tvshow stv id:' + str(stv_title['id']))
				self.log('tvshow xbmc id:' + str(xbmc_id))
				self.put(stv_title)

	def put(self, item, isLoading=False):
		" Put a new record in the list "
		self.log('PUT ' + dump(filtertitles(item)))
		# check if an item with this stvId is not already there
		if item.has_key('stvId') and self.hasStvId(item['stvId']):
			raise DuplicateStvIdException('Title with stv_id=%d is already in library' % item['stvId'])

		# update by type and id if possible
		if item.has_key('type') and item.has_key('id'):
			typeIdStr = self._getKey(item['type'], item['id'])
			if self.hasTypeIdStr(typeIdStr):
				raise DuplicateStvIdException('Title with type--xbmc_id=%s is already in library' % typeIdStr)
			self.byType[item['type']][item['id']] = item
			self.byTypeId[typeIdStr] = item

		if item.get('type') in playable_types:
			self.byFilename[item['file']] = item

		if item.has_key('stvId'):
			self.log('added stvId to index: ' + str(item['stvId']))
			self.byStvId[item['stvId']] = item

		self.items.append(item)

		logstr = 'PUT / ' + str(item.get('type')) + '--' + str(item.get('id')) + ' | ' + item.get('file', '')

		# if not loading cache and known by synopsi, add to list
		if not isLoading and item.has_key('stvId'):
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

		except Exception as e:
			self.log('REMOVE FAILED / ' + typeIdStr)
			raise

	def correct_title(self, old_title, new_title):
		" Removes old title and adds new one with the same data, except stvId and type taken from new_title "
		old_item = self.byTypeId[self._getKey(old_title['type'], old_title['xbmc_id'])]
		new_item = dict(old_item)
		new_item['stvId'] = new_title['id']
		new_item['type'] = new_title['type']

		self.log('correcting %s to %s, new stvId: %s' % (old_item.get('label'), new_item.get('label'), str(new_item['stvId'])))

		self.dump()
		self.remove(old_title['type'], old_title['xbmc_id'])
		self.put(new_item)
		self.dump()
		return new_item

	def hasTypeId(self, atype, aid):
		return self.hasTypeIdStr(self._getKey(atype, aid))

	def hasTypeIdStr(self, typeIdStr):
		return self.byTypeId.has_key(typeIdStr)

	def getByTypeId(self, atype, aid):
		return self.byTypeId[self._getKey(atype, aid)]

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
		if len(self.items) == 0:
			self.log('EMPTY')
			return

		self.log('LIST /')
		for rec in self.items:
			self.log(dump(filtertitles(rec)))

	def dump(self):
		self.log(dump(self.byTypeId))
		#~ self.log(dump(self.byStvId))
		#~ self.log(dump(self.byFilename))

	def listByFilename(self):
		if len(self.byFilename) == 0:
			self.log('EMPTY')
			return

		self.log('LIST /')
		for rec in self.byFilename.items():
			self.log(rec[0] + '\t| ' + dump(rec[1]))

	def clear(self):
		self.items = []
		self.byType = { 'movie': {}, 'tvshow': {}, 'episode': {}, 'season': {}}
		self.byTypeId = {}
		self.byFilename = {}
		self.byStvId = {}

	def getItems(self):
		return self.items

	def rebuild(self):
		"""
		Rebuild whole cache in case it is broken.
		"""

		self.clear()
		movies = xbmc_rpc.get_movies()
		#~ movies = { 'movies': [] }

		for movie in movies.get('movies', []):
			if xbmc.abortRequested:
				return
			try:
				self.addorupdate('movie', movie['movieid'])
			except Exception as e:
				#~ self.log(traceback.format_exc())
				self.log(str(e))

		tvshows = xbmc_rpc.get_all_tvshows()

		self.log('get_all_tvshows ' + dump(tvshows))

		if tvshows['limits']['total'] > 0:
			for show in tvshows['tvshows']:
				if xbmc.abortRequested:
					return

				episodes = xbmc_rpc.get_episodes(show["tvshowid"])
				self.log('episodes: ' + dump(filtertitles(episodes)))

				if episodes['limits']['total'] > 0:
					for episode in episodes["episodes"]:
						if xbmc.abortRequested:
							return
						try:
							self.addorupdate('episode', episode['episodeid'])
						except Exception as e:
							#~ self.log(traceback.format_exc())
							self.log(str(e))


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

		self.log('get_all_tvshows ' + dump(filtertitles(tvshows)))

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
		self.clear()
		f = open(self.filePath, 'r')
		json_obj = self.deserialize(f.read())
		for item in json_obj:
			self.put(item, True)

		f.close()

	def _getKey(self, atype, aid):
		return str(atype) + '--' + str(aid)

	def updateTitle(self, title):
		" Update title values from cache, using 'id' as 'stvId', updating stv_title_hash, file "
		if self.hasStvId(title['id']):
			cached_title = self.getByStvId(title['id'])
			title['stv_title_hash'] = cached_title['stv_title_hash']
			title['file'] = cached_title['file']
			title['xbmc_id'] = cached_title['id']
			self.log('updating title %s with xbmc_id: %d file: %s' % (title.get('name'), title['xbmc_id'], title['file']))

